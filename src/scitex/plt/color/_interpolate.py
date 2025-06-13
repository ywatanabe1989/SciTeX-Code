#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-03 00:51:06 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/plt/color/_interp_colors.py
# ----------------------------------------
import os

__FILE__ = "./src/scitex/plt/color/_interp_colors.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import matplotlib.colors as mcolors
import numpy as np
from scitex.decorators import deprecated


def gen_interpolate(color_start, color_end, num_points, round=3):
    color_start_rgba = np.array(mcolors.to_rgba(color_start))
    color_end_rgba = np.array(mcolors.to_rgba(color_end))
    rgba_values = np.linspace(color_start_rgba, color_end_rgba, num_points).round(round)
    return [list(color) for color in rgba_values]


@deprecated("Use gen_interpolate instead")
def interpolate(color_start, color_end, num_points, round=3):
    return gen_interpolate(color_start, color_end, num_points, round=round)


# EOF
