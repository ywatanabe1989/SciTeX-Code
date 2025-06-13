#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-02 09:00:52 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/plt/ax/_style/_force_aspect.py
# ----------------------------------------
import os

__FILE__ = "./src/scitex/plt/ax/_style/_force_aspect.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import matplotlib
from ....plt.utils import assert_valid_axis


def force_aspect(axis, aspect=1):
    """
    Forces aspect ratio of an axis based on the extent of the image.
    
    Arguments:
        axis (matplotlib.axes.Axes or scitex.plt._subplots.AxisWrapper): The axis to adjust.
        aspect (float, optional): The aspect ratio to apply. Defaults to 1.
        
    Returns:
        matplotlib.axes.Axes or scitex.plt._subplots.AxisWrapper: The axis with adjusted aspect ratio.
    """
    assert_valid_axis(axis, "First argument must be a matplotlib axis or scitex axis wrapper")

    im = axis.get_images()

    extent = im[0].get_extent()

    axis.set_aspect(abs((extent[1] - extent[0]) / (extent[3] - extent[2])) / aspect)
    return axis


# EOF
