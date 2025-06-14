#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-05 07:37:09 (ywatanabe)"
# File: ./scitex_repo/src/scitex/pd/_merge_columns.py

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-10-07 12:03:29 (ywatanabe)"
# ./src/scitex/pd/_merge_cols.py

from typing import Union, List, Tuple
import pandas as pd


def merge_columns(
    df: pd.DataFrame,
    *args: Union[str, List[str], Tuple[str, ...]],
    sep: str = None,
    sep1: str = "_",
    sep2: str = "-",
    name: str = "merged"
) -> pd.DataFrame:
    """Creates a new column by joining specified columns.

    Example
    -------
    >>> df = pd.DataFrame({
    ...     'A': [0, 5, 10],
    ...     'B': [1, 6, 11],
    ...     'C': [2, 7, 12]
    ... })
    >>> # Simple concatenation with separator
    >>> merge_columns(df, 'A', 'B', sep=' ')
       A  B  C    A_B
    0  0  1  2    0 1
    1  5  6  7    5 6
    2 10 11 12  10 11

    >>> # With column labels
    >>> merge_columns(df, 'A', 'B', sep1='_', sep2='-')
       A  B  C        A_B
    0  0  1  2    A-0_B-1
    1  5  6  7    A-5_B-6
    2 10 11 12  A-10_B-11

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame
    *args : Union[str, List[str], Tuple[str, ...]]
        Column names to join
    sep : str, optional
        Simple separator for values only (overrides sep1/sep2)
    sep1 : str, optional
        Separator between column-value pairs, by default "_"
    sep2 : str, optional
        Separator between column name and value, by default "-"
    name : str, optional
        Name for the merged column, by default "merged"

    Returns
    -------
    pd.DataFrame
        DataFrame with added merged column
    """
    _df = df.copy()
    columns = args[0] if len(args) == 1 and isinstance(args[0], (list, tuple)) else args

    if not columns:
        raise ValueError("No columns specified for merging")

    if not all(col in _df.columns for col in columns):
        missing = [col for col in columns if col not in _df.columns]
        raise KeyError(f"Columns not found in DataFrame: {missing}")

    # Handle empty DataFrame case
    if len(_df) == 0:
        # Determine column name
        if name == "merged" and sep is not None:
            new_col_name = "_".join(columns)
        else:
            new_col_name = name
        # Create empty Series with the correct name
        _df[new_col_name] = pd.Series(dtype=str)
        return _df

    if sep is not None:
        # Simple value concatenation
        merged_col = (
            _df[list(columns)]
            .astype(str)
            .apply(
                lambda row: sep.join(row.values),
                axis=1,
            )
        )
    else:
        # Concatenation with column labels
        merged_col = _df[list(columns)].apply(
            lambda row: sep1.join(f"{col}{sep2}{val}" for col, val in row.items()),
            axis=1,
        )

    # Determine column name
    if name == "merged" and sep is not None:
        # When using simple separator and default name, use joined column names
        new_col_name = "_".join(columns)
    else:
        # Use provided name or default
        new_col_name = name

    _df[new_col_name] = merged_col
    return _df


merge_cols = merge_columns

# EOF

# #!./env/bin/python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-10-07 12:03:29 (ywatanabe)"
# # ./src/scitex/pd/_merge_cols.py


# def merge_columns(df, *args, sep1="_", sep2="-", name="merged"):
#     """
#     Join specified columns with their labels.

#     Example:
#         import pandas as pd
#         import numpy as np

#         df = pd.DataFrame(
#             data=np.arange(25).reshape(5, 5),
#             columns=["A", "B", "C", "D", "E"],
#         )

#         df1 = merge_columns(df, "A", "B", sep1="_", sep2="-")
#         df2 = merge_columns(df, ["A", "B"], sep1="_", sep2="-")
#         assert (df1 == df2).all().all() # True

#         #     A   B   C   D   E        A_B
#         # 0   0   1   2   3   4    A-0_B-1
#         # 1   5   6   7   8   9    A-5_B-6
#         # 2  10  11  12  13  14  A-10_B-11
#         # 3  15  16  17  18  19  A-15_B-16
#         # 4  20  21  22  23  24  A-20_B-21


#     Parameters
#     ----------
#     df : pandas.DataFrame
#         Input DataFrame
#     *args : str or list
#         Column names to join, either as separate arguments or a single list
#     sep1 : str, optional
#         Separator for joining column names, default "_"
#     sep2 : str, optional
#         Separator between column name and value, default "-"

#     Returns
#     -------
#     pandas.DataFrame
#         DataFrame with added merged column
#     """
#     _df = df.copy()
#     columns = (
#         args[0]
#         if len(args) == 1 and isinstance(args[0], (list, tuple))
#         else args
#     )
#     merged_col = _df[list(columns)].apply(
#         lambda row: sep1.join(f"{col}{sep2}{val}" for col, val in row.items()),
#         axis=1,
#     )

#     new_col_name = sep1.join(columns) if not name else str(name)
#     _df[new_col_name] = merged_col
#     return _df


# merge_cols = merge_columns

# # def merge_columns(_df, *columns):
# #     """
# #     Add merged columns in string.

# #     DF = pd.DataFrame(data=np.arange(25).reshape(5,5),
# #                       columns=["A", "B", "C", "D", "E"],
# #     )

# #     print(DF)

# #     # A   B   C   D   E
# #     # 0   0   1   2   3   4
# #     # 1   5   6   7   8   9
# #     # 2  10  11  12  13  14
# #     # 3  15  16  17  18  19
# #     # 4  20  21  22  23  24

# #     print(merge_columns(DF, "A", "B", "C"))

# #     #     A   B   C   D   E     A_B_C
# #     # 0   0   1   2   3   4     0_1_2
# #     # 1   5   6   7   8   9     5_6_7
# #     # 2  10  11  12  13  14  10_11_12
# #     # 3  15  16  17  18  19  15_16_17
# #     # 4  20  21  22  23  24  20_21_22
# #     """
# #     from copy import deepcopy

# #     df = deepcopy(_df)
# #     merged = deepcopy(df[columns[0]])  # initialization
# #     for c in columns[1:]:
# #         merged = scitex.ml.utils.merge_labels(list(merged), deepcopy(df[c]))
# #     df.loc[:, scitex.gen.connect_strs(columns)] = merged
# #     return df


# EOF
