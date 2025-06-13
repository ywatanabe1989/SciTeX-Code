#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-10 18:00:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/plt/ax/_plot/test__plot_shaded_line_comprehensive.py

"""Comprehensive tests for plot_shaded_line functionality."""

import os
import numpy as np
import pytest
import matplotlib.pyplot as plt
import pandas as pd
from unittest.mock import patch, MagicMock
from scitex.plt.ax._plot import plot_shaded_line, _plot_single_shaded_line, _plot_shaded_line


class TestPlotShadedLineBasic:
    """Test basic plot_shaded_line functionality."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
        
        # Create sample data
        self.x = np.linspace(0, 10, 100)
        self.y_middle = np.sin(self.x)
        self.y_lower = self.y_middle - 0.2
        self.y_upper = self.y_middle + 0.2
        
        # Create output directory if it doesn't exist
        self.out_dir = os.path.join(os.path.dirname(__file__), "test_output")
        os.makedirs(self.out_dir, exist_ok=True)
    
    def teardown_method(self):
        """Clean up after tests."""
        plt.close('all')
    
    def test_single_shaded_line_basic(self):
        """Test basic single shaded line plotting."""
        ax, df = plot_shaded_line(
            self.ax,
            self.x,
            self.y_lower,
            self.y_middle,
            self.y_upper
        )
        
        assert ax is self.ax
        assert isinstance(df, pd.DataFrame)
        assert len(self.ax.lines) > 0
        assert len(self.ax.collections) > 0
    
    def test_single_shaded_line_with_color(self):
        """Test single shaded line with custom color."""
        ax, df = plot_shaded_line(
            self.ax,
            self.x,
            self.y_lower,
            self.y_middle,
            self.y_upper,
            color='red'
        )
        
        # Check that line color is red
        line = self.ax.lines[0]
        assert line.get_color() == 'red'
    
    def test_single_shaded_line_with_label(self):
        """Test single shaded line with label."""
        ax, df = plot_shaded_line(
            self.ax,
            self.x,
            self.y_lower,
            self.y_middle,
            self.y_upper,
            label='Test Label'
        )
        
        # Check that label was set
        line = self.ax.lines[0]
        assert line.get_label() == 'Test Label'
    
    def test_single_shaded_line_with_alpha(self):
        """Test single shaded line with custom alpha."""
        ax, df = plot_shaded_line(
            self.ax,
            self.x,
            self.y_lower,
            self.y_middle,
            self.y_upper,
            alpha=0.5
        )
        
        # Check that alpha was set
        line = self.ax.lines[0]
        assert line.get_alpha() == 0.5
    
    def test_returned_dataframe_structure(self):
        """Test the structure of returned DataFrame."""
        ax, df = plot_shaded_line(
            self.ax,
            self.x,
            self.y_lower,
            self.y_middle,
            self.y_upper
        )
        
        # Check DataFrame columns
        expected_columns = ['x', 'y_lower', 'y_middle', 'y_upper']
        assert list(df.columns) == expected_columns
        
        # Check DataFrame values
        np.testing.assert_array_equal(df['x'].values, self.x)
        np.testing.assert_array_equal(df['y_lower'].values, self.y_lower)
        np.testing.assert_array_equal(df['y_middle'].values, self.y_middle)
        np.testing.assert_array_equal(df['y_upper'].values, self.y_upper)


class TestPlotShadedLineMultiple:
    """Test multiple shaded lines functionality."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
        
        # Create sample data for multiple lines
        self.n_lines = 3
        self.x = np.linspace(0, 10, 100)
        
        self.xs = [self.x for _ in range(self.n_lines)]
        self.ys_middle = [np.sin(self.x + i) for i in range(self.n_lines)]
        self.ys_lower = [y - 0.2 for y in self.ys_middle]
        self.ys_upper = [y + 0.2 for y in self.ys_middle]
    
    def teardown_method(self):
        """Clean up after tests."""
        plt.close('all')
    
    def test_multiple_shaded_lines_basic(self):
        """Test basic multiple shaded lines plotting."""
        ax, dfs = _plot_shaded_line(
            self.ax,
            self.xs,
            self.ys_lower,
            self.ys_middle,
            self.ys_upper
        )
        
        assert ax is self.ax
        assert isinstance(dfs, list)
        assert len(dfs) == self.n_lines
        assert all(isinstance(df, pd.DataFrame) for df in dfs)
        
        # Check that correct number of lines and collections were created
        assert len(self.ax.lines) == self.n_lines
        assert len(self.ax.collections) == self.n_lines
    
    def test_multiple_shaded_lines_with_single_color(self):
        """Test multiple shaded lines with single color."""
        ax, dfs = _plot_shaded_line(
            self.ax,
            self.xs,
            self.ys_lower,
            self.ys_middle,
            self.ys_upper,
            color='blue'
        )
        
        # All lines should be blue
        for line in self.ax.lines:
            assert line.get_color() == 'blue'
    
    def test_multiple_shaded_lines_with_color_list(self):
        """Test multiple shaded lines with color list."""
        colors = ['red', 'green', 'blue']
        ax, dfs = _plot_shaded_line(
            self.ax,
            self.xs,
            self.ys_lower,
            self.ys_middle,
            self.ys_upper,
            color=colors
        )
        
        # Each line should have its corresponding color
        for i, line in enumerate(self.ax.lines):
            assert line.get_color() == colors[i]
    
    def test_multiple_shaded_lines_different_lengths(self):
        """Test multiple shaded lines with different x array lengths."""
        # Create data with different lengths
        xs = [np.linspace(0, 10, 50), np.linspace(0, 10, 100), np.linspace(0, 10, 150)]
        ys_middle = [np.sin(x) for x in xs]
        ys_lower = [y - 0.2 for y in ys_middle]
        ys_upper = [y + 0.2 for y in ys_middle]
        
        ax, dfs = _plot_shaded_line(
            self.ax,
            xs,
            ys_lower,
            ys_middle,
            ys_upper
        )
        
        # Check that DataFrames have correct lengths
        for i, df in enumerate(dfs):
            assert len(df) == len(xs[i])


class TestPlotShadedLineEdgeCases:
    """Test edge cases and error handling."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
    
    def teardown_method(self):
        """Clean up after tests."""
        plt.close('all')
    
    def test_mismatched_array_lengths(self):
        """Test error when arrays have different lengths."""
        x = np.linspace(0, 10, 100)
        y_middle = np.sin(x)
        y_lower = y_middle[:-10]  # Shorter array
        y_upper = y_middle + 0.2
        
        with pytest.raises(AssertionError, match="All arrays must have the same length"):
            plot_shaded_line(self.ax, x, y_lower, y_middle, y_upper)
    
    def test_invalid_axis_type(self):
        """Test error when axis is not matplotlib axis."""
        x = np.linspace(0, 10, 100)
        y_middle = np.sin(x)
        y_lower = y_middle - 0.2
        y_upper = y_middle + 0.2
        
        with pytest.raises(AssertionError, match="First argument must be a matplotlib axis"):
            _plot_single_shaded_line("not_an_axis", x, y_lower, y_middle, y_upper)
    
    def test_empty_arrays(self):
        """Test with empty arrays."""
        x = np.array([])
        y_middle = np.array([])
        y_lower = np.array([])
        y_upper = np.array([])
        
        ax, df = plot_shaded_line(self.ax, x, y_lower, y_middle, y_upper)
        
        assert len(df) == 0
        assert len(self.ax.lines) == 1  # Empty line still created
    
    def test_single_point(self):
        """Test with single data point."""
        x = np.array([1.0])
        y_middle = np.array([0.5])
        y_lower = np.array([0.3])
        y_upper = np.array([0.7])
        
        ax, df = plot_shaded_line(self.ax, x, y_lower, y_middle, y_upper)
        
        assert len(df) == 1
        assert len(self.ax.lines) == 1
    
    def test_nan_values(self):
        """Test handling of NaN values."""
        x = np.linspace(0, 10, 100)
        y_middle = np.sin(x)
        y_middle[40:60] = np.nan
        y_lower = y_middle - 0.2
        y_upper = y_middle + 0.2
        
        ax, df = plot_shaded_line(self.ax, x, y_lower, y_middle, y_upper)
        
        # Should still create plot despite NaN values
        assert len(self.ax.lines) > 0
        assert len(self.ax.collections) > 0
    
    def test_infinite_values(self):
        """Test handling of infinite values."""
        x = np.linspace(0, 10, 100)
        y_middle = np.sin(x)
        y_middle[50] = np.inf
        y_lower = y_middle - 0.2
        y_upper = y_middle + 0.2
        
        ax, df = plot_shaded_line(self.ax, x, y_lower, y_middle, y_upper)
        
        # Should still create plot despite infinite values
        assert len(self.ax.lines) > 0
        assert len(self.ax.collections) > 0


class TestPlotShadedLineIntegration:
    """Test integration with other matplotlib features."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
    
    def teardown_method(self):
        """Clean up after tests."""
        plt.close('all')
    
    def test_multiple_calls_same_axis(self):
        """Test multiple calls to plot_shaded_line on same axis."""
        x = np.linspace(0, 10, 100)
        
        # First call
        y1_middle = np.sin(x)
        y1_lower = y1_middle - 0.2
        y1_upper = y1_middle + 0.2
        ax1, df1 = plot_shaded_line(
            self.ax, x, y1_lower, y1_middle, y1_upper, 
            label='Sin', color='blue'
        )
        
        # Second call
        y2_middle = np.cos(x)
        y2_lower = y2_middle - 0.2
        y2_upper = y2_middle + 0.2
        ax2, df2 = plot_shaded_line(
            self.ax, x, y2_lower, y2_middle, y2_upper,
            label='Cos', color='red'
        )
        
        assert ax1 is ax2 is self.ax
        assert len(self.ax.lines) == 2
        assert len(self.ax.collections) == 2
        
        # Check labels
        labels = [line.get_label() for line in self.ax.lines]
        assert 'Sin' in labels
        assert 'Cos' in labels
    
    def test_with_existing_plots(self):
        """Test adding shaded line to axis with existing plots."""
        # Add regular plot first
        x = np.linspace(0, 10, 100)
        self.ax.plot(x, np.sin(x), 'k--', label='Regular plot')
        
        # Add shaded line
        y_middle = np.cos(x)
        y_lower = y_middle - 0.2
        y_upper = y_middle + 0.2
        ax, df = plot_shaded_line(
            self.ax, x, y_lower, y_middle, y_upper,
            label='Shaded plot'
        )
        
        # Should have 2 lines total
        assert len(self.ax.lines) == 2
        assert len(self.ax.collections) == 1
    
    def test_with_axis_limits(self):
        """Test shaded line respects axis limits."""
        # Set axis limits before plotting
        self.ax.set_xlim(2, 8)
        self.ax.set_ylim(-0.5, 0.5)
        
        x = np.linspace(0, 10, 100)
        y_middle = np.sin(x)
        y_lower = y_middle - 0.2
        y_upper = y_middle + 0.2
        
        ax, df = plot_shaded_line(self.ax, x, y_lower, y_middle, y_upper)
        
        # Check that limits are preserved
        assert self.ax.get_xlim() == (2, 8)
        assert self.ax.get_ylim() == (-0.5, 0.5)
    
    def test_with_logarithmic_scale(self):
        """Test shaded line with logarithmic scale."""
        # Use log scale
        self.ax.set_yscale('log')
        
        x = np.linspace(1, 10, 100)
        y_middle = np.exp(x/5)
        y_lower = y_middle * 0.8
        y_upper = y_middle * 1.2
        
        ax, df = plot_shaded_line(self.ax, x, y_lower, y_middle, y_upper)
        
        # Check that scale is still logarithmic
        assert self.ax.get_yscale() == 'log'
        assert len(self.ax.lines) > 0
        assert len(self.ax.collections) > 0


class TestPlotShadedLineKwargs:
    """Test various kwargs passed to plot_shaded_line."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
        
        self.x = np.linspace(0, 10, 100)
        self.y_middle = np.sin(self.x)
        self.y_lower = self.y_middle - 0.2
        self.y_upper = self.y_middle + 0.2
    
    def teardown_method(self):
        """Clean up after tests."""
        plt.close('all')
    
    def test_linestyle_kwarg(self):
        """Test passing linestyle kwarg."""
        ax, df = plot_shaded_line(
            self.ax,
            self.x,
            self.y_lower,
            self.y_middle,
            self.y_upper,
            linestyle='--'
        )
        
        line = self.ax.lines[0]
        assert line.get_linestyle() == '--'
    
    def test_linewidth_kwarg(self):
        """Test passing linewidth kwarg."""
        ax, df = plot_shaded_line(
            self.ax,
            self.x,
            self.y_lower,
            self.y_middle,
            self.y_upper,
            linewidth=3
        )
        
        line = self.ax.lines[0]
        assert line.get_linewidth() == 3
    
    def test_marker_kwarg(self):
        """Test passing marker kwarg."""
        # Use fewer points for marker visibility
        x = np.linspace(0, 10, 10)
        y_middle = np.sin(x)
        y_lower = y_middle - 0.2
        y_upper = y_middle + 0.2
        
        ax, df = plot_shaded_line(
            self.ax,
            x,
            y_lower,
            y_middle,
            y_upper,
            marker='o'
        )
        
        line = self.ax.lines[0]
        assert line.get_marker() == 'o'
    
    def test_zorder_kwarg(self):
        """Test passing zorder kwarg."""
        ax, df = plot_shaded_line(
            self.ax,
            self.x,
            self.y_lower,
            self.y_middle,
            self.y_upper,
            zorder=10
        )
        
        line = self.ax.lines[0]
        assert line.get_zorder() == 10
    
    def test_combined_kwargs(self):
        """Test passing multiple kwargs together."""
        ax, df = plot_shaded_line(
            self.ax,
            self.x,
            self.y_lower,
            self.y_middle,
            self.y_upper,
            color='green',
            alpha=0.7,
            linestyle='-.',
            linewidth=2,
            label='Combined test'
        )
        
        line = self.ax.lines[0]
        assert line.get_color() == 'green'
        assert line.get_alpha() == 0.7
        assert line.get_linestyle() == '-.'
        assert line.get_linewidth() == 2
        assert line.get_label() == 'Combined test'


class TestPlotShadedLinePerformance:
    """Test performance aspects of plot_shaded_line."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
    
    def teardown_method(self):
        """Clean up after tests."""
        plt.close('all')
    
    def test_large_dataset(self):
        """Test with large dataset."""
        # Create large dataset
        x = np.linspace(0, 100, 10000)
        y_middle = np.sin(x)
        y_lower = y_middle - 0.2
        y_upper = y_middle + 0.2
        
        ax, df = plot_shaded_line(self.ax, x, y_lower, y_middle, y_upper)
        
        assert len(df) == 10000
        assert len(self.ax.lines) > 0
        assert len(self.ax.collections) > 0
    
    def test_many_lines(self):
        """Test plotting many shaded lines."""
        n_lines = 20
        x = np.linspace(0, 10, 100)
        
        xs = [x for _ in range(n_lines)]
        ys_middle = [np.sin(x + i/2) for i in range(n_lines)]
        ys_lower = [y - 0.1 for y in ys_middle]
        ys_upper = [y + 0.1 for y in ys_middle]
        
        ax, dfs = _plot_shaded_line(
            self.ax,
            xs,
            ys_lower,
            ys_middle,
            ys_upper
        )
        
        assert len(dfs) == n_lines
        assert len(self.ax.lines) == n_lines
        assert len(self.ax.collections) == n_lines


if __name__ == "__main__":
    pytest.main([__file__, "-v"])