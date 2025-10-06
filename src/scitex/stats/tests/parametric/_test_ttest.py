#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-01 15:00:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/stats/tests/_test_ttest.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
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
from typing import Union, Optional, Literal
from scipy import stats
import matplotlib.pyplot as plt
import matplotlib.axes
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
    ax: Optional[matplotlib.axes.Axes] = None,
    return_as: Literal['dict', 'dataframe'] = 'dict',
    verbose: bool = False
) -> Union[dict, pd.DataFrame]:
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
        - test_method: Name of test performed
        - statistic: t-statistic value
        - pvalue: p-value
        - stars: Significance stars
        - significant: Whether null hypothesis is rejected
        - effect_size: Cohen's d
        - power: Statistical power
        - n_x, n_y: Sample sizes
        - var_x, var_y: Variable labels
        - H0: Null hypothesis description

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

    >>> # With auto-created figure
    >>> result = test_ttest_ind(x, y, plot=True)

    >>> # Plot on existing axes
    >>> fig, ax = plt.subplots()
    >>> result = test_ttest_ind(x, y, ax=ax)

    >>> # As DataFrame
    >>> df = test_ttest_ind(x, y, return_as='dataframe')
    >>> df['stars'].iloc[0]
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
        'statistic': t_stat,
        'alternative': alternative,
        'n_x': n_x,
        'n_y': n_y,
        'var_x': var_x,
        'var_y': var_y,
        'pvalue': pvalue,
        'stars': p2stars(pvalue),
        'alpha': alpha,
        'significant': pvalue < alpha,
        'effect_size': effect_size,
        'effect_size_metric': "Cohen's d",
        'effect_size_interpretation': effect_size_interpretation,
        'power': power,
        'H0': H0,
    }

    # Log results if verbose
    if verbose:
        logger.info(f"{test_method}: t = {t_stat:.3f}, p = {pvalue:.4f} {p2stars(pvalue)}")
        logger.info(f"Cohen's d = {effect_size:.3f} ({effect_size_interpretation}), power = {power:.3f}")

    # Auto-enable plotting if ax is provided
    if ax is not None:
        plot = True

    # Generate plot if requested
    if plot:
        if ax is None:
            fig, ax = stx.plt.subplots()
        _plot_ttest_ind(x, y, var_x, var_y, result, ax)

    # Convert to requested format
    if return_as == 'dataframe':
        result = force_dataframe(result)

    return result


def _plot_ttest_ind(x, y, var_x, var_y, result, ax):
    """Create violin+swarm visualization for independent t-test on given axes."""
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
            x_vals, y_vals,
            alpha=0.6,
            s=40,
            color=colors[i],
            edgecolors='white',
            linewidths=0.5,
            zorder=3  # Ensure points are in front
        )

    # Add mean lines
    for i, vals in enumerate(box_data):
        mean = np.mean(vals)
        ax.hlines(
            mean,
            positions[i] - 0.3,
            positions[i] + 0.3,
            colors='black',
            linewidth=2,
            zorder=4
        )

    # Add significance stars
    y_max = max(np.max(x), np.max(y))
    y_min = min(np.min(x), np.min(y))
    y_range = y_max - y_min
    sig_y = y_max + y_range * 0.05

    ax.plot([0, 1], [sig_y, sig_y], 'k-', linewidth=1.5)
    ax.text(
        0.5, sig_y + y_range * 0.02,
        result['stars'],
        ha='center',
        va='bottom',
        fontsize=14,
        fontweight='bold'
    )

    ax.set_xticks(positions)
    ax.set_xticklabels([var_x, var_y])
    ax.set_ylabel('Value')
    ax.set_title(
        f"{result['test_method']}\n"
        f"t = {result['statistic']:.2f}, "
        f"p = {result['pvalue']:.4f} {result['stars']}\n"
        f"d = {result['effect_size']:.2f}, "
        f"power = {result['power']:.2f}"
    )
    ax.grid(True, alpha=0.3, axis='y')


def test_ttest_rel(
    x: Union[np.ndarray, pd.Series],
    y: Union[np.ndarray, pd.Series],
    var_x: str = 'before',
    var_y: str = 'after',
    alternative: Literal['two-sided', 'greater', 'less'] = 'two-sided',
    alpha: float = 0.05,
    plot: bool = False,
    ax: Optional[matplotlib.axes.Axes] = None,
    return_as: Literal['dict', 'dataframe'] = 'dict'
) -> Union[dict, pd.DataFrame]:
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
    ax : matplotlib.axes.Axes, optional
        Axes object to plot on. If None and plot=True, creates new figure.
        If provided, automatically enables plotting.
    return_as : {'dict', 'dataframe'}, default 'dict'
        Output format

    Returns
    -------
    results : dict or DataFrame
        Test results (same structure as test_ttest_ind)

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
    >>> fig, ax = plt.subplots()
    >>> result = test_ttest_rel(before, after, ax=ax)
    >>> plt.show()
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
        'statistic': t_stat,
        'alternative': alternative,
        'n_pairs': n_pairs,
        'var_x': var_x,
        'var_y': var_y,
        'pvalue': pvalue,
        'stars': p2stars(pvalue),
        'alpha': alpha,
        'significant': pvalue < alpha,
        'effect_size': effect_size,
        'effect_size_metric': "Cohen's d (paired)",
        'effect_size_interpretation': effect_size_interpretation,
        'power': power,
        'H0': H0,
    }

    # Auto-enable plotting if ax is provided
    if ax is not None:
        plot = True

    # Generate plot if requested
    if plot:
        if ax is None:
            fig, ax = stx.plt.subplots()
        _plot_ttest_rel(x, y, var_x, var_y, result, ax)

    # Convert to requested format
    if return_as == 'dataframe':
        result = force_dataframe(result)

    return result


def _plot_ttest_rel(x, y, var_x, var_y, result, ax):
    """Create visualization for paired t-test on given axes."""
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
    ax.set_title(
        f"Paired t-test\n"
        f"t = {result['statistic']:.2f}, "
        f"p = {result['pvalue']:.4f} {result['stars']}\n"
        f"d = {result['effect_size']:.2f}, "
        f"power = {result.get('power', np.nan):.2f}"
    )
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')


def test_ttest_1samp(
    x: Union[np.ndarray, pd.Series],
    popmean: float = 0,
    var_x: str = 'sample',
    alternative: Literal['two-sided', 'greater', 'less'] = 'two-sided',
    alpha: float = 0.05,
    plot: bool = False,
    ax: Optional[matplotlib.axes.Axes] = None,
    return_as: Literal['dict', 'dataframe'] = 'dict'
) -> Union[dict, pd.DataFrame]:
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
    ax : matplotlib.axes.Axes, optional
        Axes object to plot on. If provided, plots visualization on given axes.
    return_as : {'dict', 'dataframe'}, default 'dict'
        Output format

    Returns
    -------
    results : dict or DataFrame
        Test results

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
        'statistic': t_stat,
        'alternative': alternative,
        'n_x': n_x,
        'var_x': var_x,
        'popmean': popmean,
        'sample_mean': float(np.mean(x)),
        'pvalue': pvalue,
        'stars': p2stars(pvalue),
        'alpha': alpha,
        'significant': pvalue < alpha,
        'effect_size': effect_size,
        'effect_size_metric': "Cohen's d (one-sample)",
        'effect_size_interpretation': effect_size_interpretation,
        'power': power,
        'H0': H0,
    }

    # Generate plot if ax provided
    if ax is not None:
        _plot_ttest_1samp(x, popmean, var_x, result, ax)

    # Convert to requested format
    if return_as == 'dataframe':
        result = force_dataframe(result)

    return result


def _plot_ttest_1samp(x, popmean, var_x, result, ax):
    """Create visualization for one-sample t-test on given axes."""
    # Box plot
    bp = ax.boxplot([x], positions=[0], widths=0.4, patch_artist=True, showfliers=True)
    bp['boxes'][0].set_facecolor('lightblue')

    # Add reference line for population mean
    ax.axhline(popmean, color='red', linestyle='-', linewidth=2,
               label=f'H0: μ = {popmean}')

    # Add confidence interval
    ci = stats.t.interval(1 - result['alpha'], len(x) - 1,
                          loc=np.mean(x),
                          scale=stats.sem(x))
    ax.plot([0, 0], ci, 'b-', linewidth=3, label=f'{int((1-result["alpha"])*100)}% CI')

    ax.set_xticks([0])
    ax.set_xticklabels([var_x])
    ax.set_ylabel('Value')
    ax.set_title(
        f"One-sample t-test\n"
        f"t = {result['statistic']:.2f}, "
        f"p = {result['pvalue']:.4f} {result['stars']}\n"
        f"d = {result['effect_size']:.2f}, "
        f"power = {result.get('power', np.nan):.2f}"
    )
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')


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
        verbose=True
    )

    # Example 2: Non-significant difference
    logger.info("\n=== Example 2: Non-significant difference ===")

    x2 = np.random.normal(0, 1, 30)
    y2 = np.random.normal(0.2, 1, 30)  # Small effect

    result2 = test_ttest_ind(
        x2, y2,
        var_x='Group A',
        var_y='Group B',
        verbose=True
    )

    # Example 3: Welch's t-test (unequal variances)
    logger.info("\n=== Example 3: Welch's t-test ===")

    x3 = np.random.normal(0, 1, 40)
    y3 = np.random.normal(0.5, 2, 40)  # Different variance

    result3 = test_ttest_ind(
        x3, y3,
        var_x='Low Variance',
        var_y='High Variance',
        equal_var=False,
        verbose=True
    )

    # Example 4: One-sided test
    logger.info("\n=== Example 4: One-sided test ===")

    x4 = np.random.normal(0, 1, 50)
    y4 = np.random.normal(0.6, 1, 50)

    test_ttest_ind(x4, y4, alternative='two-sided', verbose=True)
    test_ttest_ind(x4, y4, alternative='less', verbose=True)

    # Example 5: With visualization
    logger.info("\n=== Example 5: With visualization ===")

    x5 = np.random.normal(10, 2, 60)
    y5 = np.random.normal(12, 2, 60)

    result5 = test_ttest_ind(
        x5, y5,
        var_x='Baseline',
        var_y='Follow-up',
        plot=True,
        verbose=True
    )
    stx.io.save(plt.gcf(), "./.dev/ttest_ind_example5.jpg")
    plt.close()

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
    logger.info(f"\n{df_all[['var_x', 'var_y', 'pvalue', 'stars', 'effect_size', 'power']]}")

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
