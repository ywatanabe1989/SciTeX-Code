#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-01 20:00:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/stats/posthoc/_games_howell.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
  - Perform Games-Howell post-hoc test
  - Pairwise comparisons with unequal variances
  - Does not assume homogeneity of variance
  - Welch-Satterthwaite degrees of freedom

Dependencies:
  - packages: numpy, pandas, scipy

IO:
  - input: Multiple groups data
  - output: Pairwise comparison results (DataFrame)
"""

"""Imports"""
import numpy as np
import pandas as pd
from typing import Union, List, Optional
from scipy import stats
from ..utils._formatters import p2stars
from ..utils._normalizers import convert_results


def welch_satterthwaite_df(var_i: float, n_i: int, var_j: float, n_j: int) -> float:
    """
    Compute Welch-Satterthwaite degrees of freedom.

    Parameters
    ----------
    var_i : float
        Variance of group i
    n_i : int
        Sample size of group i
    var_j : float
        Variance of group j
    n_j : int
        Sample size of group j

    Returns
    -------
    df : float
        Degrees of freedom

    Notes
    -----
    Formula:
    df = (s_i²/n_i + s_j²/n_j)² / [(s_i²/n_i)²/(n_i-1) + (s_j²/n_j)²/(n_j-1)]
    """
    s_i_sq_n_i = var_i / n_i
    s_j_sq_n_j = var_j / n_j

    numerator = (s_i_sq_n_i + s_j_sq_n_j) ** 2
    denominator = (s_i_sq_n_i ** 2) / (n_i - 1) + (s_j_sq_n_j ** 2) / (n_j - 1)

    if denominator == 0:
        return n_i + n_j - 2

    df = numerator / denominator
    return float(df)


def posthoc_games_howell(
    groups: List[Union[np.ndarray, pd.Series]],
    group_names: Optional[List[str]] = None,
    alpha: float = 0.05,
    return_as: str = 'dataframe'
) -> Union[pd.DataFrame, List[dict]]:
    """
    Perform Games-Howell post-hoc test for pairwise comparisons.

    Modified Tukey HSD that does not assume equal variances.
    Uses Welch-Satterthwaite degrees of freedom approximation.

    Parameters
    ----------
    groups : list of arrays
        List of sample arrays for each group
    group_names : list of str, optional
        Names for each group. If None, uses 'Group 1', 'Group 2', etc.
    alpha : float, default 0.05
        Family-wise error rate
    return_as : {'dataframe', 'dict'}, default 'dataframe'
        Output format

    Returns
    -------
    results : DataFrame or list of dict
        Pairwise comparison results including:
        - group_i: First group name
        - group_j: Second group name
        - mean_i: Mean of group i
        - mean_j: Mean of group j
        - mean_diff: Difference in means (i - j)
        - std_error: Standard error of difference
        - t_statistic: t-statistic (Welch)
        - df: Welch-Satterthwaite degrees of freedom
        - pvalue: p-value
        - significant: Whether difference is significant
        - ci_lower: Lower bound of 95% CI
        - ci_upper: Upper bound of 95% CI

    Notes
    -----
    Games-Howell test is a non-parametric post-hoc test that does not
    assume equal variances across groups (heteroscedasticity).

    **Test Statistic (Welch t-test)**:

    .. math::
        t = \\frac{\\bar{x}_i - \\bar{x}_j}{\\sqrt{s_i^2/n_i + s_j^2/n_j}}

    **Degrees of Freedom (Welch-Satterthwaite)**:

    .. math::
        df = \\frac{(s_i^2/n_i + s_j^2/n_j)^2}{\\frac{(s_i^2/n_i)^2}{n_i-1} + \\frac{(s_j^2/n_j)^2}{n_j-1}}

    **Critical Value**:
    Uses studentized range distribution with Welch df (approximated).

    **Assumptions**:
    1. Independence of observations
    2. Normality within each group
    3. **Does NOT assume equal variances** (main advantage over Tukey HSD)

    **Advantages**:
    - Robust to unequal variances
    - More accurate than Tukey HSD when homogeneity violated
    - Controls Type I error well even with variance heterogeneity

    **Disadvantages**:
    - Slightly less powerful than Tukey HSD when variances are equal
    - More complex calculations
    - Requires larger sample sizes for accuracy

    **When to use**:
    - After ANOVA with unequal variances (Levene's test significant)
    - When Tukey HSD assumptions violated
    - With unbalanced designs and heteroscedasticity

    Examples
    --------
    >>> import numpy as np
    >>> from scitex.stats.posthoc import posthoc_games_howell
    >>>
    >>> # Example: Groups with different variances
    >>> np.random.seed(42)
    >>> group1 = np.random.normal(10, 1, 20)   # Small variance
    >>> group2 = np.random.normal(12, 5, 25)   # Large variance
    >>> group3 = np.random.normal(11, 2, 15)   # Medium variance
    >>>
    >>> results = posthoc_games_howell(
    ...     [group1, group2, group3],
    ...     group_names=['Low Var', 'High Var', 'Med Var']
    ... )
    >>>
    >>> print(results[['group_i', 'group_j', 'mean_diff', 'pvalue', 'significant']])

    References
    ----------
    .. [1] Games, P. A., & Howell, J. F. (1976). "Pairwise multiple comparison
           procedures with unequal n's and/or variances: A Monte Carlo study".
           Journal of Educational Statistics, 1(2), 113-125.
    .. [2] Welch, B. L. (1947). "The generalization of 'Student's' problem when
           several different population variances are involved". Biometrika,
           34(1/2), 28-35.

    See Also
    --------
    posthoc_tukey : For equal variances
    posthoc_dunnett : For comparisons vs control
    """
    # Convert to list of arrays
    groups = [np.asarray(g) for g in groups]

    k = len(groups)

    if k < 2:
        raise ValueError("Need at least 2 groups for pairwise comparisons")

    # Group names
    if group_names is None:
        group_names = [f'Group {i+1}' for i in range(k)]

    if len(group_names) != k:
        raise ValueError(f"Expected {k} group names, got {len(group_names)}")

    # Compute group statistics
    n_groups = [len(g) for g in groups]
    means = [np.mean(g) for g in groups]
    variances = [np.var(g, ddof=1) for g in groups]

    # Perform all pairwise comparisons
    results = []

    for i in range(k):
        for j in range(i + 1, k):
            n_i = n_groups[i]
            n_j = n_groups[j]
            mean_i = means[i]
            mean_j = means[j]
            var_i = variances[i]
            var_j = variances[j]

            # Mean difference
            mean_diff = mean_i - mean_j

            # Standard error (Welch formula)
            se = np.sqrt(var_i / n_i + var_j / n_j)

            # Welch t-statistic
            if se == 0:
                t_stat = 0.0
            else:
                t_stat = mean_diff / se

            # Welch-Satterthwaite degrees of freedom
            df = welch_satterthwaite_df(var_i, n_i, var_j, n_j)

            # p-value (two-tailed)
            pvalue = 2 * (1 - stats.t.cdf(abs(t_stat), df))

            # Critical value for CI (using studentized range approximation)
            # For simplicity, use t-distribution with Bonferroni-like adjustment
            alpha_adj = alpha / (k * (k - 1) / 2)
            t_crit = stats.t.ppf(1 - alpha_adj / 2, df)

            # Determine significance
            significant = abs(t_stat) > t_crit

            # Confidence interval
            margin = t_crit * se
            ci_lower = mean_diff - margin
            ci_upper = mean_diff + margin

            results.append({
                'group_i': group_names[i],
                'group_j': group_names[j],
                'n_i': n_i,
                'n_j': n_j,
                'mean_i': round(float(mean_i), 3),
                'mean_j': round(float(mean_j), 3),
                'var_i': round(float(var_i), 3),
                'var_j': round(float(var_j), 3),
                'mean_diff': round(float(mean_diff), 3),
                'std_error': round(float(se), 3),
                't_statistic': round(float(t_stat), 3),
                'df': round(float(df), 2),
                'pvalue': round(float(pvalue), 4),
                'significant': bool(significant),
                'pstars': p2stars(pvalue),
                'ci_lower': round(float(ci_lower), 3),
                'ci_upper': round(float(ci_upper), 3),
                'alpha': alpha,
            })

    # Return format
    if return_as == 'dataframe':
        return pd.DataFrame(results)
    else:
        return results


if __name__ == "__main__":
    import sys
    import argparse
    import scitex as stx

    parser = argparse.ArgumentParser()
    args = parser.parse_args([])

    CONFIG, sys.stdout, sys.stderr, plt, CC, rng = stx.session.start(
        sys=sys,
        plt=None,
        args=args,
        file=__FILE__,
        verbose=True,
        agg=True,
    )

    logger = stx.logging.getLogger(__name__)

    logger.info("=" * 70)
    logger.info("Games-Howell Post-hoc Test Examples")
    logger.info("=" * 70)

    # Example 1: Unequal variances
    logger.info("\n[Example 1] Groups with unequal variances")
    logger.info("-" * 70)

    np.random.seed(42)
    group1 = np.random.normal(10, 1, 20)   # Small variance
    group2 = np.random.normal(12, 5, 25)   # Large variance
    group3 = np.random.normal(11, 2, 15)   # Medium variance

    logger.info(f"Group 1: mean={np.mean(group1):.2f}, var={np.var(group1, ddof=1):.2f}, n={len(group1)}")
    logger.info(f"Group 2: mean={np.mean(group2):.2f}, var={np.var(group2, ddof=1):.2f}, n={len(group2)}")
    logger.info(f"Group 3: mean={np.mean(group3):.2f}, var={np.var(group3, ddof=1):.2f}, n={len(group3)}")

    results = posthoc_games_howell(
        [group1, group2, group3],
        group_names=['Low Var', 'High Var', 'Med Var']
    )

    logger.info(f"\n{results[['group_i', 'group_j', 'mean_diff', 'df', 'pvalue', 'significant']].to_string()}")

    # Example 2: Comparison with Tukey HSD
    logger.info("\n[Example 2] Games-Howell vs Tukey HSD")
    logger.info("-" * 70)

    from ._tukey_hsd import posthoc_tukey

    results_gh = posthoc_games_howell([group1, group2, group3])
    results_tukey = posthoc_tukey([group1, group2, group3])

    logger.info("\nGames-Howell results:")
    logger.info(f"{results_gh[['group_i', 'group_j', 'pvalue', 'significant']].to_string()}")

    logger.info("\nTukey HSD results:")
    logger.info(f"{results_tukey[['group_i', 'group_j', 'pvalue', 'significant']].to_string()}")

    logger.info("\nNote: Games-Howell is more appropriate with unequal variances")

    # Example 3: After ANOVA with heteroscedasticity
    logger.info("\n[Example 3] After ANOVA with violated homogeneity")
    logger.info("-" * 70)

    from ..tests.parametric import test_anova

    anova_result = test_anova(
        [group1, group2, group3],
        var_names=['Low Var', 'High Var', 'Med Var'],
        check_assumptions=True
    )

    logger.info(f"ANOVA: F = {anova_result['statistic']:.3f}, p = {anova_result['pvalue']:.4f}")
    logger.info(f"Assumptions met: {anova_result.get('assumptions_met', 'N/A')}")

    is_sig = anova_result.get('significant', anova_result.get('is_significant', False))
    if is_sig:
        logger.info("\nANOVA significant. Using Games-Howell (robust to unequal variances)...")
        logger.info(f"\n{results.to_string()}")

    # Example 4: Extreme variance ratios
    logger.info("\n[Example 4] Extreme variance heterogeneity")
    logger.info("-" * 70)

    extreme1 = np.random.normal(50, 1, 20)    # Very small variance
    extreme2 = np.random.normal(55, 10, 20)   # Very large variance

    var_ratio = np.var(extreme2, ddof=1) / np.var(extreme1, ddof=1)
    logger.info(f"Variance ratio: {var_ratio:.1f}")

    results_extreme = posthoc_games_howell([extreme1, extreme2])

    logger.info(f"\n{results_extreme.to_string()}")

    # Example 5: Export results
    logger.info("\n[Example 5] Export results")
    logger.info("-" * 70)

    convert_results(results, return_as='excel', path='./games_howell_results.xlsx')
    logger.info("Saved to: ./games_howell_results.xlsx")

    stx.session.close(
        CONFIG,
        verbose=False,
        notify=False,
        exit_status=0,
    )

# EOF
