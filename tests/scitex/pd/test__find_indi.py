#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-05 10:00:00 (ywatanabe)"
# File: ./tests/scitex/pd/test__find_indi.py

import pytest
import numpy as np
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os
import sys


class TestFindIndiBasic:
    """Test basic functionality of find_indi."""

    def test_single_condition_string(self):
        """Test finding indices with single string condition."""
        from scitex.pd import find_indi

        df = pd.DataFrame({"A": ["x", "y", "x", "z"], "B": [1, 2, 3, 4]})
        conditions = {"A": "x"}
        result = find_indi(df, conditions)

        assert isinstance(result, list)
        assert result == [0, 2]

    def test_single_condition_number(self):
        """Test finding indices with single numeric condition."""
        from scitex.pd import find_indi

        df = pd.DataFrame({"A": [1, 2, 3, 2], "B": ["a", "b", "c", "d"]})
        conditions = {"A": 2}
        result = find_indi(df, conditions)

        assert result == [1, 3]

    def test_multiple_conditions(self):
        """Test finding indices with multiple conditions."""
        from scitex.pd import find_indi

        df = pd.DataFrame(
            {"A": [1, 2, 1, 2], "B": ["x", "x", "y", "y"], "C": [10, 20, 30, 40]}
        )
        conditions = {"A": 1, "B": "x"}
        result = find_indi(df, conditions)

        assert result == [0]

    def test_list_condition(self):
        """Test finding indices with list condition."""
        from scitex.pd import find_indi

        df = pd.DataFrame({"A": [1, 2, 3, 4, 5], "B": ["a", "b", "c", "d", "e"]})
        conditions = {"A": [1, 3, 5]}
        result = find_indi(df, conditions)

        assert result == [0, 2, 4]

    def test_mixed_conditions(self):
        """Test finding indices with mixed single and list conditions."""
        from scitex.pd import find_indi

        df = pd.DataFrame(
            {
                "A": [1, 2, 3, 1, 2],
                "B": ["x", "y", "z", "x", "y"],
                "C": [100, 200, 300, 400, 500],
            }
        )
        conditions = {"A": [1, 2], "B": "x"}
        result = find_indi(df, conditions)

        assert result == [0, 3]


class TestFindIndiNaNHandling:
    """Test NaN handling in find_indi."""

    def test_nan_in_dataframe(self):
        """Test handling NaN values in DataFrame."""
        from scitex.pd import find_indi

        df = pd.DataFrame({"A": [1, 2, np.nan, 4], "B": ["x", "y", "z", "w"]})
        conditions = {"A": 2}
        result = find_indi(df, conditions)

        assert result == [1]

    def test_nan_in_condition_single(self):
        """Test finding NaN values with single condition."""
        from scitex.pd import find_indi

        df = pd.DataFrame({"A": [1, np.nan, 3, np.nan], "B": ["a", "b", "c", "d"]})
        conditions = {"A": np.nan}
        result = find_indi(df, conditions)

        assert result == [1, 3]

    def test_nan_in_condition_list(self):
        """Test finding NaN values in list condition."""
        from scitex.pd import find_indi

        df = pd.DataFrame({"A": [1, np.nan, 3, 4, np.nan]})
        conditions = {"A": [1, np.nan]}
        result = find_indi(df, conditions)

        assert result == [0, 1, 4]

    def test_none_in_condition(self):
        """Test finding None values."""
        from scitex.pd import find_indi

        df = pd.DataFrame({"A": [1, None, 3, None], "B": ["a", "b", "c", "d"]})
        conditions = {"A": None}
        result = find_indi(df, conditions)

        assert result == [1, 3]

    def test_pd_na_in_condition(self):
        """Test finding pd.NA values."""
        from scitex.pd import find_indi

        df = pd.DataFrame({"A": [1, pd.NA, 3, pd.NA]}, dtype="Int64")
        conditions = {"A": pd.NA}
        result = find_indi(df, conditions)

        assert result == [1, 3]


class TestFindIndiEdgeCases:
    """Test edge cases in find_indi."""

    def test_empty_dataframe(self):
        """Test with empty DataFrame."""
        from scitex.pd import find_indi

        df = pd.DataFrame()
        conditions = {}
        result = find_indi(df, conditions)

        assert result == []

    def test_empty_conditions(self):
        """Test with empty conditions."""
        from scitex.pd import find_indi

        df = pd.DataFrame({"A": [1, 2, 3], "B": ["x", "y", "z"]})
        conditions = {}
        result = find_indi(df, conditions)

        assert result == []

    def test_no_matches(self):
        """Test when no rows match conditions."""
        from scitex.pd import find_indi

        df = pd.DataFrame({"A": [1, 2, 3], "B": ["x", "y", "z"]})
        conditions = {"A": 999}
        result = find_indi(df, conditions)

        assert result == []

    def test_all_matches(self):
        """Test when all rows match conditions."""
        from scitex.pd import find_indi

        df = pd.DataFrame({"A": [1, 1, 1], "B": ["x", "x", "x"]})
        conditions = {"A": 1, "B": "x"}
        result = find_indi(df, conditions)

        assert result == [0, 1, 2]

    def test_custom_index(self):
        """Test with custom DataFrame index."""
        from scitex.pd import find_indi

        df = pd.DataFrame({"A": [1, 2, 3], "B": ["x", "y", "z"]}, index=[10, 20, 30])
        conditions = {"A": 2}
        result = find_indi(df, conditions)

        assert result == [20]


class TestFindIndiErrorHandling:
    """Test error handling in find_indi."""

    def test_column_not_found(self):
        """Test KeyError when column not in DataFrame."""
        from scitex.pd import find_indi

        df = pd.DataFrame({"A": [1, 2, 3], "B": ["x", "y", "z"]})
        conditions = {"C": 1}

        with pytest.raises(KeyError, match="Columns not found in DataFrame: \\['C'\\]"):
            find_indi(df, conditions)

    def test_multiple_columns_not_found(self):
        """Test KeyError with multiple missing columns."""
        from scitex.pd import find_indi

        df = pd.DataFrame({"A": [1, 2, 3]})
        conditions = {"B": 1, "C": 2}

        with pytest.raises(KeyError, match="Columns not found in DataFrame"):
            find_indi(df, conditions)


class TestFindIndiDataTypes:
    """Test find_indi with various data types."""

    def test_float_values(self):
        """Test with float values."""
        from scitex.pd import find_indi

        df = pd.DataFrame({"A": [1.1, 2.2, 3.3, 2.2]})
        conditions = {"A": 2.2}
        result = find_indi(df, conditions)

        assert result == [1, 3]

    def test_boolean_values(self):
        """Test with boolean values."""
        from scitex.pd import find_indi

        df = pd.DataFrame({"A": [True, False, True, False]})
        conditions = {"A": True}
        result = find_indi(df, conditions)

        assert result == [0, 2]

    def test_datetime_values(self):
        """Test with datetime values."""
        from scitex.pd import find_indi

        dates = pd.to_datetime(["2021-01-01", "2021-01-02", "2021-01-01"])
        df = pd.DataFrame({"date": dates})
        conditions = {"date": pd.Timestamp("2021-01-01")}
        result = find_indi(df, conditions)

        assert result == [0, 2]

    def test_categorical_values(self):
        """Test with categorical values."""
        from scitex.pd import find_indi

        df = pd.DataFrame({"A": pd.Categorical(["cat", "dog", "cat", "bird"])})
        conditions = {"A": "cat"}
        result = find_indi(df, conditions)

        assert result == [0, 2]


class TestFindIndiComplexScenarios:
    """Test complex scenarios with find_indi."""

    def test_multiple_columns_multiple_values(self):
        """Test with multiple columns and multiple values."""
        from scitex.pd import find_indi

        df = pd.DataFrame(
            {
                "A": [1, 2, 3, 4, 5],
                "B": ["x", "y", "z", "x", "y"],
                "C": [10, 20, 30, 40, 50],
            }
        )
        conditions = {"A": [1, 2, 3], "B": ["x", "y"]}
        result = find_indi(df, conditions)

        assert result == [0, 1]

    def test_large_dataframe(self):
        """Test with large DataFrame."""
        from scitex.pd import find_indi

        n = 10000
        df = pd.DataFrame(
            {
                "A": np.random.randint(0, 10, n),
                "B": np.random.choice(["x", "y", "z"], n),
                "C": np.random.rand(n),
            }
        )
        conditions = {"A": 5, "B": "x"}
        result = find_indi(df, conditions)

        # Verify result manually
        expected = df[(df["A"] == 5) & (df["B"] == "x")].index.tolist()
        assert result == expected

    def test_tuple_condition(self):
        """Test with tuple condition (should work like list)."""
        from scitex.pd import find_indi

        df = pd.DataFrame({"A": [1, 2, 3, 4, 5]})
        conditions = {"A": (2, 4)}
        result = find_indi(df, conditions)

        assert result == [1, 3]

    def test_mixed_types_in_list(self):
        """Test with mixed types in list condition."""
        from scitex.pd import find_indi

        df = pd.DataFrame({"A": [1, "2", 3, "4", 5]})
        conditions = {"A": [1, "2", 3]}
        result = find_indi(df, conditions)

        assert result == [0, 1, 2]


class TestFindIndiDocumentationExamples:
    """Test examples from documentation."""

    def test_docstring_example(self):
        """Test the example from the docstring."""
        from scitex.pd import find_indi

        df = pd.DataFrame({"A": [1, 2, None], "B": ["x", "y", "x"]})
        conditions = {"A": [1, None], "B": "x"}
        result = find_indi(df, conditions)

        # Should find rows where A is 1 or None AND B is 'x'
        assert result == [0, 2]

    def test_original_commented_example(self):
        """Test example from commented code."""
        from scitex.pd import find_indi

        df = pd.DataFrame({"A": [1, 2, 3], "B": ["x", "y", "x"]})
        conditions = {"A": [1, 2], "B": "x"}
        result = find_indi(df, conditions)

        # Should find rows where A is 1 or 2 AND B is 'x'
        assert result == [0]

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/pd/_find_indi.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-05 08:11:05 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/pd/_find_indi.py
# 
# from typing import Dict, List, Union
# 
# import pandas as pd
# 
# 
# # def find_indi(df: pd.DataFrame, conditions: Dict[str, Union[str, int, float, List]]) -> pd.Series:
# #     """Finds indices of rows that satisfy all given conditions in a DataFrame.
# 
# #     Example
# #     -------
# #     >>> df = pd.DataFrame({'A': [1, 2, 3], 'B': ['x', 'y', 'x']})
# #     >>> conditions = {'A': [1, 2], 'B': 'x'}
# #     >>> result = find_indi(df, conditions)
# #     >>> print(result)
# #     0     True
# #     1    False
# #     2    False
# #     dtype: bool
# 
# #     Parameters
# #     ----------
# #     df : pd.DataFrame
# #         Input DataFrame to search in
# #     conditions : Dict[str, Union[str, int, float, List]]
# #         Dictionary of column names and their target values
# 
# #     Returns
# #     -------
# #     pd.Series
# #         Boolean Series indicating which rows satisfy all conditions
# 
# #     Raises
# #     ------
# #     KeyError
# #         If any column in conditions is not found in DataFrame
# #     """
# #     if not all(col in df.columns for col in conditions):
# #         missing_cols = [col for col in conditions if col not in df.columns]
# #         raise KeyError(f"Columns not found in DataFrame: {missing_cols}")
# 
# #     condition_series = []
# #     for key, value in conditions.items():
# #         if isinstance(value, (list, tuple)):
# #             condition_series.append(df[key].isin(value))
# #         else:
# #             condition_series.append(df[key] == value)
# 
# #     return pd.concat(condition_series, axis=1).all(axis=1)
# 
# 
# def find_indi(
#     df: pd.DataFrame, conditions: Dict[str, Union[str, int, float, List]]
# ) -> List[int]:
#     """Finds indices of rows that satisfy conditions, handling NaN values.
# 
#     Example
#     -------
#     >>> df = pd.DataFrame({'A': [1, 2, None], 'B': ['x', 'y', 'x']})
#     >>> conditions = {'A': [1, None], 'B': 'x'}
#     >>> result = find_indi(df, conditions)
# 
#     Parameters
#     ----------
#     df : pd.DataFrame
#         Input DataFrame
#     conditions : Dict[str, Union[str, int, float, List]]
#         Column conditions
# 
#     Returns
#     -------
#     List[int]
#         List of integer indices of matching rows
#     """
#     if not conditions:
#         return []
# 
#     if not all(col in df.columns for col in conditions):
#         missing_cols = [col for col in conditions if col not in df.columns]
#         raise KeyError(f"Columns not found in DataFrame: {missing_cols}")
# 
#     condition_series = []
#     for key, value in conditions.items():
#         if isinstance(value, (list, tuple)):
#             # Handle NaN in lists
#             has_na = False
#             try:
#                 # Check for None
#                 if None in value:
#                     has_na = True
#                 # Check for pd.NA (may raise TypeError)
#                 elif any(v is pd.NA for v in value):
#                     has_na = True
#                 # Check for np.nan
#                 elif any(pd.isna(v) for v in value):
#                     has_na = True
#             except (TypeError, ValueError):
#                 # If any check fails, try alternative approach
#                 has_na = any(
#                     pd.isna(v) if not isinstance(v, str) else False for v in value
#                 )
# 
#             if has_na:
#                 condition = df[key].isin(value) | df[key].isna()
#             else:
#                 condition = df[key].isin(value)
#         else:
#             # Handle single NaN value
#             if pd.isna(value):
#                 condition = df[key].isna()
#             else:
#                 condition = df[key] == value
#         condition_series.append(condition)
# 
#     if condition_series:
#         mask = pd.concat(condition_series, axis=1).all(axis=1)
#         return df.index[mask].tolist()
#     else:
#         return []
# 
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/pd/_find_indi.py
# --------------------------------------------------------------------------------
