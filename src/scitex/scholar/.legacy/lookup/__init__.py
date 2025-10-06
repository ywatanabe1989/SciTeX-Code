#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-01 14:05:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/lookup/__init__.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Fast lookup functionality for SciTeX Scholar.

Provides DOI to storage key mapping without full database dependency.
"""

from ._LookupIndex import LookupIndex, get_default_lookup

__all__ = ["LookupIndex", "get_default_lookup"]

# EOF