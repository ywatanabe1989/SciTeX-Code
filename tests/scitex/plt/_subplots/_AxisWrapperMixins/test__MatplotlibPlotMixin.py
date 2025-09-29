#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-18 16:32:43 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/tests/scitex/plt/_subplots/_AxisWrapperMixins/test__MatplotlibPlotMixin.py
# ----------------------------------------
import os

__FILE__ = "./tests/scitex/plt/_subplots/_AxisWrapperMixins/test__MatplotlibPlotMixin.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import matplotlib
import scitex
import numpy as np
from scitex.plt import subplots  # Import from the public API

matplotlib.use("agg")

ACTUAL_SAVE_DIR = __file__.replace(".py", "_out")
os.makedirs(ACTUAL_SAVE_DIR, exist_ok=True)


def test_plot_image():
    """Test plot_image function"""
    # Figure
    fig, ax = subplots()
    # Data
    data = np.random.randn(20, 20)
    # Plot - add ID for tracking
    ax.plot_image(
        data, cmap="viridis", interpolation="nearest", id="image_test"
    )
    # Visualization
    ax.set_xyt("X", "Y", "Plot_Image Test")
    # Saving
    spath = f"./plot_image_test.png"
    scitex.io.save(fig, spath, symlink_from_cwd=False)
    # Closing
    scitex.plt.close(fig)
    # Assertion for PNG
    actual_spath = os.path.join(ACTUAL_SAVE_DIR, spath)
    assert os.path.exists(actual_spath), f"Failed to save figure to {spath}"
    # Assertion for CSV
    csv_spath = actual_spath.replace(".png", ".csv")
    assert os.path.exists(csv_spath), f"Failed to save CSV data to {csv_spath}"


def test_plot_image_xyz():
    """Test plot_image with xyz=True"""
    # Figure
    fig, ax = subplots()
    # Data
    data = np.random.randn(20, 20)
    # Plot - add ID for tracking
    ax.plot_image(data, xyz=True, cmap="plasma", id="image_xyz_test")
    # Visualization
    ax.set_xyt("X", "Y", "Plot_Image with XYZ Test")
    # Saving
    spath = f"./plot_image_xyz_test.png"
    scitex.io.save(fig, spath, symlink_from_cwd=False)
    # Closing
    scitex.plt.close(fig)
    # Assertion for PNG
    actual_spath = os.path.join(ACTUAL_SAVE_DIR, spath)
    assert os.path.exists(actual_spath), f"Failed to save figure to {spath}"
    # Assertion for CSV
    csv_spath = actual_spath.replace(".png", ".csv")
    assert os.path.exists(csv_spath), f"Failed to save CSV data to {csv_spath}"


def test_plot_kde():
    """Test plot_kde function"""
    # Figure
    fig, ax = subplots()
    # Data
    data = np.concatenate([np.random.normal(0, 1, 500), np.random.normal(5, 1, 300)])
    # Plot
    ax.plot_kde(data, label="Bimodal Distribution", fill=True)
    # Visualization
    ax.set_xyt("Value", "Density", "PLOT_KDE Test")
    ax.legend()
    # Saving
    spath = f"./plot_kde_test.png"
    scitex.io.save(fig, spath, symlink_from_cwd=False)
    # Closing
    scitex.plt.close(fig)
    # Assertion for PNG
    actual_spath = os.path.join(ACTUAL_SAVE_DIR, spath)
    assert os.path.exists(actual_spath), f"Failed to save figure to {spath}"
    # Assertion for CSV
    csv_spath = actual_spath.replace(".png", ".csv")
    assert os.path.exists(csv_spath), f"Failed to save CSV data to {csv_spath}"


def test_plot_kde_cumulative():
    """Test plot_kde function with cumulative=True"""
    # Figure
    fig, ax = subplots()
    # Data
    data = np.random.normal(0, 1, 1000)
    # Plot - add ID for tracking
    ax.plot_kde(
        data,
        label="Normal Distribution",
        cumulative=True,
        id="kde_cumulative_test",
    )
    # Visualization
    ax.set_xyt("Value", "Cumulative Density", "Cumulative PLOT_KDE Test")
    ax.legend()
    # Saving
    spath = f"./plot_kde_cumulative_test.png"
    scitex.io.save(fig, spath, symlink_from_cwd=False)
    # Closing
    scitex.plt.close(fig)
    # Assertion for PNG
    actual_spath = os.path.join(ACTUAL_SAVE_DIR, spath)
    assert os.path.exists(actual_spath), f"Failed to save figure to {spath}"
    # Assertion for CSV
    csv_spath = actual_spath.replace(".png", ".csv")
    assert os.path.exists(csv_spath), f"Failed to save CSV data to {csv_spath}"


def test_plot_conf_mat():
    """Test plot_conf_mat function"""
    # Figure
    fig, ax = subplots()
    # Data
    cm = np.array([[85, 10, 5], [15, 70, 15], [10, 20, 70]])
    class_labels = ["Class A", "Class B", "Class C"]
    # Plot - add ID for tracking
    ax.plot_conf_mat(
        cm,
        x_labels=class_labels,
        y_labels=class_labels,
        title="Confusion Matrix Test",
        calc_bacc=True,
        id="conf_mat_test",
    )
    # Saving
    spath = f"./plot_conf_mat_test.png"
    scitex.io.save(fig, spath, symlink_from_cwd=False)
    # Closing
    scitex.plt.close(fig)
    # Assertion for PNG
    actual_spath = os.path.join(ACTUAL_SAVE_DIR, spath)
    assert os.path.exists(actual_spath), f"Failed to save figure to {spath}"
    # Assertion for CSV
    csv_spath = actual_spath.replace(".png", ".csv")
    assert os.path.exists(csv_spath), f"Failed to save CSV data to {csv_spath}"


def test_plot_rectangle():
    """Test plot_rectangle function"""
    # Figure
    fig, ax = subplots()
    # Data
    x = np.linspace(0, 10, 100)
    # Add rectangles
    ax.plot_rectangle(2, 0, 2, 0.5, color="red", alpha=0.3, label="Highlight Region 1")
    ax.plot_rectangle(
        6,
        -0.5,
        2,
        0.5,
        color="blue",
        alpha=0.3,
        label="Highlight Region 2",
        id="rectangle_2_test",
    )
    # Visualization
    ax.set_xyt("X axis", "Y axis", "Plot_Rectangle Test")
    ax.legend()
    # Saving
    spath = f"./plot_rectangle_test.png"
    scitex.io.save(fig, spath, symlink_from_cwd=False)
    # Closing
    scitex.plt.close(fig)
    # Assertion for PNG
    actual_spath = os.path.join(ACTUAL_SAVE_DIR, spath)
    assert os.path.exists(actual_spath), f"Failed to save figure to {spath}"
    # Assertion for CSV
    csv_spath = actual_spath.replace(".png", ".csv")
    assert os.path.exists(csv_spath), f"Failed to save CSV data to {csv_spath}"


def test_plot_fillv():
    """Test plot_fillv function"""
    # Figure
    fig, ax = subplots()
    # Data
    x = np.linspace(0, 10, 100)
    y = np.sin(x)
    # Add vertical shaded regions - add ID for tracking
    ax.plot_fillv([2, 6], [4, 8], color="green", alpha=0.3, id="fillv_test")
    # Visualization
    ax.set_xyt("X axis", "Y axis", "Plot_Fillv Test")
    # Saving
    spath = f"./plot_fillv_test.png"
    scitex.io.save(fig, spath, symlink_from_cwd=False)
    # Closing
    scitex.plt.close(fig)
    # Assertion for PNG
    actual_spath = os.path.join(ACTUAL_SAVE_DIR, spath)
    assert os.path.exists(actual_spath), f"Failed to save figure to {spath}"
    # Assertion for CSV
    csv_spath = actual_spath.replace(".png", ".csv")
    assert os.path.exists(csv_spath), f"Failed to save CSV data to {csv_spath}"


def test_plot_box():
    """Test plot_box function"""
    # Figure
    fig, ax = subplots()
    # Data
    data = [
        np.random.normal(0, 1, 100),
        np.random.normal(2, 1.5, 100),
        np.random.normal(5, 0.8, 100),
    ]
    # Plot - add ID for tracking
    ax.plot_box(data, labels=["Group A", "Group B", "Group C"], id="box_test")
    # Visualization
    ax.set_xyt("Groups", "Values", "Plot_Box Test")
    # Saving
    spath = f"./plot_boxtest.png"
    scitex.io.save(fig, spath, symlink_from_cwd=False)
    # Closing
    scitex.plt.close(fig)
    # Assertion for PNG
    actual_spath = os.path.join(ACTUAL_SAVE_DIR, spath)
    assert os.path.exists(actual_spath), f"Failed to save figure to {spath}"
    # Assertion for CSV
    csv_spath = actual_spath.replace(".png", ".csv")
    assert os.path.exists(csv_spath), f"Failed to save CSV data to {csv_spath}"


def test_plot_raster():
    """Test plot_raster function"""
    # Figure
    fig, ax = subplots()
    # Data - sample spike train data
    n_neurons = 5
    t_max = 100
    np.random.seed(42)  # For reproducibility
    positions = [
        np.sort(np.random.uniform(0, t_max, np.random.randint(20, 50)))
        for _ in range(n_neurons)
    ]
    labels = [f"Neuron {ii+1}" for ii in range(n_neurons)]
    # Plot - add ID for tracking
    ax.plot_raster(positions, labels=labels, id="raster_test")
    # Visualization
    ax.set_xyt("Time (ms)", "Neuron", "Plot_Raster Plot Test")
    # Saving
    spath = f"./plot_raster_test.png"
    scitex.io.save(fig, spath, symlink_from_cwd=False)
    # Closing
    scitex.plt.close(fig)
    # Assertion for PNG
    actual_spath = os.path.join(ACTUAL_SAVE_DIR, spath)
    assert os.path.exists(actual_spath), f"Failed to save figure to {spath}"
    # Assertion for CSV
    csv_spath = actual_spath.replace(".png", ".csv")
    assert os.path.exists(csv_spath), f"Failed to save CSV data to {csv_spath}"


def test_plot_ecdf():
    """Test plot_ecdf function"""
    # Figure
    fig, ax = subplots()
    # Data
    data = np.random.normal(0, 1, 1000)
    # Plot
    ax.plot_ecdf(
        data, label="Normal Distribution PLOT_ECDF", id="plot_ecdf_id"
    )
    # Visualization
    ax.set_xyt("Value", "Cumulative Probability", "PLOT_ECDF Test")
    ax.legend()
    # Saving
    spath = f"./plot_ecdf_test.png"
    scitex.io.save(fig, spath, symlink_from_cwd=False)
    # Closing
    scitex.plt.close(fig)
    # Assertion for PNG
    actual_spath = os.path.join(ACTUAL_SAVE_DIR, spath)
    assert os.path.exists(actual_spath), f"Failed to save figure to {spath}"
    # Assertion for CSV
    csv_spath = actual_spath.replace(".png", ".csv")
    assert os.path.exists(csv_spath), f"Failed to save CSV data to {csv_spath}"


def test_plot_joyplot():
    """Test plot_joyplot function"""
    # Figure
    fig, ax = subplots()
    # Data for multiple distributions
    data = {
        "Group A": np.random.normal(0, 1, 500),
        "Group B": np.random.normal(2, 1.5, 500),
        "Group C": np.random.normal(5, 0.8, 500),
        "Group D": np.random.normal(8, 2, 500),
    }
    # Plot
    ax.plot_joyplot(data, id="plot_joyplot_id")
    # Visualization
    ax.set_xyt("Value", "", "Plot_Joyplot Test")
    # Saving
    spath = f"./plot_joyplot_test.png"
    scitex.io.save(fig, spath, symlink_from_cwd=False)
    # Closing
    scitex.plt.close(fig)
    # Assertion for PNG
    actual_spath = os.path.join(ACTUAL_SAVE_DIR, spath)
    assert os.path.exists(actual_spath), f"Failed to save figure to {spath}"
    # Assertion for CSV
    csv_spath = actual_spath.replace(".png", ".csv")
    assert os.path.exists(csv_spath), f"Failed to save CSV data to {csv_spath}"


def test_plot_line():
    """Test plot_line function"""
    # Figure
    fig, ax = subplots()

    # Data
    x = np.linspace(0, 10, 100)
    y = np.sin(x)

    # Plot
    ax.plot_line(y, label="Sine Wave", id="plot_line_id")

    # Visualization
    ax.set_xyt("X", "Y", "Plot_Line Test")
    ax.legend()

    # Saving
    spath = f"./plot_line_test.png"
    scitex.io.save(fig, spath, symlink_from_cwd=False)

    # Closing
    scitex.plt.close(fig)

    # Assertion for PNG
    actual_spath = os.path.join(ACTUAL_SAVE_DIR, spath)
    assert os.path.exists(actual_spath), f"Failed to save figure to {spath}"
    # Assertion for CSV
    csv_spath = actual_spath.replace(".png", ".csv")
    assert os.path.exists(csv_spath), f"Failed to save CSV data to {csv_spath}"


def test_plot_scatter_hist():
    """Test plot_scatter_hist function"""
    # Figure
    fig, ax = scitex.plt.subplots(figsize=(8, 8))

    # Data
    x = np.random.normal(0, 1, 500)
    y = x + np.random.normal(0, 0.5, 500)

    # Plot
    ax.plot_scatter_hist(
        x, y, hist_bins=30, scatter_alpha=0.7, id="plot_scatter_hist_id"
    )

    # Visualization
    ax.set_xyt("X Values", "Y Values", "Plot_Scatter_Hist Test")

    # Saving
    spath = f"./plot_scatter_hist_test.png"
    scitex.io.save(fig, spath, symlink_from_cwd=False)

    # Closing
    scitex.plt.close(fig)

    # Assertion for PNG
    actual_spath = os.path.join(ACTUAL_SAVE_DIR, spath)
    assert os.path.exists(actual_spath), f"Failed to save figure to {spath}"
    # Assertion for CSV
    csv_spath = actual_spath.replace(".png", ".csv")
    assert os.path.exists(csv_spath), f"Failed to save CSV data to {csv_spath}"


def test_plot_heatmap():
    """Test plot_heatmap function"""
    # Figure
    fig, ax = subplots()

    # Data
    data = np.random.rand(5, 10)
    x_labels = [f"X{ii+1}" for ii in range(5)]
    y_labels = [f"Y{ii+1}" for ii in range(10)]

    # Plot
    ax.plot_heatmap(
        data,
        x_labels=x_labels,
        y_labels=y_labels,
        cbar_label="Values",
        show_annot=True,
        value_format="{x:.2f}",
        cmap="viridis",
        annot_color_lighter="white",
        annot_color_darker="dimgray",
        id="plot_heatmap_id",
    )

    # Visualization
    ax.set_title("Plot_Heatmap Test")

    # Saving
    spath = f"./plot_heatmap_test.png"
    scitex.io.save(fig, spath, symlink_from_cwd=False)

    # Closing
    scitex.plt.close(fig)

    # Assertion for PNG
    actual_spath = os.path.join(ACTUAL_SAVE_DIR, spath)
    assert os.path.exists(actual_spath), f"Failed to save figure to {spath}"
    # Assertion for CSV
    csv_spath = actual_spath.replace(".png", ".csv")
    assert os.path.exists(csv_spath), f"Failed to save CSV data to {csv_spath}"


def test_plot_violin():
    """Test plot_violin function"""
    # Figure
    fig, ax = subplots()

    # Test with list data
    data_list = [
        np.random.normal(0, 1, 100),
        np.random.normal(2, 1.5, 100),
        np.random.normal(5, 0.8, 100),
    ]
    labels = ["Group A", "Group B", "Group C"]

    # Plot traditional violin
    ax.plot_violin(data_list, labels=labels, colors=["red", "blue", "green"], half=True)

    # Visualization
    ax.set_xyt("Groups", "Values", "Plot_Violin Test (Traditional)")

    # Saving
    spath = "./plot_violin_test_traditional.png"
    scitex.io.save(fig, spath, symlink_from_cwd=False)

    # Closing
    scitex.plt.close(fig)

    # Assertion for PNG
    actual_spath = os.path.join(ACTUAL_SAVE_DIR, spath)
    assert os.path.exists(actual_spath), f"Failed to save figure to {spath}"
    # Assertion for CSV
    csv_spath = actual_spath.replace(".png", ".csv")
    assert os.path.exists(csv_spath), f"Failed to save CSV data to {csv_spath}"


def test_plot_mean_std():
    """Test plot_mean_std function"""
    # Figure
    fig, ax = subplots()

    # Data
    np.random.seed(42)
    data = np.random.normal(0, 1, (20, 100))  # 20 samples, 100 time points

    # Plot
    ax.plot_mean_std(data, label="Mean±SD", sd=1, id="plot_mean_std_id")

    # Visualization
    ax.set_xyt("Time", "Value", "Plot_Mean_Std Test")
    ax.legend()

    # Saving
    spath = f"./plot_mean_std_test.png"
    scitex.io.save(fig, spath, symlink_from_cwd=False)

    # Closing
    scitex.plt.close(fig)

    # Assertion for PNG
    actual_spath = os.path.join(ACTUAL_SAVE_DIR, spath)
    assert os.path.exists(actual_spath), f"Failed to save figure to {spath}"
    # Assertion for CSV
    csv_spath = actual_spath.replace(".png", ".csv")
    assert os.path.exists(csv_spath), f"Failed to save CSV data to {csv_spath}"


def test_plot_mean_ci():
    """Test plot_mean_ci function"""
    # Figure
    fig, ax = subplots()

    # Data
    np.random.seed(42)
    data = np.random.normal(0, 1, (20, 100))  # 20 samples, 100 time points

    # Plot
    ax.plot_mean_ci(data, label="Mean with CI", perc=95, id="plot_mean_ci_id")

    # Visualization
    ax.set_xyt("Time", "Value", "Plot_Mean_CI Test")
    ax.legend()

    # Saving
    spath = f"./plot_mean_ci_test.png"
    scitex.io.save(fig, spath, symlink_from_cwd=False)

    # Closing
    scitex.plt.close(fig)

    # Assertion for PNG
    actual_spath = os.path.join(ACTUAL_SAVE_DIR, spath)
    assert os.path.exists(actual_spath), f"Failed to save figure to {spath}"
    # Assertion for CSV
    csv_spath = actual_spath.replace(".png", ".csv")
    assert os.path.exists(csv_spath), f"Failed to save CSV data to {csv_spath}"


def test_plot_median_iqr():
    """Test plot_median_iqr function"""
    # Figure
    fig, ax = subplots()

    # Data
    np.random.seed(42)
    data = np.random.normal(0, 1, (20, 100))  # 20 samples, 100 time points

    # Plot
    ax.plot_median_iqr(data, label="Median with IQR", id="plot_median_iqr_id")

    # Visualization
    ax.set_xyt("Time", "Value", "Plot_Median_IQR Test")
    ax.legend()

    # Saving
    spath = f"./plot_median_iqr_test.png"
    scitex.io.save(fig, spath, symlink_from_cwd=False)

    # Closing
    scitex.plt.close(fig)

    # Assertion for PNG
    actual_spath = os.path.join(ACTUAL_SAVE_DIR, spath)
    assert os.path.exists(actual_spath), f"Failed to save figure to {spath}"
    # Assertion for CSV
    csv_spath = actual_spath.replace(".png", ".csv")
    assert os.path.exists(csv_spath), f"Failed to save CSV data to {csv_spath}"


def test_plot_shaded_line():
    """Test plot_shaded_line function"""
    # Figure
    fig, ax = subplots()

    # Data
    x = np.linspace(0, 10, 100)
    y_middle = np.sin(x)
    y_lower = y_middle - 0.2
    y_upper = y_middle + 0.2

    # Plot
    ax.plot_shaded_line(
        x,
        y_lower,
        y_middle,
        y_upper,
        label="Sine with error",
        id="plot_shaded_line_id",
    )

    # Visualization
    ax.set_xyt("X", "Y", "Plot_Shaded_Line Test")
    ax.legend()

    # Saving
    spath = f"./plot_shaded_line_test.png"
    scitex.io.save(fig, spath, symlink_from_cwd=False)

    # Closing
    scitex.plt.close(fig)

    # Assertion for PNG
    actual_spath = os.path.join(ACTUAL_SAVE_DIR, spath)
    assert os.path.exists(actual_spath), f"Failed to save figure to {spath}"
    # Assertion for CSV
    csv_spath = actual_spath.replace(".png", ".csv")
    assert os.path.exists(csv_spath), f"Failed to save CSV data to {csv_spath}"


# def test_plot_area():
#     """Test plot_area function"""
#     # Figure
#     fig, ax = scitex.plt.subplots()

#     # Data
#     x = np.linspace(0, 10, 100)
#     y = np.array([np.sin(x), np.cos(x), np.sin(x + np.pi / 4)]).T

#     # Plot
#     ax.plot_area(x, y, stacked=True, alpha=0.7)

#     # Visualization
#     ax.set_xyt("X Values", "Y Values", "Plot_Area Test")

#     # Saving
#     spath = f"./plot_area_test.png"
#     scitex.io.save(fig, spath, symlink_from_cwd=False)

#     # Closing
#     scitex.plt.close(fig)

#     # Assertion
#     actual_spath = os.path.join(ACTUAL_SAVE_DIR, spath)
#     assert os.path.exists(actual_spath), f"Failed to save figure to {spath}"


# def test_plot_radar():
#     """Test plot_radar function"""
#     # Figure
#     fig, ax = scitex.plt.subplots(figsize=(8, 8))

#     # Data
#     categories = ["Speed", "Power", "Agility", "Endurance", "Technique"]
#     data = np.array(
#         [
#             [4.5, 3.5, 4.8, 5.0, 3.8],  # Player 1
#             [4.0, 5.0, 3.5, 3.0, 4.5],  # Player 2
#             [3.5, 4.0, 4.0, 4.5, 5.0],  # Player 3
#         ]
#     )
#     groups = ["Player 1", "Player 2", "Player 3"]

#     # Plot
#     ax.plot_radar(
#         data, categories=categories, groups=groups, fill=True, alpha=0.3
#     )

#     # Visualization
#     ax.set_title("Plot_Radar Test")

#     # Saving
#     spath = f"./plot_radar_test.png"
#     scitex.io.save(fig, spath, symlink_from_cwd=False)

#     # Closing
#     scitex.plt.close(fig)

#     # Assertion
#     actual_spath = os.path.join(ACTUAL_SAVE_DIR, spath)
#     assert os.path.exists(actual_spath), f"Failed to save figure to {spath}"


# def test_plot_bubble():
#     """Test plot_bubble function"""
#     # Figure
#     fig, ax = scitex.plt.subplots()

#     # Data
#     x = np.random.rand(30)
#     y = np.random.rand(30)
#     size = np.random.rand(30) * 100 + 10
#     color = np.random.rand(30)

#     # Plot
#     ax.plot_bubble(x, y, size, color=color, alpha=0.7, colormap="viridis")

#     # Visualization
#     ax.set_xyt("X Values", "Y Values", "Plot_Bubble Test")

#     # Saving
#     spath = f"./plot_bubble_test.png"
#     scitex.io.save(fig, spath, symlink_from_cwd=False)

#     # Closing
#     scitex.plt.close(fig)

#     # Assertion
#     actual_spath = os.path.join(ACTUAL_SAVE_DIR, spath)
#     assert os.path.exists(actual_spath), f"Failed to save figure to {spath}"


# def test_plot_ridgeline():
#     """Test plot_ridgeline function"""
#     # Figure
#     fig, ax = scitex.plt.subplots(figsize=(8, 8))

#     # Data
#     data = [
#         np.random.normal(0, 1, 500),
#         np.random.normal(2, 1.5, 500),
#         np.random.normal(5, 0.8, 500),
#         np.random.normal(8, 2, 500),
#     ]
#     labels = [
#         "Distribution A",
#         "Distribution B",
#         "Distribution C",
#         "Distribution D",
#     ]

#     # Plot
#     ax.plot_ridgeline(data, labels=labels, fill=True, alpha=0.7)

#     # Visualization
#     ax.set_xyt("Value", "", "Plot_Ridgeline Test")

#     # Saving
#     spath = f"./plot_ridgeline_test.png"
#     scitex.io.save(fig, spath, symlink_from_cwd=False)

#     # Closing
#     scitex.plt.close(fig)

#     # Assertion
#     actual_spath = os.path.join(ACTUAL_SAVE_DIR, spath)
#     assert os.path.exists(actual_spath), f"Failed to save figure to {spath}"


# def test_plot_parallel_coordinates():
#     """Test plot_parallel_coordinates function"""
#     # Figure
#     fig, ax = scitex.plt.subplots(figsize=(10, 6))

#     # Data
#     np.random.seed(42)
#     df = pd.DataFrame(
#         {
#             "feature1": np.random.rand(30),
#             "feature2": np.random.rand(30),
#             "feature3": np.random.rand(30),
#             "feature4": np.random.rand(30),
#             "class": np.random.randint(0, 3, 30),
#         }
#     )

#     # Plot
#     ax.plot_parallel_coordinates(df, class_column="class")

#     # Visualization
#     ax.set_title("Plot_Parallel_Coordinates Test")

#     # Saving
#     spath = f"./plot_parallel_coordinates_test.png"
#     scitex.io.save(fig, spath, symlink_from_cwd=False)

#     # Closing
#     scitex.plt.close(fig)

#     # Assertion
#     actual_spath = os.path.join(ACTUAL_SAVE_DIR, spath)
#     assert os.path.exists(actual_spath), f"Failed to save figure to {spath}"

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/plt/_subplots/_AxisWrapperMixins/_MatplotlibPlotMixin.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-05-18 17:51:44 (ywatanabe)"
# # File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/plt/_subplots/_AxisWrapperMixins/_MatplotlibPlotMixin.py
# # ----------------------------------------
# import os
# 
# __FILE__ = "./src/scitex/plt/_subplots/_AxisWrapperMixins/_MatplotlibPlotMixin.py"
# __DIR__ = os.path.dirname(__FILE__)
# # ----------------------------------------
# 
# from functools import wraps
# from typing import Any, Dict, List, Optional, Tuple, Union
# 
# import matplotlib
# import numpy as np
# import pandas as pd
# from scipy.stats import gaussian_kde
# 
# from ....pd import to_xyz
# from ....types import ArrayLike
# 
# 
# class MatplotlibPlotMixin:
#     """Mixin class for basic plotting operations."""
#     
#     def _get_ax_module(self):
#         """Lazy import ax module to avoid circular imports."""
#         from ....plt import ax as ax_module
#         return ax_module
# 
#     def plot_image(
#         self,
#         arr_2d: ArrayLike,
#         track: bool = True,
#         id: Optional[str] = None,
#         **kwargs,
#     ) -> None:
#         # Method Name for downstream csv exporting
#         method_name = "plot_image"
# 
#         # Plotting with pure matplotlib methods under non-tracking context
#         with self._no_tracking():
#             self._axis_mpl = self._get_ax_module().plot_image(self._axis_mpl, arr_2d, **kwargs)
# 
#         # Tracking
#         tracked_dict = {"image_df": pd.DataFrame(arr_2d)}
#         if kwargs.get("xyz", False):
#             tracked_dict["image_df"] = to_xyz(tracked_dict["image_df"])
#         self._track(
#             track,
#             id,
#             method_name,
#             tracked_dict,
#             None,
#         )
# 
#         return self._axis_mpl
# 
#     def plot_kde(
#         self,
#         data: ArrayLike,
#         cumulative=False,
#         fill=False,
#         track: bool = True,
#         id: Optional[str] = None,
#         **kwargs,
#     ) -> None:
#         # Method Name for downstream csv exporting
#         method_name = "plot_kde"
# 
#         # Sample count as label
#         n_samples = (~np.isnan(data)).sum()
#         if kwargs.get("label"):
#             kwargs["label"] = f"{kwargs['label']} (n={n_samples})"
# 
#         # Xlim (kwargs["xlim"] is not accepted in downstream plotters)
#         xlim = kwargs.get("xlim")
#         if not xlim:
#             xlim = (np.nanmin(data), np.nanmax(data))
# 
#         # X
#         xx = np.linspace(xlim[0], xlim[1], int(1e3))
# 
#         # Y
#         density = gaussian_kde(data)(xx)
#         density /= density.sum()
# 
#         # Cumulative
#         if cumulative:
#             density = np.cumsum(density)
# 
#         # Plotting with pure matplotlib methods under non-tracking context
#         with self._no_tracking():
#             # Filled Line
#             if fill:
#                 self._axis_mpl.fill_between(
#                     xx,
#                     density,
#                 )
#             # Simple Line
#             else:
#                 self._axis_mpl.plot(xx, density)
# 
#         # Tracking
#         tracked_dict = {
#             "x": xx,
#             "kde": density,
#             "n": n_samples,
#         }
#         self._track(
#             track,
#             id,
#             method_name,
#             tracked_dict,
#             None,
#         )
# 
#         return self._axis_mpl
# 
#     def plot_conf_mat(
#         self,
#         data: ArrayLike,
#         x_labels: Optional[List[str]] = None,
#         y_labels: Optional[List[str]] = None,
#         title: str = "Confusion Matrix",
#         cmap: str = "Blues",
#         cbar: bool = True,
#         cbar_kw: Dict[str, Any] = {},
#         label_rotation_xy: Tuple[float, float] = (15, 15),
#         x_extend_ratio: float = 1.0,
#         y_extend_ratio: float = 1.0,
#         calc_bacc: bool = False,
#         track: bool = True,
#         id: Optional[str] = None,
#         **kwargs,
#     ) -> None:
#         # Method Name for downstream csv exporting
#         method_name = "plot_conf_mat"
# 
#         # Plotting with pure matplotlib methods under non-tracking context
#         with self._no_tracking():
#             self._axis_mpl, bacc_val = self._get_ax_module().plot_conf_mat(
#                 self._axis_mpl,
#                 data,
#                 x_labels=x_labels,
#                 y_labels=y_labels,
#                 title=title,
#                 cmap=cmap,
#                 cbar=cbar,
#                 cbar_kw=cbar_kw,
#                 label_rotation_xy=label_rotation_xy,
#                 x_extend_ratio=x_extend_ratio,
#                 y_extend_ratio=y_extend_ratio,
#                 calc_bacc=calc_bacc,
#                 **kwargs,
#             )
# 
#         tracked_dict = {"balanced_accuracy": bacc_val}
#         # Tracking
#         self._track(track, id, method_name, tracked_dict, None)
# 
#         return self._axis_mpl, bacc_val
# 
#     # @wraps removed to avoid circular import
#     def plot_rectangle(
#         self,
#         xx: float,
#         yy: float,
#         width: float,
#         height: float,
#         track: bool = True,
#         id: Optional[str] = None,
#         **kwargs,
#     ) -> None:
#         # Method Name for downstream csv exporting
#         method_name = "plot_rectangle"
# 
#         # Plotting with pure matplotlib methods under non-tracking context
#         with self._no_tracking():
#             self._axis_mpl = self._get_ax_module().plot_rectangle(
#                 self._axis_mpl, xx, yy, width, height, **kwargs
#             )
# 
#         # Tracking
#         tracked_dict = {"xx": xx, "yy": yy, "width": width, "height": height}
#         self._track(track, id, method_name, tracked_dict, None)
# 
#         return self._axis_mpl
# 
#     # @wraps removed to avoid circular import
#     def plot_fillv(
#         self,
#         starts: ArrayLike,
#         ends: ArrayLike,
#         color: str = "red",
#         alpha: float = 0.2,
#         track: bool = True,
#         id: Optional[str] = None,
#         **kwargs,
#     ) -> None:
#         # Method Name for downstream csv exporting
#         method_name = "plot_fillv"
# 
#         # Plotting with pure matplotlib methods under non-tracking context
#         with self._no_tracking():
#             self._axis_mpl = self._get_ax_module().plot_fillv(
#                 self._axis_mpl, starts, ends, color=color, alpha=alpha
#             )
# 
#         # Tracking
#         tracked_dict = {"starts": starts, "ends": ends}
#         self._track(track, id, method_name, tracked_dict, None)
# 
#         return self._axis_mpl
# 
#     def plot_box(
#         self,
#         data: ArrayLike,
#         track: bool = True,
#         id: Optional[str] = None,
#         **kwargs,
#     ) -> None:
#         # Method Name for downstream csv exporting
#         method_name = "plot_box"
# 
#         # Copy data
#         _data = data.copy()
# 
#         # Sample count as label
#         n = len(data)
#         if kwargs.get("label"):
#             kwargs["label"] = kwargs["label"] + f" (n={n})"
# 
#         # Plotting with pure matplotlib methods under non-tracking context
#         with self._no_tracking():
#             self._axis_mpl.boxplot(data, **kwargs)
# 
#         # Tracking
#         tracked_dict = {
#             "data": _data,
#             "n": [n for ii in range(len(data))],
#         }
#         self._track(track, id, method_name, tracked_dict, None)
# 
#         return self._axis_mpl
#         
#     def hist(
#         self,
#         x: ArrayLike,
#         bins: Union[int, str, ArrayLike] = 10,
#         range: Optional[Tuple[float, float]] = None,
#         align_bins: bool = True,
#         track: bool = True,
#         id: Optional[str] = None,
#         **kwargs,
#     ) -> None:
#         """
#         Plot a histogram.
#         
#         This is an override of the standard matplotlib hist function to ensure
#         that histogram bin data is properly tracked for CSV export and bins are
#         aligned for histograms on the same axis.
#         
#         Args:
#             x: Input data
#             bins: Bin specification (count, edges, or algorithm)
#             range: Optional histogram range (min, max)
#             align_bins: Whether to align bins with other histograms on this axis
#             track: Whether to track this operation
#             id: Identifier for tracking
#             **kwargs: Additional keywords passed to matplotlib hist
#             
#         Returns:
#             Histogram output
#         """
#         # Method Name for downstream csv exporting
#         method_name = "hist"
#         
#         # Get the axis ID for bin alignment
#         axis_id = str(hash(self._axis_mpl))
#         hist_id = id if id is not None else str(self.id)
#         
#         # Align bins if requested and not the first histogram on this axis
#         if align_bins:
#             from ....plt.utils import histogram_bin_manager
#             bins, range = histogram_bin_manager.register_histogram(
#                 axis_id, hist_id, x, bins, range
#             )
#         
#         # Plotting with pure matplotlib methods under non-tracking context
#         with self._no_tracking():
#             hist_data = self._axis_mpl.hist(x, bins=bins, range=range, **kwargs)
#         
#         # Save histogram result for CSV export
#         # hist_data[0] = counts, hist_data[1] = bin_edges
#         tracked_dict = {
#             "args": (x,),
#             "hist_result": (hist_data[0], hist_data[1]),
#             "bins": bins,
#             "range": range,
#         }
#         
#         self._track(track, id, method_name, tracked_dict, kwargs)
#         
#         return hist_data
# 
#     # @wraps removed to avoid circular import
#     def plot_raster(
#         self,
#         positions: List[ArrayLike],
#         time: Optional[ArrayLike] = None,
#         labels: Optional[List[str]] = None,
#         colors: Optional[List[str]] = None,
#         track: bool = True,
#         id: Optional[str] = None,
#         **kwargs,
#     ) -> None:
#         # Method Name for downstream csv exporting
#         method_name = "plot_raster"
# 
#         # Plotting with pure matplotlib methods under non-tracking context
#         with self._no_tracking():
#             self._axis_mpl, raster_digit_df = self._get_ax_module().plot_raster(
#                 self._axis_mpl, positions, time=time
#             )
# 
#         # Tracking
#         tracked_dict = {"raster_digit_df": raster_digit_df}
#         self._track(track, id, method_name, tracked_dict, None)
# 
#         return self._axis_mpl, raster_digit_df
# 
#     # @wraps removed to avoid circular import
#     def plot_ecdf(
#         self,
#         data: ArrayLike,
#         track: bool = True,
#         id: Optional[str] = None,
#         **kwargs,
#     ) -> None:
#         # Method Name for downstream csv exporting
#         method_name = "plot_ecdf"
# 
#         # Plotting with pure matplotlib methods under non-tracking context
#         with self._no_tracking():
#             self._axis_mpl, ecdf_df = self._get_ax_module().plot_ecdf(
#                 self._axis_mpl, data, **kwargs
#             )
# 
#         # Tracking
#         tracked_dict = {"ecdf_df": ecdf_df}
#         self._track(track, id, method_name, tracked_dict, None)
# 
#         return self._axis_mpl, ecdf_df
# 
#     # @wraps removed to avoid circular import
#     def plot_joyplot(
#         self,
#         data: ArrayLike,
#         orientation: str = "vertical",
#         track: bool = True,
#         id: Optional[str] = None,
#         **kwargs,
#     ) -> None:
#         # Method Name for downstream csv exporting
#         method_name = "plot_joyplot"
# 
#         # Plotting with pure matplotlib methods under non-tracking context
#         with self._no_tracking():
#             self._axis_mpl = self._get_ax_module().plot_joyplot(
#                 self._axis_mpl, data, orientation=orientation, **kwargs
#             )
# 
#         # Tracking
#         tracked_dict = {"joyplot_data": data}
#         self._track(track, id, method_name, tracked_dict, None)
# 
#         return self._axis_mpl
# 
#     # @wraps removed to avoid circular import
#     def plot_joyplot(
#         self,
#         data: ArrayLike,
#         track: bool = True,
#         id: Optional[str] = None,
#         **kwargs,
#     ) -> None:
#         # Method Name for downstream csv exporting
#         method_name = "plot_joyplot"
# 
#         # Plotting with pure matplotlib methods under non-tracking context
#         with self._no_tracking():
#             self._axis_mpl = self._get_ax_module().plot_joyplot(self._axis_mpl, data, **kwargs)
# 
#         # Tracking
#         tracked_dict = {"joyplot_data": data}
#         self._track(track, id, method_name, tracked_dict, None)
# 
#         return self._axis_mpl
# 
#     # @wraps removed to avoid circular import
#     def plot_scatter_hist(
#         self,
#         x: ArrayLike,
#         y: ArrayLike,
#         hist_bins: int = 20,
#         scatter_alpha: float = 0.6,
#         scatter_size: float = 20,
#         scatter_color: str = "blue",
#         hist_color_x: str = "blue",
#         hist_color_y: str = "red",
#         hist_alpha: float = 0.5,
#         scatter_ratio: float = 0.8,
#         track: bool = True,
#         id: Optional[str] = None,
#         **kwargs,
#     ) -> None:
#         """Plot a scatter plot with marginal histograms."""
#         # Method Name for downstream csv exporting
#         method_name = "plot_scatter_hist"
# 
#         # Plotting with pure matplotlib methods under non-tracking context
#         with self._no_tracking():
#             self._axis_mpl, ax_histx, ax_histy, hist_data = self._get_ax_module().plot_scatter_hist(
#                 self._axis_mpl,
#                 x,
#                 y,
#                 hist_bins=hist_bins,
#                 scatter_alpha=scatter_alpha,
#                 scatter_size=scatter_size,
#                 scatter_color=scatter_color,
#                 hist_color_x=hist_color_x,
#                 hist_color_y=hist_color_y,
#                 hist_alpha=hist_alpha,
#                 scatter_ratio=scatter_ratio,
#                 **kwargs,
#             )
# 
#         # Tracking
#         tracked_dict = {
#             "x": x,
#             "y": y,
#             "hist_x": hist_data["hist_x"],
#             "hist_y": hist_data["hist_y"],
#             "bin_edges_x": hist_data["bin_edges_x"],
#             "bin_edges_y": hist_data["bin_edges_y"],
#         }
#         self._track(track, id, method_name, tracked_dict, None)
# 
#         return self._axis_mpl, ax_histx, ax_histy, hist_data
# 
#     # @wraps removed to avoid circular import
#     def plot_heatmap(
#         self,
#         data: ArrayLike,
#         x_labels: Optional[List[str]] = None,
#         y_labels: Optional[List[str]] = None,
#         cmap: str = "viridis",
#         cbar_label: str = "ColorBar Label",
#         value_format: str = "{x:.1f}",
#         show_annot: bool = True,
#         annot_color_lighter: str = "white",
#         annot_color_darker: str = "black",
#         track: bool = True,
#         id: Optional[str] = None,
#         **kwargs,
#     ) -> Tuple[matplotlib.image.AxesImage, matplotlib.colorbar.Colorbar]:
#         """Plot a heatmap on the axes."""
#         # Method Name for downstream csv exporting
#         method_name = "plot_heatmap"
# 
#         # Plotting with pure matplotlib methods under non-tracking context
#         with self._no_tracking():
#             ax, im, cbar = self._get_ax_module().plot_heatmap(
#                 self._axis_mpl,
#                 data,
#                 x_labels=x_labels,
#                 y_labels=y_labels,
#                 cmap=cmap,
#                 cbar_label=cbar_label,
#                 value_format=value_format,
#                 show_annot=show_annot,
#                 annot_color_lighter=annot_color_lighter,
#                 annot_color_darker=annot_color_darker,
#                 **kwargs,
#             )
# 
#         # Tracking
#         tracked_dict = {
#             "data": data,
#             "x_labels": x_labels,
#             "y_labels": y_labels,
#         }
#         self._track(track, id, method_name, tracked_dict, None)
# 
#         return ax, im, cbar
# 
#     # @wraps removed to avoid circular import
#     def plot_violin(
#         self,
#         data: Union[pd.DataFrame, List, ArrayLike],
#         x=None,
#         y=None,
#         hue=None,
#         labels=None,
#         colors=None,
#         half=False,
#         track: bool = True,
#         id: Optional[str] = None,
#         **kwargs,
#     ) -> None:
#         """Plot a violin plot."""
#         # Method Name for downstream csv exporting
#         method_name = "plot_violin"
# 
#         # Plotting with pure matplotlib methods under non-tracking context
#         with self._no_tracking():
#             # Handle the list-style input case
#             if isinstance(data, list) and all(
#                 isinstance(item, (list, np.ndarray)) for item in data
#             ):
#                 self._axis_mpl = self._get_ax_module().plot_violin(
#                     self._axis_mpl,
#                     data_list=data,
#                     labels=labels,
#                     colors=colors,
#                     half=half,
#                     **kwargs,
#                 )
#             # Handle DataFrame or other inputs
#             else:
#                 self._axis_mpl = self._get_ax_module().plot_violin(
#                     self._axis_mpl,
#                     data=data,
#                     x=x,
#                     y=y,
#                     hue=hue,
#                     half=half,
#                     **kwargs,
#                 )
# 
#         # Tracking
#         tracked_dict = {
#             "data": data,
#             "x": x,
#             "y": y,
#             "hue": hue,
#             "half": half,
#             "labels": labels,
#             "colors": colors,
#         }
#         self._track(track, id, method_name, tracked_dict, None)
#         return self._axis_mpl
# 
#     # def plot_area(
#     #     self,
#     #     x: ArrayLike,
#     #     y: ArrayLike,
#     #     stacked: bool = False,
#     #     fill: bool = True,
#     #     alpha: float = 0.5,
#     #     track: bool = True,
#     #     id: Optional[str] = None,
#     #     **kwargs,
#     # ) -> None:
#     #     """Plot an area plot."""
#     #     # Method Name for downstream csv exporting
#     #     method_name = "plot_area"
# 
#     #     # Plotting with pure matplotlib methods under non-tracking context
#     #     with self._no_tracking():
#     #         self._axis_mpl = self._get_ax_module().plot_area(
#     #             self._axis_mpl,
#     #             x,
#     #             y,
#     #             stacked=stacked,
#     #             fill=fill,
#     #             alpha=alpha,
#     #             **kwargs,
#     #         )
# 
#     #     # Tracking
#     #     tracked_dict = {"x": x, "y": y}
#     #     self._track(track, id, method_name, tracked_dict, None)
# 
#     #     return self._axis_mpl
# 
#     # def plot_radar(
#     #     self,
#     #     data: ArrayLike,
#     #     categories: List[str],
#     #     groups: Optional[List[str]] = None,
#     #     fill: bool = True,
#     #     alpha: float = 0.2,
#     #     grid_step: int = 5,
#     #     track: bool = True,
#     #     id: Optional[str] = None,
#     #     **kwargs,
#     # ) -> None:
#     #     """Plot a radar/spider chart."""
#     #     # Method Name for downstream csv exporting
#     #     method_name = "plot_radar"
# 
#     #     # Convert data to DataFrame if not already
#     #     if not isinstance(data, pd.DataFrame):
#     #         if groups is not None:
#     #             data = pd.DataFrame(data, columns=categories, index=groups)
#     #         else:
#     #             data = pd.DataFrame(data, columns=categories)
# 
#     #     # Plotting with pure matplotlib methods under non-tracking context
#     #     with self._no_tracking():
#     #         self._axis_mpl = self._get_ax_module().plot_radar(
#     #             self._axis_mpl,
#     #             data,
#     #             categories=categories,
#     #             fill=fill,
#     #             alpha=alpha,
#     #             grid_step=grid_step,
#     #             **kwargs,
#     #         )
# 
#     #     # Tracking
#     #     tracked_dict = {"radar_data": data}
#     #     self._track(track, id, method_name, tracked_dict, None)
# 
#     #     return self._axis_mpl
# 
#     # def plot_bubble(
#     #     self,
#     #     x: ArrayLike,
#     #     y: ArrayLike,
#     #     size: ArrayLike,
#     #     color: Optional[ArrayLike] = None,
#     #     size_scale: float = 1000.0,
#     #     alpha: float = 0.6,
#     #     colormap: str = "viridis",
#     #     show_colorbar: bool = True,
#     #     colorbar_label: str = "",
#     #     track: bool = True,
#     #     id: Optional[str] = None,
#     #     **kwargs,
#     # ) -> None:
#     #     """Plot a bubble chart."""
#     #     # Method Name for downstream csv exporting
#     #     method_name = "plot_bubble"
# 
#     #     # Plotting with pure matplotlib methods under non-tracking context
#     #     with self._no_tracking():
#     #         self._axis_mpl = self._get_ax_module().plot_bubble(
#     #             self._axis_mpl,
#     #             x,
#     #             y,
#     #             size,
#     #             color=color,
#     #             size_scale=size_scale,
#     #             alpha=alpha,
#     #             colormap=colormap,
#     #             show_colorbar=show_colorbar,
#     #             colorbar_label=colorbar_label,
#     #             **kwargs,
#     #         )
# 
#     #     # Tracking
#     #     tracked_dict = {"x": x, "y": y, "size": size}
#     #     if color is not None:
#     #         tracked_dict["color"] = color
# 
#     #     self._track(track, id, method_name, tracked_dict, None)
# 
#     #     return self._axis_mpl
# 
#     # def plot_ridgeline(
#     #     self,
#     #     data: ArrayLike,
#     #     labels: Optional[List[str]] = None,
#     #     overlap: float = 0.8,
#     #     fill: bool = True,
#     #     alpha: float = 0.6,
#     #     colormap: str = "viridis",
#     #     bandwidth: Optional[float] = None,
#     #     track: bool = True,
#     #     id: Optional[str] = None,
#     #     **kwargs,
#     # ) -> None:
#     #     """Plot a ridgeline plot (similar to joyplot but with KDE)."""
#     #     # Method Name for downstream csv exporting
#     #     method_name = "plot_ridgeline"
# 
#     #     # Ensure data is in correct format
#     #     if isinstance(data, pd.DataFrame):
#     #         _data = [data[col].dropna().values for col in data.columns]
#     #         if labels is None:
#     #             labels = list(data.columns)
#     #     elif isinstance(data, list):
#     #         _data = data
#     #     else:
#     #         _data = [data]
# 
#     #     # Plotting with pure matplotlib methods under non-tracking context
#     #     with self._no_tracking():
#     #         self._axis_mpl, ridge_data = self._get_ax_module().plot_ridgeline(
#     #             self._axis_mpl,
#     #             _data,
#     #             labels=labels,
#     #             overlap=overlap,
#     #             fill=fill,
#     #             alpha=alpha,
#     #             colormap=colormap,
#     #             bandwidth=bandwidth,
#     #             **kwargs,
#     #         )
# 
#     #     # Tracking
#     #     tracked_dict = {
#     #         "ridgeline_data": _data,
#     #         "kde_x": ridge_data["kde_x"],
#     #         "kde_y": ridge_data["kde_y"],
#     #     }
#     #     if labels is not None:
#     #         tracked_dict["labels"] = labels
#     #     self._track(track, id, method_name, tracked_dict, None)
# 
#     #     return self._axis_mpl, ridge_data
# 
#     # def plot_parallel_coordinates(
#     #     self,
#     #     data: pd.DataFrame,
#     #     class_column: Optional[str] = None,
#     #     colormap: str = "viridis",
#     #     alpha: float = 0.5,
#     #     track: bool = True,
#     #     id: Optional[str] = None,
#     #     **kwargs,
#     # ) -> None:
#     #     """Plot parallel coordinates."""
#     #     # Method Name for downstream csv exporting
#     #     method_name = "plot_parallel_coordinates"
# 
#     #     # Plotting with pure matplotlib methods under non-tracking context
#     #     with self._no_tracking():
#     #         self._axis_mpl = self._get_ax_module().plot_parallel_coordinates(
#     #             self._axis_mpl,
#     #             data,
#     #             class_column=class_column,
#     #             colormap=colormap,
#     #             alpha=alpha,
#     #             **kwargs,
#     #         )
# 
#     #     # Tracking
#     #     tracked_dict = {"parallel_data": data}
#     #     self._track(track, id, method_name, tracked_dict, None)
# 
#     #     return self._axis_mpl
# 
#     # @wraps removed to avoid circular import
#     def plot_line(
#         self,
#         data: ArrayLike,
#         xx: Optional[ArrayLike] = None,
#         track: bool = True,
#         id: Optional[str] = None,
#         **kwargs,
#     ) -> None:
#         """Plot a simple line."""
#         # Method Name for downstream csv exporting
#         method_name = "plot_line"
# 
#         # Plotting with pure matplotlib methods under non-tracking context
#         with self._no_tracking():
#             self._axis_mpl, plot_df = self._get_ax_module().plot_line(
#                 self._axis_mpl, data, xx=xx, **kwargs
#             )
# 
#         # Tracking
#         tracked_dict = {"plot_df": plot_df}
#         self._track(track, id, method_name, tracked_dict, None)
# 
#         return self._axis_mpl, plot_df
# 
#     # @wraps removed to avoid circular import
#     def plot_mean_std(
#         self,
#         data: ArrayLike,
#         xx: Optional[ArrayLike] = None,
#         sd: float = 1,
#         track: bool = True,
#         id: Optional[str] = None,
#         **kwargs,
#     ) -> None:
#         """Plot mean line with standard deviation shading."""
#         # Method Name for downstream csv exporting
#         method_name = "plot_mean_std"
# 
#         # Plotting with pure matplotlib methods under non-tracking context
#         with self._no_tracking():
#             self._axis_mpl, plot_df = self._get_ax_module().plot_mean_std(
#                 self._axis_mpl, data, xx=xx, sd=sd, **kwargs
#             )
# 
#         # Tracking
#         tracked_dict = {"plot_df": plot_df}
#         self._track(track, id, method_name, tracked_dict, None)
# 
#         return self._axis_mpl, plot_df
# 
#     # @wraps removed to avoid circular import
#     def plot_mean_ci(
#         self,
#         data: ArrayLike,
#         xx: Optional[ArrayLike] = None,
#         perc: float = 95,
#         track: bool = True,
#         id: Optional[str] = None,
#         **kwargs,
#     ) -> None:
#         """Plot mean line with confidence interval shading."""
#         # Method Name for downstream csv exporting
#         method_name = "plot_mean_ci"
# 
#         # Plotting with pure matplotlib methods under non-tracking context
#         with self._no_tracking():
#             self._axis_mpl, plot_df = self._get_ax_module().plot_mean_ci(
#                 self._axis_mpl, data, xx=xx, perc=perc, **kwargs
#             )
# 
#         # Tracking
#         tracked_dict = {"plot_df": plot_df}
#         self._track(track, id, method_name, tracked_dict, None)
# 
#         return self._axis_mpl, plot_df
# 
#     # @wraps removed to avoid circular import
#     def plot_median_iqr(
#         self,
#         data: ArrayLike,
#         xx: Optional[ArrayLike] = None,
#         track: bool = True,
#         id: Optional[str] = None,
#         **kwargs,
#     ) -> None:
#         """Plot median line with interquartile range shading."""
#         # Method Name for downstream csv exporting
#         method_name = "plot_median_iqr"
# 
#         # Plotting with pure matplotlib methods under non-tracking context
#         with self._no_tracking():
#             self._axis_mpl, plot_df = self._get_ax_module().plot_median_iqr(
#                 self._axis_mpl, data, xx=xx, **kwargs
#             )
# 
#         # Tracking
#         tracked_dict = {"plot_df": plot_df}
#         self._track(track, id, method_name, tracked_dict, None)
# 
#         return self._axis_mpl, plot_df
# 
#     # @wraps removed to avoid circular import
#     def plot_shaded_line(
#         self,
#         xs: ArrayLike,
#         ys_lower: ArrayLike,
#         ys_middle: ArrayLike,
#         ys_upper: ArrayLike,
#         color: str or Optional[Union[str, List[str]]] = None,
#         label: str or Optional[Union[str, List[str]]] = None,
#         track: bool = True,
#         id: Optional[str] = None,
#         **kwargs,
#     ) -> None:
#         """Plot a line with shaded area between lower and upper bounds."""
#         # Method Name for downstream csv exporting
#         method_name = "plot_shaded_line"
# 
#         # Plotting with pure matplotlib methods under non-tracking context
#         with self._no_tracking():
#             self._axis_mpl, plot_df = self._get_ax_module().plot_shaded_line(
#                 self._axis_mpl,
#                 xs,
#                 ys_lower,
#                 ys_middle,
#                 ys_upper,
#                 color=color,
#                 label=label,
#                 **kwargs,
#             )
# 
#         # Tracking
#         tracked_dict = {"plot_df": plot_df}
#         self._track(track, id, method_name, tracked_dict, None)
# 
#         return self._axis_mpl, plot_df
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/plt/_subplots/_AxisWrapperMixins/_MatplotlibPlotMixin.py
# --------------------------------------------------------------------------------
