#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-18 22:05:10 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/_subplots/_export_as_csv_formatters/test_formatters.py
# ----------------------------------------
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import unittest
import numpy as np
import pandas as pd

# Import formatters directly
from ._format_plot import _format_plot
from ._format_plot_kde import _format_plot_kde
from ._format_plot_ecdf import _format_plot_ecdf
from ._format_plot_heatmap import _format_plot_heatmap
from ._format_plot_violin import _format_plot_violin
from ._format_plot_shaded_line import _format_plot_shaded_line
from ._format_plot_scatter_hist import _format_plot_scatter_hist


class FormattersTest(unittest.TestCase):
    """Test the formatter functions."""

    def test_format_plot_kde(self):
        """Test _format_plot_kde function."""
        # Test case 1: Normal input
        tracked_dict = {
            'x': np.linspace(-3, 3, 100),
            'kde': np.exp(-np.linspace(-3, 3, 100)**2/2),
            'n': 500
        }
        id = 'test_kde'
        df = _format_plot_kde(id, tracked_dict, {})
        
        # Verify columns
        self.assertIn(f"{id}_kde_x", df.columns)
        self.assertIn(f"{id}_kde_density", df.columns)
        self.assertIn(f"{id}_kde_n", df.columns)
        
        # Test case 2: Empty tracked_dict
        df = _format_plot_kde(id, {}, {})
        self.assertTrue(df.empty)
        
        # Test case 3: Missing 'x' key
        tracked_dict = {'kde': np.exp(-np.linspace(-3, 3, 100)**2/2)}
        df = _format_plot_kde(id, tracked_dict, {})
        self.assertTrue(df.empty)

    def test_format_plot(self):
        """Test _format_plot function."""
        # Test case 1: Normal input
        tracked_dict = {
            'plot_df': pd.DataFrame({
                'x': np.linspace(0, 10, 100),
                'y': np.sin(np.linspace(0, 10, 100))
            })
        }
        id = 'test_plot'
        df = _format_plot(id, tracked_dict, {})
        
        # Verify it returned the DataFrame with added prefix
        self.assertFalse(df.empty)
        
        # Test case 2: Empty tracked_dict
        df = _format_plot(id, {}, {})
        self.assertTrue(df.empty)

    def test_format_plot_ecdf(self):
        """Test _format_plot_ecdf function."""
        # Test case 1: Normal input
        tracked_dict = {
            'ecdf_df': pd.DataFrame({
                'x': np.linspace(-3, 3, 100),
                'ecdf': np.linspace(0, 1, 100)
            })
        }
        id = 'test_ecdf'
        df = _format_plot_ecdf(id, tracked_dict, {})
        
        # Verify it returned the DataFrame
        self.assertFalse(df.empty)
        
        # Test case 2: Empty tracked_dict
        df = _format_plot_ecdf(id, {}, {})
        self.assertTrue(df.empty)

    def test_format_plot_heatmap(self):
        """Test _format_plot_heatmap function."""
        # Test case 1: Normal input with labels
        data = np.random.rand(3, 4)
        x_labels = ['A', 'B', 'C']
        y_labels = ['W', 'X', 'Y', 'Z']
        
        tracked_dict = {
            'data': data,
            'x_labels': x_labels,
            'y_labels': y_labels
        }
        id = 'test_heatmap'
        df = _format_plot_heatmap(id, tracked_dict, {})
        
        # Verify it returned the DataFrame with the expected shape
        self.assertFalse(df.empty)
        self.assertEqual(df.shape[0], 12)  # 3 rows * 4 columns = 12 cells
        # We should have 5 columns: row, col, value, row_label, col_label
        self.assertEqual(df.shape[1], 5)
        
        # Test case 2: No labels
        tracked_dict = {'data': data}
        df = _format_plot_heatmap(id, tracked_dict, {})
        self.assertFalse(df.empty)
        
        # Test case 3: Empty tracked_dict
        df = _format_plot_heatmap(id, {}, {})
        self.assertTrue(df.empty)

    def test_format_plot_violin(self):
        """Test _format_plot_violin function."""
        # Test case 1: List data
        data = [np.random.normal(0, 1, 100), np.random.normal(2, 1, 100)]
        labels = ['Group A', 'Group B']
        
        tracked_dict = {
            'data': data,
            'labels': labels
        }
        id = 'test_violin'
        df = _format_plot_violin(id, tracked_dict, {})
        
        # Verify it returned the DataFrame
        self.assertFalse(df.empty)
        
        # Test case 2: DataFrame data
        data_df = pd.DataFrame({
            'values': np.concatenate([np.random.normal(0, 1, 100), np.random.normal(2, 1, 100)]),
            'group': ['A'] * 100 + ['B'] * 100
        })
        tracked_dict = {
            'data': data_df,
            'x': 'group',
            'y': 'values'
        }
        df = _format_plot_violin(id, tracked_dict, {})
        self.assertFalse(df.empty)
        
        # Test case 3: Empty tracked_dict
        df = _format_plot_violin(id, {}, {})
        self.assertTrue(df.empty)

    def test_format_plot_shaded_line(self):
        """Test _format_plot_shaded_line function."""
        # Test case 1: Normal input
        tracked_dict = {
            'plot_df': pd.DataFrame({
                'x': np.linspace(0, 10, 100),
                'y_lower': np.sin(np.linspace(0, 10, 100)) - 0.2,
                'y_middle': np.sin(np.linspace(0, 10, 100)),
                'y_upper': np.sin(np.linspace(0, 10, 100)) + 0.2
            })
        }
        id = 'test_shaded'
        df = _format_plot_shaded_line(id, tracked_dict, {})
        
        # Verify it returned the DataFrame
        self.assertFalse(df.empty)
        
        # Test case 2: Empty tracked_dict
        df = _format_plot_shaded_line(id, {}, {})
        self.assertTrue(df.empty)

    def test_format_plot_scatter_hist(self):
        """Test _format_plot_scatter_hist function."""
        # Test case 1: Normal input
        tracked_dict = {
            'x': np.random.normal(0, 1, 100),
            'y': np.random.normal(0, 1, 100),
            'hist_x': np.random.rand(10),
            'hist_y': np.random.rand(10),
            'bin_edges_x': np.linspace(-3, 3, 11),
            'bin_edges_y': np.linspace(-3, 3, 11)
        }
        id = 'test_scatter_hist'
        df = _format_plot_scatter_hist(id, tracked_dict, {})
        
        # Verify it returned the DataFrame with expected columns
        self.assertFalse(df.empty)
        self.assertTrue(any(col.startswith(f"{id}_scatter_hist_x") for col in df.columns))
        self.assertTrue(any(col.startswith(f"{id}_scatter_hist_y") for col in df.columns))
        
        # Test case 2: Missing keys
        tracked_dict = {
            'x': np.random.normal(0, 1, 100),
            'y': np.random.normal(0, 1, 100)
        }
        df = _format_plot_scatter_hist(id, tracked_dict, {})
        self.assertFalse(df.empty)  # Should still work with just x,y
        
        # Test case 3: Empty tracked_dict
        df = _format_plot_scatter_hist(id, {}, {})
        self.assertTrue(df.empty)


if __name__ == '__main__':
    unittest.main()