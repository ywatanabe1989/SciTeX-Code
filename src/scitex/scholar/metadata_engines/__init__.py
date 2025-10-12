#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-27 15:38:04 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/doi/engines/__init__.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
DOI engines for the SingleDOIResolver.

This module provides different engines for resolving DOIs including
CrossRef, PubMed, OpenAlex, and Semantic Scholar.
"""

from .ScholarEngine import ScholarEngine

# EOF
