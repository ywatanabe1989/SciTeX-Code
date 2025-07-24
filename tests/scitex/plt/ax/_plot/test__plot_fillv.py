#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-03 15:15:42 (ywatanabe)"
# File: /home/ywatanabe/proj/_scitex_repo/tests/scitex/plt/ax/_plot/test__plot_fillv.py
# ----------------------------------------
import os

__FILE__ = "./tests/scitex/plt/ax/_plot/test__plot_fillv.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pytest
from scitex.plt.ax._plot import plot_fillv

matplotlib.use("Agg")


class TestPlotFillV:
    def setup_method(self):
        # Setup test fixtures
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
        self.ax.plot(np.linspace(0, 10, 100), np.sin(np.linspace(0, 10, 100)))
        # Setup multiple axes
        self.fig_multi = plt.figure()
        self.axes = np.array(
            [
                self.fig_multi.add_subplot(2, 2, 1),
                self.fig_multi.add_subplot(2, 2, 2),
                self.fig_multi.add_subplot(2, 2, 3),
                self.fig_multi.add_subplot(2, 2, 4),
            ]
        )
        # Create output directory if it doesn't exist
        self.out_dir = __file__.replace(".py", "_out")
        os.makedirs(self.out_dir, exist_ok=True)

    def teardown_method(self):
        # Clean up after tests
        plt.close(self.fig)
        plt.close(self.fig_multi)

    def save_test_figure(self, fig, method_name):
        """Helper method to save figure using method name"""
        from scitex.io import save

        spath = f"./{os.path.basename(__file__).replace('.py', '')}_{method_name}.jpg"
        save(fig, spath)
        # Check saved file
        actual_spath = os.path.join(self.out_dir, spath)
        assert os.path.exists(actual_spath), f"Failed to save figure to {spath}"

    def test_single_axis(self):
        # Test with single axis
        starts = [2, 4]
        ends = [3, 5]
        ax = plot_fillv(self.ax, starts, ends)
        self.ax.set_title("Single Axis Fill Between")

        # Save figure
        self.save_test_figure(self.fig, "test_single_axis")

        # Check that fill was added
        assert len(self.ax.patches) > 0

    def test_multiple_axes(self):
        # Test with array of axes
        starts = [2, 4]
        ends = [3, 5]
        for ax in self.axes:
            ax.plot(np.linspace(0, 10, 100), np.sin(np.linspace(0, 10, 100)))
            ax = plot_fillv(ax, starts, ends)

        # axes = plot_fillv(self.axes, starts, ends)
        # for ii, ax in enumerate(self.axes):
        #     ax.set_title(f"Subplot {ii+1}")

        # Save figure
        self.save_test_figure(self.fig_multi, "test_multiple_axes")

        # # Check that fill was added to all axes
        # for ax in axes:
        #     assert len(ax.patches) > 0

    def test_custom_color(self):
        # Test with custom color
        starts = [2, 4]
        ends = [3, 5]
        color = "green"
        ax = plot_fillv(self.ax, starts, ends, color=color)
        self.ax.set_title("Fill Between with Custom Color")

        # Save figure
        self.save_test_figure(self.fig, "test_custom_color")

        # Check color
        assert self.ax.patches[0].get_facecolor()[0:3] == matplotlib.colors.to_rgb(
            color
        )

    def test_plot_fillv_savefig(self):
        starts = [2, 4]
        ends = [3, 5]
        axes = plot_fillv(self.axes, starts, ends)
        for ii, ax in enumerate(self.axes):
            ax.set_title(f"Subplot {ii+1}")

        # Saving
        from scitex.io import save

        spath = f"./{os.path.basename(__file__)}.jpg"
        save(self.fig_multi, spath)

        # Check saved file
        ACTUAL_SAVE_DIR = __file__.replace(".py", "_out")
        actual_spath = os.path.join(ACTUAL_SAVE_DIR, spath)
        assert os.path.exists(actual_spath), f"Failed to save figure to {spath}"

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/plt/ax/_plot/_plot_fillv.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-04-30 21:26:45 (ywatanabe)"
# # File: /home/ywatanabe/proj/scitex_repo/src/scitex/plt/ax/_plot_fillv.py
# # ----------------------------------------
# import os
# 
# __FILE__ = "./src/scitex/plt/ax/_plot_fillv.py"
# __DIR__ = os.path.dirname(__FILE__)
# # ----------------------------------------
# 
# import matplotlib
# import numpy as np
# from ....plt.utils import assert_valid_axis
# 
# 
# def plot_fillv(axes, starts, ends, color="red", alpha=0.2):
#     """
#     Fill between specified start and end intervals on an axis or array of axes.
# 
#     Parameters
#     ----------
#     axes : matplotlib.axes.Axes or scitex.plt._subplots.AxisWrapper or numpy.ndarray of axes
#         The axis object(s) to fill intervals on.
#     starts : array-like
#         Array-like of start positions.
#     ends : array-like
#         Array-like of end positions.
#     color : str, optional
#         The color to use for the filled regions. Default is "red".
#     alpha : float, optional
#         The alpha blending value, between 0 (transparent) and 1 (opaque). Default is 0.2.
# 
#     Returns
#     -------
#     list
#         List of axes with filled intervals.
#     """
# 
#     is_axes = isinstance(axes, np.ndarray)
# 
#     axes = axes if isinstance(axes, np.ndarray) else [axes]
# 
#     for ax in axes:
#         assert_valid_axis(ax, "First argument must be a matplotlib axis or scitex axis wrapper")
#         for start, end in zip(starts, ends):
#             ax.axvspan(start, end, color=color, alpha=alpha)
# 
#     if not is_axes:
#         return axes[0]
#     else:
#         return axes
# 
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/plt/ax/_plot/_plot_fillv.py
# --------------------------------------------------------------------------------
