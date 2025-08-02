#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-26 14:23:00 (ywatanabe)"
# File: ./src/scitex/scholar/utils/_paths.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/scholar/utils/_paths.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Path utilities for SciTeX Scholar.

This module provides functions for managing scholar-related paths.
"""

from pathlib import Path


def get_scholar_dir() -> Path:
    """Get SciTeX scholar directory."""
    scholar_dir = Path.home() / ".scitex" / "scholar"
    scholar_dir.mkdir(parents=True, exist_ok=True)
    return scholar_dir

# EOF