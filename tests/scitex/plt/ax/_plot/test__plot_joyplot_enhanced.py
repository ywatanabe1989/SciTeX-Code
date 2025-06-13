#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-23 (ywatanabe)"

"""
Comprehensive tests for the enhanced joyplot functionality.
Tests the improved orientation handling and error conditions.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest
from unittest.mock import patch, MagicMock

from scitex.plt.ax._plot import plot_joyplot


class TestPlotJoyplotEnhanced:
    """Enhanced tests for plot_joyplot function."""

    @pytest.fixture
    def sample_data(self):
        """Create sample data for testing."""
        np.random.seed(42)  # For reproducible tests
        return pd.DataFrame({
            'A': np.random.normal(0, 1, 100),
            'B': np.random.normal(1, 1.5, 100),
            'C': np.random.normal(-1, 0.5, 100)
        })

    @pytest.fixture
    def mock_axes(self):
        """Create a mock matplotlib axes."""
        return MagicMock()

    def test_plot_joyplot_vertical_orientation(self, sample_data, mock_axes):
        """Test joyplot with vertical orientation (default)."""
        with patch('scitex.plt.ax._plot._plot_joyplot.joypy.joyplot') as mock_joypy:
            mock_joypy.return_value = (MagicMock(), [mock_axes])
            
            with patch('scitex.plt.ax._plot._plot_joyplot.scitex_plt_set_xyt') as mock_set_xyt:
                mock_set_xyt.return_value = mock_axes
                
                result = plot_joyplot(mock_axes, sample_data, orientation="vertical")
                
                # Verify joypy was called with data
                mock_joypy.assert_called_once()
                call_args = mock_joypy.call_args
                assert call_args[1]['data'] is sample_data
                
                # Verify correct label setting for vertical orientation
                mock_set_xyt.assert_called_once_with(mock_axes, None, "Density", "Joyplot")
                
                assert result is mock_axes

    def test_plot_joyplot_horizontal_orientation(self, sample_data, mock_axes):
        """Test joyplot with horizontal orientation."""
        with patch('scitex.plt.ax._plot._plot_joyplot.joypy.joyplot') as mock_joypy:
            mock_joypy.return_value = (MagicMock(), [mock_axes])
            
            with patch('scitex.plt.ax._plot._plot_joyplot.scitex_plt_set_xyt') as mock_set_xyt:
                mock_set_xyt.return_value = mock_axes
                
                result = plot_joyplot(mock_axes, sample_data, orientation="horizontal")
                
                # Verify joypy was called with data and proper parameters
                mock_joypy.assert_called_once()
                call_args = mock_joypy.call_args
                assert call_args[1]['data'] is sample_data
                assert call_args[1].get('kind') == 'kde'  # Should set default kind for horizontal
                
                # Verify correct label setting for horizontal orientation
                mock_set_xyt.assert_called_once_with(mock_axes, "Density", None, "Joyplot")
                
                assert result is mock_axes

    def test_plot_joyplot_default_orientation(self, sample_data, mock_axes):
        """Test joyplot with default orientation (should be vertical)."""
        with patch('scitex.plt.ax._plot._plot_joyplot.joypy.joyplot') as mock_joypy:
            mock_joypy.return_value = (MagicMock(), [mock_axes])
            
            with patch('scitex.plt.ax._plot._plot_joyplot.scitex_plt_set_xyt') as mock_set_xyt:
                mock_set_xyt.return_value = mock_axes
                
                # Call without specifying orientation
                result = plot_joyplot(mock_axes, sample_data)
                
                # Should default to vertical behavior
                mock_set_xyt.assert_called_once_with(mock_axes, None, "Density", "Joyplot")

    def test_plot_joyplot_invalid_orientation(self, sample_data, mock_axes):
        """Test joyplot with invalid orientation raises ValueError."""
        with pytest.raises(ValueError, match="orientation must be either 'vertical' or 'horizontal'"):
            plot_joyplot(mock_axes, sample_data, orientation="diagonal")

    def test_plot_joyplot_invalid_orientation_none(self, sample_data, mock_axes):
        """Test joyplot with None orientation raises ValueError."""
        with pytest.raises(ValueError, match="orientation must be either 'vertical' or 'horizontal'"):
            plot_joyplot(mock_axes, sample_data, orientation=None)

    def test_plot_joyplot_case_sensitivity(self, sample_data, mock_axes):
        """Test that orientation parameter is case-sensitive."""
        with pytest.raises(ValueError):
            plot_joyplot(mock_axes, sample_data, orientation="VERTICAL")
        
        with pytest.raises(ValueError):
            plot_joyplot(mock_axes, sample_data, orientation="Horizontal")

    def test_plot_joyplot_kwargs_passthrough(self, sample_data, mock_axes):
        """Test that additional kwargs are passed through to joypy."""
        with patch('scitex.plt.ax._plot._plot_joyplot.joypy.joyplot') as mock_joypy:
            mock_joypy.return_value = (MagicMock(), [mock_axes])
            
            with patch('scitex.plt.ax._plot._plot_joyplot.scitex_plt_set_xyt') as mock_set_xyt:
                mock_set_xyt.return_value = mock_axes
                
                # Test with additional kwargs
                custom_kwargs = {
                    'colormap': 'viridis',
                    'alpha': 0.7,
                    'overlap': 0.8,
                    'linewidth': 2
                }
                
                plot_joyplot(mock_axes, sample_data, **custom_kwargs)
                
                # Verify all kwargs were passed through
                call_args = mock_joypy.call_args
                for key, value in custom_kwargs.items():
                    assert call_args[1][key] == value

    def test_plot_joyplot_horizontal_kde_default(self, sample_data, mock_axes):
        """Test that horizontal orientation sets kde as default kind."""
        with patch('scitex.plt.ax._plot._plot_joyplot.joypy.joyplot') as mock_joypy:
            mock_joypy.return_value = (MagicMock(), [mock_axes])
            
            with patch('scitex.plt.ax._plot._plot_joyplot.scitex_plt_set_xyt'):
                plot_joyplot(mock_axes, sample_data, orientation="horizontal")
                
                # Verify kde kind was set as default
                call_args = mock_joypy.call_args
                assert call_args[1].get('kind') == 'kde'

    def test_plot_joyplot_horizontal_kde_override(self, sample_data, mock_axes):
        """Test that explicit kind parameter overrides default for horizontal."""
        with patch('scitex.plt.ax._plot._plot_joyplot.joypy.joyplot') as mock_joypy:
            mock_joypy.return_value = (MagicMock(), [mock_axes])
            
            with patch('scitex.plt.ax._plot._plot_joyplot.scitex_plt_set_xyt'):
                plot_joyplot(mock_axes, sample_data, orientation="horizontal", kind="hist")
                
                # Verify explicit kind parameter takes precedence
                call_args = mock_joypy.call_args
                assert call_args[1].get('kind') == 'hist'

    def test_plot_joyplot_vertical_no_kde_default(self, sample_data, mock_axes):
        """Test that vertical orientation doesn't force kde kind."""
        with patch('scitex.plt.ax._plot._plot_joyplot.joypy.joyplot') as mock_joypy:
            mock_joypy.return_value = (MagicMock(), [mock_axes])
            
            with patch('scitex.plt.ax._plot._plot_joyplot.scitex_plt_set_xyt'):
                plot_joyplot(mock_axes, sample_data, orientation="vertical")
                
                # Verify no default kind is set for vertical
                call_args = mock_joypy.call_args
                assert 'kind' not in call_args[1]

    def test_plot_joyplot_empty_dataframe(self, mock_axes):
        """Test joyplot with empty DataFrame."""
        empty_data = pd.DataFrame()
        
        with patch('scitex.plt.ax._plot._plot_joyplot.joypy.joyplot') as mock_joypy:
            mock_joypy.return_value = (MagicMock(), [mock_axes])
            
            with patch('scitex.plt.ax._plot._plot_joyplot.scitex_plt_set_xyt') as mock_set_xyt:
                mock_set_xyt.return_value = mock_axes
                
                result = plot_joyplot(mock_axes, empty_data)
                
                # Should still call joypy and return axes
                mock_joypy.assert_called_once()
                assert result is mock_axes

    def test_plot_joyplot_single_column_data(self, mock_axes):
        """Test joyplot with single column DataFrame."""
        single_col_data = pd.DataFrame({'A': np.random.normal(0, 1, 50)})
        
        with patch('scitex.plt.ax._plot._plot_joyplot.joypy.joyplot') as mock_joypy:
            mock_joypy.return_value = (MagicMock(), [mock_axes])
            
            with patch('scitex.plt.ax._plot._plot_joyplot.scitex_plt_set_xyt') as mock_set_xyt:
                mock_set_xyt.return_value = mock_axes
                
                result = plot_joyplot(mock_axes, single_col_data)
                
                mock_joypy.assert_called_once()
                assert result is mock_axes

    def test_plot_joyplot_array_data(self, mock_axes):
        """Test joyplot with numpy array data."""
        array_data = np.random.normal(0, 1, (100, 3))
        
        with patch('scitex.plt.ax._plot._plot_joyplot.joypy.joyplot') as mock_joypy:
            mock_joypy.return_value = (MagicMock(), [mock_axes])
            
            with patch('scitex.plt.ax._plot._plot_joyplot.scitex_plt_set_xyt') as mock_set_xyt:
                mock_set_xyt.return_value = mock_axes
                
                result = plot_joyplot(mock_axes, array_data)
                
                # Should pass array data to joypy
                call_args = mock_joypy.call_args
                np.testing.assert_array_equal(call_args[1]['data'], array_data)
                assert result is mock_axes

    def test_plot_joyplot_docstring_completeness(self):
        """Test that the function has proper docstring."""
        assert plot_joyplot.__doc__ is not None
        assert "Parameters" in plot_joyplot.__doc__
        assert "Returns" in plot_joyplot.__doc__
        assert "Raises" in plot_joyplot.__doc__
        assert "orientation" in plot_joyplot.__doc__
        assert "ValueError" in plot_joyplot.__doc__


class TestPlotJoyplotIntegration:
    """Integration tests for plot_joyplot function."""

    @pytest.mark.skipif(True, reason="Integration test - requires joypy dependency")
    def test_plot_joyplot_real_execution(self):
        """Integration test with real joypy execution."""
        # This test would run the actual function with real data
        # Skip by default to avoid dependency issues in CI
        import matplotlib.pyplot as plt
        
        fig, ax = plt.subplots()
        data = pd.DataFrame({
            'A': np.random.normal(0, 1, 100),
            'B': np.random.normal(1, 1, 100)
        })
        
        try:
            result = plot_joyplot(ax, data, orientation="vertical")
            assert result is not None
        except ImportError:
            pytest.skip("joypy not available for integration test")
        finally:
            plt.close(fig)


if __name__ == "__main__":
    import os
    import pytest
    pytest.main([os.path.abspath(__file__)])