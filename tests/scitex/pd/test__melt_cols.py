#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-03 10:45:00 (ywatanabe)"
# File: ./tests/scitex/pd/test__melt_cols.py

import pytest
import numpy as np
import pandas as pd
from unittest.mock import Mock, patch
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../src"))

from scitex.pd import melt_cols


class TestBasicFunctionality:
    """Test basic functionality of melt_cols."""

    def test_simple_melt(self):
        """Test basic melting of columns."""
        df = pd.DataFrame(
            {
                "id": [1, 2, 3],
                "name": ["A", "B", "C"],
                "score_1": [10, 20, 30],
                "score_2": [15, 25, 35],
            }
        )

        result = melt_cols(df, cols=["score_1", "score_2"])

        assert len(result) == 6  # 3 rows * 2 columns
        assert "variable" in result.columns
        assert "value" in result.columns
        assert "id" in result.columns
        assert "name" in result.columns

        # Check first few rows
        assert result.iloc[0]["id"] == 1
        assert result.iloc[0]["name"] == "A"
        assert result.iloc[0]["variable"] == "score_1"
        assert result.iloc[0]["value"] == 10

    def test_single_column_melt(self):
        """Test melting a single column."""
        df = pd.DataFrame({"id": [1, 2], "value": [100, 200]})

        result = melt_cols(df, cols=["value"])

        assert len(result) == 2
        assert result["variable"].unique() == ["value"]
        # When melting a column named "value", the melted values are in "melted_value"
        assert list(result["melted_value"]) == [100, 200]
        assert list(result["id"]) == [1, 2]

    def test_multiple_id_columns(self):
        """Test with multiple identifier columns."""
        df = pd.DataFrame(
            {
                "year": [2020, 2021, 2022],
                "month": [1, 2, 3],
                "category": ["A", "B", "C"],
                "sales": [100, 200, 300],
                "costs": [50, 100, 150],
            }
        )

        result = melt_cols(df, cols=["sales", "costs"])

        assert len(result) == 6
        # All identifier columns should be preserved
        assert "year" in result.columns
        assert "month" in result.columns
        assert "category" in result.columns

        # Check data integrity
        sales_rows = result[result["variable"] == "sales"]
        assert list(sales_rows["value"]) == [100, 200, 300]


class TestIdColumnParameter:
    """Test id_columns parameter functionality."""

    def test_explicit_id_columns(self):
        """Test with explicitly specified id columns."""
        df = pd.DataFrame(
            {
                "id": [1, 2],
                "name": ["A", "B"],
                "extra": ["X", "Y"],
                "val1": [10, 20],
                "val2": [30, 40],
            }
        )

        result = melt_cols(df, cols=["val1", "val2"], id_columns=["id", "name"])

        # Should only have specified id columns
        assert "id" in result.columns
        assert "name" in result.columns
        assert "extra" not in result.columns
        assert len(result) == 4

    def test_empty_id_columns(self):
        """Test with empty id columns list."""
        df = pd.DataFrame({"a": [1, 2], "b": [3, 4], "c": [5, 6]})

        result = melt_cols(df, cols=["a", "b"], id_columns=[])

        # Should only have variable and value columns
        assert set(result.columns) == {"variable", "value"}
        assert len(result) == 4

    def test_auto_id_columns(self):
        """Test automatic detection of id columns."""
        df = pd.DataFrame(
            {
                "id": [1, 2, 3],
                "group": ["A", "B", "C"],
                "metric1": [10, 20, 30],
                "metric2": [40, 50, 60],
                "metric3": [70, 80, 90],
            }
        )

        result = melt_cols(df, cols=["metric1", "metric2", "metric3"])

        # Should automatically use non-melted columns as id
        assert "id" in result.columns
        assert "group" in result.columns
        assert len(result) == 9  # 3 rows * 3 metrics


class TestDataTypes:
    """Test handling of different data types."""

    def test_mixed_data_types(self):
        """Test with mixed data types in melted columns."""
        df = pd.DataFrame(
            {
                "id": [1, 2],
                "int_col": [10, 20],
                "float_col": [1.5, 2.5],
                "str_col": ["a", "b"],
                "bool_col": [True, False],
            }
        )

        result = melt_cols(df, cols=["int_col", "float_col", "str_col", "bool_col"])

        assert len(result) == 8  # 2 rows * 4 columns
        # Value column should handle mixed types
        assert 10 in result["value"].values
        assert 1.5 in result["value"].values
        assert "a" in result["value"].values
        assert True in result["value"].values

    def test_datetime_columns(self):
        """Test with datetime columns."""
        df = pd.DataFrame(
            {
                "id": [1, 2],
                "date1": pd.to_datetime(["2023-01-01", "2023-01-02"]),
                "date2": pd.to_datetime(["2023-02-01", "2023-02-02"]),
            }
        )

        result = melt_cols(df, cols=["date1", "date2"])

        assert len(result) == 4
        assert pd.api.types.is_datetime64_any_dtype(result["value"])

    def test_categorical_data(self):
        """Test with categorical data."""
        df = pd.DataFrame(
            {
                "id": [1, 2, 3],
                "cat1": pd.Categorical(["A", "B", "C"]),
                "cat2": pd.Categorical(["X", "Y", "Z"]),
            }
        )

        result = melt_cols(df, cols=["cat1", "cat2"])

        assert len(result) == 6
        # When melting multiple categorical columns, pandas converts to object dtype
        assert result["value"].dtype == object
        # But the values themselves are still from the original categories
        assert set(result["value"]) == {"A", "B", "C", "X", "Y", "Z"}


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_missing_columns_error(self):
        """Test error when specified columns don't exist."""
        df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})

        with pytest.raises(ValueError, match="Columns not found"):
            melt_cols(df, cols=["c", "d"])

    def test_partial_missing_columns(self):
        """Test error with partially missing columns."""
        df = pd.DataFrame({"a": [1, 2], "b": [3, 4], "c": [5, 6]})

        with pytest.raises(ValueError, match="Columns not found.*{'d'}"):
            melt_cols(df, cols=["a", "b", "d"])

    def test_empty_dataframe(self):
        """Test with empty DataFrame."""
        df = pd.DataFrame()

        with pytest.raises(ValueError, match="Columns not found"):
            melt_cols(df, cols=["a"])

    def test_single_row(self):
        """Test with single row DataFrame."""
        df = pd.DataFrame({"id": [1], "val1": [10], "val2": [20]})

        result = melt_cols(df, cols=["val1", "val2"])

        assert len(result) == 2
        assert list(result["value"]) == [10, 20]

    def test_all_columns_melted(self):
        """Test melting all columns."""
        df = pd.DataFrame({"a": [1, 2], "b": [3, 4], "c": [5, 6]})

        result = melt_cols(df, cols=["a", "b", "c"])

        # Should have no id columns except for internal index handling
        assert set(result.columns) == {"variable", "value"}
        assert len(result) == 6


class TestNullHandling:
    """Test handling of null values."""

    def test_null_in_melted_columns(self):
        """Test null values in columns being melted."""
        df = pd.DataFrame(
            {"id": [1, 2, 3], "val1": [10, np.nan, 30], "val2": [np.nan, 20, np.nan]}
        )

        result = melt_cols(df, cols=["val1", "val2"])

        assert len(result) == 6
        assert result["value"].isna().sum() == 3

    def test_null_in_id_columns(self):
        """Test null values in identifier columns."""
        df = pd.DataFrame(
            {"id": [1, np.nan, 3], "name": ["A", "B", None], "value": [10, 20, 30]}
        )

        result = melt_cols(df, cols=["value"])

        assert len(result) == 3
        assert pd.isna(result.iloc[1]["id"])
        assert result.iloc[2]["name"] is None


class TestIndexHandling:
    """Test DataFrame index handling."""

    def test_non_default_index(self):
        """Test with non-default index."""
        df = pd.DataFrame(
            {"val1": [10, 20, 30], "val2": [40, 50, 60]}, index=["a", "b", "c"]
        )

        result = melt_cols(df, cols=["val1", "val2"])

        # Should reset index and handle properly
        assert len(result) == 6
        assert result.index.tolist() == list(range(6))

    def test_multiindex(self):
        """Test with MultiIndex DataFrame."""
        arrays = [["A", "A", "B", "B"], [1, 2, 1, 2]]
        index = pd.MultiIndex.from_arrays(arrays, names=("letter", "number"))
        df = pd.DataFrame(
            {"val1": [10, 20, 30, 40], "val2": [50, 60, 70, 80]}, index=index
        )

        result = melt_cols(df, cols=["val1", "val2"])

        # Should handle MultiIndex by resetting
        assert len(result) == 8
        assert isinstance(result.index, pd.RangeIndex)


class TestOrderPreservation:
    """Test order preservation in results."""

    def test_row_order_preservation(self):
        """Test that row order is preserved."""
        df = pd.DataFrame(
            {
                "id": [3, 1, 2],
                "name": ["C", "A", "B"],
                "val1": [30, 10, 20],
                "val2": [60, 40, 50],
            }
        )

        result = melt_cols(df, cols=["val1", "val2"])

        # First 3 rows should be val1 in original order
        val1_rows = result[result["variable"] == "val1"]
        assert list(val1_rows["id"]) == [3, 1, 2]
        assert list(val1_rows["value"]) == [30, 10, 20]

    def test_column_order_in_result(self):
        """Test column order in result."""
        df = pd.DataFrame({"z": [1, 2], "a": [3, 4], "val1": [5, 6], "val2": [7, 8]})

        result = melt_cols(df, cols=["val1", "val2"], id_columns=["a", "z"])

        # Check that columns are in a sensible order
        cols = list(result.columns)
        assert "variable" in cols
        assert "value" in cols
        assert "a" in cols
        assert "z" in cols


class TestRealWorldScenarios:
    """Test real-world use cases."""

    def test_time_series_reshape(self):
        """Test reshaping time series data."""
        df = pd.DataFrame(
            {
                "date": pd.date_range("2023-01-01", periods=3),
                "location": ["NYC", "LA", "CHI"],
                "temp_morning": [32, 65, 40],
                "temp_afternoon": [45, 78, 55],
                "temp_evening": [38, 70, 42],
            }
        )

        result = melt_cols(df, cols=["temp_morning", "temp_afternoon", "temp_evening"])

        assert len(result) == 9  # 3 locations * 3 time periods
        # Check that date and location are preserved for each measurement
        nyc_temps = result[result["location"] == "NYC"]
        assert len(nyc_temps) == 3
        assert set(nyc_temps["variable"]) == {
            "temp_morning",
            "temp_afternoon",
            "temp_evening",
        }

    def test_survey_data_reshape(self):
        """Test reshaping survey response data."""
        df = pd.DataFrame(
            {
                "respondent_id": [1, 2, 3],
                "age": [25, 35, 45],
                "gender": ["M", "F", "M"],
                "q1_satisfaction": [4, 5, 3],
                "q2_satisfaction": [5, 4, 4],
                "q3_satisfaction": [3, 5, 2],
            }
        )

        result = melt_cols(
            df, cols=["q1_satisfaction", "q2_satisfaction", "q3_satisfaction"]
        )

        assert len(result) == 9
        # All respondent info should be preserved
        assert "respondent_id" in result.columns
        assert "age" in result.columns
        assert "gender" in result.columns

        # Check specific respondent
        resp1 = result[result["respondent_id"] == 1]
        assert list(resp1["value"]) == [4, 5, 3]


class TestDocstringExample:
    """Test the example from the docstring."""

    def test_docstring_example(self):
        """Test exact example from docstring."""
        data = pd.DataFrame(
            {
                "id": [1, 2, 3],
                "name": ["Alice", "Bob", "Charlie"],
                "score_1": [85, 90, 78],
                "score_2": [92, 88, 95],
            }
        )

        melted = melt_cols(data, cols=["score_1", "score_2"])

        # Check structure
        assert len(melted) == 6
        assert set(melted.columns) == {"id", "name", "variable", "value"}

        # Check specific values from docstring output
        assert melted.iloc[0]["id"] == 1
        assert melted.iloc[0]["name"] == "Alice"
        assert melted.iloc[0]["variable"] == "score_1"
        assert melted.iloc[0]["value"] == 85

        assert melted.iloc[3]["id"] == 1
        assert melted.iloc[3]["name"] == "Alice"
        assert melted.iloc[3]["variable"] == "score_2"
        assert melted.iloc[3]["value"] == 92


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
