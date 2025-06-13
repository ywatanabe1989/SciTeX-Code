#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-10 18:08:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/plt/ax/_plot/test__plot_violin_comprehensive.py

"""Comprehensive tests for violin plot functionality."""

import os
import numpy as np
import pandas as pd
import pytest
import matplotlib.pyplot as plt
import seaborn as sns
from unittest.mock import patch, MagicMock
import tempfile
from scitex.plt.ax._plot import plot_violin, sns_plot_violin


class TestPlotViolinBasic:
    """Test basic violin plot functionality."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
        
        # Create sample data
        np.random.seed(42)
        self.data_size = 100
        self.data_list = [
            np.random.normal(0, 1, self.data_size),
            np.random.normal(3, 1.2, self.data_size),
            np.random.normal(5, 0.8, self.data_size)
        ]
        self.labels = ['Group A', 'Group B', 'Group C']
        
        # Create DataFrame format data
        self.df = pd.DataFrame({
            'value': np.concatenate(self.data_list),
            'group': np.repeat(self.labels, self.data_size)
        })
    
    def teardown_method(self):
        """Clean up after tests."""
        plt.close('all')
    
    def test_basic_violin_plot(self):
        """Test basic violin plot with data list."""
        ax = plot_violin(self.ax, self.data_list)
        
        assert ax is self.ax
        assert len(ax.collections) > 0  # Violin collections created
    
    def test_violin_plot_with_labels(self):
        """Test violin plot with custom labels."""
        ax = plot_violin(self.ax, self.data_list, labels=self.labels)
        
        # Check that labels are set correctly
        x_labels = [tick.get_text() for tick in ax.get_xticklabels()]
        for label in self.labels:
            assert label in x_labels
    
    def test_violin_plot_with_colors(self):
        """Test violin plot with custom colors."""
        colors = ['red', 'green', 'blue']
        ax = plot_violin(self.ax, self.data_list, labels=self.labels, colors=colors)
        
        assert len(ax.collections) > 0
    
    def test_half_violin_plot(self):
        """Test half violin plot."""
        ax = plot_violin(self.ax, self.data_list, labels=self.labels, half=True)
        
        assert len(ax.collections) > 0
    
    def test_empty_data_list(self):
        """Test with empty data list."""
        ax = plot_violin(self.ax, [])
        
        assert ax is self.ax
        # Should handle empty data gracefully
    
    def test_single_group(self):
        """Test with single group."""
        ax = plot_violin(self.ax, [self.data_list[0]], labels=['Single Group'])
        
        assert len(ax.collections) > 0
    
    def test_different_data_sizes(self):
        """Test with groups of different sizes."""
        data_list = [
            np.random.normal(0, 1, 50),
            np.random.normal(2, 1, 100),
            np.random.normal(4, 1, 150)
        ]
        ax = plot_violin(self.ax, data_list)
        
        assert len(ax.collections) > 0


class TestSnsPlotViolin:
    """Test seaborn-based violin plot functionality."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
        
        # Create sample DataFrame
        np.random.seed(42)
        self.df = pd.DataFrame({
            'x': np.repeat(['A', 'B', 'C'], 100),
            'y': np.concatenate([
                np.random.normal(0, 1, 100),
                np.random.normal(2, 1.2, 100),
                np.random.normal(4, 0.8, 100)
            ]),
            'hue': np.tile(['Type1', 'Type2'], 150)
        })
    
    def teardown_method(self):
        """Clean up after tests."""
        plt.close('all')
    
    def test_sns_violin_basic(self):
        """Test basic seaborn violin plot."""
        ax = sns_plot_violin(self.ax, data=self.df, x='x', y='y')
        
        assert ax is self.ax
        assert len(ax.collections) > 0
    
    def test_sns_violin_with_hue(self):
        """Test seaborn violin plot with hue."""
        ax = sns_plot_violin(self.ax, data=self.df, x='x', y='y', hue='hue')
        
        assert ax is self.ax
        assert len(ax.collections) > 0
        # Should have legend with hue categories
        if ax.legend_:
            legend_texts = [t.get_text() for t in ax.legend_.get_texts()]
            assert 'Type1' in legend_texts or 'Type2' in legend_texts
    
    def test_sns_violin_half_mode(self):
        """Test half violin plot mode."""
        ax = sns_plot_violin(self.ax, data=self.df, x='x', y='y', half=True)
        
        assert ax is self.ax
        assert len(ax.collections) > 0
    
    def test_sns_violin_with_palette(self):
        """Test violin plot with custom palette."""
        palette = {'A': 'red', 'B': 'green', 'C': 'blue'}
        ax = sns_plot_violin(self.ax, data=self.df, x='x', y='y', palette=palette)
        
        assert len(ax.collections) > 0
    
    def test_sns_violin_with_kwargs(self):
        """Test passing additional kwargs to seaborn."""
        ax = sns_plot_violin(
            self.ax, 
            data=self.df, 
            x='x', 
            y='y',
            inner='quartile',
            scale='count',
            cut=2
        )
        
        assert len(ax.collections) > 0


class TestPlotViolinEdgeCases:
    """Test edge cases and error handling."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
    
    def teardown_method(self):
        """Clean up after tests."""
        plt.close('all')
    
    def test_nan_values(self):
        """Test handling of NaN values."""
        data_with_nan = [
            np.array([1, 2, np.nan, 4, 5]),
            np.array([np.nan, 2, 3, 4, np.nan])
        ]
        
        ax = plot_violin(self.ax, data_with_nan)
        assert len(ax.collections) > 0
    
    def test_infinite_values(self):
        """Test handling of infinite values."""
        data_with_inf = [
            np.array([1, 2, np.inf, 4, 5]),
            np.array([-np.inf, 2, 3, 4, 5])
        ]
        
        # Should handle or filter infinite values
        ax = plot_violin(self.ax, data_with_inf)
        assert ax is self.ax
    
    def test_all_same_values(self):
        """Test when all values in a group are the same."""
        data_same = [
            np.ones(50) * 5,
            np.ones(50) * 10
        ]
        
        ax = plot_violin(self.ax, data_same)
        assert len(ax.collections) > 0
    
    def test_very_small_dataset(self):
        """Test with very small datasets."""
        small_data = [
            np.array([1, 2]),
            np.array([3, 4])
        ]
        
        ax = plot_violin(self.ax, small_data)
        assert ax is self.ax
    
    def test_mixed_data_types(self):
        """Test with mixed numeric types."""
        mixed_data = [
            np.array([1, 2, 3], dtype=int),
            np.array([4.5, 5.5, 6.5], dtype=float)
        ]
        
        ax = plot_violin(self.ax, mixed_data)
        assert len(ax.collections) > 0
    
    def test_extreme_values(self):
        """Test with extreme value ranges."""
        extreme_data = [
            np.array([1e-10, 2e-10, 3e-10]),
            np.array([1e10, 2e10, 3e10])
        ]
        
        ax = plot_violin(self.ax, extreme_data)
        assert ax is self.ax


class TestPlotViolinColors:
    """Test color handling in violin plots."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
        self.data_list = [
            np.random.normal(0, 1, 100),
            np.random.normal(2, 1, 100),
            np.random.normal(4, 1, 100)
        ]
    
    def teardown_method(self):
        """Clean up after tests."""
        plt.close('all')
    
    def test_color_list(self):
        """Test with list of colors."""
        colors = ['red', 'green', 'blue']
        ax = plot_violin(self.ax, self.data_list, colors=colors)
        
        assert len(ax.collections) > 0
    
    def test_color_dict(self):
        """Test with dictionary of colors."""
        labels = ['A', 'B', 'C']
        colors = {'A': 'red', 'B': 'green', 'C': 'blue'}
        ax = plot_violin(self.ax, self.data_list, labels=labels, colors=colors)
        
        assert len(ax.collections) > 0
    
    def test_hex_colors(self):
        """Test with hex color codes."""
        colors = ['#FF0000', '#00FF00', '#0000FF']
        ax = plot_violin(self.ax, self.data_list, colors=colors)
        
        assert len(ax.collections) > 0
    
    def test_rgb_tuples(self):
        """Test with RGB tuple colors."""
        colors = [(1, 0, 0), (0, 1, 0), (0, 0, 1)]
        ax = plot_violin(self.ax, self.data_list, colors=colors)
        
        assert len(ax.collections) > 0
    
    def test_colormap_name(self):
        """Test with colormap name."""
        ax = plot_violin(self.ax, self.data_list, colors='viridis')
        
        assert len(ax.collections) > 0
    
    def test_insufficient_colors(self):
        """Test when fewer colors than groups."""
        colors = ['red', 'green']  # Only 2 colors for 3 groups
        ax = plot_violin(self.ax, self.data_list, colors=colors)
        
        assert len(ax.collections) > 0


class TestPlotViolinStyling:
    """Test styling options for violin plots."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
        self.data_list = [
            np.random.normal(0, 1, 100),
            np.random.normal(2, 1, 100)
        ]
    
    def teardown_method(self):
        """Clean up after tests."""
        plt.close('all')
    
    def test_inner_styles(self):
        """Test different inner visualization styles."""
        inner_styles = ['box', 'quartile', 'point', 'stick', None]
        
        for inner in inner_styles:
            ax = self.ax.clear() or self.ax
            ax = plot_violin(self.ax, self.data_list, inner=inner)
            assert ax is self.ax
    
    def test_scale_options(self):
        """Test different scaling options."""
        scale_options = ['area', 'count', 'width']
        
        for scale in scale_options:
            ax = self.ax.clear() or self.ax
            ax = plot_violin(self.ax, self.data_list, scale=scale)
            assert ax is self.ax
    
    def test_bw_method(self):
        """Test bandwidth calculation methods."""
        bw_methods = ['scott', 'silverman', 0.5]
        
        for bw in bw_methods:
            ax = self.ax.clear() or self.ax
            ax = plot_violin(self.ax, self.data_list, bw=bw)
            assert ax is self.ax
    
    def test_cut_parameter(self):
        """Test cut parameter for extending density past extreme values."""
        cut_values = [0, 1, 2, 3]
        
        for cut in cut_values:
            ax = self.ax.clear() or self.ax
            ax = plot_violin(self.ax, self.data_list, cut=cut)
            assert ax is self.ax
    
    def test_split_violin(self):
        """Test split violin for comparison."""
        # Create data suitable for split violin
        df = pd.DataFrame({
            'x': np.repeat(['A', 'A', 'B', 'B'], 50),
            'y': np.random.normal(0, 1, 200),
            'hue': np.tile(['M', 'F'], 100)
        })
        
        ax = sns_plot_violin(self.ax, data=df, x='x', y='y', hue='hue', split=True)
        assert len(ax.collections) > 0


class TestPlotViolinIntegration:
    """Test integration with other plot elements."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
        self.data_list = [
            np.random.normal(0, 1, 100),
            np.random.normal(2, 1, 100)
        ]
    
    def teardown_method(self):
        """Clean up after tests."""
        plt.close('all')
    
    def test_with_existing_plots(self):
        """Test adding violin plot to axis with existing plots."""
        # Add a line plot first
        self.ax.plot([0, 1, 2], [1, 3, 2], 'k--', label='Line')
        
        # Add violin plot
        ax = plot_violin(self.ax, self.data_list)
        
        # Should have both line and violin elements
        assert len(self.ax.lines) > 0
        assert len(self.ax.collections) > 0
    
    def test_multiple_violin_calls(self):
        """Test multiple violin plot calls on same axis."""
        # First violin plot
        ax = plot_violin(self.ax, [self.data_list[0]], labels=['First'])
        
        # Second violin plot with offset
        self.ax.set_xlim(-0.5, 2.5)
        ax = plot_violin(self.ax, [self.data_list[1]], labels=['Second'])
        
        assert len(self.ax.collections) >= 2
    
    def test_with_axis_labels(self):
        """Test that axis labels are preserved."""
        self.ax.set_xlabel('Groups')
        self.ax.set_ylabel('Values')
        self.ax.set_title('Violin Plot Test')
        
        ax = plot_violin(self.ax, self.data_list)
        
        assert self.ax.get_xlabel() == 'Groups'
        assert self.ax.get_ylabel() == 'Values'
        assert self.ax.get_title() == 'Violin Plot Test'
    
    def test_with_grid(self):
        """Test violin plot with grid enabled."""
        self.ax.grid(True, alpha=0.3)
        
        ax = plot_violin(self.ax, self.data_list)
        
        assert self.ax.xaxis.get_gridlines()[0].get_visible() or \
               self.ax.yaxis.get_gridlines()[0].get_visible()


class TestPlotViolinDataFormats:
    """Test various input data formats."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
    
    def teardown_method(self):
        """Clean up after tests."""
        plt.close('all')
    
    def test_list_of_lists(self):
        """Test with list of lists."""
        data = [
            [1, 2, 3, 4, 5],
            [2, 3, 4, 5, 6],
            [3, 4, 5, 6, 7]
        ]
        ax = plot_violin(self.ax, data)
        assert len(ax.collections) > 0
    
    def test_list_of_arrays(self):
        """Test with list of numpy arrays."""
        data = [
            np.array([1, 2, 3, 4, 5]),
            np.array([2, 3, 4, 5, 6])
        ]
        ax = plot_violin(self.ax, data)
        assert len(ax.collections) > 0
    
    def test_list_of_series(self):
        """Test with list of pandas Series."""
        data = [
            pd.Series([1, 2, 3, 4, 5]),
            pd.Series([2, 3, 4, 5, 6])
        ]
        ax = plot_violin(self.ax, data)
        assert len(ax.collections) > 0
    
    def test_mixed_types(self):
        """Test with mixed data types in list."""
        data = [
            [1, 2, 3],
            np.array([2, 3, 4]),
            pd.Series([3, 4, 5])
        ]
        ax = plot_violin(self.ax, data)
        assert len(ax.collections) > 0


class TestPlotViolinSaveLoad:
    """Test saving and loading violin plots."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
        self.data_list = [
            np.random.normal(0, 1, 100),
            np.random.normal(2, 1, 100)
        ]
    
    def teardown_method(self):
        """Clean up after tests."""
        plt.close('all')
    
    def test_save_figure(self):
        """Test saving figure with violin plot."""
        ax = plot_violin(self.ax, self.data_list, labels=['A', 'B'])
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            self.fig.savefig(f.name)
            assert os.path.exists(f.name)
            os.unlink(f.name)
    
    def test_save_multiple_formats(self):
        """Test saving in different formats."""
        ax = plot_violin(self.ax, self.data_list)
        
        formats = ['.png', '.jpg', '.pdf', '.svg']
        for fmt in formats:
            with tempfile.NamedTemporaryFile(suffix=fmt, delete=False) as f:
                try:
                    self.fig.savefig(f.name)
                    assert os.path.exists(f.name)
                finally:
                    if os.path.exists(f.name):
                        os.unlink(f.name)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])