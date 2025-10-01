#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-01 18:14:34 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/stats/tests/nonparametric/_test_kruskal.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/stats/tests/nonparametric/_test_kruskal.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
  - Perform Kruskal-Wallis H test for independent samples
  - Non-parametric alternative to one-way ANOVA
  - Compute epsilon-squared effect size
  - Generate box plots with significance annotations
  - Support flexible output formats (dict or DataFrame)

Dependencies:
  - packages: numpy, pandas, scipy, matplotlib

IO:
  - input: Multiple independent samples (arrays or Series)
  - output: Test results (dict or DataFrame) and optional figure
"""

"""Imports"""
import argparse
from typing import List, Literal, Optional, Union

import matplotlib
import matplotlib.axes
import numpy as np
import pandas as pd
import scitex as stx
from scipy import stats
from scitex.logging import getLogger

logger = getLogger(__name__)

"""Functions"""


def test_kruskal(
    groups: List[Union[np.ndarray, pd.Series]],
    var_names: Optional[List[str]] = None,
    alpha: float = 0.05,
    plot: bool = False,
    ax: Optional[matplotlib.axes.Axes] = None,
    return_as: Literal["dict", "dataframe"] = "dict",
    decimals: int = 3,
    verbose: bool = False,
) -> Union[dict, pd.DataFrame]:
    """
    Perform Kruskal-Wallis H test for independent samples.

    Parameters
    ----------
    groups : list of arrays
        List of sample arrays for each group (minimum 2 groups)
    var_names : list of str, optional
        Names for each group. If None, uses 'Group 1', 'Group 2', etc.
    alpha : float, default 0.05
        Significance level
    plot : bool, default False
        Whether to generate box plots
    ax : matplotlib.axes.Axes, optional
        Axes object to plot on. If None and plot=True, creates new figure.
        If provided, automatically enables plotting.
    return_as : {'dict', 'dataframe'}, default 'dict'
        Output format
    decimals : int, default 3
        Number of decimal places for rounding
    verbose : bool, default False
        Whether to print test results

    Returns
    -------
    results : dict or DataFrame
        Test results including:
        - test_method: 'Kruskal-Wallis H test'
        - statistic: H-statistic value
        - pvalue: p-value
        - stars: Significance stars
        - significant: Whether null hypothesis is rejected
        - effect_size: Epsilon-squared (ε²)
        - effect_size_metric: 'epsilon-squared'
        - effect_size_interpretation: Interpretation of epsilon-squared
        - n_groups: Number of groups
        - n_samples: Sample sizes for each group
        - var_names: Group labels
        - H0: Null hypothesis description

    Notes
    -----
    The Kruskal-Wallis H test is a non-parametric alternative to one-way ANOVA.
    It tests whether samples originate from the same distribution by comparing
    the ranks of observations across groups.

    **Null Hypothesis (H0)**: All groups have the same population median
    (more precisely: all groups have identical distribution functions)

    **Assumptions**:
    - Independent observations within and between groups
    - Ordinal or continuous data
    - Similar distribution shapes across groups (for median interpretation)

    **Advantages over ANOVA**:
    - No normality assumption required
    - Robust to outliers
    - Works with ordinal data
    - More powerful than ANOVA for heavy-tailed distributions

    **When to use**:
    - Comparing 3+ independent groups
    - Data violate normality (use test_shapiro to check)
    - Presence of outliers
    - Ordinal data (e.g., Likert scales)

    **Test Statistic H**:

    .. math::
        H = \\frac{12}{N(N+1)} \\sum_{i=1}^{k} \\frac{R_i^2}{n_i} - 3(N+1)

    Where:
    - k: Number of groups
    - N: Total sample size
    - R_i: Sum of ranks for group i
    - n_i: Sample size of group i

    **Effect Size (Epsilon-squared)**:

    .. math::
        \\epsilon^2 = \\frac{H - k + 1}{N - k}

    Interpretation (similar to eta-squared):
    - ε² < 0.01:  negligible
    - ε² < 0.06:  small
    - ε² < 0.14:  medium
    - ε² ≥ 0.14:  large

    **Post-hoc tests**:
    If significant, use pairwise comparisons with correction:
    - test_brunner_munzel() for all pairs
    - correct_bonferroni() or correct_fdr() for multiple comparisons

    **Tied ranks**: Handled automatically by scipy.stats.kruskal()

    References
    ----------
    .. [1] Kruskal, W. H., & Wallis, W. A. (1952). "Use of ranks in
           one-criterion variance analysis". Journal of the American
           Statistical Association, 47(260), 583-621.
    .. [2] Hecke, T. V. (2012). "Power study of ANOVA versus Kruskal-Wallis
           test". Journal of Statistics and Management Systems, 15(2-3), 241-247.
    .. [3] Tomczak, M., & Tomczak, E. (2014). "The need to report effect size
           estimates revisited". Trends in Sport Sciences, 21(1), 19-25.

    Examples
    --------
    >>> # Three groups with different medians
    >>> group1 = np.array([1, 2, 3, 4, 5])
    >>> group2 = np.array([3, 4, 5, 6, 7])
    >>> group3 = np.array([5, 6, 7, 8, 9])
    >>> result = test_kruskal([group1, group2, group3])
    >>> result['rejected']
    True

    >>> # With custom names and plot
    >>> result, fig = test_kruskal(
    ...     [group1, group2, group3],
    ...     var_names=['Control', 'Treatment 1', 'Treatment 2'],
    ...     plot=True
    ... )

    >>> # Export results
    >>> from scitex.stats.utils._normalizers import convert_results
    >>> convert_results(result, return_as='excel', path='kruskal_results.xlsx')
    """
    from ...utils._effect_size import (epsilon_squared,
                                       interpret_epsilon_squared)
    from ...utils._formatters import p2stars
    from ...utils._normalizers import convert_results, force_dataframe

    # Validate input
    if len(groups) < 2:
        raise ValueError("Kruskal-Wallis test requires at least 2 groups")

    # Convert to numpy arrays and remove NaN
    groups = [np.asarray(g) for g in groups]
    groups = [g[~np.isnan(g)] for g in groups]

    # Check if all groups have at least 5 observations (recommended)
    for i, g in enumerate(groups):
        if len(g) < 5:
            logger.warning(
                f"Group {i+1} has only {len(g)} observations. "
                "Kruskal-Wallis test is most reliable with n ≥ 5 per group."
            )

    # Generate default names if not provided
    if var_names is None:
        var_names = [f"Group {i+1}" for i in range(len(groups))]

    if len(var_names) != len(groups):
        raise ValueError("Number of var_names must match number of groups")

    # Get sample sizes
    n_samples = [len(g) for g in groups]
    n_groups = len(groups)
    n_total = sum(n_samples)

    # Perform Kruskal-Wallis test
    h_result = stats.kruskal(*groups)
    h_stat = float(h_result.statistic)
    pvalue = float(h_result.pvalue)

    # Determine rejection
    rejected = pvalue < alpha

    # Compute effect size (epsilon-squared)
    effect_size = epsilon_squared(groups)
    effect_size_interp = interpret_epsilon_squared(effect_size)

    # Compile results
    result = {
        "test_method": "Kruskal-Wallis H test",
        "statistic": round(h_stat, decimals),
        "n_groups": n_groups,
        "n_samples": n_samples,
        "var_names": var_names,
        "pvalue": round(pvalue, decimals),
        "stars": p2stars(pvalue),
        "alpha": alpha,
        "significant": rejected,
        "effect_size": round(effect_size, decimals),
        "effect_size_metric": "epsilon-squared",
        "effect_size_interpretation": effect_size_interp,
        "H0": "All groups have the same population median",
    }

    # Add post-hoc recommendation if significant
    if rejected:
        result["recommendation"] = (
            "Significant difference detected. Perform post-hoc pairwise comparisons "
            "with test_brunner_munzel() and apply correction (correct_bonferroni or correct_fdr)."
        )
    else:
        result["recommendation"] = "No significant difference between groups."

    # Log results if verbose
    if verbose:
        logger.info(
            f"Kruskal-Wallis: H = {h_stat:.3f}, p = {pvalue:.4f} {p2stars(pvalue)}"
        )
        logger.info(
            f"Epsilon-squared = {effect_size:.3f} ({effect_size_interp})"
        )

    # Auto-enable plotting if ax is provided
    if ax is not None:
        plot = True

    # Generate plot if requested
    if plot:
        if ax is None:
            fig, ax = stx.plt.subplots()
        _plot_kruskal(groups, var_names, result, ax)

    # Convert to requested format
    if return_as == "dataframe":
        result = force_dataframe(result)
    elif return_as not in ["dict", "dataframe"]:
        # Use universal converter for other formats
        return convert_results(result, return_as=return_as)

    return result


def _plot_kruskal(groups, var_names, result, ax):
    """Create violin+swarm visualization on given axes."""
    n_groups = len(groups)
    positions = np.arange(n_groups)
    colors = [f"C{i}" for i in range(n_groups)]

    # Violin plot (background, transparent)
    parts = ax.violinplot(
        groups,
        positions=positions,
        widths=0.6,
        showmeans=False,
        showmedians=False,
        showextrema=False,
    )

    for i, pc in enumerate(parts["bodies"]):
        pc.set_facecolor(colors[i])
        pc.set_alpha(0.3)
        pc.set_edgecolor(colors[i])
        pc.set_linewidth(1.5)

    # Swarm plot (foreground - scatter in front!)
    np.random.seed(42)
    for i, vals in enumerate(groups):
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
            zorder=3,  # In front!
        )

    # Add median lines
    for i, vals in enumerate(groups):
        median = np.median(vals)
        ax.hlines(
            median,
            positions[i] - 0.3,
            positions[i] + 0.3,
            colors="black",
            linewidth=2,
            zorder=4,
        )

    # Significance annotation
    if result["rejected"]:
        y_max = max(np.max(g) for g in groups)
        y_min = min(np.min(g) for g in groups)
        y_range = y_max - y_min
        y_pos = y_max + 0.1 * y_range

        ax.plot([0, n_groups - 1], [y_pos, y_pos], "k-", linewidth=1.5)
        ax.text(
            (n_groups - 1) / 2,
            y_pos + 0.02 * y_range,
            result["stars"],
            ha="center",
            va="bottom",
            fontsize=14,
            fontweight="bold",
        )

    ax.set_xticks(positions)
    ax.set_xticklabels(var_names)
    ax.set_ylabel("Value")
    ax.set_title(
        f"Kruskal-Wallis Test\nH = {result['statistic']:.2f}, p = {result['pvalue']:.4f} {result['stars']}"
    )
    ax.grid(True, alpha=0.3, axis="y")


"""Main function"""


def main(args):
    """Demonstrate Kruskal-Wallis test functionality."""
    logger.info("Demonstrating Kruskal-Wallis H test")

    # Set random seed
    np.random.seed(42)

    # Example 1: Three groups with clear differences
    logger.info("\n=== Example 1: Three groups with clear differences ===")

    group1 = np.random.normal(5, 1, 30)
    group2 = np.random.normal(7, 1, 30)
    group3 = np.random.normal(9, 1, 30)

    result1 = test_kruskal(
        [group1, group2, group3], var_names=["Group A", "Group B", "Group C"], verbose=True
    )

    # Example 2: No significant difference
    logger.info("\n=== Example 2: No significant difference ===")

    group1 = np.random.normal(5, 1, 30)
    group2 = np.random.normal(5.2, 1, 30)
    group3 = np.random.normal(4.9, 1, 30)

    result2 = test_kruskal(
        [group1, group2, group3],
        var_names=["Control", "Treatment 1", "Treatment 2"],
        verbose=True
    )

    # Example 3: Non-normal data with outliers (with visualization)
    logger.info("\n=== Example 3: Non-normal data with outliers ===")

    group1 = np.concatenate(
        [np.random.exponential(2, 25), [20, 22]]  # Outliers
    )
    group2 = np.random.exponential(3, 27)
    group3 = np.random.exponential(4, 28)

    result3 = test_kruskal(
        [group1, group2, group3],
        var_names=["Exponential 1", "Exponential 2", "Exponential 3"],
        plot=True,
        verbose=True
    )
    stx.io.save(stx.plt.gcf(), "./kruskal_example3.jpg")
    stx.plt.close()

    # Example 4: Four groups comparison
    logger.info("\n=== Example 4: Four groups comparison ===")

    group1 = np.random.normal(10, 2, 25)
    group2 = np.random.normal(12, 2, 25)
    group3 = np.random.normal(14, 2, 25)
    group4 = np.random.normal(16, 2, 25)

    result4 = test_kruskal(
        [group1, group2, group3, group4],
        var_names=["Dose 0", "Dose 1", "Dose 2", "Dose 3"],
        verbose=True
    )

    # Example 5: Ordinal data (Likert scale)
    logger.info("\n=== Example 5: Ordinal data (Likert scale responses) ===")

    # Simulated Likert scale data (1-5)
    likert1 = np.random.choice(
        [1, 2, 3, 4, 5], size=50, p=[0.05, 0.15, 0.40, 0.30, 0.10]
    )
    likert2 = np.random.choice(
        [1, 2, 3, 4, 5], size=50, p=[0.10, 0.20, 0.30, 0.25, 0.15]
    )
    likert3 = np.random.choice(
        [1, 2, 3, 4, 5], size=50, p=[0.05, 0.10, 0.25, 0.35, 0.25]
    )

    result5 = test_kruskal(
        [likert1, likert2, likert3],
        var_names=["Condition A", "Condition B", "Condition C"],
        verbose=True
    )
    logger.info(
        f"Medians: {np.median(likert1):.1f}, {np.median(likert2):.1f}, {np.median(likert3):.1f}"
    )

    # Example 6: Post-hoc pairwise comparisons
    logger.info("\n=== Example 6: Post-hoc pairwise comparisons ===")

    from ...correct._correct_bonferroni import correct_bonferroni
    from ._test_brunner_munzel import test_brunner_munzel

    # Use data from Example 1
    groups = [group1, group2, group3]
    names = ["Group A", "Group B", "Group C"]

    # Perform overall test
    overall = test_kruskal(groups, var_names=names)

    if overall["significant"]:
        logger.info(
            "Overall test significant. Performing post-hoc pairwise comparisons..."
        )

        # Pairwise comparisons
        pairwise_results = []
        for i in range(len(groups)):
            for j in range(i + 1, len(groups)):
                result = test_brunner_munzel(
                    groups[i], groups[j], var_x=names[i], var_y=names[j]
                )
                pairwise_results.append(result)
                logger.info(
                    f"{names[i]} vs {names[j]}: "
                    f"p = {result['pvalue']:.4f} {result['stars']}"
                )

        # Apply Bonferroni correction
        corrected = correct_bonferroni(pairwise_results)

        logger.info("\nAfter Bonferroni correction:")
        for res in corrected:
            logger.info(
                f"{res['var_x']} vs {res['var_y']}: "
                f"p_adjusted = {res['pvalue_adjusted']:.4f}, "
                f"significant = {res['significant']}"
            )

    # Example 7: Export results
    logger.info("\n=== Example 7: Export results to multiple formats ===")

    from ...utils._normalizers import convert_results, force_dataframe

    # Create multiple test results
    test_results = [result1, result2, result3, result4, result5]

    # Export to DataFrame
    df = force_dataframe(test_results)
    logger.info(f"\nDataFrame shape: {df.shape}")
    logger.info(f"Columns: {df.columns.tolist()}")

    # Export to Excel with styling
    convert_results(
        test_results, return_as="excel", path="./kruskal_tests.xlsx"
    )
    logger.info("Results exported to Excel")

    # Export to CSV
    convert_results(test_results, return_as="csv", path="./kruskal_tests.csv")
    logger.info("Results exported to CSV")

    return 0


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Demonstrate Kruskal-Wallis H test"
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
