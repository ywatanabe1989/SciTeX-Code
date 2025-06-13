#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-05-30 22:10:00 (Claude)"
# File: ./scitex_repo/src/scitex/stats/_nan_stats.py

"""
Functions for NaN statistics.
"""

import numpy as np
import pandas as pd


def nan(data):
    """
    Get statistics about NaN values in the data.

    Parameters
    ----------
    data : array-like
        Input data

    Returns
    -------
    dict
        Dictionary containing NaN statistics
    """
    # Convert to numpy array if needed
    if isinstance(data, pd.DataFrame):
        data_flat = data.values.flatten()
    elif isinstance(data, pd.Series):
        data_flat = data.values
    else:
        data_flat = np.asarray(data).flatten()

    # Count NaNs
    nan_mask = np.isnan(data_flat)
    nan_count = int(np.sum(nan_mask))
    total_count = len(data_flat)

    return {
        "count": nan_count,
        "proportion": nan_count / total_count if total_count > 0 else 0.0,
        "total": total_count,
        "valid_count": total_count - nan_count,
    }


def real(data):
    """
    Get statistics for real (non-NaN, non-Inf) values.

    Parameters
    ----------
    data : array-like
        Input data

    Returns
    -------
    dict
        Dictionary containing statistics for real values
    """
    # Convert to numpy array
    data_array = np.asarray(data)

    # Get only finite values
    finite_mask = np.isfinite(data_array)
    real_values = data_array[finite_mask]

    if len(real_values) == 0:
        return {
            "mean": np.nan,
            "median": np.nan,
            "std": np.nan,
            "skew": np.nan,
            "kurtosis": np.nan,
            "count": 0,
        }

    # Calculate statistics
    from scipy import stats as scipy_stats

    return {
        "mean": float(np.mean(real_values)),
        "median": float(np.median(real_values)),
        "std": float(np.std(real_values)),
        "skew": float(scipy_stats.skew(real_values)),
        "kurtosis": float(scipy_stats.kurtosis(real_values)),
        "count": len(real_values),
    }


__all__ = ["nan", "real"]
