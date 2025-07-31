#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-27 16:23:39 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/enrichment/__init__.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/enrichment/__init__.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
"""Metadata enrichment module for SciTeX Scholar.

This module provides tools to enrich scientific papers with additional metadata
including DOIs, citation counts, impact factors, and abstracts from various sources.
"""

from ._MetadataEnricher import (
    MetadataEnricher,
    JCR_YEAR,
    _enrich_papers_with_all,
    _enrich_papers_with_citations,
    _enrich_papers_with_impact_factors,
)

__all__ = [
    "MetadataEnricher",
    "JCR_YEAR",
    "_enrich_papers_with_all",
    "_enrich_papers_with_citations",
    "_enrich_papers_with_impact_factors",
]

# EOF
