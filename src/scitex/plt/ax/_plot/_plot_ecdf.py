#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-01 20:17:59 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/plt/ax/_plot/_plot_ecdf.py
# ----------------------------------------
import os

__FILE__ = "./src/scitex/plt/ax/_plot/_plot_ecdf.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import warnings

import matplotlib
import numpy as np

from ....pd._force_df import force_df as scitex_pd_force_df
from ....plt.utils import assert_valid_axis


def plot_ecdf(axis, data, **kwargs):
    """Plot Empirical Cumulative Distribution Function (ECDF).

    The ECDF shows the proportion of data points less than or equal to each value,
    representing the empirical estimate of the cumulative distribution function.

    Parameters
    ----------
    axis : matplotlib.axes.Axes or scitex.plt._subplots.AxisWrapper
        Matplotlib axis or scitex axis wrapper to plot on
    data : array-like
        Data to compute and plot ECDF for. NaN values are ignored.
    **kwargs : dict
        Additional arguments to pass to plot function

    Returns
    -------
    tuple
        (axis, DataFrame) containing the plot and data
    """
    assert_valid_axis(axis, "First argument must be a matplotlib axis or scitex axis wrapper")

    # Flatten and remove NaN values
    data = np.hstack(data)

    # Warnings
    if np.isnan(data).any():
        warnings.warn("NaN value are ignored for ECDF plot.")
    data = data[~np.isnan(data)]
    nn = len(data)

    # Sort the data and compute the ECDF values
    data_sorted = np.sort(data)
    ecdf_perc = 100 * np.arange(1, len(data_sorted) + 1) / len(data_sorted)

    # Create the pseudo x-axis for step plotting
    x_step = np.repeat(data_sorted, 2)[1:]
    y_step = np.repeat(ecdf_perc, 2)[:-1]

    # Plot the ECDF using steps
    axis.plot(x_step, y_step, drawstyle="steps-post", **kwargs)

    # Scatter the original data points
    axis.plot(data_sorted, ecdf_perc, marker=".", linestyle="none")

    # Set ylim, xlim, and aspect ratio
    axis.set_ylim(0, 100)
    axis.set_xlim(0, 1.0)

    # Create a DataFrame to hold the ECDF data
    df = scitex_pd_force_df(
        {
            "x": data_sorted,
            "y": ecdf_perc,
            "n": nn,
            "x_step": x_step,
            "y_step": y_step,
        }
    )

    return axis, df


# EOF
