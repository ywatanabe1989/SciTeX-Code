#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-11 03:20:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/tests/scitex/plt/_subplots/test__export_as_csv.py
# ----------------------------------------
"""Comprehensive tests for export_as_csv functionality."""

import os
import warnings

__FILE__ = "./tests/scitex/plt/_subplots/test__export_as_csv.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-05-18 06:05:04 (ywatanabe)"
# # File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/tests/scitex/plt/_subplots/test__export_as_csv.py
# # ----------------------------------------
# import os
# __FILE__ = (
#     "./tests/scitex/plt/_subplots/test__export_as_csv.py"
# )
# __DIR__ = os.path.dirname(__FILE__)
# # ----------------------------------------

import numpy as np
import pandas as pd
import pytest
import xarray as xr
from unittest.mock import patch, MagicMock

# Try direct import
try:
    from scitex.plt._subplots import export_as_csv, format_record, _format_imshow2d
except ImportError:
    # Skip tests if module not properly available
    pytest.skip("Module scitex.plt._subplots._export_as_csv not available", allow_module_level=True)


class TestExportAsCSV:
    """Test suite for export_as_csv function."""
    
    def test_empty_history(self):
        """Test export with empty history."""
        history = {}
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = export_as_csv(history)
            assert isinstance(result, pd.DataFrame)
            assert result.empty
            assert len(w) == 1
            assert "Plotting records not found" in str(w[0].message)

    def test_simple_plot(self):
        """Test export with simple plot."""
        history = {"plot1": ("plot1", "plot", ([1, 2, 3], [4, 5, 6]), {})}
        result = export_as_csv(history)
        assert isinstance(result, pd.DataFrame)
        assert "plot1_plot_x" in result.columns
        assert "plot1_plot_y" in result.columns
        assert result["plot1_plot_x"].tolist() == [1, 2, 3]
        assert result["plot1_plot_y"].tolist() == [4, 5, 6]

    def test_multiple_plots(self):
        """Test export with multiple plots."""
        history = {
            "plot1": ("plot1", "plot", ([1, 2, 3], [4, 5, 6]), {}),
            "plot2": ("plot2", "plot", ([4, 5, 6], [1, 2, 3]), {}),
        }
        result = export_as_csv(history)
        assert isinstance(result, pd.DataFrame)
        assert list(result.columns) == [
            "plot1_plot_x",
            "plot1_plot_y",
            "plot2_plot_x",
            "plot2_plot_y",
        ]
        
    def test_export_concat_failure(self):
        """Test export when concat fails."""
        # Create a mock that raises exception
        with patch('pandas.concat', side_effect=ValueError("Test error")):
            history = {
                "plot1": ("plot1", "plot", ([1, 2], [3, 4]), {}),
                "plot2": ("plot2", "plot", ([5, 6, 7], [8, 9, 10]), {})  # Different length
            }
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                result = export_as_csv(history)
                assert isinstance(result, pd.DataFrame)
                assert result.empty
                assert len(w) == 1
                assert "Plotting records not combined" in str(w[0].message)

    def test_scatter_plot(self):
        """Test export with scatter plot."""
        history = {"scatter1": ("scatter1", "scatter", ([1, 2, 3], [4, 5, 6]), {})}
        result = export_as_csv(history)
        assert isinstance(result, pd.DataFrame)
        assert "scatter1_scatter_x" in result.columns
        assert "scatter1_scatter_y" in result.columns
        assert result["scatter1_scatter_x"].tolist() == [1, 2, 3]
        assert result["scatter1_scatter_y"].tolist() == [4, 5, 6]

    def test_bar_plot(self):
        """Test export with bar plot."""
        history = {"bar1": ("bar1", "bar", (["A", "B", "C"], [4, 5, 6]), {})}
        result = export_as_csv(history)
        assert isinstance(result, pd.DataFrame)
        assert "bar1_bar_x" in result.columns
        assert "bar1_bar_y" in result.columns
        assert result["bar1_bar_x"].tolist() == ["A", "B", "C"]
        assert result["bar1_bar_y"].tolist() == [4, 5, 6]

    def test_bar_plot_with_yerr(self):
        """Test export with bar plot including error bars."""
        history = {
            "bar1": (
                "bar1",
                "bar",
                (["A", "B", "C"], [4, 5, 6]),
                {"yerr": [0.1, 0.2, 0.3]},
            )
        }
        result = export_as_csv(history)
        assert isinstance(result, pd.DataFrame)
        assert "bar1_bar_yerr" in result.columns
        assert result["bar1_bar_yerr"].tolist() == [0.1, 0.2, 0.3]
        
    def test_histogram_plot(self):
        """Test export with histogram."""
        history = {"hist1": ("hist1", "hist", [1, 2, 2, 3, 3, 3], {})}
        result = export_as_csv(history)
        assert isinstance(result, pd.DataFrame)
        assert "hist1_hist_x" in result.columns
        assert result["hist1_hist_x"].tolist() == [1, 2, 2, 3, 3, 3]
        
    def test_mixed_plot_types(self):
        """Test export with mixed plot types."""
        history = {
            "plot1": ("plot1", "plot", ([1, 2], [3, 4]), {}),
            "scatter1": ("scatter1", "scatter", ([5, 6], [7, 8]), {}),
            "bar1": ("bar1", "bar", (["X", "Y"], [9, 10]), {})
        }
        result = export_as_csv(history)
        assert isinstance(result, pd.DataFrame)
        assert result.shape[1] == 6  # 2 cols per plot type
        assert all(col in result.columns for col in [
            "plot1_plot_x", "plot1_plot_y",
            "scatter1_scatter_x", "scatter1_scatter_y", 
            "bar1_bar_x", "bar1_bar_y"
        ])


class TestFormatRecord:
    """Test suite for format_record function."""
    
    def test_imshow2d_format(self):
        """Test formatting imshow2d data."""
        df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
        record = ("img1", "imshow2d", df, {})
        result = format_record(record)
        assert isinstance(result, pd.DataFrame)
        pd.testing.assert_frame_equal(result, df)
        
    def test_plot_with_single_array(self):
        """Test plot formatting with single 2D array."""
        record = ("plot1", "plot", [np.array([[1, 4], [2, 5], [3, 6]])], {})
        result = format_record(record)
        assert isinstance(result, pd.DataFrame)
        assert "plot1_plot_x" in result.columns
        assert result["plot1_plot_x"].tolist() == [1, 2, 3]

    def test_plot_with_separate_arrays(self):
        """Test plot formatting with separate x and y arrays."""
        record = (
            "plot1",
            "plot",
            [np.array([1, 2, 3]), np.array([4, 5, 6])],
            {},
        )
        result = format_record(record)
        assert isinstance(result, pd.DataFrame)
        assert "plot1_plot_x" in result.columns
        assert "plot1_plot_y" in result.columns
        assert result["plot1_plot_x"].tolist() == [1, 2, 3]
        assert result["plot1_plot_y"].tolist() == [4, 5, 6]

    def test_plot_with_2d_y_array(self):
        """Test plot formatting with 2D y array (multiple lines)."""
        record = (
            "plot1",
            "plot",
            [np.array([1, 2, 3]), np.array([[4, 7], [5, 8], [6, 9]])],
            {},
        )
        result = format_record(record)
        assert isinstance(result, pd.DataFrame)
        assert "plot1_plot_x00" in result.columns
        assert "plot1_plot_y00" in result.columns
        assert "plot1_plot_y01" in result.columns
        assert result["plot1_plot_y00"].tolist() == [4, 5, 6]
        assert result["plot1_plot_y01"].tolist() == [7, 8, 9]

    def test_plot_with_dataframe_y(self):
        """Test plot formatting with DataFrame as y values."""
        y_df = pd.DataFrame({"col1": [4, 5, 6], "col2": [7, 8, 9]})
        record = ("plot1", "plot", [np.array([1, 2, 3]), y_df], {})
        result = format_record(record)
        assert isinstance(result, pd.DataFrame)
        assert "plot1_plot_x" in result.columns
        assert "plot1_plot_y00" in result.columns
        assert "plot1_plot_y01" in result.columns
        
    def test_plot_with_xarray(self):
        """Test plot formatting with xarray DataArray."""
        y_xr = xr.DataArray(
            [[4, 7], [5, 8], [6, 9]], 
            dims=["x", "y"]
        )
        record = ("plot1", "plot", [np.array([1, 2, 3]), y_xr], {})
        result = format_record(record)
        assert isinstance(result, pd.DataFrame)
        assert "plot1_plot_x00" in result.columns
        assert "plot1_plot_y00" in result.columns
        assert "plot1_plot_y01" in result.columns
        
    def test_plot_with_list_y(self):
        """Test plot formatting with list as y values."""
        record = ("plot1", "plot", [np.array([1, 2, 3]), [4, 5, 6]], {})
        result = format_record(record)
        assert isinstance(result, pd.DataFrame)
        assert "plot1_plot_x" in result.columns
        assert "plot1_plot_y" in result.columns

    def test_bar_with_scalar_values(self):
        """Test bar formatting with scalar x and y."""
        record = ("bar1", "bar", (1, 5), {})
        result = format_record(record)
        assert isinstance(result, pd.DataFrame)
        assert "bar1_bar_x" in result.columns
        assert "bar1_bar_y" in result.columns
        assert len(result) == 1
        
    def test_bar_with_scalar_yerr(self):
        """Test bar formatting with scalar error value."""
        record = ("bar1", "bar", (["A"], [5]), {"yerr": 0.5})
        result = format_record(record)
        assert isinstance(result, pd.DataFrame)
        assert "bar1_bar_yerr" in result.columns
        assert result["bar1_bar_yerr"].iloc[0] == 0.5

    def test_boxplot(self):
        """Test boxplot formatting with single box."""
        record = ("box1", "boxplot", [[1, 2, 3, 4, 5]], {})
        result = format_record(record)
        assert isinstance(result, pd.DataFrame)
        assert "box1_boxplot_0_x" in result.columns
        assert result["box1_boxplot_0_x"].tolist() == [1, 2, 3, 4, 5]
        
    def test_boxplot_multiple(self):
        """Test boxplot formatting with multiple boxes."""
        record = ("box1", "boxplot", [[[1, 2, 3], [4, 5, 6, 7]]], {})
        result = format_record(record)
        assert isinstance(result, pd.DataFrame)
        assert "box1_boxplot_0_x" in result.columns
        assert "box1_boxplot_1_x" in result.columns
        # Check dropna behavior
        assert len(result["box1_boxplot_0_x"].dropna()) == 3
        assert len(result["box1_boxplot_1_x"].dropna()) == 4
        
    def test_boxplot_with_numpy(self):
        """Test boxplot formatting with numpy array."""
        record = ("box1", "boxplot", [np.array([1.5, 2.5, 3.5])], {})
        result = format_record(record)
        assert isinstance(result, pd.DataFrame)
        assert result.shape[1] == 1
        
    def test_plot_fillv(self):
        """Test plot_fillv formatting."""
        record = ("fill1", "plot_fillv", ([1, 3, 5], [2, 4, 6]), {})
        result = format_record(record)
        assert isinstance(result, pd.DataFrame)
        assert "fill1_plot_fillv_starts" in result.columns
        assert "fill1_plot_fillv_ends" in result.columns
        assert result["fill1_plot_fillv_starts"].tolist() == [1, 3, 5]
        assert result["fill1_plot_fillv_ends"].tolist() == [2, 4, 6]
        
    def test_plot_raster(self):
        """Test plot_raster formatting."""
        df = pd.DataFrame({"spike_times": [0.1, 0.5, 1.2]})
        record = ("raster1", "plot_raster", df, {})
        result = format_record(record)
        assert isinstance(result, pd.DataFrame)
        pd.testing.assert_frame_equal(result, df)
        
    def test_plot_ecdf(self):
        """Test plot_ecdf formatting."""
        df = pd.DataFrame({"values": [1, 2, 3, 4, 5]})
        record = ("ecdf1", "plot_ecdf", df, {})
        result = format_record(record)
        assert isinstance(result, pd.DataFrame)
        pd.testing.assert_frame_equal(result, df)
        
    def test_plot_kde(self):
        """Test plot_kde formatting."""
        df = pd.DataFrame({"density": [0.1, 0.3, 0.5, 0.3, 0.1]})
        record = ("kde1", "plot_kde", df, {})
        result = format_record(record)
        assert isinstance(result, pd.DataFrame)
        assert "kde1_plot_kde_density" in result.columns
        
    def test_plot_kde_no_id(self):
        """Test plot_kde formatting without ID."""
        df = pd.DataFrame({"density": [0.1, 0.3, 0.5]})
        record = (None, "plot_kde", df, {})
        result = format_record(record)
        assert isinstance(result, pd.DataFrame)
        assert result.columns[0] == "density"  # Original column name preserved
        
    def test_sns_barplot(self):
        """Test seaborn barplot formatting."""
        df = pd.DataFrame({
            "A": [1, 2, 3],
            "B": [2, 4, 6],
            "C": [3, 6, 9]
        })
        record = ("sns_bar1", "sns_barplot", df, {})
        result = format_record(record)
        assert isinstance(result, pd.DataFrame)
        assert result.shape == (1, 3)  # Diagonal values
        
    def test_sns_boxplot(self):
        """Test seaborn boxplot formatting."""
        df = pd.DataFrame({
            "group1": [1, 2, 3, 4],
            "group2": [5, 6, 7, 8]
        })
        record = ("sns_box1", "sns_boxplot", df, {})
        result = format_record(record)
        assert isinstance(result, pd.DataFrame)
        assert "sns_box1_sns_boxplot_group1" in result.columns
        assert "sns_box1_sns_boxplot_group2" in result.columns
        
    def test_sns_boxplot_no_id(self):
        """Test seaborn boxplot formatting without ID."""
        df = pd.DataFrame({"data": [1, 2, 3]})
        record = (None, "sns_boxplot", df, {})
        result = format_record(record)
        assert isinstance(result, pd.DataFrame)
        assert result.columns[0] == "data"
        
    def test_sns_heatmap(self):
        """Test seaborn heatmap formatting."""
        df = pd.DataFrame(np.random.rand(3, 3))
        record = ("heatmap1", "sns_heatmap", df, {})
        result = format_record(record)
        assert isinstance(result, pd.DataFrame)
        pd.testing.assert_frame_equal(result, df)
        
    def test_sns_histplot(self):
        """Test seaborn histplot formatting."""
        df = pd.DataFrame({"values": np.random.randn(100)})
        record = ("hist1", "sns_histplot", df, {})
        result = format_record(record)
        assert isinstance(result, pd.DataFrame)
        pd.testing.assert_frame_equal(result, df)
        
    def test_sns_violinplot(self):
        """Test seaborn violinplot formatting."""
        df = pd.DataFrame({
            "A": np.random.randn(50),
            "B": np.random.randn(50)
        })
        record = ("violin1", "sns_violinplot", df, {})
        result = format_record(record)
        assert isinstance(result, pd.DataFrame)
        pd.testing.assert_frame_equal(result, df)
        
    def test_unsupported_method(self):
        """Test formatting with unsupported method."""
        record = ("unknown1", "unknown_method", [1, 2, 3], {})
        result = format_record(record)
        assert result is None
        
    def test_set_method_ignored(self):
        """Test that set_ methods are ignored."""
        record = ("set1", "set_xlabel", ["X Label"], {})
        result = format_record(record)
        assert result is None


class TestFormatImshow2D:
    """Test suite for _format_imshow2d function."""
    
    def test_basic_imshow2d(self):
        """Test basic imshow2d formatting."""
        df = pd.DataFrame(np.random.rand(5, 5))
        record = ("img1", "imshow2d", df, {})
        result = _format_imshow2d(record)
        assert isinstance(result, pd.DataFrame)
        pd.testing.assert_frame_equal(result, df)
        
    def test_imshow2d_preserves_structure(self):
        """Test that imshow2d preserves DataFrame structure."""
        df = pd.DataFrame(
            np.arange(9).reshape(3, 3),
            index=["row1", "row2", "row3"],
            columns=["col1", "col2", "col3"]
        )
        record = ("img1", "imshow2d", df, {})
        result = _format_imshow2d(record)
        pd.testing.assert_frame_equal(result, df)
        assert list(result.index) == ["row1", "row2", "row3"]
        assert list(result.columns) == ["col1", "col2", "col3"]


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_none_values_in_history(self):
        """Test handling of None values in history."""
        history = {
            "plot1": ("plot1", "plot", ([1, 2, None], [4, None, 6]), {}),
        }
        result = export_as_csv(history)
        assert isinstance(result, pd.DataFrame)
        assert pd.isna(result["plot1_plot_x"].iloc[2])
        assert pd.isna(result["plot1_plot_y"].iloc[1])
        
    def test_empty_arrays(self):
        """Test handling of empty arrays."""
        history = {
            "plot1": ("plot1", "plot", ([], []), {}),
        }
        result = export_as_csv(history)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
        
    def test_mismatched_array_lengths(self):
        """Test handling of mismatched array lengths in plots."""
        # This should be handled by the plotting function, but test robustness
        record = ("plot1", "plot", ([1, 2, 3], [4, 5]), {})
        # Format record should handle this gracefully
        result = format_record(record)
        assert isinstance(result, pd.DataFrame)
        
    def test_unicode_in_labels(self):
        """Test handling of unicode characters in labels."""
        history = {
            "plot1": ("plot1", "bar", (["α", "β", "γ"], [1, 2, 3]), {})
        }
        result = export_as_csv(history)
        assert isinstance(result, pd.DataFrame)
        assert result["plot1_bar_x"].tolist() == ["α", "β", "γ"]
        
    def test_very_long_ids(self):
        """Test handling of very long plot IDs."""
        long_id = "a" * 100
        history = {
            long_id: (long_id, "plot", ([1, 2], [3, 4]), {})
        }
        result = export_as_csv(history)
        assert isinstance(result, pd.DataFrame)
        assert f"{long_id}_plot_x" in result.columns
        
    def test_special_characters_in_id(self):
        """Test handling of special characters in plot IDs."""
        special_id = "plot-1_test@#$"
        history = {
            special_id: (special_id, "plot", ([1, 2], [3, 4]), {})
        }
        result = export_as_csv(history)
        assert isinstance(result, pd.DataFrame)
        assert f"{special_id}_plot_x" in result.columns

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/plt/_subplots/_export_as_csv.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-05-18 18:14:08 (ywatanabe)"
# # File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/plt/_subplots/_export_as_csv.py
# # ----------------------------------------
# import os
# 
# __FILE__ = "./src/scitex/plt/_subplots/_export_as_csv.py"
# __DIR__ = os.path.dirname(__FILE__)
# # ----------------------------------------
# 
# import warnings
# 
# import pandas as pd
# 
# from ._export_as_csv_formatters import (_format_bar, _format_barh,
#                                         _format_boxplot, _format_contour,
#                                         _format_errorbar, _format_eventplot,
#                                         _format_fill, _format_fill_between,
#                                         _format_hist, _format_imshow,
#                                         _format_imshow2d, _format_plot,
#                                         _format_plot_box,
#                                         _format_plot_conf_mat,
#                                         _format_plot_ecdf, _format_plot_fillv,
#                                         _format_plot_heatmap,
#                                         _format_plot_image,
#                                         _format_plot_joyplot, _format_plot_kde,
#                                         _format_plot_line,
#                                         _format_plot_mean_ci,
#                                         _format_plot_mean_std,
#                                         _format_plot_median_iqr,
#                                         _format_plot_raster,
#                                         _format_plot_rectangle,
#                                         _format_plot_scatter_hist,
#                                         _format_plot_shaded_line,
#                                         _format_plot_violin, _format_scatter,
#                                         _format_sns_barplot,
#                                         _format_sns_boxplot,
#                                         _format_sns_heatmap,
#                                         _format_sns_histplot,
#                                         _format_sns_jointplot,
#                                         _format_sns_kdeplot,
#                                         _format_sns_lineplot,
#                                         _format_sns_pairplot,
#                                         _format_sns_scatterplot,
#                                         _format_sns_stripplot,
#                                         _format_sns_swarmplot,
#                                         _format_sns_violinplot, _format_violin,
#                                         _format_violinplot)
# 
# from scitex.pd import to_xyz
# 
# 
# def _to_numpy(data):
#     """Convert various data types to numpy array.
#     
#     Handles torch tensors, pandas Series/DataFrame, and other array-like objects.
#     
#     Parameters
#     ----------
#     data : array-like
#         Data to convert to numpy array
#         
#     Returns
#     -------
#     numpy.ndarray
#         Data as numpy array
#     """
#     if hasattr(data, 'numpy'):  # torch tensor
#         return data.detach().numpy() if hasattr(data, 'detach') else data.numpy()
#     elif hasattr(data, 'values'):  # pandas series/dataframe
#         return data.values
#     else:
#         return np.asarray(data)
# 
# 
# def export_as_csv(history_records):
#     """Convert plotting history records to a combined DataFrame suitable for CSV export.
# 
#     Args:
#         history_records (dict): Dictionary of plotting records.
# 
#     Returns:
#         pd.DataFrame: Combined DataFrame containing all plotting data.
# 
#     Raises:
#         ValueError: If no plotting records are found or they cannot be combined.
#     """
#     if len(history_records) <= 0:
#         warnings.warn("Plotting records not found. Cannot export empty data.")
#         return pd.DataFrame()  # Return empty DataFrame instead of None
# 
#     dfs = []
#     for record in list(history_records.values()):
#         try:
#             formatted_df = format_record(record)
#             if formatted_df is not None and not formatted_df.empty:
#                 dfs.append(formatted_df)
#         except Exception as e:
#             warnings.warn(f"Failed to format record {record[0]}: {e}")
#     
#     # If no valid dataframes were created, return an empty one
#     if not dfs:
#         warnings.warn("No valid data found to export.")
#         return pd.DataFrame()
# 
#     try:
#         df = pd.concat(dfs, axis=1)
#         return df
#     except Exception as e:
#         warnings.warn(f"Failed to combine plotting records: {e}")
#         # Return a DataFrame with metadata about what records were attempted
#         meta_df = pd.DataFrame({
#             "record_id": [r[0] for r in history_records.values()],
#             "method": [r[1] for r in history_records.values()],
#             "has_data": ["Yes" if r[2] and r[2] != {} else "No" for r in history_records.values()]
#         })
#         return meta_df
# 
# 
# def format_record(record):
#     """Route record to the appropriate formatting function based on plot method.
# 
#     Args:
#         record (tuple): Plotting record tuple (id, method, tracked_dict, kwargs).
# 
#     Returns:
#         pd.DataFrame: Formatted data for the plot record.
#     """
#     id, method, tracked_dict, kwargs = record
# 
#     # Basic Matplotlib functions
#     if method == "plot":
#         return _format_plot(id, tracked_dict, kwargs)
#     elif method == "scatter":
#         return _format_scatter(id, tracked_dict, kwargs)
#     elif method == "bar":
#         return _format_bar(id, tracked_dict, kwargs)
#     elif method == "barh":
#         return _format_barh(id, tracked_dict, kwargs)
#     elif method == "hist":
#         return _format_hist(id, tracked_dict, kwargs)
#     elif method == "boxplot":
#         return _format_boxplot(id, tracked_dict, kwargs)
#     elif method == "contour":
#         return _format_contour(id, tracked_dict, kwargs)
#     elif method == "errorbar":
#         return _format_errorbar(id, tracked_dict, kwargs)
#     elif method == "eventplot":
#         return _format_eventplot(id, tracked_dict, kwargs)
#     elif method == "fill":
#         return _format_fill(id, tracked_dict, kwargs)
#     elif method == "fill_between":
#         return _format_fill_between(id, tracked_dict, kwargs)
#     elif method == "imshow":
#         return _format_imshow(id, tracked_dict, kwargs)
#     elif method == "imshow2d":
#         return _format_imshow2d(id, tracked_dict, kwargs)
#     elif method == "violin":
#         return _format_violin(id, tracked_dict, kwargs)
#     elif method == "violinplot":
#         return _format_violinplot(id, tracked_dict, kwargs)
# 
#     # Custom plotting functions
#     elif method == "plot_box":
#         return _format_plot_box(id, tracked_dict, kwargs)
#     elif method == "plot_conf_mat":
#         return _format_plot_conf_mat(id, tracked_dict, kwargs)
#     elif method == "plot_ecdf":
#         return _format_plot_ecdf(id, tracked_dict, kwargs)
#     elif method == "plot_fillv":
#         return _format_plot_fillv(id, tracked_dict, kwargs)
#     elif method == "plot_heatmap":
#         return _format_plot_heatmap(id, tracked_dict, kwargs)
#     elif method == "plot_image":
#         return _format_plot_image(id, tracked_dict, kwargs)
#     elif method == "plot_joyplot":
#         return _format_plot_joyplot(id, tracked_dict, kwargs)
#     elif method == "plot_kde":
#         return _format_plot_kde(id, tracked_dict, kwargs)
#     elif method == "plot_line":
#         return _format_plot_line(id, tracked_dict, kwargs)
#     elif method == "plot_mean_ci":
#         return _format_plot_mean_ci(id, tracked_dict, kwargs)
#     elif method == "plot_mean_std":
#         return _format_plot_mean_std(id, tracked_dict, kwargs)
#     elif method == "plot_median_iqr":
#         return _format_plot_median_iqr(id, tracked_dict, kwargs)
#     elif method == "plot_raster":
#         return _format_plot_raster(id, tracked_dict, kwargs)
#     elif method == "plot_rectangle":
#         return _format_plot_rectangle(id, tracked_dict, kwargs)
#     elif method == "plot_scatter_hist":
#         return _format_plot_scatter_hist(id, tracked_dict, kwargs)
#     elif method == "plot_shaded_line":
#         return _format_plot_shaded_line(id, tracked_dict, kwargs)
#     elif method == "plot_violin":
#         return _format_plot_violin(id, tracked_dict, kwargs)
# 
#     # Seaborn functions
#     elif method == "sns_barplot":
#         return _format_sns_barplot(id, tracked_dict, kwargs)
#     elif method == "sns_boxplot":
#         return _format_sns_boxplot(id, tracked_dict, kwargs)
#     elif method == "sns_heatmap":
#         return _format_sns_heatmap(id, tracked_dict, kwargs)
#     elif method == "sns_histplot":
#         return _format_sns_histplot(id, tracked_dict, kwargs)
#     elif method == "sns_jointplot":
#         return _format_sns_jointplot(id, tracked_dict, kwargs)
#     elif method == "sns_kdeplot":
#         return _format_sns_kdeplot(id, tracked_dict, kwargs)
#     elif method == "sns_lineplot":
#         return _format_sns_lineplot(id, tracked_dict, kwargs)
#     elif method == "sns_pairplot":
#         return _format_sns_pairplot(id, tracked_dict, kwargs)
#     elif method == "sns_scatterplot":
#         return _format_sns_scatterplot(id, tracked_dict, kwargs)
#     elif method == "sns_stripplot":
#         return _format_sns_stripplot(id, tracked_dict, kwargs)
#     elif method == "sns_swarmplot":
#         return _format_sns_swarmplot(id, tracked_dict, kwargs)
#     elif method == "sns_violinplot":
#         return _format_sns_violinplot(id, tracked_dict, kwargs)
#     else:
#         # Unknown or unimplemented method
#         raise NotImplementedError(
#             f"CSV export for plot method '{method}' is not yet implemented in the scitex.plt module. "
#             f"Check the feature-request-export-as-csv-functions.md for implementation status."
#         )
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/plt/_subplots/_export_as_csv.py
# --------------------------------------------------------------------------------
