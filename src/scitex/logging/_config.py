#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-21 21:41:37 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/log/_config.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Configuration and setup for SciTeX logging."""

import logging
from typing import Optional, Union

from ._handlers import create_console_handler, create_file_handler, get_default_log_path
from ._levels import CRITICAL, DEBUG, ERROR, FAIL, INFO, SUCCESS, WARNING
from ._logger import setup_logger_class

# Global level variable
_GLOBAL_LEVEL = None
_FILE_LOGGING_ENABLED = True  # Enable file logging by default


def set_level(level: Union[str, int]):
    """Set global log level for all SciTeX loggers."""
    global _GLOBAL_LEVEL

    level_map = {
        "debug": DEBUG,
        "info": INFO,
        "warning": WARNING,
        "error": ERROR,
        "critical": CRITICAL,
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


def enable_file_logging(enabled: bool = True):
    """Enable or disable file logging globally."""
    global _FILE_LOGGING_ENABLED
    _FILE_LOGGING_ENABLED = enabled


def is_file_logging_enabled():
    """Check if file logging is enabled."""
    return _FILE_LOGGING_ENABLED


def configure(
    level: Union[str, int] = "info",
    log_file: Optional[str] = None,
    enable_file: bool = True,
    enable_console: bool = True,
    capture_prints: bool = True,
    max_file_size: int = 10 * 1024 * 1024,
    backup_count: int = 5,
):
    """Configure logging for SciTeX with both console and file output.

    Args:
        level: Log level (string or logging constant)
        log_file: Path to log file (default: ~/.scitex/logs/scitex-YYYY-MM-DD.log)
        enable_file: Whether to enable file logging
        enable_console: Whether to enable console logging
        capture_prints: Whether to capture print() statements to logs
        max_file_size: Maximum size of log file before rotation (default: 10MB)
        backup_count: Number of backup files to keep (default: 5)
    """
    # Setup custom logger class
    setup_logger_class()

    # Convert level if string
    level_map = {
        "debug": DEBUG,
        "info": INFO,
        "warning": WARNING,
        "error": ERROR,
        "critical": CRITICAL,
        "success": SUCCESS,
        "fail": FAIL,
    }

    if isinstance(level, str):
        level = level_map.get(level.lower(), level)

    # Set global level
    set_level(level)

    # Clear any existing handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    handlers = []

    # Add console handler if enabled
    if enable_console:
        console_handler = create_console_handler(level)
        handlers.append(console_handler)

    # Add file handler if enabled
    if enable_file and is_file_logging_enabled():
        if log_file is None:
            log_file = get_default_log_path()

        file_handler = create_file_handler(
            log_file, level, max_bytes=max_file_size, backup_count=backup_count
        )
        handlers.append(file_handler)

    # Configure basic logging with our handlers
    logging.basicConfig(
        level=level, handlers=handlers, force=True  # Force reconfiguration
    )

    # Enable print capture if requested
    if capture_prints:
        from ._print_capture import enable_print_capture

        enable_print_capture()


def get_log_path():
    """Get the current log file path."""
    for handler in logging.getLogger().handlers:
        if hasattr(handler, "baseFilename"):
            return handler.baseFilename
    return None


__all__ = [
    "set_level",
    "get_level",
    "enable_file_logging",
    "is_file_logging_enabled",
    "configure",
    "get_log_path",
]

# EOF
