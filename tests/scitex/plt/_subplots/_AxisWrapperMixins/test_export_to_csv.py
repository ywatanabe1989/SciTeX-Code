#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-18 20:55:37 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/tests/scitex/plt/_subplots/_AxisWrapperMixins/test_export_to_csv.py
# ----------------------------------------
import os
__FILE__ = (
    "./tests/scitex/plt/_subplots/_AxisWrapperMixins/test_export_to_csv.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import matplotlib
import numpy as np
import pandas as pd
import pytest

import scitex
from scitex.plt import subplots  # Import from the public API

matplotlib.use("agg")

ACTUAL_SAVE_DIR = __file__.replace(".py", "_out")
os.makedirs(ACTUAL_SAVE_DIR, exist_ok=True)


def test_export_plot_kde_to_csv():
    """Test that plot_kde data is correctly formatted and exported to CSV."""
    # Figure
    fig, ax = subplots()
    # Data
    data = np.concatenate([np.random.normal(0, 1, 500), np.random.normal(5, 1, 300)])
    # Plot with ID for tracking
    ax.plot_kde(data, label="Test Distribution", id="kde_export_test")
    # Visualization
    ax.set_xyt("Value", "Density", "KDE Export Test")
    # Save as PNG and CSV
    spath = f"./kde_export_test.png"
    scitex.io.save(fig, spath, symlink_from_cwd=False)
    # Get the full path
    actual_spath = os.path.join(ACTUAL_SAVE_DIR, spath)
    # Get the CSV path
    csv_spath = actual_spath.replace(".png", ".csv")
    
    # Read the CSV file to verify its contents
    df = pd.read_csv(csv_spath)
    
    # Verify the columns exist with the expected IDs
    assert "kde_export_test_kde_x" in df.columns
    assert "kde_export_test_kde_density" in df.columns
    assert len(df) > 0
    
    # Clean up
    scitex.plt.close(fig)


def test_export_plot_line_to_csv():
    """Test that plot_line data is correctly formatted and exported to CSV."""
    # Figure
    fig, ax = subplots()
    # Data
    x = np.linspace(0, 10, 100)
    y = np.sin(x)
    # Plot with ID for tracking
    ax.plot_line(y, label="Sine Wave", id="line_export_test")
    # Visualization
    ax.set_xyt("X", "Y", "Line Export Test")
    # Save as PNG and CSV
    spath = f"./line_export_test.png"
    scitex.io.save(fig, spath, symlink_from_cwd=False)
    # Get the full path
    actual_spath = os.path.join(ACTUAL_SAVE_DIR, spath)
    # Get the CSV path
    csv_spath = actual_spath.replace(".png", ".csv")
    
    # Read the CSV file to verify its contents
    df = pd.read_csv(csv_spath)
    
    # Verify the columns exist with the expected IDs
    assert any(col.startswith("line_export_test_line_") for col in df.columns)
    assert len(df) > 0
    
    # Clean up
    scitex.plt.close(fig)


def test_export_plot_shaded_line_to_csv():
    """Test that plot_shaded_line data is correctly formatted and exported to CSV."""
    # Figure
    fig, ax = subplots()
    # Data
    x = np.linspace(0, 10, 100)
    y_middle = np.sin(x)
    y_lower = y_middle - 0.2
    y_upper = y_middle + 0.2
    # Plot with ID for tracking
    ax.plot_shaded_line(
        x, y_lower, y_middle, y_upper,
        label="Sine with error",
        id="shaded_line_export_test"
    )
    # Visualization
    ax.set_xyt("X", "Y", "Shaded Line Export Test")
    # Save as PNG and CSV
    spath = f"./shaded_line_export_test.png"
    scitex.io.save(fig, spath, symlink_from_cwd=False)
    # Get the full path
    actual_spath = os.path.join(ACTUAL_SAVE_DIR, spath)
    # Get the CSV path
    csv_spath = actual_spath.replace(".png", ".csv")
    
    # Read the CSV file to verify its contents
    df = pd.read_csv(csv_spath)
    
    # Verify the data is correct
    assert any(col.startswith("shaded_line_export_test") for col in df.columns)
    assert len(df) > 0
    
    # Clean up
    scitex.plt.close(fig)


def test_export_multiple_plots_to_csv():
    """Test that multiple plots on the same axis export correctly to CSV."""
    # Figure
    fig, ax = subplots()
    
    # Data for line
    x1 = np.linspace(0, 10, 100)
    y1 = np.sin(x1)
    
    # Data for KDE
    data = np.random.normal(0, 1, 500)
    
    # Create multiple plots with different IDs
    ax.plot_line(y1, label="Line", id="multi_test_line")
    ax.plot_kde(data, label="KDE", id="multi_test_kde")
    
    # Save as PNG and CSV
    spath = f"./multi_plot_export_test.png"
    scitex.io.save(fig, spath, symlink_from_cwd=False)
    
    # Get the full path
    actual_spath = os.path.join(ACTUAL_SAVE_DIR, spath)
    # Get the CSV path
    csv_spath = actual_spath.replace(".png", ".csv")
    
    # Read the CSV file to verify its contents
    df = pd.read_csv(csv_spath)
    
    # Verify both datasets are in the CSV
    assert any(col.startswith("multi_test_line") for col in df.columns)
    assert any(col.startswith("multi_test_kde") for col in df.columns)
    
    # Clean up
    scitex.plt.close(fig)


def test_track_parameter_controls_csv_export():
    """Test that the track parameter correctly controls CSV export."""
    # Figure with tracking
    fig1, ax1 = subplots()
    # Data
    data = np.random.normal(0, 1, 100)
    # Plot with tracking enabled (default)
    ax1.plot_kde(data, id="track_test_on")
    # Save
    spath1 = f"./track_test_on.png"
    scitex.io.save(fig1, spath1, symlink_from_cwd=False)
    csv_spath1 = os.path.join(ACTUAL_SAVE_DIR, spath1.replace(".png", ".csv"))
    
    # Figure without tracking
    fig2, ax2 = subplots()
    # Plot with tracking disabled
    ax2.plot_kde(data, id="track_test_off", track=False)
    # Save
    spath2 = f"./track_test_off.png"
    scitex.io.save(fig2, spath2, symlink_from_cwd=False)
    csv_spath2 = os.path.join(ACTUAL_SAVE_DIR, spath2.replace(".png", ".csv"))
    
    # Verify tracking status impacts CSV output
    assert os.path.exists(csv_spath1)  # With tracking, CSV should exist
    
    # No data should be recorded when track=False, so the CSV might exist but should be empty
    # or missing the plot data
    if os.path.exists(csv_spath2):
        df = pd.read_csv(csv_spath2)
        assert not any(col.startswith("track_test_off") for col in df.columns)
    
    # Clean up
    scitex.plt.close(fig1)
    scitex.plt.close(fig2)


if __name__ == "__main__":
    import os
    import pytest
    pytest.main([os.path.abspath(__file__)])