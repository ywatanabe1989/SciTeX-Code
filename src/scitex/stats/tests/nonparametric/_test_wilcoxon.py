#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-01 15:45:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/stats/tests/nonparametric/_test_wilcoxon.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/stats/tests/nonparametric/_test_wilcoxon.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------


"""
Functionalities:
  - Perform Wilcoxon signed-rank test (non-parametric paired test)
  - Compute rank-biserial correlation effect size
  - Generate visualizations
  - Support flexible output formats (dict or DataFrame)

Dependencies:
  - packages: numpy, pandas, scipy, matplotlib

IO:
  - input: Two paired samples (arrays or Series)
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
def test_wilcoxon(
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
    Perform Wilcoxon signed-rank test (non-parametric paired test).

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
        - 'two-sided': distributions differ
        - 'greater': x tends to be greater than y
        - 'less': x tends to be less than y
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
        - test_method: 'Wilcoxon signed-rank test'
        - statistic_name: 'W'
        - statistic: W-statistic (sum of signed ranks)
        - pvalue: p-value
        - effect_size: rank-biserial correlation
        - effect_size_metric: 'rank-biserial correlation'
        - n_pairs: number of pairs (excluding zeros)
        - n_zeros: number of zero differences (ties)
    fig : matplotlib.figure.Figure, optional
        Figure object (only if plot=True)

    Notes
    -----
    The Wilcoxon signed-rank test is the non-parametric alternative to
    the paired t-test. It tests whether the median of differences is zero.

    **When to use:**
    - Paired samples (before-after, matched pairs)
    - Data are not normally distributed
    - Ordinal data or continuous data with outliers
    - Robust alternative to paired t-test

    **Assumptions:**
    - Paired observations
    - Differences are symmetric around the median
    - Ordinal or continuous data

    **How it works:**
    1. Compute differences: d = x - y
    2. Remove zero differences
    3. Rank absolute differences
    4. Sum ranks of positive differences (W+)
    5. Sum ranks of negative differences (W-)
    6. Test statistic: W = min(W+, W-)

    **Effect size** (rank-biserial correlation):

    .. math::
        r = \\frac{W_+ - W_-}{n(n+1)/2}

    Ranges from -1 to 1:
    - r close to 1: x > y (large positive effect)
    - r close to 0: no difference
    - r close to -1: x < y (large negative effect)

    Interpretation:
    - |r| < 0.1: negligible
    - |r| < 0.3: small
    - |r| < 0.5: medium
    - |r| ≥ 0.5: large

    References
    ----------
    .. [1] Wilcoxon, F. (1945). "Individual comparisons by ranking methods".
           Biometrics Bulletin, 1(6), 80-83.
    .. [2] Kerby, D. S. (2014). "The simple difference formula: An approach to
           teaching nonparametric correlation". Comprehensive Psychology, 3, 11.

    Examples
    --------
    >>> before = np.array([10, 12, 15, 18, 20])
    >>> after = np.array([12, 14, 17, 20, 22])
    >>> result = test_wilcoxon(before, after)
    >>> result['pvalue']
    0.062...

    >>> # With visualization
    >>> result, fig = test_wilcoxon(before, after, plot=True)
    """
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
        raise ValueError(f"Paired samples must have same length: {len(x)} vs {len(y)}")

    # Compute differences
    diff = x - y

    # Count zeros (ties)
    n_zeros = np.sum(diff == 0)

    # Perform Wilcoxon signed-rank test
    w_result = stats.wilcoxon(x, y, alternative=alternative, zero_method='wilcox')
    w_stat = float(w_result.statistic)
    pvalue = float(w_result.pvalue)

    # Compute rank-biserial correlation (effect size)
    # Remove zeros for ranking
    diff_nonzero = diff[diff != 0]
    n_nonzero = len(diff_nonzero)

    if n_nonzero > 0:
        # Rank absolute differences
        abs_diff = np.abs(diff_nonzero)
        ranks = stats.rankdata(abs_diff)

        # Sum of ranks for positive and negative differences
        w_plus = np.sum(ranks[diff_nonzero > 0])
        w_minus = np.sum(ranks[diff_nonzero < 0])

        # Rank-biserial correlation
        max_sum = n_nonzero * (n_nonzero + 1) / 2
        r = (w_plus - w_minus) / max_sum
        effect_size = float(r)
    else:
        effect_size = 0.0

    # Interpret effect size
    effect_size_abs = abs(effect_size)
    if effect_size_abs < 0.1:
        effect_size_interpretation = 'negligible'
    elif effect_size_abs < 0.3:
        effect_size_interpretation = 'small'
    elif effect_size_abs < 0.5:
        effect_size_interpretation = 'medium'
    else:
        effect_size_interpretation = 'large'

    # Create null hypothesis description
    if alternative == 'two-sided':
        H0 = f"median({var_x} - {var_y}) = 0"
    elif alternative == 'greater':
        H0 = f"median({var_x} - {var_y}) ≤ 0"
    else:  # less
        H0 = f"median({var_x} - {var_y}) ≥ 0"

    # Compile results
    result = {
        'test_method': 'Wilcoxon signed-rank test',
        'statistic_name': 'W',
        'statistic': w_stat,
        'alternative': alternative,
        'n_pairs': n_nonzero,
        'n_zeros': n_zeros,
        'var_x': var_x,
        'var_y': var_y,
        'pvalue': pvalue,
        'pstars': p2stars(pvalue),
        'alpha': alpha,
        'rejected': pvalue < alpha,
        'effect_size': effect_size,
        'effect_size_metric': 'rank-biserial correlation',
        'effect_size_interpretation': effect_size_interpretation,
        'H0': H0,
    }

    # Generate plot if requested
    fig = None
    if plot:
        fig = _plot_wilcoxon(x, y, var_x, var_y, result)

    # Convert to requested format
    if return_as == 'dataframe':
        result = force_dataframe(result)

    # Return based on plot option
    if plot:
        return result, fig
    else:
        return result


def _plot_wilcoxon(x, y, var_x, var_y, result):
    """Create visualization for Wilcoxon test."""
    fig, axes = stx.plt.subplots(1, 2, figsize=(12, 5))

    # Compute differences
    diff = x - y

    # Plot 1: Before-after plot
    ax = axes[0]

    # Plot paired lines
    for i in range(len(x)):
        color = 'green' if x[i] > y[i] else 'red' if x[i] < y[i] else 'gray'
        ax.plot([0, 1], [x[i], y[i]], 'o-', color=color, alpha=0.4)

    # Plot medians
    ax.plot([0], [np.median(x)], 'bo', markersize=15, label=f'{var_x} (median)')
    ax.plot([1], [np.median(y)], 'ro', markersize=15, label=f'{var_y} (median)')

    ax.set_xticks([0, 1])
    ax.set_xticklabels([var_x, var_y])
    ax.set_ylabel('Value')
    ax.set_title(f'Paired Measurements {result["pstars"]}')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')

    # Plot 2: Ranked differences
    ax = axes[1]

    # Remove zeros
    diff_nonzero = diff[diff != 0]

    if len(diff_nonzero) > 0:
        # Rank absolute differences
        abs_diff = np.abs(diff_nonzero)
        ranks = stats.rankdata(abs_diff)

        # Separate positive and negative
        pos_ranks = ranks[diff_nonzero > 0]
        neg_ranks = ranks[diff_nonzero < 0]

        # Bar plot of ranks
        if len(pos_ranks) > 0:
            ax.barh(np.arange(len(pos_ranks)), pos_ranks, color='green', alpha=0.6, label='Positive ranks')
        if len(neg_ranks) > 0:
            ax.barh(np.arange(len(pos_ranks), len(pos_ranks) + len(neg_ranks)), neg_ranks,
                   color='red', alpha=0.6, label='Negative ranks')

        ax.set_xlabel('Rank')
        ax.set_ylabel('Pair Index')
        ax.set_title(
            f"W = {result['statistic']:.0f}, "
            f"p = {result['pvalue']:.4f}\n"
            f"r = {result['effect_size']:.2f} ({result['effect_size_interpretation']})"
        )
        ax.legend()
        ax.grid(True, alpha=0.3, axis='x')
    else:
        ax.text(0.5, 0.5, 'All differences are zero',
                ha='center', va='center', transform=ax.transAxes)

    plt.tight_layout()

    return fig


"""Main function"""
def main(args):
    """Demonstrate Wilcoxon signed-rank test functionality."""
    logger.info("Demonstrating Wilcoxon signed-rank test")

    # Set random seed
    np.random.seed(42)

    # Example 1: Normal data (compare with paired t-test)
    logger.info("\n=== Example 1: Normal data ===")

    before1 = np.random.normal(10, 2, 30)
    after1 = before1 + np.random.normal(2, 1, 30)

    result1 = test_wilcoxon(before1, after1, var_x='Before', var_y='After')

    logger.info(f"W = {result1['statistic']:.0f}")
    logger.info(f"p = {result1['pvalue']:.4f} {result1['pstars']}")
    logger.info(f"Effect size (r) = {result1['effect_size']:.3f} ({result1['effect_size_interpretation']})")

    # Example 2: Skewed data
    logger.info("\n=== Example 2: Skewed data ===")

    before2 = np.random.exponential(2, 30)
    after2 = before2 + np.random.exponential(1, 30)

    result2 = test_wilcoxon(before2, after2)

    logger.info(f"W = {result2['statistic']:.0f}")
    logger.info(f"p = {result2['pvalue']:.4f} {result2['pstars']}")
    logger.info(f"Effect size (r) = {result2['effect_size']:.3f}")

    # Example 3: Data with outliers
    logger.info("\n=== Example 3: Data with outliers ===")

    before3 = np.concatenate([np.random.normal(10, 1, 28), [20, 25]])  # Add outliers
    after3 = np.concatenate([np.random.normal(12, 1, 28), [22, 27]])

    result3 = test_wilcoxon(before3, after3, var_x='Pre', var_y='Post')

    logger.info(f"W = {result3['statistic']:.0f}")
    logger.info(f"p = {result3['pvalue']:.4f} {result3['pstars']}")
    logger.info("Wilcoxon is robust to outliers")

    # Example 4: Small effect
    logger.info("\n=== Example 4: Small effect (borderline) ===")

    before4 = np.random.normal(10, 2, 25)
    after4 = before4 + np.random.normal(0.3, 1, 25)  # Small change

    result4 = test_wilcoxon(before4, after4)

    logger.info(f"W = {result4['statistic']:.0f}")
    logger.info(f"p = {result4['pvalue']:.4f} {result4['pstars']}")
    logger.info(f"Effect size (r) = {result4['effect_size']:.3f}")

    # Example 5: One-sided test
    logger.info("\n=== Example 5: One-sided test ===")

    before5 = np.random.normal(10, 2, 30)
    after5 = before5 + np.random.normal(1.5, 1, 30)

    result_two = test_wilcoxon(before5, after5, alternative='two-sided')
    result_less = test_wilcoxon(before5, after5, alternative='less')

    logger.info(f"Two-sided: p = {result_two['pvalue']:.4f} {result_two['pstars']}")
    logger.info(f"One-sided (less): p = {result_less['pvalue']:.4f} {result_less['pstars']}")

    # Example 6: With visualization
    logger.info("\n=== Example 6: With visualization ===")

    before6 = np.random.lognormal(2, 0.5, 40)
    after6 = before6 * np.random.lognormal(0.15, 0.3, 40)

    result6, fig6 = test_wilcoxon(
        before6, after6,
        var_x='Baseline',
        var_y='Treatment',
        plot=True
    )

    stx.io.save(fig6, './wilcoxon_test_demo.png')
    logger.info("Visualization saved")

    # Example 7: Compare with paired t-test
    logger.info("\n=== Example 7: Wilcoxon vs Paired t-test ===")

    # For normal data
    normal_before = np.random.normal(10, 2, 50)
    normal_after = normal_before + np.random.normal(1, 1.5, 50)

    from ..parametric._test_ttest import test_ttest_rel

    result_wilcox = test_wilcoxon(normal_before, normal_after)
    result_ttest = test_ttest_rel(normal_before, normal_after)

    logger.info(f"Wilcoxon: p = {result_wilcox['pvalue']:.4f} {result_wilcox['pstars']}, r = {result_wilcox['effect_size']:.3f}")
    logger.info(f"Paired t-test: p = {result_ttest['pvalue']:.4f} {result_ttest['pstars']}, d = {result_ttest['effect_size']:.3f}")
    logger.info("For normal data, both tests should agree")

    # Example 8: Export results
    logger.info("\n=== Example 8: Multiple comparisons ===")

    from ...utils._normalizers import combine_results, export_summary

    results_list = []
    for i in range(5):
        before = np.random.exponential(2, 30)
        after = before + np.random.exponential(0.5, 30)
        result = test_wilcoxon(
            before, after,
            var_x=f'Pre_{i}',
            var_y=f'Post_{i}'
        )
        results_list.append(result)

    df_all = combine_results(results_list)
    logger.info(f"\n{df_all[['var_x', 'var_y', 'pvalue', 'pstars', 'effect_size']]}")

    export_summary(df_all, './wilcoxon_results.csv')
    logger.info("Results exported")

    return 0


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Demonstrate Wilcoxon signed-rank test'
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
