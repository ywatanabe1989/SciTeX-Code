#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-01 16:30:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/stats/tests/parametric/_test_anova.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------


"""
Functionalities:
  - Perform one-way ANOVA for independent samples
  - Compute eta-squared effect size
  - Generate box plots and distribution visualizations
  - Support flexible output formats (dict or DataFrame)
  - Automatic normality and homogeneity checking

Dependencies:
  - packages: numpy, pandas, scipy, matplotlib

IO:
  - input: Multiple independent samples (arrays or Series)
  - output: Test results (dict or DataFrame) and optional figure
"""

"""Imports"""
import sys
import argparse
import numpy as np
import pandas as pd
from typing import Union, Optional, Literal, List
from scipy import stats
import matplotlib.pyplot as plt
import matplotlib.axes
import scitex as stx
from scitex.logging import getLogger

logger = getLogger(__name__)

"""Functions"""
def test_anova(
    groups: List[Union[np.ndarray, pd.Series]],
    var_names: Optional[List[str]] = None,
    alpha: float = 0.05,
    check_assumptions: bool = True,
    plot: bool = False,
    ax: Optional[matplotlib.axes.Axes] = None,
    return_as: Literal['dict', 'dataframe'] = 'dict',
    decimals: int = 3,
    verbose: bool = False
) -> Union[dict, pd.DataFrame]:
    """
    Perform one-way ANOVA for independent samples.

    Parameters
    ----------
    groups : list of arrays
        List of sample arrays for each group (minimum 2 groups)
    var_names : list of str, optional
        Names for each group. If None, uses 'Group 1', 'Group 2', etc.
    alpha : float, default 0.05
        Significance level
    check_assumptions : bool, default True
        Whether to check normality and homogeneity assumptions
    plot : bool, default False
        Whether to generate visualization
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
        - test_method: 'One-way ANOVA'
        - statistic: F-statistic value
        - pvalue: p-value
        - stars: Significance stars
        - significant: Whether null hypothesis is rejected
        - effect_size: Eta-squared (η²)
        - effect_size_metric: 'eta-squared'
        - effect_size_interpretation: Interpretation of eta-squared
        - n_groups: Number of groups
        - n_samples: Sample sizes for each group
        - df_between: Degrees of freedom between groups
        - df_within: Degrees of freedom within groups
        - var_names: Group labels
        - assumptions_met: Whether assumptions are satisfied
        - H0: Null hypothesis description

    Notes
    -----
    One-way ANOVA (Analysis of Variance) tests whether samples from different
    groups have the same population mean.

    **Null Hypothesis (H0)**: All groups have equal population means

    **Alternative Hypothesis (H1)**: At least one group mean differs

    **Assumptions**:
    1. **Independence**: Observations within and between groups are independent
    2. **Normality**: Data in each group are normally distributed
       - Can be checked with test_shapiro()
       - Robust to moderate violations with large samples (n > 30 per group)
    3. **Homogeneity of variance**: Groups have equal population variances
       - Can be checked with Levene's test
       - If violated, consider Welch's ANOVA or non-parametric alternative

    **When assumptions are violated**:
    - Non-normality: Use test_kruskal() (Kruskal-Wallis test)
    - Unequal variances: Use Welch's ANOVA (not yet implemented)
    - Outliers present: Use test_kruskal() or remove outliers

    **F-Statistic**:

    .. math::
        F = \\frac{MS_{between}}{MS_{within}} = \\frac{SS_{between}/(k-1)}{SS_{within}/(N-k)}

    Where:
    - k: Number of groups
    - N: Total sample size
    - SS: Sum of squares
    - MS: Mean square

    **Effect Size (Eta-squared)**:

    .. math::
        \\eta^2 = \\frac{SS_{between}}{SS_{total}}

    Interpretation:
    - η² < 0.01:  negligible
    - η² < 0.06:  small
    - η² < 0.14:  medium
    - η² ≥ 0.14:  large

    **Post-hoc tests**:
    If significant, perform pairwise comparisons with correction:
    - test_ttest_ind() for all pairs (if assumptions met)
    - test_brunner_munzel() for all pairs (robust alternative)
    - correct_bonferroni() or correct_fdr() for multiple comparisons

    References
    ----------
    .. [1] Fisher, R. A. (1925). Statistical Methods for Research Workers.
           Oliver and Boyd.
    .. [2] Cohen, J. (1988). Statistical Power Analysis for the Behavioral
           Sciences (2nd ed.). Routledge.
    .. [3] Maxwell, S. E., & Delaney, H. D. (2004). Designing Experiments
           and Analyzing Data: A Model Comparison Perspective (2nd ed.).
           Psychology Press.

    Examples
    --------
    >>> # Three groups with different means
    >>> group1 = np.array([1, 2, 3, 4, 5])
    >>> group2 = np.array([3, 4, 5, 6, 7])
    >>> group3 = np.array([5, 6, 7, 8, 9])
    >>> result = test_anova([group1, group2, group3])
    >>> result['rejected']
    True

    >>> # With auto-created figure
    >>> result = test_anova(
    ...     [group1, group2, group3],
    ...     var_names=['Control', 'Treatment 1', 'Treatment 2'],
    ...     plot=True
    ... )

    >>> # Plot on existing axes
    >>> fig, ax = plt.subplots()
    >>> result = test_anova([group1, group2, group3], ax=ax)

    >>> # Export results
    >>> from scitex.stats.utils._normalizers import convert_results
    >>> convert_results(result, return_as='excel', path='anova_results.xlsx')
    """
    from ...utils._formatters import p2stars
    from ...utils._normalizers import force_dataframe, convert_results
    from ...utils._effect_size import eta_squared, interpret_eta_squared
    from ..normality._test_shapiro import test_normality

    # Validate input
    if len(groups) < 2:
        raise ValueError("ANOVA requires at least 2 groups")

    # Convert to numpy arrays and remove NaN
    groups = [np.asarray(g) for g in groups]
    groups = [g[~np.isnan(g)] for g in groups]

    # Generate default names if not provided
    if var_names is None:
        var_names = [f'Group {i+1}' for i in range(len(groups))]

    if len(var_names) != len(groups):
        raise ValueError("Number of var_names must match number of groups")

    # Get sample sizes
    n_samples = [len(g) for g in groups]
    n_groups = len(groups)
    n_total = sum(n_samples)

    # Check assumptions if requested
    assumptions_met = True
    assumption_warnings = []

    if check_assumptions:
        # Check normality for each group
        normality_check = test_normality(*groups, var_names=var_names, alpha=alpha, warn=False)

        if not normality_check['all_normal']:
            assumptions_met = False
            non_normal = [r['var_x'] for r in normality_check['results'] if not r['normal']]
            warning_msg = (
                f"Normality assumption violated for: {', '.join(non_normal)}. "
                "Consider using test_kruskal() (Kruskal-Wallis test) instead."
            )
            assumption_warnings.append(warning_msg)
            logger.warning(warning_msg)

        # Check homogeneity of variance (Levene's test)
        levene_stat, levene_p = stats.levene(*groups)

        if levene_p < alpha:
            assumptions_met = False
            warning_msg = (
                f"Homogeneity of variance violated (Levene's test: p={levene_p:.4f}). "
                "Consider using Welch's ANOVA or test_kruskal()."
            )
            assumption_warnings.append(warning_msg)
            logger.warning(warning_msg)

    # Perform one-way ANOVA
    f_result = stats.f_oneway(*groups)
    f_stat = float(f_result.statistic)
    pvalue = float(f_result.pvalue)

    # Determine rejection
    rejected = pvalue < alpha

    # Compute effect size (eta-squared)
    effect_size = eta_squared(groups)
    effect_size_interp = interpret_eta_squared(effect_size)

    # Compute degrees of freedom
    df_between = n_groups - 1
    df_within = n_total - n_groups

    # Compile results
    result = {
        'test_method': 'One-way ANOVA',
        'statistic': round(f_stat, decimals),
        'n_groups': n_groups,
        'n_samples': n_samples,
        'df_between': df_between,
        'df_within': df_within,
        'var_names': var_names,
        'pvalue': round(pvalue, decimals),
        'stars': p2stars(pvalue),
        'alpha': alpha,
        'significant': rejected,
        'effect_size': round(effect_size, decimals),
        'effect_size_metric': 'eta-squared',
        'effect_size_interpretation': effect_size_interp,
        'assumptions_met': assumptions_met,
        'H0': 'All groups have equal population means',
    }

    # Add assumption warnings if any
    if assumption_warnings:
        result['assumption_warnings'] = assumption_warnings

    # Add post-hoc recommendation if significant
    if result['significant']:
        if assumptions_met:
            result['recommendation'] = (
                "Significant difference detected. Perform post-hoc pairwise comparisons "
                "with test_ttest_ind() and apply correction (correct_bonferroni or correct_fdr)."
            )
        else:
            result['recommendation'] = (
                "Significant difference detected, but assumptions violated. "
                "Consider using test_kruskal() or performing pairwise test_brunner_munzel() with correction."
            )
    else:
        result['recommendation'] = "No significant difference between groups."

    # Log results if verbose
    if verbose:
        logger.info(f"One-way ANOVA: F({df_between}, {df_within}) = {f_stat:.3f}, p = {pvalue:.4f} {p2stars(pvalue)}")
        logger.info(f"η² = {effect_size:.3f} ({effect_size_interp})")

    # Auto-enable plotting if ax is provided
    if ax is not None:
        plot = True

    # Generate plot if requested
    if plot:
        if ax is None:
            fig, ax = stx.plt.subplots()
        _plot_anova(groups, var_names, result, ax)

    # Convert to requested format
    if return_as == 'dataframe':
        result = force_dataframe(result)
    elif return_as not in ['dict', 'dataframe']:
        # Use universal converter for other formats
        return convert_results(result, return_as=return_as)

    return result


def _plot_anova(groups, var_names, result, ax):
    """Create violin+swarm visualization for ANOVA results on given axes."""
    positions = np.arange(1, len(groups) + 1)
    n_groups = len(groups)

    # Use matplotlib default color cycle
    prop_cycle = stx.plt.rcParams['axes.prop_cycle']
    colors = prop_cycle.by_key()['color'][:n_groups]

    # Violin plot (in background)
    parts = ax.violinplot(
        groups,
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
    for i, vals in enumerate(groups):
        y_vals = vals
        x_vals = np.random.normal(positions[i], 0.04, size=len(vals))
        ax.scatter(
            x_vals, y_vals,
            alpha=0.6,
            s=40,
            color=colors[i],
            edgecolors='white',
            linewidths=0.5,
            zorder=3  # Ensure points are in front
        )

    # Add mean lines
    for i, vals in enumerate(groups):
        mean = np.mean(vals)
        ax.hlines(
            mean,
            positions[i] - 0.3,
            positions[i] + 0.3,
            colors='black',
            linewidth=2,
            zorder=4
        )

    ax.set_xticks(positions)
    ax.set_xticklabels(var_names)
    ax.set_ylabel('Value')
    ax.set_title(
        f"One-way ANOVA\n"
        f"F({result['df_between']}, {result['df_within']}) = {result['statistic']:.3f}, "
        f"p = {result['pvalue']:.4f} {result['stars']}\n"
        f"η² = {result['effect_size']:.3f} ({result['effect_size_interpretation']})"
    )
    ax.grid(True, alpha=0.3, axis='y')

    # Add significance annotation
    if result['significant']:
        y_max = max(np.max(g) for g in groups)
        y_range = y_max - min(np.min(g) for g in groups)
        y_pos = y_max + 0.1 * y_range

        ax.plot([1, len(groups)], [y_pos, y_pos], 'k-', linewidth=1.5)
        ax.text(
            (1 + len(groups)) / 2, y_pos + 0.02 * y_range,
            result['stars'],
            ha='center', va='bottom', fontsize=14, fontweight='bold'
        )


"""Main function"""
def main(args):
    """Demonstrate one-way ANOVA functionality."""
    logger.info("Demonstrating one-way ANOVA")

    # Set random seed
    np.random.seed(42)

    # Example 1: Three groups with clear differences
    logger.info("\n=== Example 1: Three groups with clear differences ===")

    group1 = np.random.normal(5, 1, 30)
    group2 = np.random.normal(7, 1, 30)
    group3 = np.random.normal(9, 1, 30)

    result1 = test_anova(
        [group1, group2, group3],
        var_names=['Group A', 'Group B', 'Group C'],
        verbose=True
    )

    logger.info(f"F({result1['df_between']}, {result1['df_within']}) = {result1['statistic']:.3f}")
    logger.info(f"p = {result1['pvalue']:.4f} {result1['stars']}")
    logger.info(f"η² = {result1['effect_size']:.3f} ({result1['effect_size_interpretation']})")
    logger.info(f"Assumptions met: {result1['assumptions_met']}")
    logger.info(f"Recommendation: {result1['recommendation']}")

    # Example 2: No significant difference
    logger.info("\n=== Example 2: No significant difference ===")

    group1 = np.random.normal(5, 1, 30)
    group2 = np.random.normal(5.2, 1, 30)
    group3 = np.random.normal(4.9, 1, 30)

    result2 = test_anova(
        [group1, group2, group3],
        var_names=['Control', 'Treatment 1', 'Treatment 2'],
        verbose=True
    )

    logger.info(f"F({result2['df_between']}, {result2['df_within']}) = {result2['statistic']:.3f}")
    logger.info(f"p = {result2['pvalue']:.4f}")
    logger.info(f"Significant: {result2['significant']}")

    # Example 3: With visualization
    logger.info("\n=== Example 3: Complete analysis with visualization ===")

    group1 = np.random.normal(10, 2, 25)
    group2 = np.random.normal(12, 2, 25)
    group3 = np.random.normal(14, 2, 25)
    group4 = np.random.normal(16, 2, 25)

    result3 = test_anova(
        [group1, group2, group3, group4],
        var_names=['Dose 0', 'Dose 1', 'Dose 2', 'Dose 3'],
        plot=True,
        verbose=True
    )
    stx.io.save(plt.gcf(), "./.dev/anova_example3.jpg")
    plt.close()

    # Example 4: Assumption violation - unequal variances
    logger.info("\n=== Example 4: Unequal variances ===")

    group1 = np.random.normal(5, 1, 30)    # Small variance
    group2 = np.random.normal(7, 3, 30)    # Large variance
    group3 = np.random.normal(9, 1, 30)    # Small variance

    result4 = test_anova(
        [group1, group2, group3],
        var_names=['Group A', 'Group B', 'Group C'],
        check_assumptions=True,
        verbose=True
    )

    logger.info(f"F = {result4['statistic']:.3f}, p = {result4['pvalue']:.4f}")
    logger.info(f"Assumptions met: {result4['assumptions_met']}")
    if 'assumption_warnings' in result4:
        for warning in result4['assumption_warnings']:
            logger.info(f"Warning: {warning}")

    # Example 5: Non-normal data
    logger.info("\n=== Example 5: Non-normal data (exponential) ===")

    group1 = np.random.exponential(2, 30)
    group2 = np.random.exponential(3, 30)
    group3 = np.random.exponential(4, 30)

    result5 = test_anova(
        [group1, group2, group3],
        var_names=['Exp 1', 'Exp 2', 'Exp 3'],
        check_assumptions=True,
        verbose=True
    )

    logger.info(f"F = {result5['statistic']:.3f}, p = {result5['pvalue']:.4f}")
    logger.info(f"Assumptions met: {result5['assumptions_met']}")
    logger.info(f"Recommendation: {result5['recommendation']}")

    # Example 6: Post-hoc pairwise comparisons
    logger.info("\n=== Example 6: Post-hoc pairwise comparisons ===")

    from ._test_ttest import test_ttest_ind
    from ...correct._correct_bonferroni import correct_bonferroni

    # Use data from Example 1 (assumptions met)
    groups = [group1, group2, group3]
    names = ['Group A', 'Group B', 'Group C']

    # Perform overall ANOVA
    overall = test_anova(groups, var_names=names, verbose=True)

    if overall['significant'] and overall['assumptions_met']:
        logger.info("Overall ANOVA significant. Performing post-hoc pairwise t-tests...")

        # Pairwise comparisons
        pairwise_results = []
        for i in range(len(groups)):
            for j in range(i + 1, len(groups)):
                result = test_ttest_ind(
                    groups[i], groups[j],
                    var_x=names[i], var_y=names[j]
                )
                pairwise_results.append(result)
                logger.info(
                    f"{names[i]} vs {names[j]}: "
                    f"t = {result['statistic']:.3f}, "
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

    # Example 7: Comparison with Kruskal-Wallis
    logger.info("\n=== Example 7: ANOVA vs Kruskal-Wallis comparison ===")

    from ..nonparametric._test_kruskal import test_kruskal

    # Use non-normal data
    groups_exp = [
        np.random.exponential(2, 30),
        np.random.exponential(3, 30),
        np.random.exponential(4, 30)
    ]

    anova_result = test_anova(groups_exp, check_assumptions=False, verbose=True)
    kruskal_result = test_kruskal(groups_exp, verbose=True)

    logger.info(f"ANOVA:   F = {anova_result['statistic']:.3f}, p = {anova_result['pvalue']:.4f}")
    logger.info(f"Kruskal: H = {kruskal_result['statistic']:.3f}, p = {kruskal_result['pvalue']:.4f}")
    logger.info("Note: Kruskal-Wallis is more appropriate for non-normal data")

    # Example 8: Export results
    logger.info("\n=== Example 8: Export results ===")

    from ...utils._normalizers import convert_results, force_dataframe

    # Collect multiple test results
    test_results = [result1, result2, result3, result4, result5]

    # Export to DataFrame
    df = force_dataframe(test_results)
    logger.info(f"\nDataFrame shape: {df.shape}")

    # Export to Excel
    convert_results(test_results, return_as='excel', path='./.dev/anova_tests.xlsx')
    logger.info("Results exported to Excel")

    # Export to CSV
    convert_results(test_results, return_as='csv', path='./.dev/anova_tests.csv')
    logger.info("Results exported to CSV")

    return 0


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Demonstrate one-way ANOVA'
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
