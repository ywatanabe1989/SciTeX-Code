#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-01 02:47:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/utils/_progress_display.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/utils/_progress_display.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Progress display utilities for rsync-like output."""

import time
from datetime import datetime, timedelta
from typing import Optional

from scitex import logging

logger = logging.getLogger(__name__)


class ProgressDisplay:
    """Display progress with ETA like rsync."""
    
    def __init__(self, total: int, description: str = "Processing"):
        """Initialize progress display.
        
        Args:
            total: Total number of items
            description: Task description
        """
        self.total = total
        self.description = description
        self.processed = 0
        self.start_time = time.time()
        self.last_update = 0
        self._success_count = 0
        self._failed_count = 0
        self._skipped_count = 0
        
    def update(self, processed: Optional[int] = None, 
               success: bool = True, skipped: bool = False):
        """Update progress.
        
        Args:
            processed: Number of items processed (increments by 1 if None)
            success: Whether the last item succeeded
            skipped: Whether the last item was skipped
        """
        if processed is not None:
            self.processed = processed
        else:
            self.processed += 1
            
        # Update counts
        if skipped:
            self._skipped_count += 1
        elif success:
            self._success_count += 1
        else:
            self._failed_count += 1
            
        # Only update display every 0.5 seconds or on significant progress
        current_time = time.time()
        if (current_time - self.last_update < 0.5 and 
            self.processed < self.total and 
            self.processed % max(1, self.total // 20) != 0):
            return
            
        self.last_update = current_time
        self._display()
        
    def _display(self):
        """Display current progress."""
        if self.total == 0:
            return
            
        # Calculate progress
        progress_pct = (self.processed / self.total) * 100
        elapsed = time.time() - self.start_time
        
        # Calculate rate and ETA
        if self.processed > 0 and elapsed > 0:
            rate = self.processed / elapsed
            remaining = self.total - self.processed
            eta_seconds = remaining / rate if rate > 0 else 0
            eta = self._format_time(eta_seconds)
            elapsed_str = self._format_time(elapsed)
            
            # Format rate
            if rate >= 1:
                rate_str = f"{rate:.1f} items/s"
            else:
                rate_str = f"{1/rate:.1f} s/item"
        else:
            eta = "calculating..."
            elapsed_str = "0:00"
            rate_str = "-- items/s"
            
        # Build progress bar
        bar_width = 30
        filled = int(bar_width * self.processed / self.total)
        bar = "=" * filled + ">" + " " * (bar_width - filled - 1)
        
        # Build status counts
        status_parts = []
        if self._success_count > 0:
            status_parts.append(f"✓{self._success_count}")
        if self._failed_count > 0:
            status_parts.append(f"✗{self._failed_count}")
        if self._skipped_count > 0:
            status_parts.append(f"↷{self._skipped_count}")
        status_str = " ".join(status_parts) if status_parts else ""
        
        # Display progress line (rsync-style)
        progress_line = (
            f"\r{self.description}: [{bar}] "
            f"{self.processed}/{self.total} "
            f"({progress_pct:5.1f}%) "
            f"{status_str:15s} "
            f"{rate_str:12s} "
            f"elapsed: {elapsed_str:>6s} "
            f"eta: {eta:>6s}"
        )
        
        # Use print with end='' for overwriting line
        print(progress_line, end='', flush=True)
        
    def _format_time(self, seconds: float) -> str:
        """Format seconds as MM:SS or HH:MM:SS."""
        if seconds < 0:
            return "0:00"
            
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes}:{secs:02d}"
            
    def finish(self, message: Optional[str] = None):
        """Finish progress display."""
        # Final update
        self._display()
        print()  # New line after progress
        
        # Show summary
        elapsed = time.time() - self.start_time
        if message:
            logger.info(message)
        else:
            logger.info(
                f"{self.description} complete: "
                f"{self.processed}/{self.total} items in {self._format_time(elapsed)} "
                f"(✓{self._success_count} ✗{self._failed_count} ↷{self._skipped_count})"
            )


def create_progress_display(total: int, description: str = "Processing") -> ProgressDisplay:
    """Create a progress display instance."""
    return ProgressDisplay(total, description)


# Example usage
if __name__ == "__main__":
    import random
    
    # Simulate processing
    progress = ProgressDisplay(100, "Resolving DOIs")
    
    for i in range(100):
        # Simulate work
        time.sleep(random.uniform(0.05, 0.2))
        
        # Simulate success/failure
        if random.random() < 0.1:
            progress.update(success=False)
        elif random.random() < 0.05:
            progress.update(skipped=True)
        else:
            progress.update(success=True)
    
    progress.finish()

# EOF