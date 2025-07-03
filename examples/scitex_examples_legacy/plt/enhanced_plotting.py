#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-31 07:00:00 (Claude)"
# File: /data/gpfs/projects/punim2354/ywatanabe/.claude-worktree/scitex_repo/examples/scitex/plt/enhanced_plotting.py
# ----------------------------------------
import os

__FILE__ = "./examples/scitex/plt/enhanced_plotting.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
  - Demonstrates scitex.plt.subplots for automatic data tracking
  - Creates plots with automatic CSV export
  - Shows various plot types with scitex enhancements
  - Saves plots and data in the scitex output directory

Dependencies:
  - scripts:
    - None
  - packages:
    - numpy
    - pandas
    - matplotlib
    - scitex
IO:
  - input-files:
    - None

  - output-files:
    - trig_functions.png
    - trig_functions.png.csv
    - multi_panel_demo.png
    - multi_panel_demo.png.csv
    - statistical_comparison.png
    - statistical_comparison.png.csv
    - custom_styling.png
    - custom_styling.png.csv
    - power_functions.png
    - power_functions.png.csv
"""

"""Imports"""
import argparse

"""Warnings"""
# scitex.pd.ignore_SettingWithCopyWarning()
# warnings.simplefilter("ignore", UserWarning)

"""Parameters"""
# from scitex.io import load_configs
# CONFIG = load_configs()

"""Functions & Classes"""


def main(args):
    """Run all plotting examples."""
    example_basic_plotting()
    example_multi_panel()
    example_statistical_plot()
    example_custom_styling()
    example_data_export()

    print("\n✅ All plotting examples completed!")
    print(f"📁 Check {CONFIG.SDIR} for generated files")
    print("📊 Each .png file has a corresponding .csv with the plotted data!")
    return 0


def example_basic_plotting():
    """Basic plotting with data tracking."""
    print("\n1. Basic Line Plot with Data Tracking")

    # Generate sample data
    x = np.linspace(0, 2 * np.pi, 100)
    y1 = np.sin(x)
    y2 = np.cos(x)

    # Create figure with scitex
    fig, ax = scitex.plt.subplots(figsize=(8, 6))

    # Plot data
    ax.plot(x, y1, label="sin(x)", color="blue", linewidth=2)
    ax.plot(x, y2, label="cos(x)", color="red", linewidth=2)

    # Use scitex enhanced labeling
    ax.set_xlabel("x (radians)")
    ax.set_ylabel("y value")
    ax.set_title("Trigonometric Functions")

    ax.legend()
    ax.grid(True, alpha=0.3)

    # Save - this creates both .png and .csv files!
    scitex.io.save(fig, "trig_functions.png")
    print("   ✅ Saved: trig_functions.png AND trig_functions.png.csv")


def example_multi_panel():
    """Multi-panel figure with different plot types."""
    print("\n2. Multi-panel Figure")

    # Create 2x2 subplot
    fig, axes = scitex.plt.subplots(2, 2, figsize=(12, 10))

    # Panel 1: Scatter plot
    n_points = 200
    x_scatter = np.random.randn(n_points)
    y_scatter = 2 * x_scatter + np.random.randn(n_points) * 0.5

    axes[0, 0].scatter(x_scatter, y_scatter, alpha=0.5, s=30)
    axes[0, 0].set_xlabel("X values")
    axes[0, 0].set_ylabel("Y values")
    axes[0, 0].set_title("Scatter Plot")

    # Panel 2: Histogram
    data_hist = np.random.normal(100, 15, 1000)
    axes[0, 1].hist(data_hist, bins=30, alpha=0.7, color="green", edgecolor="black")
    axes[0, 1].set_xlabel("Value")
    axes[0, 1].set_ylabel("Frequency")
    axes[0, 1].set_title("Normal Distribution")

    # Panel 3: Bar plot
    categories = ["A", "B", "C", "D", "E"]
    values = np.random.randint(10, 100, len(categories))
    axes[1, 0].bar(categories, values, color="orange", alpha=0.8)
    axes[1, 0].set_xlabel("Category")
    axes[1, 0].set_ylabel("Count")
    axes[1, 0].set_title("Bar Chart")

    # Panel 4: Time series
    time = pd.date_range("2024-01-01", periods=100, freq="D")
    signal = np.cumsum(np.random.randn(100)) + 50
    axes[1, 1].plot(time, signal, color="purple", linewidth=1.5)
    axes[1, 1].set_xlabel("Date")
    axes[1, 1].set_ylabel("Value")
    axes[1, 1].set_title("Time Series")

    # Automatic date formatting
    axes[1, 1].xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter("%Y-%m"))
    fig.autofmt_xdate()

    fig.suptitle("Multi-Panel Figure Demonstration", fontsize=16)
    plt.tight_layout()

    scitex.io.save(fig, "multi_panel_demo.png")
    print("   ✅ Saved: multi_panel_demo.png AND .csv files")


def example_statistical_plot():
    """Statistical plotting with error bars and confidence intervals."""
    print("\n3. Statistical Plot with Error Bars")

    # Generate data with uncertainty
    n_groups = 5
    n_samples = 100

    groups = []
    means = []
    stds = []

    for i in range(n_groups):
        data = np.random.normal(50 + i * 10, 5 + i * 2, n_samples)
        groups.append(f"Group {i+1}")
        means.append(np.mean(data))
        stds.append(np.std(data))

    # Create figure
    fig, (ax1, ax2) = scitex.plt.subplots(1, 2, figsize=(12, 5))

    # Bar plot with error bars
    x_pos = np.arange(len(groups))
    ax1.bar(
        x_pos,
        means,
        yerr=stds,
        capsize=5,
        alpha=0.7,
        color="skyblue",
        edgecolor="navy",
        linewidth=2,
    )
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(groups)
    ax1.set_xlabel("Groups")
    ax1.set_ylabel("Mean ± SD")
    ax1.set_title("Group Comparison")

    # Line plot with confidence intervals
    x_line = np.linspace(0, 4, 100)
    y_mean = 50 + 10 * x_line + np.sin(x_line * 2) * 5
    y_std = 5 + x_line

    ax2.plot(x_line, y_mean, "b-", linewidth=2, label="Mean")
    ax2.fill_between(
        x_line,
        y_mean - 1.96 * y_std,
        y_mean + 1.96 * y_std,
        alpha=0.3,
        color="blue",
        label="95% CI",
    )
    ax2.set_xlabel("X values")
    ax2.set_ylabel("Y values")
    ax2.set_title("Confidence Interval Plot")
    ax2.legend()

    plt.tight_layout()
    scitex.io.save(fig, "statistical_comparison.png")
    print("   ✅ Saved: statistical_comparison.png with data")


def example_custom_styling():
    """Custom styling and color schemes."""
    print("\n4. Custom Styling Example")

    # Use scitex color utilities
    n_lines = 5
    colors = scitex.plt.color.get_colors_from_cmap("viridis", n_lines)

    fig, ax = scitex.plt.subplots(figsize=(10, 6))

    # Plot multiple lines with custom colors
    x = np.linspace(0, 10, 100)
    for i in range(n_lines):
        y = np.sin(x + i * np.pi / 4) * (i + 1)
        ax.plot(x, y, color=colors[i], linewidth=2.5, label=f"Phase shift: {i*45}°")

    # Custom styling
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Amplitude")
    ax.set_title("Phase-shifted Sine Waves")
    ax.legend(loc="upper right")
    ax.grid(True, alpha=0.3, linestyle="--")

    # Add shaded region
    ax.axvspan(2, 4, alpha=0.2, color="gray", label="Region of Interest")

    # Custom spine styling
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_linewidth(2)
    ax.spines["bottom"].set_linewidth(2)

    scitex.io.save(fig, "custom_styling.png")
    print("   ✅ Saved: custom_styling.png with styling data")


def example_data_export():
    """Demonstrate automatic data export feature."""
    print("\n5. Data Export Feature")

    # Generate data
    x = np.linspace(0, 5, 50)
    y1 = x**2
    y2 = x**2.5
    y3 = x**3

    # Plot
    fig, ax = scitex.plt.subplots(figsize=(8, 6))
    ax.plot(x, y1, "r-", label="x²", linewidth=2)
    ax.plot(x, y2, "g--", label="x^2.5", linewidth=2)
    ax.plot(x, y3, "b:", label="x³", linewidth=3)

    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_title("Power Functions")
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Save and demonstrate CSV export
    output_path = "power_functions.png"
    scitex.io.save(fig, output_path)
    print(f"   ✅ Saved: {output_path}")

    # Show that CSV was created automatically
    csv_path = os.path.join(CONFIG.SDIR, output_path + ".csv")
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        print(f"\n   📊 Exported data shape: {df.shape}")
        print(f"   📊 Columns: {list(df.columns)}")
        print(f"\n   First few rows of exported data:")
        print(df.head())


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    import scitex

    script_mode = scitex.gen.is_script()
    parser = argparse.ArgumentParser(
        description="Enhanced plotting examples with scitex.plt"
    )
    args = parser.parse_args()
    scitex.str.printc(args, c="yellow")
    return args


def run_main() -> None:
    """Initialize scitex framework, run main function, and cleanup."""
    global CONFIG, CC, sys, plt, np, pd, scitex, os

    import sys
    import os
    import numpy as np
    import pandas as pd
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

# EOF
