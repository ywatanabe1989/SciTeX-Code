#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Comprehensive tests for scitex.pd module.

This module contains comprehensive tests for all pandas-related utilities
in the scitex.pd module, covering DataFrame manipulation, column operations,
data transformations, and utility functions.
"""

import pytest
import pandas as pd
import numpy as np
import warnings
import scitex.pd


class TestDataFrameCreation:
    """Test DataFrame creation and conversion utilities."""

    def test_force_df_with_series(self):
        """Test force_df with pandas Series."""
        series = pd.Series([1, 2, 3], name="values")
        df = scitex.pd.force_df(series)

        assert isinstance(df, pd.DataFrame)
        assert df.shape == (3, 1)
        assert "values" in df.columns
        assert df["values"].tolist() == [1, 2, 3]

    def test_force_df_with_dataframe(self):
        """Test force_df with existing DataFrame."""
        original_df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
        df = scitex.pd.force_df(original_df)

        assert isinstance(df, pd.DataFrame)
        pd.testing.assert_frame_equal(df, original_df)

    def test_force_df_with_dict(self):
        """Test force_df with dictionary."""
        data_dict = {"col1": [1, 2, 3], "col2": [4, 5, 6]}
        df = scitex.pd.force_df(data_dict)

        assert isinstance(df, pd.DataFrame)
        assert df.shape == (3, 2)
        assert set(df.columns) == {"col1", "col2"}

    def test_force_df_with_list(self):
        """Test force_df with list."""
        data_list = [1, 2, 3, 4, 5]
        df = scitex.pd.force_df(data_list)

        assert isinstance(df, pd.DataFrame)
        assert df.shape == (5, 1)
        assert df.iloc[:, 0].tolist() == data_list

    def test_force_df_with_numpy_array(self):
        """Test force_df with numpy array."""
        arr = np.array([[1, 2], [3, 4], [5, 6]])
        df = scitex.pd.force_df(arr)

        assert isinstance(df, pd.DataFrame)
        assert df.shape == (3, 2)
        np.testing.assert_array_equal(df.values, arr)


class TestColumnOperations:
    """Test column manipulation functions."""

    def test_merge_columns_basic(self):
        """Test merging columns with default separator."""
        df = pd.DataFrame({"first": ["John", "Jane"], "last": ["Doe", "Smith"]})

        result = scitex.pd.merge_columns(df, ["first", "last"])
        assert "merged" in result.columns
        assert result["merged"].tolist() == [
            "first-John_last-Doe",
            "first-Jane_last-Smith",
        ]

    def test_merge_columns_custom_separator(self):
        """Test merging columns with custom separator."""
        df = pd.DataFrame(
            {"year": [2023, 2024], "month": ["Jan", "Feb"], "day": [15, 20]}
        )

        result = scitex.pd.merge_columns(df, ["year", "month", "day"], sep1="|", sep2="=")
        assert "merged" in result.columns
        assert result["merged"].tolist() == [
            "year=2023|month=Jan|day=15",
            "year=2024|month=Feb|day=20",
        ]

    def test_melt_cols(self):
        """Test melting columns."""
        # Create wide format data
        df = pd.DataFrame(
            {
                "id": [1, 2],
                "A_value": [10, 20],
                "B_value": [30, 40],
                "C_value": [50, 60],
            }
        )

        # Melt specific columns
        melted = scitex.pd.melt_cols(df, cols=["A_value", "B_value", "C_value"])

        assert "variable" in melted.columns
        assert "value" in melted.columns
        assert "id" in melted.columns  # id should be preserved
        assert len(melted) == 6  # 2 ids * 3 variables

    def test_mv_to_first(self):
        """Test moving column to first position."""
        df = pd.DataFrame({"a": [1, 2], "b": [3, 4], "c": [5, 6], "d": [7, 8]})

        result = scitex.pd.mv_to_first(df, "c")
        assert list(result.columns) == ["c", "a", "b", "d"]
        pd.testing.assert_series_equal(result["c"], df["c"])

    def test_mv_to_last(self):
        """Test moving column to last position."""
        df = pd.DataFrame({"a": [1, 2], "b": [3, 4], "c": [5, 6], "d": [7, 8]})

        result = scitex.pd.mv_to_last(df, "b")
        assert list(result.columns) == ["a", "c", "d", "b"]
        pd.testing.assert_series_equal(result["b"], df["b"])


class TestDataTransformations:
    """Test data transformation functions."""

    def test_to_numeric_basic(self):
        """Test converting columns to numeric."""
        df = pd.DataFrame(
            {
                "numbers": ["1", "2", "3"],
                "mixed": ["1", "2.5", "three"],
                "text": ["a", "b", "c"],
            }
        )

        result = scitex.pd.to_numeric(df)

        # Check that numeric strings are converted
        assert pd.api.types.is_numeric_dtype(result["numbers"])
        assert result["numbers"].tolist() == [1, 2, 3]

        # Mixed column should handle non-numeric as NaN
        assert pd.api.types.is_numeric_dtype(result["mixed"])
        assert result["mixed"][:2].tolist() == [1.0, 2.5]
        assert pd.isna(result["mixed"].iloc[2])

    def test_to_xyz_format(self):
        """Test converting DataFrame to xyz format."""
        # Create a pivot table-like DataFrame
        df = pd.DataFrame(
            {"A": [1, 2, 3], "B": [4, 5, 6], "C": [7, 8, 9]}, index=["X", "Y", "Z"]
        )

        xyz = scitex.pd.to_xyz(df)

        assert "x" in xyz.columns
        assert "y" in xyz.columns
        assert "z" in xyz.columns
        assert len(xyz) == 9  # 3x3 matrix = 9 points

    def test_from_xyz_format(self):
        """Test converting from xyz format to DataFrame."""
        xyz = pd.DataFrame(
            {"x": ["A", "A", "B", "B"], "y": ["X", "Y", "X", "Y"], "z": [1, 2, 3, 4]}
        )

        df = scitex.pd.from_xyz(xyz)

        assert isinstance(df, pd.DataFrame)
        assert df.shape == (2, 2)  # 2x2 matrix
        assert df.loc["X", "A"] == 1
        assert df.loc["Y", "B"] == 4

    def test_to_xy_format(self):
        """Test converting DataFrame to xy format (no z values)."""
        df = pd.DataFrame(
            {"col1": [1, 0, 1], "col2": [0, 1, 0], "col3": [1, 1, 0]},
            index=["row1", "row2", "row3"],
        )

        xy = scitex.pd.to_xy(df)

        assert "x" in xy.columns
        assert "y" in xy.columns
        assert len(xy) > 0


class TestSearchAndFilter:
    """Test search and filtering functions."""

    def test_find_indi_exact_match(self):
        """Test finding indices with exact match."""
        df = pd.DataFrame(
            {"name": ["Alice", "Bob", "Charlie", "David"], "age": [25, 30, 35, 30]}
        )

        # Find by single column value
        indices = scitex.pd.find_indi(df, {"name": "Bob"})
        assert indices == [1]

        # Find by multiple criteria
        indices = scitex.pd.find_indi(df, {"age": 30})
        assert indices == [1, 3]

    def test_find_indi_multiple_conditions(self):
        """Test finding indices with multiple conditions."""
        df = pd.DataFrame(
            {
                "category": ["A", "B", "A", "B"],
                "value": [10, 20, 30, 40],
                "status": ["active", "active", "inactive", "active"],
            }
        )

        indices = scitex.pd.find_indi(df, {"category": "B", "status": "active"})
        assert indices == [1, 3]

    def test_find_pval_columns(self):
        """Test finding p-value columns."""
        df = pd.DataFrame(
            {
                "treatment": ["A", "B", "C"],
                "pval": [0.05, 0.01, 0.001],
                "p_value": [0.1, 0.2, 0.3],
                "pval_adjusted": [0.06, 0.02, 0.002],
                "significance": ["ns", "*", "**"],
            }
        )

        pval_cols = scitex.pd.find_pval(df)
        assert "pval" in pval_cols
        assert "p_value" in pval_cols
        assert "pval_adjusted" in pval_cols
        assert "significance" not in pval_cols


class TestDataManipulation:
    """Test data manipulation utilities."""

    def test_slice_dataframe(self):
        """Test slicing DataFrame."""
        df = pd.DataFrame({"a": range(10), "b": range(10, 20), "c": range(20, 30)})

        # Slice rows
        sliced = scitex.pd.slice(df, slice(2, 5))
        assert len(sliced) == 3
        assert sliced.index.tolist() == [2, 3, 4]

        # Slice with step
        sliced = scitex.pd.slice(df, slice(0, 10, 2))
        assert len(sliced) == 5
        assert sliced.index.tolist() == [0, 2, 4, 6, 8]

    def test_sort_dataframe(self):
        """Test sorting DataFrame."""
        df = pd.DataFrame(
            {
                "name": ["Charlie", "Alice", "Bob"],
                "score": [85, 95, 90],
                "rank": [3, 1, 2],
            }
        )

        # Sort by single column
        sorted_df = scitex.pd.sort(df, "name")
        assert sorted_df["name"].tolist() == ["Alice", "Bob", "Charlie"]

        # Sort by multiple columns
        sorted_df = scitex.pd.sort(df, ["rank", "score"])
        assert sorted_df["rank"].tolist() == [1, 2, 3]

    def test_round_dataframe(self):
        """Test rounding DataFrame values."""
        df = pd.DataFrame(
            {
                "float_col": [1.234, 2.567, 3.891],
                "int_col": [1, 2, 3],
                "mixed": [1.1, 2, 3.333],
            }
        )

        # Round to 2 decimal places
        rounded = scitex.pd.round(df, 2)
        assert rounded["float_col"].tolist() == [1.23, 2.57, 3.89]
        assert rounded["mixed"].tolist() == [1.1, 2.0, 3.33]

    def test_replace_values(self):
        """Test replacing values in DataFrame."""
        df = pd.DataFrame(
            {"category": ["A", "B", "A", "C", "B"], "value": [1, 2, 1, 3, 2]}
        )

        # Replace single value
        replaced = scitex.pd.replace(df, "A", "Group_A")
        assert "Group_A" in replaced["category"].values
        assert "A" not in replaced["category"].values

        # Replace multiple values
        replaced = scitex.pd.replace(df, {1: 10, 2: 20})
        assert replaced["value"].tolist() == [10, 20, 10, 3, 20]


class TestUtilities:
    """Test utility functions."""

    def test_ignore_setting_with_copy_warning(self):
        """Test ignoring SettingWithCopyWarning."""
        # This should not raise a warning
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            df = pd.DataFrame({"a": [1, 2, 3]})
            df_view = df[df["a"] > 1]

            with scitex.pd.ignore_SettingWithCopyWarning():
                df_view["a"] = 100

            # Check no SettingWithCopyWarning was raised
            setting_warnings = [
                warning
                for warning in w
                if issubclass(warning.category, pd.errors.SettingWithCopyWarning)
            ]
            assert len(setting_warnings) == 0


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_dataframe(self):
        """Test functions with empty DataFrame."""
        empty_df = pd.DataFrame()

        # force_df should handle empty DataFrame
        result = scitex.pd.force_df(empty_df)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0

        # find_indi should return empty list
        indices = scitex.pd.find_indi(empty_df, {})
        assert indices == []

    def test_single_row_dataframe(self):
        """Test functions with single row DataFrame."""
        single_row = pd.DataFrame({"a": [1], "b": [2]})

        # Test various operations
        sorted_df = scitex.pd.sort(single_row, "a")
        assert len(sorted_df) == 1

        rounded = scitex.pd.round(single_row, 0)
        assert len(rounded) == 1

    def test_none_and_nan_handling(self):
        """Test handling of None and NaN values."""
        df = pd.DataFrame(
            {"col1": [1, None, 3], "col2": [None, 2, None], "col3": [1, 2, 3]}
        )

        # to_numeric should handle None as NaN
        numeric = scitex.pd.to_numeric(df)
        assert pd.isna(numeric["col1"].iloc[1])
        assert pd.isna(numeric["col2"].iloc[0])

    def test_mixed_types(self):
        """Test handling mixed data types."""
        df = pd.DataFrame({"mixed": [1, "2", 3.0, True, None]})

        # force_df should preserve the DataFrame
        result = scitex.pd.force_df(df)
        assert len(result) == 5

        # to_numeric should convert what it can
        numeric = scitex.pd.to_numeric(result)
        assert numeric["mixed"].iloc[0] == 1
        assert numeric["mixed"].iloc[1] == 2
        assert numeric["mixed"].iloc[2] == 3.0
        assert numeric["mixed"].iloc[3] == 1  # True -> 1


class TestIntegration:
    """Test integration scenarios combining multiple functions."""

    def test_data_pipeline(self):
        """Test a typical data processing pipeline."""
        # Start with raw data
        raw_data = {
            "first_name": ["John", "Jane", "Bob"],
            "last_name": ["Doe", "Smith", "Jones"],
            "score_1": ["95", "87", "92"],
            "score_2": ["88", "91", "85"],
            "score_3": ["90", "89", "88"],
        }

        # Convert to DataFrame
        df = scitex.pd.force_df(raw_data)

        # Merge name columns
        df = scitex.pd.merge_columns(df, ["first_name", "last_name"], sep=" ")

        # Convert scores to numeric (keep text columns as is)
        df = scitex.pd.to_numeric(df, errors="ignore")

        # Calculate average score
        score_cols = [col for col in df.columns if "score" in col]
        df["avg_score"] = df[score_cols].mean(axis=1)

        # Round averages
        df = scitex.pd.round(df, 1)

        # Sort by average score
        df = scitex.pd.sort(df, "avg_score", ascending=False)

        # Verify pipeline results
        assert "first_name_last_name" in df.columns
        assert df["first_name_last_name"].iloc[0] in [
            "John Doe",
            "Jane Smith",
            "Bob Jones",
        ]
        assert "avg_score" in df.columns
        assert all(isinstance(score, (int, float)) for score in df["avg_score"])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
