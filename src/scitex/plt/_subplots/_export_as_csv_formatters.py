#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-18 18:14:26 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/plt/_subplots/_export_as_csv_formatters.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/plt/_subplots/_export_as_csv_formatters.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

# Import formatters from the submodule
from scitex.plt._subplots._export_as_csv_formatters import (
    # Standard matplotlib formatters
    _format_plot,
    _format_scatter,
    _format_bar,
    _format_barh,
    _format_hist,
    _format_boxplot,
    _format_contour,
    _format_errorbar,
    _format_eventplot,
    _format_fill,
    _format_fill_between,
    _format_imshow,
    _format_imshow2d,
    _format_violin,
    _format_violinplot,
    
    # Custom plotting formatters
    _format_plot_box,
    _format_plot_conf_mat,
    _format_plot_ecdf,
    _format_plot_fillv,
    _format_plot_heatmap,
    _format_plot_image,
    _format_plot_joyplot,
    _format_plot_kde,
    _format_plot_line,
    _format_plot_mean_ci,
    _format_plot_mean_std,
    _format_plot_median_iqr,
    _format_plot_raster,
    _format_plot_rectangle,
    _format_plot_scatter_hist,
    _format_plot_shaded_line,
    _format_plot_violin,
    
    # Seaborn formatters
    _format_sns_barplot,
    _format_sns_boxplot,
    _format_sns_heatmap,
    _format_sns_histplot,
    _format_sns_jointplot,
    _format_sns_kdeplot,
    _format_sns_lineplot,
    _format_sns_pairplot,
    _format_sns_scatterplot,
    _format_sns_stripplot,
    _format_sns_swarmplot,
    _format_sns_violinplot,
)

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