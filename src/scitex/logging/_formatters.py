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
import sys


class SciTeXConsoleFormatter(logging.Formatter):
    """Custom formatter with color support for terminal console."""

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

    def format(self, record):
        if hasattr(sys.stdout, "isatty") and sys.stdout.isatty():
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
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )


__all__ = ["SciTeXConsoleFormatter", "SciTeXFileFormatter"]

# EOF
