#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-01 15:21:37 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/plt/ax/_plot/_plot_cube.py
# ----------------------------------------
import os

__FILE__ = "./src/scitex/plt/ax/_plot/_plot_cube.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from itertools import combinations, product

import numpy as np


def plot_cube(ax, xlim, ylim, zlim, c="blue", alpha=1.0):
    """
    Plot a 3D cube on the given axis.

    Args:
        ax: Matplotlib 3D axis
        xlim: Range for x-axis as a tuple (min, max)
        ylim: Range for y-axis as a tuple (min, max)
        zlim: Range for z-axis as a tuple (min, max)
        c: Color of the cube edges (default: 'blue')
        alpha: Transparency of the cube edges (default: 1.0)

    Returns:
        Matplotlib axis with the cube plotted
    """
    # Validate inputs
    assert hasattr(ax, "plot3D"), "The axis must be a 3D axis with plot3D method"
    assert len(xlim) == 2, "xlim must be a tuple of (min, max)"
    assert len(ylim) == 2, "ylim must be a tuple of (min, max)"
    assert len(zlim) == 2, "zlim must be a tuple of (min, max)"
    assert xlim[0] < xlim[1], "xlim[0] must be less than xlim[1]"
    assert ylim[0] < ylim[1], "ylim[0] must be less than ylim[1]"
    assert zlim[0] < zlim[1], "zlim[0] must be less than zlim[1]"

    # Get all corners of the cube
    corners = np.array(list(product(xlim, ylim, zlim)))

    # Draw edges between corners
    for start, end in combinations(corners, 2):
        # Check if the points form an edge (differ in exactly one dimension)
        if np.sum(np.abs(start - end)) == xlim[1] - xlim[0]:
            ax.plot3D(*zip(start, end), c=c, linewidth=3, alpha=alpha)
        if np.sum(np.abs(start - end)) == ylim[1] - ylim[0]:
            ax.plot3D(*zip(start, end), c=c, linewidth=3, alpha=alpha)
        if np.sum(np.abs(start - end)) == zlim[1] - zlim[0]:
            ax.plot3D(*zip(start, end), c=c, linewidth=3, alpha=alpha)

    return ax


# EOF
