#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Custom formatters for SciTeX logging."""

import logging
import sys


class SciTeXConsoleFormatter(logging.Formatter):
    """Custom formatter with color support for terminal console."""

    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[30m',     # Black
        'INFO': '\033[30m',      # Black
        'SUCCESS': '\033[32m',   # Green
        'WARNING': '\033[33m',   # Yellow
        'FAIL': '\033[91m',      # Light Red
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
    }
    RESET = '\033[0m'

    def format(self, record):
        """Format the log record with colors for terminal output."""
        if hasattr(sys.stdout, 'isatty') and sys.stdout.isatty():
            levelname = record.levelname
            if levelname in self.COLORS:
                color = self.COLORS[levelname]
                message = record.getMessage()
                return f"{color}{levelname}: {message}{self.RESET}"
        return super().format(record)


class SciTeXFileFormatter(logging.Formatter):
    """Custom formatter for file output without colors."""

    def __init__(self):
        super().__init__(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )


__all__ = ['SciTeXConsoleFormatter', 'SciTeXFileFormatter']