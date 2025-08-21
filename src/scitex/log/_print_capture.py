#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Print capture system for SciTeX logging."""

import sys
import logging
from typing import Optional
from io import StringIO


class PrintCapture:
    """Capture print() output and redirect to logging system."""
    
    def __init__(self, logger_name: str = "scitex.print_capture"):
        self.logger = log.getLogger(logger_name)
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        self.capturing = False
        
    def start_capture(self):
        """Start capturing print output."""
        if self.capturing:
            return
            
        self.capturing = True
        sys.stdout = self
        
    def stop_capture(self):
        """Stop capturing print output."""
        if not self.capturing:
            return
            
        self.capturing = False
        sys.stdout = self.original_stdout
        
    def write(self, text):
        """Handle write calls from print()."""
        # Also write to original stdout for real-time viewing
        self.original_stdout.write(text)
        self.original_stdout.flush()
        
        # Log the output (strip newlines for cleaner logs)
        clean_text = text.rstrip('\n')
        if clean_text:  # Only log non-empty text
            self.logger.info(clean_text)
            
    def flush(self):
        """Handle flush calls."""
        self.original_stdout.flush()
        
    def isatty(self):
        """Handle isatty calls."""
        return self.original_stdout.isatty()
        
    def __enter__(self):
        """Context manager entry."""
        self.start_capture()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop_capture()


# Global print capture instance
_print_capture = None


def enable_print_capture(logger_name: str = "scitex.print_capture"):
    """Enable automatic print capture globally."""
    global _print_capture
    if _print_capture is None:
        _print_capture = PrintCapture(logger_name)
    _print_capture.start_capture()


def disable_print_capture():
    """Disable automatic print capture globally."""
    global _print_capture
    if _print_capture is not None:
        _print_capture.stop_capture()


def is_print_capture_enabled():
    """Check if print capture is currently enabled."""
    global _print_capture
    return _print_capture is not None and _print_capture.capturing


__all__ = [
    'PrintCapture',
    'enable_print_capture', 
    'disable_print_capture',
    'is_print_capture_enabled'
]