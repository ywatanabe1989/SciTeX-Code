#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-11 00:17:43 (ywatanabe)"
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

# Global format configuration via environment variable
# Options: default, minimal, detailed, debug, full
# SCITEX_LOG_FORMAT=debug python script.py
LOG_FORMAT = os.getenv("SCITEX_LOG_FORMAT", "default")

# Available format templates
FORMAT_TEMPLATES = {
    "minimal": "%(levelname)s: %(message)s",
    "default": "%(levelname)s: %(message)s",
    "detailed": "%(levelname)s: [%(name)s] %(message)s",
    "debug": "%(levelname)s: [%(filename)s:%(lineno)d - %(funcName)s()] %(message)s",
    "full": "%(asctime)s - %(levelname)s: [%(filename)s:%(lineno)d - %(name)s.%(funcName)s()] %(message)s",
}


class SciTeXConsoleFormatter(logging.Formatter):
    """Custom formatter with color support and configurable format."""

    # ANSI color codes for log levels
    COLORS = {
        "DEBU": "\033[90m",  # Grey
        "INFO": "\033[90m",  # Grey
        "SUCC": "\033[32m",  # Green
        "WARN": "\033[33m",  # Yellow
        "FAIL": "\033[91m",  # Light Red
        "ERRO": "\033[31m",  # Red
        "CRIT": "\033[35m",  # Magenta
    }

    # Color name to ANSI code mapping
    COLOR_NAMES = {
        "black": "\033[30m",
        "red": "\033[31m",
        "green": "\033[32m",
        "yellow": "\033[33m",
        "blue": "\033[34m",
        "magenta": "\033[35m",
        "cyan": "\033[36m",
        "white": "\033[37m",
        "grey": "\033[90m",
        "light_red": "\033[91m",
        "light_green": "\033[92m",
        "light_yellow": "\033[93m",
        "light_blue": "\033[94m",
        "light_magenta": "\033[95m",
        "light_cyan": "\033[96m",
    }

    RESET = "\033[0m"

    def __init__(self, fmt=None, indent_width=2):
        """
        Initialize with format from global config.

        Args:
            fmt: Format template string
            indent_width: Number of spaces per indent level (default: 2)
        """
        if fmt is None:
            fmt = FORMAT_TEMPLATES.get(LOG_FORMAT, FORMAT_TEMPLATES["default"])
        super().__init__(fmt)
        self.indent_width = indent_width

    def format(self, record):
        # Apply indentation if specified in record
        indent_level = getattr(record, "indent", 0)
        if indent_level > 0:
            indent = " " * (indent_level * self.indent_width)
            record.msg = f"{indent}{record.msg}"

        # Use parent formatter to apply template
        formatted = super().format(record)

        if hasattr(sys.stdout, "isatty") and sys.stdout.isatty():
            # Check for custom color override
            custom_color = getattr(record, "color", None)

            if custom_color and custom_color in self.COLOR_NAMES:
                # Use custom color
                color = self.COLOR_NAMES[custom_color]
                return f"{color}{formatted}{self.RESET}"
            else:
                # Use default color for log level
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
