#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-29 13:43:40 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/stats/_p2stars.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/stats/_p2stars.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
# Time-stamp: "2024-10-06 10:39:57 (ywatanabe)"

from typing import Union

import pandas as pd


def p2stars(
    input_data: Union[float, str, pd.DataFrame], ns: bool = False
) -> Union[str, pd.DataFrame]:
    """
    Convert p-value(s) to significance stars.

    Example
    -------
    >>> p2stars(0.0005)
    '***'
    >>> p2stars("0.03")
    '*'
    >>> p2stars("1e-4")
    '***'
    >>> df = pd.DataFrame({'p_value': [0.001, "0.03", 0.1, "NA"]})
    >>> p2stars(df)
       p_value
    0    0.001 ***
    1    0.030   *
    2    0.100
    3       NA  NA

    Parameters
    ----------
    input_data : float, str, or pd.DataFrame
        The p-value or DataFrame containing p-values to convert.
        For DataFrame, columns matching re.search(r'p[_.-]?val', col.lower()) are considered.
    ns : bool, optional
        Whether to return 'n.s.' for non-significant results (default is False)

    Returns
    -------
    str or pd.DataFrame
        Significance stars or DataFrame with added stars column
    """
    if isinstance(input_data, (float, int, str)):
        return _p2stars_str(input_data, ns)
    elif isinstance(input_data, pd.DataFrame):
        return _p2stars_pd(input_data, ns)
    else:
        raise ValueError(
            "Input must be a float, string, or a pandas DataFrame"
        )


def _p2stars_str(pvalue: Union[float, str], ns: bool = False) -> str:
    try:
        if isinstance(pvalue, str):
            pvalue = pvalue.strip().lower()
            if pvalue in ["na", "nan", "null", ""]:
                return "NA"
        pvalue_float = float(pvalue)
        if pvalue_float < 0 or pvalue_float > 1:
            raise ValueError(
                f"P-value must be between 0 and 1, got {pvalue_float}"
            )
    except ValueError as e:
        raise ValueError(f"Invalid p-value: {pvalue}. {str(e)}")

    if pvalue_float <= 0.001:
        return "***"
    elif pvalue_float <= 0.01:
        return "**"
    elif pvalue_float <= 0.05:
        return "*"
    else:
        return "ns" if ns else ""


def _p2stars_pd(df: pd.DataFrame, ns: bool = False) -> pd.DataFrame:
    from scitex.pd import find_pval

    pvalue_cols = find_pval(df, multiple=True)
    assert pvalue_cols, "No p-value columns found in DataFrame"

    for pvalue_col in pvalue_cols:
        star_col = pvalue_col + "_stars"
        df[star_col] = df[pvalue_col].apply(lambda x: _p2stars_str(x, ns))

        # Get the index of the current p-value column
        col_idx = df.columns.get_loc(pvalue_col)

        # Move the star column right after the p-value column
        cols = list(df.columns)
        cols.insert(col_idx + 1, cols.pop(cols.index(star_col)))
        df = df.reindex(columns=cols)

    return df


# def _find_pvalue_columns(df: pd.DataFrame) -> List[str]:
#     """
#     Find columns that likely contain p-values.

#     Example
#     -------
#     >>> df = pd.DataFrame({'p_value': [0.05], 'pval': [0.01], 'p-val': [0.001], 'p.value': [0.1]})
#     >>> _find_pvalue_columns(df)
#     ['p_value', 'pval', 'p-val', 'p.value']

#     Parameters
#     ----------
#     df : pd.DataFrame
#         Input DataFrame

#     Returns
#     -------
#     List[str]
#         List of column names that likely contain p-values
#     """
#     return [col for col in df.columns if re.search(r'p[_.-]?val', col.lower())]

# EOF
