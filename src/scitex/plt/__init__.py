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
_figure = None

def subplots(*args, **kwargs):
    """Lazy-loaded subplots function."""
    global _subplots
    if _subplots is None:
        from ._subplots._SubplotsWrapper import subplots as _subplots_func
        _subplots = _subplots_func
    return _subplots(*args, **kwargs)

def figure(*args, **kwargs):
    """Lazy-loaded figure function that returns a FigWrapper."""
    global _figure
    if _figure is None:
        import matplotlib.pyplot as plt
        from ._subplots._FigWrapper import FigWrapper
        def _figure_func(*args, **kwargs):
            fig_mpl = plt.figure(*args, **kwargs)
            return FigWrapper(fig_mpl)
        _figure = _figure_func
    return _figure(*args, **kwargs)

__all__ = [
    "termplot",
    "subplots",
    "figure",
    "utils",
    "color",
]

def __getattr__(name):
    """
    Fallback to matplotlib.pyplot for any missing attributes.
    This makes scitex.plt a complete drop-in replacement for matplotlib.pyplot.
    """
    try:
        import matplotlib.pyplot as plt
        if hasattr(plt, name):
            return getattr(plt, name)
        else:
            raise AttributeError(f"module 'scitex.plt' has no attribute '{name}'")
    except ImportError:
        raise AttributeError(f"module 'scitex.plt' has no attribute '{name}' (matplotlib not available)")

def __dir__():
    """
    Provide comprehensive directory listing including matplotlib.pyplot functions.
    """
    # Get local attributes
    local_attrs = __all__.copy()
    
    # Add matplotlib.pyplot attributes
    try:
        import matplotlib.pyplot as plt
        mpl_attrs = [attr for attr in dir(plt) if not attr.startswith('_')]
        local_attrs.extend(mpl_attrs)
    except ImportError:
        pass
    
    return sorted(set(local_attrs))

# EOF
