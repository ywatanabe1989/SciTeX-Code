#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-22 18:01:49 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/externals/impact_factor/src/impact_factor/core/__init__.py
# ----------------------------------------

"""
Core Impact Factor Calculation System

This module provides legal impact factor calculations using open APIs:
- OpenAlex for comprehensive journal data
- Crossref for publication metadata  
- Semantic Scholar for citation metrics

All calculations are based on publicly available data and transparent methodologies.
"""

from .calculator import ImpactFactorCalculator
from .journal_matcher import JournalMatcher
from .cache_manager import CacheManager

__all__ = [
    "ImpactFactorCalculator",
    "JournalMatcher", 
    "CacheManager"
]

# EOF