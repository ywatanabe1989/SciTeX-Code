#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-04 12:05:00 (ywatanabe)"
# File: ./src/scitex/stats/_additional_tests.py

"""
Additional statistical tests for comprehensive analysis.

This module provides additional statistical tests commonly used in scientific research,
with a focus on robust methods and clear interpretations.
"""

import numpy as np
from typing import Tuple, Union, Dict, Any, List
import warnings
from scipy import stats as scipy_stats


def f_oneway(*args) -> Tuple[float, float]:
    """
    Perform one-way ANOVA test.
    
    NOTE: Consider using Kruskal-Wallis test for non-parametric alternative
    when normality assumptions are violated.
    
    Parameters
    ----------
    *args : array_like
        Sample data arrays. Need at least 2 groups.
        
    Returns
    -------
    statistic : float
        The F-statistic
    pvalue : float
        The p-value
        
    Examples
    --------
    >>> from scitex import stats
    >>> group1 = np.random.normal(0, 1, 100)
    >>> group2 = np.random.normal(0.5, 1, 100)
    >>> group3 = np.random.normal(1, 1, 100)
    >>> f_stat, p = stats.f_oneway(group1, group2, group3)
    >>> print(f"F-statistic: {f_stat:.4f}, p-value: {p:.4f}")
    """
    if len(args) < 2:
        raise ValueError("Need at least 2 groups for ANOVA")
    
    # Use scipy's implementation
    return scipy_stats.f_oneway(*args)


def kruskal(*args) -> Tuple[float, float]:
    """
    Perform Kruskal-Wallis H-test (non-parametric alternative to one-way ANOVA).
    
    This test is more robust than ANOVA when normality assumptions are violated.
    
    Parameters
    ----------
    *args : array_like
        Sample data arrays. Need at least 2 groups.
        
    Returns
    -------
    statistic : float
        The Kruskal-Wallis H-statistic
    pvalue : float
        The p-value
        
    Examples
    --------
    >>> from scitex import stats
    >>> group1 = np.random.exponential(1, 100)  # Non-normal data
    >>> group2 = np.random.exponential(1.5, 100)
    >>> group3 = np.random.exponential(2, 100)
    >>> h_stat, p = stats.kruskal(group1, group2, group3)
    >>> print(f"H-statistic: {h_stat:.4f}, p-value: {p:.4f}")
    """
    if len(args) < 2:
        raise ValueError("Need at least 2 groups for Kruskal-Wallis test")
    
    return scipy_stats.kruskal(*args)


def chi2_contingency(observed: np.ndarray, correction: bool = True, 
                     lambda_: Union[None, float] = None) -> Tuple[float, float, int, np.ndarray]:
    """
    Chi-square test of independence of variables in a contingency table.
    
    Parameters
    ----------
    observed : array_like
        The contingency table
    correction : bool, optional
        If True, apply Yates' correction for continuity
    lambda_ : float or None, optional
        The cressie-read power divergence statistic
        
    Returns
    -------
    chi2 : float
        The test statistic
    p : float
        The p-value of the test
    dof : int
        Degrees of freedom
    expected : ndarray
        The expected frequencies
        
    Examples
    --------
    >>> from scitex import stats
    >>> # Contingency table: treatment vs outcome
    >>> observed = np.array([[10, 10, 20], [20, 20, 40]])
    >>> chi2, p, dof, expected = stats.chi2_contingency(observed)
    >>> print(f"Chi-square: {chi2:.4f}, p-value: {p:.4f}")
    """
    return scipy_stats.chi2_contingency(observed, correction=correction, lambda_=lambda_)


def shapiro(x: np.ndarray) -> Tuple[float, float]:
    """
    Shapiro-Wilk test for normality.
    
    Parameters
    ----------
    x : array_like
        Sample data
        
    Returns
    -------
    statistic : float
        The test statistic
    pvalue : float
        The p-value
        
    Examples
    --------
    >>> from scitex import stats
    >>> data = np.random.normal(0, 1, 100)
    >>> stat, p = stats.shapiro(data)
    >>> print(f"Shapiro-Wilk statistic: {stat:.4f}, p-value: {p:.4f}")
    """
    return scipy_stats.shapiro(x)


def pearsonr(x: np.ndarray, y: np.ndarray) -> Tuple[float, float]:
    """
    Pearson correlation coefficient and p-value.
    
    Parameters
    ----------
    x : array_like
        First variable
    y : array_like
        Second variable
        
    Returns
    -------
    r : float
        Pearson correlation coefficient
    pvalue : float
        Two-tailed p-value
        
    Examples
    --------
    >>> from scitex import stats
    >>> x = np.random.normal(0, 1, 100)
    >>> y = x + np.random.normal(0, 0.5, 100)
    >>> r, p = stats.pearsonr(x, y)
    >>> print(f"Pearson r: {r:.4f}, p-value: {p:.4f}")
    """
    return scipy_stats.pearsonr(x, y)


def spearmanr(x: np.ndarray, y: np.ndarray = None, axis: int = 0, 
              nan_policy: str = 'propagate') -> Tuple[float, float]:
    """
    Spearman rank-order correlation coefficient and p-value.
    
    Parameters
    ----------
    x : array_like
        First variable or 2D array
    y : array_like, optional
        Second variable (if x is 1D)
    axis : int, optional
        Axis along which to compute
    nan_policy : str, optional
        How to handle NaN values
        
    Returns
    -------
    correlation : float
        Spearman correlation coefficient
    pvalue : float
        Two-tailed p-value
        
    Examples
    --------
    >>> from scitex import stats
    >>> x = np.random.normal(0, 1, 100)
    >>> y = x**2 + np.random.normal(0, 0.5, 100)  # Non-linear relationship
    >>> rho, p = stats.spearmanr(x, y)
    >>> print(f"Spearman rho: {rho:.4f}, p-value: {p:.4f}")
    """
    result = scipy_stats.spearmanr(x, y, axis=axis, nan_policy=nan_policy)
    if isinstance(result.correlation, np.ndarray):
        # If 2D input, return correlation matrix and p-value matrix
        return result.correlation, result.pvalue
    else:
        # If 1D input, return scalar values
        return result.correlation, result.pvalue


def sem(a: np.ndarray, axis: int = 0, ddof: int = 1) -> Union[float, np.ndarray]:
    """
    Standard error of the mean.
    
    Parameters
    ----------
    a : array_like
        Input array
    axis : int or None, optional
        Axis along which to compute
    ddof : int, optional
        Delta degrees of freedom
        
    Returns
    -------
    s : float or ndarray
        Standard error of the mean
        
    Examples
    --------
    >>> from scitex import stats
    >>> data = np.random.normal(0, 1, 100)
    >>> se = stats.sem(data)
    >>> print(f"Standard error: {se:.4f}")
    """
    return scipy_stats.sem(a, axis=axis, ddof=ddof)


def trim_mean(a: np.ndarray, proportiontocut: float, axis: int = 0) -> Union[float, np.ndarray]:
    """
    Trimmed mean (robust measure of central tendency).
    
    Parameters
    ----------
    a : array_like
        Input array
    proportiontocut : float
        Proportion to cut from each end (0 to 0.5)
    axis : int or None, optional
        Axis along which to compute
        
    Returns
    -------
    mean : float or ndarray
        Trimmed mean
        
    Examples
    --------
    >>> from scitex import stats
    >>> data = np.concatenate([np.random.normal(0, 1, 90), [10, -10]])  # With outliers
    >>> mean_trimmed = stats.trim_mean(data, 0.1)  # Trim 10% from each end
    >>> print(f"Trimmed mean: {mean_trimmed:.4f}")
    """
    return scipy_stats.trim_mean(a, proportiontocut, axis=axis)


def probplot(x: np.ndarray, sparams=(), dist='norm', fit=True, plot=None):
    """
    Probability plot to assess if data follows a distribution.
    
    Parameters
    ----------
    x : array_like
        Sample data
    sparams : tuple, optional
        Shape parameters for the distribution
    dist : str or stats.distributions instance, optional
        Distribution to test against
    fit : bool, optional
        If True, fit a line to the data
    plot : object, optional
        Plot object with 'plot' method
        
    Returns
    -------
    (osm, osr) : tuple of ndarrays
        Ordered statistic medians and ordered response data
    (slope, intercept, r) : tuple of floats, optional
        Regression results
        
    Examples
    --------
    >>> from scitex import stats
    >>> import matplotlib.pyplot as plt
    >>> data = np.random.normal(0, 1, 100)
    >>> stats.probplot(data, plot=plt)
    >>> plt.show()
    """
    return scipy_stats.probplot(x, sparams=sparams, dist=dist, fit=fit, plot=plot)


# Statistical distribution objects
class norm:
    """Normal distribution utilities."""
    
    @staticmethod
    def ppf(q: Union[float, np.ndarray], loc: float = 0, scale: float = 1) -> Union[float, np.ndarray]:
        """Percent point function (inverse CDF) for normal distribution."""
        return scipy_stats.norm.ppf(q, loc=loc, scale=scale)
    
    @staticmethod
    def cdf(x: Union[float, np.ndarray], loc: float = 0, scale: float = 1) -> Union[float, np.ndarray]:
        """Cumulative distribution function for normal distribution."""
        return scipy_stats.norm.cdf(x, loc=loc, scale=scale)
    
    @staticmethod
    def pdf(x: Union[float, np.ndarray], loc: float = 0, scale: float = 1) -> Union[float, np.ndarray]:
        """Probability density function for normal distribution."""
        return scipy_stats.norm.pdf(x, loc=loc, scale=scale)


class t:
    """Student's t-distribution utilities."""
    
    @staticmethod
    def ppf(q: Union[float, np.ndarray], df: float, loc: float = 0, scale: float = 1) -> Union[float, np.ndarray]:
        """Percent point function (inverse CDF) for t-distribution."""
        return scipy_stats.t.ppf(q, df, loc=loc, scale=scale)
    
    @staticmethod
    def cdf(x: Union[float, np.ndarray], df: float, loc: float = 0, scale: float = 1) -> Union[float, np.ndarray]:
        """Cumulative distribution function for t-distribution."""
        return scipy_stats.t.cdf(x, df, loc=loc, scale=scale)
    
    @staticmethod
    def pdf(x: Union[float, np.ndarray], df: float, loc: float = 0, scale: float = 1) -> Union[float, np.ndarray]:
        """Probability density function for t-distribution."""
        return scipy_stats.t.pdf(x, df, loc=loc, scale=scale)


class chi2:
    """Chi-square distribution utilities."""
    
    @staticmethod
    def ppf(q: Union[float, np.ndarray], df: float, loc: float = 0, scale: float = 1) -> Union[float, np.ndarray]:
        """Percent point function (inverse CDF) for chi-square distribution."""
        return scipy_stats.chi2.ppf(q, df, loc=loc, scale=scale)
    
    @staticmethod
    def cdf(x: Union[float, np.ndarray], df: float, loc: float = 0, scale: float = 1) -> Union[float, np.ndarray]:
        """Cumulative distribution function for chi-square distribution."""
        return scipy_stats.chi2.cdf(x, df, loc=loc, scale=scale)


class nct:
    """Non-central t-distribution utilities."""
    
    @staticmethod
    def cdf(x: Union[float, np.ndarray], df: float, nc: float, loc: float = 0, scale: float = 1) -> Union[float, np.ndarray]:
        """Cumulative distribution function for non-central t-distribution."""
        return scipy_stats.nct.cdf(x, df, nc, loc=loc, scale=scale)


# Multiple testing correction utilities
class multitest:
    """Multiple testing correction methods."""
    
    @staticmethod
    def multipletests(pvals: np.ndarray, alpha: float = 0.05, method: str = 'fdr_bh',
                      is_sorted: bool = False, returnsorted: bool = False):
        """
        Multiple testing p-value correction.
        
        Parameters
        ----------
        pvals : array_like
            Uncorrected p-values
        alpha : float
            Family-wise error rate
        method : str
            Correction method ('bonferroni', 'fdr_bh', 'fdr_by', etc.)
        is_sorted : bool
            If True, pvals are already sorted
        returnsorted : bool
            If True, return sorted p-values
            
        Returns
        -------
        reject : ndarray, bool
            True if hypothesis is rejected after correction
        pvals_corrected : ndarray
            Corrected p-values
        alphacSidak : float
            Sidak corrected alpha
        alphacBonf : float
            Bonferroni corrected alpha
        """
        from statsmodels.stats.multitest import multipletests as sm_multipletests
        return sm_multipletests(pvals, alpha=alpha, method=method, 
                                is_sorted=is_sorted, returnsorted=returnsorted)


# Aliases for common use
anova = f_oneway
chisquare = chi2_contingency


# EOF