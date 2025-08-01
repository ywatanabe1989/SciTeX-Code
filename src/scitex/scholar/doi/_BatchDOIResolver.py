#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-01 12:26:00 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/doi/_BatchDOIResolver.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/doi/_BatchDOIResolver.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Enhanced resumable DOI resolver with intuitive features and performance optimizations."""

import asyncio
import json
import time
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

from scitex import logging
from ._DOIResolver import DOIResolver
from ..utils._progress_display import ProgressDisplay

logger = logging.getLogger(__name__)


class BatchDOIResolver:
    """Enhanced DOI resolver with better performance and user experience.
    
    Features:
    - Smart rate limiting with adaptive delays
    - Concurrent resolution with configurable workers
    - Deduplication of similar titles
    - Intelligent retry strategies
    - Real-time rsync-like progress with accurate ETA
    - Automatic resume from any interruption
    - Memory of successful sources per paper type
    """
    
    def __init__(
        self, 
        progress_file: Optional[Path] = None,
        max_workers: int = 4,
        cache_dir: Optional[Path] = None
    ):
        """Initialize enhanced resolver.
        
        Args:
            progress_file: Path to progress file (auto-generated if None)
            max_workers: Number of concurrent workers
            cache_dir: Directory for caching DOI lookups
        """
        self.doi_resolver = DOIResolver()
        self.max_workers = max_workers
        
        # Set up progress tracking
        if progress_file:
            self.progress_file = Path(progress_file)
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.progress_file = Path(f"doi_resolution_{timestamp}.progress.json")
            
        # Set up cache directory
        if cache_dir:
            self.cache_dir = Path(cache_dir)
        else:
            self.cache_dir = Path.home() / ".scitex" / "scholar" / "doi_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Load state
        self.progress_data = self._load_progress()
        self._start_time = time.time()
        
        # Performance tracking
        self._source_success_rates = self._load_source_stats()
        self._recent_rates = deque(maxlen=50)  # Track recent processing rates
        self._title_cache = {}  # Cache normalized titles
        
    def _load_progress(self) -> Dict[str, Any]:
        """Load or create progress data with enhanced fields."""
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r') as f:
                    data = json.load(f)
                logger.info(f"Resuming from: {self.progress_file}")
                
                # Migrate old format if needed
                if "source_performance" not in data:
                    data["source_performance"] = {}
                if "processing_times" not in data:
                    data["processing_times"] = []
                    
                return data
            except Exception as e:
                logger.warning(f"Could not load progress file: {e}")
                
        # Create new enhanced progress data
        return {
            "version": 2,
            "started_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "completed": False,
            "papers": {},
            "statistics": {
                "total": 0,
                "processed": 0,
                "resolved": 0,
                "failed": 0,
                "skipped": 0,
                "rate_limited": 0,
                "cached": 0
            },
            "rate_limit_info": {
                "last_request_time": 0,
                "requests_in_window": 0,
                "window_start": 0,
                "adaptive_delay": 0.1  # Start with 100ms
            },
            "source_performance": {},  # Track which sources work best
            "processing_times": [],  # Track processing times for ETA
            "duplicate_groups": {}  # Track potential duplicates
        }
        
    def _load_source_stats(self) -> Dict[str, Dict[str, float]]:
        """Load historical source performance stats."""
        stats_file = self.cache_dir / "source_stats.json"
        if stats_file.exists():
            try:
                with open(stats_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
        
    def _save_source_stats(self):
        """Save source performance stats."""
        stats_file = self.cache_dir / "source_stats.json"
        try:
            with open(stats_file, 'w') as f:
                json.dump(self._source_success_rates, f, indent=2)
        except:
            pass
            
    def _normalize_title(self, title: str) -> str:
        """Normalize title for deduplication."""
        # Remove common variations
        import re
        title = title.lower().strip()
        title = re.sub(r'[^\w\s]', '', title)  # Remove punctuation
        title = re.sub(r'\s+', ' ', title)  # Normalize whitespace
        return title
        
    def _find_similar_papers(self, papers: List[Dict[str, Any]]) -> Dict[str, List[int]]:
        """Find potentially duplicate papers."""
        from difflib import SequenceMatcher
        
        groups = {}
        processed = set()
        
        for i, paper1 in enumerate(papers):
            if i in processed:
                continue
                
            title1 = self._normalize_title(paper1.get("title", ""))
            if not title1:
                continue
                
            group = [i]
            for j, paper2 in enumerate(papers[i+1:], start=i+1):
                if j in processed:
                    continue
                    
                title2 = self._normalize_title(paper2.get("title", ""))
                if not title2:
                    continue
                    
                # Check similarity
                similarity = SequenceMatcher(None, title1, title2).ratio()
                if similarity > 0.85:  # 85% similar
                    group.append(j)
                    processed.add(j)
                    
            if len(group) > 1:
                groups[f"group_{len(groups)}"] = group
                logger.info(f"Found {len(group)} similar papers for: {paper1.get('title', '')[:50]}...")
                
        return groups
        
    def _adaptive_rate_limit(self) -> float:
        """Adaptive rate limiting based on recent success/failures."""
        rate_info = self.progress_data["rate_limit_info"]
        current_time = time.time()
        
        # Increase delay if we're getting rate limited
        if self.progress_data["statistics"]["rate_limited"] > 5:
            rate_info["adaptive_delay"] = min(2.0, rate_info["adaptive_delay"] * 1.5)
            
        # Decrease delay if we're successful
        elif self.progress_data["statistics"]["resolved"] > 10:
            recent_success_rate = self._calculate_recent_success_rate()
            if recent_success_rate > 0.8:
                rate_info["adaptive_delay"] = max(0.05, rate_info["adaptive_delay"] * 0.9)
                
        return rate_info["adaptive_delay"]
        
    def _calculate_recent_success_rate(self) -> float:
        """Calculate success rate from recent attempts."""
        if not self._recent_rates:
            return 0.5
            
        successes = sum(1 for r in self._recent_rates if r)
        return successes / len(self._recent_rates)
        
    def _get_optimal_sources(self, paper: Dict[str, Any]) -> List[str]:
        """Get sources ordered by likelihood of success."""
        # Start with default order
        sources = self.doi_resolver.sources.copy()
        
        # Use historical performance if available
        journal = paper.get("journal", "").lower()
        if journal in self._source_success_rates:
            # Sort by success rate for this journal
            journal_stats = self._source_success_rates[journal]
            sources.sort(key=lambda s: journal_stats.get(s, 0), reverse=True)
            
        return sources
        
    async def _resolve_single_async(self, paper: Dict[str, Any], index: int, total: int) -> Tuple[str, Optional[str]]:
        """Resolve single paper asynchronously with optimizations."""
        title = paper.get("title", "")
        if not title:
            return title, None
            
        # Check cache first
        cache_key = self._normalize_title(title)
        cache_file = self.cache_dir / f"{hash(cache_key)}.json"
        
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    cached = json.load(f)
                    if cached.get("doi"):
                        self.progress_data["statistics"]["cached"] += 1
                        return title, cached["doi"]
            except:
                pass
                
        # Get optimal source order
        sources = self._get_optimal_sources(paper)
        
        # Try resolution with adaptive timeout
        start_time = time.time()
        try:
            doi = await asyncio.wait_for(
                self.doi_resolver.title_to_doi_async(
                    title=title,
                    year=paper.get("year"),
                    authors=paper.get("authors"),
                    sources=sources[:3]  # Try top 3 sources only
                ),
                timeout=30  # 30 second timeout
            )
            
            # Track success
            if doi:
                elapsed = time.time() - start_time
                self._recent_rates.append(True)
                self.progress_data["processing_times"].append(elapsed)
                
                # Cache result
                with open(cache_file, 'w') as f:
                    json.dump({"doi": doi, "timestamp": datetime.now().isoformat()}, f)
                    
                # Update source stats
                journal = paper.get("journal", "").lower()
                if journal not in self._source_success_rates:
                    self._source_success_rates[journal] = {}
                for source in sources[:3]:
                    self._source_success_rates[journal][source] = \
                        self._source_success_rates[journal].get(source, 0) * 0.9 + 0.1
                        
                return title, doi
            else:
                self._recent_rates.append(False)
                return title, None
                
        except asyncio.TimeoutError:
            logger.warning(f"Timeout resolving: {title[:50]}...")
            self._recent_rates.append(False)
            return title, None
        except Exception as e:
            logger.error(f"Error resolving {title[:30]}...: {e}")
            self._recent_rates.append(False)
            return title, None
            
    def resolve_from_bibtex(self, bibtex_path: Path, sources: Optional[List[str]] = None) -> Dict[str, str]:
        """Resolve DOIs with enhanced performance."""
        from scitex.io import load
        
        # Load BibTeX
        bibtex_path = Path(bibtex_path)
        logger.info(f"Loading: {bibtex_path}")
        
        try:
            entries = load(str(bibtex_path))
        except Exception as e:
            logger.error(f"Failed to load BibTeX: {e}")
            return {}
            
        # Extract papers
        papers_metadata = []
        for entry in entries:
            fields = entry.get("fields", {})
            title = fields.get("title", "").strip()
            if not title:
                continue
                
            papers_metadata.append({
                "title": title,
                "authors": self._parse_bibtex_authors(fields.get("author", "")),
                "year": self._parse_year(fields.get("year", "")),
                "journal": fields.get("journal", ""),
                "doi": fields.get("doi", "")
            })
            
        # Find duplicates
        duplicate_groups = self._find_similar_papers(papers_metadata)
        if duplicate_groups:
            logger.info(f"Found {len(duplicate_groups)} groups of similar papers")
            self.progress_data["duplicate_groups"] = duplicate_groups
            
        # Update total
        self.progress_data["statistics"]["total"] = len(papers_metadata)
        self._save_progress()
        
        # Resolve DOIs
        return self.resolve_batch(papers_metadata, sources)
        
    def resolve_batch(self, papers: List[Dict[str, Any]], sources: Optional[List[str]] = None) -> Dict[str, str]:
        """Resolve DOIs with enhanced batch processing."""
        results = {}
        
        # Filter out already processed papers
        papers_to_process = []
        for paper in papers:
            paper_key = self._get_paper_key(paper)
            
            # Skip if already resolved
            if paper_key in self.progress_data["papers"]:
                paper_info = self.progress_data["papers"][paper_key]
                if paper_info["status"] == "resolved":
                    results[paper["title"]] = paper_info["doi"]
                    continue
                    
            # Skip if already has DOI
            if paper.get("doi"):
                results[paper["title"]] = paper["doi"]
                self.progress_data["papers"][paper_key] = {
                    "title": paper["title"],
                    "doi": paper["doi"],
                    "status": "resolved",
                    "source": "existing"
                }
                continue
                
            papers_to_process.append(paper)
            
        if not papers_to_process:
            logger.info("All papers already resolved!")
            return results
            
        # Create progress display
        progress = ProgressDisplay(
            total=len(papers_to_process),
            description="Resolving DOIs"
        )
        
        # Process concurrently with asyncio
        logger.info(f"Processing {len(papers_to_process)} papers with {self.max_workers} workers...")
        
        async def process_all():
            tasks = []
            for i, paper in enumerate(papers_to_process):
                task = self._resolve_single_async(paper, i, len(papers_to_process))
                tasks.append(task)
                
            # Process with semaphore to limit concurrency
            semaphore = asyncio.Semaphore(self.max_workers)
            
            async def bounded_resolve(paper, index):
                async with semaphore:
                    # Add adaptive delay
                    delay = self._adaptive_rate_limit()
                    await asyncio.sleep(delay)
                    return await self._resolve_single_async(paper, index, len(papers_to_process))
                    
            bounded_tasks = [
                bounded_resolve(paper, i) 
                for i, paper in enumerate(papers_to_process)
            ]
            
            # Process and update progress
            for coro in asyncio.as_completed(bounded_tasks):
                title, doi = await coro
                
                if doi:
                    results[title] = doi
                    self._update_progress_success(title, doi)
                    progress.update(success=True)
                else:
                    self._update_progress_failure(title)
                    progress.update(success=False)
                    
                self._save_progress()
                
            return results
            
        # Run async processing
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(process_all())
        finally:
            loop.close()
            
        # Finish
        progress.finish()
        self._save_source_stats()
        self._show_final_summary()
        
        return results
        
    def _get_paper_key(self, paper: Dict[str, Any]) -> str:
        """Generate unique key for paper."""
        title = self._normalize_title(paper.get("title", ""))
        year = paper.get("year", "")
        return f"{title}_{year}"
        
    def _update_progress_success(self, title: str, doi: str):
        """Update progress for successful resolution."""
        paper_key = self._normalize_title(title)
        self.progress_data["papers"][paper_key] = {
            "title": title,
            "doi": doi,
            "status": "resolved",
            "timestamp": datetime.now().isoformat()
        }
        self.progress_data["statistics"]["resolved"] += 1
        self.progress_data["statistics"]["processed"] += 1
        
    def _update_progress_failure(self, title: str):
        """Update progress for failed resolution."""
        paper_key = self._normalize_title(title)
        self.progress_data["papers"][paper_key] = {
            "title": title,
            "status": "failed",
            "timestamp": datetime.now().isoformat()
        }
        self.progress_data["statistics"]["failed"] += 1
        self.progress_data["statistics"]["processed"] += 1
        
    def _save_progress(self):
        """Save progress atomically."""
        self.progress_data["last_updated"] = datetime.now().isoformat()
        
        temp_file = self.progress_file.with_suffix('.tmp')
        try:
            with open(temp_file, 'w') as f:
                json.dump(self.progress_data, f, indent=2)
            temp_file.replace(self.progress_file)
        except Exception as e:
            logger.error(f"Failed to save progress: {e}")
            if temp_file.exists():
                temp_file.unlink()
                
    def _parse_bibtex_authors(self, authors_str: str) -> List[str]:
        """Parse BibTeX author string."""
        if not authors_str:
            return []
        return [a.strip() for a in authors_str.split(" and ") if a.strip()]
        
    def _parse_year(self, year_str: str) -> Optional[int]:
        """Parse year from string."""
        try:
            return int(year_str)
        except:
            return None
            
    def _show_final_summary(self):
        """Show enhanced final summary."""
        stats = self.progress_data["statistics"]
        duration = time.time() - self._start_time
        
        logger.info("\n" + "="*60)
        logger.info("DOI Resolution Summary")
        logger.info("="*60)
        logger.info(f"Total papers: {stats['total']}")
        logger.info(f"Successfully resolved: {stats['resolved']} ({stats['resolved']/stats['total']*100:.1f}%)")
        logger.info(f"From cache: {stats['cached']}")
        logger.info(f"Failed: {stats['failed']}")
        logger.info(f"Duration: {duration:.1f} seconds")
        
        # Show average processing time
        if self.progress_data["processing_times"]:
            avg_time = sum(self.progress_data["processing_times"]) / len(self.progress_data["processing_times"])
            logger.info(f"Average resolution time: {avg_time:.2f} seconds")
            
        # Show duplicate groups
        if self.progress_data["duplicate_groups"]:
            logger.info(f"\nFound {len(self.progress_data['duplicate_groups'])} groups of similar papers")
            
        logger.info(f"\nProgress saved to: {self.progress_file}")
        logger.info("="*60)


# EOF