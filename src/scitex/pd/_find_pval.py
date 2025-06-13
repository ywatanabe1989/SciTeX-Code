#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-03 03:25:00 (ywatanabe)"
# File: ./scitex_repo/src/scitex/pd/_find_pval.py

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-10-06 11:09:07 (ywatanabe)"
# /home/ywatanabe/proj/_scitex_repo_openhands/src/scitex/stats/_find_pval_col.py

"""
Functionality:
    - Identifies column name(s) in a DataFrame or keys in other data structures that correspond to p-values
Input:
    - pandas DataFrame, numpy array, list, or dict
Output:
    - String or list of strings representing the identified p-value column name(s) or key(s), or None if not found
Prerequisites:
    - pandas, numpy libraries
"""

import re
from typing import Dict, List, Optional, Union

import numpy as np
import pandas as pd


def find_pval(
    data: Union[pd.DataFrame, np.ndarray, List, Dict], multiple: bool = True
) -> Union[Optional[str], List[str]]:
    """
    Find p-value column name(s) or key(s) in various data structures.

    Example:
    --------
    >>> df = pd.DataFrame({'p_value': [0.05, 0.01], 'pval': [0.1, 0.001], 'other': [1, 2]})
    >>> find_pval(df)
    ['p_value', 'pval']
    >>> find_pval(df, multiple=False)
    'p_value'

    Parameters:
    -----------
    data : Union[pd.DataFrame, np.ndarray, List, Dict]
        Data structure to search for p-value column or key
    multiple : bool, optional
        If True, return all matches; if False, return only the first match (default is True)

    Returns:
    --------
    Union[Optional[str], List[str]]
        Name(s) of the column(s) or key(s) that match p-value patterns, or None if not found
    """
    if isinstance(data, pd.DataFrame):
        return _find_pval_col(data, multiple)
    elif isinstance(data, (np.ndarray, list, dict)):
        return _find_pval(data, multiple)
    else:
        raise ValueError("Input must be a pandas DataFrame, numpy array, list, or dict")


def _find_pval(
    data: Union[np.ndarray, List, Dict], multiple: bool
) -> Union[Optional[str], List[str]]:
    pattern = re.compile(r"p[-_]?val(ue)?(?!.*stars)", re.IGNORECASE)
    matches = []

    if isinstance(data, dict):
        matches = [key for key in data.keys() if pattern.search(str(key))]
    elif (
        isinstance(data, (np.ndarray, list))
        and len(data) > 0
        and isinstance(data[0], dict)
    ):
        matches = [key for key in data[0].keys() if pattern.search(str(key))]

    return matches if multiple else (matches[0] if matches else None)


def _find_pval_col(
    df: pd.DataFrame, multiple: bool = False
) -> Union[Optional[str], List[str]]:
    """
    Find p-value column name(s) in a DataFrame.

    Example:
    --------
    >>> df = pd.DataFrame({'p_value': [0.05, 0.01], 'pval': [0.1, 0.001], 'other': [1, 2]})
    >>> find_pval_col(df)
    ['p_value', 'pval']
    >>> find_pval_col(df, multiple=False)
    'p_value'

    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame to search for p-value column(s)
    multiple : bool, optional
        If True, return all matches; if False, return only the first match (default is False)

    Returns:
    --------
    Union[Optional[str], List[str]]
        Name(s) of the column(s) that match p-value patterns, or None if not found
    """
    pattern = re.compile(r"p[-_]?val(ue)?(?!.*stars)", re.IGNORECASE)
    matches = [col for col in df.columns if pattern.search(str(col))]

    return matches if multiple else (matches[0] if matches else None)


# EOF
