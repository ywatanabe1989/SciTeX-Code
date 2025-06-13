#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-04-30 20:18:52 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/plt/ax/_add_marginal_ax.py
# ----------------------------------------
import os

__FILE__ = "./src/scitex/plt/ax/_add_marginal_ax.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import matplotlib
from mpl_toolkits.axes_grid1 import make_axes_locatable
from ....plt.utils import assert_valid_axis


def add_marginal_ax(axis, place, size=0.2, pad=0.1):
    """
    Add a marginal axis to the specified side of an existing axis.
    
    Arguments:
        axis (matplotlib.axes.Axes or scitex.plt._subplots.AxisWrapper): The axis to which a marginal axis will be added.
        place (str): Where to place the marginal axis ('top', 'right', 'bottom', or 'left').
        size (float, optional): Fractional size of the marginal axis relative to the main axis. Defaults to 0.2.
        pad (float, optional): Padding between the axes. Defaults to 0.1.
        
    Returns:
        matplotlib.axes.Axes: The newly created marginal axis.
    """
    assert_valid_axis(axis, "First argument must be a matplotlib axis or scitex axis wrapper")

    divider = make_axes_locatable(axis)

    size_perc_str = f"{size*100}%"
    if place in ["left", "right"]:
        size = 1.0 / size

    axis_marginal = divider.append_axes(place, size=size_perc_str, pad=pad)
    axis_marginal.set_box_aspect(size)

    return axis_marginal


# EOF
