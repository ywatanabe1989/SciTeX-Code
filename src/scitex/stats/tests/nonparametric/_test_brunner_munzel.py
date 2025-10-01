#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-01 13:37:32 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/stats/tests/nonparametric/_test_brunner_munzel.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/stats/tests/nonparametric/_test_brunner_munzel.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
  - Perform Brunner-Munzel test (non-parametric alternative to t-test)
  - Compute both P(X>Y) and Cliff's delta effect sizes
  - Generate visualizations with significance indicators
  - Support flexible output formats (dict or DataFrame)

Dependencies:
  - packages: numpy, pandas, scipy, matplotlib

IO:
  - input: Two samples (arrays or Series)
  - output: Test results (dict or DataFrame) and optional figure
"""

"""Imports"""
import argparse
from typing import Literal, Tuple, Union

import matplotlib
import numpy as np
import pandas as pd
import scitex as stx
from scipy import stats
from scitex.logging import getLogger

logger = getLogger(__name__)

"""Functions"""


def test_brunner_munzel(
    x: Union[np.ndarray, pd.Series],
    y: Union[np.ndarray, pd.Series],
    var_x: str = "x",
    var_y: str = "y",
    alternative: Literal["two-sided", "greater", "less"] = "two-sided",
    alpha: float = 0.05,
    plot: bool = False,
    return_as: Literal["dict", "dataframe"] = "dict",
) -> Union[
    dict,
    pd.DataFrame,
    Tuple[dict, "matplotlib.figure.Figure"],
    Tuple[pd.DataFrame, "matplotlib.figure.Figure"],
]:
    """
    Perform Brunner-Munzel test (non-parametric).

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
        - test_method: 'Brunner-Munzel test'
        - statistic_name: 'W'
        - statistic: W-statistic value
        - pvalue: p-value
        - pstars: Significance stars
        - rejected: Whether null hypothesis is rejected
        - effect_size: P(X > Y) (primary effect size)
        - effect_size_metric: 'P(X>Y)'
        - effect_size_interpretation: Interpretation of P(X>Y)
        - effect_size_secondary: Cliff's delta (secondary effect size)
        - effect_size_secondary_metric: "Cliff's delta"
        - effect_size_secondary_interpretation: Interpretation of delta
        - n_x, n_y: Sample sizes
        - var_x, var_y: Variable labels
        - H0: Null hypothesis description
    fig : matplotlib.figure.Figure, optional
        Figure object (only if plot=True)

    Notes
    -----
    The Brunner-Munzel test is a non-parametric test for comparing two independent
    samples. It is more robust than the t-test when:
    - Distributions are non-normal
    - Variances are unequal
    - Sample sizes differ
    - Data contain outliers

    Unlike Mann-Whitney U test, Brunner-Munzel does not assume equal variances
    and provides better control of Type I error rate.

    The test statistic W is approximately t-distributed:

    .. math::
        W = \\frac{\\hat{p} - 0.5}{\\sqrt{\\hat{\\sigma}^2}}

    where :math:`\\hat{p}` is an estimate of P(X > Y).

    **Effect Sizes:**

    1. **P(X > Y)**: Probability that a random value from X exceeds a random
       value from Y. Interpretation:
       - 0.50: No effect (chance)
       - 0.56: Small effect
       - 0.64: Medium effect
       - 0.71: Large effect

    2. **Cliff's delta (δ)**: Ranges from -1 to 1, related to P(X>Y) by:
       δ = 2×P(X>Y) - 1. Interpretation:
       - |δ| < 0.147: Negligible
       - |δ| < 0.33: Small
       - |δ| < 0.474: Medium
       - |δ| ≥ 0.474: Large

    References
    ----------
    .. [1] Brunner, E., & Munzel, U. (2000). "The nonparametric Behrens-Fisher
           problem: Asymptotic theory and a small-sample approximation".
           Biometrical Journal, 42(1), 17-25.
    .. [2] Neubert, K., & Brunner, E. (2007). "A studentized permutation test
           for the non-parametric Behrens-Fisher problem". Computational
           Statistics & Data Analysis, 51(10), 5192-5204.

    Examples
    --------
    >>> x = np.array([1, 2, 3, 4, 5])
    >>> y = np.array([2, 3, 4, 5, 6])
    >>> result = test_brunner_munzel(x, y)
    >>> result['pvalue']
    0.109...
    >>> result['effect_size']  # P(X > Y)
    0.2
    >>> result['effect_size_secondary']  # Cliff's delta
    -0.6

    >>> # With visualization
    >>> result, fig = test_brunner_munzel(x, y, plot=True)

    >>> # As DataFrame
    >>> df = test_brunner_munzel(x, y, return_as='dataframe')
    """
    from ...utils._effect_size import (cliffs_delta, interpret_cliffs_delta,
                                       interpret_prob_superiority,
                                       prob_superiority)
    from ...utils._formatters import p2stars
    from ...utils._normalizers import force_dataframe

    # Convert to numpy arrays and remove NaN
    x = np.asarray(x)
    y = np.asarray(y)
    x = x[~np.isnan(x)]
    y = y[~np.isnan(y)]

    n_x = len(x)
    n_y = len(y)

    # Perform Brunner-Munzel test
    bm_result = stats.brunnermunzel(x, y, alternative=alternative)
    w_stat = float(bm_result.statistic)
    pvalue = float(bm_result.pvalue)

    # Compute effect sizes
    prob_xy = prob_superiority(x, y)
    delta = cliffs_delta(x, y)

    # Interpretations
    prob_interp = interpret_prob_superiority(prob_xy)
    delta_interp = interpret_cliffs_delta(delta)

    # Create null hypothesis description
    if alternative == "two-sided":
        H0 = f"P({var_x} > {var_y}) = 0.5"
    elif alternative == "greater":
        H0 = f"P({var_x} > {var_y}) ≤ 0.5"
    else:  # less
        H0 = f"P({var_x} > {var_y}) ≥ 0.5"

    # Compile results
    result = {
        "test_method": "Brunner-Munzel test",
        "statistic_name": "W",
        "statistic": w_stat,
        "alternative": alternative,
        "n_x": n_x,
        "n_y": n_y,
        "var_x": var_x,
        "var_y": var_y,
        "pvalue": pvalue,
        "pstars": p2stars(pvalue),
        "alpha": alpha,
        "rejected": pvalue < alpha,
        "effect_size": prob_xy,
        "effect_size_metric": "P(X>Y)",
        "effect_size_interpretation": prob_interp,
        "effect_size_secondary": delta,
        "effect_size_secondary_metric": "Cliff's delta",
        "effect_size_secondary_interpretation": delta_interp,
        "H0": H0,
    }

    # Generate plot if requested
    fig = None
    if plot:
        fig = _plot_brunner_munzel(x, y, var_x, var_y, result)

    # Convert to requested format
    if return_as == "dataframe":
        result = force_dataframe(result)

    # Return based on plot option
    if plot:
        return result, fig
    else:
        return result


def _plot_brunner_munzel(x, y, var_x, var_y, result):
    """Create visualization for Brunner-Munzel test."""
    fig, axes = stx.plt.subplots(1, 2, figsize=(12, 5))

    # Prepare data
    data_x = pd.DataFrame({"value": x, "group": var_x})
    data_y = pd.DataFrame({"value": y, "group": var_y})
    data = pd.concat([data_x, data_y], ignore_index=True)

    # Plot 1: Histogram + KDE
    ax = axes[0]

    # Histogram
    bins = np.histogram_bin_edges(np.concatenate([x, y]), bins="auto")
    ax.hist(x, bins=bins, alpha=0.5, label=var_x, density=True)
    ax.hist(y, bins=bins, alpha=0.5, label=var_y, density=True)

    # Add median lines
    ax.axvline(
        np.median(x), color="blue", linestyle="--", linewidth=2, alpha=0.7
    )
    ax.axvline(
        np.median(y), color="orange", linestyle="--", linewidth=2, alpha=0.7
    )

    ax.set_xlabel("Value")
    ax.set_ylabel("Density")
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
        showfliers=False,
    )

    # Color boxes
    colors = ["lightblue", "lightcoral"]
    for patch, color in zip(bp["boxes"], colors):
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

    ax.plot([0, 1], [sig_y, sig_y], "k-", linewidth=1.5)
    ax.text(
        0.5,
        sig_y + y_range * 0.02,
        result["pstars"],
        ha="center",
        va="bottom",
        fontsize=14,
        fontweight="bold",
    )

    ax.set_xticks(positions)
    ax.set_xticklabels([var_x, var_y])
    ax.set_ylabel("Value")
    ax.set_title(
        f"W = {result['statistic']:.2f}, "
        f"p = {result['pvalue']:.4f}\n"
        f"P(X>Y) = {result['effect_size']:.2f}, "
        f"δ = {result['effect_size_secondary']:.2f}"
    )
    ax.grid(True, alpha=0.3, axis="y")

    plt.tight_layout()

    return fig


"""Main function"""


def main(args):
    """Demonstrate Brunner-Munzel test functionality."""
    logger.info("Demonstrating Brunner-Munzel test")

    # Set random seed
    np.random.seed(42)

    # Example 1: Normal distributions (compare with t-test)
    logger.info("\n=== Example 1: Normal distributions ===")

    x1 = np.random.normal(0, 1, 50)
    y1 = np.random.normal(0.6, 1, 50)

    result_bm = test_brunner_munzel(x1, y1, var_x="Control", var_y="Treatment")

    logger.info(f"Brunner-Munzel W = {result_bm['statistic']:.3f}")
    logger.info(f"p = {result_bm['pvalue']:.4f} {result_bm['pstars']}")
    logger.info(
        f"P(X > Y) = {result_bm['effect_size']:.3f} ({result_bm['effect_size_interpretation']})"
    )
    logger.info(
        f"Cliff's δ = {result_bm['effect_size_secondary']:.3f} ({result_bm['effect_size_secondary_interpretation']})"
    )

    # Example 2: Non-normal distributions (skewed)
    logger.info("\n=== Example 2: Non-normal (skewed) distributions ===")

    x2 = np.random.gamma(2, 2, 40)  # Right-skewed
    y2 = np.random.gamma(3, 2, 40)  # Right-skewed

    result_skewed = test_brunner_munzel(
        x2, y2, var_x="Group A", var_y="Group B"
    )

    logger.info(f"W = {result_skewed['statistic']:.3f}")
    logger.info(f"p = {result_skewed['pvalue']:.4f} {result_skewed['pstars']}")
    logger.info(f"P(X > Y) = {result_skewed['effect_size']:.3f}")
    logger.info(f"Cliff's δ = {result_skewed['effect_size_secondary']:.3f}")

    # Example 3: With outliers
    logger.info("\n=== Example 3: Data with outliers ===")

    x3 = np.concatenate([np.random.normal(0, 1, 35), [10, 12]])  # Add outliers
    y3 = np.random.normal(0.5, 1, 40)

    result_outlier = test_brunner_munzel(
        x3, y3, var_x="With Outliers", var_y="Normal"
    )

    logger.info(f"W = {result_outlier['statistic']:.3f}")
    logger.info(
        f"p = {result_outlier['pvalue']:.4f} {result_outlier['pstars']}"
    )
    logger.info("Brunner-Munzel is robust to outliers")

    # Example 4: Unequal variances
    logger.info("\n=== Example 4: Unequal variances ===")

    x4 = np.random.normal(0, 1, 50)
    y4 = np.random.normal(0.5, 3, 50)  # Much larger variance

    result_unequal = test_brunner_munzel(
        x4, y4, var_x="Low Variance", var_y="High Variance"
    )

    logger.info(f"W = {result_unequal['statistic']:.3f}")
    logger.info(
        f"p = {result_unequal['pvalue']:.4f} {result_unequal['pstars']}"
    )
    logger.info(f"Variance ratio: {np.var(y4) / np.var(x4):.1f}")

    # Example 5: One-sided test
    logger.info("\n=== Example 5: One-sided test ===")

    x5 = np.random.normal(0, 1, 40)
    y5 = np.random.normal(0.8, 1, 40)

    result_two = test_brunner_munzel(x5, y5, alternative="two-sided")
    result_less = test_brunner_munzel(x5, y5, alternative="less")

    logger.info(
        f"Two-sided: p = {result_two['pvalue']:.4f} {result_two['pstars']}"
    )
    logger.info(
        f"One-sided (less): p = {result_less['pvalue']:.4f} {result_less['pstars']}"
    )

    # Example 6: With visualization
    logger.info("\n=== Example 6: With visualization ===")

    x6 = np.random.exponential(2, 50)
    y6 = np.random.exponential(3, 50)

    result6, fig6 = test_brunner_munzel(
        x6,
        y6,
        var_x="Exponential (λ=0.5)",
        var_y="Exponential (λ=0.33)",
        plot=True,
    )

    stx.io.save(fig6, "./brunner_munzel_demo.png")
    logger.info("Visualization saved")

    # Example 7: DataFrame output
    logger.info("\n=== Example 7: DataFrame output ===")

    df_result = test_brunner_munzel(x1, y1, return_as="dataframe")
    logger.info(f"\n{df_result.T}")

    # Example 8: Multiple comparisons
    logger.info("\n=== Example 8: Multiple comparisons ===")

    from ...utils._normalizers import convert_results

    results_list = []
    for i in range(5):
        x = np.random.exponential(2, 30)
        y = np.random.exponential(2.5, 30)
        result = test_brunner_munzel(
            x, y, var_x=f"Control_{i}", var_y=f"Treatment_{i}"
        )
        results_list.append(result)

    df_all = combine_results(results_list)
    logger.info(
        f"\n{df_all[['var_x', 'var_y', 'pvalue', 'pstars', 'effect_size', 'effect_size_secondary']]}"
    )

    # Example 9: Export to various formats
    logger.info("\n=== Example 9: Export to various formats ===")

    from ...utils._normalizers import export_results, export_summary

    # CSV export (all columns)
    csv_path = export_results(df_all, "./brunner_munzel_results.csv")
    logger.info(f"Exported full results to: {csv_path}")

    # Summary export (key columns only)
    summary_path = export_summary(df_all, "./brunner_munzel_summary.csv")
    logger.info(f"Exported summary to: {summary_path}")

    # JSON export
    json_path = export_results(df_all, "./brunner_munzel_results.json")
    logger.info(f"Exported to JSON: {json_path}")

    # Excel export
    try:
        xlsx_path = export_results(df_all, "./brunner_munzel_results.xlsx")
        logger.info(f"Exported to Excel: {xlsx_path}")
    except ImportError:
        logger.warning("openpyxl not available, skipping Excel export")

    # LaTeX table export
    latex_path = export_summary(
        df_all,
        "./brunner_munzel_table.tex",
        columns=[
            "var_x",
            "var_y",
            "pvalue",
            "pstars",
            "effect_size",
            "effect_size_secondary",
        ],
    )
    logger.info(f"Exported LaTeX table: {latex_path}")

    # Tab-separated text file
    txt_path = export_results(
        df_all, "./brunner_munzel_results.txt", format="txt"
    )
    logger.info(f"Exported to text: {txt_path}")

    return 0


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Demonstrate Brunner-Munzel test"
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Enable verbose output"
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


if __name__ == "__main__":
    run_main()

# EOF
