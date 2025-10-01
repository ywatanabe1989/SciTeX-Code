#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-01 15:00:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/stats/tests/_test_ttest.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/stats/tests/parametric/_test_ttest.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------


"""
Functionalities:
  - Perform independent samples t-test
  - Compute effect size (Cohen's d) and statistical power
  - Generate visualizations with significance indicators
  - Support flexible output formats (dict or DataFrame)

Dependencies:
  - packages: numpy, pandas, scipy, matplotlib

IO:
  - input: Two samples (arrays or Series)
  - output: Test results (dict or DataFrame) and optional figure
"""

"""Imports"""
import sys
import argparse
import numpy as np
import pandas as pd
from typing import Union, Optional, Literal, Tuple
from scipy import stats
import scitex as stx
from scitex.logging import getLogger

logger = getLogger(__name__)

"""Functions"""
def test_ttest_ind(
    x: Union[np.ndarray, pd.Series],
    y: Union[np.ndarray, pd.Series],
    var_x: str = 'x',
    var_y: str = 'y',
    alternative: Literal['two-sided', 'greater', 'less'] = 'two-sided',
    equal_var: bool = True,
    alpha: float = 0.05,
    plot: bool = False,
    return_as: Literal['dict', 'dataframe'] = 'dict'
) -> Union[dict, pd.DataFrame, Tuple[dict, 'matplotlib.figure.Figure'], Tuple[pd.DataFrame, 'matplotlib.figure.Figure']]:
    """
    Perform independent samples t-test.

    Parameters
    ----------
    x : array or Series
        First sample
    y : array or Series
        Second sample
    var_x : str, default 'x'
        Label for first sample
    var_y : str, default 'y'
        Label for second sample
    alternative : {'two-sided', 'greater', 'less'}, default 'two-sided'
        Alternative hypothesis:
        - 'two-sided': means are different
        - 'greater': mean of x is greater than y
        - 'less': mean of x is less than y
    equal_var : bool, default True
        Assume equal population variances (Student's t-test)
        If False, use Welch's t-test
    alpha : float, default 0.05
        Significance level
    plot : bool, default False
        Whether to generate visualization
    return_as : {'dict', 'dataframe'}, default 'dict'
        Output format

    Returns
    -------
    results : dict or DataFrame
        Test results including:
        - test_method: Name of test performed
        - statistic_name: 't'
        - statistic: t-statistic value
        - pvalue: p-value
        - pstars: Significance stars
        - rejected: Whether null hypothesis is rejected
        - effect_size: Cohen's d
        - power: Statistical power
        - n_x, n_y: Sample sizes
        - var_x, var_y: Variable labels
        - H0: Null hypothesis description
    fig : matplotlib.figure.Figure, optional
        Figure object (only if plot=True)

    Notes
    -----
    The independent samples t-test compares means of two independent groups.

    Null hypothesis: μ_x = μ_y
    Alternative (two-sided): μ_x ≠ μ_y

    The t-statistic is computed as:

    .. math::
        t = \\frac{\\bar{x} - \\bar{y}}{s_p \\sqrt{\\frac{1}{n_x} + \\frac{1}{n_y}}}

    where :math:`s_p` is the pooled standard deviation.

    For Welch's t-test (unequal variances), the denominator uses separate
    variances and degrees of freedom are adjusted.

    References
    ----------
    .. [1] Student (1908). "The Probable Error of a Mean". Biometrika, 6(1), 1-25.
    .. [2] Welch, B. L. (1947). "The generalization of 'Student's' problem when
           several different population variances are involved". Biometrika, 34(1-2), 28-35.

    Examples
    --------
    >>> x = np.array([1, 2, 3, 4, 5])
    >>> y = np.array([2, 3, 4, 5, 6])
    >>> result = test_ttest_ind(x, y)
    >>> result['pvalue']
    0.109...

    >>> # With visualization
    >>> result, fig = test_ttest_ind(x, y, plot=True)

    >>> # As DataFrame
    >>> df = test_ttest_ind(x, y, return_as='dataframe')
    >>> df['pstars'].iloc[0]
    'ns'
    """
    from ...utils._effect_size import cohens_d
    from ...utils._power import power_ttest
    from ...utils._formatters import p2stars
    from ...utils._normalizers import force_dataframe

    # Convert to numpy arrays and remove NaN
    x = np.asarray(x)
    y = np.asarray(y)
    x = x[~np.isnan(x)]
    y = y[~np.isnan(y)]

    n_x = len(x)
    n_y = len(y)

    # Perform t-test
    t_result = stats.ttest_ind(x, y, equal_var=equal_var, alternative=alternative)
    t_stat = float(t_result.statistic)
    pvalue = float(t_result.pvalue)

    # Compute effect size
    from ...utils._effect_size import interpret_cohens_d

    effect_size = cohens_d(x, y, paired=False)
    effect_size_interpretation = interpret_cohens_d(effect_size)

    # Compute statistical power
    power = power_ttest(
        effect_size=abs(effect_size),
        n1=n_x,
        n2=n_y,
        alpha=alpha,
        alternative=alternative,
        test_type='two-sample'
    )

    # Determine test method name
    if equal_var:
        test_method = "Student's t-test (independent)"
    else:
        test_method = "Welch's t-test (independent)"

    # Create null hypothesis description
    if alternative == 'two-sided':
        H0 = f"μ({var_x}) = μ({var_y})"
    elif alternative == 'greater':
        H0 = f"μ({var_x}) ≤ μ({var_y})"
    else:  # less
        H0 = f"μ({var_x}) ≥ μ({var_y})"

    # Compile results
    result = {
        'test_method': test_method,
        'statistic_name': 't',
        'statistic': t_stat,
        'alternative': alternative,
        'n_x': n_x,
        'n_y': n_y,
        'var_x': var_x,
        'var_y': var_y,
        'pvalue': pvalue,
        'pstars': p2stars(pvalue),
        'alpha': alpha,
        'rejected': pvalue < alpha,
        'effect_size': effect_size,
        'effect_size_metric': "Cohen's d",
        'effect_size_interpretation': effect_size_interpretation,
        'power': power,
        'H0': H0,
    }

    # Generate plot if requested
    fig = None
    if plot:
        fig = _plot_ttest_ind(x, y, var_x, var_y, result)

    # Convert to requested format
    if return_as == 'dataframe':
        result = force_dataframe(result)

    # Return based on plot option
    if plot:
        return result, fig
    else:
        return result


def _plot_ttest_ind(x, y, var_x, var_y, result):
    """Create visualization for independent t-test."""
    fig, axes = stx.plt.subplots(1, 2, figsize=(12, 5))

    # Prepare data
    data_x = pd.DataFrame({'value': x, 'group': var_x})
    data_y = pd.DataFrame({'value': y, 'group': var_y})
    data = pd.concat([data_x, data_y], ignore_index=True)

    # Plot 1: Histogram + swarm plot
    ax = axes[0]

    # Histogram
    bins = np.histogram_bin_edges(
        np.concatenate([x, y]),
        bins='auto'
    )
    ax.hist(x, bins=bins, alpha=0.5, label=var_x, density=True)
    ax.hist(y, bins=bins, alpha=0.5, label=var_y, density=True)

    # Add mean lines
    ax.axvline(np.mean(x), color='blue', linestyle='--', linewidth=2, alpha=0.7)
    ax.axvline(np.mean(y), color='orange', linestyle='--', linewidth=2, alpha=0.7)

    ax.set_xlabel('Value')
    ax.set_ylabel('Density')
    ax.set_title(f'Distribution Comparison {result["pstars"]}')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Plot 2: Box plot + swarm plot
    ax = axes[1]

    # Box plot
    positions = [0, 1]
    box_data = [x, y]
    bp = ax.boxplot(
        box_data,
        positions=positions,
        widths=0.4,
        patch_artist=True,
        showfliers=False
    )

    # Color boxes
    colors = ['lightblue', 'lightcoral']
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)

    # Swarm plot (simplified - add jittered points)
    np.random.seed(42)
    for i, vals in enumerate(box_data):
        y_vals = vals
        x_vals = np.random.normal(positions[i], 0.04, size=len(vals))
        ax.scatter(x_vals, y_vals, alpha=0.5, s=30)

    # Add significance stars
    y_max = max(np.max(x), np.max(y))
    y_min = min(np.min(x), np.min(y))
    y_range = y_max - y_min
    sig_y = y_max + y_range * 0.05

    ax.plot([0, 1], [sig_y, sig_y], 'k-', linewidth=1.5)
    ax.text(
        0.5, sig_y + y_range * 0.02,
        result['pstars'],
        ha='center',
        va='bottom',
        fontsize=14,
        fontweight='bold'
    )

    ax.set_xticks(positions)
    ax.set_xticklabels([var_x, var_y])
    ax.set_ylabel('Value')
    ax.set_title(
        f"t = {result['statistic']:.2f}, "
        f"p = {result['pvalue']:.4f}\n"
        f"d = {result['effect_size']:.2f}, "
        f"power = {result['power']:.2f}"
    )
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()

    return fig


def test_ttest_rel(
    x: Union[np.ndarray, pd.Series],
    y: Union[np.ndarray, pd.Series],
    var_x: str = 'before',
    var_y: str = 'after',
    alternative: Literal['two-sided', 'greater', 'less'] = 'two-sided',
    alpha: float = 0.05,
    plot: bool = False,
    return_as: Literal['dict', 'dataframe'] = 'dict'
) -> Union[dict, pd.DataFrame, Tuple[dict, 'matplotlib.figure.Figure'], Tuple[pd.DataFrame, 'matplotlib.figure.Figure']]:
    """
    Perform paired samples t-test (related/dependent samples).

    Parameters
    ----------
    x : array or Series
        First sample (e.g., pre-test, baseline)
    y : array or Series
        Second sample (e.g., post-test, follow-up)
        Must have same length as x
    var_x : str, default 'before'
        Label for first sample
    var_y : str, default 'after'
        Label for second sample
    alternative : {'two-sided', 'greater', 'less'}, default 'two-sided'
        Alternative hypothesis:
        - 'two-sided': means differ
        - 'greater': mean(x - y) > 0
        - 'less': mean(x - y) < 0
    alpha : float, default 0.05
        Significance level
    plot : bool, default False
        Whether to generate visualization
    return_as : {'dict', 'dataframe'}, default 'dict'
        Output format

    Returns
    -------
    results : dict or DataFrame
        Test results (same structure as test_ttest_ind)
    fig : matplotlib.figure.Figure, optional
        Figure object (only if plot=True)

    Notes
    -----
    The paired t-test compares means of matched observations (within-subjects).

    **When to use:**
    - Before-after measurements on same subjects
    - Matched pairs (twins, siblings, matched controls)
    - Repeated measures at two time points

    **Assumptions:**
    - Differences (x - y) are normally distributed
    - Pairs are independent across subjects
    - No assumption about equality of variances

    The test statistic is:

    .. math::
        t = \\frac{\\bar{d}}{s_d / \\sqrt{n}}

    where :math:`\\bar{d}` is mean difference and :math:`s_d` is SD of differences.

    **Effect size** (Cohen's d for paired samples):

    .. math::
        d = \\frac{\\bar{d}}{s_d}

    This measures the standardized change from baseline.

    References
    ----------
    .. [1] Student (1908). "The Probable Error of a Mean". Biometrika, 6(1), 1-25.

    Examples
    --------
    >>> before = np.array([10, 12, 15, 18, 20])
    >>> after = np.array([12, 14, 17, 20, 22])
    >>> result = test_ttest_rel(before, after)
    >>> result['pvalue']
    0.001...

    >>> # With visualization
    >>> result, fig = test_ttest_rel(before, after, plot=True)
    """
    from ...utils._effect_size import cohens_d, interpret_cohens_d
    from ...utils._power import power_ttest
    from ...utils._formatters import p2stars
    from ...utils._normalizers import force_dataframe

    # Convert to numpy arrays and remove NaN
    x = np.asarray(x)
    y = np.asarray(y)

    # Check for paired NaN removal
    valid_mask = ~(np.isnan(x) | np.isnan(y))
    x = x[valid_mask]
    y = y[valid_mask]

    if len(x) != len(y):
        raise ValueError(f"Paired samples must have same length after NaN removal: {len(x)} vs {len(y)}")

    n_pairs = len(x)

    # Perform paired t-test
    t_result = stats.ttest_rel(x, y, alternative=alternative)
    t_stat = float(t_result.statistic)
    pvalue = float(t_result.pvalue)

    # Compute effect size (Cohen's d for paired samples)
    effect_size = cohens_d(x, y, paired=True)
    effect_size_interpretation = interpret_cohens_d(effect_size)

    # Compute statistical power
    power = power_ttest(
        effect_size=abs(effect_size),
        n=n_pairs,
        alpha=alpha,
        alternative=alternative,
        test_type='paired'
    )

    # Create null hypothesis description
    if alternative == 'two-sided':
        H0 = f"μ({var_x} - {var_y}) = 0"
    elif alternative == 'greater':
        H0 = f"μ({var_x} - {var_y}) ≤ 0"
    else:  # less
        H0 = f"μ({var_x} - {var_y}) ≥ 0"

    # Compile results
    result = {
        'test_method': "Paired t-test",
        'statistic_name': 't',
        'statistic': t_stat,
        'alternative': alternative,
        'n_pairs': n_pairs,
        'var_x': var_x,
        'var_y': var_y,
        'pvalue': pvalue,
        'pstars': p2stars(pvalue),
        'alpha': alpha,
        'rejected': pvalue < alpha,
        'effect_size': effect_size,
        'effect_size_metric': "Cohen's d (paired)",
        'effect_size_interpretation': effect_size_interpretation,
        'power': power,
        'H0': H0,
    }

    # Generate plot if requested
    fig = None
    if plot:
        fig = _plot_ttest_rel(x, y, var_x, var_y, result)

    # Convert to requested format
    if return_as == 'dataframe':
        result = force_dataframe(result)

    # Return based on plot option
    if plot:
        return result, fig
    else:
        return result


def _plot_ttest_rel(x, y, var_x, var_y, result):
    """Create visualization for paired t-test."""
    fig, axes = stx.plt.subplots(1, 2, figsize=(12, 5))

    # Compute differences
    diff = x - y

    # Plot 1: Before-after plot
    ax = axes[0]

    # Plot paired lines
    for i in range(len(x)):
        ax.plot([0, 1], [x[i], y[i]], 'o-', color='gray', alpha=0.3)

    # Plot means with error bars
    ax.errorbar([0], [np.mean(x)], yerr=[np.std(x, ddof=1)],
                fmt='o', markersize=12, color='blue', linewidth=3, capsize=5, label=var_x)
    ax.errorbar([1], [np.mean(y)], yerr=[np.std(y, ddof=1)],
                fmt='o', markersize=12, color='orange', linewidth=3, capsize=5, label=var_y)

    ax.set_xticks([0, 1])
    ax.set_xticklabels([var_x, var_y])
    ax.set_ylabel('Value')
    ax.set_title(f'Paired Measurements {result["pstars"]}')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')

    # Plot 2: Difference distribution
    ax = axes[1]

    # Histogram of differences
    ax.hist(diff, bins='auto', alpha=0.7, edgecolor='black', density=True)

    # Add mean difference line
    ax.axvline(np.mean(diff), color='red', linestyle='--', linewidth=2,
               label=f'Mean diff = {np.mean(diff):.2f}')
    ax.axvline(0, color='black', linestyle='-', linewidth=1, alpha=0.5)

    # Add normal curve overlay
    mu_diff, sigma_diff = np.mean(diff), np.std(diff, ddof=1)
    x_fit = np.linspace(np.min(diff), np.max(diff), 100)
    y_fit = stats.norm.pdf(x_fit, mu_diff, sigma_diff)
    ax.plot(x_fit, y_fit, 'r-', linewidth=2, alpha=0.7)

    ax.set_xlabel(f'Difference ({var_x} - {var_y})')
    ax.set_ylabel('Density')
    ax.set_title(
        f"t = {result['statistic']:.2f}, "
        f"p = {result['pvalue']:.4f}\n"
        f"d = {result['effect_size']:.2f}, "
        f"power = {result.get('power', np.nan):.2f}"
    )
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    return fig


def test_ttest_1samp(
    x: Union[np.ndarray, pd.Series],
    popmean: float = 0,
    var_x: str = 'sample',
    alternative: Literal['two-sided', 'greater', 'less'] = 'two-sided',
    alpha: float = 0.05,
    plot: bool = False,
    return_as: Literal['dict', 'dataframe'] = 'dict'
) -> Union[dict, pd.DataFrame, Tuple[dict, 'matplotlib.figure.Figure'], Tuple[pd.DataFrame, 'matplotlib.figure.Figure']]:
    """
    Perform one-sample t-test.

    Parameters
    ----------
    x : array or Series
        Sample data
    popmean : float, default 0
        Expected population mean (null hypothesis value)
    var_x : str, default 'sample'
        Label for sample
    alternative : {'two-sided', 'greater', 'less'}, default 'two-sided'
        Alternative hypothesis:
        - 'two-sided': mean ≠ popmean
        - 'greater': mean > popmean
        - 'less': mean < popmean
    alpha : float, default 0.05
        Significance level
    plot : bool, default False
        Whether to generate visualization
    return_as : {'dict', 'dataframe'}, default 'dict'
        Output format

    Returns
    -------
    results : dict or DataFrame
        Test results
    fig : matplotlib.figure.Figure, optional
        Figure object (only if plot=True)

    Notes
    -----
    The one-sample t-test compares sample mean to a known population mean.

    **When to use:**
    - Test if sample mean differs from theoretical/known value
    - Compare observed data to standard/reference value
    - Test if mean differs from zero (common in difference scores)

    **Assumptions:**
    - Data are normally distributed
    - Observations are independent

    The test statistic is:

    .. math::
        t = \\frac{\\bar{x} - \\mu_0}{s / \\sqrt{n}}

    where :math:`\\mu_0` is the hypothesized population mean.

    **Effect size** (Cohen's d for one sample):

    .. math::
        d = \\frac{\\bar{x} - \\mu_0}{s}

    References
    ----------
    .. [1] Student (1908). "The Probable Error of a Mean". Biometrika, 6(1), 1-25.

    Examples
    --------
    >>> # Test if sample mean differs from 0
    >>> x = np.array([1, 2, 3, 4, 5])
    >>> result = test_ttest_1samp(x, popmean=0)
    >>> result['pvalue']
    0.003...

    >>> # Test if sample mean differs from 100
    >>> scores = np.array([95, 98, 102, 105, 108])
    >>> result = test_ttest_1samp(scores, popmean=100)
    """
    from ...utils._effect_size import cohens_d, interpret_cohens_d
    from ...utils._power import power_ttest
    from ...utils._formatters import p2stars
    from ...utils._normalizers import force_dataframe

    # Convert to numpy array and remove NaN
    x = np.asarray(x)
    x = x[~np.isnan(x)]

    n_x = len(x)

    # Perform one-sample t-test
    t_result = stats.ttest_1samp(x, popmean, alternative=alternative)
    t_stat = float(t_result.statistic)
    pvalue = float(t_result.pvalue)

    # Compute effect size (Cohen's d for one sample)
    effect_size = cohens_d(x, y=None, paired=False)  # One-sample version
    effect_size_interpretation = interpret_cohens_d(effect_size)

    # Compute statistical power
    power = power_ttest(
        effect_size=abs(effect_size),
        n=n_x,
        alpha=alpha,
        alternative=alternative,
        test_type='one-sample'
    )

    # Create null hypothesis description
    if alternative == 'two-sided':
        H0 = f"μ({var_x}) = {popmean}"
    elif alternative == 'greater':
        H0 = f"μ({var_x}) ≤ {popmean}"
    else:  # less
        H0 = f"μ({var_x}) ≥ {popmean}"

    # Compile results
    result = {
        'test_method': "One-sample t-test",
        'statistic_name': 't',
        'statistic': t_stat,
        'alternative': alternative,
        'n_x': n_x,
        'var_x': var_x,
        'popmean': popmean,
        'sample_mean': float(np.mean(x)),
        'pvalue': pvalue,
        'pstars': p2stars(pvalue),
        'alpha': alpha,
        'rejected': pvalue < alpha,
        'effect_size': effect_size,
        'effect_size_metric': "Cohen's d (one-sample)",
        'effect_size_interpretation': effect_size_interpretation,
        'power': power,
        'H0': H0,
    }

    # Generate plot if requested
    fig = None
    if plot:
        fig = _plot_ttest_1samp(x, popmean, var_x, result)

    # Convert to requested format
    if return_as == 'dataframe':
        result = force_dataframe(result)

    # Return based on plot option
    if plot:
        return result, fig
    else:
        return result


def _plot_ttest_1samp(x, popmean, var_x, result):
    """Create visualization for one-sample t-test."""
    fig, axes = stx.plt.subplots(1, 2, figsize=(12, 5))

    # Plot 1: Histogram with reference line
    ax = axes[0]

    # Histogram
    ax.hist(x, bins='auto', alpha=0.7, edgecolor='black', density=True)

    # Add sample mean line
    ax.axvline(np.mean(x), color='blue', linestyle='--', linewidth=2,
               label=f'Sample mean = {np.mean(x):.2f}')

    # Add population mean reference line
    ax.axvline(popmean, color='red', linestyle='-', linewidth=2,
               label=f'H0: μ = {popmean}')

    # Add normal curve overlay
    mu, sigma = np.mean(x), np.std(x, ddof=1)
    x_fit = np.linspace(np.min(x), np.max(x), 100)
    y_fit = stats.norm.pdf(x_fit, mu, sigma)
    ax.plot(x_fit, y_fit, 'b-', linewidth=2, alpha=0.5)

    ax.set_xlabel('Value')
    ax.set_ylabel('Density')
    ax.set_title(f'Sample Distribution {result["pstars"]}')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Plot 2: Box plot with reference
    ax = axes[1]

    # Box plot
    bp = ax.boxplot([x], positions=[0], widths=0.4, patch_artist=True, showfliers=True)
    bp['boxes'][0].set_facecolor('lightblue')

    # Add reference line for population mean
    ax.axhline(popmean, color='red', linestyle='-', linewidth=2,
               label=f'H0: μ = {popmean}')

    # Add confidence interval
    ci = stats.t.interval(1 - alpha, len(x) - 1,
                          loc=np.mean(x),
                          scale=stats.sem(x))
    ax.plot([0, 0], ci, 'b-', linewidth=3, label=f'{int((1-result["alpha"])*100)}% CI')

    ax.set_xticks([0])
    ax.set_xticklabels([var_x])
    ax.set_ylabel('Value')
    ax.set_title(
        f"t = {result['statistic']:.2f}, "
        f"p = {result['pvalue']:.4f}\n"
        f"d = {result['effect_size']:.2f}, "
        f"power = {result.get('power', np.nan):.2f}"
    )
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()

    return fig


"""Main function"""
def main(args):
    """Demonstrate independent t-test functionality."""
    logger.info("Demonstrating independent samples t-test")

    # Set random seed
    np.random.seed(42)

    # Example 1: Significant difference
    logger.info("\n=== Example 1: Significant difference ===")

    x1 = np.random.normal(0, 1, 50)
    y1 = np.random.normal(0.8, 1, 50)  # Large effect

    result1 = test_ttest_ind(
        x1, y1,
        var_x='Control',
        var_y='Treatment',
        return_as='dict'
    )

    logger.info(f"Test: {result1['test_method']}")
    logger.info(f"t = {result1['statistic']:.3f}")
    logger.info(f"p = {result1['pvalue']:.4f} {result1['pstars']}")
    logger.info(f"Effect size: {result1['effect_size']:.3f}")
    logger.info(f"Power: {result1['power']:.3f}")
    logger.info(f"Rejected: {result1['rejected']}")

    # Example 2: Non-significant difference
    logger.info("\n=== Example 2: Non-significant difference ===")

    x2 = np.random.normal(0, 1, 30)
    y2 = np.random.normal(0.2, 1, 30)  # Small effect

    result2 = test_ttest_ind(
        x2, y2,
        var_x='Group A',
        var_y='Group B'
    )

    logger.info(f"t = {result2['statistic']:.3f}")
    logger.info(f"p = {result2['pvalue']:.4f} {result2['pstars']}")
    logger.info(f"Effect size: {result2['effect_size']:.3f}")
    logger.info(f"Power: {result2['power']:.3f}")

    # Example 3: Welch's t-test (unequal variances)
    logger.info("\n=== Example 3: Welch's t-test ===")

    x3 = np.random.normal(0, 1, 40)
    y3 = np.random.normal(0.5, 2, 40)  # Different variance

    result3 = test_ttest_ind(
        x3, y3,
        var_x='Low Variance',
        var_y='High Variance',
        equal_var=False
    )

    logger.info(f"Test: {result3['test_method']}")
    logger.info(f"t = {result3['statistic']:.3f}")
    logger.info(f"p = {result3['pvalue']:.4f} {result3['pstars']}")

    # Example 4: One-sided test
    logger.info("\n=== Example 4: One-sided test ===")

    x4 = np.random.normal(0, 1, 50)
    y4 = np.random.normal(0.6, 1, 50)

    result4_two = test_ttest_ind(x4, y4, alternative='two-sided')
    result4_one = test_ttest_ind(x4, y4, alternative='less')

    logger.info(f"Two-sided: p = {result4_two['pvalue']:.4f} {result4_two['pstars']}")
    logger.info(f"One-sided:  p = {result4_one['pvalue']:.4f} {result4_one['pstars']}")

    # Example 5: With visualization
    logger.info("\n=== Example 5: With visualization ===")

    x5 = np.random.normal(10, 2, 60)
    y5 = np.random.normal(12, 2, 60)

    result5, fig5 = test_ttest_ind(
        x5, y5,
        var_x='Baseline',
        var_y='Follow-up',
        plot=True
    )

    stx.io.save(fig5, './ttest_ind_demo.png')
    logger.info("Visualization saved")

    # Example 6: DataFrame output
    logger.info("\n=== Example 6: DataFrame output ===")

    df_result = test_ttest_ind(x1, y1, return_as='dataframe')
    logger.info(f"\n{df_result.T}")

    # Example 7: Multiple tests
    logger.info("\n=== Example 7: Multiple tests ===")

    from ...utils._normalizers import combine_results

    results_list = []
    for i in range(5):
        x = np.random.normal(0, 1, 40)
        y = np.random.normal(0.5, 1, 40)
        result = test_ttest_ind(
            x, y,
            var_x=f'Control_{i}',
            var_y=f'Treatment_{i}'
        )
        results_list.append(result)

    df_all = combine_results(results_list)
    logger.info(f"\n{df_all[['var_x', 'var_y', 'pvalue', 'pstars', 'effect_size', 'power']]}")

    return 0


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Demonstrate independent samples t-test'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    return parser.parse_args()


def run_main():
    """Initialize SciTeX framework and run main."""
    global CONFIG, sys, plt, rng

    import sys
    import matplotlib.pyplot as plt

    args = parse_args()

    CONFIG, sys.stdout, sys.stderr, plt, CC, rng = stx.session.start(
        sys,
        plt,
        args=args,
        file=__file__,
        verbose=args.verbose,
        agg=True,
    )

    exit_status = main(args)

    stx.session.close(
        CONFIG,
        verbose=args.verbose,
        exit_status=exit_status,
    )


if __name__ == '__main__':
    run_main()

# EOF
