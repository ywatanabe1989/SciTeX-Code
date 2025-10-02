#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-01 15:30:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/stats/tests/normality/_test_shapiro.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------


"""
Functionalities:
  - Perform Shapiro-Wilk test for normality
  - Generate Q-Q plots for visual assessment
  - Provide interpretation and recommendations
  - Support flexible output formats (dict or DataFrame)

Dependencies:
  - packages: numpy, pandas, scipy, matplotlib

IO:
  - input: One sample (array or Series)
  - output: Test results (dict or DataFrame) and optional figure
"""

"""Imports"""
import sys
import argparse
import numpy as np
import pandas as pd
from typing import Union, Optional, Literal
from scipy import stats
import matplotlib.pyplot as plt
import matplotlib.axes
import scitex as stx
from scitex.logging import getLogger

logger = getLogger(__name__)

"""Functions"""
def test_shapiro(
    x: Union[np.ndarray, pd.Series],
    var_x: str = 'x',
    alpha: float = 0.05,
    plot: bool = False,
    ax: Optional[matplotlib.axes.Axes] = None,
    return_as: Literal['dict', 'dataframe'] = 'dict',
    verbose: bool = False
) -> Union[dict, pd.DataFrame]:
    """
    Perform Shapiro-Wilk test for normality.

    Parameters
    ----------
    x : array or Series
        Sample to test
    var_x : str, default 'x'
        Label for sample
    alpha : float, default 0.05
        Significance level
    plot : bool, default False
        Whether to generate Q-Q plot
    ax : matplotlib.axes.Axes, optional
        Axes to plot on. If provided, plot is set to True
    return_as : {'dict', 'dataframe'}, default 'dict'
        Output format
    verbose : bool, default False
        If True, print test results to logger

    Returns
    -------
    results : dict or DataFrame
        Test results including:
        - test_method: 'Shapiro-Wilk test'
        - statistic: W-statistic value (0 to 1, closer to 1 = more normal)
        - pvalue: p-value
        - stars: Significance stars
        - significant: Whether null hypothesis is rejected (True = not normal)
        - normal: Whether data appears normal (True = normal)
        - recommendation: Suggested statistical approach
        - n: Sample size
        - var_x: Variable label

    Notes
    -----
    The Shapiro-Wilk test tests the null hypothesis that data come from a
    normal distribution.

    **Null Hypothesis (H0)**: Data are normally distributed

    **Test Statistic W**: Ranges from 0 to 1
    - W close to 1: Data appear normal
    - W much less than 1: Data deviate from normality

    **p-value interpretation**:
    - p > α (typically 0.05): Fail to reject H0, data appear normal
    - p ≤ α: Reject H0, data significantly deviate from normality

    **Important considerations**:
    - Sensitive to sample size: with n > 50, may detect trivial deviations
    - Works best for 3 ≤ n ≤ 5000
    - Should be combined with visual inspection (Q-Q plots)
    - Large samples: focus on Q-Q plots over p-values
    - Small samples: test may lack power to detect non-normality

    **Recommendations based on results**:
    - Normal (p > 0.05): Use parametric tests (t-test, ANOVA, Pearson)
    - Non-normal (p ≤ 0.05): Use non-parametric tests (Brunner-Munzel, Wilcoxon, Spearman)
    - Borderline: Check Q-Q plot and consider robustness

    References
    ----------
    .. [1] Shapiro, S. S., & Wilk, M. B. (1965). "An analysis of variance test
           for normality (complete samples)". Biometrika, 52(3-4), 591-611.
    .. [2] Razali, N. M., & Wah, Y. B. (2011). "Power comparisons of
           Shapiro-Wilk, Kolmogorov-Smirnov, Lilliefors and Anderson-Darling
           tests". Journal of Statistical Modeling and Analytics, 2(1), 21-33.

    Examples
    --------
    >>> # Normal data
    >>> x = np.random.normal(0, 1, 100)
    >>> result = test_shapiro(x)
    >>> result['normal']
    True

    >>> # Non-normal data
    >>> x = np.random.exponential(2, 100)
    >>> result = test_shapiro(x)
    >>> result['normal']
    False

    >>> # With Q-Q plot
    >>> result, fig = test_shapiro(x, plot=True)
    """
    from ...utils._formatters import p2stars
    from ...utils._normalizers import force_dataframe

    # Convert to numpy array and remove NaN
    x = np.asarray(x)
    x = x[~np.isnan(x)]

    n_x = len(x)

    # Check sample size
    if n_x < 3:
        raise ValueError("Shapiro-Wilk test requires at least 3 observations")
    if n_x > 5000:
        logger.warning(
            f"Sample size n={n_x} is large. "
            "Shapiro-Wilk may detect trivial deviations. "
            "Consider visual inspection (Q-Q plot) instead."
        )

    # Perform Shapiro-Wilk test
    sw_result = stats.shapiro(x)
    w_stat = float(sw_result.statistic)
    pvalue = float(sw_result.pvalue)

    # Determine if data appear normal
    normal = pvalue > alpha
    rejected = not normal

    # Generate recommendation
    if normal:
        recommendation = "Data appear normal. Parametric tests (t-test, ANOVA, Pearson) are appropriate."
    else:
        recommendation = "Data deviate from normality. Consider non-parametric tests (Brunner-Munzel, Wilcoxon, Spearman)."

    # Add sample size consideration
    if n_x > 100:
        recommendation += " Note: Large sample size - inspect Q-Q plot for practical significance."
    elif n_x < 20:
        recommendation += " Note: Small sample size - test may have low power."

    # Compile results
    result = {
        'test_method': 'Shapiro-Wilk test',
        'statistic': w_stat,
        'n': n_x,
        'var_x': var_x,
        'pvalue': pvalue,
        'stars': p2stars(pvalue),
        'alpha': alpha,
        'significant': rejected,
        'normal': normal,
        'recommendation': recommendation,
    }

    # Log results if verbose
    if verbose:
        logger.info(f"Shapiro-Wilk: W = {w_stat:.4f}, p = {pvalue:.4f} {p2stars(pvalue)}")
        logger.info(f"Normal: {normal}")

    # Auto-enable plotting if ax is provided
    if ax is not None:
        plot = True

    # Generate plot if requested
    if plot:
        if ax is None:
            fig, axes = stx.plt.subplots(1, 2, figsize=(12, 5))
            _plot_qq_full(x, var_x, result, axes)
        else:
            _plot_qq_simple(x, var_x, result, ax)

    # Convert to requested format
    if return_as == 'dataframe':
        result = force_dataframe(result)
    elif return_as not in ['dict', 'dataframe']:
        from ...utils._normalizers import convert_results
        return convert_results(result, return_as=return_as)

    return result


def _plot_qq_full(x, var_x, result, axes):
    """Create 2-panel Q-Q plot with histogram."""
    # Plot 1: Q-Q plot
    ax = axes[0]

    # Compute theoretical quantiles
    (osm, osr), (slope, intercept, r) = stats.probplot(x, dist='norm')

    # Plot
    ax.scatter(osm, osr, alpha=0.6, s=30)
    ax.plot(osm, slope * osm + intercept, 'r-', linewidth=2, label='Expected (normal)')

    ax.set_xlabel('Theoretical Quantiles')
    ax.set_ylabel('Sample Quantiles')
    ax.set_title(f'Q-Q Plot: {var_x}')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Add text with results
    text_str = (
        f"W = {result['statistic']:.4f}\n"
        f"p = {result['pvalue']:.4f} {result['stars']}\n"
        f"Normal: {result['normal']}"
    )
    ax.text(
        0.05, 0.95, text_str,
        transform=ax.transAxes,
        verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
        fontsize=10
    )

    # Plot 2: Histogram with normal curve overlay
    ax = axes[1]

    # Histogram
    n, bins, patches = ax.hist(x, bins='auto', density=True, alpha=0.7, edgecolor='black')

    # Fit normal distribution
    mu, sigma = np.mean(x), np.std(x, ddof=1)
    x_fit = np.linspace(np.min(x), np.max(x), 100)
    y_fit = stats.norm.pdf(x_fit, mu, sigma)

    ax.plot(x_fit, y_fit, 'r-', linewidth=2, label=f'Normal(μ={mu:.2f}, σ={sigma:.2f})')

    ax.set_xlabel('Value')
    ax.set_ylabel('Density')
    ax.set_title(f'Histogram: {var_x}')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()


def _plot_qq_simple(x, var_x, result, ax):
    """Create single Q-Q plot on provided axes."""
    # Compute theoretical quantiles
    (osm, osr), (slope, intercept, r) = stats.probplot(x, dist='norm')

    # Plot
    ax.scatter(osm, osr, alpha=0.6, s=30)
    ax.plot(osm, slope * osm + intercept, 'r-', linewidth=2, label='Expected (normal)')

    ax.set_xlabel('Theoretical Quantiles')
    ax.set_ylabel('Sample Quantiles')
    ax.set_title(f'Q-Q Plot: {var_x}')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Add text with results
    text_str = (
        f"W = {result['statistic']:.4f}\n"
        f"p = {result['pvalue']:.4f} {result['stars']}\n"
        f"Normal: {result['normal']}"
    )
    ax.text(
        0.05, 0.95, text_str,
        transform=ax.transAxes,
        verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
        fontsize=10
    )


def test_normality(
    *samples,
    var_names: Optional[list] = None,
    alpha: float = 0.05,
    warn: bool = True
) -> dict:
    """
    Check normality for multiple samples using Shapiro-Wilk test.

    Parameters
    ----------
    *samples : arrays
        Samples to check
    var_names : list of str, optional
        Names for each sample
    alpha : float, default 0.05
        Significance level
    warn : bool, default True
        Whether to log warnings for non-normal data

    Returns
    -------
    dict
        Dictionary with results for each sample:
        - 'all_normal': bool, True if all samples are normal
        - 'results': list of individual test results
        - 'recommendation': str, overall recommendation

    Examples
    --------
    >>> x = np.random.normal(0, 1, 50)
    >>> y = np.random.exponential(2, 50)
    >>> check = check_normality(x, y, var_names=['Normal', 'Exponential'])
    >>> check['all_normal']
    False
    >>> check['recommendation']
    'Some samples deviate from normality. Consider non-parametric tests.'
    """
    if var_names is None:
        var_names = [f'sample_{i}' for i in range(len(samples))]

    if len(var_names) != len(samples):
        raise ValueError("Number of var_names must match number of samples")

    results = []
    for sample, var_name in zip(samples, var_names):
        result = test_shapiro(sample, var_x=var_name, alpha=alpha, return_as='dict')
        results.append(result)

        if warn and not result['normal']:
            logger.warning(
                f"{var_name}: Data deviate from normality "
                f"(W={result['statistic']:.4f}, p={result['pvalue']:.4f})"
            )

    all_normal = all(r['normal'] for r in results)

    if all_normal:
        recommendation = "All samples appear normal. Parametric tests are appropriate."
    else:
        non_normal = [r['var_x'] for r in results if not r['normal']]
        recommendation = (
            f"Samples {', '.join(non_normal)} deviate from normality. "
            "Consider non-parametric tests (Brunner-Munzel, Wilcoxon, Kruskal-Wallis)."
        )

    return {
        'all_normal': all_normal,
        'results': results,
        'recommendation': recommendation
    }


"""Main function"""
def main(args):
    """Demonstrate Shapiro-Wilk test functionality."""
    logger.info("Demonstrating Shapiro-Wilk normality test")

    # Set random seed
    np.random.seed(42)

    # Example 1: Normal data
    logger.info("\n=== Example 1: Normal data ===")

    x_normal = np.random.normal(0, 1, 100)
    result_normal = test_shapiro(x_normal, var_x='Normal', verbose=True)

    # Example 2: Non-normal data (exponential)
    logger.info("\n=== Example 2: Non-normal data (exponential) ===")

    x_exp = np.random.exponential(2, 100)
    result_exp = test_shapiro(x_exp, var_x='Exponential', verbose=True)

    # Example 3: With Q-Q plot
    logger.info("\n=== Example 3: Visual assessment with Q-Q plot ===")

    x_mixed = np.concatenate([
        np.random.normal(0, 1, 90),
        np.random.normal(5, 1, 10)  # Outliers
    ])

    result_mixed = test_shapiro(x_mixed, var_x='Mixed Distribution', plot=True, verbose=True)
    stx.io.save(plt.gcf(), './shapiro_example3.jpg')
    plt.close()

    # Example 4: Multiple samples check
    logger.info("\n=== Example 4: Check multiple samples ===")

    x1 = np.random.normal(0, 1, 50)
    x2 = np.random.exponential(2, 50)
    x3 = np.random.normal(0, 1, 50)

    check_result = test_normality(
        x1, x2, x3,
        var_names=['Sample A', 'Sample B', 'Sample C'],
        warn=True
    )

    logger.info(f"All normal: {check_result['all_normal']}")
    logger.info(f"Recommendation: {check_result['recommendation']}")

    # Example 5: Different distributions comparison
    logger.info("\n=== Example 5: Distribution comparison ===")

    distributions = {
        'Normal': np.random.normal(0, 1, 100),
        'Exponential': np.random.exponential(2, 100),
        'Uniform': np.random.uniform(-3, 3, 100),
        'Gamma': np.random.gamma(2, 2, 100),
        't-dist (df=3)': np.random.standard_t(3, 100),
    }

    results_comp = []
    for name, data in distributions.items():
        result = test_shapiro(data, var_x=name, verbose=True)
        results_comp.append(result)

    # Example 6: Export results
    logger.info("\n=== Example 6: Export results ===")

    from ...utils._normalizers import export_summary

    export_summary(
        results_comp,
        './shapiro_results.csv',
        columns=['var_x', 'statistic', 'pvalue', 'stars', 'normal', 'recommendation']
    )
    logger.info("Results exported to ./shapiro_results.csv")

    return 0


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Demonstrate Shapiro-Wilk normality test'
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
