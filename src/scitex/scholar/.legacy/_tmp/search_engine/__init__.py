#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-01 17:54:17 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/search_engine/__init__.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Search module for SciTeX Scholar.

This module provides search functionality across multiple academic sources.
"""

# Import base class
from ._BaseSearchEngine import BaseSearchEngine

# Import concrete search engines
from .web._PubMedSearchEngine import PubMedSearchEngine
from .web._ArxivSearchEngine import ArxivSearchEngine
from .web._SemanticScholarSearchEngine import SemanticScholarSearchEngine
from .web._CrossRefSearchEngine import CrossRefSearchEngine
from .web._GoogleScholarSearchEngine import GoogleScholarSearchEngine
from .local._LocalSearchEngine import LocalSearchEngine
from .local._VectorSearchEngine import VectorSearchEngine

# Import unified searcher
from ._UnifiedSearcher import (
    UnifiedSearcher,
    search_async,
    search_sync,
    build_index
)

__all__ = [
    # Base class
    'BaseSearchEngine',

    # Concrete search engines
    'PubMedSearchEngine',
    'ArxivSearchEngine',
    'SemanticScholarSearchEngine',
    'CrossRefSearchEngine',
    'GoogleScholarSearchEngine',
    'LocalSearchEngine',
    'VectorSearchEngine',

    # Unified searcher
    'UnifiedSearcher',

    # Convenience functions
    'search_async',
    'search_sync',
    'build_index'
]

# EOF
