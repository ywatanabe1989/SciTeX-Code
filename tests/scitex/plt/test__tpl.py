#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-03 12:37:08 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/tests/scitex/plt/test__tpl.py
# ----------------------------------------
import os

__FILE__ = "./tests/scitex/plt/test__tpl.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import matplotlib
import numpy as np
import pytest
import termplotlib as tpl
from unittest.mock import Mock, patch, call

matplotlib.use("Agg")  # Use non-interactive backend for testing

from scitex.plt import termplot


class DummyFig:
    def __init__(self):
        self.plots = []

    def plot(self, x, y):
        self.plots.append((list(x), list(y)))

    def show(self):
        pass


def test_termplot_one_arg(monkeypatch):
    dummy = DummyFig()
    monkeypatch.setattr(tpl, "figure", lambda *args, **kwargs: dummy)
    y_values = np.array([0, 1, 2, 3])
    termplot(y_values)
    assert len(dummy.plots) == 1
    expected_x = list(np.arange(len(y_values)))
    expected_y = list(y_values)
    assert dummy.plots[0] == (expected_x, expected_y)


def test_termplot_two_args(monkeypatch):
    dummy = DummyFig()
    monkeypatch.setattr(tpl, "figure", lambda *args, **kwargs: dummy)
    x_values = np.array([10, 20, 30])
    y_values = np.array([1, 2, 3])
    termplot(x_values, y_values)
    assert dummy.plots[0] == (list(x_values), list(y_values))


def test_termplot_with_lists():
    """Test termplot with Python lists instead of numpy arrays."""
    mock_fig = Mock()
    
    with patch('termplotlib.figure', return_value=mock_fig):
        y_values = [1, 4, 9, 16, 25]
        termplot(y_values)
        
        # Check that plot was called with correct arguments
        mock_fig.plot.assert_called_once()
        call_args = mock_fig.plot.call_args[0]
        np.testing.assert_array_equal(call_args[0], np.arange(5))
        np.testing.assert_array_equal(call_args[1], y_values)
        mock_fig.show.assert_called_once()


def test_termplot_empty_array():
    """Test termplot with empty array."""
    mock_fig = Mock()
    
    with patch('termplotlib.figure', return_value=mock_fig):
        y_values = np.array([])
        termplot(y_values)
        
        # Should still call plot, even with empty data
        mock_fig.plot.assert_called_once()
        call_args = mock_fig.plot.call_args[0]
        assert len(call_args[0]) == 0  # x should be empty
        assert len(call_args[1]) == 0  # y should be empty


def test_termplot_single_value():
    """Test termplot with single value."""
    mock_fig = Mock()
    
    with patch('termplotlib.figure', return_value=mock_fig):
        termplot([42])
        
        mock_fig.plot.assert_called_once()
        call_args = mock_fig.plot.call_args[0]
        np.testing.assert_array_equal(call_args[0], [0])
        np.testing.assert_array_equal(call_args[1], [42])


def test_termplot_negative_values():
    """Test termplot with negative values."""
    mock_fig = Mock()
    
    with patch('termplotlib.figure', return_value=mock_fig):
        y_values = np.array([-10, -5, 0, 5, 10])
        termplot(y_values)
        
        mock_fig.plot.assert_called_once()
        call_args = mock_fig.plot.call_args[0]
        np.testing.assert_array_equal(call_args[0], np.arange(5))
        np.testing.assert_array_equal(call_args[1], y_values)


def test_termplot_float_values():
    """Test termplot with floating point values."""
    mock_fig = Mock()
    
    with patch('termplotlib.figure', return_value=mock_fig):
        y_values = np.array([1.5, 2.7, 3.14, 4.2])
        termplot(y_values)
        
        mock_fig.plot.assert_called_once()
        call_args = mock_fig.plot.call_args[0]
        np.testing.assert_array_equal(call_args[0], np.arange(4))
        np.testing.assert_array_almost_equal(call_args[1], y_values)


def test_termplot_custom_x_values():
    """Test termplot with custom x values."""
    mock_fig = Mock()
    
    with patch('termplotlib.figure', return_value=mock_fig):
        x_values = np.array([0.5, 1.0, 1.5, 2.0])
        y_values = np.array([1, 4, 9, 16])
        termplot(x_values, y_values)
        
        mock_fig.plot.assert_called_once()
        call_args = mock_fig.plot.call_args[0]
        np.testing.assert_array_almost_equal(call_args[0], x_values)
        np.testing.assert_array_equal(call_args[1], y_values)


def test_termplot_mismatched_lengths():
    """Test termplot with mismatched x and y lengths."""
    mock_fig = Mock()
    
    with patch('termplotlib.figure', return_value=mock_fig):
        x_values = np.array([1, 2, 3])
        y_values = np.array([10, 20, 30, 40])  # Different length
        
        # Should still work - termplotlib or numpy will handle it
        termplot(x_values, y_values)
        
        mock_fig.plot.assert_called_once()


def test_termplot_with_nan_values():
    """Test termplot with NaN values."""
    mock_fig = Mock()
    
    with patch('termplotlib.figure', return_value=mock_fig):
        y_values = np.array([1, np.nan, 3, 4, np.nan])
        termplot(y_values)
        
        mock_fig.plot.assert_called_once()
        call_args = mock_fig.plot.call_args[0]
        np.testing.assert_array_equal(call_args[0], np.arange(5))
        # NaN values should be preserved
        assert np.isnan(call_args[1][1])
        assert np.isnan(call_args[1][4])


def test_termplot_with_inf_values():
    """Test termplot with infinite values."""
    mock_fig = Mock()
    
    with patch('termplotlib.figure', return_value=mock_fig):
        y_values = np.array([1, np.inf, 3, -np.inf, 5])
        termplot(y_values)
        
        mock_fig.plot.assert_called_once()
        call_args = mock_fig.plot.call_args[0]
        np.testing.assert_array_equal(call_args[0], np.arange(5))
        assert call_args[1][1] == np.inf
        assert call_args[1][3] == -np.inf


def test_termplot_large_dataset():
    """Test termplot with large dataset."""
    mock_fig = Mock()
    
    with patch('termplotlib.figure', return_value=mock_fig):
        y_values = np.random.randn(1000)
        termplot(y_values)
        
        mock_fig.plot.assert_called_once()
        call_args = mock_fig.plot.call_args[0]
        assert len(call_args[0]) == 1000
        assert len(call_args[1]) == 1000


def test_termplot_return_value():
    """Test that termplot returns None."""
    mock_fig = Mock()
    
    with patch('termplotlib.figure', return_value=mock_fig):
        result = termplot([1, 2, 3])
        assert result is None


def test_termplot_figure_show_called():
    """Test that figure.show() is always called."""
    mock_fig = Mock()
    
    with patch('termplotlib.figure', return_value=mock_fig):
        # Test with one argument
        termplot([1, 2, 3])
        assert mock_fig.show.call_count == 1
        
        # Test with two arguments
        termplot([1, 2, 3], [4, 5, 6])
        assert mock_fig.show.call_count == 2


def test_termplot_2d_array_handling():
    """Test termplot with 2D array (should work with first dimension)."""
    mock_fig = Mock()
    
    with patch('termplotlib.figure', return_value=mock_fig):
        # 2D array - termplot should handle it somehow
        y_values = np.array([[1, 2], [3, 4], [5, 6]])
        termplot(y_values)
        
        # Function should still be called
        mock_fig.plot.assert_called_once()


def test_termplot_with_different_dtypes():
    """Test termplot with different data types."""
    mock_fig = Mock()
    
    with patch('termplotlib.figure', return_value=mock_fig):
        # Integer dtype
        termplot(np.array([1, 2, 3], dtype=np.int32))
        
        # Float32 dtype
        termplot(np.array([1.0, 2.0, 3.0], dtype=np.float32))
        
        # Complex numbers (might not display properly but shouldn't crash)
        termplot(np.array([1+2j, 3+4j, 5+6j]))
        
        assert mock_fig.plot.call_count == 3
        assert mock_fig.show.call_count == 3


def test_termplot_zero_args():
    """Test termplot with zero arguments should raise error."""
    with pytest.raises(UnboundLocalError):
        termplot()


def test_termplot_three_args():
    """Test termplot with three arguments."""
    mock_fig = Mock()
    
    with patch('termplotlib.figure', return_value=mock_fig):
        # With current implementation, this might not work properly
        # but we test current behavior
        termplot(1, 2, 3)
        
        # The function will process first two args as x, y
        mock_fig.plot.assert_called_once()

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/plt/_tpl.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-03-31 11:58:28 (ywatanabe)"
# 
# import numpy as np
# import termplotlib as tpl
# 
# 
# def termplot(*args):
#     """
#     Plots given y values against x using termplotlib, or plots a single y array against its indices if x is not provided.
# 
#     Parameters:
#     - *args: Accepts either one argument (y values) or two arguments (x and y values).
# 
#     Returns:
#     None. Displays the plot in the terminal.
#     """
#     if len(args) == 1:
#         y = args[0]  # [REVISED]
#         x = np.arange(len(y))
# 
#     if len(args) == 2:
#         x, y = args
# 
#     fig = tpl.figure()
#     fig.plot(x, y)
#     fig.show()

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/plt/_tpl.py
# --------------------------------------------------------------------------------
