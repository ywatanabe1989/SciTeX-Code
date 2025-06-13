#!./env/bin/python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-08-25 09:35:39 (ywatanabe)"
# ./src/scitex/pd/_sort.py

import pandas as pd


def sort(
    dataframe,
    by=None,
    ascending=True,
    inplace=False,
    kind="quicksort",
    na_position="last",
    ignore_index=False,
    key=None,
    orders=None,
):
    """
    Sort DataFrame by specified column(s) with optional custom ordering and column reordering.

    Example
    -------
    import pandas as pd
    df = pd.DataFrame({'A': ['foo', 'bar', 'baz'], 'B': [3, 2, 1]})
    custom_order = {'A': ['bar', 'baz', 'foo']}
    sorted_df = sort(df, by=None, orders=custom_order)
    print(sorted_df)

    Parameters
    ----------
    dataframe : pandas.DataFrame
        The DataFrame to sort.
    by : str or list of str, optional
        Name(s) of column(s) to sort by.
    ascending : bool or list of bool, default True
        Sort ascending vs. descending.
    inplace : bool, default False
        If True, perform operation in-place.
    kind : {'quicksort', 'mergesort', 'heapsort', 'stable'}, default 'quicksort'
        Choice of sorting algorithm.
    na_position : {'first', 'last'}, default 'last'
        Puts NaNs at the beginning if 'first'; 'last' puts NaNs at the end.
    ignore_index : bool, default False
        If True, the resulting axis will be labeled 0, 1, …, n - 1.
    key : callable, optional
        Apply the key function to the values before sorting.
    orders : dict, optional
        Dictionary of column names and their custom sort orders.

    Returns
    -------
    pandas.DataFrame
        Sorted DataFrame with reordered columns.
    """
    if orders:
        by = [by] if isinstance(by, str) else list(orders.keys()) if by is None else by

        def apply_custom_order(column):
            return (
                pd.Categorical(column, categories=orders[column.name], ordered=True)
                if column.name in orders
                else column
            )

        key = apply_custom_order
    elif isinstance(by, str):
        by = [by]

    sorted_df = dataframe.sort_values(
        by=by,
        ascending=ascending,
        inplace=False,
        kind=kind,
        na_position=na_position,
        ignore_index=ignore_index,
        key=key,
    )

    # Reorder columns
    if by:
        other_columns = [col for col in sorted_df.columns if col not in by]
        sorted_df = sorted_df[by + other_columns]

    if inplace:
        dataframe.update(sorted_df)
        dataframe.reindex(columns=sorted_df.columns)
        return dataframe
    else:
        return sorted_df
