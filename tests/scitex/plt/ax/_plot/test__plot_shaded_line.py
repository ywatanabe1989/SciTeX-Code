#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-02 23:28:53 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/tests/scitex/plt/ax/_plot/test__plot_shaded_line.py
# ----------------------------------------
import os

__FILE__ = "./tests/scitex/plt/ax/_plot/test__plot_shaded_line.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import matplotlib.pyplot as plt
import numpy as np
import pytest
from scitex.plt.ax._plot import plot_shaded_line


class TestPlotShadedLine:
    def setup_method(self):
        # Setup test fixtures
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)

        # Create sample data
        self.x = np.linspace(0, 10, 100)
        self.y_middle = np.sin(self.x)
        self.y_lower = self.y_middle - 0.2
        self.y_upper = self.y_middle + 0.2

        # Create output directory if it doesn't exist
        self.out_dir = __file__.replace(".py", "_out")
        os.makedirs(self.out_dir, exist_ok=True)

    def teardown_method(self):
        # Clean up after tests
        plt.close(self.fig)

    def save_test_figure(self, method_name):
        """Helper method to save figure using method name"""
        from scitex.io import save

        spath = f"./{os.path.basename(__file__).replace('.py', '')}_{method_name}.jpg"
        save(self.fig, spath)
        # Check saved file
        actual_spath = os.path.join(self.out_dir, spath)
        assert os.path.exists(actual_spath), f"Failed to save figure to {spath}"

    def test_plot_single_shaded_line(self):
        # Test with single shaded line
        ax, df = plot_shaded_line(
            self.ax,
            self.x,
            self.y_lower,
            self.y_middle,
            self.y_upper,
            label="Test Shade",
        )

        self.ax.set_title("Single Shaded Line")
        # Save figure
        self.save_test_figure("test_plot_single_shaded_line")

        # Check results
        assert len(self.ax.lines) > 0, "No lines were plotted"
        assert len(self.ax.collections) > 0, "No shaded area was created"

    def test_plot_multiple_shaded_line(self):
        # Test with first shaded line
        ax, df1 = plot_shaded_line(
            self.ax,
            self.x,
            self.y_lower,
            self.y_middle,
            self.y_upper,
            label="Test Shade 1",
            color="blue",
        )

        # Add second shaded line with different parameters
        y_middle2 = np.cos(self.x)
        y_lower2 = y_middle2 - 0.3
        y_upper2 = y_middle2 + 0.3

        ax, df2 = plot_shaded_line(
            self.ax,
            self.x,
            y_lower2,
            y_middle2,
            y_upper2,
            label="Test Shade 2",
            color="red",
        )

        self.ax.set_title("Multiple Shaded Lines")
        self.ax.legend()

        # Save figure
        self.save_test_figure("test_plot_multiple_shaded_line")

        # Check results
        assert len(self.ax.lines) >= 2, "Expected at least 2 lines"
        assert len(self.ax.collections) >= 2, "Expected at least 2 shaded areas"

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/plt/ax/_plot/_plot_shaded_line.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-05-02 23:28:32 (ywatanabe)"
# # File: /home/ywatanabe/proj/scitex_repo/src/scitex/plt/ax/_plot/_plot_shaded_line.py
# # ----------------------------------------
# import os
# 
# __FILE__ = "./src/scitex/plt/ax/_plot/_plot_shaded_line.py"
# __DIR__ = os.path.dirname(__FILE__)
# # ----------------------------------------
# 
# from typing import List, Optional, Tuple, Union
# 
# import matplotlib
# import numpy as np
# import pandas as pd
# from matplotlib.axes._axes import Axes
# 
# from ....types import ColorLike
# from ....plt.utils import assert_valid_axis
# 
# 
# def _plot_single_shaded_line(
#     axis: Union[Axes, 'AxisWrapper'],
#     xx: np.ndarray,
#     y_lower: np.ndarray,
#     y_middle: np.ndarray,
#     y_upper: np.ndarray,
#     color: Optional[ColorLike] = None,
#     alpha: float = 0.3,
#     **kwargs
# ) -> Tuple[Union[Axes, 'AxisWrapper'], pd.DataFrame]:
#     """Plot a line with shaded area between y_lower and y_upper bounds."""
#     assert_valid_axis(axis, "First argument must be a matplotlib axis or scitex axis wrapper")
#     assert (
#         len(xx) == len(y_middle) == len(y_lower) == len(y_upper)
#     ), "All arrays must have the same length"
# 
#     label = kwargs.get("label")
#     if kwargs.get("label"):
#         del kwargs["label"]
#     axis.plot(xx, y_middle, color=color, alpha=alpha, label=label, **kwargs)
#     kwargs["linewidth"] = 0
#     kwargs["edgecolor"] = "none"  # Remove edge line
#     axis.fill_between(xx, y_lower, y_upper, alpha=alpha, color=color, **kwargs)
# 
#     return axis, pd.DataFrame(
#         {"x": xx, "y_lower": y_lower, "y_middle": y_middle, "y_upper": y_upper}
#     )
# 
# 
# def _plot_shaded_line(
#     axis: Union[Axes, 'AxisWrapper'],
#     xs: List[np.ndarray],
#     ys_lower: List[np.ndarray],
#     ys_middle: List[np.ndarray],
#     ys_upper: List[np.ndarray],
#     color: Optional[Union[List[ColorLike], ColorLike]] = None,
#     **kwargs
# ) -> Tuple[Union[Axes, 'AxisWrapper'], List[pd.DataFrame]]:
#     """Plot multiple lines with shaded areas between ys_lower and ys_upper bounds."""
#     assert_valid_axis(axis, "First argument must be a matplotlib axis or scitex axis wrapper")
#     assert (
#         len(xs) == len(ys_lower) == len(ys_middle) == len(ys_upper)
#     ), "All input lists must have the same length"
# 
#     results = []
#     colors = color
#     color_list = colors
# 
#     if colors is not None:
#         if not isinstance(colors, list):
#             color_list = [colors] * len(xs)
#         else:
#             assert len(colors) == len(xs), "Number of colors must match number of lines"
#             color_list = colors
# 
#         for idx, (xx, y_lower, y_middle, y_upper) in enumerate(
#             zip(xs, ys_lower, ys_middle, ys_upper)
#         ):
#             this_kwargs = kwargs.copy()
#             this_kwargs["color"] = color_list[idx]
#             _, result_df = _plot_single_shaded_line(
#                 axis, xx, y_lower, y_middle, y_upper, **this_kwargs
#             )
#             results.append(result_df)
#     else:
#         for xx, y_lower, y_middle, y_upper in zip(xs, ys_lower, ys_middle, ys_upper):
#             _, result_df = _plot_single_shaded_line(
#                 axis, xx, y_lower, y_middle, y_upper, **kwargs
#             )
#             results.append(result_df)
# 
#     return axis, results
# 
# 
# def plot_shaded_line(
#     axis: Union[Axes, 'AxisWrapper'],
#     xs: Union[np.ndarray, List[np.ndarray]],
#     ys_lower: Union[np.ndarray, List[np.ndarray]],
#     ys_middle: Union[np.ndarray, List[np.ndarray]],
#     ys_upper: Union[np.ndarray, List[np.ndarray]],
#     color: Optional[Union[ColorLike, List[ColorLike]]] = None,
#     **kwargs
# ) -> Tuple[Union[Axes, 'AxisWrapper'], Union[pd.DataFrame, List[pd.DataFrame]]]:
#     """
#     Plot a line with shaded area, automatically switching between single and multiple line versions.
# 
#     Args:
#         axis: matplotlib axis or scitex axis wrapper
#         xs: x values (single array or list of arrays)
#         ys_lower: lower bound y values (single array or list of arrays)
#         ys_middle: middle y values (single array or list of arrays)
#         ys_upper: upper bound y values (single array or list of arrays)
#         color: color or list of colors for the lines
#         **kwargs: additional plotting parameters
# 
#     Returns:
#         tuple: (axis, DataFrame or list of DataFrames with plot data)
#     """
#     is_single = not (
#         isinstance(xs, list)
#         and isinstance(ys_lower, list)
#         and isinstance(ys_middle, list)
#         and isinstance(ys_upper, list)
#     )
# 
#     if is_single:
#         assert (
#             len(xs) == len(ys_lower) == len(ys_middle) == len(ys_upper)
#         ), "All arrays must have the same length for single line plot"
# 
#         return _plot_single_shaded_line(
#             axis, xs, ys_lower, ys_middle, ys_upper, color=color, **kwargs
#         )
#     else:
#         return _plot_shaded_line(
#             axis, xs, ys_lower, ys_middle, ys_upper, color=color, **kwargs
#         )
# 
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/plt/ax/_plot/_plot_shaded_line.py
# --------------------------------------------------------------------------------
