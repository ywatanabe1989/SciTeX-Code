#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-21 01:52:02 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/plt/_subplots/_export_as_csv_formatters.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

# Import formatters from the submodule
from scitex.plt._subplots._export_as_csv_formatters import # Standard matplotlib formatters
    _format_plot
from scitex.plt._subplots._export_as_csv_formatters import _format_scatter
from scitex.plt._subplots._export_as_csv_formatters import _format_text
from scitex.plt._subplots._export_as_csv_formatters import _format_bar
from scitex.plt._subplots._export_as_csv_formatters import _format_barh
from scitex.plt._subplots._export_as_csv_formatters import _format_hist
from scitex.plt._subplots._export_as_csv_formatters import _format_boxplot
from scitex.plt._subplots._export_as_csv_formatters import _format_contour
from scitex.plt._subplots._export_as_csv_formatters import _format_errorbar
from scitex.plt._subplots._export_as_csv_formatters import _format_eventplot
from scitex.plt._subplots._export_as_csv_formatters import _format_fill
from scitex.plt._subplots._export_as_csv_formatters import _format_fill_between
from scitex.plt._subplots._export_as_csv_formatters import _format_imshow
from scitex.plt._subplots._export_as_csv_formatters import _format_imshow2d
from scitex.plt._subplots._export_as_csv_formatters import _format_violin
from scitex.plt._subplots._export_as_csv_formatters import _format_violinplot
from scitex.plt._subplots._export_as_csv_formatters import # Custom plotting formatters
    _format_plot_box
from scitex.plt._subplots._export_as_csv_formatters import _format_plot_conf_mat
from scitex.plt._subplots._export_as_csv_formatters import _format_plot_ecdf
from scitex.plt._subplots._export_as_csv_formatters import _format_plot_fillv
from scitex.plt._subplots._export_as_csv_formatters import _format_plot_heatmap
from scitex.plt._subplots._export_as_csv_formatters import _format_plot_image
from scitex.plt._subplots._export_as_csv_formatters import _format_plot_joyplot
from scitex.plt._subplots._export_as_csv_formatters import _format_plot_kde
from scitex.plt._subplots._export_as_csv_formatters import _format_plot_line
from scitex.plt._subplots._export_as_csv_formatters import _format_plot_mean_ci
from scitex.plt._subplots._export_as_csv_formatters import _format_plot_mean_std
from scitex.plt._subplots._export_as_csv_formatters import _format_plot_median_iqr
from scitex.plt._subplots._export_as_csv_formatters import _format_plot_raster
from scitex.plt._subplots._export_as_csv_formatters import _format_plot_rectangle
from scitex.plt._subplots._export_as_csv_formatters import _format_plot_scatter_hist
from scitex.plt._subplots._export_as_csv_formatters import _format_plot_shaded_line
from scitex.plt._subplots._export_as_csv_formatters import _format_plot_violin
from scitex.plt._subplots._export_as_csv_formatters import # Seaborn formatters
    _format_sns_barplot
from scitex.plt._subplots._export_as_csv_formatters import _format_sns_boxplot
from scitex.plt._subplots._export_as_csv_formatters import _format_sns_heatmap
from scitex.plt._subplots._export_as_csv_formatters import _format_sns_histplot
from scitex.plt._subplots._export_as_csv_formatters import _format_sns_jointplot
from scitex.plt._subplots._export_as_csv_formatters import _format_sns_kdeplot
from scitex.plt._subplots._export_as_csv_formatters import _format_sns_lineplot
from scitex.plt._subplots._export_as_csv_formatters import _format_sns_pairplot
from scitex.plt._subplots._export_as_csv_formatters import _format_sns_scatterplot
from scitex.plt._subplots._export_as_csv_formatters import _format_sns_stripplot
from scitex.plt._subplots._export_as_csv_formatters import _format_sns_swarmplot
from scitex.plt._subplots._export_as_csv_formatters import _format_sns_violinplot

def main():
    # Line
    import scitex
    import matplotlib.pyplot as plt

    fig, ax = scitex.plt.subplots()
    ax.plot([1, 2, 3], [4, 5, 6], id="plot1")
    ax.plot([4, 5, 6], [1, 2, 3], id="plot2")
    scitex.io.save(fig, "./plots.png")
    scitex.io.save(ax.export_as_csv(), "./plots.csv")

    # No tracking
    fig, ax = scitex.plt.subplots(track=False)
    ax.plot([1, 2, 3], [4, 5, 6], id="plot3")
    ax.plot([4, 5, 6], [1, 2, 3], id="plot4")
    scitex.io.save(fig, "./plots_wo_tracking.png")
    scitex.io.save(ax.export_as_csv(), "./plots_wo_tracking.csv")

    # Scatter
    fig, ax = scitex.plt.subplots()
    ax.scatter([1, 2, 3], [4, 5, 6], id="scatter1")
    ax.scatter([4, 5, 6], [1, 2, 3], id="scatter2")
    scitex.io.save(fig, "./scatters.png")
    scitex.io.save(ax.export_as_csv(), "./scatters.csv")

    # Box
    fig, ax = scitex.plt.subplots()
    ax.boxplot([1, 2, 3], id="boxplot1")
    scitex.io.save(fig, "./boxplot1.png")
    scitex.io.save(ax.export_as_csv(), "./boxplot1.csv")

    # Bar
    fig, ax = scitex.plt.subplots()
    ax.bar(["A", "B", "C"], [4, 5, 6], id="bar1")
    scitex.io.save(fig, "./bar1.png")
    scitex.io.save(ax.export_as_csv(), "./bar1.csv")


if __name__ == "__main__":
    # Main
    import sys
    import scitex

    CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.session.start(
        sys, plt, verbose=False, agg=True
    )
    main()
    scitex.session.close(CONFIG, verbose=False, notify=False)

# EOF
