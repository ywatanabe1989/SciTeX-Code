#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-04-29 20:41:30 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/plt/_close.py
# ----------------------------------------
import os

__FILE__ = "./src/scitex/plt/_close.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import matplotlib
import matplotlib.pyplot as plt
import scitex.plt as scitex_plt


def close(obj):
    """Close a matplotlib figure or SciTeX FigWrapper object.

    Properly closes matplotlib figures to free memory, handling both
    standard matplotlib Figure objects and SciTeX FigWrapper objects.
    This is important for preventing memory leaks when creating many plots.

    Parameters
    ----------
    obj : matplotlib.figure.Figure or scitex.plt.FigWrapper
        The figure object to close. Can be either a matplotlib Figure
        or an SciTeX FigWrapper instance.

    Raises
    ------
    TypeError
        If obj is neither a Figure nor FigWrapper object.

    Examples
    --------
    >>> # Close a matplotlib figure
    >>> fig, ax = plt.subplots()
    >>> ax.plot([1, 2, 3], [1, 4, 9])
    >>> close(fig)

    >>> # Close an SciTeX FigWrapper
    >>> fig, axes = scitex.plt.subplots(2, 2)
    >>> close(fig)

    >>> # Prevents memory leaks in loops
    >>> for i in range(100):
    ...     fig, ax = plt.subplots()
    ...     ax.plot(data[i])
    ...     plt.savefig(f'plot_{i}.png')
    ...     close(fig)  # Important!

    See Also
    --------
    matplotlib.pyplot.close : Standard matplotlib close function
    scitex.plt.subplots : Creates FigWrapper objects
    """
    if isinstance(obj, matplotlib.figure.Figure):
        plt.close(obj)
    elif isinstance(obj, scitex_plt._subplots._FigWrapper.FigWrapper):
        plt.close(obj.figure)
    else:
        raise TypeError(
            f"Cannot close object of type {type(obj).__name__}. Expected FigWrapper or Figure object."
        )


# EOF
