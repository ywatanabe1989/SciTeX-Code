#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-01 19:55:00 (ywatanabe)"
# File: ./tests/scitex/pd/test__sort.py

"""
Test module for scitex.pd.sort function.
"""

import pytest
import pandas as pd
import numpy as np
from pandas.testing import assert_frame_equal


class TestSort:
    """Test class for sort function."""

    @pytest.fixture
    def sample_df(self):
        """Create a sample DataFrame for testing."""
        return pd.DataFrame(
            {
                "A": ["foo", "bar", "baz", "qux"],
                "B": [3, 1, 4, 2],
                "C": [2.5, 1.2, 3.8, np.nan],
            }
        )

    @pytest.fixture
    def df_with_nulls(self):
        """Create a DataFrame with null values."""
        return pd.DataFrame({"A": ["a", None, "c", "b"], "B": [1, 2, np.nan, 4]})

    def test_import(self):
        """Test that sort can be imported."""
        from scitex.pd import sort

        assert callable(sort)

    def test_basic_sort_by_column(self, sample_df):
        """Test basic sorting by a single column."""
        from scitex.pd import sort

        # Sort by column B
        result = sort(sample_df, by="B")
        assert list(result["B"]) == [1, 2, 3, 4]
        assert list(result["A"]) == ["bar", "qux", "foo", "baz"]

    def test_sort_descending(self, sample_df):
        """Test sorting in descending order."""
        from scitex.pd import sort

        result = sort(sample_df, by="B", ascending=False)
        assert list(result["B"]) == [4, 3, 2, 1]
        assert list(result["A"]) == ["baz", "foo", "qux", "bar"]

    def test_sort_multiple_columns(self):
        """Test sorting by multiple columns."""
        from scitex.pd import sort

        df = pd.DataFrame({"A": [1, 1, 2, 2], "B": [4, 3, 2, 1]})

        result = sort(df, by=["A", "B"])
        assert list(result["B"]) == [3, 4, 1, 2]

    def test_sort_with_mixed_ascending(self):
        """Test sorting with mixed ascending/descending orders."""
        from scitex.pd import sort

        df = pd.DataFrame({"A": [1, 1, 2, 2], "B": [3, 4, 1, 2]})

        result = sort(df, by=["A", "B"], ascending=[True, False])
        assert list(result["B"]) == [4, 3, 2, 1]

    def test_sort_with_na_position(self, df_with_nulls):
        """Test sorting with NaN position control."""
        from scitex.pd import sort

        # NaN last (default)
        result = sort(df_with_nulls, by="B", na_position="last")
        assert pd.isna(result["B"].iloc[-1])

        # NaN first
        result = sort(df_with_nulls, by="B", na_position="first")
        assert pd.isna(result["B"].iloc[0])

    def test_sort_ignore_index(self, sample_df):
        """Test sorting with index reset."""
        from scitex.pd import sort

        # First, set a custom index
        sample_df.index = [10, 20, 30, 40]

        # Sort without ignore_index
        result = sort(sample_df, by="B", ignore_index=False)
        assert list(result.index) == [20, 40, 10, 30]

        # Sort with ignore_index
        result = sort(sample_df, by="B", ignore_index=True)
        assert list(result.index) == [0, 1, 2, 3]

    def test_sort_with_custom_orders(self):
        """Test sorting with custom category orders."""
        from scitex.pd import sort

        df = pd.DataFrame(
            {"A": ["small", "medium", "large", "small", "large"], "B": [1, 2, 3, 4, 5]}
        )

        custom_order = {"A": ["small", "medium", "large"]}
        result = sort(df, orders=custom_order)

        # Check that 'small' comes before 'medium' and 'medium' before 'large'
        a_values = result["A"].tolist()
        assert a_values == ["small", "small", "medium", "large", "large"]

    def test_sort_with_multiple_custom_orders(self):
        """Test sorting with custom orders for multiple columns."""
        from scitex.pd import sort

        df = pd.DataFrame(
            {
                "Size": ["L", "S", "M", "L", "S"],
                "Priority": ["high", "low", "medium", "low", "high"],
            }
        )

        custom_order = {"Size": ["S", "M", "L"], "Priority": ["low", "medium", "high"]}
        result = sort(df, orders=custom_order)

        # First 2 should be 'S', last 2 should be 'L'
        assert list(result["Size"][:2]) == ["S", "S"]
        assert list(result["Size"][-2:]) == ["L", "L"]

    def test_sort_inplace(self, sample_df):
        """Test in-place sorting."""
        from scitex.pd import sort

        original_id = id(sample_df)
        result = sort(sample_df, by="B", inplace=True)

        # Should return the same object
        assert id(result) == original_id
        assert list(result["B"]) == [1, 2, 3, 4]

    def test_column_reordering(self, sample_df):
        """Test that sorted columns are moved to the front."""
        from scitex.pd import sort

        result = sort(sample_df, by="B")
        assert list(result.columns) == ["B", "A", "C"]

        # Multiple columns
        result = sort(sample_df, by=["C", "B"])
        assert list(result.columns) == ["C", "B", "A"]

    def test_sort_with_key_function(self):
        """Test sorting with a key function."""
        from scitex.pd import sort

        df = pd.DataFrame(
            {"A": ["apple", "Banana", "cherry", "Date"], "B": [1, 2, 3, 4]}
        )

        # Sort case-insensitive
        result = sort(df, by="A", key=lambda x: x.str.lower())
        assert list(result["A"]) == ["apple", "Banana", "cherry", "Date"]

    def test_different_sort_algorithms(self, sample_df):
        """Test different sorting algorithms."""
        from scitex.pd import sort

        for algorithm in ["quicksort", "mergesort", "heapsort", "stable"]:
            result = sort(sample_df, by="B", kind=algorithm)
            assert list(result["B"]) == [1, 2, 3, 4]

    def test_empty_dataframe(self):
        """Test sorting an empty DataFrame."""
        from scitex.pd import sort

        df = pd.DataFrame()
        result = sort(df)
        assert result.empty

        # Empty with columns
        df = pd.DataFrame(columns=["A", "B"])
        result = sort(df, by="A")
        assert result.empty
        assert list(result.columns) == ["A", "B"]

    def test_single_row_dataframe(self):
        """Test sorting a single-row DataFrame."""
        from scitex.pd import sort

        df = pd.DataFrame({"A": [1], "B": [2]})
        result = sort(df, by="A")
        assert_frame_equal(result, df)

    def test_sort_no_by_parameter(self, sample_df):
        """Test sorting without specifying 'by' parameter."""
        from scitex.pd import sort

        # Should use all columns when orders is provided
        orders = {"A": ["bar", "baz", "foo", "qux"]}
        result = sort(sample_df, orders=orders)
        assert list(result["A"]) == ["bar", "baz", "foo", "qux"]

    def test_error_handling(self):
        """Test error handling for invalid inputs."""
        from scitex.pd import sort

        df = pd.DataFrame({"A": [1, 2, 3]})

        # Non-existent column
        with pytest.raises(KeyError):
            sort(df, by="NonExistent")

    @pytest.mark.parametrize(
        "input_type,expected_error",
        [
            ([1, 2, 3], AttributeError),  # List instead of DataFrame
            ("not a dataframe", AttributeError),  # String
            (123, AttributeError),  # Integer
        ],
    )
    def test_invalid_input_types(self, input_type, expected_error):
        """Test that invalid input types raise appropriate errors."""
        from scitex.pd import sort

        with pytest.raises(expected_error):
            sort(input_type, by="A")


# --------------------------------------------------------------------------------

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/pd/_sort.py
# --------------------------------------------------------------------------------
# #!./env/bin/python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-08-25 09:35:39 (ywatanabe)"
# # ./src/scitex/pd/_sort.py
# 
# import pandas as pd
# 
# 
# def sort(
#     dataframe,
#     by=None,
#     ascending=True,
#     inplace=False,
#     kind="quicksort",
#     na_position="last",
#     ignore_index=False,
#     key=None,
#     orders=None,
# ):
#     """
#     Sort DataFrame by specified column(s) with optional custom ordering and column reordering.
# 
#     Example
#     -------
#     import pandas as pd
#     df = pd.DataFrame({'A': ['foo', 'bar', 'baz'], 'B': [3, 2, 1]})
#     custom_order = {'A': ['bar', 'baz', 'foo']}
#     sorted_df = sort(df, by=None, orders=custom_order)
#     print(sorted_df)
# 
#     Parameters
#     ----------
#     dataframe : pandas.DataFrame
#         The DataFrame to sort.
#     by : str or list of str, optional
#         Name(s) of column(s) to sort by.
#     ascending : bool or list of bool, default True
#         Sort ascending vs. descending.
#     inplace : bool, default False
#         If True, perform operation in-place.
#     kind : {'quicksort', 'mergesort', 'heapsort', 'stable'}, default 'quicksort'
#         Choice of sorting algorithm.
#     na_position : {'first', 'last'}, default 'last'
#         Puts NaNs at the beginning if 'first'; 'last' puts NaNs at the end.
#     ignore_index : bool, default False
#         If True, the resulting axis will be labeled 0, 1, …, n - 1.
#     key : callable, optional
#         Apply the key function to the values before sorting.
#     orders : dict, optional
#         Dictionary of column names and their custom sort orders.
# 
#     Returns
#     -------
#     pandas.DataFrame
#         Sorted DataFrame with reordered columns.
#     """
#     if orders:
#         by = [by] if isinstance(by, str) else list(orders.keys()) if by is None else by
# 
#         def apply_custom_order(column):
#             return (
#                 pd.Categorical(column, categories=orders[column.name], ordered=True)
#                 if column.name in orders
#                 else column
#             )
# 
#         key = apply_custom_order
#     elif isinstance(by, str):
#         by = [by]
# 
#     sorted_df = dataframe.sort_values(
#         by=by,
#         ascending=ascending,
#         inplace=False,
#         kind=kind,
#         na_position=na_position,
#         ignore_index=ignore_index,
#         key=key,
#     )
# 
#     # Reorder columns
#     if by:
#         other_columns = [col for col in sorted_df.columns if col not in by]
#         sorted_df = sorted_df[by + other_columns]
# 
#     if inplace:
#         dataframe.update(sorted_df)
#         dataframe.reindex(columns=sorted_df.columns)
#         return dataframe
#     else:
#         return sorted_df

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/pd/_sort.py
# --------------------------------------------------------------------------------
