#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-05-30 auto-created"
# File: ./src/scitex/stats/_statistical_tests.py

"""
Wrappers for statistical test functions to match test expectations
"""

import numpy as np
from typing import Dict, Any, Union, List


def brunner_munzel_test(sample1: np.ndarray, sample2: np.ndarray) -> Dict[str, Any]:
    """
    Wrapper for Brunner-Munzel test that matches test expectations.
    """
    from .tests._brunner_munzel_test import brunner_munzel_test as _bm_test

    # Call the actual implementation
    result = _bm_test(sample1, sample2)

    # Transform to expected format
    return {
        "statistic": result["w_statistic"],
        "p_value": result["p_value"],
        **result,  # Include all original keys
    }


def smirnov_grubbs(data: np.ndarray, alpha: float = 0.05) -> Dict[str, Any]:
    """
    Wrapper for Smirnov-Grubbs outlier test that matches test expectations.
    """
    from .tests._smirnov_grubbs import smirnov_grubbs as _sg_test

    # Call the actual implementation
    outlier_indices = _sg_test(data, alpha=alpha)

    # Calculate test statistics
    data_flat = np.array(data).flatten()
    mean = np.mean(data_flat)
    std = np.std(data_flat, ddof=1)

    # Find the most extreme value
    if outlier_indices is not None and len(outlier_indices) > 0:
        outliers = data_flat[outlier_indices]
        # Calculate test statistic for the most extreme outlier
        max_idx = np.argmax(np.abs(outliers - mean))
        test_statistic = np.abs((outliers[max_idx] - mean) / std)
    else:
        outliers = np.array([])
        # Calculate test statistic for the most extreme value
        deviations = np.abs(data_flat - mean) / std
        test_statistic = np.max(deviations)

    # Calculate critical value
    from scipy import stats

    n = len(data_flat)
    t = stats.t.isf(q=(alpha / n) / 2, df=n - 2)
    critical_value = (n - 1) * t / np.sqrt(n * (n - 2) + n * t * t)

    return {
        "outliers": outliers.tolist() if outlier_indices is not None else [],
        "test_statistic": float(test_statistic),
        "critical_value": float(critical_value),
        "outlier_indices": (
            outlier_indices.tolist() if outlier_indices is not None else []
        ),
        "alpha": alpha,
        "n": n,
    }
