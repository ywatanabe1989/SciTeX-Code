#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-01 22:40:43 (ywatanabe)"
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
from typing import Literal, Optional, Union

import matplotlib
import matplotlib.axes
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scitex as stx
from scipy import stats
from scitex.logging import getLogger

from ...utils._normalizers import export_results, export_summary

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
    ax: Optional[matplotlib.axes.Axes] = None,
    return_as: Literal["dict", "dataframe"] = "dict",
    verbose: bool = False,
) -> Union[dict, pd.DataFrame]:
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
    ax : matplotlib.axes.Axes, optional
        Axes object to plot on. If None and plot=True, creates new figure.
        If provided, automatically enables plotting.
    return_as : {'dict', 'dataframe'}, default 'dict'
        Output format
    verbose : bool, default False
        Whether to print test results

    Returns
    -------
    results : dict or DataFrame
        Test results including:
        - test_method: 'Brunner-Munzel test'
        - statistic_name: 'W'
        - statistic: W-statistic value
        - pvalue: p-value
        - stars: Significance stars
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

    >>> # With auto-created figure
    >>> result = test_brunner_munzel(x, y, plot=True)

    >>> # Plot on existing axes
    >>> fig, ax = plt.subplots()
    >>> result = test_brunner_munzel(x, y, ax=ax)

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
        "statistic": w_stat,
        "alternative": alternative,
        "n_x": n_x,
        "n_y": n_y,
        "var_x": var_x,
        "var_y": var_y,
        "pvalue": pvalue,
        "stars": p2stars(pvalue),
        "alpha": alpha,
        "significant": pvalue < alpha,
        "effect_size": prob_xy,
        "effect_size_metric": "P(X>Y)",
        "effect_size_interpretation": prob_interp,
        "effect_size_secondary": delta,
        "effect_size_secondary_metric": "Cliff's delta",
        "effect_size_secondary_interpretation": delta_interp,
        "H0": H0,
    }

    # Log results if verbose
    if verbose:
        logger.info(
            f"Brunner-Munzel: W = {w_stat:.3f}, p = {pvalue:.4f} {p2stars(pvalue)}"
        )
        logger.info(
            f"P(X>Y) = {prob_xy:.3f} ({prob_interp}), Cliff's δ = {delta:.3f} ({delta_interp})"
        )

    # Auto-enable plotting if ax is provided
    if ax is not None:
        plot = True

    # Generate plot if requested
    if plot:
        if ax is None:
            fig, ax = stx.plt.subplots()
        _plot_brunner_munzel(x, y, var_x, var_y, result, ax)

    # Convert to requested format
    if return_as == "dataframe":
        result = force_dataframe(result)

    return result


def _plot_brunner_munzel(x, y, var_x, var_y, result, ax):
    """Create violin+swarm visualization for Brunner-Munzel test on given axes."""
    positions = [0, 1]
    box_data = [x, y]
    colors = ["C0", "C1"]  # Use default matplotlib colors

    # Violin plot (in background)
    parts = ax.violinplot(
        box_data,
        positions=positions,
        widths=0.6,
        showmeans=False,
        showmedians=False,
        showextrema=False,
    )

    # Color violin plots
    for i, pc in enumerate(parts["bodies"]):
        pc.set_facecolor(colors[i])
        pc.set_alpha(0.3)
        pc.set_edgecolor(colors[i])
        pc.set_linewidth(1.5)

    # Swarm plot (in front) - jittered scatter points
    np.random.seed(42)
    for i, vals in enumerate(box_data):
        y_vals = vals
        x_vals = np.random.normal(positions[i], 0.04, size=len(vals))
        ax.scatter(
            x_vals,
            y_vals,
            alpha=0.6,
            s=40,
            color=colors[i],
            edgecolors="white",
            linewidths=0.5,
            zorder=3,  # Ensure points are in front
        )

    # Add median lines
    for i, vals in enumerate(box_data):
        median = np.median(vals)
        ax.hlines(
            median,
            positions[i] - 0.3,
            positions[i] + 0.3,
            colors="black",
            linewidth=2,
            zorder=4,
        )

    # Add significance stars
    y_max = max(np.max(x), np.max(y))
    y_min = min(np.min(x), np.min(y))
    y_range = y_max - y_min
    sig_y = y_max + y_range * 0.05

    ax.plot([0, 1], [sig_y, sig_y], "k-", linewidth=1.5)
    ax.text(
        0.5,
        sig_y + y_range * 0.02,
        result["stars"],
        ha="center",
        va="bottom",
        fontsize=14,
        fontweight="bold",
    )

    ax.set_xticks(positions)
    ax.set_xticklabels([var_x, var_y])
    ax.set_ylabel("Value")
    ax.set_title(
        f"Brunner-Munzel test\n"
        f"W = {result['statistic']:.2f}, "
        f"p = {result['pvalue']:.4f} {result['stars']}\n"
        f"P(X>Y) = {result['effect_size']:.2f}, "
        f"δ = {result['effect_size_secondary']:.2f}"
    )
    ax.grid(True, alpha=0.3, axis="y")


"""Main function"""


def main(args):
    logger.info("Demonstrating Brunner-Munzel test")
    np.random.seed(42)

    def example_01_normal_distributions():
        logger.info("\n=== Example 1: Normal distributions ===")
        x1 = np.random.normal(0, 1, 50)
        y1 = np.random.normal(0.6, 1, 50)
        result_dict = test_brunner_munzel(
            x1, y1, var_x="Control", var_y="Treatment", plot=True, verbose=True
        )
        stx.io.save(plt.gcf(), "./example_01_normal_distributions.jpg")
        return x1, y1

    def example_02_skewed_distributions():
        logger.info("\n=== Example 2: Non-normal (skewed) distributions ===")
        x2 = np.random.gamma(2, 2, 40)
        y2 = np.random.gamma(3, 2, 40)
        result_df = test_brunner_munzel(
            x2,
            y2,
            var_x="Group A",
            var_y="Group B",
            return_as="dataframe",
            plot=True,
            verbose=True,
        )
        logger.info(
            f"Cliff's δ = {result_df['effect_size_secondary'].iloc[0]:.3f}"
        )
        stx.io.save(plt.gcf(), "./example_02_skewed_distributions.jpg")
        stx.io.save(result_df, "./example_02_skewed_distributions.csv")
        stx.io.save(result_df, "./example_02_skewed_distributions.xlsx")

    def example_03_data_with_outliers():
        logger.info("\n=== Example 3: Data with outliers ===")
        x3 = np.concatenate([np.random.normal(0, 1, 35), [10, 12]])
        y3 = np.random.normal(0.5, 1, 40)
        result_df = test_brunner_munzel(
            x3,
            y3,
            var_x="With Outliers",
            var_y="Normal",
            return_as="dataframe",
            plot=True,
            verbose=True,
        )
        stx.io.save(plt.gcf(), "./example_03_data_with_outliers.jpg")
        stx.io.save(result_df, "./example_03_data_with_outliers.csv")
        stx.io.save(result_df, "./example_03_data_with_outliers.xlsx")

    def example_04_unequal_variances():
        logger.info("\n=== Example 4: Unequal variances ===")
        x4 = np.random.normal(0, 1, 50)
        y4 = np.random.normal(0.5, 3, 50)
        result_df = test_brunner_munzel(
            x4,
            y4,
            var_x="Low Variance",
            var_y="High Variance",
            return_as="dataframe",
            plot=True,
            verbose=True,
        )
        stx.io.save(plt.gcf(), "./example_04_unequal_variances.jpg")
        stx.io.save(result_df, "./example_04_unequal_variances.csv")
        stx.io.save(result_df, "./example_04_unequal_variances.xlsx")
        logger.info(f"Variance ratio: {np.var(y4) / np.var(x4):.1f}")

    def example_05_one_sided_test():
        logger.info("\n=== Example 5: One-sided test ===")
        x5 = np.random.normal(0, 1, 40)
        y5 = np.random.normal(0.8, 1, 40)
        result_two = test_brunner_munzel(
            x5, y5, alternative="two-sided", plot=True, verbose=True
        )
        result_less = test_brunner_munzel(
            x5, y5, alternative="less", plot=True, verbose=True
        )

    def example_06_with_visualization():
        logger.info("\n=== Example 6: With visualization ===")
        x6 = np.random.exponential(2, 50)
        y6 = np.random.exponential(3, 50)
        result6 = test_brunner_munzel(
            x6,
            y6,
            var_x="Exponential (λ=0.5)",
            var_y="Exponential (λ=0.33)",
            return_as="dataframe",
            plot=True,
            verbose=True,
        )
        stx.io.save(plt.gcf(), "./example_06_with_visualization.jpg")

    def example_07_dataframe_output():
        logger.info("\n=== Example 7: DataFrame output ===")
        x1, y1 = example_01_normal_distributions()
        df_result = test_brunner_munzel(x1, y1, return_as="dataframe")
        logger.info(f"\n{df_result.T}")

    def example_08_multiple_comparisons():
        logger.info("\n=== Example 8: Multiple comparisons ===")
        from ...utils._normalizers import combine_results, convert_results

        results_list = []
        for ii in range(5):
            x_temp = np.random.exponential(2, 30)
            y_temp = np.random.exponential(2.5, 30)
            result_temp = test_brunner_munzel(
                x_temp, y_temp, var_x=f"Control_{ii}", var_y=f"Treatment_{ii}"
            )
            results_list.append(result_temp)
        df_all = combine_results(results_list)
        logger.info(
            f"\n{df_all[['var_x', 'var_y', 'pvalue', 'stars', 'effect_size', 'effect_size_secondary']]}"
        )
        return df_all

    def example_09_export_to_various_formats():
        logger.info("\n=== Example 9: Export to various formats ===")
        df_all = example_08_multiple_comparisons()
        csv_path = export_results(
            df_all, "./example_09_export_to_various_formats_results.csv"
        )
        logger.info(f"Exported full results to: {csv_path}")
        summary_path = export_summary(
            df_all, "./example_09_export_to_various_formats_summary.csv"
        )
        logger.info(f"Exported summary to: {summary_path}")
        json_path = export_results(
            df_all, "./example_09_export_to_various_formats_results.json"
        )
        logger.info(f"Exported to JSON: {json_path}")
        try:
            xlsx_path = export_results(
                df_all, "./example_09_export_to_various_formats_results.xlsx"
            )
            logger.info(f"Exported to Excel: {xlsx_path}")
        except ImportError:
            logger.warning("openpyxl not available, skipping Excel export")
        latex_path = export_summary(
            df_all,
            "./example_09_export_to_various_formats_table.tex",
            columns=[
                "var_x",
                "var_y",
                "pvalue",
                "stars",
                "effect_size",
                "effect_size_secondary",
            ],
        )
        logger.info(f"Exported LaTeX table: {latex_path}")
        txt_path = export_results(
            df_all,
            "./example_09_export_to_various_formats_results.txt",
            format="txt",
        )
        logger.info(f"Exported to text: {txt_path}")

    example_01_normal_distributions()
    example_02_skewed_distributions()
    example_03_data_with_outliers()
    example_04_unequal_variances()
    example_05_one_sided_test()
    example_06_with_visualization()
    example_07_dataframe_output()
    example_08_multiple_comparisons()
    example_09_export_to_various_formats()

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
