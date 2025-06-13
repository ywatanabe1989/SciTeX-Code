# Add your tests here

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/ax/_plot/_plot_scatter_hist.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-05-02 18:14:56 (ywatanabe)"
# # File: /home/ywatanabe/proj/scitex_repo/src/scitex/plt/ax/_plot/_plot_scatter_hist.py
# # ----------------------------------------
# import os
# __FILE__ = (
#     "./src/scitex/plt/ax/_plot/_plot_scatter_hist.py"
# )
# __DIR__ = os.path.dirname(__FILE__)
# # ----------------------------------------
#
# import numpy as np
#
#
# def plot_scatter_hist(
#     ax,
#     x,
#     y,
#     fig=None,
#     hist_bins: int = 20,
#     scatter_alpha: float = 0.6,
#     scatter_size: float = 20,
#     scatter_color: str = "blue",
#     hist_color_x: str = "blue",
#     hist_color_y: str = "red",
#     hist_alpha: float = 0.5,
#     scatter_ratio: float = 0.8,
#     **kwargs,
# ):
#     """
#     Plot a scatter plot with histograms on the x and y axes.
#
#     Parameters
#     ----------
#     ax : matplotlib.axes.Axes
#         The main scatter plot axes
#     x : array-like
#         x data for scatter plot and histogram
#     y : array-like
#         y data for scatter plot and histogram
#     fig : matplotlib.figure.Figure, optional
#         Figure to create axes in. If None, uses ax.figure
#     hist_bins : int, optional
#         Number of bins for histograms, default 20
#     scatter_alpha : float, optional
#         Alpha value for scatter points, default 0.6
#     scatter_size : float, optional
#         Size of scatter points, default 20
#     scatter_color : str, optional
#         Color of scatter points, default "blue"
#     hist_color_x : str, optional
#         Color of x-axis histogram, default "blue"
#     hist_color_y : str, optional
#         Color of y-axis histogram, default "red"
#     hist_alpha : float, optional
#         Alpha value for histograms, default 0.5
#     scatter_ratio : float, optional
#         Ratio of main plot to histograms, default 0.8
#     **kwargs
#         Additional keyword arguments passed to scatter and hist functions
#
#     Returns
#     -------
#     tuple
#         (ax, ax_histx, ax_histy, hist_data) - All axes objects and histogram data
#         hist_data is a dictionary containing histogram counts and bin edges
#     """
#     # Get the current figure if not provided
#     if fig is None:
#         fig = ax.figure
#
#     # Calculate the positions based on scatter_ratio
#     margin = 0.1 * (1 - scatter_ratio)
#     hist_size = 0.2 * scatter_ratio
#
#     # Create the histogram axes
#     ax_histx = fig.add_axes(
#         [
#             ax.get_position().x0,
#             ax.get_position().y1 + margin,
#             ax.get_position().width * scatter_ratio,
#             hist_size,
#         ]
#     )
#     ax_histy = fig.add_axes(
#         [
#             ax.get_position().x1 + margin,
#             ax.get_position().y0,
#             hist_size,
#             ax.get_position().height * scatter_ratio,
#         ]
#     )
#
#     # No labels for histograms
#     ax_histx.tick_params(axis="x", labelbottom=False)
#     ax_histy.tick_params(axis="y", labelleft=False)
#
#     # The scatter plot
#     ax.scatter(
#         x,
#         y,
#         alpha=scatter_alpha,
#         s=scatter_size,
#         color=scatter_color,
#         **kwargs,
#     )
#
#     # Calculate histogram data
#     hist_x, bin_edges_x = np.histogram(x, bins=hist_bins)
#     hist_y, bin_edges_y = np.histogram(y, bins=hist_bins)
#
#     # Plot histograms
#     ax_histx.hist(x, bins=hist_bins, color=hist_color_x, alpha=hist_alpha)
#     ax_histy.hist(
#         y,
#         bins=hist_bins,
#         orientation="horizontal",
#         color=hist_color_y,
#         alpha=hist_alpha,
#     )
#
#     # Create return data structure
#     hist_data = {
#         "hist_x": hist_x,
#         "hist_y": hist_y,
#         "bin_edges_x": bin_edges_x,
#         "bin_edges_y": bin_edges_y,
#     }
#
#     return ax, ax_histx, ax_histy, hist_data
#
# # EOF
# --------------------------------------------------------------------------------
# End of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/ax/_plot/_plot_scatter_hist.py
# --------------------------------------------------------------------------------
