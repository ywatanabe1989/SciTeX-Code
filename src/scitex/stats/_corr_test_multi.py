#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-05-30 auto-created"
# File: ./src/scitex/stats/_corr_test_multi.py

"""
Multiple correlation tests for dataframes
"""

import numpy as np
import pandas as pd
from scipy import stats
from typing import Union


def corr_test_multi(data: Union[pd.DataFrame, np.ndarray]) -> pd.DataFrame:
    """
    Perform pairwise correlation tests on all columns of a DataFrame.

    Parameters
    ----------
    data : pd.DataFrame or np.ndarray
        Data with multiple variables (columns)

    Returns
    -------
    pd.DataFrame
        Correlation matrix with correlation coefficients
    """
    if isinstance(data, np.ndarray):
        # Convert to DataFrame if array
        data = pd.DataFrame(data)

    # Get column names
    cols = data.columns
    n_cols = len(cols)

    # Initialize correlation matrix
    corr_matrix = pd.DataFrame(index=cols, columns=cols, dtype=float)

    # Calculate pairwise correlations
    for i, col1 in enumerate(cols):
        for j, col2 in enumerate(cols):
            if i == j:
                # Diagonal is always 1
                corr_matrix.loc[col1, col2] = 1.0
            else:
                # Calculate correlation
                corr_coef, _ = stats.pearsonr(data[col1], data[col2])
                corr_matrix.loc[col1, col2] = corr_coef

    return corr_matrix


def nocorrelation_test(x: np.ndarray, y: np.ndarray) -> dict:
    """
    Test the null hypothesis that there is no correlation between x and y.

    Parameters
    ----------
    x : np.ndarray
        First variable
    y : np.ndarray
        Second variable

    Returns
    -------
    dict
        Dictionary containing:
        - statistic: The test statistic
        - p_value: The p-value for the test
    """
    # Convert to numpy arrays
    x = np.asarray(x)
    y = np.asarray(y)

    # Remove NaN values
    mask = ~(np.isnan(x) | np.isnan(y))
    x = x[mask]
    y = y[mask]

    # Calculate correlation and p-value
    corr_coef, p_value = stats.pearsonr(x, y)

    # Calculate test statistic (t-statistic for correlation)
    n = len(x)
    t_stat = corr_coef * np.sqrt((n - 2) / (1 - corr_coef**2))

    return {
        "statistic": float(t_stat),
        "p_value": float(p_value),
        "correlation": float(corr_coef),
        "n": n,
    }
