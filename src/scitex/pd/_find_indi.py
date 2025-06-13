#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-05 08:11:05 (ywatanabe)"
# File: ./scitex_repo/src/scitex/pd/_find_indi.py

from typing import Dict, List, Union

import pandas as pd


# def find_indi(df: pd.DataFrame, conditions: Dict[str, Union[str, int, float, List]]) -> pd.Series:
#     """Finds indices of rows that satisfy all given conditions in a DataFrame.

#     Example
#     -------
#     >>> df = pd.DataFrame({'A': [1, 2, 3], 'B': ['x', 'y', 'x']})
#     >>> conditions = {'A': [1, 2], 'B': 'x'}
#     >>> result = find_indi(df, conditions)
#     >>> print(result)
#     0     True
#     1    False
#     2    False
#     dtype: bool

#     Parameters
#     ----------
#     df : pd.DataFrame
#         Input DataFrame to search in
#     conditions : Dict[str, Union[str, int, float, List]]
#         Dictionary of column names and their target values

#     Returns
#     -------
#     pd.Series
#         Boolean Series indicating which rows satisfy all conditions

#     Raises
#     ------
#     KeyError
#         If any column in conditions is not found in DataFrame
#     """
#     if not all(col in df.columns for col in conditions):
#         missing_cols = [col for col in conditions if col not in df.columns]
#         raise KeyError(f"Columns not found in DataFrame: {missing_cols}")

#     condition_series = []
#     for key, value in conditions.items():
#         if isinstance(value, (list, tuple)):
#             condition_series.append(df[key].isin(value))
#         else:
#             condition_series.append(df[key] == value)

#     return pd.concat(condition_series, axis=1).all(axis=1)


def find_indi(
    df: pd.DataFrame, conditions: Dict[str, Union[str, int, float, List]]
) -> List[int]:
    """Finds indices of rows that satisfy conditions, handling NaN values.

    Example
    -------
    >>> df = pd.DataFrame({'A': [1, 2, None], 'B': ['x', 'y', 'x']})
    >>> conditions = {'A': [1, None], 'B': 'x'}
    >>> result = find_indi(df, conditions)

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame
    conditions : Dict[str, Union[str, int, float, List]]
        Column conditions

    Returns
    -------
    List[int]
        List of integer indices of matching rows
    """
    if not conditions:
        return []

    if not all(col in df.columns for col in conditions):
        missing_cols = [col for col in conditions if col not in df.columns]
        raise KeyError(f"Columns not found in DataFrame: {missing_cols}")

    condition_series = []
    for key, value in conditions.items():
        if isinstance(value, (list, tuple)):
            # Handle NaN in lists
            has_na = False
            try:
                # Check for None
                if None in value:
                    has_na = True
                # Check for pd.NA (may raise TypeError)
                elif any(v is pd.NA for v in value):
                    has_na = True
                # Check for np.nan
                elif any(pd.isna(v) for v in value):
                    has_na = True
            except (TypeError, ValueError):
                # If any check fails, try alternative approach
                has_na = any(
                    pd.isna(v) if not isinstance(v, str) else False for v in value
                )

            if has_na:
                condition = df[key].isin(value) | df[key].isna()
            else:
                condition = df[key].isin(value)
        else:
            # Handle single NaN value
            if pd.isna(value):
                condition = df[key].isna()
            else:
                condition = df[key] == value
        condition_series.append(condition)

    if condition_series:
        mask = pd.concat(condition_series, axis=1).all(axis=1)
        return df.index[mask].tolist()
    else:
        return []


# EOF
