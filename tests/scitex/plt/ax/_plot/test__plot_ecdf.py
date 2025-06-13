#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-01 21:54:16 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/tests/scitex/plt/ax/_plot/test__plot_ecdf.py
# ----------------------------------------
import os

__FILE__ = "./tests/scitex/plt/ax/_plot/test__plot_ecdf.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pytest
from scitex.plt.ax._plot import plot_ecdf

matplotlib.use("Agg")


class TestPlotECDF:
    def setup_method(self):
        # Setup test fixtures
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)

        # Create sample data
        np.random.seed(42)
        self.data = [np.random.uniform(0, 1, 100)]

    def teardown_method(self):
        # Clean up after tests
        plt.close(self.fig)

    def test_basic_functionality(self):
        # Test basic plot_ecdf functionality
        ax, df = plot_ecdf(self.ax, self.data)

        # Check that lines were added to the plot
        assert len(self.ax.lines) > 0

        # Check that the returned DataFrame has the expected columns
        expected_columns = ["x", "y", "n", "x_step", "y_step"]
        assert all(col in df.columns for col in expected_columns)

    def test_with_nan_values(self):
        # Test with data containing NaN values
        data_with_nan = [np.array([0.1, 0.2, np.nan, 0.4, 0.5, np.nan])]

        ax, df = plot_ecdf(self.ax, data_with_nan)

        # NaN values should be removed
        expected_length = (~np.isnan(np.hstack(data_with_nan))).sum() * 2 - 1
        assert len(df) == expected_length
        assert df["n"].iloc[0] == 4

    def test_with_plot_kwargs(self):
        # Test with additional plot kwargs
        ax, df = plot_ecdf(self.ax, self.data, color="red", linewidth=2, alpha=0.5)

        # Plot style should be applied
        for line in self.ax.lines:
            if line.get_linestyle() != "None":
                assert line.get_color() == "red"
                assert line.get_linewidth() == 2
                assert line.get_alpha() == 0.5

    def test_step_values(self):
        # Test that the step values are correct
        sorted_data = np.sort(self.data[0])
        ax, df = plot_ecdf(self.ax, self.data)

        # Check that x values in df match sorted data
        assert np.allclose(df["x"].values[: len(sorted_data)], sorted_data)

        # Check that plot_ecdf values increase monotonically
        assert np.all(np.diff(df["y"].values)[: len(sorted_data) - 1] >= 0)

        # Check that the number of steps matches expectations
        expected_steps = 2 * len(sorted_data) - 1
        assert len(df["x_step"]) == expected_steps

    def test_plot_ecdf_savefig(self):
        ax, df = plot_ecdf(self.ax, self.data, color="blue")
        ax.set_title("ECDF Plot")

        # Saving
        from scitex.io import save

        spath = f"./{os.path.basename(__file__)}.jpg"
        save(self.fig, spath)

        # Check saved file
        ACTUAL_SAVE_DIR = __file__.replace(".py", "_out")
        actual_spath = os.path.join(ACTUAL_SAVE_DIR, spath)
        assert os.path.exists(actual_spath), f"Failed to save figure to {spath}"


if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/ax/_plot/_plot_ecdf.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-05-01 20:17:59 (ywatanabe)"
# # File: /home/ywatanabe/proj/scitex_repo/src/scitex/plt/ax/_plot/_plot_ecdf.py
# # ----------------------------------------
# import os
# __FILE__ = (
#     "./src/scitex/plt/ax/_plot/_plot_ecdf.py"
# )
# __DIR__ = os.path.dirname(__FILE__)
# # ----------------------------------------
#
# import warnings
#
# import matplotlib
# import numpy as np
#
# from ....pd._force_df import force_df as scitex_pd_force_df
#
#
# def plot_ecdf(axis, data, **kwargs):
#     """Plot Empirical Cumulative Distribution Function (ECDF).
#
#     The ECDF shows the proportion of data points less than or equal to each value,
#     representing the empirical estimate of the cumulative distribution function.
#
#     Parameters
#     ----------
#     axis : matplotlib.axes.Axes
#         Matplotlib axis to plot on
#     data : array-like
#         Data to compute and plot ECDF for. NaN values are ignored.
#     **kwargs : dict
#         Additional arguments to pass to plot function
#
#     Returns
#     -------
#     tuple
#         (axis, DataFrame) containing the plot and data
#     """
#     assert isinstance(
#         axis, matplotlib.axes._axes.Axes
#     ), "First argument must be a matplotlib axis"
#
#     # Flatten and remove NaN values
#     data = np.hstack(data)
#
#     # Warnings
#     if np.isnan(data).any():
#         warnings.warn("NaN value are ignored for ECDF plot.")
#     data = data[~np.isnan(data)]
#     nn = len(data)
#
#     # Sort the data and compute the ECDF values
#     data_sorted = np.sort(data)
#     ecdf_perc = 100 * np.arange(1, len(data_sorted) + 1) / len(data_sorted)
#
#     # Create the pseudo x-axis for step plotting
#     x_step = np.repeat(data_sorted, 2)[1:]
#     y_step = np.repeat(ecdf_perc, 2)[:-1]
#
#     # Plot the ECDF using steps
#     axis.plot(x_step, y_step, drawstyle="steps-post", **kwargs)
#
#     # Scatter the original data points
#     axis.plot(data_sorted, ecdf_perc, marker=".", linestyle="none")
#
#     # Set ylim, xlim, and aspect ratio
#     axis.set_ylim(0, 100)
#     axis.set_xlim(0, 1.0)
#
#     # Create a DataFrame to hold the ECDF data
#     df = scitex_pd_force_df(
#         {
#             "x": data_sorted,
#             "y": ecdf_perc,
#             "n": nn,
#             "x_step": x_step,
#             "y_step": y_step,
#         }
#     )
#
#     return axis, df
#
# # EOF
# --------------------------------------------------------------------------------
# End of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/ax/_plot/_plot_ecdf.py
# --------------------------------------------------------------------------------
