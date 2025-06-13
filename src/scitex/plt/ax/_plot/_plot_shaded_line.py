#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-02 23:28:32 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/plt/ax/_plot/_plot_shaded_line.py
# ----------------------------------------
import os

__FILE__ = "./src/scitex/plt/ax/_plot/_plot_shaded_line.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from typing import List, Optional, Tuple, Union

import matplotlib
import numpy as np
import pandas as pd
from matplotlib.axes._axes import Axes

from ....types import ColorLike
from ....plt.utils import assert_valid_axis


def _plot_single_shaded_line(
    axis: Union[Axes, 'AxisWrapper'],
    xx: np.ndarray,
    y_lower: np.ndarray,
    y_middle: np.ndarray,
    y_upper: np.ndarray,
    color: Optional[ColorLike] = None,
    alpha: float = 0.3,
    **kwargs
) -> Tuple[Union[Axes, 'AxisWrapper'], pd.DataFrame]:
    """Plot a line with shaded area between y_lower and y_upper bounds."""
    assert_valid_axis(axis, "First argument must be a matplotlib axis or scitex axis wrapper")
    assert (
        len(xx) == len(y_middle) == len(y_lower) == len(y_upper)
    ), "All arrays must have the same length"

    label = kwargs.get("label")
    if kwargs.get("label"):
        del kwargs["label"]
    axis.plot(xx, y_middle, color=color, alpha=alpha, label=label, **kwargs)
    kwargs["linewidth"] = 0
    kwargs["edgecolor"] = "none"  # Remove edge line
    axis.fill_between(xx, y_lower, y_upper, alpha=alpha, color=color, **kwargs)

    return axis, pd.DataFrame(
        {"x": xx, "y_lower": y_lower, "y_middle": y_middle, "y_upper": y_upper}
    )


def _plot_shaded_line(
    axis: Union[Axes, 'AxisWrapper'],
    xs: List[np.ndarray],
    ys_lower: List[np.ndarray],
    ys_middle: List[np.ndarray],
    ys_upper: List[np.ndarray],
    color: Optional[Union[List[ColorLike], ColorLike]] = None,
    **kwargs
) -> Tuple[Union[Axes, 'AxisWrapper'], List[pd.DataFrame]]:
    """Plot multiple lines with shaded areas between ys_lower and ys_upper bounds."""
    assert_valid_axis(axis, "First argument must be a matplotlib axis or scitex axis wrapper")
    assert (
        len(xs) == len(ys_lower) == len(ys_middle) == len(ys_upper)
    ), "All input lists must have the same length"

    results = []
    colors = color
    color_list = colors

    if colors is not None:
        if not isinstance(colors, list):
            color_list = [colors] * len(xs)
        else:
            assert len(colors) == len(xs), "Number of colors must match number of lines"
            color_list = colors

        for idx, (xx, y_lower, y_middle, y_upper) in enumerate(
            zip(xs, ys_lower, ys_middle, ys_upper)
        ):
            this_kwargs = kwargs.copy()
            this_kwargs["color"] = color_list[idx]
            _, result_df = _plot_single_shaded_line(
                axis, xx, y_lower, y_middle, y_upper, **this_kwargs
            )
            results.append(result_df)
    else:
        for xx, y_lower, y_middle, y_upper in zip(xs, ys_lower, ys_middle, ys_upper):
            _, result_df = _plot_single_shaded_line(
                axis, xx, y_lower, y_middle, y_upper, **kwargs
            )
            results.append(result_df)

    return axis, results


def plot_shaded_line(
    axis: Union[Axes, 'AxisWrapper'],
    xs: Union[np.ndarray, List[np.ndarray]],
    ys_lower: Union[np.ndarray, List[np.ndarray]],
    ys_middle: Union[np.ndarray, List[np.ndarray]],
    ys_upper: Union[np.ndarray, List[np.ndarray]],
    color: Optional[Union[ColorLike, List[ColorLike]]] = None,
    **kwargs
) -> Tuple[Union[Axes, 'AxisWrapper'], Union[pd.DataFrame, List[pd.DataFrame]]]:
    """
    Plot a line with shaded area, automatically switching between single and multiple line versions.

    Args:
        axis: matplotlib axis or scitex axis wrapper
        xs: x values (single array or list of arrays)
        ys_lower: lower bound y values (single array or list of arrays)
        ys_middle: middle y values (single array or list of arrays)
        ys_upper: upper bound y values (single array or list of arrays)
        color: color or list of colors for the lines
        **kwargs: additional plotting parameters

    Returns:
        tuple: (axis, DataFrame or list of DataFrames with plot data)
    """
    is_single = not (
        isinstance(xs, list)
        and isinstance(ys_lower, list)
        and isinstance(ys_middle, list)
        and isinstance(ys_upper, list)
    )

    if is_single:
        assert (
            len(xs) == len(ys_lower) == len(ys_middle) == len(ys_upper)
        ), "All arrays must have the same length for single line plot"

        return _plot_single_shaded_line(
            axis, xs, ys_lower, ys_middle, ys_upper, color=color, **kwargs
        )
    else:
        return _plot_shaded_line(
            axis, xs, ys_lower, ys_middle, ys_upper, color=color, **kwargs
        )


# EOF
