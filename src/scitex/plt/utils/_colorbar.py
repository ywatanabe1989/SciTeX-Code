#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-08 11:15:00 (ywatanabe)"
# File: /src/scitex/plt/utils/_colorbar.py
# ----------------------------------------

"""Enhanced colorbar utilities for better placement with scitex.plt"""

import matplotlib.pyplot as plt
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize


def colorbar(mappable, ax=None, **kwargs):
    """Enhanced colorbar function that ensures proper spacing.
    
    This function wraps matplotlib.pyplot.colorbar with better defaults
    to prevent overlap with axes when using constrained_layout.
    
    Parameters
    ----------
    mappable : matplotlib.cm.ScalarMappable
        The mappable whose colorbar is to be made (e.g., from imshow, scatter)
    ax : matplotlib.axes.Axes or list of Axes, optional
        Parent axes from which space for a new colorbar axes will be stolen.
    **kwargs : dict
        Additional keyword arguments passed to matplotlib.pyplot.colorbar
        
    Returns
    -------
    colorbar : matplotlib.colorbar.Colorbar
        The colorbar instance
    """
    # Set better defaults for colorbar placement
    defaults = {
        'fraction': 0.046,  # Fraction of axes to use for colorbar
        'pad': 0.04,        # Padding between axes and colorbar
        'aspect': 20,       # Aspect ratio of colorbar
    }
    
    # Update defaults with any user-provided kwargs
    for key, value in defaults.items():
        if key not in kwargs:
            kwargs[key] = value
    
    # Create the colorbar
    cbar = plt.colorbar(mappable, ax=ax, **kwargs)
    
    # If using constrained_layout, ensure the figure updates
    if ax is not None:
        fig = ax.figure if hasattr(ax, 'figure') else ax[0].figure
        if hasattr(fig, 'get_constrained_layout') and fig.get_constrained_layout():
            # Force a layout update
            fig.canvas.draw_idle()
    
    return cbar


def add_shared_colorbar(fig, axes, mappable, location='right', **kwargs):
    """Add a single colorbar shared by multiple axes.
    
    Parameters
    ----------
    fig : matplotlib.figure.Figure
        The figure containing the axes
    axes : array-like of Axes
        The axes that will share the colorbar
    mappable : matplotlib.cm.ScalarMappable
        The mappable whose colorbar is to be made
    location : {'right', 'bottom', 'left', 'top'}, optional
        Where to place the colorbar (default: 'right')
    **kwargs : dict
        Additional keyword arguments passed to fig.colorbar
        
    Returns
    -------
    colorbar : matplotlib.colorbar.Colorbar
        The colorbar instance
    """
    defaults = {
        'shrink': 0.8,      # Shrink colorbar to match axes height
        'aspect': 30,       # Make it thinner for shared colorbars
    }
    
    # Update defaults with any user-provided kwargs
    for key, value in defaults.items():
        if key not in kwargs:
            kwargs[key] = value
    
    # Create the shared colorbar
    cbar = fig.colorbar(mappable, ax=axes, location=location, **kwargs)
    
    return cbar


# EOF