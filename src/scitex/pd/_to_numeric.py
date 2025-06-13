#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-08 04:35:31 (ywatanabe)"
# File: ./scitex_repo/src/scitex/pd/_to_numeric.py

import pandas as pd


def to_numeric(df, errors="coerce"):
    """Convert all possible columns in a DataFrame to numeric types.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame
    errors : str, optional
        How to handle errors. 'coerce' (default) converts invalid values to NaN,
        'ignore' leaves non-numeric columns unchanged, 'raise' raises exceptions.

    Returns
    -------
    pd.DataFrame
        DataFrame with numeric columns converted
    """
    df_copy = df.copy()
    for col in df_copy.columns:
        # First try to convert
        original_col = df_copy[col]
        converted_col = pd.to_numeric(df_copy[col], errors="coerce")

        # Check if conversion resulted in all NaN when original had values
        if converted_col.isna().all() and not original_col.isna().all():
            # This is likely a pure string column
            if errors == "ignore":
                # Keep original for pure string columns
                continue
            else:
                # For coerce, still apply it
                df_copy[col] = converted_col
        elif not converted_col.equals(original_col):
            # Conversion changed something
            if errors == "ignore":
                # Only convert if it doesn't introduce new NaNs
                if converted_col.isna().sum() == original_col.isna().sum():
                    df_copy[col] = converted_col
            elif errors == "coerce":
                df_copy[col] = converted_col
            elif errors == "raise":
                df_copy[col] = pd.to_numeric(df_copy[col], errors="raise")
    return df_copy


# EOF
