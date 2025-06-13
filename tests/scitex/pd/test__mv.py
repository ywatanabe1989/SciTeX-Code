#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-03 11:15:00 (ywatanabe)"
# File: ./tests/scitex/pd/test__mv.py

import pytest
import numpy as np
import pandas as pd
from unittest.mock import Mock, patch
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../src"))

from scitex.pd import mv, mv_to_first, mv_to_last


class TestMvBasicFunctionality:
    """Test basic functionality of mv function."""

    def test_move_column_to_position(self):
        """Test moving a column to a specific position."""
        df = pd.DataFrame(
            {"A": [1, 2, 3], "B": [4, 5, 6], "C": [7, 8, 9], "D": [10, 11, 12]}
        )

        # Move column B to position 2
        result = mv(df, "B", 2)

        assert list(result.columns) == ["A", "C", "B", "D"]
        # Data should be preserved
        assert result["B"].tolist() == [4, 5, 6]

    def test_move_column_to_first(self):
        """Test moving a column to the first position."""
        df = pd.DataFrame({"A": [1, 2], "B": [3, 4], "C": [5, 6]})

        result = mv(df, "C", 0)

        assert list(result.columns) == ["C", "A", "B"]
        assert result["C"].tolist() == [5, 6]

    def test_move_column_to_last(self):
        """Test moving a column to the last position."""
        df = pd.DataFrame({"A": [1, 2], "B": [3, 4], "C": [5, 6]})

        result = mv(df, "A", -1)

        assert list(result.columns) == ["B", "C", "A"]
        assert result["A"].tolist() == [1, 2]

    def test_move_row(self):
        """Test moving a row to a specific position."""
        df = pd.DataFrame(
            {"col1": [1, 2, 3, 4], "col2": [5, 6, 7, 8]}, index=["a", "b", "c", "d"]
        )

        # Move row 'c' to position 1
        result = mv(df, "c", 1, axis=0)

        assert list(result.index) == ["a", "c", "b", "d"]
        # Data should be preserved
        assert result.loc["c", "col1"] == 3
        assert result.loc["c", "col2"] == 7


class TestMvNegativePositions:
    """Test negative position handling."""

    def test_negative_position_columns(self):
        """Test negative positions for column movement."""
        df = pd.DataFrame({"A": [1], "B": [2], "C": [3], "D": [4], "E": [5]})

        # -1 should be last position
        result = mv(df, "B", -1)
        assert list(result.columns) == ["A", "C", "D", "E", "B"]

        # -2 should be second to last
        result = mv(df, "B", -2)
        assert list(result.columns) == ["A", "C", "D", "B", "E"]

        # -3 should be third from last
        result = mv(df, "B", -3)
        assert list(result.columns) == ["A", "C", "B", "D", "E"]

    def test_negative_position_rows(self):
        """Test negative positions for row movement."""
        df = pd.DataFrame({"col": [1, 2, 3, 4]}, index=["a", "b", "c", "d"])

        # Move 'b' to -1 (last)
        result = mv(df, "b", -1, axis=0)
        assert list(result.index) == ["a", "c", "d", "b"]

        # Move 'b' to -2 (second to last)
        result = mv(df, "b", -2, axis=0)
        assert list(result.index) == ["a", "c", "b", "d"]


class TestMvToFirst:
    """Test mv_to_first function."""

    def test_mv_to_first_column(self):
        """Test moving column to first position."""
        df = pd.DataFrame({"A": [1, 2], "B": [3, 4], "C": [5, 6], "D": [7, 8]})

        result = mv_to_first(df, "C")

        assert list(result.columns) == ["C", "A", "B", "D"]
        assert result["C"].tolist() == [5, 6]

    def test_mv_to_first_already_first(self):
        """Test moving first column to first (no change)."""
        df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})

        result = mv_to_first(df, "A")

        assert list(result.columns) == ["A", "B"]

    def test_mv_to_first_row(self):
        """Test moving row to first position."""
        df = pd.DataFrame({"col": [1, 2, 3, 4]}, index=["a", "b", "c", "d"])

        result = mv_to_first(df, "c", axis=0)

        assert list(result.index) == ["c", "a", "b", "d"]
        assert result.loc["c", "col"] == 3


class TestMvToLast:
    """Test mv_to_last function."""

    def test_mv_to_last_column(self):
        """Test moving column to last position."""
        df = pd.DataFrame({"A": [1, 2], "B": [3, 4], "C": [5, 6], "D": [7, 8]})

        result = mv_to_last(df, "B")

        assert list(result.columns) == ["A", "C", "D", "B"]
        assert result["B"].tolist() == [3, 4]

    def test_mv_to_last_already_last(self):
        """Test moving last column to last (no change)."""
        df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})

        result = mv_to_last(df, "B")

        assert list(result.columns) == ["A", "B"]

    def test_mv_to_last_row(self):
        """Test moving row to last position."""
        df = pd.DataFrame({"col": [1, 2, 3, 4]}, index=["a", "b", "c", "d"])

        result = mv_to_last(df, "b", axis=0)

        assert list(result.index) == ["a", "c", "d", "b"]
        assert result.loc["b", "col"] == 2


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_nonexistent_column(self):
        """Test moving non-existent column."""
        df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})

        with pytest.raises(ValueError):
            mv(df, "C", 0)

    def test_nonexistent_row(self):
        """Test moving non-existent row."""
        df = pd.DataFrame({"A": [1, 2]}, index=["a", "b"])

        with pytest.raises(ValueError):
            mv(df, "c", 0, axis=0)

    def test_single_column_dataframe(self):
        """Test with single column DataFrame."""
        df = pd.DataFrame({"A": [1, 2, 3]})

        # Moving the only column should work but have no effect
        result = mv(df, "A", 0)
        assert list(result.columns) == ["A"]

        result = mv(df, "A", -1)
        assert list(result.columns) == ["A"]

    def test_empty_dataframe(self):
        """Test with empty DataFrame."""
        df = pd.DataFrame()

        # Should handle gracefully even though there's nothing to move
        # This will raise because there are no columns
        with pytest.raises(ValueError):
            mv(df, "A", 0)

    def test_position_out_of_bounds(self):
        """Test with position beyond bounds."""
        df = pd.DataFrame({"A": [1], "B": [2], "C": [3]})

        # Position beyond end should place at end
        result = mv(df, "A", 10)
        assert list(result.columns) == ["B", "C", "A"]

        # Large negative position should place at beginning
        result = mv(df, "C", -10)
        assert list(result.columns) == ["C", "A", "B"]


class TestDataTypes:
    """Test with different data types."""

    def test_mixed_column_types(self):
        """Test with mixed column data types."""
        df = pd.DataFrame(
            {
                "int": [1, 2, 3],
                "float": [1.1, 2.2, 3.3],
                "str": ["a", "b", "c"],
                "bool": [True, False, True],
                "date": pd.date_range("2023-01-01", periods=3),
            }
        )

        result = mv(df, "bool", 1)

        # Check order
        assert list(result.columns) == ["int", "bool", "float", "str", "date"]
        # Check data integrity
        assert result["bool"].tolist() == [True, False, True]
        assert result["float"].tolist() == [1.1, 2.2, 3.3]

    def test_categorical_index(self):
        """Test with categorical index."""
        df = pd.DataFrame(
            {"A": [1, 2, 3], "B": [4, 5, 6]}, index=pd.Categorical(["x", "y", "z"])
        )

        result = mv(df, "y", 0, axis=0)

        assert list(result.index) == ["y", "x", "z"]
        # Note: pandas reindex doesn't preserve CategoricalIndex type
        assert isinstance(result.index, pd.Index)

    def test_multiindex_columns(self):
        """Test with MultiIndex columns."""
        # Create MultiIndex columns
        arrays = [["A", "A", "B", "B"], ["X", "Y", "X", "Y"]]
        columns = pd.MultiIndex.from_arrays(arrays)
        df = pd.DataFrame(np.random.randn(3, 4), columns=columns)

        # Move specific column
        result = mv(df, ("B", "X"), 0)

        assert result.columns[0] == ("B", "X")
        assert result.columns[1] == ("A", "X")


class TestIndexPreservation:
    """Test that indices and data are properly preserved."""

    def test_preserve_column_attributes(self):
        """Test that column attributes are preserved."""
        df = pd.DataFrame(
            {
                "A": pd.Series([1, 2, 3], name="A"),
                "B": pd.Series([4, 5, 6], name="B"),
                "C": pd.Series([7, 8, 9], name="C"),
            }
        )

        result = mv(df, "B", 0)

        # Check that column names are preserved
        assert result["B"].name == "B"
        assert result["A"].name == "A"

    def test_preserve_index_name(self):
        """Test that index names are preserved."""
        df = pd.DataFrame(
            {"A": [1, 2, 3], "B": [4, 5, 6]},
            index=pd.Index(["x", "y", "z"], name="my_index"),
        )

        result = mv(df, "y", 0, axis=0)

        assert result.index.name == "my_index"
        assert list(result.index) == ["y", "x", "z"]

    def test_no_data_modification(self):
        """Test that original DataFrame is not modified."""
        df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6], "C": [7, 8, 9]})

        original_columns = list(df.columns)
        result = mv(df, "B", 0)

        # Original should be unchanged
        assert list(df.columns) == original_columns
        # Result should be different
        assert list(result.columns) != original_columns


class TestComplexScenarios:
    """Test complex real-world scenarios."""

    def test_reorganize_dataframe_columns(self):
        """Test reorganizing DataFrame columns for analysis."""
        df = pd.DataFrame(
            {
                "id": [1, 2, 3],
                "name": ["Alice", "Bob", "Charlie"],
                "age": [25, 30, 35],
                "score": [95, 87, 92],
                "category": ["A", "B", "A"],
            }
        )

        # Move id to first, category to second
        result = mv_to_first(df, "category")
        result = mv_to_first(result, "id")

        assert list(result.columns) == ["id", "category", "name", "age", "score"]

    def test_multiple_moves(self):
        """Test multiple sequential moves."""
        df = pd.DataFrame({"A": [1], "B": [2], "C": [3], "D": [4], "E": [5]})

        # Rearrange columns
        result = mv(df, "E", 0)  # E to first: ['E', 'A', 'B', 'C', 'D']
        result = mv(result, "C", 2)  # C to position 2: ['E', 'A', 'C', 'B', 'D']
        result = mv(result, "A", -1)  # A to last: ['E', 'C', 'B', 'D', 'A']

        assert list(result.columns) == ["E", "C", "B", "D", "A"]

    def test_pivot_style_reorganization(self):
        """Test reorganizing for pivot-style analysis."""
        df = pd.DataFrame(
            {
                "value1": [10, 20, 30],
                "value2": [40, 50, 60],
                "group": ["A", "B", "C"],
                "subgroup": ["X", "Y", "Z"],
                "metric1": [1.1, 2.2, 3.3],
                "metric2": [4.4, 5.5, 6.6],
            }
        )

        # Move grouping columns to front
        result = mv_to_first(df, "subgroup")
        result = mv_to_first(result, "group")

        expected_order = ["group", "subgroup", "value1", "value2", "metric1", "metric2"]
        assert list(result.columns) == expected_order


class TestNaNAndSpecialValues:
    """Test handling of NaN and special values."""

    def test_dataframe_with_nan(self):
        """Test moving columns containing NaN values."""
        df = pd.DataFrame(
            {"A": [1, np.nan, 3], "B": [np.nan, 5, 6], "C": [7, 8, np.nan]}
        )

        result = mv(df, "B", 0)

        assert list(result.columns) == ["B", "A", "C"]
        # NaN values should be preserved
        assert pd.isna(result["B"].iloc[0])
        assert result["B"].iloc[1] == 5

    def test_datetime_with_nat(self):
        """Test with datetime columns containing NaT."""
        df = pd.DataFrame(
            {
                "dates": pd.to_datetime(["2023-01-01", pd.NaT, "2023-01-03"]),
                "values": [1, 2, 3],
            }
        )

        result = mv_to_last(df, "dates")

        assert list(result.columns) == ["values", "dates"]
        assert pd.isna(result["dates"].iloc[1])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
