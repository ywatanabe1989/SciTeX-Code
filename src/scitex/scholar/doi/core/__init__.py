#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-04 23:50:00 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/doi/core/__init__.py
# ----------------------------------------

"""Core DOI resolution components.

This module contains focused, single-responsibility classes for core DOI resolution:
- SourceManager: Source instantiation, rotation, and lifecycle management
- ResultCacheManager: DOI caching, result persistence, and retrieval
- ConfigurationResolver: Email resolution, source configuration, validation
"""

from ._SourceManager import SourceManager
from ._ResultCacheManager import ResultCacheManager
from ._ConfigurationResolver import ConfigurationResolver

__all__ = [
    "SourceManager",
    "ResultCacheManager", 
    "ConfigurationResolver",
]