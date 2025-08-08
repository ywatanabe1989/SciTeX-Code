#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-04 23:25:00 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/doi/batch/_BatchProgressManager.py
# ----------------------------------------

"""Progress tracking and persistence for batch DOI resolution."""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from scitex import logging

logger = logging.getLogger(__name__)


class BatchProgressManager:
    """Handles progress tracking, persistence, and ETA calculation for batch DOI resolution.
    
    Responsibilities:
    - Load/save progress data from/to files
    - Track successful and failed resolutions
    - Calculate processing statistics and ETA
    - Atomic file operations for progress persistence
    """

    def __init__(self, progress_file: Path, title_normalizer=None):
        """Initialize progress manager.
        
        Args:
            progress_file: Path to progress file
            title_normalizer: Function to normalize titles (for backward compatibility)
        """
        self.progress_file = Path(progress_file)
        self.progress_data = self._load_progress()
        self._start_time = time.time()
        self._title_normalizer = title_normalizer or self._default_normalize_title

    def _default_normalize_title(self, title: str) -> str:
        """Default title normalization for backward compatibility."""
        if not title:
            return ""
        # Remove common variations and normalize whitespace
        normalized = title.lower().strip()
        # Remove extra whitespace
        normalized = " ".join(normalized.split())
        return normalized

    def _load_progress(self) -> Dict[str, Any]:
        """Load or create progress data with enhanced fields."""
        if self.progress_file.exists():
            try:
                with open(self.progress_file, "r") as f:
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
            },
            "source_performance": {},  # Track which sources work best
            "processing_times": [],  # Track processing times for ETA
            "duplicate_groups": {},  # Track potential duplicates
        }

    def save_progress(self):
        """Save progress atomically."""
        self.progress_data["last_updated"] = datetime.now().isoformat()

        temp_file = self.progress_file.with_suffix(".tmp")
        try:
            with open(temp_file, "w") as f:
                json.dump(self.progress_data, f, indent=2)
            temp_file.replace(self.progress_file)
        except Exception as e:
            logger.error(f"Failed to save progress: {e}")
            if temp_file.exists():
                temp_file.unlink()

    def update_progress_success(self, title: str, doi: str):
        """Update progress for successful resolution."""
        paper_key = self._title_normalizer(title)
        self.progress_data["papers"][paper_key] = {
            "title": title,
            "doi": doi,
            "status": "resolved",
            "timestamp": datetime.now().isoformat(),
        }
        self.progress_data["statistics"]["resolved"] += 1
        self.progress_data["statistics"]["processed"] += 1

    def update_progress_failure(self, title: str):
        """Update progress for failed resolution."""
        paper_key = self._title_normalizer(title)
        self.progress_data["papers"][paper_key] = {
            "title": title,
            "status": "failed",
            "timestamp": datetime.now().isoformat(),
        }
        self.progress_data["statistics"]["failed"] += 1
        self.progress_data["statistics"]["processed"] += 1

    def update_progress_skipped(self, title: str, reason: str = "already_resolved"):
        """Update progress for skipped resolution."""
        paper_key = self._title_normalizer(title)
        self.progress_data["papers"][paper_key] = {
            "title": title,
            "status": "skipped",
            "reason": reason,
            "timestamp": datetime.now().isoformat(),
        }
        self.progress_data["statistics"]["skipped"] += 1
        self.progress_data["statistics"]["processed"] += 1

    def update_rate_limited(self):
        """Update rate limiting statistics."""
        self.progress_data["statistics"]["rate_limited"] += 1

    def set_total_papers(self, total: int):
        """Set total number of papers to process."""
        self.progress_data["statistics"]["total"] = total

    def get_paper_key(self, title: str) -> str:
        """Generate unique key for paper."""
        return self._title_normalizer(title)

    def is_paper_processed(self, title: str) -> bool:
        """Check if paper has already been processed."""
        paper_key = self.get_paper_key(title)
        return paper_key in self.progress_data["papers"]

    def get_paper_status(self, title: str) -> Optional[Dict[str, Any]]:
        """Get processing status for a paper."""
        paper_key = self.get_paper_key(title)
        return self.progress_data["papers"].get(paper_key)

    def calculate_eta(self) -> Optional[str]:
        """Calculate estimated time to completion."""
        stats = self.progress_data["statistics"]
        processed = stats["processed"]
        total = stats["total"]
        
        if processed == 0 or total == 0:
            return None
            
        elapsed = time.time() - self._start_time
        rate = processed / elapsed  # papers per second
        remaining = total - processed
        
        if rate <= 0:
            return None
            
        eta_seconds = remaining / rate
        
        # Format ETA nicely
        if eta_seconds < 60:
            return f"{eta_seconds:.0f}s"
        elif eta_seconds < 3600:
            return f"{eta_seconds/60:.1f}m"
        else:
            return f"{eta_seconds/3600:.1f}h"

    def get_progress_summary(self) -> Dict[str, Any]:
        """Get comprehensive progress summary."""
        stats = self.progress_data["statistics"]
        eta = self.calculate_eta()
        
        return {
            "total": stats["total"],
            "processed": stats["processed"],
            "resolved": stats["resolved"],
            "failed": stats["failed"],
            "skipped": stats["skipped"],
            "rate_limited": stats["rate_limited"],
            "success_rate": stats["resolved"] / stats["processed"] if stats["processed"] > 0 else 0,
            "eta": eta,
            "progress_file": str(self.progress_file),
        }

    def mark_completed(self):
        """Mark the batch processing as completed."""
        self.progress_data["completed"] = True
        self.progress_data["completed_at"] = datetime.now().isoformat()
        self.save_progress()

    def reset_progress(self):
        """Reset progress data to initial state."""
        self.progress_data = {
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
            },
            "source_performance": {},
            "processing_times": [],
            "duplicate_groups": {},
        }
        self._start_time = time.time()

    def add_processing_time(self, duration: float):
        """Add a processing time measurement for ETA calculation."""
        self.progress_data["processing_times"].append({
            "duration": duration,
            "timestamp": datetime.now().isoformat(),
        })
        
        # Keep only recent measurements (last 100) for performance
        if len(self.progress_data["processing_times"]) > 100:
            self.progress_data["processing_times"] = self.progress_data["processing_times"][-100:]

    def update_source_performance(self, source: str, success: bool):
        """Update source performance statistics."""
        if source not in self.progress_data["source_performance"]:
            self.progress_data["source_performance"][source] = {
                "attempts": 0,
                "successes": 0,
                "success_rate": 0.0,
            }
        
        perf = self.progress_data["source_performance"][source]
        perf["attempts"] += 1
        if success:
            perf["successes"] += 1
        perf["success_rate"] = perf["successes"] / perf["attempts"]


if __name__ == "__main__":
    # Example usage
    from pathlib import Path
    
    progress_file = Path("/tmp/test_progress.json")
    manager = BatchProgressManager(progress_file)
    
    # Simulate batch processing
    manager.set_total_papers(5)
    
    # Process some papers
    manager.update_progress_success("Test Paper 1", "10.1000/test1")
    manager.update_progress_failure("Test Paper 2")
    manager.update_progress_skipped("Test Paper 3", "duplicate")
    
    manager.save_progress()
    
    # Show summary
    summary = manager.get_progress_summary()
    print("Progress Summary:")
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    # Clean up
    if progress_file.exists():
        progress_file.unlink()