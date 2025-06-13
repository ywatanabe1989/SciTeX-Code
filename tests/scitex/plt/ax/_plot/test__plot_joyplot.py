#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-01 21:55:17 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/tests/scitex/plt/ax/_plot/test__plot_joyplot.py
# ----------------------------------------
import os

__FILE__ = "./tests/scitex/plt/ax/_plot/test__plot_joyplot.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest
from unittest.mock import patch, MagicMock
import warnings


def test_plot_joyplot_basic():
    """Test basic joyplot functionality."""
from scitex.plt.ax._plot import plot_joyplot
    
    fig, ax = plt.subplots()
    data = pd.DataFrame(
        {"A": np.random.normal(0, 1, 100), "B": np.random.normal(1, 1, 100)}
    )

    with patch('joypy.joyplot') as mock_joyplot:
        mock_fig = MagicMock()
        mock_axes = MagicMock()
        mock_joyplot.return_value = (mock_fig, mock_axes)
        
        result = plot_joyplot(ax, data)
        
        # Check joypy was called
        mock_joyplot.assert_called_once()
        args, kwargs = mock_joyplot.call_args
        assert 'data' in kwargs
        pd.testing.assert_frame_equal(kwargs['data'], data)
        
        # Check return value
        assert result == ax
    
    plt.close(fig)


def test_plot_joyplot_vertical_orientation():
    """Test plot_joyplot with vertical orientation."""
from scitex.plt.ax._plot import plot_joyplot
    
    fig, ax = plt.subplots()
    data = pd.DataFrame({
        "Group1": np.random.normal(0, 1, 100),
        "Group2": np.random.normal(2, 1, 100)
    })
    
    with patch('joypy.joyplot') as mock_joyplot:
        mock_fig = MagicMock()
        mock_axes = MagicMock()
        mock_joyplot.return_value = (mock_fig, mock_axes)
        
        with patch('scitex.plt.ax._plot._plot_joyplot.scitex_plt_set_xyt') as mock_set_xyt:
            mock_set_xyt.return_value = ax
            
            result = plot_joyplot(ax, data, orientation="vertical")
            
            # Check set_xyt was called correctly for vertical orientation
            mock_set_xyt.assert_called_once_with(ax, None, "Density", "Joyplot")
    
    plt.close(fig)


def test_plot_joyplot_horizontal_orientation():
    """Test plot_joyplot with horizontal orientation."""
from scitex.plt.ax._plot import plot_joyplot
    
    fig, ax = plt.subplots()
    data = pd.DataFrame({
        "A": np.random.normal(0, 1, 50),
        "B": np.random.normal(1, 1, 50)
    })
    
    with patch('joypy.joyplot') as mock_joyplot:
        mock_fig = MagicMock()
        mock_axes = MagicMock()
        mock_joyplot.return_value = (mock_fig, mock_axes)
        
        with patch('scitex.plt.ax._plot._plot_joyplot.scitex_plt_set_xyt') as mock_set_xyt:
            mock_set_xyt.return_value = ax
            
            result = plot_joyplot(ax, data, orientation="horizontal")
            
            # Check set_xyt was called correctly for horizontal orientation
            mock_set_xyt.assert_called_once_with(ax, "Density", None, "Joyplot")
            
            # Check that 'kind' default was set
            _, kwargs = mock_joyplot.call_args
            assert kwargs.get('kind') == 'kde'
    
    plt.close(fig)


def test_plot_joyplot_invalid_orientation():
    """Test plot_joyplot with invalid orientation."""
from scitex.plt.ax._plot import plot_joyplot
    
    fig, ax = plt.subplots()
    data = pd.DataFrame({"A": [1, 2, 3]})
    
    with pytest.raises(ValueError, match="orientation must be either 'vertical' or 'horizontal'"):
        plot_joyplot(ax, data, orientation="diagonal")
    
    plt.close(fig)


def test_plot_joyplot_with_kwargs():
    """Test plot_joyplot with additional keyword arguments."""
from scitex.plt.ax._plot import plot_joyplot
    
    fig, ax = plt.subplots()
    data = pd.DataFrame({
        "A": np.random.normal(0, 1, 100),
        "B": np.random.normal(1, 1, 100),
        "C": np.random.normal(2, 1, 100)
    })
    
    with patch('joypy.joyplot') as mock_joyplot:
        mock_fig = MagicMock()
        mock_axes = MagicMock()
        mock_joyplot.return_value = (mock_fig, mock_axes)
        
        custom_kwargs = {
            'colormap': plt.cm.viridis,
            'overlap': 0.5,
            'linewidth': 2,
            'alpha': 0.7
        }
        
        result = plot_joyplot(ax, data, **custom_kwargs)
        
        # Check all kwargs were passed to joypy
        _, kwargs = mock_joyplot.call_args
        for key, value in custom_kwargs.items():
            assert kwargs[key] == value
    
    plt.close(fig)


def test_plot_joyplot_empty_dataframe():
    """Test plot_joyplot with empty DataFrame."""
from scitex.plt.ax._plot import plot_joyplot
    
    fig, ax = plt.subplots()
    data = pd.DataFrame()
    
    with patch('joypy.joyplot') as mock_joyplot:
        mock_fig = MagicMock()
        mock_axes = MagicMock()
        mock_joyplot.return_value = (mock_fig, mock_axes)
        
        result = plot_joyplot(ax, data)
        
        # Should still call joypy even with empty data
        mock_joyplot.assert_called_once()
    
    plt.close(fig)


def test_plot_joyplot_single_column():
    """Test plot_joyplot with single column DataFrame."""
from scitex.plt.ax._plot import plot_joyplot
    
    fig, ax = plt.subplots()
    data = pd.DataFrame({"Single": np.random.normal(0, 1, 100)})
    
    with patch('joypy.joyplot') as mock_joyplot:
        mock_fig = MagicMock()
        mock_axes = MagicMock()
        mock_joyplot.return_value = (mock_fig, mock_axes)
        
        result = plot_joyplot(ax, data)
        
        # Check data was passed correctly
        _, kwargs = mock_joyplot.call_args
        pd.testing.assert_frame_equal(kwargs['data'], data)
    
    plt.close(fig)


def test_plot_joyplot_with_nan_values():
    """Test plot_joyplot with NaN values in data."""
from scitex.plt.ax._plot import plot_joyplot
    
    fig, ax = plt.subplots()
    data = pd.DataFrame({
        "A": [1, 2, np.nan, 4, 5],
        "B": [np.nan, 2, 3, 4, np.nan]
    })
    
    with patch('joypy.joyplot') as mock_joyplot:
        mock_fig = MagicMock()
        mock_axes = MagicMock()
        mock_joyplot.return_value = (mock_fig, mock_axes)
        
        result = plot_joyplot(ax, data)
        
        # Should pass data with NaN values to joypy
        _, kwargs = mock_joyplot.call_args
        assert kwargs['data'].isna().any().any()
    
    plt.close(fig)


def test_plot_joyplot_mixed_data_types():
    """Test plot_joyplot with mixed numeric data types."""
from scitex.plt.ax._plot import plot_joyplot
    
    fig, ax = plt.subplots()
    data = pd.DataFrame({
        "Integers": np.random.randint(0, 10, 50),
        "Floats": np.random.rand(50),
        "Normal": np.random.normal(0, 1, 50)
    })
    
    with patch('joypy.joyplot') as mock_joyplot:
        mock_fig = MagicMock()
        mock_axes = MagicMock()
        mock_joyplot.return_value = (mock_fig, mock_axes)
        
        result = plot_joyplot(ax, data)
        
        # All numeric types should be handled
        mock_joyplot.assert_called_once()
    
    plt.close(fig)


def test_plot_joyplot_large_dataset():
    """Test plot_joyplot with larger dataset."""
from scitex.plt.ax._plot import plot_joyplot
    
    fig, ax = plt.subplots()
    # Create a larger dataset with multiple groups
    data = pd.DataFrame({
        f"Group_{i}": np.random.normal(i, 1, 1000)
        for i in range(10)
    })
    
    with patch('joypy.joyplot') as mock_joyplot:
        mock_fig = MagicMock()
        mock_axes = MagicMock()
        mock_joyplot.return_value = (mock_fig, mock_axes)
        
        result = plot_joyplot(ax, data)
        
        # Check data shape is preserved
        _, kwargs = mock_joyplot.call_args
        assert kwargs['data'].shape == (1000, 10)
    
    plt.close(fig)


def test_plot_joyplot_custom_kind_parameter():
    """Test plot_joyplot with custom kind parameter."""
from scitex.plt.ax._plot import plot_joyplot
    
    fig, ax = plt.subplots()
    data = pd.DataFrame({
        "A": np.random.normal(0, 1, 100),
        "B": np.random.normal(1, 1, 100)
    })
    
    with patch('joypy.joyplot') as mock_joyplot:
        mock_fig = MagicMock()
        mock_axes = MagicMock()
        mock_joyplot.return_value = (mock_fig, mock_axes)
        
        # Test with different kind parameters
        for kind in ['kde', 'hist', 'counts']:
            result = plot_joyplot(ax, data, kind=kind)
            
            _, kwargs = mock_joyplot.call_args
            assert kwargs['kind'] == kind
    
    plt.close(fig)


def test_plot_joyplot_return_type():
    """Test that plot_joyplot returns the correct axes object."""
from scitex.plt.ax._plot import plot_joyplot
    
    fig, ax = plt.subplots()
    data = pd.DataFrame({"A": [1, 2, 3]})
    
    with patch('joypy.joyplot') as mock_joyplot:
        mock_fig = MagicMock()
        mock_axes = MagicMock()
        mock_joyplot.return_value = (mock_fig, mock_axes)
        
        result = plot_joyplot(ax, data)
        
        # Should return the input axes
        assert result is ax
        assert isinstance(result, type(ax))
    
    plt.close(fig)


def test_plot_joyplot_integration():
    """Test actual integration if joypy is available."""
from scitex.plt.ax._plot import plot_joyplot
    
    fig, ax = plt.subplots()
    data = pd.DataFrame({
        "A": np.random.normal(0, 1, 100),
        "B": np.random.normal(1, 1, 100)
    })
    
    try:
        # Try actual joypy call
        result = plot_joyplot(ax, data)
        
        # If joypy is available, check basic properties
        assert result is not None
        
        # Save for visual inspection
        from scitex.io import save
        spath = f"./joyplot_integration.jpg"
        save(fig, spath)
        
        ACTUAL_SAVE_DIR = __file__.replace(".py", "_out")
        actual_spath = os.path.join(ACTUAL_SAVE_DIR, spath)
        assert os.path.exists(actual_spath), f"Failed to save figure to {spath}"
        
    except ImportError:
        # If joypy is not installed, skip this test
        pytest.skip("joypy not installed")
    finally:
        plt.close(fig)


if __name__ == "__main__":
    import os
    import pytest
    
    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/ax/_plot/_plot_joyplot.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-05-02 09:03:23 (ywatanabe)"
# # File: /home/ywatanabe/proj/scitex_repo/src/scitex/plt/ax/_plot/_plot_joyplot.py
# # ----------------------------------------
# import os
# __FILE__ = (
#     "./src/scitex/plt/ax/_plot/_plot_joyplot.py"
# )
# __DIR__ = os.path.dirname(__FILE__)
# # ----------------------------------------
#
# import warnings
#
# import joypy
#
# from .._style._set_xyt import set_xyt as scitex_plt_set_xyt
#
#
# def plot_joyplot(ax, data, orientation="vertical", **kwargs):
#     # FIXME; orientation should be handled
#     fig, axes = joypy.joyplot(
#         data=data,
#         **kwargs,
#     )
#
#     if orientation == "vertical":
#         ax = scitex_plt_set_xyt(ax, None, "Density", "Joyplot")
#     elif orientation == "horizontal":
#         ax = scitex_plt_set_xyt(ax, "Density", None, "Joyplot")
#     else:
#         warnings.warn(
#             "orientation must be either of 'vertical' or 'horizontal'"
#         )
#
#     return ax
#
#
# # def plot_vertical_joyplot(ax, data, **kwargs):
# #     return _plot_joyplot(ax, data, "vertical", **kwargs)
#
#
# # def plot_horizontal_joyplot(ax, data, **kwargs):
# #     return _plot_joyplot(ax, data, "horizontal", **kwargs)
#
# # EOF
# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/_scitex_repo/src/scitex/plt/ax/_plot/_plot_joyplot.py
# --------------------------------------------------------------------------------
