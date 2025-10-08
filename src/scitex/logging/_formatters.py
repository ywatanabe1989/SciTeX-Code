#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-08 05:01:13 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/logging/_formatters.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/logging/_formatters.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

__FILE__ = __file__
"""Custom formatters for SciTeX logging."""

import logging
import os
import sys

# Global format configuration via environment variable
# Options: simple, detailed, debug, minimal
# SCITEX_LOG_FORMAT=debug python script.py
LOG_FORMAT = os.getenv("SCITEX_LOG_FORMAT", "simple")

# Available format templates
FORMAT_TEMPLATES = {
    "minimal": "%(levelname)s: %(message)s",
    "simple": "%(levelname)s: %(message)s",
    "detailed": "%(levelname)s: [%(name)s] %(message)s",
    "debug": "%(levelname)s: [%(filename)s:%(lineno)d - %(funcName)s()] %(message)s",
    "full": "%(asctime)s - %(levelname)s: [%(filename)s:%(lineno)d - %(name)s.%(funcName)s()] %(message)s",
}


class SciTeXConsoleFormatter(logging.Formatter):
    """Custom formatter with color support and configurable format."""

    # ANSI color codes
    COLORS = {
        "DEBU": "\033[30m",  # Black
        "INFO": "\033[30m",  # Black
        "SUCC": "\033[32m",  # Green
        "WARN": "\033[33m",  # Yellow
        "FAIL": "\033[91m",  # Light Red
        "ERRO": "\033[31m",  # Red
        "CRIT": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"

    def __init__(self, fmt=None):
        """Initialize with format from global config."""
        if fmt is None:
            fmt = FORMAT_TEMPLATES.get(LOG_FORMAT, FORMAT_TEMPLATES["simple"])
        super().__init__(fmt)

    def format(self, record):
        # Use parent formatter to apply template
        formatted = super().format(record)

        if hasattr(sys.stdout, "isatty") and sys.stdout.isatty():
            levelname = record.levelname
            if levelname in self.COLORS:
                color = self.COLORS[levelname]
                return f"{color}{formatted}{self.RESET}"

        return formatted


class SciTeXFileFormatter(logging.Formatter):
    """Custom formatter for file output without colors."""

    def __init__(self):
        super().__init__(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )


__all__ = [
    "SciTeXConsoleFormatter",
    "SciTeXFileFormatter",
    "LOG_FORMAT",
    "FORMAT_TEMPLATES",
]

# EOF
