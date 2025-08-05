#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-01 02:42:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/open_url/_ResumableOpenURLResolver.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/open_url/_ResumableOpenURLResolver.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Resumable OpenURL resolver for publisher URLs."""

import asyncio
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from scitex import logging
from ._OpenURLResolver import OpenURLResolver
from ..utils._progress_display import ProgressDisplay

logger = logging.getLogger(__name__)


class ResumableOpenURLResolver:
    """Resolves publisher URLs via OpenURL with resume capability.
    
    Creates a progress file to track:
    - Which DOIs have been processed
    - Successfully resolved URLs
    - Failed resolutions for retry
    - Rate limit tracking
    """
    
    def __init__(self, auth_manager, resolver_url: Optional[str] = None,
                 progress_file: Optional[Path] = None, 
                 concurrency: int = 2):
        """Initialize resumable OpenURL resolver.
        
        Args:
            auth_manager: Authentication manager for institutional access
            resolver_url: OpenURL resolver URL (e.g., UniMelb)
            progress_file: Path to progress tracking file
            concurrency: Max concurrent resolutions (default: 2 for politeness)
        """
        self.auth_manager = auth_manager
        self.resolver_url = resolver_url or os.getenv("SCITEX_SCHOLAR_OPENURL_RESOLVER_URL")
        self.concurrency = concurrency
        
        # Set up progress tracking
        if progress_file:
            self.progress_file = Path(progress_file)
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.progress_file = Path(f"openurl_resolution_{timestamp}.progress.json")
            
        self.progress_data = self._load_progress()
        self._start_time = time.time()
        
    def _load_progress(self) -> Dict[str, Any]:
        """Load existing progress or create new."""
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r') as f:
                    data = json.load(f)
                logger.info(f"Resuming OpenURL resolution from: {self.progress_file}")
                return data
            except Exception as e:
                logger.warning(f"Could not load progress file: {e}")
                
        # Create new progress data
        return {
            "version": 1,
            "started_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "completed": False,
            "resolver_url": self.resolver_url,
            "dois": {},  # doi -> resolution status
            "statistics": {
                "total": 0,
                "processed": 0,
                "resolved": 0,
                "failed": 0,
                "no_access": 0,
                "errors": 0
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
    
    async def resolve_from_dois_async(self, dois: List[str]) -> Dict[str, Dict[str, Any]]:
        """Resolve publisher URLs for a list of DOIs.
        
        Args:
            dois: List of DOI strings
            
        Returns:
            Dictionary mapping DOIs to resolution results
        """
        # Update total
        self.progress_data["statistics"]["total"] = len(dois)
        self._save_progress()
        
        results = {}
        
        # Filter out already processed DOIs
        dois_to_process = []
        for doi in dois:
            if doi in self.progress_data["dois"]:
                doi_info = self.progress_data["dois"][doi]
                if doi_info["status"] == "resolved":
                    results[doi] = doi_info["result"]
                    logger.debug(f"Already resolved: {doi} -> {doi_info['result']['final_url']}")
                    continue
                elif doi_info["status"] == "failed" and doi_info.get("retry_count", 0) >= 3:
                    logger.debug(f"Skipping after 3 failures: {doi}")
                    continue
            dois_to_process.append(doi)
        
        if not dois_to_process:
            logger.info("All DOIs already processed")
            return results
        
        logger.info(f"Resolving {len(dois_to_process)} DOIs via OpenURL...")
        
        # Create progress display
        progress = ProgressDisplay(
            total=len(dois_to_process),
            description="Resolving URLs"
        )
        
        # Process in batches with concurrency control
        batch_size = self.concurrency
        for i in range(0, len(dois_to_process), batch_size):
            batch = dois_to_process[i:i + batch_size]
            
            # Create resolver instance for this batch
            async with OpenURLResolver(self.auth_manager, self.resolver_url) as resolver:
                # Process batch
                batch_results = await resolver._resolve_parallel_async(batch, self.concurrency)
                
                # Process results
                for doi, result in zip(batch, batch_results):
                    if result and result.get("success"):
                        results[doi] = result
                        self.progress_data["dois"][doi] = {
                            "status": "resolved",
                            "result": result,
                            "timestamp": datetime.now().isoformat()
                        }
                        self.progress_data["statistics"]["resolved"] += 1
                        logger.success(f"  ✓ {doi} -> {result['final_url']}")
                        progress.update(success=True)
                    
                    elif result and result.get("access_type") == "no_access":
                        self.progress_data["dois"][doi] = {
                            "status": "no_access",
                            "result": result,
                            "timestamp": datetime.now().isoformat()
                        }
                        self.progress_data["statistics"]["no_access"] += 1
                        logger.warning(f"  ⚠ {doi} -> No institutional access")
                        progress.update(success=False)
                    
                    else:
                        # Track failure
                        retry_count = 0
                        if doi in self.progress_data["dois"]:
                            retry_count = self.progress_data["dois"][doi].get("retry_count", 0)
                        
                        self.progress_data["dois"][doi] = {
                            "status": "failed",
                            "result": result,
                            "timestamp": datetime.now().isoformat(),
                            "retry_count": retry_count + 1
                        }
                        self.progress_data["statistics"]["failed"] += 1
                        logger.warning(f"  ✗ {doi} -> Failed")
                        progress.update(success=False)
                    
                    self.progress_data["statistics"]["processed"] += 1
                    self._save_progress()
            
            # Small delay between batches
            if i + batch_size < len(dois_to_process):
                await asyncio.sleep(2)
        
        # Finish progress display
        progress.finish()
        
        # Mark complete
        self.progress_data["completed"] = True
        self.progress_data["completed_at"] = datetime.now().isoformat()
        self.progress_data["duration_seconds"] = time.time() - self._start_time
        self._save_progress()
        
        self._show_async_summary()
        return results
    
    def resolve_from_dois(self, dois: List[str]) -> Dict[str, Dict[str, Any]]:
        """Synchronous wrapper for resolve_from_dois_async."""
        try:
            loop = asyncio.get_running_loop()
            import nest_asyncio
            nest_asyncio.apply()
            return asyncio.run(self.resolve_from_dois_async(dois))
        except RuntimeError:
            return asyncio.run(self.resolve_from_dois_async(dois))
    
    def resolve_from_papers(self, papers: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Resolve URLs for papers with DOIs.
        
        Args:
            papers: List of paper dicts with 'doi' field
            
        Returns:
            Dictionary mapping DOIs to resolution results
        """
        # Extract DOIs
        dois = []
        for paper in papers:
            doi = paper.get("doi")
            if doi:
                dois.append(doi)
            else:
                title = paper.get("title", "Unknown")
                logger.debug(f"Skipping paper without DOI: {title[:50]}...")
        
        if not dois:
            logger.warning("No papers with DOIs to resolve")
            return {}
        
        return self.resolve_from_dois(dois)
    
    def _show_async_progress(self):
        """Show current progress."""
        stats = self.progress_data["statistics"]
        progress_pct = (stats["processed"] / stats["total"] * 100) if stats["total"] > 0 else 0
        
        logger.info(
            f"Progress: {stats['processed']}/{stats['total']} ({progress_pct:.1f}%) | "
            f"Resolved: {stats['resolved']} | No access: {stats['no_access']} | "
            f"Failed: {stats['failed']}"
        )
    
    def _show_async_summary(self):
        """Show final summary."""
        stats = self.progress_data["statistics"]
        duration = time.time() - self._start_time
        
        logger.info("\n" + "="*60)
        logger.info("OpenURL Resolution Summary")
        logger.info("="*60)
        logger.info(f"Resolver: {self.resolver_url}")
        logger.info(f"Total DOIs: {stats['total']}")
        logger.info(f"Successfully resolved: {stats['resolved']} ({stats['resolved']/stats['total']*100:.1f}%)")
        logger.info(f"No institutional access: {stats['no_access']}")
        logger.info(f"Failed: {stats['failed']}")
        logger.info(f"Duration: {duration:.1f} seconds")
        logger.info(f"Progress saved to: {self.progress_file}")
        logger.info("="*60)
    
    def get_results(self) -> Dict[str, str]:
        """Get all successfully resolved URLs."""
        results = {}
        for doi, info in self.progress_data["dois"].items():
            if info["status"] == "resolved" and info.get("result", {}).get("final_url"):
                results[doi] = info["result"]["final_url"]
        return results
    
    def cleanup(self):
        """Remove progress file after successful completion."""
        if self.progress_data.get("completed") and self.progress_file.exists():
            self.progress_file.unlink()
            logger.info("Removed progress file")


# EOF