#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-04 08:15:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/doi/utils/__init__.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/doi/utils/__init__.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
DOI Resolution Utilities

This package provides utilities to enhance DOI resolution by:
1. Extracting DOIs from URL fields
2. Converting PubMed IDs to DOIs
3. Normalizing text encoding for better search accuracy

All utilities are designed to be pluggable, testable, and independent.
"""

from ._PubMedConverter import PubMedConverter, pmid2doi
from ._RateLimitHandler import RateLimitHandler
from ._TextNormalizer import TextNormalizer
from ._URLDOIExtractor import URLDOIExtractor

__all__ = [
    "PubMedConverter",
    "pmid2doi",
    "RateLimitHandler",
    "TextNormalizer",
    "URLDOIExtractor",
]


# EOF
