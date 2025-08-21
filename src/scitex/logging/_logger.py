#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Enhanced logger class for SciTeX."""

import logging
from ._levels import SUCCESS, FAIL


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


def setup_logger_class():
    """Setup the custom logger class."""
    # Set custom logger class before any logger creation
    logging.setLoggerClass(SciTeXLogger)
    
    # Force existing root logger to use custom class
    root = logging.getLogger()
    root.__class__ = SciTeXLogger


__all__ = ['SciTeXLogger', 'setup_logger_class']