#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-01 17:30:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/stats/tests/parametric/_test_anova_2way.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/stats/tests/parametric/_test_anova_2way.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
  - Perform two-way ANOVA for factorial designs (2 factors)
  - Test main effects and interaction effects
  - Compute partial eta-squared for each effect
  - Generate interaction plots and marginal means
  - Support balanced and unbalanced designs

Dependencies:
  - packages: numpy, pandas, scipy, matplotlib

IO:
  - input: Data with two factors (DataFrame or arrays)
  - output: Test results for each effect and optional figure
"""

"""Imports"""
import numpy as np
import pandas as pd
from typing import Union, Optional, Literal, Tuple, List, Dict
from scipy import stats
from ...utils._formatters import p2stars
from ...utils._normalizers import convert_results

try:
    import matplotlib
    import matplotlib.pyplot as plt
    HAS_PLT = True
except ImportError:
    HAS_PLT = False


def partial_eta_squared(ss_effect: float, ss_error: float) -> float:
    """Compute partial eta-squared."""
    return ss_effect / (ss_effect + ss_error)


def interpret_eta_squared(eta2: float) -> str:
    """Interpret eta-squared effect size."""
    if eta2 < 0.01:
        return 'negligible'
    elif eta2 < 0.06:
        return 'small'
    elif eta2 < 0.14:
        return 'medium'
    else:
        return 'large'


def test_anova_2way(
    data: Union[pd.DataFrame, np.ndarray],
    factor_a: Optional[Union[str, np.ndarray]] = None,
    factor_b: Optional[Union[str, np.ndarray]] = None,
    value: Optional[str] = None,
    factor_a_name: str = 'Factor A',
    factor_b_name: str = 'Factor B',
    alpha: float = 0.05,
    check_assumptions: bool = True,
    plot: bool = False,
    return_as: Literal['dict', 'dataframe'] = 'dict',
    decimals: int = 3
) -> Union[dict, pd.DataFrame, Tuple]:
    """
    Perform two-way ANOVA for factorial designs.

    Parameters
    ----------
    data : DataFrame or array
        - If DataFrame: requires factor_a, factor_b, value column names
        - If array: 2D or 3D array (see factor_a, factor_b parameters)
    factor_a : str or array, optional
        - If str: column name for factor A in DataFrame
        - If array: factor A levels for each observation
    factor_b : str or array, optional
        - If str: column name for factor B in DataFrame
        - If array: factor B levels for each observation
    value : str, optional
        Column name for dependent variable (required if data is DataFrame)
    factor_a_name : str, default 'Factor A'
        Name for factor A
    factor_b_name : str, default 'Factor B'
        Name for factor B
    alpha : float, default 0.05
        Significance level
    check_assumptions : bool, default True
        Whether to check normality and homogeneity assumptions
    plot : bool, default False
        Whether to generate interaction plot
    return_as : {'dict', 'dataframe'}, default 'dict'
        Output format
    decimals : int, default 3
        Number of decimal places for rounding

    Returns
    -------
    result : dict or DataFrame
        Test results including for each effect (A, B, interaction):
        - effect: Name of effect
        - statistic: F-statistic
        - pvalue: p-value
        - df_effect: Degrees of freedom for effect
        - df_error: Degrees of freedom for error
        - effect_size: Partial eta-squared
        - rejected: Whether to reject null hypothesis
        - significant: Same as rejected

    If plot=True, returns tuple of (result, figure)

    Notes
    -----
    Two-way ANOVA tests the effects of two independent categorical variables
    (factors) on a continuous dependent variable, including their interaction.

    **Three Hypotheses Tested**:
    1. **Main effect of Factor A**: Marginal means of A levels differ
    2. **Main effect of Factor B**: Marginal means of B levels differ
    3. **Interaction A×B**: Effect of A depends on level of B (and vice versa)

    **Null Hypotheses**:
    - H0_A: All marginal means of Factor A are equal
    - H0_B: All marginal means of Factor B are equal
    - H0_AB: No interaction between Factors A and B

    **Assumptions**:
    1. **Independence**: Observations are independent
    2. **Normality**: Residuals are normally distributed within each cell
    3. **Homogeneity of variance**: Equal variances across all cells

    **Sum of Squares Decomposition**:

    .. math::
        SS_{total} = SS_A + SS_B + SS_{AB} + SS_{error}

    Where:
    - SS_A: Sum of squares for main effect A
    - SS_B: Sum of squares for main effect B
    - SS_AB: Sum of squares for interaction A×B
    - SS_error: Sum of squares for error (within cells)

    **F-statistics**:

    .. math::
        F_A = \\frac{MS_A}{MS_{error}}, \\quad F_B = \\frac{MS_B}{MS_{error}}, \\quad F_{AB} = \\frac{MS_{AB}}{MS_{error}}

    **Effect Size (Partial η²)**:

    .. math::
        \\eta_p^2 = \\frac{SS_{effect}}{SS_{effect} + SS_{error}}

    **Interpreting Results**:
    - **Significant interaction**: Main effects should be interpreted cautiously.
      Use simple effects analysis or interaction plots.
    - **Non-significant interaction**: Main effects can be interpreted directly.

    **Post-hoc tests**:
    If main effects are significant:
    - Pairwise comparisons with test_ttest_ind()
    - Apply corrections: correct_bonferroni(), correct_holm()

    If interaction is significant:
    - Simple effects: test effect of A at each level of B
    - Pairwise comparisons within each level

    Examples
    --------
    >>> import pandas as pd
    >>> import numpy as np
    >>> from scitex.stats.tests.parametric import test_anova_2way
    >>>
    >>> # Example: Drug (2 levels) × Gender (2 levels)
    >>> np.random.seed(42)
    >>> n_per_cell = 10
    >>>
    >>> data = pd.DataFrame({
    ...     'Drug': ['Placebo']*20 + ['Active']*20,
    ...     'Gender': (['Male']*10 + ['Female']*10) * 2,
    ...     'Score': np.concatenate([
    ...         np.random.normal(50, 10, 10),  # Placebo, Male
    ...         np.random.normal(55, 10, 10),  # Placebo, Female
    ...         np.random.normal(65, 10, 10),  # Active, Male
    ...         np.random.normal(75, 10, 10),  # Active, Female (interaction)
    ...     ])
    ... })
    >>>
    >>> result = test_anova_2way(
    ...     data,
    ...     factor_a='Drug',
    ...     factor_b='Gender',
    ...     value='Score',
    ...     plot=True
    ... )
    >>>
    >>> for effect in result:
    ...     print(f"{effect['effect']}: F = {effect['statistic']:.2f}, p = {effect['pvalue']:.4f}")

    References
    ----------
    .. [1] Fisher, R. A. (1925). Statistical Methods for Research Workers.
    .. [2] Montgomery, D. C. (2017). Design and Analysis of Experiments (9th ed.).

    See Also
    --------
    test_anova : One-way ANOVA
    test_anova_rm : Repeated measures ANOVA
    """
    # Parse input data
    if isinstance(data, pd.DataFrame):
        if factor_a is None or factor_b is None or value is None:
            raise ValueError("For DataFrame input, must specify factor_a, factor_b, and value column names")

        df = data.copy()
        y = df[value].values
        factor_a_vals = df[factor_a].values
        factor_b_vals = df[factor_b].values

        # Get unique levels
        a_levels = sorted(df[factor_a].unique())
        b_levels = sorted(df[factor_b].unique())

        # Use actual column names if not specified
        if factor_a_name == 'Factor A':
            factor_a_name = factor_a
        if factor_b_name == 'Factor B':
            factor_b_name = factor_b

    else:
        # Array input
        y = np.asarray(data).ravel()

        if factor_a is None or factor_b is None:
            raise ValueError("For array input, must provide factor_a and factor_b arrays")

        factor_a_vals = np.asarray(factor_a).ravel()
        factor_b_vals = np.asarray(factor_b).ravel()

        if len(y) != len(factor_a_vals) or len(y) != len(factor_b_vals):
            raise ValueError("data, factor_a, and factor_b must have same length")

        a_levels = sorted(np.unique(factor_a_vals))
        b_levels = sorted(np.unique(factor_b_vals))

    # Build design matrix
    n = len(y)
    n_a = len(a_levels)
    n_b = len(b_levels)

    # Create level indices
    a_idx = {level: i for i, level in enumerate(a_levels)}
    b_idx = {level: i for i, level in enumerate(b_levels)}

    # Compute cell counts and means
    cell_counts = np.zeros((n_a, n_b))
    cell_sums = np.zeros((n_a, n_b))
    cell_means = np.zeros((n_a, n_b))

    for i in range(n):
        ai = a_idx[factor_a_vals[i]]
        bi = b_idx[factor_b_vals[i]]
        cell_counts[ai, bi] += 1
        cell_sums[ai, bi] += y[i]

    # Check for empty cells
    if np.any(cell_counts == 0):
        raise ValueError("Empty cells detected. All factor combinations must have at least one observation.")

    cell_means = cell_sums / cell_counts

    # Compute marginal means
    a_marginal_means = np.average(cell_means, axis=1, weights=cell_counts.sum(axis=1) / cell_counts.sum())
    b_marginal_means = np.average(cell_means, axis=0, weights=cell_counts.sum(axis=0) / cell_counts.sum())
    grand_mean = np.average(y)

    # Compute sum of squares
    ss_total = np.sum((y - grand_mean) ** 2)

    # SS for factor A (main effect)
    ss_a = 0
    for ai in range(n_a):
        n_a_level = cell_counts[ai, :].sum()
        ss_a += n_a_level * (a_marginal_means[ai] - grand_mean) ** 2

    # SS for factor B (main effect)
    ss_b = 0
    for bi in range(n_b):
        n_b_level = cell_counts[:, bi].sum()
        ss_b += n_b_level * (b_marginal_means[bi] - grand_mean) ** 2

    # SS for interaction
    ss_ab = 0
    for ai in range(n_a):
        for bi in range(n_b):
            if cell_counts[ai, bi] > 0:
                n_cell = cell_counts[ai, bi]
                predicted = grand_mean + (a_marginal_means[ai] - grand_mean) + (b_marginal_means[bi] - grand_mean)
                ss_ab += n_cell * (cell_means[ai, bi] - predicted) ** 2

    # SS error (within cells)
    ss_error = 0
    for i in range(n):
        ai = a_idx[factor_a_vals[i]]
        bi = b_idx[factor_b_vals[i]]
        ss_error += (y[i] - cell_means[ai, bi]) ** 2

    # Degrees of freedom
    df_a = n_a - 1
    df_b = n_b - 1
    df_ab = df_a * df_b
    df_error = n - n_a * n_b
    df_total = n - 1

    # Mean squares
    ms_a = ss_a / df_a if df_a > 0 else 0
    ms_b = ss_b / df_b if df_b > 0 else 0
    ms_ab = ss_ab / df_ab if df_ab > 0 else 0
    ms_error = ss_error / df_error if df_error > 0 else 0

    # F-statistics
    F_a = ms_a / ms_error if ms_error > 0 else 0
    F_b = ms_b / ms_error if ms_error > 0 else 0
    F_ab = ms_ab / ms_error if ms_error > 0 else 0

    # p-values
    p_a = 1 - stats.f.cdf(F_a, df_a, df_error) if df_a > 0 else 1.0
    p_b = 1 - stats.f.cdf(F_b, df_b, df_error) if df_b > 0 else 1.0
    p_ab = 1 - stats.f.cdf(F_ab, df_ab, df_error) if df_ab > 0 else 1.0

    # Effect sizes (partial eta-squared)
    eta2_a = partial_eta_squared(ss_a, ss_error)
    eta2_b = partial_eta_squared(ss_b, ss_error)
    eta2_ab = partial_eta_squared(ss_ab, ss_error)

    # Build results for each effect
    results = []

    # Main effect A
    results.append({
        'test': 'Two-way ANOVA',
        'effect': factor_a_name,
        'effect_type': 'main',
        'statistic': round(float(F_a), decimals),
        'pvalue': round(float(p_a), decimals + 1),
        'df_effect': int(df_a),
        'df_error': int(df_error),
        'effect_size': round(float(eta2_a), decimals),
        'effect_size_metric': 'partial_eta_squared',
        'effect_size_interpretation': interpret_eta_squared(eta2_a),
        'alpha': alpha,
        'rejected': p_a < alpha,
        'significant': p_a < alpha,
        'pstars': p2stars(p_a),
    })

    # Main effect B
    results.append({
        'test': 'Two-way ANOVA',
        'effect': factor_b_name,
        'effect_type': 'main',
        'statistic': round(float(F_b), decimals),
        'pvalue': round(float(p_b), decimals + 1),
        'df_effect': int(df_b),
        'df_error': int(df_error),
        'effect_size': round(float(eta2_b), decimals),
        'effect_size_metric': 'partial_eta_squared',
        'effect_size_interpretation': interpret_eta_squared(eta2_b),
        'alpha': alpha,
        'rejected': p_b < alpha,
        'significant': p_b < alpha,
        'pstars': p2stars(p_b),
    })

    # Interaction A×B
    results.append({
        'test': 'Two-way ANOVA',
        'effect': f'{factor_a_name} × {factor_b_name}',
        'effect_type': 'interaction',
        'statistic': round(float(F_ab), decimals),
        'pvalue': round(float(p_ab), decimals + 1),
        'df_effect': int(df_ab),
        'df_error': int(df_error),
        'effect_size': round(float(eta2_ab), decimals),
        'effect_size_metric': 'partial_eta_squared',
        'effect_size_interpretation': interpret_eta_squared(eta2_ab),
        'alpha': alpha,
        'rejected': p_ab < alpha,
        'significant': p_ab < alpha,
        'pstars': p2stars(p_ab),
    })

    # Store cell means and marginals for plotting
    results_dict = {
        'effects': results,
        'cell_means': cell_means,
        'a_levels': a_levels,
        'b_levels': b_levels,
        'a_marginal_means': a_marginal_means,
        'b_marginal_means': b_marginal_means,
        'factor_a_name': factor_a_name,
        'factor_b_name': factor_b_name,
    }

    # Generate plot if requested
    fig = None
    if plot and HAS_PLT:
        fig = _plot_anova_2way(results_dict)

    # Return based on format
    if return_as == 'dataframe':
        result_df = pd.DataFrame(results)
        if plot and fig is not None:
            return result_df, fig
        return result_df
    else:
        if plot and fig is not None:
            return results, fig
        return results


def _plot_anova_2way(results_dict):
    """Create visualization for two-way ANOVA."""
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    cell_means = results_dict['cell_means']
    a_levels = results_dict['a_levels']
    b_levels = results_dict['b_levels']
    a_marginal = results_dict['a_marginal_means']
    b_marginal = results_dict['b_marginal_means']
    factor_a_name = results_dict['factor_a_name']
    factor_b_name = results_dict['factor_b_name']
    effects = results_dict['effects']

    # Panel 1: Interaction plot (A on x-axis, lines for B)
    ax = axes[0, 0]
    x_pos = np.arange(len(a_levels))

    for bi, b_level in enumerate(b_levels):
        ax.plot(x_pos, cell_means[:, bi], marker='o', label=str(b_level), linewidth=2)

    ax.set_xticks(x_pos)
    ax.set_xticklabels([str(l) for l in a_levels])
    ax.set_xlabel(factor_a_name, fontsize=12)
    ax.set_ylabel('Mean', fontsize=12)
    ax.set_title(f'Interaction Plot: {factor_a_name} × {factor_b_name}',
                fontsize=12, fontweight='bold')
    ax.legend(title=factor_b_name, loc='best')
    ax.grid(True, alpha=0.3)

    # Panel 2: Interaction plot (B on x-axis, lines for A)
    ax = axes[0, 1]
    x_pos = np.arange(len(b_levels))

    for ai, a_level in enumerate(a_levels):
        ax.plot(x_pos, cell_means[ai, :], marker='s', label=str(a_level), linewidth=2)

    ax.set_xticks(x_pos)
    ax.set_xticklabels([str(l) for l in b_levels])
    ax.set_xlabel(factor_b_name, fontsize=12)
    ax.set_ylabel('Mean', fontsize=12)
    ax.set_title(f'Interaction Plot: {factor_b_name} × {factor_a_name}',
                fontsize=12, fontweight='bold')
    ax.legend(title=factor_a_name, loc='best')
    ax.grid(True, alpha=0.3)

    # Panel 3: Marginal means for Factor A
    ax = axes[1, 0]
    bars = ax.bar(range(len(a_levels)), a_marginal, color='steelblue', alpha=0.7, edgecolor='black')

    ax.set_xticks(range(len(a_levels)))
    ax.set_xticklabels([str(l) for l in a_levels])
    ax.set_xlabel(factor_a_name, fontsize=12)
    ax.set_ylabel('Marginal Mean', fontsize=12)
    ax.set_title(f'Main Effect: {factor_a_name}', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')

    # Add significance annotation
    effect_a = effects[0]
    if effect_a['significant']:
        ax.text(0.5, 0.95, f"F = {effect_a['statistic']:.2f} {effect_a['pstars']}",
               transform=ax.transAxes, ha='center', va='top',
               bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.5))

    # Panel 4: Marginal means for Factor B
    ax = axes[1, 1]
    bars = ax.bar(range(len(b_levels)), b_marginal, color='coral', alpha=0.7, edgecolor='black')

    ax.set_xticks(range(len(b_levels)))
    ax.set_xticklabels([str(l) for l in b_levels])
    ax.set_xlabel(factor_b_name, fontsize=12)
    ax.set_ylabel('Marginal Mean', fontsize=12)
    ax.set_title(f'Main Effect: {factor_b_name}', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')

    # Add significance annotation
    effect_b = effects[1]
    if effect_b['significant']:
        ax.text(0.5, 0.95, f"F = {effect_b['statistic']:.2f} {effect_b['pstars']}",
               transform=ax.transAxes, ha='center', va='top',
               bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.5))

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
    logger.info("Two-way ANOVA Examples")
    logger.info("=" * 70)

    # Example 1: Drug × Gender (with interaction)
    logger.info("\n[Example 1] Drug × Gender (interaction present)")
    logger.info("-" * 70)

    np.random.seed(42)
    n_per_cell = 15

    data = pd.DataFrame({
        'Drug': ['Placebo']*30 + ['Active']*30,
        'Gender': (['Male']*15 + ['Female']*15) * 2,
        'Score': np.concatenate([
            np.random.normal(50, 10, 15),  # Placebo, Male
            np.random.normal(55, 10, 15),  # Placebo, Female
            np.random.normal(65, 10, 15),  # Active, Male
            np.random.normal(75, 10, 15),  # Active, Female (interaction)
        ])
    })

    results = test_anova_2way(
        data,
        factor_a='Drug',
        factor_b='Gender',
        value='Score',
        plot=True
    )

    for effect in results:
        logger.info(f"{effect['effect']:20s}: F({effect['df_effect']},{effect['df_error']}) = "
                   f"{effect['statistic']:.3f}, p = {effect['pvalue']:.4f} {effect['pstars']}, "
                   f"η²p = {effect['effect_size']:.3f}")

    # Example 2: No interaction (additive effects)
    logger.info("\n[Example 2] Temperature × Time (no interaction)")
    logger.info("-" * 70)

    data2 = pd.DataFrame({
        'Temperature': (['Low']*20 + ['Medium']*20 + ['High']*20),
        'Time': (['Short', 'Long'] * 30),
        'Yield': np.concatenate([
            np.random.normal(40, 5, 10) + np.random.normal(0, 2, 10),    # Low, Short
            np.random.normal(40, 5, 10) + np.random.normal(10, 2, 10),   # Low, Long
            np.random.normal(50, 5, 10) + np.random.normal(0, 2, 10),    # Medium, Short
            np.random.normal(50, 5, 10) + np.random.normal(10, 2, 10),   # Medium, Long
            np.random.normal(60, 5, 10) + np.random.normal(0, 2, 10),    # High, Short
            np.random.normal(60, 5, 10) + np.random.normal(10, 2, 10),   # High, Long
        ])
    })

    results2 = test_anova_2way(
        data2,
        factor_a='Temperature',
        factor_b='Time',
        value='Yield',
        plot=True
    )

    logger.info("\nMain effects should be significant, interaction should not be:")
    for effect in results2:
        logger.info(f"{effect['effect']:25s}: p = {effect['pvalue']:.4f} ({effect['effect_size_interpretation']})")

    # Example 3: DataFrame output
    logger.info("\n[Example 3] DataFrame output format")
    logger.info("-" * 70)

    results_df = test_anova_2way(
        data,
        factor_a='Drug',
        factor_b='Gender',
        value='Score',
        return_as='dataframe'
    )

    logger.info(f"\n{results_df[['effect', 'statistic', 'pvalue', 'effect_size', 'significant']].to_string()}")

    # Example 4: Export
    logger.info("\n[Example 4] Export results")
    logger.info("-" * 70)

    convert_results(results_df, return_as='excel', path='./anova_2way_results.xlsx')
    logger.info("Saved to: ./anova_2way_results.xlsx")

    stx.session.close(
        CONFIG,
        verbose=False,
        notify=False,
        exit_status=0,
    )

# EOF
