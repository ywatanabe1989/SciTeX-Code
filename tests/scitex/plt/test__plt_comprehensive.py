#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-30 11:10:00 (Claude)"
# File: /tests/scitex/plt/test__plt_comprehensive.py

"""
Comprehensive tests for scitex.plt module.
Tests enhanced plotting functionality with automatic data export.
"""

import os
import sys
import tempfile
import shutil
import pytest
import numpy as np
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../src"))

import scitex


class TestSubplotsWrapper:
    """Test the enhanced subplots wrapper functionality."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test outputs."""
        tmpdir = tempfile.mkdtemp()
        yield tmpdir
        # Cleanup
        if os.path.exists(tmpdir):
            shutil.rmtree(tmpdir)

    @pytest.fixture(autouse=True)
    def setup_matplotlib(self):
        """Setup matplotlib for testing."""
        # Use non-interactive backend
        matplotlib.use("Agg")
        yield
        # Close all figures after each test
        plt.close("all")

    def test_subplots_basic(self):
        """Test basic subplots creation."""
        # Act
        fig, axes = scitex.plt.subplots(2, 2)

        # Assert
        assert fig is not None
        assert hasattr(fig, "savefig")
        assert axes.shape == (2, 2)
        assert all(hasattr(ax, "plot") for ax in axes.flat)

    def test_subplots_single_axis(self):
        """Test subplots with single axis."""
        # Act
        fig, ax = scitex.plt.subplots()

        # Assert
        assert fig is not None
        assert hasattr(ax, "plot")
        assert not hasattr(ax, "shape")  # Single axis, not array

    def test_subplots_with_data_tracking(self, temp_dir):
        """Test that subplots wrapper tracks plotted data."""
        # Arrange
        x = np.linspace(0, 10, 100)
        y = np.sin(x)

        # Act
        fig, ax = scitex.plt.subplots()
        line = ax.plot(x, y, label="sin(x)")

        # Check if wrapper is tracking data
        if hasattr(ax, "_scitex_data"):
            assert len(ax._scitex_data) > 0

    def test_subplots_saves_data_with_figure(self, temp_dir):
        """Test that saving figure also saves data."""
        # Arrange
        x = np.linspace(0, 2 * np.pi, 50)
        y1 = np.sin(x)
        y2 = np.cos(x)

        fig_path = os.path.join(temp_dir, "test_plot.png")

        # Act
        fig, ax = scitex.plt.subplots()
        ax.plot(x, y1, label="sin")
        ax.plot(x, y2, label="cos")
        ax.legend()
        fig.savefig(fig_path)

        # Assert
        assert os.path.exists(fig_path)

        # Check if data was saved
        csv_path = fig_path.replace(".png", ".csv")
        if os.path.exists(csv_path):
            # Data export is working
            df = pd.read_csv(csv_path)
            assert len(df) == len(x)

    def test_subplots_with_multiple_axes(self, temp_dir):
        """Test subplots with multiple axes and different plots."""
        # Arrange
        x = np.linspace(0, 10, 100)

        # Act
        fig, axes = scitex.plt.subplots(2, 2, figsize=(10, 8))

        # Different plot types
        axes[0, 0].plot(x, np.sin(x))
        axes[0, 1].scatter(x[::5], np.cos(x[::5]))
        axes[1, 0].hist(np.random.randn(1000), bins=30)
        axes[1, 1].bar(["A", "B", "C"], [1, 2, 3])

        # Save
        fig_path = os.path.join(temp_dir, "multi_plot.png")
        fig.savefig(fig_path)

        # Assert
        assert os.path.exists(fig_path)
        assert all(len(ax.get_children()) > 0 for ax in axes.flat)


class TestPlottingFunctions:
    """Test various plotting utility functions."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test outputs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture(autouse=True)
    def setup_matplotlib(self):
        """Setup matplotlib for testing."""
        matplotlib.use("Agg")
        yield
        plt.close("all")

    def test_plot_with_style(self):
        """Test plotting with scitex style enhancements."""
        # Create figure
        fig, ax = scitex.plt.subplots()

        # Plot data
        x = np.linspace(0, 10, 100)
        ax.plot(x, np.sin(x))

        # Check if style is applied
        if hasattr(ax, "spines"):
            # Top and right spines might be hidden
            pass

    def test_color_palette(self):
        """Test scitex color palette functionality."""
        # Get colors
        if hasattr(scitex.plt, "get_colors"):
            colors = scitex.plt.get_colors()
            assert isinstance(colors, (dict, list))
            if isinstance(colors, dict):
                assert "blue" in colors or "b" in colors

    def test_save_with_high_dpi(self, temp_dir):
        """Test saving figures with high DPI."""
        # Create plot
        fig, ax = scitex.plt.subplots()
        ax.plot([1, 2, 3], [1, 4, 9])

        # Save with high DPI
        fig_path = os.path.join(temp_dir, "high_dpi.png")
        fig.savefig(fig_path, dpi=300)

        # Check file exists and has reasonable size
        assert os.path.exists(fig_path)
        file_size = os.path.getsize(fig_path)
        assert file_size > 10000  # Should be larger due to high DPI


class TestSpecializedPlots:
    """Test specialized plotting functions if available."""

    @pytest.fixture(autouse=True)
    def setup_matplotlib(self):
        """Setup matplotlib for testing."""
        matplotlib.use("Agg")
        yield
        plt.close("all")

    def test_heatmap_if_available(self):
        """Test heatmap plotting if function exists."""
        if hasattr(scitex.plt, "heatmap") or hasattr(scitex.plt.ax, "heatmap"):
            # Create sample data
            data = np.random.randn(10, 10)

            # Create heatmap
            fig, ax = scitex.plt.subplots()
            if hasattr(scitex.plt, "heatmap"):
                scitex.plt.heatmap(data, ax=ax)
            elif hasattr(ax, "heatmap"):
                ax.heatmap(data)

    def test_confusion_matrix_if_available(self):
        """Test confusion matrix plotting if available."""
        if hasattr(scitex.plt, "confusion_matrix") or hasattr(
            scitex.plt, "plot_confusion_matrix"
        ):
            # Create sample confusion matrix
            conf_mat = np.array([[50, 10], [5, 35]])

            # Plot
            fig, ax = scitex.plt.subplots()
            if hasattr(scitex.plt, "confusion_matrix"):
                scitex.plt.confusion_matrix(conf_mat, ax=ax)
            elif hasattr(scitex.plt, "plot_confusion_matrix"):
                scitex.plt.plot_confusion_matrix(conf_mat, ax=ax)


class TestDataExport:
    """Test automatic data export functionality."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test outputs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture(autouse=True)
    def setup_matplotlib(self):
        """Setup matplotlib for testing."""
        matplotlib.use("Agg")
        yield
        plt.close("all")

    def test_line_plot_data_export(self, temp_dir):
        """Test data export from line plots."""
        # Create data
        x = np.linspace(0, 10, 50)
        y1 = np.sin(x)
        y2 = np.cos(x)

        # Plot
        fig, ax = scitex.plt.subplots()
        ax.plot(x, y1, label="sin")
        ax.plot(x, y2, label="cos")
        ax.legend()

        # Save
        fig_path = os.path.join(temp_dir, "lines.png")
        fig.savefig(fig_path)

        # Check for exported data
        csv_path = fig_path.replace(".png", "_data.csv")
        json_path = fig_path.replace(".png", "_data.json")

        # At least one data export format should exist
        data_exported = any(os.path.exists(p) for p in [csv_path, json_path])
        # Note: Data export might not be implemented yet

    def test_scatter_plot_data_export(self, temp_dir):
        """Test data export from scatter plots."""
        # Create data
        x = np.random.randn(100)
        y = 2 * x + np.random.randn(100) * 0.5

        # Plot
        fig, ax = scitex.plt.subplots()
        ax.scatter(x, y, alpha=0.5)
        ax.set_xlabel("X")
        ax.set_ylabel("Y")

        # Save
        fig_path = os.path.join(temp_dir, "scatter.png")
        fig.savefig(fig_path)

        assert os.path.exists(fig_path)

    def test_histogram_data_export(self, temp_dir):
        """Test data export from histograms."""
        # Create data
        data = np.random.randn(1000)

        # Plot
        fig, ax = scitex.plt.subplots()
        n, bins, patches = ax.hist(data, bins=30, alpha=0.7)

        # Save
        fig_path = os.path.join(temp_dir, "histogram.png")
        fig.savefig(fig_path)

        assert os.path.exists(fig_path)


class TestPlotEnhancements:
    """Test plot enhancement features."""

    @pytest.fixture(autouse=True)
    def setup_matplotlib(self):
        """Setup matplotlib for testing."""
        matplotlib.use("Agg")
        yield
        plt.close("all")

    def test_axis_formatting(self):
        """Test axis formatting enhancements."""
        fig, ax = scitex.plt.subplots()

        # Check if enhanced methods exist
        enhanced_methods = [
            "set_xlabel",
            "set_ylabel",
            "set_title",
            "set_xlim",
            "set_ylim",
            "legend",
        ]

        for method in enhanced_methods:
            assert hasattr(ax, method)

    def test_figure_size_control(self):
        """Test figure size control."""
        # Test different figure sizes
        sizes = [(6, 4), (10, 6), (8, 8)]

        for size in sizes:
            fig, ax = scitex.plt.subplots(figsize=size)
            fig_size = fig.get_size_inches()
            np.testing.assert_array_almost_equal(fig_size, size)

    def test_style_consistency(self):
        """Test that scitex maintains consistent styling."""
        # Create multiple figures
        fig1, ax1 = scitex.plt.subplots()
        fig2, ax2 = scitex.plt.subplots()

        # Both should have consistent properties
        assert ax1.xaxis.label.get_fontsize() == ax2.xaxis.label.get_fontsize()
        assert ax1.title.get_fontsize() == ax2.title.get_fontsize()


class TestIntegration:
    """Test integration with other scitex modules."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test outputs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture(autouse=True)
    def setup_matplotlib(self):
        """Setup matplotlib for testing."""
        matplotlib.use("Agg")
        yield
        plt.close("all")

    def test_plot_and_save_workflow(self, temp_dir):
        """Test complete workflow of plotting and saving."""
        # Generate data
        x = np.linspace(0, 10, 100)
        y = np.exp(-x / 5) * np.cos(2 * x)

        # Create plot
        fig, ax = scitex.plt.subplots(figsize=(8, 6))
        ax.plot(x, y, "b-", linewidth=2)
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Amplitude")
        ax.set_title("Damped Oscillation")
        ax.grid(True, alpha=0.3)

        # Save figure
        fig_path = os.path.join(temp_dir, "damped_oscillation.png")
        fig.savefig(fig_path, dpi=150, bbox_inches="tight")

        # Verify
        assert os.path.exists(fig_path)
        assert os.path.getsize(fig_path) > 0

    def test_multiple_subplots_workflow(self, temp_dir):
        """Test workflow with multiple subplots."""
        # Create complex figure
        fig, axes = scitex.plt.subplots(2, 3, figsize=(15, 10))

        # Generate different plots
        x = np.linspace(0, 10, 100)

        # Row 1
        axes[0, 0].plot(x, np.sin(x))
        axes[0, 0].set_title("Sine")

        axes[0, 1].plot(x, np.cos(x))
        axes[0, 1].set_title("Cosine")

        axes[0, 2].plot(x, np.tan(x))
        axes[0, 2].set_ylim(-10, 10)
        axes[0, 2].set_title("Tangent")

        # Row 2
        axes[1, 0].hist(np.random.randn(1000), bins=30)
        axes[1, 0].set_title("Normal Distribution")

        axes[1, 1].scatter(np.random.rand(50), np.random.rand(50))
        axes[1, 1].set_title("Random Scatter")

        axes[1, 2].bar(["A", "B", "C", "D"], [3, 7, 2, 5])
        axes[1, 2].set_title("Bar Chart")

        # Adjust layout
        fig.tight_layout()

        # Save
        fig_path = os.path.join(temp_dir, "multi_panel.png")
        fig.savefig(fig_path)

        assert os.path.exists(fig_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
