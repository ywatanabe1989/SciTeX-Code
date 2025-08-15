#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-31 01:16:30 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/logging/__init__.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/logging/__init__.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

__FILE__ = ("./src/scitex/logging/__init__.py")

"""Logging utilities for SciTeX.

This module provides a simple wrapper around Python's logging module
to ensure consistent logging across the SciTeX package."""

import logging
import sys

# Custom log levels for success/fail
SUCCESS = 31  # Between WARNING (30) and ERROR (40)
FAIL = 35     # Between WARNING (30) and ERROR (40)

# Add custom levels
logging.addLevelName(SUCCESS, 'SUCCESS')
logging.addLevelName(FAIL, 'FAIL')

# Create enhanced logger class
class SciTeXLogger(logging.Logger):
    """Enhanced logger with success/fail methods."""

    def success(self, message, *args, **kwargs):
        """Log a success message."""
        if self.isEnabledFor(SUCCESS):
            self._log(SUCCESS, message, args, **kwargs)

    def fail(self, message, *args, **kwargs):
        """Log a failure message."""
        if self.isEnabledFor(FAIL):
            self._log(FAIL, message, args, **kwargs)

# Set custom logger class before any logger creation
logging.setLoggerClass(SciTeXLogger)

# Force existing root logger to use custom class
root = logging.getLogger()
root.__class__ = SciTeXLogger

# Custom formatter that handles success/fail nicely
class SciTeXFormatter(logging.Formatter):
    """Custom formatter with color support for terminals."""

    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[30m',     # Cyan
        'INFO': '\033[30m',      # Black
        'SUCCESS': '\033[32m',   # Green
        'WARNING': '\033[33m',   # Yellow
        'FAIL': '\033[91m',      # Light Red
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
    }
    RESET = '\033[0m'

    def format(self, record):
        if hasattr(sys.stdout, 'isatty') and sys.stdout.isatty():
            levelname = record.levelname
            if levelname in self.COLORS:
                color = self.COLORS[levelname]
                message = record.getMessage()
                return f"{color}{levelname}: {message}{self.RESET}"
        return super().format(record)

    # def format(self, record):
    #     # Add color if outputting to terminal
    #     if hasattr(sys.stdout, 'isatty') and sys.stdout.isatty():
    #         levelname = record.levelname
    #         if levelname in self.COLORS:
    #             # Color the entire message, not just the levelname
    #             original_msg = record.getMessage()
    #             colored_msg = f"{self.COLORS[levelname]}{original_msg}{self.RESET}"
    #             record.msg = colored_msg
    #             record.args = ()

    #     return super().format(record)

# Configure default logging
# Global level variable
_GLOBAL_LEVEL = None

def set_level(level):
    """Set global log level for all SciTeX loggers."""
    global _GLOBAL_LEVEL

    level_map = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
        "success": SUCCESS,
        "fail": FAIL,
    }

    if isinstance(level, str):
        level = level_map.get(level.lower(), level)

    _GLOBAL_LEVEL = level
    logging.getLogger().setLevel(level)

    # Update all existing handlers
    for handler in logging.getLogger().handlers:
        handler.setLevel(level)

def get_level():
    """Get current global log level."""
    return _GLOBAL_LEVEL or logging.getLogger().level

def configure_logging(level="info"):
    """Configure default logging settings for SciTeX."""
    level_map = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
        "success": SUCCESS,
        "fail": FAIL,
    }

    if isinstance(level, str):
        level = level_map.get(level.lower(), level)

    set_level(level)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(SciTeXFormatter(
        fmt='%(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    ))
    logging.basicConfig(level=level, handlers=[handler])

# def configure_logging(level="info"):
#     """Configure default logging settings for SciTeX."""
#     level_map = {
#         "debug": logging.DEBUG,
#         "info": logging.INFO,
#         "warning": logging.WARNING,
#         "error": logging.ERROR,
#         "critical": logging.CRITICAL,
#         "success": SUCCESS,
#         "fail": FAIL,
#     }
#     if isinstance(level, str):
#         level = level_map.get(level.lower(), level)
#     else:
#         level = level

#     handler = logging.StreamHandler(sys.stdout)
#     handler.setFormatter(
#         SciTeXFormatter(
#             # fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#             fmt='%(levelname)s: %(message)s',
#             datefmt='%Y-%m-%d %H:%M:%S'
#         )
#     )

#     logging.basicConfig(level=level, handlers=[handler])

# Auto-configure logging on import
configure_logging(level=logging.INFO)

# Re-export logging functions to maintain compatibility with standard logging
getLogger = logging.getLogger
basicConfig = logging.basicConfig
disable = logging.disable  # Add disable method for standard logging compatibility
DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL

# Export all
__all__ = [
    'getLogger',
    'basicConfig',
    'disable',  # Standard logging compatibility
    'configure_logging',
    'DEBUG',
    'INFO',
    'WARNING',
    'ERROR',
    'CRITICAL',
    'SUCCESS',
    'FAIL',
    'SciTeXLogger'
]

"""
from scitex import logging
logger = logging.getLogger()
logger.success("hello")
"""

# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-07-30 23:03:18 (ywatanabe)"
# # File: /home/ywatanabe/proj/scitex_repo/src/scitex/logging/__init__.py
# # ----------------------------------------
# from __future__ import annotations
# import os
# __FILE__ = (
#     "./src/scitex/logging/__init__.py"
# )
# __DIR__ = os.path.dirname(__FILE__)
# # ----------------------------------------
# """
# Logging utilities for SciTeX.

# This module provides a simple wrapper around Python's logging module
# to ensure consistent logging across the SciTeX package.
# """

# import logging
# import sys

# # Custom log levels for success/fail
# SUCCESS = 31  # Between WARNING (30) and ERROR (40)
# FAIL = 35     # Between WARNING (30) and ERROR (40)

# # Add custom levels
# logging.addLevelName(SUCCESS, 'SUCCESS')
# logging.addLevelName(FAIL, 'FAIL')

# # Create enhanced logger class
# class SciTeXLogger(logging.Logger):
#     """Enhanced logger with success/fail methods."""

#     def success(self, message, *args, **kwargs):
#         """Log a success message."""
#         if self.isEnabledFor(SUCCESS):
#             self._log(SUCCESS, message, args, **kwargs)

#     def fail(self, message, *args, **kwargs):
#         """Log a failure message."""
#         if self.isEnabledFor(FAIL):
#             self._log(FAIL, message, args, **kwargs)

# # Set custom logger class
# logging.setLoggerClass(SciTeXLogger)

# # Re-export logging functions
# getLogger = logging.getLogger
# basicConfig = logging.basicConfig
# DEBUG = logging.DEBUG
# INFO = logging.INFO
# WARNING = logging.WARNING
# ERROR = logging.ERROR
# CRITICAL = logging.CRITICAL

# # Custom formatter that handles success/fail nicely
# class SciTeXFormatter(logging.Formatter):
#     """Custom formatter with color support for terminals."""

#     # ANSI color codes
#     COLORS = {
#         'DEBUG': '\033[36m',     # Cyan
#         'INFO': '\033[0m',       # Default
#         'SUCCESS': '\033[32m',   # Green
#         'WARNING': '\033[33m',   # Yellow
#         'FAIL': '\033[91m',      # Light Red
#         'ERROR': '\033[31m',     # Red
#         'CRITICAL': '\033[35m',  # Magenta
#     }
#     RESET = '\033[0m'

#     def format(self, record):
#         # Add color if outputting to terminal
#         if hasattr(sys.stdout, 'isatty') and sys.stdout.isatty():
#             levelname = record.levelname
#             if levelname in self.COLORS:
#                 record.levelname = f"{self.COLORS[levelname]}{levelname}{self.RESET}"
#         return super().format(record)

# # Configure default logging
# def configure_logging(level=logging.INFO):
#     """Configure default logging settings for SciTeX."""
#     handler = logging.StreamHandler(sys.stdout)
#     handler.setFormatter(SciTeXFormatter(
#         fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#         datefmt='%Y-%m-%d %H:%M:%S'
#     ))

#     logging.basicConfig(
#         level=level,
#         handlers=[handler]
#     )

# # Export all
# __all__ = [
#     'getLogger',
#     'basicConfig',
#     'configure_logging',
#     'DEBUG',
#     'INFO',
#     'WARNING',
#     'ERROR',
#     'CRITICAL',
#     'SUCCESS',
#     'FAIL',
#     'SciTeXLogger'
# ]

# # EOF

# EOF
