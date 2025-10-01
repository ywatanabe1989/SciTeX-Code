#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-01 18:00:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/stats/tests/correlation/_test_kendall.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/stats/tests/correlation/_test_kendall.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
  - Perform Kendall's tau correlation test
  - Compute tau-b (accounts for ties)
  - Generate scatter plots with rank visualization
  - Support one-sided and two-sided tests

Dependencies:
  - packages: numpy, pandas, scipy, matplotlib

IO:
  - input: Two continuous or ordinal variables
  - output: Test results (dict or DataFrame) and optional figure
"""

"""Imports"""
import numpy as np
import pandas as pd
from typing import Union, Optional, Literal, Tuple
from scipy import stats
from ...utils._formatters import p2stars
from ...utils._normalizers import convert_results

try:
    import matplotlib
    import matplotlib.pyplot as plt
    HAS_PLT = True
except ImportError:
    HAS_PLT = False


def interpret_kendall_tau(tau: float) -> str:
    """
    Interpret Kendall's tau effect size.

    Parameters
    ----------
    tau : float
        Kendall's tau coefficient

    Returns
    -------
    interpretation : str
        Interpretation of effect size
    """
    tau_abs = abs(tau)
    if tau_abs < 0.1:
        return 'negligible'
    elif tau_abs < 0.3:
        return 'small'
    elif tau_abs < 0.5:
        return 'medium'
    else:
        return 'large'


def test_kendall(
    x: Union[np.ndarray, pd.Series],
    y: Union[np.ndarray, pd.Series],
    var_x: str = 'x',
    var_y: str = 'y',
    alternative: Literal['two-sided', 'less', 'greater'] = 'two-sided',
    variant: Literal['b', 'c'] = 'b',
    alpha: float = 0.05,
    plot: bool = False,
    return_as: Literal['dict', 'dataframe'] = 'dict',
    decimals: int = 3
) -> Union[dict, pd.DataFrame, Tuple]:
    """
    Perform Kendall's tau correlation test.

    Parameters
    ----------
    x : array or Series
        First variable
    y : array or Series
        Second variable
    var_x : str, default 'x'
        Name for x variable
    var_y : str, default 'y'
        Name for y variable
    alternative : {'two-sided', 'less', 'greater'}, default 'two-sided'
        Alternative hypothesis:
        - 'two-sided': tau ≠ 0
        - 'less': tau < 0 (negative association)
        - 'greater': tau > 0 (positive association)
    variant : {'b', 'c'}, default 'b'
        Tau variant:
        - 'b': tau-b (Kendall's tau-b, accounts for ties)
        - 'c': tau-c (Stuart's tau-c, for contingency tables)
    alpha : float, default 0.05
        Significance level
    plot : bool, default False
        Whether to generate scatter plot
    return_as : {'dict', 'dataframe'}, default 'dict'
        Output format
    decimals : int, default 3
        Number of decimal places for rounding

    Returns
    -------
    result : dict or DataFrame
        Test results including:
        - statistic: Kendall's tau coefficient
        - pvalue: p-value
        - tau_squared: tau²  (proportion of variance explained)
        - effect_size: tau (same as statistic)
        - effect_size_interpretation: interpretation
        - n: Sample size
        - n_concordant: Number of concordant pairs
        - n_discordant: Number of discordant pairs
        - n_ties: Number of tied pairs
        - rejected: Whether to reject null hypothesis
        - significant: Same as rejected

    If plot=True, returns tuple of (result, figure)

    Notes
    -----
    Kendall's tau is a non-parametric measure of monotonic association between
    two variables. It is based on concordant and discordant pairs.

    **Null Hypothesis (H0)**: No monotonic association (tau = 0)

    **Alternative Hypothesis (H1)**: Monotonic association exists

    **Concordant vs Discordant Pairs**:
    For pairs (x_i, y_i) and (x_j, y_j):
    - Concordant: (x_i < x_j and y_i < y_j) or (x_i > x_j and y_i > y_j)
    - Discordant: (x_i < x_j and y_i > y_j) or (x_i > x_j and y_i < y_j)

    **Kendall's tau-b** (accounts for ties):

    .. math::
        \\tau_b = \\frac{n_c - n_d}{\\sqrt{(n_0 - n_1)(n_0 - n_2)}}

    Where:
    - n_c: Number of concordant pairs
    - n_d: Number of discordant pairs
    - n_0: n(n-1)/2 (total possible pairs)
    - n_1: Sum of t_i(t_i-1)/2 for ties in x
    - n_2: Sum of u_j(u_j-1)/2 for ties in y

    **Interpretation**:
    - tau = 1: Perfect positive association
    - tau = 0: No association
    - tau = -1: Perfect negative association

    Effect size interpretation (same as correlation):
    - |tau| < 0.1: negligible
    - |tau| < 0.3: small
    - |tau| < 0.5: medium
    - |tau| ≥ 0.5: large

    **Advantages over Spearman**:
    - More robust to outliers
    - Better for small samples
    - Better interpretation (probability of concordance)
    - More accurate p-values with ties

    **Disadvantages**:
    - Computationally more expensive (O(n²))
    - Generally smaller magnitude than Spearman's rho
    - Less intuitive interpretation than Pearson

    **When to use Kendall's tau**:
    - Small sample sizes (n < 30)
    - Data with many ties
    - Ordinal data
    - Non-normal data with outliers

    Examples
    --------
    >>> import numpy as np
    >>> from scitex.stats.tests.correlation import test_kendall
    >>>
    >>> # Monotonic relationship with ties
    >>> x = np.array([1, 2, 2, 3, 4, 4, 5, 6, 7])
    >>> y = np.array([2, 3, 3, 5, 6, 6, 8, 9, 10])
    >>>
    >>> result = test_kendall(x, y, var_x='Treatment Dose', var_y='Response',
    ...                       plot=True)
    >>> print(f"τ = {result['statistic']:.3f}, p = {result['pvalue']:.4f}")
    >>> print(f"Concordant pairs: {result['n_concordant']}")

    References
    ----------
    .. [1] Kendall, M. G. (1938). "A New Measure of Rank Correlation".
           Biometrika, 30(1/2), 81-93.
    .. [2] Kendall, M. G. (1945). "The treatment of ties in ranking problems".
           Biometrika, 33(3), 239-251.

    See Also
    --------
    test_spearman : Alternative rank correlation
    test_pearson : Parametric correlation
    """
    # Convert to arrays
    x = np.asarray(x)
    y = np.asarray(y)

    # Check shapes
    if x.shape != y.shape:
        raise ValueError("x and y must have the same shape")

    if x.ndim != 1:
        raise ValueError("x and y must be 1-dimensional")

    # Remove missing values
    mask = ~(np.isnan(x) | np.isnan(y))
    x = x[mask]
    y = y[mask]

    n = len(x)

    if n < 2:
        raise ValueError("Need at least 2 observations")

    # Compute Kendall's tau
    if variant == 'b':
        tau, pvalue = stats.kendalltau(x, y, alternative=alternative, variant='b')
    elif variant == 'c':
        tau, pvalue = stats.kendalltau(x, y, alternative=alternative, variant='c')
    else:
        raise ValueError(f"Unknown variant: {variant}. Use 'b' or 'c'.")

    # Compute tau-squared (proportion of variance explained)
    tau_squared = tau ** 2

    # Count concordant, discordant, and tied pairs
    # This is computationally expensive but informative
    n_concordant = 0
    n_discordant = 0
    n_ties_x = 0
    n_ties_y = 0
    n_ties_both = 0

    for i in range(n):
        for j in range(i + 1, n):
            dx = x[j] - x[i]
            dy = y[j] - y[i]

            if dx == 0 and dy == 0:
                n_ties_both += 1
            elif dx == 0:
                n_ties_x += 1
            elif dy == 0:
                n_ties_y += 1
            elif (dx > 0 and dy > 0) or (dx < 0 and dy < 0):
                n_concordant += 1
            else:
                n_discordant += 1

    n_ties = n_ties_x + n_ties_y + n_ties_both

    # Interpret effect size
    tau_interpretation = interpret_kendall_tau(tau)

    # Build result dictionary
    result = {
        'test': "Kendall's tau",
        'variant': f'tau-{variant}',
        'var_x': var_x,
        'var_y': var_y,
        'statistic': round(float(tau), decimals),
        'pvalue': round(float(pvalue), decimals + 1),
        'tau_squared': round(float(tau_squared), decimals),
        'effect_size': round(float(tau), decimals),
        'effect_size_metric': 'kendall_tau',
        'effect_size_interpretation': tau_interpretation,
        'n': int(n),
        'n_concordant': int(n_concordant),
        'n_discordant': int(n_discordant),
        'n_ties_x': int(n_ties_x),
        'n_ties_y': int(n_ties_y),
        'n_ties_both': int(n_ties_both),
        'n_ties': int(n_ties),
        'alternative': alternative,
        'alpha': alpha,
        'rejected': pvalue < alpha,
        'significant': pvalue < alpha,
        'pstars': p2stars(pvalue),
    }

    # Generate plot if requested
    fig = None
    if plot and HAS_PLT:
        fig = _plot_kendall(x, y, result, var_x, var_y)

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


def _plot_kendall(x, y, result, var_x, var_y):
    """Create visualization for Kendall's tau."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Panel 1: Scatter plot with original data
    ax = axes[0]
    ax.scatter(x, y, alpha=0.6, s=50, edgecolors='black')

    # Add best-fit line (for visualization, not part of Kendall test)
    if len(x) > 1:
        z = np.polyfit(x, y, 1)
        p = np.poly1d(z)
        x_line = np.linspace(x.min(), x.max(), 100)
        ax.plot(x_line, p(x_line), 'r--', alpha=0.7, linewidth=2, label='Linear fit')

    ax.set_xlabel(var_x, fontsize=12)
    ax.set_ylabel(var_y, fontsize=12)
    ax.set_title('Scatter Plot', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend()

    # Panel 2: Rank scatter plot
    ax = axes[1]
    ranks_x = stats.rankdata(x)
    ranks_y = stats.rankdata(y)

    ax.scatter(ranks_x, ranks_y, alpha=0.6, s=50, edgecolors='black', color='coral')

    # Add diagonal (perfect correlation)
    rank_min = min(ranks_x.min(), ranks_y.min())
    rank_max = max(ranks_x.max(), ranks_y.max())
    ax.plot([rank_min, rank_max], [rank_min, rank_max], 'k--', alpha=0.3,
           label='Perfect correlation')

    ax.set_xlabel(f'{var_x} (rank)', fontsize=12)
    ax.set_ylabel(f'{var_y} (rank)', fontsize=12)
    ax.set_title('Rank Scatter Plot', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend()

    # Add result text
    result_text = f"Kendall's {result['variant']}\n"
    result_text += f"τ = {result['statistic']:.3f} {result['pstars']}\n"
    result_text += f"p = {result['pvalue']:.4f}\n"
    result_text += f"n = {result['n']}\n\n"
    result_text += f"Concordant: {result['n_concordant']}\n"
    result_text += f"Discordant: {result['n_discordant']}\n"
    result_text += f"Ties: {result['n_ties']}\n\n"
    result_text += f"Interpretation:\n{result['effect_size_interpretation']}"

    ax.text(0.98, 0.02, result_text,
           transform=ax.transAxes,
           fontsize=9,
           verticalalignment='bottom',
           horizontalalignment='right',
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
    logger.info("Kendall's Tau Correlation Examples")
    logger.info("=" * 70)

    # Example 1: Basic usage with ties
    logger.info("\n[Example 1] Basic Kendall's tau with tied values")
    logger.info("-" * 70)

    np.random.seed(42)
    x = np.array([1, 2, 2, 3, 4, 4, 5, 6, 7, 8, 9, 10])
    y = np.array([2, 3, 3, 5, 6, 6, 8, 9, 10, 11, 12, 13])

    result = test_kendall(x, y, var_x='Treatment Dose', var_y='Response', plot=True)

    logger.info(f"τ = {result['statistic']:.3f}, p = {result['pvalue']:.4f} {result['pstars']}")
    logger.info(f"τ² = {result['tau_squared']:.3f} (variance explained)")
    logger.info(f"Concordant pairs: {result['n_concordant']}")
    logger.info(f"Discordant pairs: {result['n_discordant']}")
    logger.info(f"Tied pairs: {result['n_ties']}")
    logger.info(f"Interpretation: {result['effect_size_interpretation']}")

    # Example 2: Comparison with Spearman
    logger.info("\n[Example 2] Kendall vs Spearman comparison")
    logger.info("-" * 70)

    from . import test_spearman

    result_kendall = test_kendall(x, y)
    result_spearman = test_spearman(x, y)

    logger.info(f"Kendall's τ:  {result_kendall['statistic']:.3f}, p = {result_kendall['pvalue']:.4f}")
    logger.info(f"Spearman's ρ: {result_spearman['statistic']:.3f}, p = {result_spearman['pvalue']:.4f}")
    logger.info(f"\nNote: Kendall's tau is generally smaller but more robust")

    # Example 3: Small sample size
    logger.info("\n[Example 3] Small sample (n=8)")
    logger.info("-" * 70)

    x_small = np.array([1, 2, 3, 4, 5, 6, 7, 8])
    y_small = np.array([2, 4, 3, 7, 6, 9, 8, 10])

    result_small = test_kendall(x_small, y_small, plot=True)

    logger.info(f"With small samples, Kendall's tau is preferred over Spearman")
    logger.info(f"τ = {result_small['statistic']:.3f}, p = {result_small['pvalue']:.4f}")

    # Example 4: Ordinal data (Likert scale)
    logger.info("\n[Example 4] Ordinal data (Likert scales)")
    logger.info("-" * 70)

    satisfaction = np.array([1, 2, 3, 3, 4, 4, 4, 5, 5, 5, 5])
    loyalty = np.array([1, 2, 2, 3, 3, 4, 4, 4, 5, 5, 5])

    result_ordinal = test_kendall(
        satisfaction, loyalty,
        var_x='Satisfaction (1-5)',
        var_y='Loyalty (1-5)',
        plot=True
    )

    logger.info(f"τ = {result_ordinal['statistic']:.3f}")
    logger.info(f"Ideal for ordinal data with limited unique values")

    # Example 5: One-sided test
    logger.info("\n[Example 5] One-sided test (positive association)")
    logger.info("-" * 70)

    result_one_sided = test_kendall(x, y, alternative='greater')

    logger.info(f"Two-sided p-value: {result['pvalue']:.4f}")
    logger.info(f"One-sided p-value: {result_one_sided['pvalue']:.4f}")
    logger.info(f"Note: One-sided test has more power when direction is known")

    # Example 6: DataFrame output
    logger.info("\n[Example 6] DataFrame output")
    logger.info("-" * 70)

    result_df = test_kendall(x, y, return_as='dataframe')
    logger.info(f"\n{result_df[['var_x', 'var_y', 'statistic', 'pvalue', 'n_concordant', 'n_discordant']].to_string()}")

    # Example 7: Export results
    logger.info("\n[Example 7] Export results")
    logger.info("-" * 70)

    convert_results(result_df, return_as='excel', path='./kendall_results.xlsx')
    logger.info("Saved to: ./kendall_results.xlsx")

    stx.session.close(
        CONFIG,
        verbose=False,
        notify=False,
        exit_status=0,
    )

# EOF
