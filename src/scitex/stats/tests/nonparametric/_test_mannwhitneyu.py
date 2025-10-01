#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-01 17:45:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/stats/tests/nonparametric/_test_mannwhitneyu.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/stats/tests/nonparametric/_test_mannwhitneyu.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------


"""
Functionalities:
  - Perform Mann-Whitney U test (Wilcoxon rank-sum test)
  - Non-parametric test for comparing two independent samples
  - Compute rank-biserial correlation effect size
  - Generate visualizations with rank distributions
  - Support flexible output formats (dict or DataFrame)

Dependencies:
  - packages: numpy, pandas, scipy, matplotlib

IO:
  - input: Two independent samples (arrays or Series)
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
def test_mannwhitneyu(
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
    Perform Mann-Whitney U test (Wilcoxon rank-sum test).

    Parameters
    ----------
    x, y : arrays or Series
        Two independent samples to compare
    var_x, var_y : str
        Labels for samples
    alternative : {'two-sided', 'less', 'greater'}, default 'two-sided'
        Alternative hypothesis
    alpha : float, default 0.05
        Significance level
    plot : bool, default False
        Whether to generate visualization
    return_as : {'dict', 'dataframe'}, default 'dict'
        Output format
    decimals : int, default 3
        Number of decimal places for rounding

    Returns
    -------
    results : dict or DataFrame
        Test results including:
        - test_method: 'Mann-Whitney U test'
        - statistic_name: 'U'
        - statistic: U-statistic value
        - pvalue: p-value
        - pstars: Significance stars
        - rejected: Whether null hypothesis is rejected
        - effect_size: Rank-biserial correlation
        - effect_size_metric: 'rank-biserial correlation'
        - effect_size_interpretation: Interpretation
        - n_x, n_y: Sample sizes
        - var_x, var_y: Variable labels
        - H0: Null hypothesis description
    fig : matplotlib.figure.Figure, optional
        Figure with visualizations (only if plot=True)

    Notes
    -----
    The Mann-Whitney U test (also known as Wilcoxon rank-sum test) is a
    non-parametric test for comparing two independent samples.

    **Null Hypothesis (H0)**: The two samples come from distributions with
    equal medians (more precisely: P(X > Y) = 0.5)

    **Test Statistic U**:

    .. math::
        U = n_1 n_2 + \\frac{n_1(n_1+1)}{2} - R_1

    Where:
    - n_1, n_2: Sample sizes
    - R_1: Sum of ranks for sample 1

    **Effect Size (Rank-biserial correlation)**:

    .. math::
        r = 1 - \\frac{2U}{n_1 n_2}

    Or equivalently:

    .. math::
        r = \\frac{2(\\bar{R}_1 - \\bar{R}_2)}{n_1 + n_2}

    Interpretation:
    - |r| < 0.1:  negligible
    - |r| < 0.3:  small
    - |r| < 0.5:  medium
    - |r| ≥ 0.5:  large

    **Advantages**:
    - No normality assumption required
    - Robust to outliers
    - Works with ordinal data
    - More powerful than t-test for non-normal data

    **When to use**:
    - Comparing two independent groups
    - Data violate normality
    - Presence of outliers
    - Ordinal data (e.g., Likert scales)
    - Small sample sizes

    **Comparison with other tests**:
    - vs t-test: More robust, less powerful when assumptions met
    - vs Brunner-Munzel: MWU assumes identical shape, BM does not
    - vs KS test: MWU tests location, KS tests entire distribution

    **Note on relationship to Brunner-Munzel**:
    Mann-Whitney U assumes samples have the same distribution shape
    (differing only in location). For more robust analysis without this
    assumption, use test_brunner_munzel() instead.

    References
    ----------
    .. [1] Mann, H. B., & Whitney, D. R. (1947). "On a test of whether one
           of two random variables is stochastically larger than the other".
           Annals of Mathematical Statistics, 18(1), 50-60.
    .. [2] Kerby, D. S. (2014). "The simple difference formula: An approach
           to teaching nonparametric correlation". Comprehensive Psychology, 3, 11.

    Examples
    --------
    >>> # Two samples with different medians
    >>> x = np.array([1, 2, 3, 4, 5])
    >>> y = np.array([3, 4, 5, 6, 7])
    >>> result = test_mannwhitneyu(x, y)
    >>> result['rejected']
    True

    >>> # With visualization
    >>> result, fig = test_mannwhitneyu(x, y, plot=True)
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

    # Perform Mann-Whitney U test
    u_result = stats.mannwhitneyu(x, y, alternative=alternative)
    u_stat = float(u_result.statistic)
    pvalue = float(u_result.pvalue)

    # Determine rejection
    rejected = pvalue < alpha

    # Compute rank-biserial correlation effect size
    # Formula: r = 1 - (2U) / (n1 * n2)
    r = 1 - (2 * u_stat) / (n_x * n_y)

    # Interpret effect size
    r_abs = abs(r)
    if r_abs < 0.1:
        effect_interp = 'negligible'
    elif r_abs < 0.3:
        effect_interp = 'small'
    elif r_abs < 0.5:
        effect_interp = 'medium'
    else:
        effect_interp = 'large'

    # Compile results
    result = {
        'test_method': 'Mann-Whitney U test',
        'statistic_name': 'U',
        'statistic': round(u_stat, decimals),
        'n_x': n_x,
        'n_y': n_y,
        'var_x': var_x,
        'var_y': var_y,
        'pvalue': round(pvalue, decimals),
        'pstars': p2stars(pvalue),
        'alpha': alpha,
        'rejected': rejected,
        'effect_size': round(r, decimals),
        'effect_size_metric': 'rank-biserial correlation',
        'effect_size_interpretation': effect_interp,
        'H0': f'Distributions of {var_x} and {var_y} have equal medians',
    }

    # Add recommendation
    if rejected:
        result['recommendation'] = f"{var_x} and {var_y} have significantly different medians."
    else:
        result['recommendation'] = "No significant difference in medians detected."

    # Generate plot if requested
    fig = None
    if plot:
        fig = _plot_mannwhitneyu(x, y, var_x, var_y, result)

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


def _plot_mannwhitneyu(x, y, var_x, var_y, result):
    """Create visualization for Mann-Whitney U test."""
    fig, axes = stx.plt.subplots(2, 2, figsize=(14, 10))

    # Plot 1: Box plots with individual points
    ax = axes[0, 0]

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

    # Add jittered points
    np.random.seed(42)
    for i, vals in enumerate(box_data):
        y_vals = vals
        x_vals = np.random.normal(positions[i], 0.04, size=len(vals))
        ax.scatter(x_vals, y_vals, alpha=0.5, s=30)

    # Add significance annotation
    y_max = max(np.max(x), np.max(y))
    y_min = min(np.min(x), np.min(y))
    y_range = y_max - y_min
    sig_y = y_max + y_range * 0.05

    ax.plot([0, 1], [sig_y, sig_y], 'k-', linewidth=1.5)
    ax.text(
        0.5, sig_y + y_range * 0.02,
        result['pstars'],
        ha='center', va='bottom',
        fontsize=14, fontweight='bold'
    )

    ax.set_xticks(positions)
    ax.set_xticklabels([var_x, var_y])
    ax.set_ylabel('Value')
    ax.set_title(f'Mann-Whitney U Test\nU = {result["statistic"]:.1f}, p = {result["pvalue"]:.4f}')
    ax.grid(True, alpha=0.3, axis='y')

    # Plot 2: Histograms
    ax = axes[0, 1]

    bins = np.histogram_bin_edges(np.concatenate([x, y]), bins='auto')
    ax.hist(x, bins=bins, alpha=0.5, label=var_x, density=True, edgecolor='black')
    ax.hist(y, bins=bins, alpha=0.5, label=var_y, density=True, edgecolor='black')

    # Add median lines
    ax.axvline(np.median(x), color='blue', linestyle='--', linewidth=2, alpha=0.7,
               label=f'{var_x} median')
    ax.axvline(np.median(y), color='red', linestyle='--', linewidth=2, alpha=0.7,
               label=f'{var_y} median')

    ax.set_xlabel('Value')
    ax.set_ylabel('Density')
    ax.set_title('Distribution Comparison')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Plot 3: Rank distribution
    ax = axes[1, 0]

    # Combine data and compute ranks
    combined = np.concatenate([x, y])
    ranks = stats.rankdata(combined)

    n_x = len(x)
    ranks_x = ranks[:n_x]
    ranks_y = ranks[n_x:]

    # Plot rank distributions
    ax.hist(ranks_x, bins=20, alpha=0.5, label=f'{var_x} ranks', edgecolor='black')
    ax.hist(ranks_y, bins=20, alpha=0.5, label=f'{var_y} ranks', edgecolor='black')

    # Add mean rank lines
    ax.axvline(np.mean(ranks_x), color='blue', linestyle='--', linewidth=2,
               label=f'{var_x} mean rank: {np.mean(ranks_x):.1f}')
    ax.axvline(np.mean(ranks_y), color='red', linestyle='--', linewidth=2,
               label=f'{var_y} mean rank: {np.mean(ranks_y):.1f}')

    ax.set_xlabel('Rank')
    ax.set_ylabel('Frequency')
    ax.set_title('Rank Distribution')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # Plot 4: Cumulative distribution
    ax = axes[1, 1]

    x_sorted = np.sort(x)
    y_sorted = np.sort(y)

    ecdf_x = np.arange(1, len(x) + 1) / len(x)
    ecdf_y = np.arange(1, len(y) + 1) / len(y)

    ax.step(x_sorted, ecdf_x, where='post', linewidth=2, label=var_x, color='blue')
    ax.step(y_sorted, ecdf_y, where='post', linewidth=2, label=var_y, color='red')

    ax.set_xlabel('Value')
    ax.set_ylabel('Cumulative Probability')
    ax.set_title('Empirical CDF Comparison')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Add text with results
    text_str = (
        f"U = {result['statistic']:.1f}\n"
        f"p = {result['pvalue']:.4f} {result['pstars']}\n"
        f"r = {result['effect_size']:.3f} ({result['effect_size_interpretation']})\n"
        f"n₁ = {result['n_x']}, n₂ = {result['n_y']}"
    )
    ax.text(
        0.98, 0.02, text_str,
        transform=ax.transAxes,
        verticalalignment='bottom',
        horizontalalignment='right',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
        fontsize=9
    )

    plt.tight_layout()
    return fig


"""Main function"""
def main(args):
    """Demonstrate Mann-Whitney U test functionality."""
    logger.info("Demonstrating Mann-Whitney U test")

    # Set random seed
    np.random.seed(42)

    # Example 1: Basic usage
    logger.info("\n=== Example 1: Basic usage ===")

    x1 = np.random.normal(5, 1, 30)
    y1 = np.random.normal(6, 1, 30)

    result1 = test_mannwhitneyu(x1, y1, var_x='Group A', var_y='Group B')

    logger.info(f"U = {result1['statistic']:.1f}")
    logger.info(f"p = {result1['pvalue']:.4f} {result1['pstars']}")
    logger.info(f"r = {result1['effect_size']:.3f} ({result1['effect_size_interpretation']})")
    logger.info(f"Recommendation: {result1['recommendation']}")

    # Example 2: Non-normal data
    logger.info("\n=== Example 2: Non-normal (skewed) data ===")

    x2 = np.random.exponential(2, 40)
    y2 = np.random.exponential(3, 40)

    result2 = test_mannwhitneyu(x2, y2, var_x='Exp(λ=0.5)', var_y='Exp(λ=0.33)')

    logger.info(f"U = {result2['statistic']:.1f}")
    logger.info(f"p = {result2['pvalue']:.4f} {result2['pstars']}")
    logger.info(f"r = {result2['effect_size']:.3f}")

    # Example 3: With outliers
    logger.info("\n=== Example 3: Data with outliers ===")

    x3 = np.concatenate([np.random.normal(0, 1, 35), [10, 12]])
    y3 = np.random.normal(0.5, 1, 40)

    result3 = test_mannwhitneyu(x3, y3, var_x='With Outliers', var_y='Normal')

    logger.info(f"U = {result3['statistic']:.1f}, p = {result3['pvalue']:.4f}")
    logger.info("Mann-Whitney U is robust to outliers")

    # Example 4: Ordinal data (Likert scale)
    logger.info("\n=== Example 4: Ordinal data (Likert scale) ===")

    likert1 = np.random.choice([1, 2, 3, 4, 5], size=50, p=[0.05, 0.15, 0.40, 0.30, 0.10])
    likert2 = np.random.choice([1, 2, 3, 4, 5], size=50, p=[0.05, 0.10, 0.25, 0.35, 0.25])

    result4 = test_mannwhitneyu(likert1, likert2, var_x='Condition A', var_y='Condition B')

    logger.info(f"U = {result4['statistic']:.1f}")
    logger.info(f"p = {result4['pvalue']:.4f} {result4['pstars']}")
    logger.info(f"Medians: {np.median(likert1):.1f} vs {np.median(likert2):.1f}")

    # Example 5: One-sided tests
    logger.info("\n=== Example 5: One-sided tests ===")

    x5 = np.random.normal(5, 1, 40)
    y5 = np.random.normal(6, 1, 40)

    result_two = test_mannwhitneyu(x5, y5, alternative='two-sided')
    result_less = test_mannwhitneyu(x5, y5, alternative='less')

    logger.info(f"Two-sided: p = {result_two['pvalue']:.4f} {result_two['pstars']}")
    logger.info(f"One-sided (less): p = {result_less['pvalue']:.4f} {result_less['pstars']}")

    # Example 6: With visualization
    logger.info("\n=== Example 6: Complete analysis with visualization ===")

    x6 = np.random.gamma(2, 2, 50)
    y6 = np.random.gamma(3, 2, 50)

    result6, fig6 = test_mannwhitneyu(
        x6, y6,
        var_x='Gamma(k=2)',
        var_y='Gamma(k=3)',
        plot=True
    )

    logger.info(f"U = {result6['statistic']:.1f}, p = {result6['pvalue']:.4f}")
    stx.io.save(fig6, './mannwhitneyu_demo.png')
    logger.info("Visualization saved")

    # Example 7: Comparison with t-test
    logger.info("\n=== Example 7: Mann-Whitney U vs t-test ===")

    from ..parametric._test_ttest import test_ttest_ind

    # Normal data - both tests should agree
    x_norm = np.random.normal(5, 1, 50)
    y_norm = np.random.normal(5.5, 1, 50)

    mwu_result = test_mannwhitneyu(x_norm, y_norm)
    ttest_result = test_ttest_ind(x_norm, y_norm)

    logger.info(f"Mann-Whitney U: p = {mwu_result['pvalue']:.4f}")
    logger.info(f"t-test:         p = {ttest_result['pvalue']:.4f}")

    # Non-normal data - MWU more appropriate
    x_exp = np.random.exponential(2, 50)
    y_exp = np.random.exponential(2.5, 50)

    mwu_result2 = test_mannwhitneyu(x_exp, y_exp)
    ttest_result2 = test_ttest_ind(x_exp, y_exp)

    logger.info(f"\nFor exponential data:")
    logger.info(f"Mann-Whitney U: p = {mwu_result2['pvalue']:.4f}")
    logger.info(f"t-test:         p = {ttest_result2['pvalue']:.4f}")
    logger.info("Mann-Whitney U is more reliable for non-normal data")

    # Example 8: Comparison with Brunner-Munzel
    logger.info("\n=== Example 8: Mann-Whitney U vs Brunner-Munzel ===")

    from ._test_brunner_munzel import test_brunner_munzel

    # Same shape distributions
    x8 = np.random.normal(5, 1, 50)
    y8 = np.random.normal(6, 1, 50)

    mwu = test_mannwhitneyu(x8, y8)
    bm = test_brunner_munzel(x8, y8)

    logger.info("Same distribution shape:")
    logger.info(f"  Mann-Whitney U: p = {mwu['pvalue']:.4f}, r = {mwu['effect_size']:.3f}")
    logger.info(f"  Brunner-Munzel: p = {bm['pvalue']:.4f}, P(X>Y) = {bm['effect_size']:.3f}")

    # Different shapes
    x9 = np.random.normal(5, 1, 50)
    y9 = np.random.normal(6, 3, 50)  # Different variance

    mwu2 = test_mannwhitneyu(x9, y9)
    bm2 = test_brunner_munzel(x9, y9)

    logger.info("\nDifferent distribution shapes:")
    logger.info(f"  Mann-Whitney U: p = {mwu2['pvalue']:.4f}")
    logger.info(f"  Brunner-Munzel: p = {bm2['pvalue']:.4f}")
    logger.info("  Note: Brunner-Munzel is more appropriate for different shapes")

    # Example 9: Export results
    logger.info("\n=== Example 9: Export results ===")

    from ...utils._normalizers import convert_results, force_dataframe

    test_results = [result1, result2, result3, result4, result6]

    df = force_dataframe(test_results)
    logger.info(f"\nDataFrame shape: {df.shape}")

    convert_results(test_results, return_as='excel', path='./mannwhitneyu_tests.xlsx')
    logger.info("Results exported to Excel")

    convert_results(test_results, return_as='csv', path='./mannwhitneyu_tests.csv')
    logger.info("Results exported to CSV")

    return 0


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Demonstrate Mann-Whitney U test'
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
