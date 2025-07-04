#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-13 22:42:39 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/SciTeX-Code/src/scitex/plt/__init__.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/plt/__init__.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
"""Scitex plt module."""

from ._tpl import termplot
from . import color
from . import utils

# Lazy import for subplots to avoid circular dependencies
_subplots = None

def subplots(*args, **kwargs):
    """Lazy-loaded subplots function."""
    global _subplots
    if _subplots is None:
        from ._subplots._SubplotsWrapper import subplots as _subplots_func
        _subplots = _subplots_func
    return _subplots(*args, **kwargs)

__all__ = [
    "termplot",
    "subplots",
    "utils",
    "color",
]

# EOF
