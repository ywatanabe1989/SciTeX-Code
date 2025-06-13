#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-03 11:00:00 (ywatanabe)"
# File: ./tests/scitex/pd/test__merge_columns.py

import pytest
import numpy as np
import pandas as pd
from unittest.mock import Mock, patch
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../src"))

from scitex.pd import merge_columns, merge_cols


class TestBasicFunctionality:
    """Test basic functionality of merge_columns."""

    def test_simple_merge_with_sep(self):
        """Test basic merging with simple separator."""
        df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6], "C": [7, 8, 9]})

        result = merge_columns(df, "A", "B", sep=" ")

        assert "A_B" in result.columns
        assert list(result["A_B"]) == ["1 4", "2 5", "3 6"]
        # Original columns preserved
        assert "A" in result.columns
        assert "B" in result.columns

    def test_merge_with_column_labels(self):
        """Test merging with column labels (default behavior)."""
        df = pd.DataFrame({"A": [0, 5, 10], "B": [1, 6, 11]})

        result = merge_columns(df, "A", "B")

        assert "merged" in result.columns
        assert result["merged"].iloc[0] == "A-0_B-1"
        assert result["merged"].iloc[1] == "A-5_B-6"
        assert result["merged"].iloc[2] == "A-10_B-11"

    def test_merge_multiple_columns(self):
        """Test merging more than two columns."""
        df = pd.DataFrame({"X": [1, 2], "Y": [3, 4], "Z": [5, 6]})

        result = merge_columns(df, "X", "Y", "Z", sep=",")

        assert "X_Y_Z" in result.columns
        assert result["X_Y_Z"].iloc[0] == "1,3,5"
        assert result["X_Y_Z"].iloc[1] == "2,4,6"

    def test_merge_cols_alias(self):
        """Test that merge_cols is an alias for merge_columns."""
        df = pd.DataFrame({"A": [1], "B": [2]})

        result1 = merge_columns(df, "A", "B", sep=" ")
        result2 = merge_cols(df, "A", "B", sep=" ")

        pd.testing.assert_frame_equal(result1, result2)


class TestParameterVariations:
    """Test different parameter combinations."""

    def test_custom_separators(self):
        """Test custom sep1 and sep2 parameters."""
        df = pd.DataFrame({"col1": [10, 20], "col2": [30, 40]})

        result = merge_columns(df, "col1", "col2", sep1=" & ", sep2="=")

        assert result["merged"].iloc[0] == "col1=10 & col2=30"
        assert result["merged"].iloc[1] == "col1=20 & col2=40"

    def test_custom_name(self):
        """Test custom name for merged column."""
        df = pd.DataFrame({"first": ["John", "Jane"], "last": ["Doe", "Smith"]})

        result = merge_columns(df, "first", "last", sep=" ", name="full_name")

        assert "full_name" in result.columns
        assert result["full_name"].iloc[0] == "John Doe"
        assert result["full_name"].iloc[1] == "Jane Smith"

    def test_list_input(self):
        """Test passing columns as a list."""
        df = pd.DataFrame({"A": [1, 2], "B": [3, 4], "C": [5, 6]})

        result = merge_columns(df, ["A", "B", "C"], sep="-")

        assert "A_B_C" in result.columns
        assert result["A_B_C"].iloc[0] == "1-3-5"

    def test_tuple_input(self):
        """Test passing columns as a tuple."""
        df = pd.DataFrame({"X": [7, 8], "Y": [9, 10]})

        result = merge_columns(df, ("X", "Y"), sep="/")

        assert "X_Y" in result.columns
        assert result["X_Y"].iloc[0] == "7/9"


class TestDataTypes:
    """Test handling of different data types."""

    def test_numeric_columns(self):
        """Test merging numeric columns."""
        df = pd.DataFrame({"int_col": [1, 2, 3], "float_col": [1.5, 2.5, 3.5]})

        result = merge_columns(df, "int_col", "float_col", sep=" | ")

        assert result["int_col_float_col"].iloc[0] == "1 | 1.5"
        assert result["int_col_float_col"].iloc[1] == "2 | 2.5"

    def test_mixed_types(self):
        """Test merging columns with mixed types."""
        df = pd.DataFrame(
            {
                "str": ["a", "b"],
                "int": [1, 2],
                "float": [3.14, 2.71],
                "bool": [True, False],
            }
        )

        result = merge_columns(df, "str", "int", "float", "bool", sep=",")

        assert "str_int_float_bool" in result.columns
        assert result["str_int_float_bool"].iloc[0] == "a,1,3.14,True"
        assert result["str_int_float_bool"].iloc[1] == "b,2,2.71,False"

    def test_datetime_columns(self):
        """Test merging datetime columns."""
        df = pd.DataFrame(
            {
                "date": pd.to_datetime(["2023-01-01", "2023-01-02"]),
                "time": ["10:00", "11:00"],
            }
        )

        result = merge_columns(df, "date", "time", sep=" ")

        assert "date_time" in result.columns
        # Datetime will be converted to string
        assert "2023-01-01" in result["date_time"].iloc[0]
        assert "10:00" in result["date_time"].iloc[0]

    def test_null_values(self):
        """Test handling of null values."""
        df = pd.DataFrame({"A": [1, None, 3], "B": ["x", "y", None]})

        result = merge_columns(df, "A", "B", sep="-")

        # None becomes 'None' when converted to string
        assert result["A_B"].iloc[0] == "1-x"
        assert result["A_B"].iloc[1] == "None-y"
        assert result["A_B"].iloc[2] == "3-None"


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_no_columns_error(self):
        """Test error when no columns specified."""
        df = pd.DataFrame({"A": [1, 2]})

        with pytest.raises(ValueError, match="No columns specified"):
            merge_columns(df)

    def test_missing_columns_error(self):
        """Test error when columns don't exist."""
        df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})

        with pytest.raises(KeyError, match="Columns not found.*\\['C', 'D'\\]"):
            merge_columns(df, "A", "C", "D")

    def test_single_column(self):
        """Test merging a single column (edge case)."""
        df = pd.DataFrame({"A": [1, 2, 3]})

        result = merge_columns(df, "A", sep=" ")

        assert "A" in result.columns  # Original column name when single column
        # When only one column, it just converts to string
        assert list(result["A"]) == ["1", "2", "3"]

    def test_empty_dataframe(self):
        """Test with empty DataFrame."""
        df = pd.DataFrame({"A": [], "B": []})

        result = merge_columns(df, "A", "B", sep=" ")

        assert "A_B" in result.columns
        assert len(result) == 0

    def test_large_number_of_columns(self):
        """Test merging many columns."""
        # Create DataFrame with 10 columns
        data = {f"col{i}": list(range(3)) for i in range(10)}
        df = pd.DataFrame(data)

        cols = [f"col{i}" for i in range(10)]
        result = merge_columns(df, *cols, sep=",")

        expected_name = "_".join(cols)
        assert expected_name in result.columns
        # First row should be '0,0,0,...'
        assert result[expected_name].iloc[0] == ",".join(["0"] * 10)


class TestSpecialCharacters:
    """Test handling of special characters."""

    def test_columns_with_spaces(self):
        """Test columns with spaces in names."""
        df = pd.DataFrame(
            {"First Name": ["John", "Jane"], "Last Name": ["Doe", "Smith"]}
        )

        result = merge_columns(df, "First Name", "Last Name", sep=" ")

        assert "First Name_Last Name" in result.columns
        assert result["First Name_Last Name"].iloc[0] == "John Doe"

    def test_special_separators(self):
        """Test with special character separators."""
        df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})

        # Test various special separators
        result1 = merge_columns(df, "A", "B", sep="||")
        assert result1["A_B"].iloc[0] == "1||3"

        result2 = merge_columns(df, "A", "B", sep="\t")
        assert result2["A_B"].iloc[0] == "1\t3"

        result3 = merge_columns(df, "A", "B", sep="\n")
        assert result3["A_B"].iloc[0] == "1\n3"

    def test_unicode_content(self):
        """Test with Unicode content."""
        df = pd.DataFrame(
            {"name": ["José", "François"], "city": ["São Paulo", "Montréal"]}
        )

        result = merge_columns(df, "name", "city", sep=" - ")

        assert result["name_city"].iloc[0] == "José - São Paulo"
        assert result["name_city"].iloc[1] == "François - Montréal"


class TestDocstringExamples:
    """Test examples from the docstring."""

    def test_docstring_example_simple(self):
        """Test first docstring example with simple separator."""
        df = pd.DataFrame({"A": [0, 5, 10], "B": [1, 6, 11], "C": [2, 7, 12]})

        result = merge_columns(df, "A", "B", sep=" ")

        assert result["A_B"].iloc[0] == "0 1"
        assert result["A_B"].iloc[1] == "5 6"
        assert result["A_B"].iloc[2] == "10 11"

    def test_docstring_example_labels(self):
        """Test second docstring example with column labels."""
        df = pd.DataFrame({"A": [0, 5, 10], "B": [1, 6, 11], "C": [2, 7, 12]})

        result = merge_columns(df, "A", "B", sep1="_", sep2="-")

        assert result["merged"].iloc[0] == "A-0_B-1"
        assert result["merged"].iloc[1] == "A-5_B-6"
        assert result["merged"].iloc[2] == "A-10_B-11"


class TestRealWorldScenarios:
    """Test real-world use cases."""

    def test_address_concatenation(self):
        """Test concatenating address fields."""
        df = pd.DataFrame(
            {
                "street": ["123 Main St", "456 Oak Ave"],
                "city": ["New York", "Los Angeles"],
                "state": ["NY", "CA"],
                "zip": ["10001", "90001"],
            }
        )

        result = merge_columns(
            df, "street", "city", "state", "zip", sep=", ", name="full_address"
        )

        assert result["full_address"].iloc[0] == "123 Main St, New York, NY, 10001"
        assert result["full_address"].iloc[1] == "456 Oak Ave, Los Angeles, CA, 90001"

    def test_creating_composite_keys(self):
        """Test creating composite keys for database operations."""
        df = pd.DataFrame(
            {
                "year": [2023, 2023, 2024],
                "month": [1, 2, 1],
                "category": ["A", "B", "A"],
                "subcategory": ["X", "Y", "Z"],
            }
        )

        result = merge_columns(
            df,
            "year",
            "month",
            "category",
            "subcategory",
            sep="_",
            name="composite_key",
        )

        assert result["composite_key"].iloc[0] == "2023_1_A_X"
        assert result["composite_key"].iloc[1] == "2023_2_B_Y"
        assert result["composite_key"].iloc[2] == "2024_1_A_Z"

    def test_log_message_creation(self):
        """Test creating formatted log messages."""
        df = pd.DataFrame(
            {
                "timestamp": ["2023-01-01 10:00:00", "2023-01-01 10:01:00"],
                "level": ["INFO", "ERROR"],
                "message": ["Process started", "Connection failed"],
            }
        )

        result = merge_columns(
            df, "timestamp", "level", "message", sep1=" | ", sep2=": ", name="log_entry"
        )

        expected1 = (
            "timestamp: 2023-01-01 10:00:00 | level: INFO | message: Process started"
        )
        expected2 = (
            "timestamp: 2023-01-01 10:01:00 | level: ERROR | message: Connection failed"
        )

        assert result["log_entry"].iloc[0] == expected1
        assert result["log_entry"].iloc[1] == expected2


class TestPerformance:
    """Test performance-related scenarios."""

    def test_large_dataframe(self):
        """Test with a reasonably large DataFrame."""
        n_rows = 10000
        df = pd.DataFrame(
            {
                "A": range(n_rows),
                "B": range(n_rows, 2 * n_rows),
                "C": [f"str_{i}" for i in range(n_rows)],
            }
        )

        result = merge_columns(df, "A", "B", "C", sep="-")

        assert len(result) == n_rows
        assert result["A_B_C"].iloc[0] == "0-10000-str_0"
        assert result["A_B_C"].iloc[-1] == f"{n_rows-1}-{2*n_rows-1}-str_{n_rows-1}"

    def test_no_copy_modification(self):
        """Test that original DataFrame is not modified."""
        df = pd.DataFrame({"X": [1, 2, 3], "Y": [4, 5, 6]})

        original_columns = list(df.columns)
        result = merge_columns(df, "X", "Y", sep=" ")

        # Original DataFrame should be unchanged
        assert list(df.columns) == original_columns
        assert "X_Y" not in df.columns
        # Result should have the new column
        assert "X_Y" in result.columns


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
