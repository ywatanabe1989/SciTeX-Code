#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-01 15:21:48 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/plt/ax/_plot/_plot_circular_hist.py
# ----------------------------------------
import os

__FILE__ = "./src/scitex/plt/ax/_plot/_plot_circular_hist.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

# Time-stamp: "2024-02-03 13:10:50 (ywatanabe)"
import matplotlib
import numpy as np
from ....plt.utils import assert_valid_axis


def plot_circular_hist(
    axis,
    radians,
    bins=16,
    density=True,
    offset=0,
    gaps=True,
    color=None,
    range_bias=0,
):
    """
    Example:
        fig, ax = plt.subplots(subplot_kw=dict(projection="polar"))
        ax = scitex.plt.plot_circular_hist(ax, radians)
    Produce a circular histogram of angles on ax.

    Parameters
    ----------
    ax : matplotlib.axes._subplots.PolarAxesSubplot or scitex.plt._subplots.AxisWrapper
        axis instance created with subplot_kw=dict(projection='polar').

    radians : array
        Angles to plot, expected in units of radians.

    bins : int, optional
        Defines the number of equal-width bins in the range. The default is 16.

    density : bool, optional
        If True plot frequency proportional to area. If False plot frequency
        proportional to radius. The default is True.

    offset : float, optional
        Sets the offset for the location of the 0 direction in units of
        radians. The default is 0.

    gaps : bool, optional
        Whether to allow gaps between bins. When gaps = False the bins are
        forced to partition the entire [-pi, pi] range. The default is True.

    Returns
    -------
    n : array or list of arrays
        The number of values in each bin.

    bins : array
        The edges of the bins.

    patches : `.BarContainer` or list of a single `.Polygon`
        Container of individual artists used to create the histogram
        or list of such containers if there are multiple input datasets.
    """
    assert_valid_axis(axis, "First argument must be a matplotlib axis or scitex axis wrapper")

    # Wrap angles to [-pi, pi)
    radians = (radians + np.pi) % (2 * np.pi) - np.pi

    # Force bins to partition entire circle
    if not gaps:
        bins = np.linspace(-np.pi, np.pi, num=bins + 1)

    # Bin data and record counts
    n, bins = np.histogram(
        radians, bins=bins, range=(-np.pi + range_bias, np.pi + range_bias)
    )

    # Compute width of each bin
    widths = np.diff(bins)

    # By default plot frequency proportional to area
    if density:
        # Area to assign each bin
        area = n / radians.size
        # Calculate corresponding bin radius
        radius = (area / np.pi) ** 0.5
    # Otherwise plot frequency proportional to radius
    else:
        radius = n

    mean_val = np.nanmean(radians)
    std_val = np.nanstd(radians)
    axis.axvline(mean_val, color=color)
    axis.text(mean_val, 1, std_val)

    # Plot data on ax
    patches = axis.bar(
        bins[:-1],
        radius,
        zorder=1,
        align="edge",
        width=widths,
        edgecolor=color,
        alpha=0.9,
        fill=False,
        linewidth=1,
    )

    # Set the direction of the zero angle
    axis.set_theta_offset(offset)

    # Remove ylabels for area plots (they are mostly obstructive)
    if density:
        axis.set_yticks([])

    return n, bins, patches


# EOF
