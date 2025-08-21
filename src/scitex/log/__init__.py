#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-21 20:09:30 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/logging/__init__.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/logging/__init__.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Modular logging utilities for SciTeX.

⚠️  DEPRECATED: This module is deprecated. Use `scitex.log` instead.
    The `scitex.log` module will be removed in a future version.

This module provides enhanced logging capabilities with both console and file output,
ensuring consistent logging across the SciTeX package.

Migration:
    # OLD (deprecated)
    from scitex import log
    logger = log.getLogger(__name__)

    # NEW (recommended)
    from scitex import log
    logger = log.getLogger(__name__)

Usage:
    from scitex import log  # DEPRECATED
    logger = log.getLogger(__name__)
    logger.success("Operation completed successfully")
    logger.fail("Operation failed")

    # Configure logging with file output
    logging.configure(level='info', enable_file=True)

    # Get current log file location
    log_file = logging.get_log_path()
"""

import warnings

# Issue deprecation warning when module is imported
warnings.warn(
    "scitex.log is deprecated. Use scitex.log instead. "
    "The scitex.log module will be removed in a future version.",
    DeprecationWarning,
    stacklevel=2
)

import logging as _logging

# Import modular components
from ._levels import SUCCESS, FAIL, DEBUG, INFO, WARNING, ERROR, CRITICAL
from ._logger import SciTeXLogger, setup_logger_class
from ._formatters import SciTeXConsoleFormatter, SciTeXFileFormatter
from ._handlers import create_console_handler, create_file_handler, get_default_log_path
from ._config import (
    set_level,
    get_level,
    enable_file_logging,
    is_file_logging_enabled,
    configure,
    get_log_path
)
from ._print_capture import (
    PrintCapture,
    enable_print_capture,
    disable_print_capture,
    is_print_capture_enabled
)

# Re-export standard logging functions for compatibility
getLogger = _logging.getLogger
basicConfig = _logging.basicConfig
disable = _logging.disable

# Auto-configure logging on import with file logging enabled, print capture disabled by default
configure(level=INFO, enable_file=True, enable_console=True, capture_prints=False)

# Export only essential public functions - minimal API
__all__ = [
    # Core logging functions (most commonly used)
    'getLogger',

    # Log levels
    'DEBUG',
    'INFO',
    'WARNING',
    'ERROR',
    'CRITICAL',
    'SUCCESS',
    'FAIL',

    # Configuration (minimal set)
    'configure',
    'get_log_path',
]

# EOF
