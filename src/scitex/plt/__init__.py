#!/usr/bin/env python3
"""Scitex plt module."""

from ._tpl import termplot

# Lazy import for subplots to avoid circular dependencies
_subplots = None

def subplots(*args, **kwargs):
    """Lazy-loaded subplots function."""
    global _subplots
    if _subplots is None:
        from ._subplots._SubplotsWrapper import subplots as _subplots_impl
        _subplots = _subplots_impl
    return _subplots(*args, **kwargs)

__all__ = [
    "termplot",
    "subplots",
]
