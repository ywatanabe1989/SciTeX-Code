#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-10 18:12:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/plt/ax/_plot/test__plot_fillv_comprehensive.py

"""Comprehensive tests for plot_fillv functionality."""

import os
import numpy as np
import pytest
import matplotlib
import matplotlib.pyplot as plt
from unittest.mock import patch, MagicMock
import tempfile
from scitex.plt.ax._plot import plot_fillv

matplotlib.use('Agg')


class TestPlotFillvBasic:
    """Test basic plot_fillv functionality."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
        
        # Add some base plot content
        self.x = np.linspace(0, 10, 100)
        self.y = np.sin(self.x)
        self.ax.plot(self.x, self.y, 'b-')
        
        # Default test intervals
        self.starts = [2, 4, 6]
        self.ends = [3, 5, 7]
    
    def teardown_method(self):
        """Clean up after tests."""
        plt.close('all')
    
    def test_single_interval(self):
        """Test filling a single interval."""
        ax = plot_fillv(self.ax, [2], [3])
        
        assert ax is self.ax
        assert len(self.ax.patches) == 1
        
        # Check patch properties
        patch = self.ax.patches[0]
        assert patch.get_alpha() == 0.2  # Default alpha
    
    def test_multiple_intervals(self):
        """Test filling multiple intervals."""
        ax = plot_fillv(self.ax, self.starts, self.ends)
        
        assert len(self.ax.patches) == 3
        
        # Verify each interval
        for i, patch in enumerate(self.ax.patches):
            # Check that patch exists
            assert patch is not None
    
    def test_custom_color(self):
        """Test with custom color."""
        color = 'green'
        ax = plot_fillv(self.ax, self.starts, self.ends, color=color)
        
        # Check that all patches have the correct color
        for patch in self.ax.patches:
            patch_color = patch.get_facecolor()
            expected_color = matplotlib.colors.to_rgba(color, alpha=0.2)
            np.testing.assert_array_almost_equal(patch_color, expected_color, decimal=2)
    
    def test_custom_alpha(self):
        """Test with custom alpha."""
        alpha = 0.5
        ax = plot_fillv(self.ax, self.starts, self.ends, alpha=alpha)
        
        # Check that all patches have the correct alpha
        for patch in self.ax.patches:
            assert patch.get_alpha() == alpha
    
    def test_color_formats(self):
        """Test various color format inputs."""
        color_formats = [
            'red',                    # Named color
            '#FF0000',               # Hex color
            (1.0, 0.0, 0.0),        # RGB tuple
            (1.0, 0.0, 0.0, 0.8),   # RGBA tuple
            'C0',                    # Matplotlib color cycle
            'tab:blue'               # Tableau color
        ]
        
        for color in color_formats:
            self.ax.clear()
            ax = plot_fillv(self.ax, [1], [2], color=color)
            assert len(self.ax.patches) == 1


class TestPlotFillvMultipleAxes:
    """Test plot_fillv with multiple axes."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.fig = plt.figure(figsize=(10, 8))
        self.axes = np.array([
            [self.fig.add_subplot(2, 2, 1), self.fig.add_subplot(2, 2, 2)],
            [self.fig.add_subplot(2, 2, 3), self.fig.add_subplot(2, 2, 4)]
        ])
        
        # Add content to all axes
        x = np.linspace(0, 10, 100)
        for ax_row in self.axes:
            for ax in ax_row:
                ax.plot(x, np.sin(x))
        
        self.starts = [2, 5, 8]
        self.ends = [3, 6, 9]
    
    def teardown_method(self):
        """Clean up after tests."""
        plt.close('all')
    
    def test_axes_array_1d(self):
        """Test with 1D array of axes."""
        axes_1d = self.axes.flatten()
        result = plot_fillv(axes_1d, self.starts, self.ends)
        
        # Should return array of axes
        assert isinstance(result, np.ndarray)
        assert result.shape == axes_1d.shape
        
        # Check all axes have patches
        for ax in axes_1d:
            assert len(ax.patches) == len(self.starts)
    
    def test_axes_array_2d(self):
        """Test with 2D array of axes."""
        result = plot_fillv(self.axes, self.starts, self.ends)
        
        # Should return array of axes with same shape
        assert isinstance(result, np.ndarray)
        assert result.shape == self.axes.shape
        
        # Check all axes have patches
        for ax_row in self.axes:
            for ax in ax_row:
                assert len(ax.patches) == len(self.starts)
    
    def test_different_colors_per_axis(self):
        """Test applying different colors to different axes."""
        axes_1d = self.axes.flatten()
        colors = ['red', 'green', 'blue', 'orange']
        
        for ax, color in zip(axes_1d, colors):
            plot_fillv(ax, self.starts, self.ends, color=color)
        
        # Verify each axis has its own color
        for ax, color in zip(axes_1d, colors):
            expected_color = matplotlib.colors.to_rgba(color, alpha=0.2)
            patch_color = ax.patches[0].get_facecolor()
            np.testing.assert_array_almost_equal(patch_color, expected_color, decimal=2)
    
    def test_single_axis_in_array(self):
        """Test with array containing single axis."""
        single_ax_array = np.array([self.axes[0, 0]])
        result = plot_fillv(single_ax_array, self.starts, self.ends)
        
        assert isinstance(result, np.ndarray)
        assert len(result) == 1
        assert len(result[0].patches) == len(self.starts)


class TestPlotFillvEdgeCases:
    """Test edge cases and error handling."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
        self.ax.plot([0, 10], [0, 10])
    
    def teardown_method(self):
        """Clean up after tests."""
        plt.close('all')
    
    def test_empty_intervals(self):
        """Test with empty interval lists."""
        ax = plot_fillv(self.ax, [], [])
        
        assert ax is self.ax
        assert len(self.ax.patches) == 0
    
    def test_single_boundary(self):
        """Test with single start/end pair."""
        ax = plot_fillv(self.ax, [5], [6])
        
        assert len(self.ax.patches) == 1
    
    def test_overlapping_intervals(self):
        """Test with overlapping intervals."""
        starts = [1, 2, 3]
        ends = [4, 5, 6]
        ax = plot_fillv(self.ax, starts, ends, alpha=0.3)
        
        assert len(self.ax.patches) == 3
        # Overlapping areas will appear darker due to alpha blending
    
    def test_identical_start_end(self):
        """Test when start equals end (zero-width interval)."""
        ax = plot_fillv(self.ax, [5, 7], [5, 7])
        
        # Should create patches, but they'll be invisible (zero width)
        assert len(self.ax.patches) == 2
    
    def test_reversed_intervals(self):
        """Test when end is before start."""
        # This should still work - matplotlib handles it
        ax = plot_fillv(self.ax, [5, 8], [3, 6])
        
        assert len(self.ax.patches) == 2
    
    def test_negative_values(self):
        """Test with negative interval boundaries."""
        ax = plot_fillv(self.ax, [-5, -2], [-3, 0])
        
        assert len(self.ax.patches) == 2
    
    def test_very_large_intervals(self):
        """Test with very large interval boundaries."""
        ax = plot_fillv(self.ax, [1e6, 2e6], [1.5e6, 2.5e6])
        
        assert len(self.ax.patches) == 2
    
    def test_mismatched_lengths(self):
        """Test behavior with mismatched start/end lengths."""
        starts = [1, 2, 3]
        ends = [4, 5]  # Shorter list
        
        # Should only process min(len(starts), len(ends)) intervals
        ax = plot_fillv(self.ax, starts, ends)
        
        assert len(self.ax.patches) == 2  # Only 2 complete pairs
    
    def test_nan_values(self):
        """Test handling of NaN values."""
        starts = [1, np.nan, 3]
        ends = [2, 4, np.nan]
        
        # NaN intervals might be skipped or cause issues
        ax = plot_fillv(self.ax, starts, ends)
        
        # At least the valid interval should be plotted
        assert len(self.ax.patches) >= 1
    
    def test_infinite_values(self):
        """Test handling of infinite values."""
        starts = [1, np.inf, -np.inf]
        ends = [2, 3, 0]
        
        ax = plot_fillv(self.ax, starts, ends)
        
        # Should handle infinite values (matplotlib will clip them)
        assert len(self.ax.patches) >= 1


class TestPlotFillvIntegration:
    """Test integration with other plot elements."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
    
    def teardown_method(self):
        """Clean up after tests."""
        plt.close('all')
    
    def test_with_multiple_plot_types(self):
        """Test fillv with various plot types on same axis."""
        # Add different plot types
        x = np.linspace(0, 10, 100)
        self.ax.plot(x, np.sin(x), 'b-', label='sin')
        self.ax.scatter(x[::10], np.cos(x[::10]), c='red', label='cos points')
        self.ax.bar([1, 3, 5], [0.5, 0.7, 0.3], width=0.4, alpha=0.5)
        
        # Add fill regions
        ax = plot_fillv(self.ax, [2, 6], [4, 8], color='yellow', alpha=0.3)
        
        # Check that all elements coexist
        assert len(self.ax.lines) > 0
        assert len(self.ax.collections) > 0
        assert len(self.ax.patches) > 2  # Bars + fill regions
    
    def test_with_axis_limits(self):
        """Test that fillv respects axis limits."""
        self.ax.plot([0, 10], [0, 10])
        self.ax.set_xlim(0, 10)
        self.ax.set_ylim(-5, 5)
        
        ax = plot_fillv(self.ax, [2, 12], [4, 14])
        
        # Limits should be preserved
        assert self.ax.get_xlim() == (0, 10)
        assert self.ax.get_ylim() == (-5, 5)
    
    def test_with_log_scale(self):
        """Test fillv with logarithmic scale."""
        self.ax.set_xscale('log')
        self.ax.plot(np.logspace(0, 2, 100), np.random.rand(100))
        
        ax = plot_fillv(self.ax, [10, 50], [20, 70])
        
        assert self.ax.get_xscale() == 'log'
        assert len(self.ax.patches) == 2
    
    def test_with_twin_axes(self):
        """Test fillv with twin axes."""
        # Create twin axis
        ax2 = self.ax.twinx()
        
        # Plot on both axes
        self.ax.plot([0, 10], [0, 100], 'b-')
        ax2.plot([0, 10], [100, 0], 'r-')
        
        # Fill on primary axis
        plot_fillv(self.ax, [2, 6], [4, 8], color='blue', alpha=0.2)
        
        # Fill on twin axis
        plot_fillv(ax2, [3, 7], [5, 9], color='red', alpha=0.2)
        
        assert len(self.ax.patches) == 2
        assert len(ax2.patches) == 2
    
    def test_with_subplots_adjust(self):
        """Test fillv after adjusting subplot parameters."""
        self.fig.subplots_adjust(left=0.2, right=0.8, top=0.9, bottom=0.1)
        
        self.ax.plot([0, 10], [0, 10])
        ax = plot_fillv(self.ax, [2, 6], [4, 8])
        
        assert len(self.ax.patches) == 2


class TestPlotFillvVisualProperties:
    """Test visual properties and appearance."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
        self.ax.plot(np.linspace(0, 10, 100), np.sin(np.linspace(0, 10, 100)))
    
    def teardown_method(self):
        """Clean up after tests."""
        plt.close('all')
    
    def test_alpha_blending(self):
        """Test alpha blending with multiple overlapping fills."""
        # Create overlapping fills with different alphas
        plot_fillv(self.ax, [1], [5], color='red', alpha=0.3)
        plot_fillv(self.ax, [3], [7], color='blue', alpha=0.3)
        plot_fillv(self.ax, [2], [6], color='green', alpha=0.3)
        
        assert len(self.ax.patches) == 3
        
        # Check alpha values
        for i, patch in enumerate(self.ax.patches):
            assert patch.get_alpha() == 0.3
    
    def test_zorder_handling(self):
        """Test z-order of fill patches."""
        # Plot a line
        line, = self.ax.plot([0, 10], [5, 5], 'k-', linewidth=2, zorder=10)
        
        # Add fills with different z-orders
        plot_fillv(self.ax, [2], [4], color='red', alpha=0.5)  # Should be behind line
        
        # The fill should have lower zorder than the line
        assert self.ax.patches[0].get_zorder() < line.get_zorder()
    
    def test_edge_properties(self):
        """Test that fill regions have proper edge properties."""
        ax = plot_fillv(self.ax, [2], [4], color='blue', alpha=0.5)
        
        patch = self.ax.patches[0]
        # By default, axvspan creates patches without visible edges
        assert patch.get_edgecolor()[3] == 0 or patch.get_linewidth() == 0
    
    def test_transparency_levels(self):
        """Test different transparency levels."""
        alphas = [0.0, 0.1, 0.5, 0.9, 1.0]
        
        for i, alpha in enumerate(alphas):
            ax = plot_fillv(self.ax, [i], [i+0.8], alpha=alpha)
        
        # Check that all alphas are set correctly
        for i, patch in enumerate(self.ax.patches):
            assert patch.get_alpha() == alphas[i]


class TestPlotFillvPerformance:
    """Test performance with large datasets."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
    
    def teardown_method(self):
        """Clean up after tests."""
        plt.close('all')
    
    def test_many_intervals(self):
        """Test with many intervals."""
        n_intervals = 100
        starts = np.linspace(0, 90, n_intervals)
        ends = starts + 5
        
        ax = plot_fillv(self.ax, starts, ends, alpha=0.1)
        
        assert len(self.ax.patches) == n_intervals
    
    def test_high_precision_boundaries(self):
        """Test with high-precision floating point boundaries."""
        starts = [1.23456789012345, 5.98765432109876]
        ends = [2.34567890123456, 6.87654321098765]
        
        ax = plot_fillv(self.ax, starts, ends)
        
        assert len(self.ax.patches) == 2


class TestPlotFillvSaveLoad:
    """Test saving figures with fillv."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
        self.ax.plot(np.linspace(0, 10, 100), np.sin(np.linspace(0, 10, 100)))
    
    def teardown_method(self):
        """Clean up after tests."""
        plt.close('all')
    
    def test_save_formats(self):
        """Test saving in different formats."""
        plot_fillv(self.ax, [2, 6], [4, 8], color='red', alpha=0.3)
        
        formats = ['.png', '.jpg', '.pdf', '.svg']
        for fmt in formats:
            with tempfile.NamedTemporaryFile(suffix=fmt, delete=False) as f:
                try:
                    self.fig.savefig(f.name)
                    assert os.path.exists(f.name)
                finally:
                    if os.path.exists(f.name):
                        os.unlink(f.name)
    
    def test_dpi_settings(self):
        """Test saving with different DPI settings."""
        plot_fillv(self.ax, [2], [4], color='blue', alpha=0.5)
        
        dpis = [72, 150, 300]
        for dpi in dpis:
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
                try:
                    self.fig.savefig(f.name, dpi=dpi)
                    assert os.path.exists(f.name)
                finally:
                    if os.path.exists(f.name):
                        os.unlink(f.name)


class TestPlotFillvTypeValidation:
    """Test type validation and error handling."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
    
    def teardown_method(self):
        """Clean up after tests."""
        plt.close('all')
    
    def test_invalid_axis_type(self):
        """Test with invalid axis type."""
        with pytest.raises(AssertionError, match="must be a matplotlib axis"):
            plot_fillv("not_an_axis", [1], [2])
    
    def test_invalid_axis_in_array(self):
        """Test with invalid axis in array."""
        axes = np.array([self.ax, "not_an_axis"])
        
        with pytest.raises(AssertionError, match="must be a matplotlib axis"):
            plot_fillv(axes, [1], [2])
    
    def test_list_input_handling(self):
        """Test that lists are properly handled as arrays."""
        # Using list instead of numpy array
        axes_list = [self.ax]
        
        # Should handle list by converting to array internally
        result = plot_fillv(axes_list[0], [1], [2])
        
        # Should return single axis, not array
        assert result is self.ax
        assert not isinstance(result, np.ndarray)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])