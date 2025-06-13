#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-05 07:45:00 (ywatanabe)"
# File: ./scitex_repo/src/scitex/pd/_slice.py

from typing import Dict, Union, List, Optional
import builtins

import pandas as pd

from ._find_indi import find_indi


def slice(
    df: pd.DataFrame,
    conditions: Union[
        builtins.slice, Dict[str, Union[str, int, float, List]], None
    ] = None,
    columns: Optional[List[str]] = None,
) -> pd.DataFrame:
    """Slices DataFrame rows and/or columns.

    Example
    -------
    >>> df = pd.DataFrame({'A': [1, 2, 3], 'B': ['x', 'y', 'x']})
    >>> # Slice by row indices
    >>> result = slice(df, slice(0, 2))
    >>> # Slice by conditions
    >>> result = slice(df, {'A': [1, 2], 'B': 'x'})
    >>> # Slice columns
    >>> result = slice(df, columns=['A'])

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame to slice
    conditions : slice, Dict, or None
        Either a slice object for row indices, or a dictionary of column conditions
    columns : List[str], optional
        List of column names to select

    Returns
    -------
    pd.DataFrame
        Sliced DataFrame
    """
    result = df.copy()

    # Handle row slicing
    if isinstance(conditions, builtins.slice):
        result = result.iloc[conditions]
    elif isinstance(conditions, dict):
        indices = find_indi(result, conditions)
        result = result.loc[indices]

    # Handle column slicing
    if columns is not None:
        result = result[columns]

    return result


# EOF
