#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-04-30 21:24:49 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/plt/ax/_panel.py
# ----------------------------------------
import os

__FILE__ = "./src/scitex/plt/ax/_panel.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

# Time-stamp: "2024-02-03 15:34:08 (ywatanabe)"

import matplotlib.pyplot as plt
from scitex.decorators import deprecated


def add_panel(tgt_width_mm=40, tgt_height_mm=None):
    """Creates a fixed-size ax figure for panels."""

    H_TO_W_RATIO = 0.7
    MM_TO_INCH_FACTOR = 1 / 25.4

    if tgt_height_mm is None:
        tgt_height_mm = H_TO_W_RATIO * tgt_width_mm

    # Convert target dimensions from millimeters to inches
    tgt_width_in = tgt_width_mm * MM_TO_INCH_FACTOR
    tgt_height_in = tgt_height_mm * MM_TO_INCH_FACTOR

    # Create a figure with the specified dimensions
    fig = plt.figure(figsize=(tgt_width_in * 2, tgt_height_in * 2))

    # Calculate the position and size of the axes in figure units (0 to 1)
    left = (fig.get_figwidth() - tgt_width_in) / 2 / fig.get_figwidth()
    bottom = (fig.get_figheight() - tgt_height_in) / 2 / fig.get_figheight()
    ax = fig.add_axes(
        [
            left,
            bottom,
            tgt_width_in / fig.get_figwidth(),
            tgt_height_in / fig.get_figheight(),
        ]
    )

    return fig, ax


@deprecated("Use add_panel instead")
def panel(tgt_width_mm=40, tgt_height_mm=None):
    """Create a figure panel with specified dimensions (deprecated).

    This function is deprecated and maintained only for backward compatibility.
    Please use `add_panel` instead.

    Parameters
    ----------
    tgt_width_mm : float, optional
        Target width in millimeters. Default is 40.
    tgt_height_mm : float or None, optional
        Target height in millimeters. If None, uses golden ratio.
        Default is None.

    Returns
    -------
    tuple
        (fig, ax) - matplotlib figure and axes objects

    See Also
    --------
    add_panel : The recommended function to use instead

    Examples
    --------
    >>> # Deprecated usage
    >>> fig, ax = panel(tgt_width_mm=40, tgt_height_mm=30)

    >>> # Recommended alternative
    >>> fig, ax = add_panel(tgt_width_mm=40, tgt_height_mm=30)
    """
    return add_panel(tgt_width_mm=40, tgt_height_mm=None)


if __name__ == "__main__":
    # Example usage:
    fig, ax = panel(tgt_width_mm=40, tgt_height_mm=40 * 0.7)
    ax.plot([1, 2, 3], [4, 5, 6])
    ax.scatter([1, 2, 3], [4, 5, 6])
    # ... compatible with other ax plotting methods as well
    plt.show()

# EOF
