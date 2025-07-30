#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Logging utilities for SciTeX.

This module provides a simple wrapper around Python's logging module
to ensure consistent logging across the SciTeX package.
"""

import logging
import sys

# Re-export logging functions
getLogger = logging.getLogger
basicConfig = logging.basicConfig
DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL

# Configure default logging
def configure_logging(level=logging.INFO):
    """Configure default logging settings for SciTeX."""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        stream=sys.stdout
    )

# Export all
__all__ = [
    'getLogger',
    'basicConfig',
    'configure_logging',
    'DEBUG',
    'INFO',
    'WARNING', 
    'ERROR',
    'CRITICAL'
]