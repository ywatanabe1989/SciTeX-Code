#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-01 02:34:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/resolve_dois/_ResumableDOIResolver.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/resolve_dois/_ResumableDOIResolver.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Resumable DOI resolver that can continue from interruptions."""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from scitex import logging
from ..doi._DOIResolver import DOIResolver
from ..utils._progress_display import ProgressDisplay

logger = logging.getLogger(__name__)


class ResumableDOIResolver:
    """Resolves DOIs from paper metadata with resume capability.
    
    Creates a progress file to track:
    - Which papers have been processed
    - Successfully resolved DOIs
    - Failed resolutions for retry
    - Rate limit tracking
    """
    
    def __init__(self, progress_file: Optional[Path] = None):
        """Initialize resumable DOI resolver.
        
        Args:
            progress_file: Path to progress tracking file (auto-generated if None)
        """
        self.doi_resolver = DOIResolver()
        
        # Set up progress tracking
        if progress_file:
            self.progress_file = Path(progress_file)
        else:
            # Default to current directory with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.progress_file = Path(f"doi_resolution_{timestamp}.progress.json")
            
        self.progress_data = self._load_progress()
        self._start_time = time.time()
        
    def _load_progress(self) -> Dict[str, Any]:
        """Load existing progress or create new."""
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r') as f:
                    data = json.load(f)
                logger.info(f"Resuming DOI resolution from: {self.progress_file}")
                return data
            except Exception as e:
                logger.warning(f"Could not load progress file: {e}")
                
        # Create new progress data
        return {
            "version": 1,
            "started_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "completed": False,
            "papers": {},  # title -> resolution status
            "statistics": {
                "total": 0,
                "processed": 0,
                "resolved": 0,
                "failed": 0,
                "skipped": 0,
                "rate_limited": 0
            },
            "rate_limit_info": {
                "last_request_time": 0,
                "requests_in_window": 0,
                "window_start": 0
            }
        }
    
    def _save_progress(self):
        """Save current progress atomically."""
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
    
    def _get_paper_key(self, title: str, year: Optional[int] = None, 
                       authors: Optional[List[str]] = None) -> str:
        """Generate unique key for a paper."""
        # Normalize title
        key = title.lower().strip()
        
        # Add year if available
        if year:
            key += f"_{year}"
            
        # Add first author if available
        if authors and len(authors) > 0:
            first_author = authors[0].split(',')[0].lower().strip()
            key += f"_{first_author}"
            
        return key
    
    def _check_rate_limit(self) -> bool:
        """Check if we should wait for rate limits."""
        current_time = time.time()
        rate_info = self.progress_data["rate_limit_info"]
        
        # Reset window if needed (5 minute window)
        if current_time - rate_info["window_start"] > 300:
            rate_info["window_start"] = current_time
            rate_info["requests_in_window"] = 0
            
        # Check if we've hit rate limit (100 requests per 5 minutes)
        if rate_info["requests_in_window"] >= 100:
            wait_time = 300 - (current_time - rate_info["window_start"])
            if wait_time > 0:
                logger.warning(f"Rate limit reached. Waiting {wait_time:.0f} seconds...")
                time.sleep(wait_time)
                rate_info["window_start"] = current_time
                rate_info["requests_in_window"] = 0
                
        rate_info["requests_in_window"] += 1
        rate_info["last_request_time"] = current_time
        return True
    
    def resolve_from_bibtex(self, bibtex_path: Path, 
                           sources: Optional[List[str]] = None) -> Dict[str, str]:
        """Resolve DOIs from a BibTeX file.
        
        Args:
            bibtex_path: Path to BibTeX file
            sources: DOI sources to use (default: all)
            
        Returns:
            Dictionary mapping paper titles to DOIs
        """
        from scitex.io import load
        
        # Load BibTeX entries
        bibtex_path = Path(bibtex_path)
        logger.info(f"Loading BibTeX file: {bibtex_path}")
        
        try:
            entries = load(str(bibtex_path))
        except Exception as e:
            logger.error(f"Failed to load BibTeX: {e}")
            return {}
            
        # Convert to paper metadata
        papers_metadata = []
        for entry in entries:
            fields = entry.get("fields", {})
            
            # Extract metadata
            title = fields.get("title", "").strip()
            if not title:
                continue
                
            # Parse authors
            authors_str = fields.get("author", "")
            authors = self._parse_bibtex_authors(authors_str)
            
            # Extract year
            year = None
            if "year" in fields:
                try:
                    year = int(fields["year"])
                except:
                    pass
                    
            papers_metadata.append({
                "title": title,
                "authors": authors,
                "year": year,
                "journal": fields.get("journal", ""),
                "doi": fields.get("doi", "")  # Skip if already has DOI
            })
            
        # Update total count
        self.progress_data["statistics"]["total"] = len(papers_metadata)
        self._save_progress()
        
        # Resolve DOIs
        return self.resolve_batch(papers_metadata, sources)
    
    def resolve_batch(self, papers: List[Dict[str, Any]], 
                     sources: Optional[List[str]] = None) -> Dict[str, str]:
        """Resolve DOIs for a batch of papers.
        
        Args:
            papers: List of paper metadata dicts with 'title', 'authors', 'year'
            sources: DOI sources to use
            
        Returns:
            Dictionary mapping paper titles to resolved DOIs
        """
        results = {}
        
        # Update total if needed
        if self.progress_data["statistics"]["total"] == 0:
            self.progress_data["statistics"]["total"] = len(papers)
            self._save_progress()
        
        logger.info(f"Resolving DOIs for {len(papers)} papers...")
        
        # Create progress display
        progress = ProgressDisplay(
            total=len(papers),
            description="Resolving DOIs"
        )
        
        for i, paper in enumerate(papers):
            title = paper.get("title", "")
            if not title:
                continue
                
            # Generate paper key
            paper_key = self._get_paper_key(
                title, 
                paper.get("year"),
                paper.get("authors", [])
            )
            
            # Check if already processed
            if paper_key in self.progress_data["papers"]:
                paper_info = self.progress_data["papers"][paper_key]
                if paper_info["status"] == "resolved":
                    results[title] = paper_info["doi"]
                    logger.debug(f"Already resolved: {title[:50]}... -> {paper_info['doi']}")
                    progress.update(skipped=True)
                    continue
                elif paper_info["status"] == "failed" and paper_info.get("retry_count", 0) >= 3:
                    logger.debug(f"Skipping after 3 failures: {title[:50]}...")
                    self.progress_data["statistics"]["skipped"] += 1
                    progress.update(skipped=True)
                    continue
            
            # Skip if already has DOI
            if paper.get("doi"):
                results[title] = paper["doi"]
                self.progress_data["papers"][paper_key] = {
                    "title": title,
                    "doi": paper["doi"],
                    "status": "resolved",
                    "timestamp": datetime.now().isoformat(),
                    "source": "existing"
                }
                self.progress_data["statistics"]["resolved"] += 1
                self._save_progress()
                progress.update(success=True)
                continue
            
            # Check rate limit
            self._check_rate_limit()
            
            # Try to resolve DOI
            logger.info(f"[{i+1}/{len(papers)}] Resolving: {title[:60]}...")
            
            try:
                doi = self.doi_resolver.title_to_doi(
                    title=title,
                    year=paper.get("year"),
                    authors=paper.get("authors"),
                    sources=sources
                )
                
                if doi:
                    results[title] = doi
                    self.progress_data["papers"][paper_key] = {
                        "title": title,
                        "doi": doi,
                        "status": "resolved",
                        "timestamp": datetime.now().isoformat()
                    }
                    self.progress_data["statistics"]["resolved"] += 1
                    logger.success(f"  ✓ Found: {doi}")
                    progress.update(success=True)
                else:
                    # Track failure
                    retry_count = 0
                    if paper_key in self.progress_data["papers"]:
                        retry_count = self.progress_data["papers"][paper_key].get("retry_count", 0)
                    
                    self.progress_data["papers"][paper_key] = {
                        "title": title,
                        "status": "failed",
                        "timestamp": datetime.now().isoformat(),
                        "retry_count": retry_count + 1
                    }
                    self.progress_data["statistics"]["failed"] += 1
                    logger.warning(f"  ✗ No DOI found")
                    progress.update(success=False)
                    
            except Exception as e:
                logger.error(f"  ✗ Error: {e}")
                self.progress_data["papers"][paper_key] = {
                    "title": title,
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
                self.progress_data["statistics"]["failed"] += 1
                progress.update(success=False)
            
            # Update processed count and save
            self.progress_data["statistics"]["processed"] += 1
            self._save_progress()
                
        # Finish progress display
        progress.finish()
        
        # Mark as complete
        self.progress_data["completed"] = True
        self.progress_data["completed_at"] = datetime.now().isoformat()
        self.progress_data["duration_seconds"] = time.time() - self._start_time
        self._save_progress()
        
        # Show final summary
        self._show_summary()
        
        return results
    
    def _parse_bibtex_authors(self, authors_str: str) -> List[str]:
        """Parse BibTeX author string into list."""
        if not authors_str:
            return []
            
        # Handle "and" separator
        authors = authors_str.split(" and ")
        
        # Clean up each author
        cleaned = []
        for author in authors:
            author = author.strip()
            if author:
                cleaned.append(author)
                
        return cleaned
    
    def _show_progress(self):
        """Show current progress."""
        stats = self.progress_data["statistics"]
        progress_pct = (stats["processed"] / stats["total"] * 100) if stats["total"] > 0 else 0
        
        logger.info(
            f"Progress: {stats['processed']}/{stats['total']} ({progress_pct:.1f}%) | "
            f"Resolved: {stats['resolved']} | Failed: {stats['failed']}"
        )
    
    def _show_summary(self):
        """Show final summary."""
        stats = self.progress_data["statistics"]
        duration = time.time() - self._start_time
        
        logger.info("\n" + "="*60)
        logger.info("DOI Resolution Summary")
        logger.info("="*60)
        logger.info(f"Total papers: {stats['total']}")
        logger.info(f"Successfully resolved: {stats['resolved']} ({stats['resolved']/stats['total']*100:.1f}%)")
        logger.info(f"Failed: {stats['failed']}")
        logger.info(f"Skipped: {stats['skipped']}")
        logger.info(f"Duration: {duration:.1f} seconds")
        logger.info(f"Progress saved to: {self.progress_file}")
        logger.info("="*60)
    
    def get_results(self) -> Dict[str, str]:
        """Get all successfully resolved DOIs."""
        results = {}
        for paper_key, info in self.progress_data["papers"].items():
            if info["status"] == "resolved" and info.get("doi"):
                results[info["title"]] = info["doi"]
        return results
    
    def cleanup(self):
        """Remove progress file after successful completion."""
        if self.progress_data.get("completed") and self.progress_file.exists():
            self.progress_file.unlink()
            logger.info("Removed progress file")


# EOF