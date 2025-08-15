#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-27 15:38:04 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/doi/sources/__init__.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/doi/sources/__init__.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
DOI sources for the SingleDOIResolver.

This module provides different sources for resolving DOIs including
CrossRef, PubMed, OpenAlex, and Semantic Scholar.
"""

from ._BaseDOISource import BaseDOISource
from ._CrossRefSource import CrossRefSource
from ._PubMedSource import PubMedSource
from ._OpenAlexSource import OpenAlexSource
from ._ArXivSource import ArXivSource
from ._SemanticScholarSource import SemanticScholarSource
from ._URLDOISource import URLDOISource

__all__ = [
    "BaseDOISource",
    "CrossRefSource",
    "PubMedSource",
    "OpenAlexSource",
    "ArXivSource",
    "SemanticScholarSource",
    "URLDOISource",
]

# EOF
