#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-03 11:30:00 (ywatanabe)"
# File: ./tests/scitex/pd/test__replace.py

import pytest
import numpy as np
import pandas as pd
from unittest.mock import Mock, patch
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../src"))

from scitex.pd import replace


class TestBasicReplacements:
    """Test basic replacement functionality."""

    def test_simple_string_replacement(self):
        """Test simple string replacement with old_value and new_value."""
        df = pd.DataFrame(
            {"A": ["apple", "banana", "apple"], "B": ["orange", "apple", "grape"]}
        )

        result = replace(df, "apple", "pear")

        assert result["A"].tolist() == ["pear", "banana", "pear"]
        assert result["B"].tolist() == ["orange", "pear", "grape"]

    def test_numeric_replacement(self):
        """Test replacement of numeric values."""
        df = pd.DataFrame({"A": [1, 2, 3, 1], "B": [4, 1, 6, 7]})

        result = replace(df, 1, 99)

        assert result["A"].tolist() == [99, 2, 3, 99]
        assert result["B"].tolist() == [4, 99, 6, 7]

    def test_dict_replacement(self):
        """Test replacement using dictionary mapping."""
        df = pd.DataFrame({"A": ["a", "b", "c"], "B": ["x", "y", "z"]})

        replace_dict = {"a": "alpha", "b": "beta", "x": "X", "z": "Z"}
        result = replace(df, replace_dict)

        assert result["A"].tolist() == ["alpha", "beta", "c"]
        assert result["B"].tolist() == ["X", "y", "Z"]

    def test_specific_columns_replacement(self):
        """Test replacement in specific columns only."""
        df = pd.DataFrame(
            {
                "A": ["test", "test", "other"],
                "B": ["test", "test", "test"],
                "C": ["test", "other", "test"],
            }
        )

        result = replace(df, "test", "replaced", cols=["A", "C"])

        assert result["A"].tolist() == ["replaced", "replaced", "other"]
        assert result["B"].tolist() == ["test", "test", "test"]  # B unchanged
        assert result["C"].tolist() == ["replaced", "other", "replaced"]


class TestRegexReplacements:
    """Test regex-based replacements."""

    def test_simple_regex_replacement(self):
        """Test simple regex pattern replacement."""
        df = pd.DataFrame(
            {
                "A": ["abc-123", "def-456", "ghi-789"],
                "B": ["test-001", "test-002", "test-003"],
            }
        )

        result = replace(df, r"-\d+", "", regex=True)

        assert result["A"].tolist() == ["abc", "def", "ghi"]
        assert result["B"].tolist() == ["test", "test", "test"]

    def test_regex_dict_replacement(self):
        """Test regex replacement with dictionary."""
        df = pd.DataFrame(
            {
                "A": ["email@domain.com", "user@test.org"],
                "B": ["phone: 123-456", "tel: 789-012"],
            }
        )

        replace_dict = {
            r"@.*\.com": "@company.com",
            r"@.*\.org": "@organization.org",
            r"\d{3}-\d{3}": "XXX-XXX",
        }
        result = replace(df, replace_dict, regex=True)

        assert result["A"].tolist() == ["email@company.com", "user@organization.org"]
        assert result["B"].tolist() == ["phone: XXX-XXX", "tel: XXX-XXX"]

    def test_regex_special_characters(self):
        """Test regex replacement with special characters."""
        df = pd.DataFrame(
            {"A": ["$100.00", "$250.50", "$1000.99"], "B": ["#tag1", "#tag2", "#tag3"]}
        )

        result = replace(df, r"\$|\.", "", regex=True)

        assert result["A"].tolist() == ["10000", "25050", "100099"]
        assert result["B"].tolist() == ["#tag1", "#tag2", "#tag3"]


class TestDataTypes:
    """Test replacements with different data types."""

    def test_mixed_type_dataframe(self):
        """Test replacement in DataFrame with mixed types."""
        df = pd.DataFrame(
            {
                "int": [1, 2, 3, 1],
                "float": [1.0, 2.5, 1.0, 3.5],
                "str": ["1", "2", "1", "3"],
                "bool": [True, False, True, False],
            }
        )

        result = replace(df, 1, 99)

        assert result["int"].tolist() == [99, 2, 3, 99]
        assert result["float"].tolist() == [99.0, 2.5, 99.0, 3.5]
        # Pandas doesn't replace string '1' when looking for numeric 1
        assert result["str"].tolist() == ["1", "2", "1", "3"]
        # Pandas doesn't replace True when looking for numeric 1
        assert result["bool"].tolist() == [True, False, True, False]

    def test_nan_replacement(self):
        """Test replacement of NaN values."""
        df = pd.DataFrame({"A": [1, np.nan, 3, np.nan], "B": ["a", "b", np.nan, "d"]})

        result = replace(df, np.nan, 0)

        assert result["A"].tolist() == [1, 0, 3, 0]
        assert result["B"].tolist() == ["a", "b", 0, "d"]

    def test_none_replacement(self):
        """Test replacement of None values."""
        df = pd.DataFrame({"A": [1, None, 3], "B": ["a", None, "c"]})

        result = replace(df, None, "missing")

        # In numeric columns, None becomes NaN, so replacing None doesn't affect it
        assert result["A"][0] == 1.0
        assert pd.isna(result["A"][1])  # Still NaN
        assert result["A"][2] == 3.0
        # In string columns, None is preserved and can be replaced
        assert result["B"].tolist() == ["a", "missing", "c"]

    def test_datetime_replacement(self):
        """Test replacement in datetime columns."""
        df = pd.DataFrame(
            {
                "dates": pd.to_datetime(["2023-01-01", "2023-01-02", "2023-01-01"]),
                "values": [1, 2, 3],
            }
        )

        old_date = pd.to_datetime("2023-01-01")
        new_date = pd.to_datetime("2023-01-15")

        result = replace(df, old_date, new_date)

        expected = pd.to_datetime(["2023-01-15", "2023-01-02", "2023-01-15"])
        pd.testing.assert_series_equal(
            result["dates"], pd.Series(expected, name="dates")
        )


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_no_new_value_error(self):
        """Test error when new_value not provided with string old_value."""
        df = pd.DataFrame({"A": [1, 2, 3]})

        with pytest.raises(ValueError, match="new_value must be provided"):
            replace(df, "old")

    def test_empty_dataframe(self):
        """Test replacement on empty DataFrame."""
        df = pd.DataFrame()

        result = replace(df, "old", "new")

        assert result.empty
        assert isinstance(result, pd.DataFrame)

    def test_nonexistent_column(self):
        """Test replacement with non-existent column specified."""
        df = pd.DataFrame({"A": [1, 2, 3]})

        # Should not raise error, just skip non-existent column
        result = replace(df, 1, 99, cols=["A", "B", "C"])

        assert result["A"].tolist() == [99, 2, 3]
        assert list(result.columns) == ["A"]

    def test_no_matches(self):
        """Test when no values match replacement criteria."""
        df = pd.DataFrame({"A": [1, 2, 3], "B": ["a", "b", "c"]})

        result = replace(df, 99, 100)

        # Should return unchanged DataFrame
        pd.testing.assert_frame_equal(result, df)

    def test_empty_replace_dict(self):
        """Test with empty replacement dictionary."""
        df = pd.DataFrame({"A": [1, 2, 3]})

        result = replace(df, {})

        pd.testing.assert_frame_equal(result, df)


class TestComplexScenarios:
    """Test complex real-world scenarios."""

    def test_data_cleaning_workflow(self):
        """Test typical data cleaning workflow."""
        df = pd.DataFrame(
            {
                "name": ["John Doe", "Jane Smith", "Bob Johnson"],
                "phone": ["123-456-7890", "(555) 123-4567", "999.888.7777"],
                "email": ["john@example.com", "jane@test.org", "bob@company.com"],
            }
        )

        # Clean phone numbers
        phone_replacements = {
            r"[^\d]": "",  # Remove non-digits
        }
        result = replace(df, phone_replacements, regex=True, cols=["phone"])

        assert result["phone"].tolist() == ["1234567890", "5551234567", "9998887777"]
        # Other columns unchanged
        assert result["name"].tolist() == df["name"].tolist()

    def test_categorical_mapping(self):
        """Test replacing categories with standardized values."""
        df = pd.DataFrame(
            {
                "size": ["S", "small", "M", "medium", "L", "large"],
                "color": ["red", "RED", "Blue", "BLUE", "green", "GREEN"],
            }
        )

        size_map = {
            "S": "Small",
            "small": "Small",
            "M": "Medium",
            "medium": "Medium",
            "L": "Large",
            "large": "Large",
        }

        result = replace(df, size_map, cols=["size"])

        expected = ["Small", "Small", "Medium", "Medium", "Large", "Large"]
        assert result["size"].tolist() == expected

    def test_multiple_replacements_same_column(self):
        """Test multiple replacements in sequence."""
        df = pd.DataFrame(
            {"text": ["Hello World!", "Python Programming", "Data Science"]}
        )

        # First replacement
        result = replace(df, "Hello", "Hi")
        # Second replacement
        result = replace(result, "Programming", "Coding")
        # Third replacement
        result = replace(result, "!", ".")

        expected = ["Hi World.", "Python Coding", "Data Science"]
        assert result["text"].tolist() == expected


class TestDocstringExample:
    """Test the example from the docstring."""

    def test_docstring_example_simple(self):
        """Test simple replacement from docstring."""
        df = pd.DataFrame({"A": ["abc-123", "def-456"], "B": ["ghi-789", "jkl-012"]})

        df_replaced = replace(df, "abc", "xyz")

        assert df_replaced["A"].iloc[0] == "xyz-123"
        assert df_replaced["A"].iloc[1] == "def-456"

    def test_docstring_example_dict(self):
        """Test dictionary replacement from docstring."""
        df = pd.DataFrame({"A": ["abc-123", "def-456"], "B": ["ghi-789", "jkl-012"]})

        replace_dict = {"-": "_", "1": "one"}
        df_replaced = replace(df, replace_dict, cols=["A"])

        # Should replace - with _ and 1 with one in column A only
        assert df_replaced["A"].iloc[0] == "abc_one23"
        assert df_replaced["A"].iloc[1] == "def_456"
        assert df_replaced["B"].iloc[0] == "ghi-789"  # B unchanged


class TestPreservation:
    """Test that original DataFrame is not modified."""

    def test_original_unchanged(self):
        """Test that original DataFrame is not modified."""
        df = pd.DataFrame({"A": [1, 2, 3], "B": ["a", "b", "c"]})

        original_a = df["A"].copy()
        original_b = df["B"].copy()

        result = replace(df, 1, 99)

        # Original should be unchanged
        pd.testing.assert_series_equal(df["A"], original_a)
        pd.testing.assert_series_equal(df["B"], original_b)

        # Result should be different
        assert result["A"].iloc[0] == 99
        assert df["A"].iloc[0] == 1

    def test_index_preserved(self):
        """Test that DataFrame index is preserved."""
        df = pd.DataFrame({"A": [1, 2, 3]}, index=["x", "y", "z"])

        result = replace(df, 2, 99)

        assert list(result.index) == ["x", "y", "z"]
        assert result.loc["y", "A"] == 99

    def test_column_order_preserved(self):
        """Test that column order is preserved."""
        df = pd.DataFrame({"Z": [1, 2], "A": [3, 4], "M": [5, 6]})

        result = replace(df, 1, 99)

        assert list(result.columns) == ["Z", "A", "M"]


class TestLargeDatasets:
    """Test with larger datasets."""

    def test_large_dataframe(self):
        """Test replacement on large DataFrame."""
        n = 10000
        df = pd.DataFrame(
            {
                "A": np.random.choice(["a", "b", "c"], n),
                "B": np.random.randint(0, 10, n),
                "C": np.random.choice(["x", "y", "z"], n),
            }
        )

        result = replace(df, {"a": "alpha", "b": "beta", 5: 555})

        # Check replacements worked
        assert "alpha" in result["A"].values
        assert "beta" in result["A"].values
        assert "c" in result["A"].values
        assert "a" not in result["A"].values
        assert "b" not in result["A"].values

        if 5 in df["B"].values:
            assert 555 in result["B"].values
            assert 5 not in result["B"].values


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
