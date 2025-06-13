#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-01 08:47:27 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/plt/ax/_style/_share_axes.py
# ----------------------------------------
import os

__FILE__ = "./src/scitex/plt/ax/_style/_share_axes.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import matplotlib.pyplot as plt
import scitex
import numpy as np


def sharexy(*multiple_axes):
    """Share both x and y axis limits across multiple axes.

    Synchronizes both x and y axis limits across all provided axes objects,
    ensuring they all display the same data range. Useful for comparing
    multiple plots on the same scale.

    Parameters
    ----------
    *multiple_axes : matplotlib.axes.Axes or array of Axes
        Variable number of axes objects to synchronize.

    Examples
    --------
    >>> fig, (ax1, ax2, ax3) = plt.subplots(1, 3)
    >>> ax1.plot([1, 2, 3], [1, 4, 9])
    >>> ax2.plot([1, 2, 3], [2, 5, 8])
    >>> ax3.plot([1, 2, 3], [3, 6, 10])
    >>> sharexy(ax1, ax2, ax3)  # All axes now show same range

    See Also
    --------
    sharex : Share only x-axis limits
    sharey : Share only y-axis limits
    """
    sharex(*multiple_axes)
    sharey(*multiple_axes)


def sharex(*multiple_axes):
    """Share x-axis limits across multiple axes.

    Finds the global x-axis limits across all axes and applies them
    to each axis, ensuring horizontal alignment of data.

    Parameters
    ----------
    *multiple_axes : matplotlib.axes.Axes or array of Axes
        Variable number of axes objects to synchronize.

    Returns
    -------
    axes : axes object(s)
        The modified axes with shared x-limits.
    xlim : tuple
        The (xmin, xmax) limits applied.

    Examples
    --------
    >>> fig, axes = plt.subplots(2, 1)
    >>> axes[0].plot([1, 5], [1, 2])
    >>> axes[1].plot([2, 4], [3, 4])
    >>> sharex(axes[0], axes[1])  # Both show x-range [1, 5]
    """
    xlim = get_global_xlim(*multiple_axes)
    return set_xlims(*multiple_axes, xlim=xlim)


def sharey(*multiple_axes):
    """Share y-axis limits across multiple axes.

    Finds the global y-axis limits across all axes and applies them
    to each axis, ensuring vertical alignment of data.

    Parameters
    ----------
    *multiple_axes : matplotlib.axes.Axes or array of Axes
        Variable number of axes objects to synchronize.

    Returns
    -------
    axes : axes object(s)
        The modified axes with shared y-limits.
    ylim : tuple
        The (ymin, ymax) limits applied.

    Examples
    --------
    >>> fig, axes = plt.subplots(1, 2)
    >>> axes[0].plot([1, 2], [1, 5])
    >>> axes[1].plot([1, 2], [2, 4])
    >>> sharey(axes[0], axes[1])  # Both show y-range [1, 5]
    """
    ylim = get_global_ylim(*multiple_axes)
    return set_ylims(*multiple_axes, ylim=ylim)


def get_global_xlim(*multiple_axes):
    """Get the global x-axis limits across multiple axes.

    Scans all provided axes to find the minimum and maximum x-values
    across all of them. Handles both single axes and arrays of axes.

    Parameters
    ----------
    *multiple_axes : matplotlib.axes.Axes or array of Axes
        Variable number of axes objects to scan.

    Returns
    -------
    tuple
        (xmin, xmax) representing the global x-axis limits.

    Examples
    --------
    >>> fig, (ax1, ax2) = plt.subplots(1, 2)
    >>> ax1.plot([1, 3], [1, 2])  # x-range: [1, 3]
    >>> ax2.plot([2, 5], [1, 2])  # x-range: [2, 5]
    >>> xlim = get_global_xlim(ax1, ax2)
    >>> print(xlim)  # (1, 5)

    Notes
    -----
    There appears to be a bug in the current implementation where
    get_ylim() is called instead of get_xlim(). This should be fixed.
    """
    xmin, xmax = np.inf, -np.inf
    for axes in multiple_axes:
        # axes
        if isinstance(axes, (np.ndarray, scitex.plt._subplots._AxesWrapper.AxesWrapper)):
            for ax in axes.flat:
                _xmin, _xmax = ax.get_xlim()  # Fixed: was get_ylim()
                xmin = min(xmin, _xmin)
                xmax = max(xmax, _xmax)
        # axis
        else:
            ax = axes
            _xmin, _xmax = ax.get_xlim()  # Fixed: was get_ylim()
            xmin = min(xmin, _xmin)
            xmax = max(xmax, _xmax)

    return (xmin, xmax)


# def get_global_xlim(*multiple_axes):
#     xmin, xmax = np.inf, -np.inf
#     for axes in multiple_axes:
#         for ax in axes.flat:
#             _xmin, _xmax = ax.get_xlim()
#             xmin = min(xmin, _xmin)
#             xmax = max(xmax, _xmax)
#     return (xmin, xmax)


def get_global_ylim(*multiple_axes):
    """Get the global y-axis limits across multiple axes.

    Scans all provided axes to find the minimum and maximum y-values
    across all of them. Handles both single axes and arrays of axes.

    Parameters
    ----------
    *multiple_axes : matplotlib.axes.Axes or array of Axes
        Variable number of axes objects to scan.

    Returns
    -------
    tuple
        (ymin, ymax) representing the global y-axis limits.

    Examples
    --------
    >>> fig, (ax1, ax2) = plt.subplots(1, 2)
    >>> ax1.plot([1, 2], [1, 3])  # y-range: [1, 3]
    >>> ax2.plot([1, 2], [2, 5])  # y-range: [2, 5]
    >>> ylim = get_global_ylim(ax1, ax2)
    >>> print(ylim)  # (1, 5)
    """
    ymin, ymax = np.inf, -np.inf
    for axes in multiple_axes:
        # axes
        if isinstance(axes, (np.ndarray, scitex.plt._subplots._AxesWrapper.AxesWrapper)):
            for ax in axes.flat:
                _ymin, _ymax = ax.get_ylim()
                ymin = min(ymin, _ymin)
                ymax = max(ymax, _ymax)
        # axis
        else:
            ax = axes
            _ymin, _ymax = ax.get_ylim()
            ymin = min(ymin, _ymin)
            ymax = max(ymax, _ymax)

    return (ymin, ymax)


def set_xlims(*multiple_axes, xlim=None):
    if xlim is None:
        raise ValueError("Please set xlim. get_global_xlim() might be useful.")

    for axes in multiple_axes:
        # axes
        if isinstance(axes, (np.ndarray, scitex.plt._subplots._AxesWrapper.AxesWrapper)):
            for ax in axes.flat:
                ax.set_xlim(xlim)
        # axis
        else:
            ax = axes
            ax.set_xlim(xlim)

    # Return
    if len(multiple_axes) == 1:
        return multiple_axes[0], xlim
    else:
        return multiple_axes, xlim


def set_ylims(*multiple_axes, ylim=None):
    if ylim is None:
        raise ValueError("Please set ylim. get_global_xlim() might be useful.")

    for axes in multiple_axes:
        # axes
        if isinstance(axes, (np.ndarray, scitex.plt._subplots._AxesWrapper.AxesWrapper)):
            for ax in axes.flat:
                ax.set_ylim(ylim)

        # axis
        else:
            ax = axes
            ax.set_ylim(ylim)

    # Return
    if len(multiple_axes) == 1:
        return multiple_axes[0], ylim
    else:
        return multiple_axes, ylim


def main():
    pass


if __name__ == "__main__":
    # # Argument Parser
    # import argparse
    import sys

    # parser = argparse.ArgumentParser(description='')
    # parser.add_argument('--var', '-v', type=int, default=1, help='')
    # parser.add_argument('--flag', '-f', action='store_true', default=False, help='')
    # args = parser.parse_args()
    # Main
    CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.gen.start(sys, plt, verbose=False)
    main()
    scitex.gen.close(CONFIG, verbose=False, notify=False)

# EOF
