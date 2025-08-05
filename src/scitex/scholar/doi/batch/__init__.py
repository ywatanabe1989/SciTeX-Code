#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-04 23:25:00 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/doi/batch/__init__.py
# ----------------------------------------

"""Batch DOI resolution components.

This module contains focused, single-responsibility classes for batch DOI resolution:
- BatchProgressManager: Progress tracking and persistence
- MetadataEnhancer: Paper metadata processing and validation
- BatchConfigurationManager: Configuration resolution and validation
- LibraryStructureCreator: Scholar library organization and management
"""

from ._BatchProgressManager import BatchProgressManager
from ._MetadataEnhancer import MetadataEnhancer
from ._BatchConfigurationManager import BatchConfigurationManager
from ._LibraryStructureCreator import LibraryStructureCreator

__all__ = [
    "BatchProgressManager",
    "MetadataEnhancer", 
    "BatchConfigurationManager",
    "LibraryStructureCreator",
]