#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-10-05 23:04:16 (ywatanabe)"
# /home/ywatanabe/proj/_scitex_repo_openhands/src/scitex/pd/_melt_cols.py


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-10-05 23:03:39 (ywatanabe)"
# /home/ywatanabe/proj/_scitex_repo_openhands/src/scitex/pd/_melt_cols.py

from typing import List, Optional
import pandas as pd


def melt_cols(
    df: pd.DataFrame, cols: List[str], id_columns: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Melt specified columns while preserving links to other data in a DataFrame.

    Example
    -------
    >>> data = pd.DataFrame({
    ...     'id': [1, 2, 3],
    ...     'name': ['Alice', 'Bob', 'Charlie'],
    ...     'score_1': [85, 90, 78],
    ...     'score_2': [92, 88, 95]
    ... })
    >>> melted = melt_cols(data, cols=['score_1', 'score_2'])
    >>> print(melted)
       id     name variable  value
    0   1    Alice  score_1     85
    1   2      Bob  score_1     90
    2   3  Charlie  score_1     78
    3   1    Alice  score_2     92
    4   2      Bob  score_2     88
    5   3  Charlie  score_2     95

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame
    cols : List[str]
        Columns to be melted
    id_columns : Optional[List[str]], default None
        Columns to preserve as identifiers. If None, all columns not in 'cols' are used.

    Returns
    -------
    pd.DataFrame
        Melted DataFrame with preserved identifier columns

    Raises
    ------
    ValueError
        If cols are not present in the DataFrame
    """
    missing_melt = set(cols) - set(df.columns)
    if missing_melt:
        raise ValueError(f"Columns not found in DataFrame: {missing_melt}")

    if id_columns is None:
        id_columns = [col for col in df.columns if col not in cols]

    df_copy = df.reset_index(drop=True)
    df_copy["global_index"] = df_copy.index

    # Use a different value_name if "value" is one of the columns being melted
    value_name = "value" if "value" not in cols else "melted_value"
    melted_df = df_copy[cols + ["global_index"]].melt(
        id_vars=["global_index"], value_name=value_name
    )
    if id_columns:
        formatted_df = melted_df.merge(
            df_copy[id_columns + ["global_index"]], on="global_index"
        )
        return formatted_df.drop("global_index", axis=1)
    else:
        # No id columns to merge, just return melted data without global_index
        return melted_df.drop("global_index", axis=1)
