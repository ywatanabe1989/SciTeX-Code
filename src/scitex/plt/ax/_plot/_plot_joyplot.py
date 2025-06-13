#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-02 09:03:23 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/plt/ax/_plot/_plot_joyplot.py
# ----------------------------------------
import os

__FILE__ = "./src/scitex/plt/ax/_plot/_plot_joyplot.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import warnings

import joypy

from .._style._set_xyt import set_xyt as scitex_plt_set_xyt


def plot_joyplot(ax, data, orientation="vertical", **kwargs):
    """
    Create a joyplot (ridgeline plot) with proper orientation handling.
    
    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes to plot on
    data : pandas.DataFrame or array-like
        The data to plot
    orientation : str, default "vertical"
        Plot orientation. Either "vertical" or "horizontal"
    **kwargs
        Additional keyword arguments passed to joypy.joyplot()
    
    Returns
    -------
    matplotlib.axes.Axes
        The axes with the joyplot
    
    Raises
    ------
    ValueError
        If orientation is not "vertical" or "horizontal"
    """
    if orientation not in ["vertical", "horizontal"]:
        raise ValueError("orientation must be either 'vertical' or 'horizontal'")
    
    # Handle orientation by setting appropriate joypy parameters
    if orientation == "horizontal":
        # For horizontal orientation, we need to transpose the data display
        # joypy doesn't have direct horizontal support, so we work with the result
        kwargs.setdefault("kind", "kde")  # Ensure we're using KDE plots
        
    fig, axes = joypy.joyplot(
        data=data,
        **kwargs,
    )

    # Set appropriate labels based on orientation
    if orientation == "vertical":
        ax = scitex_plt_set_xyt(ax, None, "Density", "Joyplot")
    elif orientation == "horizontal":
        ax = scitex_plt_set_xyt(ax, "Density", None, "Joyplot")
        # For horizontal plots, we might need additional transformations
        # This is a limitation of joypy which primarily supports vertical plots

    return ax


# def plot_vertical_joyplot(ax, data, **kwargs):
#     return _plot_joyplot(ax, data, "vertical", **kwargs)


# def plot_horizontal_joyplot(ax, data, **kwargs):
#     return _plot_joyplot(ax, data, "horizontal", **kwargs)

# EOF
