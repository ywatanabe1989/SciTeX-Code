#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-01 18:30:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/stats/tests/nonparametric/_test_friedman.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/stats/tests/nonparametric/_test_friedman.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
  - Perform Friedman test for repeated measures (non-parametric)
  - Non-parametric alternative to repeated measures ANOVA
  - Test differences across 3+ related samples
  - Compute Kendall's W (coefficient of concordance)
  - Generate rank-based visualizations

Dependencies:
  - packages: numpy, pandas, scipy, matplotlib

IO:
  - input: Data in wide or long format (subjects × conditions)
  - output: Test results (dict or DataFrame) and optional figure
"""

"""Imports"""
import numpy as np
import pandas as pd
from typing import Union, Optional, Literal, Tuple, List
from scipy import stats
from ...utils._formatters import p2stars
from ...utils._normalizers import convert_results

try:
    import matplotlib
    import matplotlib.pyplot as plt
    HAS_PLT = True
except ImportError:
    HAS_PLT = False


def kendall_w(ranks: np.ndarray) -> float:
    """
    Compute Kendall's W (coefficient of concordance).

    Parameters
    ----------
    ranks : array, shape (n_subjects, n_conditions)
        Rank matrix

    Returns
    -------
    W : float
        Kendall's W (0 to 1)

    Notes
    -----
    W = 0: No agreement among subjects
    W = 1: Complete agreement among subjects
    """
    n, k = ranks.shape

    # Sum of ranks for each condition
    R = ranks.sum(axis=0)

    # Mean of rank sums
    R_mean = R.mean()

    # Sum of squared deviations
    S = np.sum((R - R_mean) ** 2)

    # Kendall's W
    W = (12 * S) / (n ** 2 * (k ** 3 - k))

    return float(W)


def interpret_kendall_w(W: float) -> str:
    """Interpret Kendall's W effect size."""
    if W < 0.1:
        return 'negligible agreement'
    elif W < 0.3:
        return 'weak agreement'
    elif W < 0.5:
        return 'moderate agreement'
    elif W < 0.7:
        return 'strong agreement'
    else:
        return 'very strong agreement'


def test_friedman(
    data: Union[np.ndarray, pd.DataFrame],
    subject_col: Optional[str] = None,
    condition_col: Optional[str] = None,
    value_col: Optional[str] = None,
    condition_names: Optional[List[str]] = None,
    alpha: float = 0.05,
    plot: bool = False,
    return_as: Literal['dict', 'dataframe'] = 'dict',
    decimals: int = 3
) -> Union[dict, pd.DataFrame, Tuple]:
    """
    Perform Friedman test for repeated measures (non-parametric).

    Non-parametric alternative to repeated measures ANOVA. Tests whether
    distributions differ across 3+ related samples using ranks.

    Parameters
    ----------
    data : array or DataFrame
        - If array: shape (n_subjects, n_conditions), wide format
        - If DataFrame with subject_col/condition_col: long format
        - If DataFrame without: wide format (rows=subjects, cols=conditions)
    subject_col : str, optional
        Column name for subject IDs (long format)
    condition_col : str, optional
        Column name for conditions (long format)
    value_col : str, optional
        Column name for values (long format)
    condition_names : list of str, optional
        Names for conditions (wide format)
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
    result : dict or DataFrame
        Test results including:
        - statistic: Chi-square statistic (Friedman's χ²)
        - pvalue: p-value
        - df: Degrees of freedom (k - 1)
        - kendall_w: Kendall's W (coefficient of concordance)
        - effect_size: Kendall's W
        - effect_size_interpretation: interpretation
        - n_subjects: Number of subjects
        - n_conditions: Number of conditions
        - mean_ranks: Mean rank for each condition
        - rejected: Whether to reject null hypothesis
        - significant: Same as rejected

    If plot=True, returns tuple of (result, figure)

    Notes
    -----
    The Friedman test is the non-parametric alternative to repeated measures
    ANOVA. It is used when:
    - Normality assumption is violated
    - Data are ordinal (e.g., Likert scales)
    - Sample sizes are small

    **Null Hypothesis (H0)**: All conditions have the same distribution

    **Alternative Hypothesis (H1)**: At least one condition differs

    **Procedure**:
    1. Rank observations within each subject (across conditions)
    2. Compute sum of ranks for each condition
    3. Calculate test statistic based on rank sums

    **Test Statistic**:

    .. math::
        \\chi^2_F = \\frac{12}{nk(k+1)} \\sum_{j=1}^{k} R_j^2 - 3n(k+1)

    Where:
    - n: Number of subjects
    - k: Number of conditions
    - R_j: Sum of ranks for condition j

    **Effect Size (Kendall's W)**:

    .. math::
        W = \\frac{12 \\sum_{j=1}^{k}(R_j - \\bar{R})^2}{n^2(k^3 - k)}

    Interpretation:
    - W < 0.1: negligible agreement
    - W < 0.3: weak agreement
    - W < 0.5: moderate agreement
    - W < 0.7: strong agreement
    - W ≥ 0.7: very strong agreement

    **Assumptions**:
    - Paired/repeated observations (same subjects)
    - At least ordinal scale data
    - 3+ conditions (for 2 conditions, use Wilcoxon signed-rank test)

    **Post-hoc tests**:
    If significant:
    - Pairwise Wilcoxon signed-rank tests
    - Apply corrections: correct_bonferroni(), correct_holm()

    **Advantages**:
    - No normality assumption
    - Robust to outliers
    - Works with ordinal data
    - No sphericity assumption

    **Disadvantages**:
    - Less powerful than RM-ANOVA when assumptions are met
    - Requires at least ordinal data
    - Sensitive to ties

    Examples
    --------
    >>> import numpy as np
    >>> from scitex.stats.tests.nonparametric import test_friedman
    >>>
    >>> # Example: Pain ratings (ordinal) across 4 time points
    >>> data = np.array([
    ...     [7, 6, 5, 4],  # Subject 1
    ...     [8, 7, 6, 5],  # Subject 2
    ...     [6, 5, 4, 3],  # Subject 3
    ...     [9, 8, 7, 6],  # Subject 4
    ... ])
    >>>
    >>> result = test_friedman(
    ...     data,
    ...     condition_names=['Baseline', '1 week', '2 weeks', '3 weeks'],
    ...     plot=True
    ... )
    >>>
    >>> print(f"χ² = {result['statistic']:.2f}, p = {result['pvalue']:.4f}")
    >>> print(f"Kendall's W = {result['kendall_w']:.3f}")

    References
    ----------
    .. [1] Friedman, M. (1937). "The use of ranks to avoid the assumption of
           normality implicit in the analysis of variance". Journal of the
           American Statistical Association, 32(200), 675-701.
    .. [2] Kendall, M. G., & Babington Smith, B. (1939). "The problem of m
           rankings". The Annals of Mathematical Statistics, 10(3), 275-287.

    See Also
    --------
    test_anova_rm : Parametric alternative (repeated measures ANOVA)
    test_wilcoxon : For 2 related samples
    test_kruskal : For 3+ independent samples
    """
    # Convert data to wide format array
    if isinstance(data, pd.DataFrame):
        if subject_col is not None and condition_col is not None and value_col is not None:
            # Long format - pivot to wide
            data_wide = data.pivot(index=subject_col, columns=condition_col, values=value_col)
            data_array = data_wide.values
            if condition_names is None:
                condition_names = list(data_wide.columns)
        else:
            # Already wide format
            data_array = data.values
            if condition_names is None:
                condition_names = list(data.columns)
    else:
        data_array = np.asarray(data)
        if data_array.ndim != 2:
            raise ValueError("Data must be 2D (subjects × conditions)")

    n_subjects, n_conditions = data_array.shape

    if n_conditions < 3:
        raise ValueError("Friedman test requires at least 3 conditions. Use test_wilcoxon for 2 conditions.")

    if n_subjects < 2:
        raise ValueError("Need at least 2 subjects")

    if condition_names is None:
        condition_names = [f'Condition {i+1}' for i in range(n_conditions)]

    # Perform Friedman test
    statistic, pvalue = stats.friedmanchisquare(*data_array.T)

    # Compute ranks for each subject (across conditions)
    ranks = np.zeros_like(data_array)
    for i in range(n_subjects):
        ranks[i, :] = stats.rankdata(data_array[i, :])

    # Compute mean ranks for each condition
    mean_ranks = ranks.mean(axis=0)

    # Compute Kendall's W
    W = kendall_w(ranks)
    W_interpretation = interpret_kendall_w(W)

    # Degrees of freedom
    df = n_conditions - 1

    # Build result dictionary
    result = {
        'test': 'Friedman test',
        'statistic': round(float(statistic), decimals),
        'pvalue': round(float(pvalue), decimals + 1),
        'df': int(df),
        'kendall_w': round(float(W), decimals),
        'effect_size': round(float(W), decimals),
        'effect_size_metric': 'kendall_w',
        'effect_size_interpretation': W_interpretation,
        'n_subjects': int(n_subjects),
        'n_conditions': int(n_conditions),
        'condition_names': condition_names,
        'mean_ranks': [round(float(r), decimals) for r in mean_ranks],
        'alpha': alpha,
        'rejected': pvalue < alpha,
        'significant': pvalue < alpha,
        'pstars': p2stars(pvalue),
    }

    # Generate plot if requested
    fig = None
    if plot and HAS_PLT:
        fig = _plot_friedman(data_array, ranks, result, condition_names)

    # Return based on format
    if return_as == 'dataframe':
        result_df = pd.DataFrame([result])
        if plot and fig is not None:
            return result_df, fig
        return result_df
    else:
        if plot and fig is not None:
            return result, fig
        return result


def _plot_friedman(data, ranks, result, condition_names):
    """Create visualization for Friedman test."""
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    n_subjects, n_conditions = data.shape
    conditions = np.arange(n_conditions)

    # Panel 1: Original data - box plots
    ax = axes[0, 0]
    data_list = [data[:, i] for i in range(n_conditions)]
    bp = ax.boxplot(data_list, positions=conditions + 1, widths=0.6, patch_artist=True)

    for patch in bp['boxes']:
        patch.set_facecolor('lightblue')
        patch.set_alpha(0.7)

    ax.set_xticks(conditions + 1)
    ax.set_xticklabels(condition_names, rotation=45, ha='right')
    ax.set_xlabel('Condition', fontsize=12)
    ax.set_ylabel('Value', fontsize=12)
    ax.set_title('Original Data Distribution', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')

    # Panel 2: Rank data - box plots
    ax = axes[0, 1]
    ranks_list = [ranks[:, i] for i in range(n_conditions)]
    bp = ax.boxplot(ranks_list, positions=conditions + 1, widths=0.6, patch_artist=True)

    for patch in bp['boxes']:
        patch.set_facecolor('lightcoral')
        patch.set_alpha(0.7)

    ax.set_xticks(conditions + 1)
    ax.set_xticklabels(condition_names, rotation=45, ha='right')
    ax.set_xlabel('Condition', fontsize=12)
    ax.set_ylabel('Rank', fontsize=12)
    ax.set_title('Rank Distribution', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')

    # Panel 3: Mean ranks bar plot
    ax = axes[1, 0]
    mean_ranks = result['mean_ranks']
    bars = ax.bar(conditions, mean_ranks, color='steelblue', alpha=0.7, edgecolor='black')

    # Add value labels on bars
    for i, (bar, rank) in enumerate(zip(bars, mean_ranks)):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
               f'{rank:.2f}',
               ha='center', va='bottom', fontsize=10, fontweight='bold')

    ax.set_xticks(conditions)
    ax.set_xticklabels(condition_names, rotation=45, ha='right')
    ax.set_xlabel('Condition', fontsize=12)
    ax.set_ylabel('Mean Rank', fontsize=12)
    ax.set_title('Mean Ranks by Condition', fontsize=12, fontweight='bold')
    ax.axhline(y=np.mean(mean_ranks), color='red', linestyle='--', alpha=0.5, label='Expected (no effect)')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')

    # Panel 4: Results summary
    ax = axes[1, 1]
    ax.axis('off')

    result_text = "Friedman Test Results\n"
    result_text += "=" * 30 + "\n\n"
    result_text += f"χ² = {result['statistic']:.3f}\n"
    result_text += f"df = {result['df']}\n"
    result_text += f"p-value = {result['pvalue']:.4f} {result['pstars']}\n\n"
    result_text += f"Kendall's W = {result['kendall_w']:.3f}\n"
    result_text += f"Interpretation:\n  {result['effect_size_interpretation']}\n\n"
    result_text += f"Subjects: {result['n_subjects']}\n"
    result_text += f"Conditions: {result['n_conditions']}\n\n"
    result_text += f"Mean Ranks:\n"
    for name, rank in zip(condition_names, mean_ranks):
        result_text += f"  {name}: {rank:.2f}\n"
    result_text += f"\nSignificant (α={result['alpha']}): "
    result_text += "Yes" if result['significant'] else "No"

    ax.text(0.1, 0.5, result_text,
           transform=ax.transAxes,
           fontsize=10,
           verticalalignment='center',
           fontfamily='monospace',
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

    plt.tight_layout()
    return fig


if __name__ == "__main__":
    import sys
    import argparse
    import scitex as stx

    parser = argparse.ArgumentParser()
    args = parser.parse_args([])

    CONFIG, sys.stdout, sys.stderr, plt, CC, rng = stx.session.start(
        sys=sys,
        plt=plt,
        args=args,
        file=__FILE__,
        verbose=True,
        agg=True,
    )

    logger = stx.logging.getLogger(__name__)

    logger.info("=" * 70)
    logger.info("Friedman Test Examples")
    logger.info("=" * 70)

    # Example 1: Pain ratings (ordinal data)
    logger.info("\n[Example 1] Pain ratings across 4 time points (ordinal)")
    logger.info("-" * 70)

    np.random.seed(42)
    # Simulate decreasing pain over time
    pain_data = np.array([
        [7, 6, 5, 4],
        [8, 7, 6, 5],
        [6, 5, 4, 3],
        [9, 8, 7, 6],
        [7, 6, 5, 4],
        [8, 7, 6, 5],
        [6, 5, 5, 4],
        [7, 6, 5, 5],
    ])

    result = test_friedman(
        pain_data,
        condition_names=['Baseline', 'Week 1', 'Week 2', 'Week 3'],
        plot=True
    )

    logger.info(f"χ² = {result['statistic']:.3f}, p = {result['pvalue']:.4f} {result['pstars']}")
    logger.info(f"Kendall's W = {result['kendall_w']:.3f} ({result['effect_size_interpretation']})")
    logger.info(f"Mean ranks: {result['mean_ranks']}")

    # Example 2: Likert scale ratings
    logger.info("\n[Example 2] Likert scale ratings (1-5) for 4 products")
    logger.info("-" * 70)

    likert_data = np.array([
        [3, 4, 5, 3],
        [2, 3, 4, 2],
        [4, 5, 5, 4],
        [3, 4, 4, 3],
        [2, 3, 5, 2],
        [3, 4, 4, 3],
        [4, 5, 5, 4],
        [3, 3, 4, 3],
        [2, 4, 5, 3],
        [3, 4, 4, 2],
    ])

    result_likert = test_friedman(
        likert_data,
        condition_names=['Product A', 'Product B', 'Product C', 'Product D'],
        plot=True
    )

    logger.info(f"χ²({result_likert['df']}) = {result_likert['statistic']:.3f}")
    logger.info(f"p-value = {result_likert['pvalue']:.4f}")
    logger.info(f"Kendall's W = {result_likert['kendall_w']:.3f}")

    # Example 3: Long format DataFrame
    logger.info("\n[Example 3] Long format DataFrame input")
    logger.info("-" * 70)

    subjects = np.repeat(np.arange(8), 4)
    conditions = np.tile(['Pre', 'Mid1', 'Mid2', 'Post'], 8)
    values = np.random.randint(1, 11, 32)  # Random scores 1-10

    df_long = pd.DataFrame({
        'Subject': subjects,
        'TimePoint': conditions,
        'Score': values
    })

    result_long = test_friedman(
        df_long,
        subject_col='Subject',
        condition_col='TimePoint',
        value_col='Score',
        plot=True
    )

    logger.info(f"χ² = {result_long['statistic']:.3f}, p = {result_long['pvalue']:.4f}")

    # Example 4: Comparison with RM-ANOVA
    logger.info("\n[Example 4] Comparison: Friedman vs RM-ANOVA")
    logger.info("-" * 70)

    from ..parametric import test_anova_rm

    # Data with outliers
    data_outlier = np.random.normal(5, 1, (10, 4))
    data_outlier[0, 0] = 20  # Add outlier

    result_friedman = test_friedman(data_outlier)
    result_rm_anova = test_anova_rm(data_outlier)

    logger.info(f"Friedman: χ² = {result_friedman['statistic']:.3f}, p = {result_friedman['pvalue']:.4f}")
    logger.info(f"RM-ANOVA: F = {result_rm_anova['statistic']:.3f}, p = {result_rm_anova['pvalue']:.4f}")
    logger.info(f"Note: Friedman is more robust to outliers")

    # Example 5: Export results
    logger.info("\n[Example 5] Export results")
    logger.info("-" * 70)

    convert_results(result, return_as='excel', path='./friedman_results.xlsx')
    logger.info("Saved to: ./friedman_results.xlsx")

    stx.session.close(
        CONFIG,
        verbose=False,
        notify=False,
        exit_status=0,
    )

# EOF
