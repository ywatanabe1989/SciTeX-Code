#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-18 23:14:10 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/_subplots/_export_as_csv_formatters/verify_formatters.py
# ----------------------------------------
import os
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend

# Add src to path if needed
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../'))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

import scitex

# Create output directory
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'formatter_test_output')
os.makedirs(OUTPUT_DIR, exist_ok=True)

def test_all_formatters():
    """
    Test all formatters by creating actual plots and saving both image and CSV files.
    Each function will create a different type of plot, save it, and verify the CSV export.
    """
    # Test each formatter with a real plot
    test_plot_kde()
    test_plot_image()
    test_plot_shaded_line()
    test_plot_scatter_hist()
    test_plot_violin()
    test_plot_heatmap()
    test_plot_ecdf()
    test_multiple_plots()

def test_plot_kde():
    """Test KDE plotting and CSV export."""
    print("Testing plot_kde...")
    
    # Create figure
    fig, ax = scitex.plt.subplots()
    
    # Generate data
    np.random.seed(42)  # For reproducibility
    data = np.concatenate([np.random.normal(0, 1, 500), np.random.normal(5, 1, 300)])
    
    # Plot with ID for tracking
    ax.plot_kde(data, label="Bimodal Distribution", id="kde_test")
    
    # Style the plot
    ax.set_xyt("Value", "Density", "KDE Test")
    ax.legend()
    
    # Save both image and data
    save_path = os.path.join(OUTPUT_DIR, "kde_test.png")
    scitex.io.save(fig, save_path)
    
    # Verify CSV was created
    csv_path = save_path.replace(".png", ".csv")
    assert os.path.exists(csv_path), f"CSV file not created: {csv_path}"
    
    # Read CSV and verify contents
    df = pd.read_csv(csv_path)
    assert "kde_test_kde_x" in df.columns, "Expected column 'kde_test_kde_x' not found"
    assert "kde_test_kde_density" in df.columns, "Expected column 'kde_test_kde_density' not found"
    
    # Close figure
    scitex.plt.close(fig)
    print("✓ plot_kde test successful")

def test_plot_image():
    """Test image plotting and CSV export."""
    print("Testing plot_image...")
    
    # Create figure
    fig, ax = scitex.plt.subplots()
    
    # Generate data
    np.random.seed(42)  # For reproducibility
    data = np.random.rand(20, 20)
    
    # Plot with ID for tracking
    ax.plot_image(data, cmap="viridis", id="image_test")
    
    # Style the plot
    ax.set_xyt("X", "Y", "Image Test")
    
    # Save both image and data
    save_path = os.path.join(OUTPUT_DIR, "image_test.png")
    scitex.io.save(fig, save_path)
    
    # Verify CSV was created
    csv_path = save_path.replace(".png", ".csv")
    assert os.path.exists(csv_path), f"CSV file not created: {csv_path}"
    
    # Read CSV and verify contents
    df = pd.read_csv(csv_path)
    # The formatter should have converted the 2D array to a DataFrame
    assert not df.empty, "CSV file is empty"
    
    # Close figure
    scitex.plt.close(fig)
    print("✓ plot_image test successful")

def test_plot_shaded_line():
    """Test shaded line plotting and CSV export."""
    print("Testing plot_shaded_line...")
    
    # Create figure
    fig, ax = scitex.plt.subplots()
    
    # Generate data
    np.random.seed(42)  # For reproducibility
    x = np.linspace(0, 10, 100)
    y_middle = np.sin(x)
    y_lower = y_middle - 0.2
    y_upper = y_middle + 0.2
    
    # Plot with ID for tracking
    ax.plot_shaded_line(x, y_lower, y_middle, y_upper, label="Sine with error", id="shaded_line_test")
    
    # Style the plot
    ax.set_xyt("X", "Y", "Shaded Line Test")
    ax.legend()
    
    # Save both image and data
    save_path = os.path.join(OUTPUT_DIR, "shaded_line_test.png")
    scitex.io.save(fig, save_path)
    
    # Verify CSV was created
    csv_path = save_path.replace(".png", ".csv")
    assert os.path.exists(csv_path), f"CSV file not created: {csv_path}"
    
    # Read CSV and verify contents
    df = pd.read_csv(csv_path)
    assert not df.empty, "CSV file is empty"
    
    # Close figure
    scitex.plt.close(fig)
    print("✓ plot_shaded_line test successful")

def test_plot_scatter_hist():
    """Test scatter histogram plotting and CSV export."""
    print("Testing plot_scatter_hist...")
    
    # Create figure
    fig, ax = scitex.plt.subplots(figsize=(8, 8))
    
    # Generate data
    np.random.seed(42)  # For reproducibility
    x = np.random.normal(0, 1, 500)
    y = x + np.random.normal(0, 0.5, 500)
    
    # Plot with ID for tracking
    ax.plot_scatter_hist(x, y, hist_bins=30, scatter_alpha=0.7, id="scatter_hist_test")
    
    # Style the plot
    ax.set_xyt("X Values", "Y Values", "Scatter Histogram Test")
    
    # Save both image and data
    save_path = os.path.join(OUTPUT_DIR, "scatter_hist_test.png")
    scitex.io.save(fig, save_path)
    
    # Verify CSV was created
    csv_path = save_path.replace(".png", ".csv")
    assert os.path.exists(csv_path), f"CSV file not created: {csv_path}"
    
    # Read CSV and verify contents
    df = pd.read_csv(csv_path)
    assert not df.empty, "CSV file is empty"
    
    # Close figure
    scitex.plt.close(fig)
    print("✓ plot_scatter_hist test successful")

def test_plot_violin():
    """Test violin plotting and CSV export."""
    print("Testing plot_violin...")
    
    # Create figure
    fig, ax = scitex.plt.subplots()
    
    # Generate data
    np.random.seed(42)  # For reproducibility
    data = [
        np.random.normal(0, 1, 100),
        np.random.normal(2, 1.5, 100),
        np.random.normal(5, 0.8, 100),
    ]
    labels = ["Group A", "Group B", "Group C"]
    
    # Plot with ID for tracking
    ax.plot_violin(data, labels=labels, colors=["red", "blue", "green"], id="violin_test")
    
    # Style the plot
    ax.set_xyt("Groups", "Values", "Violin Plot Test")
    
    # Save both image and data
    save_path = os.path.join(OUTPUT_DIR, "violin_test.png")
    scitex.io.save(fig, save_path)
    
    # Verify CSV was created
    csv_path = save_path.replace(".png", ".csv")
    assert os.path.exists(csv_path), f"CSV file not created: {csv_path}"
    
    # Read CSV and verify contents
    df = pd.read_csv(csv_path)
    assert not df.empty, "CSV file is empty"
    
    # Close figure
    scitex.plt.close(fig)
    print("✓ plot_violin test successful")

def test_plot_heatmap():
    """Test heatmap plotting and CSV export."""
    print("Testing plot_heatmap...")
    
    # Create figure
    fig, ax = scitex.plt.subplots()
    
    # Generate data
    np.random.seed(42)  # For reproducibility
    data = np.random.rand(5, 10)
    x_labels = [f"X{ii+1}" for ii in range(5)]
    y_labels = [f"Y{ii+1}" for ii in range(10)]
    
    # Plot with ID for tracking
    ax.plot_heatmap(
        data,
        x_labels=x_labels,
        y_labels=y_labels,
        cbar_label="Values",
        show_annot=True,
        value_format="{x:.2f}",
        cmap="viridis",
        id="heatmap_test",
    )
    
    # Style the plot
    ax.set_title("Heatmap Test")
    
    # Save both image and data
    save_path = os.path.join(OUTPUT_DIR, "heatmap_test.png")
    scitex.io.save(fig, save_path)
    
    # Verify CSV was created
    csv_path = save_path.replace(".png", ".csv")
    assert os.path.exists(csv_path), f"CSV file not created: {csv_path}"
    
    # Read CSV and verify contents
    df = pd.read_csv(csv_path)
    assert not df.empty, "CSV file is empty"
    
    # Close figure
    scitex.plt.close(fig)
    print("✓ plot_heatmap test successful")

def test_plot_ecdf():
    """Test ECDF plotting and CSV export."""
    print("Testing plot_ecdf...")
    
    # Create figure
    fig, ax = scitex.plt.subplots()
    
    # Generate data
    np.random.seed(42)  # For reproducibility
    data = np.random.normal(0, 1, 1000)
    
    # Plot with ID for tracking
    ax.plot_ecdf(data, label="Normal Distribution", id="ecdf_test")
    
    # Style the plot
    ax.set_xyt("Value", "Cumulative Probability", "ECDF Test")
    ax.legend()
    
    # Save both image and data
    save_path = os.path.join(OUTPUT_DIR, "ecdf_test.png")
    scitex.io.save(fig, save_path)
    
    # Verify CSV was created
    csv_path = save_path.replace(".png", ".csv")
    assert os.path.exists(csv_path), f"CSV file not created: {csv_path}"
    
    # Read CSV and verify contents
    df = pd.read_csv(csv_path)
    assert not df.empty, "CSV file is empty"
    
    # Close figure
    scitex.plt.close(fig)
    print("✓ plot_ecdf test successful")

def test_multiple_plots():
    """Test multiple plots on the same axis."""
    print("Testing multiple plots on the same axis...")
    
    # Create figure
    fig, ax = scitex.plt.subplots()
    
    # Generate data
    np.random.seed(42)  # For reproducibility
    x = np.linspace(0, 10, 100)
    y1 = np.sin(x)
    y2 = np.cos(x)
    
    # Create multiple plots with different IDs
    ax.plot_line(y1, label="Sine", id="multi_test_sine")
    ax.plot_line(y2, label="Cosine", id="multi_test_cosine")
    
    # Style the plot
    ax.set_xyt("X", "Y", "Multiple Plots Test")
    ax.legend()
    
    # Save both image and data
    save_path = os.path.join(OUTPUT_DIR, "multiple_plots_test.png")
    scitex.io.save(fig, save_path)
    
    # Verify CSV was created
    csv_path = save_path.replace(".png", ".csv")
    assert os.path.exists(csv_path), f"CSV file not created: {csv_path}"
    
    # Read CSV and verify contents
    df = pd.read_csv(csv_path)
    assert not df.empty, "CSV file is empty"
    
    # Check that both plots are in the CSV
    sine_cols = [col for col in df.columns if col.startswith("multi_test_sine")]
    cosine_cols = [col for col in df.columns if col.startswith("multi_test_cosine")]
    assert len(sine_cols) > 0, "Sine plot data not found in CSV"
    assert len(cosine_cols) > 0, "Cosine plot data not found in CSV"
    
    # Close figure
    scitex.plt.close(fig)
    print("✓ Multiple plots test successful")

if __name__ == "__main__":
    print("Starting formatter verification tests...")
    test_all_formatters()
    print("\nAll formatter tests completed successfully!")
    print(f"Output files are in: {OUTPUT_DIR}")