#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-04 23:25:00 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/doi/batch/__init__.py
# ----------------------------------------

"""Batch DOI resolution components.

This module contains focused, single-responsibility classes for batch DOI resolution:
- ProgressManagerForBatchDOIResolution: Progress tracking and persistence
- MetadataHandlerForBatchDOIResolution: Paper metadata processing and validation
- SourceStatsManagerForBatchDOIResolution: Configuration resolution and validation
- LibraryManager: Scholar library organization and management
"""

from ._ProgressManagerForBatchDOIResolution import ProgressManagerForBatchDOIResolution
from ._MetadataHandlerForBatchDOIResolution import MetadataHandlerForBatchDOIResolution
from ._SourceStatsManagerForBatchDOIResolution import SourceStatsManagerForBatchDOIResolution

__all__ = [
    "ProgressManagerForBatchDOIResolution",
    "MetadataHandlerForBatchDOIResolution",
    "SourceStatsManagerForBatchDOIResolution",
]
