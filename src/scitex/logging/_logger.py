#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-21 21:43:19 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/log/_logger.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Enhanced logger class for SciTeX."""

import logging

from ._levels import FAIL, SUCCESS


class SciTeXLogger(logging.Logger):
    """Enhanced logger with success/fail methods, indent, and separator support."""

    def _log_with_indent(self, level, message, indent=0, sep=None, n=40, *args, **kwargs):
        """Internal method to log with indent and separator support."""
        # Add separator lines if requested
        if sep is not None:
            separator = sep * n
            message = f"\n{separator}\n{message}\n{separator}"

        # Add indent info to extra
        if indent > 0 or sep is not None:
            extra = kwargs.get('extra', {})
            extra['indent'] = indent
            kwargs['extra'] = extra

        self._log(level, message, args, **kwargs)

    def debug(self, message, indent=0, sep=None, n=40, *args, **kwargs):
        """Log a debug message with optional indent and separator."""
        if self.isEnabledFor(logging.DEBUG):
            self._log_with_indent(logging.DEBUG, message, indent, sep, n, *args, **kwargs)

    def info(self, message, indent=0, sep=None, n=40, *args, **kwargs):
        """Log an info message with optional indent and separator."""
        if self.isEnabledFor(logging.INFO):
            self._log_with_indent(logging.INFO, message, indent, sep, n, *args, **kwargs)

    def warning(self, message, indent=0, sep=None, n=40, *args, **kwargs):
        """Log a warning message with optional indent and separator."""
        if self.isEnabledFor(logging.WARNING):
            self._log_with_indent(logging.WARNING, message, indent, sep, n, *args, **kwargs)

    def error(self, message, indent=0, sep=None, n=40, *args, **kwargs):
        """Log an error message with optional indent and separator."""
        if self.isEnabledFor(logging.ERROR):
            self._log_with_indent(logging.ERROR, message, indent, sep, n, *args, **kwargs)

    def critical(self, message, indent=0, sep=None, n=40, *args, **kwargs):
        """Log a critical message with optional indent and separator."""
        if self.isEnabledFor(logging.CRITICAL):
            self._log_with_indent(logging.CRITICAL, message, indent, sep, n, *args, **kwargs)

    def success(self, message, indent=0, sep=None, n=40, *args, **kwargs):
        """Log a success message with optional indent and separator."""
        if self.isEnabledFor(SUCCESS):
            self._log_with_indent(SUCCESS, message, indent, sep, n, *args, **kwargs)

    def fail(self, message, indent=0, sep=None, n=40, *args, **kwargs):
        """Log a failure message with optional indent and separator."""
        if self.isEnabledFor(FAIL):
            self._log_with_indent(FAIL, message, indent, sep, n, *args, **kwargs)


def setup_logger_class():
    """Setup the custom logger class."""
    # Set custom logger class before any logger creation
    logging.setLoggerClass(SciTeXLogger)

    # Force existing root logger to use custom class
    root = logging.getLogger()
    root.__class__ = SciTeXLogger


__all__ = ["SciTeXLogger", "setup_logger_class"]

# EOF
