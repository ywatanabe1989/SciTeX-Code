#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-04 12:00:00 (ywatanabe)"
# File: ./src/scitex/stats/_two_sample_tests.py

"""
Two-sample statistical tests with Brunner-Munzel as the preferred method.

This module provides robust two-sample tests, prioritizing the Brunner-Munzel test
over traditional t-tests due to its superior robustness to assumption violations.
"""

import numpy as np
from typing import Tuple, Union, Dict, Any
import warnings


def ttest_ind(a: np.ndarray, b: np.ndarray, equal_var: bool = True) -> Tuple[float, float]:
    """
    Perform two-sample test using Brunner-Munzel test (more robust than t-test).
    
    NOTE: This function uses Brunner-Munzel test instead of traditional t-test
    for better robustness. The Brunner-Munzel test is valid under less restrictive
    assumptions and provides better Type I error control.
    
    Parameters
    ----------
    a : array_like
        First sample
    b : array_like  
        Second sample
    equal_var : bool, optional
        Ignored. Kept for API compatibility with scipy.stats.ttest_ind
        
    Returns
    -------
    statistic : float
        The test statistic
    pvalue : float
        Two-sided p-value
        
    Examples
    --------
    >>> from scitex import stats
    >>> group1 = np.random.normal(0, 1, 100)
    >>> group2 = np.random.normal(0.5, 1, 100)
    >>> stat, p = stats.ttest_ind(group1, group2)
    >>> print(f"Statistic: {stat:.4f}, p-value: {p:.4f}")
    """
    warnings.warn(
        "Using Brunner-Munzel test instead of t-test for better robustness. "
        "To use traditional t-test, use scipy.stats.ttest_ind directly.",
        UserWarning
    )
    
    from ._statistical_tests import brunner_munzel_test
    
    result = brunner_munzel_test(a, b)
    return result["statistic"], result["p_value"]


def brunner_munzel(a: np.ndarray, b: np.ndarray) -> Tuple[float, float]:
    """
    Perform Brunner-Munzel test for two independent samples.
    
    The Brunner-Munzel test is a robust alternative to the Mann-Whitney U test
    and t-test that doesn't assume equal variances or specific distributions.
    
    Parameters
    ----------
    a : array_like
        First sample
    b : array_like
        Second sample
        
    Returns
    -------
    statistic : float
        The test statistic
    pvalue : float
        Two-sided p-value
        
    Examples
    --------
    >>> from scitex import stats
    >>> group1 = np.random.normal(0, 1, 100)
    >>> group2 = np.random.normal(0.5, 2, 100)  # Different variance
    >>> stat, p = stats.brunner_munzel(group1, group2)
    >>> print(f"Brunner-Munzel statistic: {stat:.4f}, p-value: {p:.4f}")
    """
    from ._statistical_tests import brunner_munzel_test
    
    result = brunner_munzel_test(a, b)
    return result["statistic"], result["p_value"]


def mannwhitneyu(x: np.ndarray, y: np.ndarray, use_continuity: bool = True, 
                 alternative: str = 'two-sided') -> Tuple[float, float]:
    """
    Perform two-sample test using Brunner-Munzel (more robust than Mann-Whitney U).
    
    NOTE: This function uses Brunner-Munzel test for better robustness.
    The Brunner-Munzel test handles tied values and unequal variances better
    than the traditional Mann-Whitney U test.
    
    Parameters
    ----------
    x : array_like
        First sample
    y : array_like
        Second sample  
    use_continuity : bool, optional
        Ignored. Kept for API compatibility
    alternative : str, optional
        Ignored. Always performs two-sided test
        
    Returns
    -------
    statistic : float
        The test statistic
    pvalue : float
        Two-sided p-value
    """
    warnings.warn(
        "Using Brunner-Munzel test instead of Mann-Whitney U for better robustness. "
        "To use traditional Mann-Whitney U, use scipy.stats.mannwhitneyu directly.",
        UserWarning
    )
    
    from ._statistical_tests import brunner_munzel_test
    
    result = brunner_munzel_test(x, y)
    return result["statistic"], result["p_value"]


# Aliases for convenience
ttest = ttest_ind
bm_test = brunner_munzel


# EOF