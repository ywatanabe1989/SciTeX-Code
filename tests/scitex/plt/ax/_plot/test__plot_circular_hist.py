#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-03 15:13:17 (ywatanabe)"
# File: /home/ywatanabe/proj/_scitex_repo/tests/scitex/plt/ax/_plot/test__plot_circular_hist.py
# ----------------------------------------
import os

__FILE__ = "./tests/scitex/plt/ax/_plot/test__plot_circular_hist.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from scitex.plt.ax._plot import plot_circular_hist

matplotlib.use("Agg")


class TestPlotCircularHist:
    def setup_method(self):
        # Setup test fixtures - polar axes required for circular histogram
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, projection="polar")
        # Create sample radians data (0 to 2pi)
        self.rads = np.random.uniform(0, 2 * np.pi, 1000)
        # Create output directory if it doesn't exist
        self.out_dir = __file__.replace(".py", "_out")
        os.makedirs(self.out_dir, exist_ok=True)

    def teardown_method(self):
        # Clean up after tests
        plt.close(self.fig)

    def save_test_figure(self, method_name):
        """Helper method to save figure using method name"""
        from scitex.io import save

        spath = f".{method_name}.jpg"
        save(self.fig, spath)
        # Check saved file
        actual_spath = os.path.join(self.out_dir, spath)
        assert os.path.exists(actual_spath), f"Failed to save figure to {spath}"

    def test_basic_functionality(self):
        # Test with default parameters
        n, bins, patches = plot_circular_hist(self.ax, self.rads)
        self.ax.set_title("Basic Circular Histogram")

        # Save figure
        self.save_test_figure("test_basic_functionality")

        # Check return values
        assert isinstance(n, np.ndarray)
        assert isinstance(bins, np.ndarray)
        assert len(n) == len(bins) - 1
        assert len(n) == 16  # Default bin count
        # Check that patches were added to the plot
        assert len(patches) == 16

    def test_with_custom_bins(self):
        # Test with custom number of bins
        bin_count = 24
        n, bins, patches = plot_circular_hist(self.ax, self.rads, bins=bin_count)
        self.ax.set_title("Circular Histogram with Custom Bins")

        # Save figure
        self.save_test_figure("test_with_custom_bins")

        # Check correct number of bins
        assert len(n) == bin_count
        assert len(patches) == bin_count

    def test_with_no_gaps(self):
        # Test with gaps=False
        n, bins, patches = plot_circular_hist(self.ax, self.rads, gaps=False)
        self.ax.set_title("Circular Histogram with No Gaps")

        # Save figure
        self.save_test_figure("test_with_no_gaps")

        # Check that bins span the entire circle
        assert np.isclose(bins[0], -np.pi)
        assert np.isclose(bins[-1], np.pi)

    def test_with_custom_color(self):
        # Test with custom color
        color = "red"
        n, bins, patches = plot_circular_hist(self.ax, self.rads, color=color)
        self.ax.set_title("Circular Histogram with Custom Color")

        # Save figure
        self.save_test_figure("test_with_custom_color")

        # Check that patches have the correct color
        for patch in patches:
            assert patch.get_edgecolor()[0:3] == matplotlib.colors.to_rgb(color)

    def test_with_non_density(self):
        # Test with density=False
        n, bins, patches = plot_circular_hist(self.ax, self.rads, density=False)
        self.ax.set_title("Circular Histogram with Non-Density")

        # Save figure
        self.save_test_figure("test_with_non_density")

        # Check that y-ticks are visible
        assert len(self.ax.get_yticks()) > 0

    def test_with_offset(self):
        # Test with custom offset
        offset = np.pi / 4  # 45 degrees
        n, bins, patches = plot_circular_hist(self.ax, self.rads, offset=offset)
        self.ax.set_title("Circular Histogram with Offset")

        # Save figure
        self.save_test_figure("test_with_offset")

        # Check that theta offset was set correctly
        assert self.ax.get_theta_offset() == offset

    def test_with_range_bias(self):
        # Test with range_bias
        range_bias = 0.5
        n, bins, patches = plot_circular_hist(self.ax, self.rads, range_bias=range_bias)
        self.ax.set_title("Circular Histogram with Range Bias")

        # Save figure
        self.save_test_figure("test_with_range_bias")

        # Check that histogram is biased as expected
        assert np.isclose(bins[0], -np.pi + range_bias, atol=1e-5)

    def test_plot_circular_hist_savefig(self):
        n, bins, patches = plot_circular_hist(self.ax, self.rads, color="green")
        self.ax.set_title("Circular Histogram Test")

        # Saving
        from scitex.io import save

        spath = f"./{os.path.basename(__file__)}.jpg"
        save(self.fig, spath)

        # Check saved file
        ACTUAL_SAVE_DIR = __file__.replace(".py", "_out")
        actual_spath = os.path.join(ACTUAL_SAVE_DIR, spath)
        assert os.path.exists(actual_spath), f"Failed to save figure to {spath}"


# class TestMainFunctionality:
#     def setup_method(self):
#         # Setup test fixtures - polar axes required for circular histogram
#         self.fig = plt.figure()
#         self.ax = self.fig.add_subplot(111, projection="polar")

#         # Create sample radians data (0 to 2pi)
#         self.rads = np.random.uniform(0, 2 * np.pi, 1000)

#     def teardown_method(self):
#         # Clean up after tests
#         plt.close(self.fig)

#     def test_basic_functionality(self):
#         # Test with default parameters
#         n, bins, patches = plot_circular_hist(self.ax, self.rads)

#         # Check return values
#         assert isinstance(n, np.ndarray)
#         assert isinstance(bins, np.ndarray)
#         assert len(n) == len(bins) - 1
#         assert len(n) == 16  # Default bin count

#         # Check that patches were added to the plot
#         assert len(patches) == 16

#     def test_with_custom_bins(self):
#         # Test with custom number of bins
#         bin_count = 24
#         n, bins, patches = plot_circular_hist(
#             self.ax, self.rads, bins=bin_count
#         )

#         # Check correct number of bins
#         assert len(n) == bin_count
#         assert len(patches) == bin_count

#     def test_with_no_gaps(self):
#         # Test with gaps=False
#         n, bins, patches = plot_circular_hist(self.ax, self.rads, gaps=False)

#         # Check that bins span the entire circle
#         assert np.isclose(bins[0], -np.pi)
#         assert np.isclose(bins[-1], np.pi)

#     def test_with_custom_color(self):
#         # Test with custom color
#         color = "red"
#         n, bins, patches = plot_circular_hist(self.ax, self.rads, color=color)

#         # Check that patches have the correct color
#         for patch in patches:
#             assert patch.get_edgecolor()[0:3] == matplotlib.colors.to_rgb(
#                 color
#             )

#     def test_with_non_density(self):
#         # Test with density=False
#         n, bins, patches = plot_circular_hist(
#             self.ax, self.rads, density=False
#         )

#         # Check that y-ticks are visible
#         assert len(self.ax.get_yticks()) > 0

#     def test_with_offset(self):
#         # Test with custom offset
#         offset = np.pi / 4  # 45 degrees
#         n, bins, patches = plot_circular_hist(
#             self.ax, self.rads, offset=offset
#         )

#         # Check that theta offset was set correctly
#         assert self.ax.get_theta_offset() == offset

#     def test_with_range_bias(self):
#         # Test with range_bias
#         range_bias = 0.5
#         n, bins, patches = plot_circular_hist(
#             self.ax, self.rads, range_bias=range_bias
#         )

#         # Check that histogram is biased as expected
#         assert np.isclose(bins[0], -np.pi + range_bias, atol=1e-5)

#     def test_plot_circular_hist_savefig(self):

#         # fig = plt.figure()
#         # ax = fig.add_subplot(111, projection="polar")
#         # rads = np.random.uniform(0, 2 * np.pi, 1000)
#         n, bins, patches = plot_circular_hist(
#             self.ax, self.rads, color="green"
#         )

#         # Saving
#         from scitex.io import save

#         spath = f"./{os.path.basename(__file__)}.jpg"
#         save(self.fig, spath)

#         # Check saved file
#         ACTUAL_SAVE_DIR = __file__.replace(".py", "_out")
#         actual_spath = os.path.join(ACTUAL_SAVE_DIR, spath)
#         assert os.path.exists(
#             actual_spath
#         ), f"Failed to save figure to {spath}"

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/plt/ax/_plot/_plot_circular_hist.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-05-01 15:21:48 (ywatanabe)"
# # File: /home/ywatanabe/proj/scitex_repo/src/scitex/plt/ax/_plot/_plot_circular_hist.py
# # ----------------------------------------
# import os
# 
# __FILE__ = "./src/scitex/plt/ax/_plot/_plot_circular_hist.py"
# __DIR__ = os.path.dirname(__FILE__)
# # ----------------------------------------
# 
# # Time-stamp: "2024-02-03 13:10:50 (ywatanabe)"
# import matplotlib
# import numpy as np
# from ....plt.utils import assert_valid_axis
# 
# 
# def plot_circular_hist(
#     axis,
#     radians,
#     bins=16,
#     density=True,
#     offset=0,
#     gaps=True,
#     color=None,
#     range_bias=0,
# ):
#     """
#     Example:
#         fig, ax = plt.subplots(subplot_kw=dict(projection="polar"))
#         ax = scitex.plt.plot_circular_hist(ax, radians)
#     Produce a circular histogram of angles on ax.
# 
#     Parameters
#     ----------
#     ax : matplotlib.axes._subplots.PolarAxesSubplot or scitex.plt._subplots.AxisWrapper
#         axis instance created with subplot_kw=dict(projection='polar').
# 
#     radians : array
#         Angles to plot, expected in units of radians.
# 
#     bins : int, optional
#         Defines the number of equal-width bins in the range. The default is 16.
# 
#     density : bool, optional
#         If True plot frequency proportional to area. If False plot frequency
#         proportional to radius. The default is True.
# 
#     offset : float, optional
#         Sets the offset for the location of the 0 direction in units of
#         radians. The default is 0.
# 
#     gaps : bool, optional
#         Whether to allow gaps between bins. When gaps = False the bins are
#         forced to partition the entire [-pi, pi] range. The default is True.
# 
#     Returns
#     -------
#     n : array or list of arrays
#         The number of values in each bin.
# 
#     bins : array
#         The edges of the bins.
# 
#     patches : `.BarContainer` or list of a single `.Polygon`
#         Container of individual artists used to create the histogram
#         or list of such containers if there are multiple input datasets.
#     """
#     assert_valid_axis(axis, "First argument must be a matplotlib axis or scitex axis wrapper")
# 
#     # Wrap angles to [-pi, pi)
#     radians = (radians + np.pi) % (2 * np.pi) - np.pi
# 
#     # Force bins to partition entire circle
#     if not gaps:
#         bins = np.linspace(-np.pi, np.pi, num=bins + 1)
# 
#     # Bin data and record counts
#     n, bins = np.histogram(
#         radians, bins=bins, range=(-np.pi + range_bias, np.pi + range_bias)
#     )
# 
#     # Compute width of each bin
#     widths = np.diff(bins)
# 
#     # By default plot frequency proportional to area
#     if density:
#         # Area to assign each bin
#         area = n / radians.size
#         # Calculate corresponding bin radius
#         radius = (area / np.pi) ** 0.5
#     # Otherwise plot frequency proportional to radius
#     else:
#         radius = n
# 
#     mean_val = np.nanmean(radians)
#     std_val = np.nanstd(radians)
#     axis.axvline(mean_val, color=color)
#     axis.text(mean_val, 1, std_val)
# 
#     # Plot data on ax
#     patches = axis.bar(
#         bins[:-1],
#         radius,
#         zorder=1,
#         align="edge",
#         width=widths,
#         edgecolor=color,
#         alpha=0.9,
#         fill=False,
#         linewidth=1,
#     )
# 
#     # Set the direction of the zero angle
#     axis.set_theta_offset(offset)
# 
#     # Remove ylabels for area plots (they are mostly obstructive)
#     if density:
#         axis.set_yticks([])
# 
#     return n, bins, patches
# 
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/plt/ax/_plot/_plot_circular_hist.py
# --------------------------------------------------------------------------------
