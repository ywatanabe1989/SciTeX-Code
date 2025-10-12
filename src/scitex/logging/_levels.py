#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Custom log levels for SciTeX."""

import logging

# Custom log levels for success/fail
SUCCESS = 31  # Between WARNING (30) and ERROR (40)
FAIL = 35     # Between WARNING (30) and ERROR (40)

# Add custom levels to logging module with 4-character abbreviations
logging.addLevelName(SUCCESS, 'SUCC')
logging.addLevelName(FAIL, 'FAIL')
logging.addLevelName(logging.DEBUG, 'DEBU')
logging.addLevelName(logging.INFO, 'INFO')
logging.addLevelName(logging.WARNING, 'WARN')
logging.addLevelName(logging.ERROR, 'ERRO')
logging.addLevelName(logging.CRITICAL, 'CRIT')

# Standard levels for convenience
DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL

__all__ = [
    'SUCCESS',
    'FAIL',
    'DEBUG',
    'INFO',
    'WARNING', 
    'ERROR',
    'CRITICAL'
]