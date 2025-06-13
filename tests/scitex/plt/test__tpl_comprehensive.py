#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-04 09:19:00 (ywatanabe)"
# File: ./tests/scitex/plt/test__tpl_comprehensive.py

"""Comprehensive tests for scitex.plt._tpl terminal plotting functionality."""

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock


class TestTermplotImport:
    """Test import functionality and dependencies."""

    def test_import_termplot(self):
        """Test that termplot function can be imported."""
from scitex.plt import termplot
        assert callable(termplot)

    def test_dependencies_available(self):
        """Test that required dependencies are available."""
        import scitex.plt._tpl as tpl_module
        
        # Check numpy is available
        assert hasattr(tpl_module, 'np')
        assert tpl_module.np is np
        
        # Check termplotlib is available
        assert hasattr(tpl_module, 'tpl')


class TestTermplotBasicFunctionality:
    """Test basic termplot functionality."""

    @patch('scitex.plt._tpl.tpl.figure')
    def test_termplot_single_argument(self, mock_figure):
        """Test termplot with single y-values argument."""
from scitex.plt import termplot
        
        # Setup mock
        mock_fig = Mock()
        mock_figure.return_value = mock_fig
        
        # Test data
        y_data = [1, 2, 3, 4, 5]
        
        # Call function
        termplot(y_data)
        
        # Verify termplotlib was called correctly
        mock_figure.assert_called_once()
        mock_fig.plot.assert_called_once()
        mock_fig.show.assert_called_once()
        
        # Verify x-values were generated correctly
        call_args = mock_fig.plot.call_args[0]
        x_values, y_values = call_args
        
        np.testing.assert_array_equal(x_values, np.arange(len(y_data)))
        np.testing.assert_array_equal(y_values, y_data)

    @patch('scitex.plt._tpl.tpl.figure')
    def test_termplot_two_arguments(self, mock_figure):
        """Test termplot with both x and y arguments."""
from scitex.plt import termplot
        
        # Setup mock
        mock_fig = Mock()
        mock_figure.return_value = mock_fig
        
        # Test data
        x_data = [0, 1, 2, 3, 4]
        y_data = [1, 4, 9, 16, 25]
        
        # Call function
        termplot(x_data, y_data)
        
        # Verify termplotlib was called correctly
        mock_figure.assert_called_once()
        mock_fig.plot.assert_called_once()
        mock_fig.show.assert_called_once()
        
        # Verify data was passed correctly
        call_args = mock_fig.plot.call_args[0]
        passed_x, passed_y = call_args
        
        np.testing.assert_array_equal(passed_x, x_data)
        np.testing.assert_array_equal(passed_y, y_data)

    @patch('scitex.plt._tpl.tpl.figure')
    def test_termplot_numpy_arrays(self, mock_figure):
        """Test termplot with numpy arrays."""
from scitex.plt import termplot
        
        # Setup mock
        mock_fig = Mock()
        mock_figure.return_value = mock_fig
        
        # Test data as numpy arrays
        y_data = np.array([1, 2, 3, 4, 5])
        
        # Call function
        termplot(y_data)
        
        # Verify function executed successfully
        mock_figure.assert_called_once()
        mock_fig.plot.assert_called_once()
        mock_fig.show.assert_called_once()

    @patch('scitex.plt._tpl.tpl.figure')
    def test_termplot_empty_array(self, mock_figure):
        """Test termplot with empty array."""
from scitex.plt import termplot
        
        # Setup mock
        mock_fig = Mock()
        mock_figure.return_value = mock_fig
        
        # Test data
        y_data = []
        
        # Call function
        termplot(y_data)
        
        # Verify function handles empty data
        mock_figure.assert_called_once()
        mock_fig.plot.assert_called_once()
        mock_fig.show.assert_called_once()
        
        # Verify x-values for empty array
        call_args = mock_fig.plot.call_args[0]
        x_values, y_values = call_args
        
        np.testing.assert_array_equal(x_values, np.arange(0))
        assert len(y_values) == 0


class TestTermplotDataTypes:
    """Test termplot with different data types."""

    @patch('scitex.plt._tpl.tpl.figure')
    def test_termplot_integers(self, mock_figure):
        """Test termplot with integer data."""
from scitex.plt import termplot
        
        mock_fig = Mock()
        mock_figure.return_value = mock_fig
        
        y_data = [1, 2, 3, 4, 5]
        termplot(y_data)
        
        mock_fig.plot.assert_called_once()
        
    @patch('scitex.plt._tpl.tpl.figure')
    def test_termplot_floats(self, mock_figure):
        """Test termplot with float data."""
from scitex.plt import termplot
        
        mock_fig = Mock()
        mock_figure.return_value = mock_fig
        
        y_data = [1.1, 2.2, 3.3, 4.4, 5.5]
        termplot(y_data)
        
        mock_fig.plot.assert_called_once()

    @patch('scitex.plt._tpl.tpl.figure')
    def test_termplot_mixed_types(self, mock_figure):
        """Test termplot with mixed numeric types."""
from scitex.plt import termplot
        
        mock_fig = Mock()
        mock_figure.return_value = mock_fig
        
        y_data = [1, 2.5, 3, 4.8, 5]
        termplot(y_data)
        
        mock_fig.plot.assert_called_once()

    @patch('scitex.plt._tpl.tpl.figure')
    def test_termplot_negative_values(self, mock_figure):
        """Test termplot with negative values."""
from scitex.plt import termplot
        
        mock_fig = Mock()
        mock_figure.return_value = mock_fig
        
        y_data = [-2, -1, 0, 1, 2]
        termplot(y_data)
        
        mock_fig.plot.assert_called_once()

    @patch('scitex.plt._tpl.tpl.figure')
    def test_termplot_large_values(self, mock_figure):
        """Test termplot with large values."""
from scitex.plt import termplot
        
        mock_fig = Mock()
        mock_figure.return_value = mock_fig
        
        y_data = [1e6, 2e6, 3e6, 4e6, 5e6]
        termplot(y_data)
        
        mock_fig.plot.assert_called_once()


class TestTermplotEdgeCases:
    """Test edge cases and error conditions."""

    def test_termplot_no_arguments(self):
        """Test termplot with no arguments raises appropriate error."""
from scitex.plt import termplot
        
        with pytest.raises(UnboundLocalError):
            termplot()

    def test_termplot_too_many_arguments(self):
        """Test termplot with too many arguments."""
from scitex.plt import termplot
        
        # The function only handles 1 or 2 arguments
        # With 3+ arguments, current implementation has UnboundLocalError
        x_data = [1, 2, 3]
        y_data = [4, 5, 6]
        z_data = [7, 8, 9]
        
        # Current implementation raises UnboundLocalError with 3+ arguments
        with pytest.raises(UnboundLocalError):
            termplot(x_data, y_data, z_data)

    @patch('scitex.plt._tpl.tpl.figure')
    def test_termplot_single_value(self, mock_figure):
        """Test termplot with single value."""
from scitex.plt import termplot
        
        mock_fig = Mock()
        mock_figure.return_value = mock_fig
        
        y_data = [42]
        termplot(y_data)
        
        mock_figure.assert_called_once()
        mock_fig.plot.assert_called_once()
        
        # Verify x-values for single point
        call_args = mock_fig.plot.call_args[0]
        x_values, y_values = call_args
        
        np.testing.assert_array_equal(x_values, np.arange(1))
        np.testing.assert_array_equal(y_values, [42])

    @patch('scitex.plt._tpl.tpl.figure')
    def test_termplot_mismatched_lengths(self, mock_figure):
        """Test termplot with mismatched x and y lengths."""
from scitex.plt import termplot
        
        mock_fig = Mock()
        mock_figure.return_value = mock_fig
        
        x_data = [1, 2, 3]
        y_data = [4, 5]  # Different length
        
        # Function should still call termplotlib (behavior depends on termplotlib)
        termplot(x_data, y_data)
        
        mock_figure.assert_called_once()
        mock_fig.plot.assert_called_once()


class TestTermplotMathematicalFunctions:
    """Test termplot with mathematical functions and patterns."""

    @patch('scitex.plt._tpl.tpl.figure')
    def test_termplot_linear_function(self, mock_figure):
        """Test termplot with linear function."""
from scitex.plt import termplot
        
        mock_fig = Mock()
        mock_figure.return_value = mock_fig
        
        x_data = np.linspace(0, 10, 11)
        y_data = 2 * x_data + 3  # Linear function
        
        termplot(x_data, y_data)
        
        mock_fig.plot.assert_called_once()
        
        # Verify data integrity
        call_args = mock_fig.plot.call_args[0]
        passed_x, passed_y = call_args
        
        np.testing.assert_array_almost_equal(passed_x, x_data)
        np.testing.assert_array_almost_equal(passed_y, y_data)

    @patch('scitex.plt._tpl.tpl.figure')
    def test_termplot_quadratic_function(self, mock_figure):
        """Test termplot with quadratic function."""
from scitex.plt import termplot
        
        mock_fig = Mock()
        mock_figure.return_value = mock_fig
        
        x_data = np.linspace(-5, 5, 11)
        y_data = x_data ** 2  # Quadratic function
        
        termplot(x_data, y_data)
        
        mock_fig.plot.assert_called_once()

    @patch('scitex.plt._tpl.tpl.figure')
    def test_termplot_sine_wave(self, mock_figure):
        """Test termplot with sine wave."""
from scitex.plt import termplot
        
        mock_fig = Mock()
        mock_figure.return_value = mock_fig
        
        x_data = np.linspace(0, 2*np.pi, 100)
        y_data = np.sin(x_data)
        
        termplot(x_data, y_data)
        
        mock_fig.plot.assert_called_once()

    @patch('scitex.plt._tpl.tpl.figure')
    def test_termplot_exponential_function(self, mock_figure):
        """Test termplot with exponential function."""
from scitex.plt import termplot
        
        mock_fig = Mock()
        mock_figure.return_value = mock_fig
        
        x_data = np.linspace(0, 3, 20)
        y_data = np.exp(x_data)
        
        termplot(x_data, y_data)
        
        mock_fig.plot.assert_called_once()


class TestTermplotSpecialValues:
    """Test termplot with special numerical values."""

    @patch('scitex.plt._tpl.tpl.figure')
    def test_termplot_with_nan(self, mock_figure):
        """Test termplot with NaN values."""
from scitex.plt import termplot
        
        mock_fig = Mock()
        mock_figure.return_value = mock_fig
        
        y_data = [1, 2, np.nan, 4, 5]
        
        # Function should handle NaN gracefully
        termplot(y_data)
        
        mock_fig.plot.assert_called_once()

    @patch('scitex.plt._tpl.tpl.figure')
    def test_termplot_with_inf(self, mock_figure):
        """Test termplot with infinite values."""
from scitex.plt import termplot
        
        mock_fig = Mock()
        mock_figure.return_value = mock_fig
        
        y_data = [1, 2, np.inf, 4, 5]
        
        # Function should handle infinity gracefully
        termplot(y_data)
        
        mock_fig.plot.assert_called_once()

    @patch('scitex.plt._tpl.tpl.figure')
    def test_termplot_with_negative_inf(self, mock_figure):
        """Test termplot with negative infinite values."""
from scitex.plt import termplot
        
        mock_fig = Mock()
        mock_figure.return_value = mock_fig
        
        y_data = [1, 2, -np.inf, 4, 5]
        
        # Function should handle negative infinity gracefully
        termplot(y_data)
        
        mock_fig.plot.assert_called_once()


class TestTermplotPerformance:
    """Test termplot performance and efficiency."""

    @patch('scitex.plt._tpl.tpl.figure')
    def test_termplot_large_dataset(self, mock_figure):
        """Test termplot with large dataset."""
from scitex.plt import termplot
        
        mock_fig = Mock()
        mock_figure.return_value = mock_fig
        
        # Large dataset
        y_data = np.random.randn(10000)
        
        # Should handle large datasets without issues
        termplot(y_data)
        
        mock_fig.plot.assert_called_once()
        mock_fig.show.assert_called_once()

    @patch('scitex.plt._tpl.tpl.figure')
    def test_termplot_repeated_calls(self, mock_figure):
        """Test multiple calls to termplot."""
from scitex.plt import termplot
        
        mock_fig = Mock()
        mock_figure.return_value = mock_fig
        
        # Multiple calls should work independently
        for i in range(5):
            y_data = [1, 2, 3, 4, 5]
            termplot(y_data)
        
        # Should have been called 5 times
        assert mock_figure.call_count == 5
        assert mock_fig.plot.call_count == 5
        assert mock_fig.show.call_count == 5


class TestTermplotIntegration:
    """Test termplot integration scenarios."""

    @patch('scitex.plt._tpl.tpl.figure')
    def test_termplot_figure_creation(self, mock_figure):
        """Test that termplot creates figures correctly."""
from scitex.plt import termplot
        
        mock_fig = Mock()
        mock_figure.return_value = mock_fig
        
        y_data = [1, 2, 3, 4, 5]
        termplot(y_data)
        
        # Verify the complete workflow
        mock_figure.assert_called_once_with()  # Figure creation
        mock_fig.plot.assert_called_once()     # Plot data
        mock_fig.show.assert_called_once()     # Display plot

    @patch('scitex.plt._tpl.tpl.figure')
    def test_termplot_error_handling(self, mock_figure):
        """Test termplot error handling."""
from scitex.plt import termplot
        
        # Mock figure that raises an error
        mock_figure.side_effect = Exception("Termplotlib error")
        
        y_data = [1, 2, 3, 4, 5]
        
        # Should propagate termplotlib errors
        with pytest.raises(Exception, match="Termplotlib error"):
            termplot(y_data)

    @patch('scitex.plt._tpl.tpl')
    def test_termplot_module_integration(self, mock_tpl):
        """Test termplot integration with termplotlib module."""
from scitex.plt import termplot
        
        # Mock the entire termplotlib module
        mock_fig = Mock()
        mock_tpl.figure.return_value = mock_fig
        
        y_data = [1, 2, 3, 4, 5]
        termplot(y_data)
        
        # Verify integration with termplotlib
        mock_tpl.figure.assert_called_once()
        mock_fig.plot.assert_called_once()
        mock_fig.show.assert_called_once()


class TestTermplotDocumentation:
    """Test termplot documentation and introspection."""

    def test_termplot_function_exists(self):
        """Test that termplot function exists and is discoverable."""
from scitex.plt import termplot
        
        # Function should exist
        assert termplot is not None
        assert callable(termplot)

    def test_termplot_introspection(self):
        """Test termplot function introspection."""
from scitex.plt import termplot
        import inspect
        
        # Should be introspectable
        assert inspect.isfunction(termplot)
        
        # Get signature
        sig = inspect.signature(termplot)
        
        # Should accept variable arguments
        assert len([p for p in sig.parameters.values() 
                   if p.kind == p.VAR_POSITIONAL]) > 0

    def test_termplot_docstring(self):
        """Test termplot docstring availability."""
from scitex.plt import termplot
        
        # Should have a docstring
        assert termplot.__doc__ is not None
        assert len(termplot.__doc__.strip()) > 0
        
        # Docstring should contain key information
        docstring = termplot.__doc__.lower()
        assert any(word in docstring for word in ['plot', 'terminal', 'x', 'y'])


if __name__ == "__main__":
    import os
    pytest.main([os.path.abspath(__file__), "-v"])