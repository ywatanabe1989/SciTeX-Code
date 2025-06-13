#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-05 14:15:00 (ywatanabe)"
# File: ./examples/scitex/plt/sigmaplot_export_example.py
# ----------------------------------------
import os
__FILE__ = (
    "./examples/scitex/plt/sigmaplot_export_example.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
  - Demonstrates SigmaPlot CSV export functionality
  - Creates plots with SciTeX tracking enabled
  - Shows automatic CSV export when saving figures
  - Exports data in regular and SigmaPlot-compatible formats

Dependencies:
  - scripts:
    - None
  - packages:
    - numpy
    - matplotlib
    - scitex
IO:
  - input-files:
    - None

  - output-files:
    - regular_export.csv
    - sigmaplot_export.csv
    - example_plot.png
    - example_plot.csv
    - example_plot_for_sigmaplot.csv
"""

"""Imports"""
import argparse
import numpy as np

"""Warnings"""
# scitex.pd.ignore_SettingWithCopyWarning()
# warnings.simplefilter("ignore", UserWarning)

"""Parameters"""
# from scitex.io import load_configs
# CONFIG = load_configs()

"""Functions & Classes"""
def main(args):
    
    # Create figure and axes with SciTeX tracking
    fig, ax = scitex.plt.subplots(figsize=(8, 6))
    
    # Generate sample data
    x = np.linspace(0, 10, 100)
    y1 = np.sin(x) + np.random.normal(0, 0.1, len(x))
    y2 = np.cos(x) + np.random.normal(0, 0.1, len(x))
    
    # Create plots with IDs for tracking
    ax.plot(x, y1, label='Sine + Noise', id='sine_data')
    ax.plot(x, y2, label='Cosine + Noise', id='cosine_data')
    
    # Add bar plot
    bar_x = np.arange(3)
    bar_y = [2.5, 3.7, 1.8]
    bar_err = [0.2, 0.3, 0.15]
    ax.bar(bar_x, bar_y, yerr=bar_err, alpha=0.5, id='bar_data')
    
    # Customize plot
    ax.set_xlabel('X Values')
    ax.set_ylabel('Y Values')
    ax.set_title('Example Plot for SigmaPlot Export')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Export data in different formats
    print("=== Exporting plot data ===")
    
    # 1. Export regular CSV (just the data)
    df_regular = ax.export_as_csv()
    print(f"\nRegular CSV shape: {df_regular.shape}")
    print(f"Regular CSV columns: {list(df_regular.columns)}")
    scitex.io.save(df_regular, 'regular_export.csv')
    
    # 2. Export SigmaPlot-formatted CSV (with visual parameters)
    df_sigmaplot = ax.export_as_csv_for_sigmaplot()
    print(f"\nSigmaPlot CSV shape: {df_sigmaplot.shape}")
    print(f"SigmaPlot CSV columns: {list(df_sigmaplot.columns)[:8]}...")  # Show first 8 columns
    scitex.io.save(df_sigmaplot, 'sigmaplot_export.csv')
    
    # 3. Save figure - this automatically creates both CSV files
    print("\n=== Saving figure (automatically creates CSV files) ===")
    scitex.io.save(fig, 'example_plot.png', verbose=True)
    
    # The above command creates:
    # - example_plot.png (the figure)
    # - example_plot.csv (regular data export)
    # - example_plot_for_sigmaplot.csv (SigmaPlot-formatted export)
    
    print("\n=== Example of SigmaPlot CSV content ===")
    print(df_sigmaplot.head(10))
    
    print("\n✓ Example completed successfully!")
    print("Files created:")
    print("  - regular_export.csv")
    print("  - sigmaplot_export.csv")
    print("  - example_plot.png")
    print("  - example_plot.csv")
    print("  - example_plot_for_sigmaplot.csv")
    
    return 0


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    import scitex

    script_mode = scitex.gen.is_script()
    parser = argparse.ArgumentParser(description="SigmaPlot CSV export example")
    args = parser.parse_args()
    scitex.str.printc(args, c="yellow")
    return args


def run_main() -> None:
    """Initialize scitex framework, run main function, and cleanup."""
    global CONFIG, CC, sys, plt

    import sys

    import matplotlib.pyplot as plt
    import scitex

    args = parse_args()

    CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.gen.start(
        sys,
        plt,
        args=args,
        file=__FILE__,
        verbose=False,
        agg=True,
    )

    exit_status = main(args)

    scitex.gen.close(
        CONFIG,
        verbose=False,
        notify=False,
        message="",
        exit_status=exit_status,
    )


if __name__ == "__main__":
    run_main()