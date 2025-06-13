#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-04-30 21:26:45 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/plt/ax/_plot_fillv.py
# ----------------------------------------
import os

__FILE__ = "./src/scitex/plt/ax/_plot_fillv.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import matplotlib
import numpy as np
from ....plt.utils import assert_valid_axis


def plot_fillv(axes, starts, ends, color="red", alpha=0.2):
    """
    Fill between specified start and end intervals on an axis or array of axes.

    Parameters
    ----------
    axes : matplotlib.axes.Axes or scitex.plt._subplots.AxisWrapper or numpy.ndarray of axes
        The axis object(s) to fill intervals on.
    starts : array-like
        Array-like of start positions.
    ends : array-like
        Array-like of end positions.
    color : str, optional
        The color to use for the filled regions. Default is "red".
    alpha : float, optional
        The alpha blending value, between 0 (transparent) and 1 (opaque). Default is 0.2.

    Returns
    -------
    list
        List of axes with filled intervals.
    """

    is_axes = isinstance(axes, np.ndarray)

    axes = axes if isinstance(axes, np.ndarray) else [axes]

    for ax in axes:
        assert_valid_axis(ax, "First argument must be a matplotlib axis or scitex axis wrapper")
        for start, end in zip(starts, ends):
            ax.axvspan(start, end, color=color, alpha=alpha)

    if not is_axes:
        return axes[0]
    else:
        return axes


# EOF
