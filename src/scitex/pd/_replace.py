#!./env/bin/python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-08-29 23:08:35 (ywatanabe)"
# ./src/scitex/pd/_replace.py


def replace(dataframe, old_value, new_value=None, regex=False, cols=None):
    """
    Replace values in a DataFrame.

    Example
    -------
    import pandas as pd
    df = pd.DataFrame({'A': ['abc-123', 'def-456'], 'B': ['ghi-789', 'jkl-012']})

    # Replace single value
    df_replaced = replace(df, 'abc', 'xyz')

    # Replace with dictionary
    replace_dict = {'-': '_', '1': 'one'}
    df_replaced = replace(df, replace_dict, cols=['A'])
    print(df_replaced)

    Parameters
    ----------
    dataframe : pandas.DataFrame
        Input DataFrame to modify.
    old_value : str, dict
        If str, the value to replace (requires new_value).
        If dict, mapping of old values (keys) to new values (values).
    new_value : str, optional
        New value to replace old_value with. Required if old_value is str.
    regex : bool, optional
        If True, treat replacement keys as regular expressions. Default is False.
    cols : list of str, optional
        List of column names to apply replacements. If None, apply to all columns.

    Returns
    -------
    pandas.DataFrame
        DataFrame with specified replacements applied.
    """
    dataframe = dataframe.copy()

    # Handle different input formats
    if isinstance(old_value, dict):
        replace_dict = old_value
    else:
        if new_value is None:
            raise ValueError("new_value must be provided when old_value is not a dict")
        replace_dict = {old_value: new_value}

    # Apply replacements to all columns if cols not specified
    if cols is None:
        # Use pandas replace method for all columns
        return dataframe.replace(replace_dict, regex=regex)
    else:
        # Apply to specific columns
        for column in cols:
            if column in dataframe.columns:
                dataframe[column] = dataframe[column].replace(replace_dict, regex=regex)
        return dataframe
