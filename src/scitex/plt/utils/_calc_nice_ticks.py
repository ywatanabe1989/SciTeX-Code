#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-01 13:40:19 (ywatanabe)"
# File: /home/ywatanabe/proj/_scitex_repo/src/scitex/plt/_calc_nice_ticks.py
# ----------------------------------------
import os

__FILE__ = "./src/scitex/plt/_calc_nice_ticks.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import matplotlib.ticker as mticker
import numpy as np


def calc_nice_ticks(
    min_val,
    max_val,
    allow_edge_min=True,
    allow_edge_max=False,
    pad_perc=5,
    num_ticks=4,
    prefer_integer=True,
):
    """
    Calculate nice tick values for axes based on data range.
    Parameters:
    -----------
    min_val : float
        Minimum data value
    max_val : float
        Maximum data value
    allow_edge_min : bool, optional
        Whether to allow a tick at the min value, defaults to True
    allow_edge_max : bool, optional
        Whether to allow a tick at the max value, defaults to False
    pad_perc : float, optional
        Percentage of data range to pad, defaults to 5%
    num_ticks : int, optional
        Target number of ticks to display, defaults to 4
    prefer_integer : bool, optional
        If True, convert ticks to integers when possible, defaults to True
    Returns:
    --------
    list
        List of nicely spaced tick positions
    """
    # Handle edge cases
    if min_val == max_val:
        if min_val == 0:
            return [0, 1, 2, 3]
        else:
            # Create a small range around the single value
            margin = abs(min_val) * 0.1
            min_val -= margin
            max_val += margin

    # Store original values before padding
    original_min = min_val
    original_max = max_val

    # Apply padding if needed
    range_size = max_val - min_val
    if not allow_edge_min:
        min_val -= range_size * pad_perc / 100
    if not allow_edge_max:
        max_val += range_size * pad_perc / 100

    # Use matplotlib's MaxNLocator to get nice tick locations
    locator = mticker.MaxNLocator(
        nbins=num_ticks,
        steps=[1, 2, 5, 10],
        integer=False,
        symmetric=False,
        prune=None,
        min_n_ticks=3,
    )

    # Get tick locations
    tick_locations = locator.tick_values(min_val, max_val)

    # If we got too many ticks, try to reduce them
    if len(tick_locations) > num_ticks + 1:
        locator = mticker.MaxNLocator(nbins=num_ticks - 1)
        tick_locations = locator.tick_values(min_val, max_val)

    # Filter out ticks outside the original data range if needed
    if not allow_edge_min:
        tick_locations = [tick for tick in tick_locations if tick >= original_min]
    if not allow_edge_max:
        tick_locations = [tick for tick in tick_locations if tick <= original_max]

    # Convert to integers if all values can be represented as integers
    if prefer_integer and all(float(int(tick)) == tick for tick in tick_locations):
        tick_locations = [int(tick) for tick in tick_locations]

    # Convert to simple list
    return np.array(tick_locations).tolist()


# EOF
