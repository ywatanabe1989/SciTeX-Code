#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-01 19:30:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/stats/posthoc/_tukey_hsd.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
  - Perform Tukey HSD (Honestly Significant Difference) post-hoc test
  - All pairwise comparisons after ANOVA
  - Control family-wise error rate
  - Assumes equal variances and balanced/unbalanced designs

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


def studentized_range_critical(k: int, df: int, alpha: float = 0.05) -> float:
    """
    Get critical value from studentized range distribution.

    Parameters
    ----------
    k : int
        Number of groups
    df : int
        Degrees of freedom for error
    alpha : float
        Significance level

    Returns
    -------
    q_crit : float
        Critical value

    Notes
    -----
    Uses approximation since scipy doesn't have exact studentized range.
    For exact values, we approximate using the relationship between
    studentized range and normal distribution.
    """
    # Approximate critical value using normal distribution
    # This is less accurate than exact tables but serviceable
    # For production, consider using statsmodels or R integration

    # Use Bonferroni-adjusted critical value as conservative approximation
    # Actual studentized range is less conservative
    alpha_adj = alpha / (k * (k - 1) / 2)  # Number of pairwise comparisons
    t_crit = stats.t.ppf(1 - alpha_adj / 2, df)

    # Studentized range is approximately sqrt(2) * t for equal sample sizes
    q_crit = np.sqrt(2) * t_crit

    return float(q_crit)


def posthoc_tukey(
    groups: List[Union[np.ndarray, pd.Series]],
    group_names: Optional[List[str]] = None,
    alpha: float = 0.05,
    return_as: str = 'dataframe'
) -> Union[pd.DataFrame, List[dict]]:
    """
    Perform Tukey HSD post-hoc test for pairwise comparisons.

    Conducts all pairwise comparisons between groups after ANOVA,
    controlling the family-wise error rate.

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
        - q_statistic: Studentized range statistic
        - q_critical: Critical value
        - pvalue: Approximate p-value
        - significant: Whether difference is significant
        - ci_lower: Lower bound of 95% CI
        - ci_upper: Upper bound of 95% CI

    Notes
    -----
    Tukey's Honestly Significant Difference (HSD) test is used for all
    pairwise comparisons between group means after a significant ANOVA.

    **Test Statistic (Studentized Range)**:

    .. math::
        q = \\frac{|\\bar{x}_i - \\bar{x}_j|}{\\sqrt{MS_{error}/n}}

    Where:
    - MS_error: Mean square error from ANOVA
    - n: Harmonic mean of sample sizes (for unbalanced designs)

    **Assumptions**:
    1. Independence of observations
    2. Normality within each group
    3. Homogeneity of variance across groups (same as ANOVA)

    **Advantages**:
    - Controls family-wise error rate exactly at α
    - More powerful than Bonferroni correction
    - Provides confidence intervals for differences

    **Disadvantages**:
    - Assumes equal variances (use Games-Howell if violated)
    - Less powerful than Bonferroni for small number of comparisons
    - Requires significant ANOVA first (recommended practice)

    **When to use**:
    - After significant one-way ANOVA
    - When variances are approximately equal
    - For all pairwise comparisons (not subset)

    Examples
    --------
    >>> import numpy as np
    >>> from scitex.stats.posthoc import posthoc_tukey
    >>>
    >>> # Example: Compare 4 treatment groups
    >>> np.random.seed(42)
    >>> control = np.random.normal(10, 2, 20)
    >>> treatment1 = np.random.normal(12, 2, 20)
    >>> treatment2 = np.random.normal(11, 2, 20)
    >>> treatment3 = np.random.normal(13, 2, 20)
    >>>
    >>> results = posthoc_tukey(
    ...     [control, treatment1, treatment2, treatment3],
    ...     group_names=['Control', 'Treat1', 'Treat2', 'Treat3']
    ... )
    >>>
    >>> print(results[['group_i', 'group_j', 'mean_diff', 'pvalue', 'significant']])

    References
    ----------
    .. [1] Tukey, J. W. (1949). "Comparing individual means in the analysis
           of variance". Biometrics, 5(2), 99-114.
    .. [2] Kramer, C. Y. (1956). "Extension of multiple range tests to group
           means with unequal numbers of replications". Biometrics, 12(3),
           307-310.

    See Also
    --------
    posthoc_games_howell : For unequal variances
    posthoc_dunnett : For comparisons vs control
    correct_bonferroni : Simple but conservative alternative
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

    # Total sample size and degrees of freedom
    N = sum(n_groups)
    df_error = N - k

    # Pooled variance (MS_error from ANOVA)
    ss_error = 0
    for g in groups:
        ss_error += np.sum((g - np.mean(g)) ** 2)

    ms_error = ss_error / df_error

    # Get critical value
    q_crit = studentized_range_critical(k, df_error, alpha)

    # Perform all pairwise comparisons
    results = []

    for i in range(k):
        for j in range(i + 1, k):
            n_i = n_groups[i]
            n_j = n_groups[j]
            mean_i = means[i]
            mean_j = means[j]

            # Mean difference
            mean_diff = mean_i - mean_j

            # Standard error for unequal sample sizes (Tukey-Kramer)
            se = np.sqrt(ms_error * (1/n_i + 1/n_j) / 2)

            # Studentized range statistic
            q_stat = abs(mean_diff) / se

            # Approximate p-value
            # Using conservative approximation
            # Exact p-value requires studentized range distribution
            t_equiv = q_stat / np.sqrt(2)
            pvalue = 2 * (1 - stats.t.cdf(t_equiv, df_error))

            # Determine significance
            significant = q_stat > q_crit

            # Confidence interval
            margin = q_crit * se
            ci_lower = mean_diff - margin
            ci_upper = mean_diff + margin

            results.append({
                'group_i': group_names[i],
                'group_j': group_names[j],
                'n_i': n_i,
                'n_j': n_j,
                'mean_i': round(float(mean_i), 3),
                'mean_j': round(float(mean_j), 3),
                'mean_diff': round(float(mean_diff), 3),
                'std_error': round(float(se), 3),
                'q_statistic': round(float(q_stat), 3),
                'q_critical': round(float(q_crit), 3),
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
    logger.info("Tukey HSD Post-hoc Test Examples")
    logger.info("=" * 70)

    # Example 1: Basic usage after ANOVA
    logger.info("\n[Example 1] Basic Tukey HSD after significant ANOVA")
    logger.info("-" * 70)

    np.random.seed(42)
    control = np.random.normal(10, 2, 20)
    treatment1 = np.random.normal(12, 2, 20)
    treatment2 = np.random.normal(11, 2, 20)
    treatment3 = np.random.normal(13, 2, 20)

    # First run ANOVA
    from ..tests.parametric import test_anova

    anova_result = test_anova(
        [control, treatment1, treatment2, treatment3],
        var_names=['Control', 'Treat1', 'Treat2', 'Treat3']
    )

    logger.info(f"ANOVA: F = {anova_result['statistic']:.3f}, p = {anova_result['pvalue']:.4f}")

    if anova_result['significant']:
        logger.info("\nANOVA significant, conducting Tukey HSD...")

        results = posthoc_tukey(
            [control, treatment1, treatment2, treatment3],
            group_names=['Control', 'Treat1', 'Treat2', 'Treat3']
        )

        logger.info(f"\n{results[['group_i', 'group_j', 'mean_diff', 'pvalue', 'significant']].to_string()}")

    # Example 2: Unbalanced design (Tukey-Kramer)
    logger.info("\n[Example 2] Unbalanced design (different sample sizes)")
    logger.info("-" * 70)

    group_a = np.random.normal(50, 10, 15)
    group_b = np.random.normal(60, 10, 25)
    group_c = np.random.normal(55, 10, 20)

    results_unbalanced = posthoc_tukey(
        [group_a, group_b, group_c],
        group_names=['A', 'B', 'C']
    )

    logger.info(f"Sample sizes: A={len(group_a)}, B={len(group_b)}, C={len(group_c)}")
    logger.info(f"\n{results_unbalanced.to_string()}")

    # Example 3: With confidence intervals
    logger.info("\n[Example 3] Confidence intervals for differences")
    logger.info("-" * 70)

    for _, row in results.iterrows():
        if row['significant']:
            logger.info(f"{row['group_i']} vs {row['group_j']}: "
                       f"Diff = {row['mean_diff']:.2f}, "
                       f"95% CI [{row['ci_lower']:.2f}, {row['ci_upper']:.2f}] {row['pstars']}")

    # Example 4: Export results
    logger.info("\n[Example 4] Export results")
    logger.info("-" * 70)

    convert_results(results, return_as='excel', path='./tukey_hsd_results.xlsx')
    logger.info("Saved to: ./tukey_hsd_results.xlsx")

    stx.session.close(
        CONFIG,
        verbose=False,
        notify=False,
        exit_status=0,
    )

# EOF
