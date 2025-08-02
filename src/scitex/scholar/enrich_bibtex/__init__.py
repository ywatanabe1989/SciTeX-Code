#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-01 02:24:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/enrich_bibtex/__init__.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/enrich_bibtex/__init__.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""BibTeX enrichment module for SciTeX Scholar."""

from .._Scholar import Scholar

def enrich_bibtex(bibtex_path, output_path=None):
    """Enrich a BibTeX file with metadata."""
    scholar = Scholar()
    return scholar.enrich_bibtex(bibtex_path, output_path)

__all__ = ["enrich_bibtex"]

# EOF