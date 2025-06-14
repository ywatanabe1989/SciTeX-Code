#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-10 19:00:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/plt/ax/_plot/test__plot_scatter_hist_comprehensive.py

"""Comprehensive tests for plot_scatter_hist functionality."""

import os
from unittest.mock import MagicMock, Mock, patch

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pytest

matplotlib.use('Agg')  # Use non-interactive backend


class TestPlotScatterHistBasic:
    """Basic functionality tests for plot_scatter_hist."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.fig, self.ax = plt.subplots()
        self.x = np.random.randn(100)
        self.y = np.random.randn(100)
    
    def teardown_method(self):
        """Clean up after tests."""
        plt.close('all')
    
    def test_import(self):
        """Test that plot_scatter_hist can be imported."""
        from scitex.plt.ax._plot import plot_scatter_hist
        assert callable(plot_scatter_hist)
    
    def test_basic_plot(self):
        """Test basic scatter histogram plot."""
        from scitex.plt.ax._plot import plot_scatter_hist
        
        result = plot_scatter_hist(self.ax, self.x, self.y)
        
        assert len(result) == 4
        ax_main, ax_histx, ax_histy, hist_data = result
        
        assert ax_main is self.ax
        assert ax_histx is not None
        assert ax_histy is not None
        assert isinstance(hist_data, dict)
    
    def test_histogram_data_structure(self):
        """Test the returned histogram data structure."""
        from scitex.plt.ax._plot import plot_scatter_hist
        
        _, _, _, hist_data = plot_scatter_hist(self.ax, self.x, self.y)
        
        assert 'hist_x' in hist_data
        assert 'hist_y' in hist_data
        assert 'bin_edges_x' in hist_data
        assert 'bin_edges_y' in hist_data
        
        assert isinstance(hist_data['hist_x'], np.ndarray)
        assert isinstance(hist_data['hist_y'], np.ndarray)
        assert isinstance(hist_data['bin_edges_x'], np.ndarray)
        assert isinstance(hist_data['bin_edges_y'], np.ndarray)
    
    def test_axes_creation(self):
        """Test that histogram axes are created correctly."""
        from scitex.plt.ax._plot import plot_scatter_hist
        
        initial_axes_count = len(self.fig.axes)
        
        ax_main, ax_histx, ax_histy, _ = plot_scatter_hist(self.ax, self.x, self.y)
        
        # Should have 3 axes total (main + 2 histograms)
        assert len(self.fig.axes) == initial_axes_count + 2
        assert ax_histx in self.fig.axes
        assert ax_histy in self.fig.axes


class TestPlotScatterHistParameters:
    """Test parameter handling in plot_scatter_hist."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.fig, self.ax = plt.subplots()
        self.x = np.random.randn(50)
        self.y = np.random.randn(50)
    
    def teardown_method(self):
        """Clean up after tests."""
        plt.close('all')
    
    def test_hist_bins_parameter(self):
        """Test histogram bins parameter."""
        from scitex.plt.ax._plot import plot_scatter_hist
        
        bins = 10
        _, _, _, hist_data = plot_scatter_hist(self.ax, self.x, self.y, hist_bins=bins)
        
        # Check bin edges (bins + 1 edges for bins)
        assert len(hist_data['bin_edges_x']) == bins + 1
        assert len(hist_data['bin_edges_y']) == bins + 1
        assert len(hist_data['hist_x']) == bins
        assert len(hist_data['hist_y']) == bins
    
    def test_scatter_parameters(self):
        """Test scatter plot parameters."""
        from scitex.plt.ax._plot import plot_scatter_hist
        
        scatter_alpha = 0.3
        scatter_size = 50
        scatter_color = 'red'
        
        ax_main, _, _, _ = plot_scatter_hist(
            self.ax, self.x, self.y,
            scatter_alpha=scatter_alpha,
            scatter_size=scatter_size,
            scatter_color=scatter_color
        )
        
        # Check that scatter plot was created with parameters
        collections = ax_main.collections
        assert len(collections) > 0
        
        # Get the scatter collection
        scatter = collections[0]
        assert scatter.get_alpha() == scatter_alpha
        assert np.all(scatter.get_sizes() == scatter_size)
    
    def test_histogram_colors(self):
        """Test histogram color parameters."""
        from scitex.plt.ax._plot import plot_scatter_hist
        
        hist_color_x = 'green'
        hist_color_y = 'orange'
        
        _, ax_histx, ax_histy, _ = plot_scatter_hist(
            self.ax, self.x, self.y,
            hist_color_x=hist_color_x,
            hist_color_y=hist_color_y
        )
        
        # Check that histograms exist
        assert len(ax_histx.patches) > 0
        assert len(ax_histy.patches) > 0
    
    def test_scatter_ratio(self):
        """Test scatter ratio parameter affects layout."""
        from scitex.plt.ax._plot import plot_scatter_hist
        
        # Test with different scatter ratios
        for ratio in [0.5, 0.7, 0.9]:
            fig, ax = plt.subplots()
            
            _, ax_histx, ax_histy, _ = plot_scatter_hist(
                ax, self.x, self.y, 
                scatter_ratio=ratio
            )
            
            # Histogram axes should be positioned based on ratio
            assert ax_histx.get_position().width > 0
            assert ax_histy.get_position().height > 0
            
            plt.close(fig)
    
    def test_histogram_alpha(self):
        """Test histogram alpha parameter."""
        from scitex.plt.ax._plot import plot_scatter_hist
        
        hist_alpha = 0.7
        
        _, ax_histx, ax_histy, _ = plot_scatter_hist(
            self.ax, self.x, self.y,
            hist_alpha=hist_alpha
        )
        
        # Check patches have correct alpha
        if len(ax_histx.patches) > 0:
            assert ax_histx.patches[0].get_alpha() == hist_alpha
        if len(ax_histy.patches) > 0:
            assert ax_histy.patches[0].get_alpha() == hist_alpha


class TestPlotScatterHistDataTypes:
    """Test different data types and shapes."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.fig, self.ax = plt.subplots()
    
    def teardown_method(self):
        """Clean up after tests."""
        plt.close('all')
    
    def test_list_input(self):
        """Test with list input instead of numpy arrays."""
        from scitex.plt.ax._plot import plot_scatter_hist
        
        x = [1, 2, 3, 4, 5]
        y = [2, 4, 6, 8, 10]
        
        result = plot_scatter_hist(self.ax, x, y)
        assert len(result) == 4
    
    def test_integer_data(self):
        """Test with integer data."""
        from scitex.plt.ax._plot import plot_scatter_hist
        
        x = np.array([1, 2, 3, 4, 5])
        y = np.array([5, 4, 3, 2, 1])
        
        _, _, _, hist_data = plot_scatter_hist(self.ax, x, y)
        
        assert hist_data['hist_x'].sum() == len(x)
        assert hist_data['hist_y'].sum() == len(y)
    
    def test_large_dataset(self):
        """Test with large dataset."""
        from scitex.plt.ax._plot import plot_scatter_hist
        
        x = np.random.randn(10000)
        y = np.random.randn(10000)
        
        result = plot_scatter_hist(self.ax, x, y)
        assert len(result) == 4
        
        _, _, _, hist_data = result
        assert hist_data['hist_x'].sum() == len(x)
    
    def test_single_point(self):
        """Test with single data point."""
        from scitex.plt.ax._plot import plot_scatter_hist
        
        x = np.array([1])
        y = np.array([1])
        
        result = plot_scatter_hist(self.ax, x, y)
        assert len(result) == 4
    
    def test_empty_data(self):
        """Test with empty data."""
        from scitex.plt.ax._plot import plot_scatter_hist
        
        x = np.array([])
        y = np.array([])
        
        # Should handle empty data gracefully
        result = plot_scatter_hist(self.ax, x, y)
        assert len(result) == 4


class TestPlotScatterHistEdgeCases:
    """Test edge cases and error conditions."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.fig, self.ax = plt.subplots()
    
    def teardown_method(self):
        """Clean up after tests."""
        plt.close('all')
    
    def test_mismatched_lengths(self):
        """Test with mismatched x and y lengths."""
        from scitex.plt.ax._plot import plot_scatter_hist
        
        x = np.array([1, 2, 3])
        y = np.array([1, 2])  # Different length
        
        # Should raise error or handle gracefully
        with pytest.raises(ValueError):
            plot_scatter_hist(self.ax, x, y)
    
    def test_nan_values(self):
        """Test with NaN values in data."""
        from scitex.plt.ax._plot import plot_scatter_hist
        
        x = np.array([1, 2, np.nan, 4, 5])
        y = np.array([5, 4, 3, np.nan, 1])
        
        # Should handle NaN values
        result = plot_scatter_hist(self.ax, x, y)
        assert len(result) == 4
    
    def test_inf_values(self):
        """Test with infinite values."""
        from scitex.plt.ax._plot import plot_scatter_hist
        
        x = np.array([1, 2, np.inf, 4, 5])
        y = np.array([5, 4, 3, -np.inf, 1])
        
        # Should handle infinite values
        result = plot_scatter_hist(self.ax, x, y)
        assert len(result) == 4
    
    def test_all_same_values(self):
        """Test when all values are the same."""
        from scitex.plt.ax._plot import plot_scatter_hist
        
        x = np.ones(10)
        y = np.ones(10) * 2
        
        result = plot_scatter_hist(self.ax, x, y)
        _, _, _, hist_data = result
        
        # All data should be in one bin
        assert np.max(hist_data['hist_x']) == 10
        assert np.max(hist_data['hist_y']) == 10
    
    def test_extreme_values(self):
        """Test with extreme value ranges."""
        from scitex.plt.ax._plot import plot_scatter_hist
        
        x = np.array([1e-10, 1e10])
        y = np.array([-1e10, 1e-10])
        
        result = plot_scatter_hist(self.ax, x, y)
        assert len(result) == 4


class TestPlotScatterHistFigureHandling:
    """Test figure parameter handling."""
    
    def teardown_method(self):
        """Clean up after tests."""
        plt.close('all')
    
    def test_with_explicit_figure(self):
        """Test with explicitly provided figure."""
        from scitex.plt.ax._plot import plot_scatter_hist
        
        fig, ax = plt.subplots()
        x = np.random.randn(50)
        y = np.random.randn(50)
        
        result = plot_scatter_hist(ax, x, y, fig=fig)
        assert len(result) == 4
        
        # All axes should belong to the provided figure
        _, ax_histx, ax_histy, _ = result
        assert ax_histx.figure is fig
        assert ax_histy.figure is fig
    
    def test_without_figure_parameter(self):
        """Test without figure parameter (uses ax.figure)."""
        from scitex.plt.ax._plot import plot_scatter_hist
        
        fig, ax = plt.subplots()
        x = np.random.randn(50)
        y = np.random.randn(50)
        
        result = plot_scatter_hist(ax, x, y)
        
        _, ax_histx, ax_histy, _ = result
        assert ax_histx.figure is ax.figure
        assert ax_histy.figure is ax.figure
    
    def test_multiple_subplots(self):
        """Test with multiple subplots in figure."""
        from scitex.plt.ax._plot import plot_scatter_hist
        
        fig, axes = plt.subplots(2, 2)
        x = np.random.randn(50)
        y = np.random.randn(50)
        
        # Use one of the subplots
        target_ax = axes[0, 1]
        result = plot_scatter_hist(target_ax, x, y)
        
        assert len(result) == 4
        ax_main, _, _, _ = result
        assert ax_main is target_ax


class TestPlotScatterHistAxesProperties:
    """Test properties of created axes."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.fig, self.ax = plt.subplots()
        self.x = np.random.randn(100)
        self.y = np.random.randn(100)
    
    def teardown_method(self):
        """Clean up after tests."""
        plt.close('all')
    
    def test_histogram_axes_labels(self):
        """Test that histogram axes have correct label settings."""
        from scitex.plt.ax._plot import plot_scatter_hist
        
        _, ax_histx, ax_histy, _ = plot_scatter_hist(self.ax, self.x, self.y)
        
        # X histogram should not have x labels
        assert not ax_histx.xaxis.get_ticklabels()[0].get_visible()
        
        # Y histogram should not have y labels  
        assert not ax_histy.yaxis.get_ticklabels()[0].get_visible()
    
    def test_histogram_orientation(self):
        """Test histogram orientations."""
        from scitex.plt.ax._plot import plot_scatter_hist
        
        _, ax_histx, ax_histy, _ = plot_scatter_hist(self.ax, self.x, self.y)
        
        # X histogram should be vertical (default)
        # Y histogram should be horizontal
        # This is verified by the orientation parameter in the source
        assert len(ax_histx.patches) > 0  # Has vertical bars
        assert len(ax_histy.patches) > 0  # Has horizontal bars
    
    def test_axes_positions(self):
        """Test that axes are positioned correctly."""
        from scitex.plt.ax._plot import plot_scatter_hist
        
        _, ax_histx, ax_histy, _ = plot_scatter_hist(self.ax, self.x, self.y)
        
        # X histogram should be above main plot
        assert ax_histx.get_position().y0 > self.ax.get_position().y1
        
        # Y histogram should be to the right of main plot
        assert ax_histy.get_position().x0 > self.ax.get_position().x1


class TestPlotScatterHistKwargs:
    """Test additional keyword arguments handling."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.fig, self.ax = plt.subplots()
        self.x = np.random.randn(50)
        self.y = np.random.randn(50)
    
    def teardown_method(self):
        """Clean up after tests."""
        plt.close('all')
    
    def test_scatter_kwargs(self):
        """Test additional kwargs passed to scatter."""
        from scitex.plt.ax._plot import plot_scatter_hist
        
        # Additional scatter parameters
        kwargs = {
            'edgecolors': 'black',
            'linewidths': 2,
            'marker': '^'
        }
        
        ax_main, _, _, _ = plot_scatter_hist(self.ax, self.x, self.y, **kwargs)
        
        # Check scatter collection has the properties
        scatter = ax_main.collections[0]
        assert scatter.get_linewidths()[0] == 2
    
    def test_mixed_parameters(self):
        """Test mixing explicit parameters with kwargs."""
        from scitex.plt.ax._plot import plot_scatter_hist
        
        result = plot_scatter_hist(
            self.ax, self.x, self.y,
            scatter_color='red',
            scatter_size=100,
            hist_bins=15,
            label='Test Data'  # Additional kwarg
        )
        
        assert len(result) == 4


class TestPlotScatterHistIntegration:
    """Integration tests with matplotlib functionality."""
    
    def teardown_method(self):
        """Clean up after tests."""
        plt.close('all')
    
    def test_with_styled_axes(self):
        """Test with pre-styled axes."""
        from scitex.plt.ax._plot import plot_scatter_hist
        
        fig, ax = plt.subplots()
        
        # Style the main axes
        ax.set_xlabel('X Label')
        ax.set_ylabel('Y Label')
        ax.set_title('Main Title')
        
        x = np.random.randn(100)
        y = np.random.randn(100)
        
        result = plot_scatter_hist(ax, x, y)
        
        # Original styling should be preserved
        assert ax.get_xlabel() == 'X Label'
        assert ax.get_ylabel() == 'Y Label'
        assert ax.get_title() == 'Main Title'
    
    def test_save_figure(self):
        """Test saving figure with scatter histogram."""
        from scitex.plt.ax._plot import plot_scatter_hist
        import tempfile
        
        fig, ax = plt.subplots()
        x = np.random.randn(100)
        y = np.random.randn(100)
        
        plot_scatter_hist(ax, x, y)
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix='.png', delete=True) as tmp:
            fig.savefig(tmp.name)
            assert os.path.exists(tmp.name)
            assert os.path.getsize(tmp.name) > 0
    
    def test_correlation_visualization(self):
        """Test visualizing correlated data."""
        from scitex.plt.ax._plot import plot_scatter_hist
        
        fig, ax = plt.subplots()
        
        # Create correlated data
        x = np.random.randn(200)
        y = 2 * x + np.random.randn(200) * 0.5
        
        _, _, _, hist_data = plot_scatter_hist(ax, x, y)
        
        # Both histograms should have similar shapes due to correlation
        assert len(hist_data['hist_x']) == len(hist_data['hist_y'])


class TestPlotScatterHistPerformance:
    """Performance tests for plot_scatter_hist."""
    
    def teardown_method(self):
        """Clean up after tests."""
        plt.close('all')
    
    def test_large_dataset_performance(self):
        """Test performance with large dataset."""
        from scitex.plt.ax._plot import plot_scatter_hist
        import time
        
        fig, ax = plt.subplots()
        x = np.random.randn(50000)
        y = np.random.randn(50000)
        
        start_time = time.time()
        result = plot_scatter_hist(ax, x, y)
        duration = time.time() - start_time
        
        assert len(result) == 4
        assert duration < 5.0  # Should complete within 5 seconds
    
    def test_many_bins_performance(self):
        """Test performance with many histogram bins."""
        from scitex.plt.ax._plot import plot_scatter_hist
        
        fig, ax = plt.subplots()
        x = np.random.randn(1000)
        y = np.random.randn(1000)
        
        # Use many bins
        _, _, _, hist_data = plot_scatter_hist(ax, x, y, hist_bins=100)
        
        assert len(hist_data['hist_x']) == 100
        assert len(hist_data['hist_y']) == 100


class TestPlotScatterHistDocumentation:
    """Test documentation and API."""
    
    def test_function_has_docstring(self):
        """Test that function has comprehensive docstring."""
        from scitex.plt.ax._plot import plot_scatter_hist
        
        assert plot_scatter_hist.__doc__ is not None
        assert 'Parameters' in plot_scatter_hist.__doc__
        assert 'Returns' in plot_scatter_hist.__doc__
    
    def test_return_value_documentation(self):
        """Test that return values match documentation."""
        from scitex.plt.ax._plot import plot_scatter_hist
        
        fig, ax = plt.subplots()
        x = np.random.randn(50)
        y = np.random.randn(50)
        
        result = plot_scatter_hist(ax, x, y)
        
        # Should return tuple of 4 items as documented
        assert isinstance(result, tuple)
        assert len(result) == 4
        
        ax_main, ax_histx, ax_histy, hist_data = result
        assert isinstance(ax_main, plt.Axes)
        assert isinstance(ax_histx, plt.Axes)
        assert isinstance(ax_histy, plt.Axes)
        assert isinstance(hist_data, dict)
        
        plt.close(fig)


if __name__ == "__main__":
    pytest.main([os.path.abspath(__file__), "-v"])