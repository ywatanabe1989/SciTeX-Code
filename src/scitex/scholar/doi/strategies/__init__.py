#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-04 22:45:00 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/doi/strategies/__init__.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/doi/strategies/__init__.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""DOI resolution strategies module.

This module contains strategy classes that handle specific aspects of DOI resolution
following the Single Responsibility Principle. Each strategy focuses on one concern:

- ScholarLibraryStrategy: Scholar library lookup, storage, and project management
- SourceResolutionStrategy: Core DOI resolution from multiple API sources
- ResolutionOrchestrator: Complete workflow coordination with enrichment
"""

from ._ScholarLibraryStrategy import ScholarLibraryStrategy
from ._SourceResolutionStrategy import SourceResolutionStrategy
from ._ResolutionOrchestrator import ResolutionOrchestrator

__all__ = [
    "ScholarLibraryStrategy",
    "SourceResolutionStrategy",
    "ResolutionOrchestrator",
]

# EOF