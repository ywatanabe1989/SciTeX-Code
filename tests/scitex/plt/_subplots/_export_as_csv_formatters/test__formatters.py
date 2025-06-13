#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-18 20:49:59 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/tests/scitex/plt/_subplots/_export_as_csv_formatters/test__formatters.py
# ----------------------------------------
import os
__FILE__ = (
    "./tests/scitex/plt/_subplots/_export_as_csv_formatters/test__formatters.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import numpy as np
import pandas as pd
import pytest

from scitex.plt._subplots import (
    _format_plot_kde,
    _format_plot_line,
    _format_plot_conf_mat,
    _format_plot_mean_std,
    _format_plot_ecdf,
    _format_plot_raster,
    _format_plot_joyplot,
    _format_sns_boxplot,
)


def test_format_plot_kde():
    """Test _format_plot_kde function."""
    # Create sample tracked dict data
    x = np.linspace(0, 10, 100)
    kde = np.exp(-(x - 5) ** 2 / 2)
    n = 500
    tracked_dict = {"x": x, "kde": kde, "n": n}
    
    # Test with ID
    result = _format_plot_kde("kde_test", tracked_dict, {})
    
    # Verify result
    assert isinstance(result, pd.DataFrame)
    assert "kde_test_kde_x" in result.columns
    assert "kde_test_kde_density" in result.columns
    assert "kde_test_kde_n" in result.columns
    assert len(result) == len(x)
    
    # Test without ID
    result_no_id = _format_plot_kde(None, tracked_dict, {})
    assert "kde_x" not in result_no_id.columns  # No prefix without ID
    
    # Test with missing data
    incomplete_dict = {"x": x}  # Missing 'kde'
    result_incomplete = _format_plot_kde("test", incomplete_dict, {})
    assert result_incomplete.empty


def test_format_plot_line():
    """Test _format_plot_line function."""
    # Create sample DataFrame that would be returned by ax_module.plot_line
    x = np.linspace(0, 10, 100)
    y = np.sin(x)
    plot_df = pd.DataFrame({"x": x, "y": y})
    
    # Create tracked dict data
    tracked_dict = {"plot_df": plot_df}
    
    # Test with ID
    result = _format_plot_line("line_test", tracked_dict, {})
    
    # Verify result
    assert isinstance(result, pd.DataFrame)
    assert "line_test_line_x" in result.columns
    assert "line_test_line_y" in result.columns
    assert len(result) == len(x)
    
    # Test with invalid data
    invalid_dict = {"not_plot_df": "invalid"}
    result_invalid = _format_plot_line("test", invalid_dict, {})
    assert result_invalid.empty


def test_format_plot_conf_mat():
    """Test _format_plot_conf_mat function."""
    # Create sample tracked dict data with balanced accuracy
    tracked_dict = {"balanced_accuracy": 0.85}
    
    # Test with ID
    result = _format_plot_conf_mat("cm_test", tracked_dict, {})
    
    # Verify result
    assert isinstance(result, pd.DataFrame)
    assert "cm_test_conf_mat_balanced_accuracy" in result.columns
    assert result["cm_test_conf_mat_balanced_accuracy"].iloc[0] == 0.85
    
    # Test with missing data
    empty_dict = {}
    result_empty = _format_plot_conf_mat("test", empty_dict, {})
    assert result_empty.empty


def test_format_plot_mean_std():
    """Test _format_plot_mean_std function."""
    # Create sample DataFrame that would be returned by ax_module.plot_mean_std
    x = np.linspace(0, 10, 100)
    mean = np.sin(x)
    lower = mean - 0.2
    upper = mean + 0.2
    plot_df = pd.DataFrame({"x": x, "mean": mean, "lower": lower, "upper": upper})
    
    # Create tracked dict data
    tracked_dict = {"plot_df": plot_df}
    
    # Test with ID
    result = _format_plot_mean_std("mean_std_test", tracked_dict, {})
    
    # Verify result
    assert isinstance(result, pd.DataFrame)
    assert "mean_std_test_mean_std_x" in result.columns
    assert "mean_std_test_mean_std_mean" in result.columns
    assert "mean_std_test_mean_std_lower" in result.columns
    assert "mean_std_test_mean_std_upper" in result.columns
    assert len(result) == len(x)


def test_format_plot_ecdf():
    """Test _format_plot_ecdf function."""
    # Create sample DataFrame that would be returned by ax_module.plot_ecdf
    x = np.linspace(-3, 3, 100)
    y = 0.5 * (1 + np.tanh(x))  # Sigmoid-like ECDF
    ecdf_df = pd.DataFrame({"x": x, "ecdf": y})
    
    # Create tracked dict data
    tracked_dict = {"ecdf_df": ecdf_df}
    
    # Test with ID
    result = _format_plot_ecdf("ecdf_test", tracked_dict, {})
    
    # Verify result
    assert isinstance(result, pd.DataFrame)
    assert "ecdf_test_ecdf_x" in result.columns
    assert "ecdf_test_ecdf_ecdf" in result.columns
    assert len(result) == len(x)


def test_format_plot_joyplot():
    """Test _format_plot_joyplot function."""
    # Test with dictionary data
    data = {
        "Group A": np.random.normal(0, 1, 100),
        "Group B": np.random.normal(3, 1.5, 100),
        "Group C": np.random.normal(6, 0.8, 100),
    }
    tracked_dict = {"joyplot_data": data}
    
    # Test with ID
    result = _format_plot_joyplot("joy_test", tracked_dict, {})
    
    # Verify result
    assert isinstance(result, pd.DataFrame)
    assert "joy_test_joyplot_Group A" in result.columns
    assert "joy_test_joyplot_Group B" in result.columns
    assert "joy_test_joyplot_Group C" in result.columns
    
    # Test with list data
    data_list = [
        np.random.normal(0, 1, 100),
        np.random.normal(3, 1.5, 100),
        np.random.normal(6, 0.8, 100),
    ]
    tracked_dict_list = {"joyplot_data": data_list}
    
    result_list = _format_plot_joyplot("joy_list_test", tracked_dict_list, {})
    assert "joy_list_test_joyplot_group00" in result_list.columns
    assert "joy_list_test_joyplot_group01" in result_list.columns
    assert "joy_list_test_joyplot_group02" in result_list.columns


def test_format_sns_boxplot():
    """Test _format_sns_boxplot function."""
    # Create sample DataFrame
    data = pd.DataFrame({
        "Group A": np.random.normal(0, 1, 100),
        "Group B": np.random.normal(3, 1.5, 100),
        "Group C": np.random.normal(6, 0.8, 100),
    })
    
    # Test with ID
    result = _format_sns_boxplot("box_test", data, {})
    
    # Verify result
    assert isinstance(result, pd.DataFrame)
    assert "box_test_sns_boxplot_Group A" in result.columns
    assert "box_test_sns_boxplot_Group B" in result.columns
    assert "box_test_sns_boxplot_Group C" in result.columns
    assert len(result) == 100


def test_format_plot_raster():
    """Test _format_plot_raster function."""
    # Create sample raster data
    raster_df = pd.DataFrame({
        "time": np.concatenate([np.random.uniform(0, 100, 20) for _ in range(5)]),
        "neuron": np.concatenate([np.ones(20) * i for i in range(5)]),
    })
    
    # Create tracked dict data
    tracked_dict = {"raster_digit_df": raster_df}
    
    # Test with ID
    result = _format_plot_raster("raster_test", tracked_dict, {})
    
    # Verify result
    assert isinstance(result, pd.DataFrame)
    assert "raster_test_raster_time" in result.columns
    assert "raster_test_raster_neuron" in result.columns
    assert len(result) == len(raster_df)


if __name__ == "__main__":
    import os
    import pytest
    pytest.main([os.path.abspath(__file__)])