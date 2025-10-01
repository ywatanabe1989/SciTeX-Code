#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-01 19:00:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/stats/tests/categorical/_test_cochran_q.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/stats/tests/categorical/_test_cochran_q.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
  - Perform Cochran's Q test for binary repeated measures
  - Extension of McNemar's test to 3+ conditions
  - Test for differences in success proportions across conditions
  - Generate proportion visualizations

Dependencies:
  - packages: numpy, pandas, scipy, matplotlib

IO:
  - input: Binary data (subjects × conditions)
  - output: Test results (dict or DataFrame) and optional figure
"""

"""Imports"""
import argparse
import numpy as np
import pandas as pd
from typing import Union, Optional, Literal, Tuple, List
from scipy import stats
import scitex as stx
from scitex.logging import getLogger
from ...utils._formatters import p2stars
from ...utils._normalizers import convert_results

logger = getLogger(__name__)

try:
    import matplotlib
    import matplotlib.pyplot as plt
    HAS_PLT = True
except ImportError:
    HAS_PLT = False


def cochran_q_statistic(data: np.ndarray) -> Tuple[float, int]:
    """
    Compute Cochran's Q statistic.

    Parameters
    ----------
    data : array, shape (n_subjects, n_conditions)
        Binary data (0/1)

    Returns
    -------
    Q : float
        Cochran's Q statistic
    df : int
        Degrees of freedom

    Notes
    -----
    Q follows chi-square distribution with k-1 degrees of freedom.
    """
    n, k = data.shape

    # Column sums (successes per condition)
    G = data.sum(axis=0)

    # Row sums (successes per subject)
    L = data.sum(axis=1)

    # Total successes
    N = data.sum()

    # Cochran's Q
    numerator = (k - 1) * (k * np.sum(G ** 2) - N ** 2)
    denominator = k * N - np.sum(L ** 2)

    if denominator == 0:
        Q = 0.0
    else:
        Q = numerator / denominator

    df = k - 1

    return float(Q), int(df)


def effect_size_cochran(data: np.ndarray) -> float:
    """
    Compute effect size for Cochran's Q (Kendall's W for binary data).

    Parameters
    ----------
    data : array, shape (n_subjects, n_conditions)
        Binary data

    Returns
    -------
    W : float
        Effect size (0 to 1)
    """
    n, k = data.shape

    # Column sums
    G = data.sum(axis=0)

    # Mean column sum
    G_mean = G.mean()

    # Sum of squared deviations
    S = np.sum((G - G_mean) ** 2)

    # Kendall's W for binary data
    W = S / (n * (k - 1) * k / 12)

    # Bound between 0 and 1
    W = min(max(W, 0.0), 1.0)

    return float(W)


def interpret_effect_size(W: float) -> str:
    """Interpret Cochran's Q effect size."""
    if W < 0.1:
        return 'negligible'
    elif W < 0.3:
        return 'small'
    elif W < 0.5:
        return 'medium'
    else:
        return 'large'


def test_cochran_q(
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
    Perform Cochran's Q test for binary repeated measures.

    Extension of McNemar's test to 3+ conditions. Tests whether proportions
    of successes differ across multiple related binary measurements.

    Parameters
    ----------
    data : array or DataFrame
        - If array: shape (n_subjects, n_conditions), wide format with 0/1 values
        - If DataFrame with subject_col/condition_col: long format
        - If DataFrame without: wide format (rows=subjects, cols=conditions)
    subject_col : str, optional
        Column name for subject IDs (long format)
    condition_col : str, optional
        Column name for conditions (long format)
    value_col : str, optional
        Column name for binary values (long format)
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
        - statistic: Cochran's Q statistic
        - pvalue: p-value
        - df: Degrees of freedom (k - 1)
        - effect_size: Kendall's W
        - effect_size_interpretation: interpretation
        - n_subjects: Number of subjects
        - n_conditions: Number of conditions
        - proportions: Success proportion for each condition
        - n_successes: Number of successes per condition
        - significant: Whether to reject null hypothesis
        - stars: Significance stars

    If plot=True, returns tuple of (result, figure)

    Notes
    -----
    Cochran's Q test is used for repeated binary measurements (dichotomous data)
    on the same subjects across 3+ conditions.

    **Null Hypothesis (H0)**: Proportions of successes are equal across conditions

    **Alternative Hypothesis (H1)**: At least one proportion differs

    **Test Statistic**:

    .. math::
        Q = \\frac{(k-1)[k\\sum_{j=1}^{k}G_j^2 - N^2]}{k\\sum_{i=1}^{n}L_i - \\sum_{i=1}^{n}L_i^2}

    Where:
    - k: Number of conditions
    - n: Number of subjects
    - G_j: Number of successes in condition j
    - L_i: Number of successes for subject i (across conditions)
    - N: Total number of successes

    Q follows chi-square distribution with k-1 degrees of freedom.

    **Effect Size (Kendall's W for binary)**:

    .. math::
        W = \\frac{\\sum_{j=1}^{k}(G_j - \\bar{G})^2}{n(k-1)k/12}

    Interpretation:
    - W < 0.1: negligible
    - W < 0.3: small
    - W < 0.5: medium
    - W ≥ 0.5: large

    **Assumptions**:
    - Binary outcomes (0/1, success/failure, yes/no)
    - Repeated measurements on same subjects
    - At least 3 conditions (for 2 conditions, use McNemar's test)

    **Relation to other tests**:
    - Extension of McNemar's test (2 conditions → 3+ conditions)
    - Binary version of Friedman test
    - Can use Friedman test on same data (Q ≈ Friedman χ²)

    **Post-hoc tests**:
    If significant:
    - Pairwise McNemar tests
    - Apply corrections: correct_bonferroni(), correct_holm()

    **Advantages**:
    - Appropriate for binary repeated measures
    - No normality assumption
    - Accounts for within-subject correlation

    **Disadvantages**:
    - Requires binary data
    - Sensitive to subjects with all 0s or all 1s
    - Less powerful than parametric alternatives if assumptions met

    Examples
    --------
    >>> import numpy as np
    >>> from scitex.stats.tests.categorical import test_cochran_q
    >>>
    >>> # Example: Treatment success (0=fail, 1=success) across 4 visits
    >>> data = np.array([
    ...     [0, 0, 1, 1],  # Subject 1: improved over time
    ...     [0, 1, 1, 1],  # Subject 2: improved
    ...     [0, 0, 0, 1],  # Subject 3: late improvement
    ...     [1, 1, 1, 1],  # Subject 4: always success
    ...     [0, 0, 1, 1],  # Subject 5: improved
    ... ])
    >>>
    >>> result = test_cochran_q(
    ...     data,
    ...     condition_names=['Visit 1', 'Visit 2', 'Visit 3', 'Visit 4'],
    ...     plot=True
    ... )
    >>>
    >>> print(f"Q = {result['statistic']:.2f}, p = {result['pvalue']:.4f}")
    >>> print(f"Proportions: {result['proportions']}")

    References
    ----------
    .. [1] Cochran, W. G. (1950). "The comparison of percentages in matched
           samples". Biometrika, 37(3/4), 256-266.
    .. [2] McNemar, Q. (1947). "Note on the sampling error of the difference
           between correlated proportions or percentages". Psychometrika,
           12(2), 153-157.

    See Also
    --------
    test_mcnemar : For 2 binary conditions
    test_friedman : Non-parametric repeated measures (non-binary)
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
        raise ValueError("Cochran's Q requires at least 3 conditions. Use test_mcnemar for 2 conditions.")

    if n_subjects < 2:
        raise ValueError("Need at least 2 subjects")

    # Validate binary data
    unique_vals = np.unique(data_array)
    if not np.all(np.isin(unique_vals, [0, 1])):
        raise ValueError("Data must be binary (0 or 1)")

    if condition_names is None:
        condition_names = [f'Condition {i+1}' for i in range(n_conditions)]

    # Compute Cochran's Q statistic
    Q, df = cochran_q_statistic(data_array)

    # p-value from chi-square distribution
    pvalue = 1 - stats.chi2.cdf(Q, df)

    # Compute proportions and counts
    n_successes = data_array.sum(axis=0)
    proportions = n_successes / n_subjects

    # Compute effect size
    W = effect_size_cochran(data_array)
    W_interpretation = interpret_effect_size(W)

    # Build result dictionary
    result = {
        'test': "Cochran's Q test",
        'statistic': round(float(Q), decimals),
        'pvalue': round(float(pvalue), decimals + 1),
        'df': int(df),
        'effect_size': round(float(W), decimals),
        'effect_size_metric': 'kendall_w_binary',
        'effect_size_interpretation': W_interpretation,
        'n_subjects': int(n_subjects),
        'n_conditions': int(n_conditions),
        'condition_names': condition_names,
        'n_successes': [int(n) for n in n_successes],
        'proportions': [round(float(p), decimals) for p in proportions],
        'alpha': alpha,
        'significant': pvalue < alpha,
        'stars': p2stars(pvalue),
    }

    # Generate plot if requested
    fig = None
    if plot and HAS_PLT:
        fig = _plot_cochran_q(data_array, result, condition_names)

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


def _plot_cochran_q(data, result, condition_names):
    """Create visualization for Cochran's Q test."""
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    n_subjects, n_conditions = data.shape
    proportions = result['proportions']
    n_successes = result['n_successes']

    # Panel 1: Stacked bar chart (individual subjects)
    ax = axes[0]
    bottom = np.zeros(n_conditions)

    for i in range(n_subjects):
        ax.bar(range(n_conditions), data[i, :], bottom=bottom, alpha=0.7,
              edgecolor='black', linewidth=0.5)
        bottom += data[i, :]

    ax.set_xticks(range(n_conditions))
    ax.set_xticklabels(condition_names, rotation=45, ha='right')
    ax.set_xlabel('Condition')
    ax.set_ylabel('Cumulative Successes')
    ax.set_title('Individual Subject Patterns', fontweight='bold')
    ax.set_ylim([0, n_subjects])
    ax.grid(True, alpha=0.3, axis='y')

    # Panel 2: Proportion bar chart
    ax = axes[1]
    bars = ax.bar(range(n_conditions), proportions, color='steelblue',
                 alpha=0.7, edgecolor='black')

    # Add count labels
    for i, (bar, count) in enumerate(zip(bars, n_successes)):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
               f'{count}/{n_subjects}\n({proportions[i]:.1%})',
               ha='center', va='bottom')

    ax.set_xticks(range(n_conditions))
    ax.set_xticklabels(condition_names, rotation=45, ha='right')
    ax.set_xlabel('Condition')
    ax.set_ylabel('Proportion of Successes')
    ax.set_title('Success Proportions', fontweight='bold')
    ax.set_ylim([0, 1.0])
    ax.grid(True, alpha=0.3, axis='y')

    # Add overall mean line
    mean_prop = np.mean(proportions)
    ax.axhline(y=mean_prop, color='red', linestyle='--', alpha=0.5,
              label=f'Mean: {mean_prop:.2%}')
    ax.legend()

    # Panel 3: Results summary
    ax = axes[2]
    ax.axis('off')

    result_text = "Cochran's Q Test\n"
    result_text += "=" * 30 + "\n\n"
    result_text += f"Q = {result['statistic']:.3f}\n"
    result_text += f"df = {result['df']}\n"
    result_text += f"p-value = {result['pvalue']:.4f} {result['stars']}\n\n"
    result_text += f"Effect size (W) = {result['effect_size']:.3f}\n"
    result_text += f"Interpretation:\n  {result['effect_size_interpretation']}\n\n"
    result_text += f"Subjects: {result['n_subjects']}\n"
    result_text += f"Conditions: {result['n_conditions']}\n\n"
    result_text += "Success proportions:\n"
    for name, prop, count in zip(condition_names, proportions, n_successes):
        result_text += f"  {name}: {prop:.1%} ({count}/{n_subjects})\n"
    result_text += f"\nSignificant (α={result['alpha']}): "
    result_text += "Yes" if result['significant'] else "No"

    ax.text(0.1, 0.5, result_text,
           transform=ax.transAxes,
           verticalalignment='center',
           fontfamily='monospace',
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

    plt.tight_layout()
    return fig

"""Main function"""
def main(args):




    logger.info("=" * 70)
    logger.info("Cochran's Q Test Examples")
    logger.info("=" * 70)

    # Example 1: Treatment success over time
    logger.info("\n[Example 1] Treatment success (0/1) across 4 visits")
    logger.info("-" * 70)

    np.random.seed(42)
    # Simulate improving success rate over time
    data = np.array([
        [0, 0, 1, 1],
        [0, 1, 1, 1],
        [0, 0, 0, 1],
        [1, 1, 1, 1],
        [0, 0, 1, 1],
        [0, 1, 1, 1],
        [0, 0, 1, 1],
        [0, 1, 0, 1],
        [1, 1, 1, 1],
        [0, 0, 0, 1],
    ])

    result, _ = test_cochran_q(
        data,
        condition_names=['Visit 1', 'Visit 2', 'Visit 3', 'Visit 4'],
        plot=True
    )

    logger.info(f"Q = {result['statistic']:.3f}, p = {result['pvalue']:.4f} {result['stars']}")
    logger.info(f"Effect size (W) = {result['effect_size']:.3f} ({result['effect_size_interpretation']})")
    logger.info(f"Proportions: {[f'{p:.1%}' for p in result['proportions']]}")
    stx.io.save(plt.gcf(), "./.dev/cochran_q_example1.jpg")
    plt.close()

    # Example 2: Symptom presence (binary)
    logger.info("\n[Example 2] Symptom presence across 3 time points")
    logger.info("-" * 70)

    symptom_data = np.array([
        [1, 1, 0],
        [1, 0, 0],
        [1, 1, 1],
        [1, 1, 0],
        [1, 0, 0],
        [1, 1, 0],
        [0, 0, 0],
        [1, 1, 1],
    ])

    result_symptom, _ = test_cochran_q(
        symptom_data,
        condition_names=['Baseline', 'Week 2', 'Week 4'],
        plot=True
    )

    logger.info(f"Q({result_symptom['df']}) = {result_symptom['statistic']:.3f}")
    logger.info(f"p-value = {result_symptom['pvalue']:.4f}")
    stx.io.save(plt.gcf(), "./.dev/cochran_q_example2.jpg")
    plt.close()

    # Example 3: Comparison with Friedman test
    logger.info("\n[Example 3] Comparison: Cochran Q vs Friedman")
    logger.info("-" * 70)

    from ..nonparametric import test_friedman

    result_cochran = test_cochran_q(data)
    result_friedman = test_friedman(data.astype(float))

    logger.info(f"Cochran's Q:    Q = {result_cochran['statistic']:.3f}, p = {result_cochran['pvalue']:.4f}")
    logger.info(f"Friedman test:  χ² = {result_friedman['statistic']:.3f}, p = {result_friedman['pvalue']:.4f}")
    logger.info(f"Note: For binary data, both tests are similar")

    # Example 4: Long format DataFrame
    logger.info("\n[Example 4] Long format DataFrame input")
    logger.info("-" * 70)

    subjects = np.repeat(np.arange(10), 3)
    conditions = np.tile(['Pre', 'Mid', 'Post'], 10)
    values = np.random.binomial(1, [0.3, 0.5, 0.7] * 10)

    df_long = pd.DataFrame({
        'Subject': subjects,
        'TimePoint': conditions,
        'Success': values
    })

    result_long, _ = test_cochran_q(
        df_long,
        subject_col='Subject',
        condition_col='TimePoint',
        value_col='Success',
        plot=True
    )

    logger.info(f"Q = {result_long['statistic']:.3f}, p = {result_long['pvalue']:.4f}")
    stx.io.save(plt.gcf(), "./.dev/cochran_q_example4.jpg")
    plt.close()

    # Example 5: Export results
    logger.info("\n[Example 5] Export results")
    logger.info("-" * 70)

    df_result = convert_results(result, return_as='dataframe')
    df_result.to_excel('./cochran_q_results.xlsx', index=False)
    logger.info("Saved to: ./cochran_q_results.xlsx")


    return 0

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    return parser.parse_args()


def run_main():
    """Initialize SciTeX framework and run main."""
    global CONFIG, CC, sys, plt, rng

    import sys
    import matplotlib.pyplot as plt

    args = parse_args()

    CONFIG, sys.stdout, sys.stderr, plt, CC, rng = stx.session.start(
        sys,
        plt,
        args=args,
        file=__FILE__,
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
