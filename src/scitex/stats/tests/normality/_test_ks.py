#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-01 17:30:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/stats/tests/normality/_test_ks.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/stats/tests/normality/_test_ks.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------


"""
Functionalities:
  - Perform Kolmogorov-Smirnov test for distribution comparison
  - One-sample KS test (compare to reference distribution)
  - Two-sample KS test (compare two empirical distributions)
  - Generate CDF comparison plots
  - Support flexible output formats (dict or DataFrame)

Dependencies:
  - packages: numpy, pandas, scipy, matplotlib

IO:
  - input: One or two samples (arrays or Series)
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
def test_ks_1samp(
    x: Union[np.ndarray, pd.Series],
    cdf: Union[str, callable] = 'norm',
    args: tuple = (),
    var_x: str = 'x',
    alternative: Literal['two-sided', 'less', 'greater'] = 'two-sided',
    alpha: float = 0.05,
    plot: bool = False,
    return_as: Literal['dict', 'dataframe'] = 'dict',
    decimals: int = 3
) -> Union[dict, pd.DataFrame, Tuple[dict, 'matplotlib.figure.Figure'], Tuple[pd.DataFrame, 'matplotlib.figure.Figure']]:
    """
    Perform one-sample Kolmogorov-Smirnov test.

    Parameters
    ----------
    x : array or Series
        Sample to test
    cdf : str or callable, default 'norm'
        Reference distribution. Either:
        - String: 'norm', 'uniform', 'expon', etc. (scipy.stats distribution name)
        - Callable: CDF function
    args : tuple, default ()
        Distribution parameters (e.g., (loc, scale) for normal)
    var_x : str, default 'x'
        Label for sample
    alternative : {'two-sided', 'less', 'greater'}, default 'two-sided'
        Alternative hypothesis
    alpha : float, default 0.05
        Significance level
    plot : bool, default False
        Whether to generate CDF comparison plot
    return_as : {'dict', 'dataframe'}, default 'dict'
        Output format
    decimals : int, default 3
        Number of decimal places for rounding

    Returns
    -------
    results : dict or DataFrame
        Test results including:
        - test_method: 'Kolmogorov-Smirnov test (1-sample)'
        - statistic_name: 'D'
        - statistic: KS D-statistic (maximum CDF difference)
        - pvalue: p-value
        - pstars: Significance stars
        - rejected: Whether null hypothesis is rejected
        - n_x: Sample size
        - var_x: Variable label
        - reference_distribution: Name of reference distribution
        - H0: Null hypothesis description
    fig : matplotlib.figure.Figure, optional
        Figure with CDF comparison (only if plot=True)

    Notes
    -----
    The one-sample Kolmogorov-Smirnov test compares the empirical cumulative
    distribution function (ECDF) of the sample against a reference CDF.

    **Null Hypothesis (H0)**: Data follow the specified distribution

    **Test Statistic D**:

    .. math::
        D = \\sup_x |F_n(x) - F(x)|

    Where:
    - F_n(x): Empirical CDF of sample
    - F(x): Reference CDF

    **Advantages**:
    - Distribution-free (no assumptions about data)
    - Can test against any continuous distribution
    - More general than Shapiro-Wilk (not limited to normality)

    **Disadvantages**:
    - Less powerful than Shapiro-Wilk for normality testing
    - Sensitive to sample size (large n → high power, may detect trivial deviations)
    - Assumes continuous distribution (not suitable for discrete data)

    **When to use**:
    - Testing goodness-of-fit to any continuous distribution
    - Comparing sample to theoretical distribution
    - When Shapiro-Wilk is not applicable (non-normal distributions)
    - Large sample sizes (n > 50)

    References
    ----------
    .. [1] Kolmogorov, A. (1933). "Sulla determinazione empirica di una legge
           di distribuzione". Giornale dell'Istituto Italiano degli Attuari, 4, 83-91.
    .. [2] Smirnov, N. (1948). "Table for estimating the goodness of fit of
           empirical distributions". Annals of Mathematical Statistics, 19(2), 279-281.

    Examples
    --------
    >>> # Test if data are normally distributed
    >>> x = np.random.normal(0, 1, 100)
    >>> result = test_ks_1samp(x, cdf='norm', args=(0, 1))
    >>> result['rejected']
    False

    >>> # Test if data are uniformly distributed
    >>> x = np.random.uniform(0, 1, 100)
    >>> result = test_ks_1samp(x, cdf='uniform', args=(0, 1))
    """
    from ...utils._formatters import p2stars
    from ...utils._normalizers import force_dataframe, convert_results

    # Convert to numpy array and remove NaN
    x = np.asarray(x)
    x = x[~np.isnan(x)]
    n_x = len(x)

    # Check sample size
    if n_x < 3:
        raise ValueError("KS test requires at least 3 observations")

    # Get reference distribution
    if isinstance(cdf, str):
        ref_dist_name = cdf
        # Get scipy distribution
        ref_dist = getattr(stats, cdf)
        if args:
            cdf_func = lambda t: ref_dist.cdf(t, *args)
        else:
            cdf_func = ref_dist.cdf
    else:
        ref_dist_name = 'custom'
        cdf_func = cdf

    # Perform KS test
    ks_result = stats.ks_1samp(x, cdf_func, alternative=alternative)
    d_stat = float(ks_result.statistic)
    pvalue = float(ks_result.pvalue)

    # Determine if distribution matches
    rejected = pvalue < alpha
    matches = not rejected

    # Compile results
    result = {
        'test_method': 'Kolmogorov-Smirnov test (1-sample)',
        'statistic_name': 'D',
        'statistic': round(d_stat, decimals),
        'n_x': n_x,
        'var_x': var_x,
        'pvalue': round(pvalue, decimals),
        'pstars': p2stars(pvalue),
        'alpha': alpha,
        'rejected': rejected,
        'matches_distribution': matches,
        'reference_distribution': ref_dist_name,
        'H0': f'Data follow {ref_dist_name} distribution',
    }

    # Generate plot if requested
    fig = None
    if plot:
        fig = _plot_ks_1samp(x, cdf_func, var_x, result, ref_dist_name)

    # Convert to requested format
    if return_as == 'dataframe':
        result = force_dataframe(result)
    elif return_as not in ['dict', 'dataframe']:
        return convert_results(result, return_as=return_as)

    # Return based on plot option
    if plot:
        return result, fig
    else:
        return result


def test_ks_2samp(
    x: Union[np.ndarray, pd.Series],
    y: Union[np.ndarray, pd.Series],
    var_x: str = 'x',
    var_y: str = 'y',
    alternative: Literal['two-sided', 'less', 'greater'] = 'two-sided',
    alpha: float = 0.05,
    plot: bool = False,
    return_as: Literal['dict', 'dataframe'] = 'dict',
    decimals: int = 3
) -> Union[dict, pd.DataFrame, Tuple[dict, 'matplotlib.figure.Figure'], Tuple[pd.DataFrame, 'matplotlib.figure.Figure']]:
    """
    Perform two-sample Kolmogorov-Smirnov test.

    Parameters
    ----------
    x, y : arrays or Series
        Two samples to compare
    var_x, var_y : str
        Labels for samples
    alternative : {'two-sided', 'less', 'greater'}, default 'two-sided'
        Alternative hypothesis
    alpha : float, default 0.05
        Significance level
    plot : bool, default False
        Whether to generate CDF comparison plot
    return_as : {'dict', 'dataframe'}, default 'dict'
        Output format
    decimals : int, default 3
        Number of decimal places for rounding

    Returns
    -------
    results : dict or DataFrame
        Test results including:
        - test_method: 'Kolmogorov-Smirnov test (2-sample)'
        - statistic_name: 'D'
        - statistic: KS D-statistic
        - pvalue: p-value
        - pstars: Significance stars
        - rejected: Whether null hypothesis is rejected
        - n_x, n_y: Sample sizes
        - var_x, var_y: Variable labels
        - H0: Null hypothesis description
    fig : matplotlib.figure.Figure, optional
        Figure with CDF comparison (only if plot=True)

    Notes
    -----
    The two-sample Kolmogorov-Smirnov test compares the ECDFs of two samples.

    **Null Hypothesis (H0)**: Both samples come from the same distribution

    **Test Statistic D**:

    .. math::
        D = \\sup_x |F_{n_1}(x) - F_{n_2}(x)|

    Where F_{n_1} and F_{n_2} are the empirical CDFs.

    **Advantages**:
    - Distribution-free (non-parametric)
    - Tests entire distribution, not just location
    - Can detect differences in location, scale, or shape

    **Disadvantages**:
    - Less powerful than t-test when assumptions are met
    - Most sensitive to differences near the center of distributions
    - Less sensitive to tail differences

    **When to use**:
    - Comparing two independent samples
    - No assumptions about distribution shape
    - Want to test overall distribution equality (not just means)
    - Alternative to t-test when normality violated

    **Comparison with other tests**:
    - vs t-test: More robust, less powerful
    - vs Mann-Whitney U: Tests different hypotheses (distribution vs median)
    - vs Brunner-Munzel: KS tests full distribution, BM tests P(X>Y)

    Examples
    --------
    >>> # Two samples from same distribution
    >>> x = np.random.normal(0, 1, 100)
    >>> y = np.random.normal(0, 1, 100)
    >>> result = test_ks_2samp(x, y)
    >>> result['rejected']
    False

    >>> # Two samples from different distributions
    >>> x = np.random.normal(0, 1, 100)
    >>> y = np.random.normal(2, 1, 100)
    >>> result = test_ks_2samp(x, y)
    >>> result['rejected']
    True
    """
    from ...utils._formatters import p2stars
    from ...utils._normalizers import force_dataframe, convert_results

    # Convert to numpy arrays and remove NaN
    x = np.asarray(x)
    y = np.asarray(y)
    x = x[~np.isnan(x)]
    y = y[~np.isnan(y)]

    n_x = len(x)
    n_y = len(y)

    # Perform two-sample KS test
    ks_result = stats.ks_2samp(x, y, alternative=alternative)
    d_stat = float(ks_result.statistic)
    pvalue = float(ks_result.pvalue)

    # Determine rejection
    rejected = pvalue < alpha

    # Compile results
    result = {
        'test_method': 'Kolmogorov-Smirnov test (2-sample)',
        'statistic_name': 'D',
        'statistic': round(d_stat, decimals),
        'n_x': n_x,
        'n_y': n_y,
        'var_x': var_x,
        'var_y': var_y,
        'pvalue': round(pvalue, decimals),
        'pstars': p2stars(pvalue),
        'alpha': alpha,
        'rejected': rejected,
        'same_distribution': not rejected,
        'H0': 'Both samples come from the same distribution',
    }

    # Generate plot if requested
    fig = None
    if plot:
        fig = _plot_ks_2samp(x, y, var_x, var_y, result)

    # Convert to requested format
    if return_as == 'dataframe':
        result = force_dataframe(result)
    elif return_as not in ['dict', 'dataframe']:
        return convert_results(result, return_as=return_as)

    # Return based on plot option
    if plot:
        return result, fig
    else:
        return result


def _plot_ks_1samp(x, cdf_func, var_x, result, ref_dist_name):
    """Create CDF comparison plot for one-sample KS test."""
    fig, axes = stx.plt.subplots(1, 2, figsize=(14, 6))

    # Plot 1: CDF comparison
    ax = axes[0]

    # Compute ECDF
    x_sorted = np.sort(x)
    ecdf = np.arange(1, len(x) + 1) / len(x)

    # Compute reference CDF
    ref_cdf = cdf_func(x_sorted)

    # Plot both CDFs
    ax.step(x_sorted, ecdf, where='post', linewidth=2, label=f'Empirical ({var_x})', color='blue')
    ax.plot(x_sorted, ref_cdf, linewidth=2, label=f'Reference ({ref_dist_name})', color='red')

    # Mark maximum difference
    diff = np.abs(ecdf - ref_cdf)
    max_idx = np.argmax(diff)
    ax.vlines(x_sorted[max_idx], ecdf[max_idx], ref_cdf[max_idx],
              colors='green', linestyles='dashed', linewidth=2,
              label=f'D = {result["statistic"]:.3f}')

    ax.set_xlabel('Value')
    ax.set_ylabel('Cumulative Probability')
    ax.set_title(f'CDF Comparison: {var_x} vs {ref_dist_name}')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Add text with results
    text_str = (
        f"D = {result['statistic']:.3f}\n"
        f"p = {result['pvalue']:.4f} {result['pstars']}\n"
        f"Matches: {result['matches_distribution']}"
    )
    ax.text(
        0.98, 0.02, text_str,
        transform=ax.transAxes,
        verticalalignment='bottom',
        horizontalalignment='right',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
        fontsize=10
    )

    # Plot 2: Histogram with reference PDF
    ax = axes[1]

    ax.hist(x, bins='auto', density=True, alpha=0.7, edgecolor='black', label='Data')

    # If reference is a known distribution, plot PDF
    if ref_dist_name != 'custom':
        x_range = np.linspace(np.min(x), np.max(x), 200)
        ref_dist = getattr(stats, ref_dist_name)
        # Try to get PDF
        try:
            if hasattr(ref_dist, 'pdf'):
                pdf_vals = ref_dist.pdf(x_range)
                ax.plot(x_range, pdf_vals, 'r-', linewidth=2, label=f'{ref_dist_name} PDF')
        except:
            pass

    ax.set_xlabel('Value')
    ax.set_ylabel('Density')
    ax.set_title(f'Distribution: {var_x}')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    return fig


def _plot_ks_2samp(x, y, var_x, var_y, result):
    """Create CDF comparison plot for two-sample KS test."""
    fig, axes = stx.plt.subplots(1, 2, figsize=(14, 6))

    # Plot 1: CDF comparison
    ax = axes[0]

    # Compute ECDFs
    x_sorted = np.sort(x)
    ecdf_x = np.arange(1, len(x) + 1) / len(x)

    y_sorted = np.sort(y)
    ecdf_y = np.arange(1, len(y) + 1) / len(y)

    # Plot both ECDFs
    ax.step(x_sorted, ecdf_x, where='post', linewidth=2, label=var_x, color='blue')
    ax.step(y_sorted, ecdf_y, where='post', linewidth=2, label=var_y, color='red')

    ax.set_xlabel('Value')
    ax.set_ylabel('Cumulative Probability')
    ax.set_title(f'CDF Comparison: {var_x} vs {var_y}')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Add text with results
    text_str = (
        f"D = {result['statistic']:.3f}\n"
        f"p = {result['pvalue']:.4f} {result['pstars']}\n"
        f"Same dist: {result['same_distribution']}"
    )
    ax.text(
        0.98, 0.02, text_str,
        transform=ax.transAxes,
        verticalalignment='bottom',
        horizontalalignment='right',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
        fontsize=10
    )

    # Plot 2: Overlapping histograms
    ax = axes[1]

    ax.hist(x, bins='auto', density=True, alpha=0.5, label=var_x, color='blue', edgecolor='black')
    ax.hist(y, bins='auto', density=True, alpha=0.5, label=var_y, color='red', edgecolor='black')

    ax.set_xlabel('Value')
    ax.set_ylabel('Density')
    ax.set_title('Distribution Comparison')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    return fig


"""Main function"""
def main(args):
    """Demonstrate Kolmogorov-Smirnov test functionality."""
    logger.info("Demonstrating Kolmogorov-Smirnov tests")

    # Set random seed
    np.random.seed(42)

    # Example 1: One-sample test - normal data
    logger.info("\n=== Example 1: One-sample KS test (normal data) ===")

    x_normal = np.random.normal(0, 1, 100)
    result1 = test_ks_1samp(x_normal, cdf='norm', args=(0, 1), var_x='Normal data')

    logger.info(f"D = {result1['statistic']:.3f}")
    logger.info(f"p = {result1['pvalue']:.4f} {result1['pstars']}")
    logger.info(f"Matches normal distribution: {result1['matches_distribution']}")

    # Example 2: One-sample test - exponential data tested against normal
    logger.info("\n=== Example 2: One-sample KS test (exponential data vs normal) ===")

    x_exp = np.random.exponential(2, 100)
    result2 = test_ks_1samp(x_exp, cdf='norm', args=(np.mean(x_exp), np.std(x_exp)),
                            var_x='Exponential data')

    logger.info(f"D = {result2['statistic']:.3f}")
    logger.info(f"p = {result2['pvalue']:.4f} {result2['pstars']}")
    logger.info(f"Matches normal distribution: {result2['matches_distribution']}")

    # Example 3: One-sample test - uniform data
    logger.info("\n=== Example 3: One-sample KS test (uniform data) ===")

    x_unif = np.random.uniform(0, 1, 100)
    result3 = test_ks_1samp(x_unif, cdf='uniform', args=(0, 1), var_x='Uniform data')

    logger.info(f"D = {result3['statistic']:.3f}")
    logger.info(f"p = {result3['pvalue']:.4f}")
    logger.info(f"Matches uniform distribution: {result3['matches_distribution']}")

    # Example 4: One-sample test with visualization
    logger.info("\n=== Example 4: One-sample KS test with visualization ===")

    x_mixed = np.concatenate([np.random.normal(0, 1, 90), np.random.normal(3, 1, 10)])
    result4, fig4 = test_ks_1samp(
        x_mixed,
        cdf='norm',
        args=(0, 1),
        var_x='Mixed data',
        plot=True
    )

    logger.info(f"D = {result4['statistic']:.3f}, p = {result4['pvalue']:.4f}")
    stx.io.save(fig4, './ks_1samp_demo.png')
    logger.info("Visualization saved")

    # Example 5: Two-sample test - same distribution
    logger.info("\n=== Example 5: Two-sample KS test (same distribution) ===")

    x1 = np.random.normal(0, 1, 100)
    y1 = np.random.normal(0, 1, 100)

    result5 = test_ks_2samp(x1, y1, var_x='Sample 1', var_y='Sample 2')

    logger.info(f"D = {result5['statistic']:.3f}")
    logger.info(f"p = {result5['pvalue']:.4f}")
    logger.info(f"Same distribution: {result5['same_distribution']}")

    # Example 6: Two-sample test - different means
    logger.info("\n=== Example 6: Two-sample KS test (different means) ===")

    x2 = np.random.normal(0, 1, 100)
    y2 = np.random.normal(2, 1, 100)

    result6 = test_ks_2samp(x2, y2, var_x='Group A', var_y='Group B')

    logger.info(f"D = {result6['statistic']:.3f}")
    logger.info(f"p = {result6['pvalue']:.4f} {result6['pstars']}")
    logger.info(f"Same distribution: {result6['same_distribution']}")

    # Example 7: Two-sample test - different variances
    logger.info("\n=== Example 7: Two-sample KS test (different variances) ===")

    x3 = np.random.normal(0, 1, 100)
    y3 = np.random.normal(0, 3, 100)

    result7 = test_ks_2samp(x3, y3, var_x='Low variance', var_y='High variance')

    logger.info(f"D = {result7['statistic']:.3f}")
    logger.info(f"p = {result7['pvalue']:.4f} {result7['pstars']}")
    logger.info("KS test detected difference in distributions (variances)")

    # Example 8: Two-sample test with visualization
    logger.info("\n=== Example 8: Two-sample KS test with visualization ===")

    x4 = np.random.normal(5, 1, 80)
    y4 = np.random.exponential(2, 80)

    result8, fig8 = test_ks_2samp(
        x4, y4,
        var_x='Normal',
        var_y='Exponential',
        plot=True
    )

    logger.info(f"D = {result8['statistic']:.3f}, p = {result8['pvalue']:.4f}")
    stx.io.save(fig8, './ks_2samp_demo.png')
    logger.info("Visualization saved")

    # Example 9: Comparison with Shapiro-Wilk
    logger.info("\n=== Example 9: KS vs Shapiro-Wilk for normality ===")

    from ._test_shapiro import test_shapiro

    x_test = np.random.exponential(2, 100)

    ks_result = test_ks_1samp(x_test, cdf='norm',
                              args=(np.mean(x_test), np.std(x_test)))
    shapiro_result = test_shapiro(x_test)

    logger.info(f"KS test:      D = {ks_result['statistic']:.3f}, p = {ks_result['pvalue']:.4f}")
    logger.info(f"Shapiro-Wilk: W = {shapiro_result['statistic']:.4f}, p = {shapiro_result['pvalue']:.4f}")
    logger.info("Note: Shapiro-Wilk is more powerful for normality testing")

    # Example 10: Export results
    logger.info("\n=== Example 10: Export results ===")

    from ...utils._normalizers import convert_results, force_dataframe

    test_results = [result1, result2, result3, result5, result6, result7]

    df = force_dataframe(test_results)
    logger.info(f"\nDataFrame shape: {df.shape}")

    convert_results(test_results, return_as='excel', path='./ks_tests.xlsx')
    logger.info("Results exported to Excel")

    return 0


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Demonstrate Kolmogorov-Smirnov tests'
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
