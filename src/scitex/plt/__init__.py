#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-13 22:42:39 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/SciTeX-Code/src/scitex/plt/__init__.py
# ----------------------------------------
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
"""Scitex plt module."""

from ._tpl import termplot
from . import color
from . import utils
from . import ax

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

def tight_layout(**kwargs):
    """
    Wrapper for matplotlib.pyplot.tight_layout that suppresses the layout change warning.

    This function calls tight_layout on the current figure and suppresses the common
    UserWarning: "The figure layout has changed to tight" which is informational
    and typically not actionable.

    Parameters
    ----------
    **kwargs
        All keyword arguments are passed to matplotlib.pyplot.tight_layout()
    """
    import warnings
    import matplotlib.pyplot as plt

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="The figure layout has changed to tight")
        plt.tight_layout(**kwargs)


def colorbar(mappable=None, cax=None, ax=None, **kwargs):
    """
    Create a colorbar, automatically unwrapping SciTeX AxisWrapper objects.

    This function handles both regular matplotlib axes and SciTeX AxisWrapper
    objects transparently, making it a drop-in replacement for plt.colorbar().

    Parameters
    ----------
    mappable : ScalarMappable, optional
        The image, contour set, etc. to which the colorbar applies.
        If None, uses the current image.
    cax : Axes, optional
        Axes into which the colorbar will be drawn.
    ax : Axes or AxisWrapper or list thereof, optional
        Parent axes from which space for the colorbar will be stolen.
        If None, uses current axes.
    **kwargs
        Additional keyword arguments passed to matplotlib.pyplot.colorbar()

    Returns
    -------
    Colorbar
        The created colorbar object
    """
    import matplotlib.pyplot as plt

    # Unwrap ax if it's a SciTeX AxisWrapper
    if ax is not None:
        if hasattr(ax, '__iter__') and not isinstance(ax, str):
            # Handle list/array of axes
            ax = [a._axis_mpl if hasattr(a, '_axis_mpl') else a for a in ax]
        else:
            # Single axis
            ax = ax._axis_mpl if hasattr(ax, '_axis_mpl') else ax

    # Unwrap cax if provided
    if cax is not None:
        cax = cax._axis_mpl if hasattr(cax, '_axis_mpl') else cax

    # Call matplotlib's colorbar with unwrapped axes
    return plt.colorbar(mappable=mappable, cax=cax, ax=ax, **kwargs)

__all__ = [
    "termplot",
    "subplots",
    "figure",
    "tight_layout",
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
