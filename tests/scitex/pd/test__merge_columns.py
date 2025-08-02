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

        # When numeric columns contain None, they become float before string conversion
        assert result["A_B"].iloc[0] == "1.0-x"
        assert result["A_B"].iloc[1] == "nan-y"  # None becomes NaN in numeric column
        assert result["A_B"].iloc[2] == "3.0-None"  # None stays as 'None' in string column


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
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/pd/_merge_columns.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-05 07:37:09 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/pd/_merge_columns.py
# 
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-10-07 12:03:29 (ywatanabe)"
# # ./src/scitex/pd/_merge_cols.py
# 
# from typing import Union, List, Tuple
# import pandas as pd
# 
# 
# def merge_columns(
#     df: pd.DataFrame,
#     *args: Union[str, List[str], Tuple[str, ...]],
#     sep: str = None,
#     sep1: str = "_",
#     sep2: str = "-",
#     name: str = "merged"
# ) -> pd.DataFrame:
#     """Creates a new column by joining specified columns.
# 
#     Example
#     -------
#     >>> df = pd.DataFrame({
#     ...     'A': [0, 5, 10],
#     ...     'B': [1, 6, 11],
#     ...     'C': [2, 7, 12]
#     ... })
#     >>> # Simple concatenation with separator
#     >>> merge_columns(df, 'A', 'B', sep=' ')
#        A  B  C    A_B
#     0  0  1  2    0 1
#     1  5  6  7    5 6
#     2 10 11 12  10 11
# 
#     >>> # With column labels
#     >>> merge_columns(df, 'A', 'B', sep1='_', sep2='-')
#        A  B  C        A_B
#     0  0  1  2    A-0_B-1
#     1  5  6  7    A-5_B-6
#     2 10 11 12  A-10_B-11
# 
#     Parameters
#     ----------
#     df : pd.DataFrame
#         Input DataFrame
#     *args : Union[str, List[str], Tuple[str, ...]]
#         Column names to join
#     sep : str, optional
#         Simple separator for values only (overrides sep1/sep2)
#     sep1 : str, optional
#         Separator between column-value pairs, by default "_"
#     sep2 : str, optional
#         Separator between column name and value, by default "-"
#     name : str, optional
#         Name for the merged column, by default "merged"
# 
#     Returns
#     -------
#     pd.DataFrame
#         DataFrame with added merged column
#     """
#     _df = df.copy()
#     columns = args[0] if len(args) == 1 and isinstance(args[0], (list, tuple)) else args
# 
#     if not columns:
#         raise ValueError("No columns specified for merging")
# 
#     if not all(col in _df.columns for col in columns):
#         missing = [col for col in columns if col not in _df.columns]
#         raise KeyError(f"Columns not found in DataFrame: {missing}")
# 
#     # Handle empty DataFrame case
#     if len(_df) == 0:
#         # Determine column name
#         if name == "merged" and sep is not None:
#             new_col_name = "_".join(columns)
#         else:
#             new_col_name = name
#         # Create empty Series with the correct name
#         _df[new_col_name] = pd.Series(dtype=str)
#         return _df
# 
#     if sep is not None:
#         # Simple value concatenation
#         merged_col = (
#             _df[list(columns)]
#             .astype(str)
#             .apply(
#                 lambda row: sep.join(row.values),
#                 axis=1,
#             )
#         )
#     else:
#         # Concatenation with column labels
#         merged_col = _df[list(columns)].apply(
#             lambda row: sep1.join(f"{col}{sep2}{val}" for col, val in row.items()),
#             axis=1,
#         )
# 
#     # Determine column name
#     if name == "merged" and sep is not None:
#         # When using simple separator and default name, use joined column names
#         new_col_name = "_".join(columns)
#     else:
#         # Use provided name or default
#         new_col_name = name
# 
#     _df[new_col_name] = merged_col
#     return _df
# 
# 
# merge_cols = merge_columns
# 
# # EOF
# 
# # #!./env/bin/python3
# # # -*- coding: utf-8 -*-
# # # Time-stamp: "2024-10-07 12:03:29 (ywatanabe)"
# # # ./src/scitex/pd/_merge_cols.py
# 
# 
# # def merge_columns(df, *args, sep1="_", sep2="-", name="merged"):
# #     """
# #     Join specified columns with their labels.
# 
# #     Example:
# #         import pandas as pd
# #         import numpy as np
# 
# #         df = pd.DataFrame(
# #             data=np.arange(25).reshape(5, 5),
# #             columns=["A", "B", "C", "D", "E"],
# #         )
# 
# #         df1 = merge_columns(df, "A", "B", sep1="_", sep2="-")
# #         df2 = merge_columns(df, ["A", "B"], sep1="_", sep2="-")
# #         assert (df1 == df2).all().all() # True
# 
# #         #     A   B   C   D   E        A_B
# #         # 0   0   1   2   3   4    A-0_B-1
# #         # 1   5   6   7   8   9    A-5_B-6
# #         # 2  10  11  12  13  14  A-10_B-11
# #         # 3  15  16  17  18  19  A-15_B-16
# #         # 4  20  21  22  23  24  A-20_B-21
# 
# 
# #     Parameters
# #     ----------
# #     df : pandas.DataFrame
# #         Input DataFrame
# #     *args : str or list
# #         Column names to join, either as separate arguments or a single list
# #     sep1 : str, optional
# #         Separator for joining column names, default "_"
# #     sep2 : str, optional
# #         Separator between column name and value, default "-"
# 
# #     Returns
# #     -------
# #     pandas.DataFrame
# #         DataFrame with added merged column
# #     """
# #     _df = df.copy()
# #     columns = (
# #         args[0]
# #         if len(args) == 1 and isinstance(args[0], (list, tuple))
# #         else args
# #     )
# #     merged_col = _df[list(columns)].apply(
# #         lambda row: sep1.join(f"{col}{sep2}{val}" for col, val in row.items()),
# #         axis=1,
# #     )
# 
# #     new_col_name = sep1.join(columns) if not name else str(name)
# #     _df[new_col_name] = merged_col
# #     return _df
# 
# 
# # merge_cols = merge_columns
# 
# # # def merge_columns(_df, *columns):
# # #     """
# # #     Add merged columns in string.
# 
# # #     DF = pd.DataFrame(data=np.arange(25).reshape(5,5),
# # #                       columns=["A", "B", "C", "D", "E"],
# # #     )
# 
# # #     print(DF)
# 
# # #     # A   B   C   D   E
# # #     # 0   0   1   2   3   4
# # #     # 1   5   6   7   8   9
# # #     # 2  10  11  12  13  14
# # #     # 3  15  16  17  18  19
# # #     # 4  20  21  22  23  24
# 
# # #     print(merge_columns(DF, "A", "B", "C"))
# 
# # #     #     A   B   C   D   E     A_B_C
# # #     # 0   0   1   2   3   4     0_1_2
# # #     # 1   5   6   7   8   9     5_6_7
# # #     # 2  10  11  12  13  14  10_11_12
# # #     # 3  15  16  17  18  19  15_16_17
# # #     # 4  20  21  22  23  24  20_21_22
# # #     """
# # #     from copy import deepcopy
# 
# # #     df = deepcopy(_df)
# # #     merged = deepcopy(df[columns[0]])  # initialization
# # #     for c in columns[1:]:
# # #         merged = scitex.ml.utils.merge_labels(list(merged), deepcopy(df[c]))
# # #     df.loc[:, scitex.gen.connect_strs(columns)] = merged
# # #     return df
# 
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/pd/_merge_columns.py
# --------------------------------------------------------------------------------
