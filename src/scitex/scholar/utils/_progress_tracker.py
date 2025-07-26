#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---
# @Author: ywatanabe
# @Date: 2025-07-24
# @Description: Progress tracking for Scholar PDF downloads
# ---

import sys
import time
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import shutil
import threading


class ProgressTracker:
    """Progress tracker for PDF downloads with method visibility."""
    
    def __init__(self, total: int, show_progress: bool = True):
        self.total = total
        self.completed = 0
        self.failed = 0
        self.show_progress = show_progress
        self.start_time = time.time()
        self.current_file = ""
        self.current_method = ""
        self.method_attempts = {}  # Track attempts per file
        self.paper_status = {}  # Track status per paper
        self.terminal_width = shutil.get_terminal_size().columns
        self._last_print_length = 0
        self._lock = threading.Lock()  # Thread safety for concurrent updates
        self._active_downloads = {}  # Track active downloads per identifier
        
    def update(self, identifier: str, method: Optional[str] = None, 
               status: Optional[str] = None, completed: Optional[int] = None):
        """Update progress with current download info."""
        with self._lock:
            self.current_file = identifier
            
            if completed is not None:
                self.completed = completed
            
            if method:
                self.current_method = method
                # Track method attempts
                if identifier not in self.method_attempts:
                    self.method_attempts[identifier] = []
                self.method_attempts[identifier].append(method)
                # Track active download
                self._active_downloads[identifier] = method
                
            if status:
                self.paper_status[identifier] = status
                if status == "failed":
                    self.failed += 1
                elif status == "success":
                    # Remove from active downloads
                    self._active_downloads.pop(identifier, None)
                    
            if self.show_progress:
                self._print_progress()
    
    def _print_progress(self):
        """Print progress bar with current status."""
        # Calculate progress
        progress = self.completed / self.total if self.total > 0 else 0
        elapsed = time.time() - self.start_time
        
        # Calculate ETA
        if self.completed > 0 and progress < 1:
            eta_seconds = (elapsed / self.completed) * (self.total - self.completed)
            eta = str(timedelta(seconds=int(eta_seconds)))
        else:
            eta = "N/A"
        
        # Build progress bar
        bar_width = min(40, self.terminal_width - 60)
        filled = int(bar_width * progress)
        bar = "█" * filled + "░" * (bar_width - filled)
        
        # Build status line
        status_parts = [
            f"\r[{bar}] {progress*100:.1f}%",
            f"({self.completed}/{self.total})",
        ]
        
        if self.failed > 0:
            status_parts.append(f"Failed: {self.failed}")
            
        status_parts.append(f"ETA: {eta}")
        
        # Add current file and method on new line
        status_line = " ".join(status_parts)
        
        # Clear previous lines
        clear = "\033[K"  # Clear to end of line
        if self._last_print_length > 0:
            # Move up and clear previous lines
            sys.stdout.write(f"\033[{self._last_print_length}A")
            
        # Print status
        sys.stdout.write(f"{status_line}{clear}\n")
        
        # Show active downloads (up to 3 concurrent)
        lines_printed = 1
        max_file_len = self.terminal_width - 80
        max_shown = 3  # Only show up to 3 concurrent downloads
        
        for idx, (identifier, method) in enumerate(list(self._active_downloads.items())):
            if idx >= max_shown:
                break
                
            display_file = identifier
            if len(display_file) > max_file_len:
                display_file = "..." + display_file[-(max_file_len-3):]
            
            file_line = f"  → {display_file} [Method: {method}]"
            sys.stdout.write(f"{file_line}{clear}\n")
            lines_printed += 1
            
        # If there are more active downloads, show count
        if len(self._active_downloads) > max_shown:
            more_count = len(self._active_downloads) - max_shown
            sys.stdout.write(f"  ... and {more_count} more downloading in parallel{clear}\n")
            lines_printed += 1
            
        # Clear any remaining lines from previous print
        for _ in range(max(0, self._last_print_length - lines_printed)):
            sys.stdout.write(f"{clear}\n")
            
        self._last_print_length = lines_printed
        sys.stdout.flush()
    
    def finish(self):
        """Print final summary."""
        if not self.show_progress:
            return
            
        elapsed = time.time() - self.start_time
        success = self.completed - self.failed
        
        # Clear progress lines
        if self._last_print_length > 0:
            sys.stdout.write(f"\033[{self._last_print_length}A")
            sys.stdout.write("\033[K" * self._last_print_length)
            
        # Print summary
        print(f"\n✓ Download complete: {success}/{self.total} successful")
        
        if self.failed > 0:
            print(f"✗ Failed downloads: {self.failed}")
            
        print(f"⏱  Total time: {str(timedelta(seconds=int(elapsed)))}")
        
        # Print method statistics
        method_stats = {}
        for identifier, methods in self.method_attempts.items():
            for method in methods:
                method_stats[method] = method_stats.get(method, 0) + 1
                
        if method_stats:
            print("\n📊 Methods used:")
            for method, count in sorted(method_stats.items(), key=lambda x: -x[1]):
                print(f"  • {method}: {count} attempts")


class SimpleProgressLogger:
    """Fallback progress logger for non-terminal environments."""
    
    def __init__(self, total: int):
        self.total = total
        self.completed = 0
        self.failed = 0
        self.start_time = time.time()
        self._last_percent = -1
        
    def update(self, identifier: str, method: Optional[str] = None, 
               status: Optional[str] = None, completed: Optional[int] = None):
        """Update progress with simple output."""
        if completed is not None:
            self.completed = completed
            
        if status == "failed":
            self.failed += 1
            print(f"✗ Failed: {identifier}")
        elif status == "success":
            print(f"✓ Downloaded: {identifier}")
            
        # Print progress every 10%
        percent = int((self.completed / self.total) * 10) * 10
        if percent > self._last_percent:
            self._last_percent = percent
            print(f"Progress: {percent}% ({self.completed}/{self.total})")
            
    def finish(self):
        """Print final summary."""
        elapsed = time.time() - self.start_time
        success = self.completed - self.failed
        print(f"\n✓ Download complete: {success}/{self.total} successful")
        if self.failed > 0:
            print(f"✗ Failed downloads: {self.failed}")
        print(f"⏱  Total time: {str(timedelta(seconds=int(elapsed)))}")


def create_progress_tracker(total: int, show_progress: bool = True) -> Any:
    """Create appropriate progress tracker based on environment."""
    # Check if running in terminal
    is_terminal = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
    
    if show_progress and is_terminal:
        return ProgressTracker(total, show_progress=True)
    else:
        return SimpleProgressLogger(total)