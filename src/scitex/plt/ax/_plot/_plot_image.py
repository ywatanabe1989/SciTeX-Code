#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-01 08:39:46 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/plt/ax/_plot/_plot_image2d.py
# ----------------------------------------
import os

__FILE__ = "./src/scitex/plt/ax/_plot/_plot_image2d.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import matplotlib
from scitex.plt.utils import assert_valid_axis


def plot_image(
    ax,
    arr_2d,
    cbar=True,
    cbar_label=None,
    cbar_shrink=1.0,
    cbar_fraction=0.046,
    cbar_pad=0.04,
    cmap="viridis",
    aspect="auto",
    vmin=None,
    vmax=None,
    **kwargs,
):
    """
    Imshows an two-dimensional array with theese two conditions:
    1) The first dimension represents the x dim, from left to right.
    2) The second dimension represents the y dim, from bottom to top
    
    Parameters
    ----------
    ax : matplotlib.axes.Axes or scitex.plt._subplots._AxisWrapper.AxisWrapper
        The axis to plot on
    arr_2d : numpy.ndarray
        The 2D array to display
    cbar : bool, optional
        Whether to show colorbar, by default True
    cbar_label : str, optional
        Label for the colorbar, by default None
    cbar_shrink : float, optional
        Shrink factor for the colorbar, by default 1.0
    cbar_fraction : float, optional
        Fraction of original axes to use for colorbar, by default 0.046
    cbar_pad : float, optional
        Padding between the image axes and colorbar axes, by default 0.04
    cmap : str, optional
        Colormap name, by default "viridis"
    aspect : str, optional
        Aspect ratio adjustment, by default "auto"
    vmin : float, optional
        Minimum data value for colormap scaling, by default None
    vmax : float, optional
        Maximum data value for colormap scaling, by default None
    **kwargs
        Additional keyword arguments passed to ax.imshow()
        
    Returns
    -------
    matplotlib.axes.Axes or scitex.plt._subplots._AxisWrapper.AxisWrapper
        The axis with the image plotted
    """
    assert_valid_axis(ax, "First argument must be a matplotlib axis or scitex axis wrapper")
    assert arr_2d.ndim == 2, "Input array must be 2-dimensional"

    if kwargs.get("xyz"):
        kwargs.pop("xyz")

    # Transposes arr_2d for correct orientation
    arr_2d = arr_2d.T

    # Cals the original ax.imshow() method on the transposed array
    im = ax.imshow(arr_2d, cmap=cmap, vmin=vmin, vmax=vmax, aspect=aspect, **kwargs)

    # Color bar
    if cbar:
        fig = ax.get_figure()
        _cbar = fig.colorbar(
            im, ax=ax, shrink=cbar_shrink, fraction=cbar_fraction, pad=cbar_pad
        )
        if cbar_label:
            _cbar.set_label(cbar_label)

    # Invert y-axis to match typical image orientation
    ax.invert_yaxis()

    return ax


# EOF
