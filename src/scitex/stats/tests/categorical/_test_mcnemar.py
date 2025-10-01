#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-01 16:30:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/stats/tests/categorical/_test_mcnemar.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/stats/tests/categorical/_test_mcnemar.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
  - McNemar's test for paired categorical data
  - Test for marginal homogeneity in 2×2 contingency tables
  - Compute odds ratio for matched pairs
  - Generate visualizations for paired outcomes

Dependencies:
  - packages: numpy, pandas, scipy, matplotlib

IO:
  - input: 2×2 contingency table (array or DataFrame)
  - output: Test results (dict or DataFrame) and optional figure
"""

"""Imports"""
from typing import Union, Optional, Literal, Tuple
import numpy as np
import pandas as pd
from scipy import stats
from ...utils._formatters import p2stars
from ...utils._normalizers import force_dataframe, convert_results

try:
    import matplotlib
    import matplotlib.pyplot as plt
    HAS_PLT = True
except ImportError:
    HAS_PLT = False


def mcnemar_odds_ratio(b: int, c: int) -> float:
    """
    Compute odds ratio for McNemar's test from discordant pairs.

    Parameters
    ----------
    b : int
        Count in cell [0,1] (success before, failure after)
    c : int
        Count in cell [1,0] (failure before, success after)

    Returns
    -------
    or_val : float
        Odds ratio = b / c

    Notes
    -----
    For McNemar's test, OR = b/c where b and c are the discordant pairs.
    OR > 1 indicates more b than c (positive change)
    OR < 1 indicates more c than b (negative change)
    OR = 1 indicates no change
    """
    if c == 0:
        if b == 0:
            return 1.0  # No discordant pairs
        return float('inf')  # Only b discordant pairs
    return float(b / c)


def interpret_mcnemar_or(or_val: float) -> str:
    """
    Interpret McNemar's odds ratio.

    Parameters
    ----------
    or_val : float
        Odds ratio

    Returns
    -------
    interpretation : str
        Interpretation
    """
    if or_val == 1.0:
        return 'no change'
    elif or_val > 1.0:
        if or_val < 2.0:
            return 'small increase'
        elif or_val < 4.0:
            return 'medium increase'
        else:
            return 'large increase'
    else:  # or_val < 1.0
        if or_val > 0.5:
            return 'small decrease'
        elif or_val > 0.25:
            return 'medium decrease'
        else:
            return 'large decrease'


def test_mcnemar(
    observed: Union[np.ndarray, pd.DataFrame, list],
    var_before: Optional[str] = None,
    var_after: Optional[str] = None,
    correction: bool = True,
    alpha: float = 0.05,
    plot: bool = False,
    return_as: Literal['dict', 'dataframe'] = 'dict',
    decimals: int = 3
) -> Union[dict, pd.DataFrame, Tuple]:
    """
    Perform McNemar's test for paired categorical data.

    Tests whether there is a significant change in proportions for paired binary data.
    Appropriate for before-after studies with binary outcomes.

    Parameters
    ----------
    observed : array-like, shape (2, 2)
        2×2 contingency table:
        [[a, b],
         [c, d]]
        where:
        - a: both conditions negative (0,0)
        - b: before negative, after positive (0,1)
        - c: before positive, after negative (1,0)
        - d: both conditions positive (1,1)
    var_before : str, optional
        Name for before condition
    var_after : str, optional
        Name for after condition
    correction : bool, default True
        Whether to apply continuity correction (recommended for small samples)
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
        - statistic: χ² statistic
        - pvalue: p-value
        - df: degrees of freedom (always 1)
        - b: count of (before=0, after=1)
        - c: count of (before=1, after=0)
        - odds_ratio: b / c
        - effect_size: odds ratio
        - effect_size_interpretation: interpretation
        - rejected: whether to reject null hypothesis
        - significant: same as rejected
        - pstars: significance stars

    If plot=True, returns tuple of (result, figure)

    Notes
    -----
    McNemar's test is used for paired nominal data, testing whether row and column
    marginal frequencies are equal (marginal homogeneity).

    The test statistic is based on the discordant pairs (b and c):

    .. math::
        \\chi^2 = \\frac{(b - c)^2}{b + c}  \\quad \\text{(without correction)}

    .. math::
        \\chi^2 = \\frac{(|b - c| - 1)^2}{b + c}  \\quad \\text{(with correction)}

    **Null hypothesis:** The marginal proportions are equal (no change)
    **Alternative:** The marginal proportions differ (significant change)

    **Assumptions:**
    - Paired data (matched observations)
    - Binary outcomes for both conditions
    - Large enough sample (b + c ≥ 10 recommended for chi-square approximation)

    **Effect size (Odds Ratio):**
    OR = b / c
    - OR = 1: no change
    - OR > 1: increase (more transitions from 0→1 than 1→0)
    - OR < 1: decrease (more transitions from 1→0 than 0→1)

    Examples
    --------
    >>> import numpy as np
    >>> from scitex.stats.tests.categorical import test_mcnemar
    >>>
    >>> # Example: Treatment effectiveness (before/after)
    >>> # Rows: before, Columns: after
    >>> # [[no→no, no→yes],
    >>> #  [yes→no, yes→yes]]
    >>> observed = [[59, 6],   # 59 stayed negative, 6 improved
    ...             [16, 19]]  # 16 relapsed, 19 stayed positive
    >>>
    >>> result = test_mcnemar(observed, var_before='Before Treatment',
    ...                       var_after='After Treatment', plot=True)
    >>> print(f"χ² = {result['statistic']:.2f}, p = {result['pvalue']:.4f}")
    >>> print(f"Odds Ratio = {result['odds_ratio']:.2f}")

    References
    ----------
    .. [1] McNemar, Q. (1947). "Note on the sampling error of the difference between
           correlated proportions or percentages". Psychometrika, 12(2), 153-157.
    .. [2] Edwards, A. L. (1948). "Note on the correction for continuity in testing
           the significance of the difference between correlated proportions".
           Psychometrika, 13(3), 185-187.

    See Also
    --------
    test_chi2 : For independent (unpaired) categorical data
    test_fisher : For 2×2 tables with small expected frequencies
    """
    # Convert to numpy array
    if isinstance(observed, pd.DataFrame):
        observed_array = observed.values
    elif isinstance(observed, list):
        observed_array = np.array(observed)
    else:
        observed_array = np.asarray(observed)

    # Validate shape
    if observed_array.shape != (2, 2):
        raise ValueError(f"McNemar's test requires a 2×2 table, got shape {observed_array.shape}")

    # Extract cells
    a, b = observed_array[0]
    c, d = observed_array[1]

    # Validate data types
    if not all(isinstance(x, (int, np.integer)) or (isinstance(x, (float, np.floating)) and x == int(x))
              for x in [a, b, c, d]):
        raise ValueError("All values must be non-negative integers (counts)")

    if any(x < 0 for x in [a, b, c, d]):
        raise ValueError("All counts must be non-negative")

    a, b, c, d = int(a), int(b), int(c), int(d)

    # Perform McNemar's test
    # scipy.stats.contingency.mcnemar is not available in older scipy
    # We'll compute manually
    n_discordant = b + c

    if n_discordant == 0:
        # No discordant pairs - perfect agreement
        statistic = 0.0
        pvalue = 1.0
    else:
        if correction:
            # With continuity correction
            statistic = (abs(b - c) - 1.0) ** 2 / n_discordant
        else:
            # Without continuity correction
            statistic = (b - c) ** 2 / n_discordant

        # p-value from chi-square distribution with df=1
        pvalue = 1.0 - stats.chi2.cdf(statistic, df=1)

    # Compute odds ratio
    odds_ratio = mcnemar_odds_ratio(b, c)
    or_interpretation = interpret_mcnemar_or(odds_ratio)

    # Variable names
    var_before = var_before or 'Before'
    var_after = var_after or 'After'

    # Build result dictionary
    result = {
        'test': "McNemar's test",
        'var_before': var_before,
        'var_after': var_after,
        'statistic': round(float(statistic), decimals),
        'pvalue': round(float(pvalue), decimals + 1),
        'df': 1,
        'b': int(b),  # Changed (0→1)
        'c': int(c),  # Changed (1→0)
        'n_discordant': int(n_discordant),
        'odds_ratio': round(float(odds_ratio), decimals) if np.isfinite(odds_ratio) else odds_ratio,
        'effect_size': round(float(odds_ratio), decimals) if np.isfinite(odds_ratio) else odds_ratio,
        'effect_size_interpretation': or_interpretation,
        'correction': correction,
        'alpha': alpha,
        'rejected': pvalue < alpha,
        'significant': pvalue < alpha,
        'pstars': p2stars(pvalue),
    }

    # Generate plot if requested
    fig = None
    if plot and HAS_PLT:
        fig = _plot_mcnemar(observed_array, result, var_before, var_after)

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


def _plot_mcnemar(observed, result, var_before, var_after):
    """Create visualization for McNemar's test."""
    fig, axes = plt.subplots(1, 3, figsize=(12, 4))

    a, b = observed[0]
    c, d = observed[1]

    # Panel 1: Contingency table heatmap
    ax = axes[0]
    im = ax.imshow(observed, cmap='Blues', aspect='auto')

    # Add text annotations
    for i in range(2):
        for j in range(2):
            text = ax.text(j, i, int(observed[i, j]),
                          ha="center", va="center", color="black", fontsize=14)

    ax.set_xticks([0, 1])
    ax.set_yticks([0, 1])
    ax.set_xticklabels(['0', '1'])
    ax.set_yticklabels(['0', '1'])
    ax.set_xlabel(f'{var_after}', fontsize=12)
    ax.set_ylabel(f'{var_before}', fontsize=12)
    ax.set_title('Contingency Table', fontsize=12, fontweight='bold')

    # Add colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Frequency', rotation=270, labelpad=15)

    # Panel 2: Discordant pairs comparison
    ax = axes[1]
    categories = ['0→1\n(b)', '1→0\n(c)']
    counts = [b, c]
    colors = ['lightblue', 'lightcoral']

    bars = ax.bar(categories, counts, color=colors, edgecolor='black', alpha=0.7)

    # Add count labels
    for bar, count in zip(bars, counts):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
               f'{int(count)}',
               ha='center', va='bottom', fontsize=12, fontweight='bold')

    ax.set_ylabel('Count', fontsize=12)
    ax.set_title('Discordant Pairs', fontsize=12, fontweight='bold')
    ax.set_ylim(0, max(counts) * 1.2 if max(counts) > 0 else 1)

    # Add grid
    ax.yaxis.grid(True, alpha=0.3)
    ax.set_axisbelow(True)

    # Panel 3: Results summary
    ax = axes[2]
    ax.axis('off')

    # Create result text
    result_text = f"McNemar's Test Results\n"
    result_text += "=" * 30 + "\n\n"
    result_text += f"χ² = {result['statistic']:.3f}\n"
    result_text += f"df = {result['df']}\n"
    result_text += f"p-value = {result['pvalue']:.4f} {result['pstars']}\n\n"
    result_text += f"Discordant pairs:\n"
    result_text += f"  b (0→1) = {result['b']}\n"
    result_text += f"  c (1→0) = {result['c']}\n"
    result_text += f"  Total = {result['n_discordant']}\n\n"

    if np.isfinite(result['odds_ratio']):
        result_text += f"Odds Ratio = {result['odds_ratio']:.3f}\n"
        result_text += f"Interpretation: {result['effect_size_interpretation']}\n\n"
    else:
        result_text += f"Odds Ratio = ∞\n"
        result_text += f"(All changes in one direction)\n\n"

    result_text += f"Correction: {result['correction']}\n"
    result_text += f"Significant (α={result['alpha']}): "
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

    # Parse empty args
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
    logger.info("McNemar's Test Examples")
    logger.info("=" * 70)

    # Example 1: Treatment effectiveness
    logger.info("\n[Example 1] Treatment effectiveness (before/after)")
    logger.info("-" * 70)

    observed = [[59, 6],   # No disease before: stayed negative (59), became positive (6)
                [16, 19]]  # Disease before: became negative (16), stayed positive (19)

    result = test_mcnemar(
        observed,
        var_before='Before Treatment',
        var_after='After Treatment',
        plot=True
    )

    logger.info(f"Contingency table:")
    logger.info(f"  [[{observed[0][0]}, {observed[0][1]}],")
    logger.info(f"   [{observed[1][0]}, {observed[1][1]}]]")
    logger.info(f"\nχ² = {result['statistic']:.3f}, p = {result['pvalue']:.4f} {result['pstars']}")
    logger.info(f"Discordant pairs: b={result['b']}, c={result['c']}")
    logger.info(f"Odds Ratio = {result['odds_ratio']:.3f} ({result['effect_size_interpretation']})")
    logger.info(f"Significant: {result['significant']}")

    # Example 2: No change (null case)
    logger.info("\n[Example 2] No change (equal discordant pairs)")
    logger.info("-" * 70)

    observed_null = [[40, 10],
                     [10, 40]]

    result_null = test_mcnemar(observed_null, plot=True)

    logger.info(f"b = {result_null['b']}, c = {result_null['c']}")
    logger.info(f"Odds Ratio = {result_null['odds_ratio']:.3f}")
    logger.info(f"p-value = {result_null['pvalue']:.4f}")
    logger.info(f"Result: No significant change (as expected)")

    # Example 3: Strong effect
    logger.info("\n[Example 3] Strong treatment effect")
    logger.info("-" * 70)

    observed_strong = [[50, 25],   # Many improved (0→1)
                       [2, 23]]    # Few relapsed (1→0)

    result_strong = test_mcnemar(observed_strong, plot=True)

    logger.info(f"Improvement: {result_strong['b']} patients")
    logger.info(f"Relapse: {result_strong['c']} patients")
    logger.info(f"Odds Ratio = {result_strong['odds_ratio']:.3f}")
    logger.info(f"p-value = {result_strong['pvalue']:.4f} {result_strong['pstars']}")

    # Example 4: With and without correction
    logger.info("\n[Example 4] Effect of continuity correction")
    logger.info("-" * 70)

    observed_small = [[40, 6],
                      [2, 12]]

    result_with = test_mcnemar(observed_small, correction=True)
    result_without = test_mcnemar(observed_small, correction=False)

    logger.info(f"With correction:    χ² = {result_with['statistic']:.3f}, p = {result_with['pvalue']:.4f}")
    logger.info(f"Without correction: χ² = {result_without['statistic']:.3f}, p = {result_without['pvalue']:.4f}")
    logger.info(f"Difference: Correction makes test more conservative")

    # Example 5: DataFrame output
    logger.info("\n[Example 5] DataFrame output format")
    logger.info("-" * 70)

    results_list = []
    for i in range(3):
        obs = [[40 + i*5, 10 + i],
               [8 - i, 42 + i*3]]
        r = test_mcnemar(obs, var_before=f'Time_{i}', var_after=f'Time_{i+1}')
        results_list.append(r)

    df_results = pd.DataFrame(results_list)
    logger.info(f"\n{df_results[['var_before', 'var_after', 'statistic', 'pvalue', 'odds_ratio', 'significant']].to_string()}")

    # Example 6: Export results
    logger.info("\n[Example 6] Export results to Excel")
    logger.info("-" * 70)

    convert_results(df_results, return_as='excel', path='./mcnemar_results.xlsx')
    logger.info("Saved to: ./mcnemar_results.xlsx")

    stx.session.close(
        CONFIG,
        verbose=False,
        notify=False,
        exit_status=0,
    )

# EOF
