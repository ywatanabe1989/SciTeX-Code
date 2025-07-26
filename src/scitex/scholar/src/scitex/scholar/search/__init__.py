#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-26 14:03:00 (ywatanabe)"
# File: ./src/scitex/scholar/search/__init__.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/scholar/search/__init__.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Search module for Scholar."""

# Import search engines
from ._UnifiedSearcher import UnifiedSearcher
from ._BaseSearchEngine import BaseSearchEngine
from ._PubMedEngine import PubMedEngine
from ._SemanticScholarEngine import SemanticScholarEngine
from ._ArxivEngine import ArxivEngine

__all__ = [
    "UnifiedSearcher",
    "BaseSearchEngine",
    "PubMedEngine",
    "SemanticScholarEngine",
    "ArxivEngine"
]

# EOF