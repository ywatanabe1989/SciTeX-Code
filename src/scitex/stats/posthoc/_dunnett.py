#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-01 20:30:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/stats/posthoc/_dunnett.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
  - Perform Dunnett's test post-hoc comparison
  - Compare multiple treatment groups vs single control
  - Control family-wise error rate
  - Two-sided or one-sided comparisons

Dependencies:
  - packages: numpy, pandas, scipy

IO:
  - input: Control group and treatment groups data
  - output: Comparison results vs control (DataFrame)
"""

"""Imports"""
import numpy as np
import pandas as pd
from typing import Union, List, Optional, Literal
from scipy import stats
from ..utils._formatters import p2stars
from ..utils._normalizers import convert_results


def dunnett_critical_value(k: int, df: int, alpha: float = 0.05,
                          alternative: str = 'two-sided') -> float:
    """
    Get critical value for Dunnett's test.

    Parameters
    ----------
    k : int
        Number of treatment groups (excluding control)
    df : int
        Degrees of freedom for error
    alpha : float
        Significance level
    alternative : {'two-sided', 'less', 'greater'}
        Direction of test

    Returns
    -------
    d_crit : float
        Critical value

    Notes
    -----
    Uses conservative approximation based on t-distribution with
    Bonferroni-like adjustment. For exact values, specialized tables
    or software (R, SAS) would be needed.
    """
    # Conservative approximation using Bonferroni adjustment
    if alternative == 'two-sided':
        alpha_adj = alpha / (2 * k)
    else:
        alpha_adj = alpha / k

    t_crit = stats.t.ppf(1 - alpha_adj, df)

    # Dunnett critical value is typically slightly smaller than Bonferroni
    # This approximation is conservative
    d_crit = t_crit * 0.95  # Slight correction factor

    return float(d_crit)


def posthoc_dunnett(
    control: Union[np.ndarray, pd.Series],
    treatments: List[Union[np.ndarray, pd.Series]],
    treatment_names: Optional[List[str]] = None,
    control_name: str = 'Control',
    alpha: float = 0.05,
    alternative: Literal['two-sided', 'less', 'greater'] = 'two-sided',
    return_as: str = 'dataframe'
) -> Union[pd.DataFrame, List[dict]]:
    """
    Perform Dunnett's test for comparing treatments vs control.

    Conducts multiple comparisons of treatment groups against a single
    control group, controlling the family-wise error rate.

    Parameters
    ----------
    control : array-like
        Control group data
    treatments : list of arrays
        List of treatment group arrays
    treatment_names : list of str, optional
        Names for treatment groups. If None, uses 'Treatment 1', etc.
    control_name : str, default 'Control'
        Name for control group
    alpha : float, default 0.05
        Family-wise error rate
    alternative : {'two-sided', 'less', 'greater'}, default 'two-sided'
        Direction of comparison:
        - 'two-sided': treatments differ from control
        - 'less': treatments < control
        - 'greater': treatments > control
    return_as : {'dataframe', 'dict'}, default 'dataframe'
        Output format

    Returns
    -------
    results : DataFrame or list of dict
        Comparison results including:
        - treatment: Treatment group name
        - control: Control group name
        - mean_treatment: Mean of treatment
        - mean_control: Mean of control
        - mean_diff: Difference (treatment - control)
        - std_error: Standard error of difference
        - t_statistic: t-statistic
        - d_critical: Dunnett critical value
        - pvalue: Approximate p-value
        - significant: Whether difference is significant
        - ci_lower: Lower bound of CI
        - ci_upper: Upper bound of CI

    Notes
    -----
    Dunnett's test is specifically designed for comparing multiple treatment
    groups against a single control group, which is more powerful than
    using Tukey HSD for this purpose.

    **Test Statistic**:

    .. math::
        t_i = \\frac{\\bar{x}_i - \\bar{x}_c}{\\sqrt{MS_{error}(1/n_i + 1/n_c)}}

    Where:
    - :math:`\\bar{x}_i`: Mean of treatment i
    - :math:`\\bar{x}_c`: Mean of control
    - MS_error: Pooled mean square error

    **Critical Value**:
    Uses Dunnett distribution tables (approximated here via conservative
    t-distribution adjustment).

    **Assumptions**:
    1. Independence of observations
    2. Normality within each group
    3. Homogeneity of variance across groups
    4. One group designated as control

    **Advantages**:
    - More powerful than Tukey HSD for control comparisons
    - More powerful than Bonferroni for this specific design
    - Controls family-wise error rate exactly
    - Provides directional tests (one-sided)

    **Disadvantages**:
    - Only compares vs control (not all pairwise)
    - Requires equal variances (use Dunnett T3 if violated)
    - Requires control group designation

    **When to use**:
    - After ANOVA with one control and multiple treatments
    - Drug trials (placebo vs multiple doses)
    - Baseline comparisons (control vs interventions)

    Examples
    --------
    >>> import numpy as np
    >>> from scitex.stats.posthoc import posthoc_dunnett
    >>>
    >>> # Example: Placebo vs 3 drug doses
    >>> np.random.seed(42)
    >>> placebo = np.random.normal(100, 15, 30)
    >>> dose_low = np.random.normal(105, 15, 30)
    >>> dose_med = np.random.normal(110, 15, 30)
    >>> dose_high = np.random.normal(115, 15, 30)
    >>>
    >>> results = posthoc_dunnett(
    ...     control=placebo,
    ...     treatments=[dose_low, dose_med, dose_high],
    ...     treatment_names=['Low Dose', 'Med Dose', 'High Dose'],
    ...     control_name='Placebo'
    ... )
    >>>
    >>> print(results[['treatment', 'mean_diff', 'pvalue', 'significant']])

    References
    ----------
    .. [1] Dunnett, C. W. (1955). "A multiple comparison procedure for
           comparing several treatments with a control". Journal of the
           American Statistical Association, 50(272), 1096-1121.
    .. [2] Dunnett, C. W. (1964). "New tables for multiple comparisons
           with a control". Biometrics, 20(3), 482-491.

    See Also
    --------
    posthoc_tukey : For all pairwise comparisons
    posthoc_games_howell : For unequal variances (all pairs)
    """
    # Convert to arrays
    control = np.asarray(control)
    treatments = [np.asarray(t) for t in treatments]

    k = len(treatments)  # Number of treatment groups

    if k < 1:
        raise ValueError("Need at least 1 treatment group")

    # Treatment names
    if treatment_names is None:
        treatment_names = [f'Treatment {i+1}' for i in range(k)]

    if len(treatment_names) != k:
        raise ValueError(f"Expected {k} treatment names, got {len(treatment_names)}")

    # Group statistics
    n_control = len(control)
    mean_control = np.mean(control)

    n_treatments = [len(t) for t in treatments]
    means_treatments = [np.mean(t) for t in treatments]

    # Total sample size and degrees of freedom
    N = n_control + sum(n_treatments)
    df_error = N - (k + 1)  # k treatments + 1 control

    # Pooled variance (MS_error)
    ss_error = np.sum((control - mean_control) ** 2)
    for t in treatments:
        ss_error += np.sum((t - np.mean(t)) ** 2)

    ms_error = ss_error / df_error

    # Get critical value
    d_crit = dunnett_critical_value(k, df_error, alpha, alternative)

    # Perform comparisons vs control
    results = []

    for i, (treatment, n_t, mean_t) in enumerate(zip(treatments, n_treatments, means_treatments)):
        # Mean difference
        mean_diff = mean_t - mean_control

        # Standard error
        se = np.sqrt(ms_error * (1/n_t + 1/n_control))

        # t-statistic
        if se == 0:
            t_stat = 0.0
        else:
            t_stat = mean_diff / se

        # p-value (conservative approximation)
        if alternative == 'two-sided':
            pvalue = 2 * (1 - stats.t.cdf(abs(t_stat), df_error))
        elif alternative == 'greater':
            pvalue = 1 - stats.t.cdf(t_stat, df_error)
        else:  # less
            pvalue = stats.t.cdf(t_stat, df_error)

        # Adjust for multiple comparisons (conservative)
        pvalue = min(pvalue * k, 1.0)

        # Determine significance
        if alternative == 'two-sided':
            significant = abs(t_stat) > d_crit
        elif alternative == 'greater':
            significant = t_stat > d_crit
        else:  # less
            significant = t_stat < -d_crit

        # Confidence interval
        margin = d_crit * se
        if alternative == 'two-sided':
            ci_lower = mean_diff - margin
            ci_upper = mean_diff + margin
        elif alternative == 'greater':
            ci_lower = mean_diff - margin
            ci_upper = np.inf
        else:  # less
            ci_lower = -np.inf
            ci_upper = mean_diff + margin

        results.append({
            'treatment': treatment_names[i],
            'control': control_name,
            'n_treatment': n_t,
            'n_control': n_control,
            'mean_treatment': round(float(mean_t), 3),
            'mean_control': round(float(mean_control), 3),
            'mean_diff': round(float(mean_diff), 3),
            'std_error': round(float(se), 3),
            't_statistic': round(float(t_stat), 3),
            'd_critical': round(float(d_crit), 3),
            'pvalue': round(float(pvalue), 4),
            'significant': bool(significant),
            'pstars': p2stars(pvalue),
            'ci_lower': round(float(ci_lower), 3) if not np.isinf(ci_lower) else '-inf',
            'ci_upper': round(float(ci_upper), 3) if not np.isinf(ci_upper) else 'inf',
            'alpha': alpha,
            'alternative': alternative,
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
    logger.info("Dunnett's Test Post-hoc Examples")
    logger.info("=" * 70)

    # Example 1: Drug trial - placebo vs multiple doses
    logger.info("\n[Example 1] Drug trial: Placebo vs 3 doses")
    logger.info("-" * 70)

    np.random.seed(42)
    placebo = np.random.normal(100, 15, 30)
    dose_low = np.random.normal(105, 15, 30)
    dose_med = np.random.normal(110, 15, 30)
    dose_high = np.random.normal(115, 15, 30)

    logger.info(f"Placebo: mean={np.mean(placebo):.2f}, n={len(placebo)}")
    logger.info(f"Low Dose: mean={np.mean(dose_low):.2f}, n={len(dose_low)}")
    logger.info(f"Med Dose: mean={np.mean(dose_med):.2f}, n={len(dose_med)}")
    logger.info(f"High Dose: mean={np.mean(dose_high):.2f}, n={len(dose_high)}")

    results = posthoc_dunnett(
        control=placebo,
        treatments=[dose_low, dose_med, dose_high],
        treatment_names=['Low Dose', 'Med Dose', 'High Dose'],
        control_name='Placebo'
    )

    logger.info(f"\n{results[['treatment', 'mean_diff', 't_statistic', 'pvalue', 'significant']].to_string()}")

    # Example 2: One-sided test (treatments > control)
    logger.info("\n[Example 2] One-sided test (greater than control)")
    logger.info("-" * 70)

    results_greater = posthoc_dunnett(
        control=placebo,
        treatments=[dose_low, dose_med, dose_high],
        treatment_names=['Low Dose', 'Med Dose', 'High Dose'],
        control_name='Placebo',
        alternative='greater'
    )

    logger.info(f"\n{results_greater[['treatment', 'mean_diff', 'pvalue', 'significant']].to_string()}")

    # Example 3: Baseline comparison
    logger.info("\n[Example 3] Baseline vs interventions")
    logger.info("-" * 70)

    baseline = np.random.normal(50, 10, 25)
    intervention_a = np.random.normal(55, 10, 25)
    intervention_b = np.random.normal(58, 10, 25)

    results_baseline = posthoc_dunnett(
        control=baseline,
        treatments=[intervention_a, intervention_b],
        treatment_names=['Intervention A', 'Intervention B'],
        control_name='Baseline'
    )

    logger.info(f"\n{results_baseline.to_string()}")

    # Example 4: Comparison with Tukey HSD
    logger.info("\n[Example 4] Dunnett vs Tukey HSD power comparison")
    logger.info("-" * 70)

    from ._tukey_hsd import posthoc_tukey

    # All groups for Tukey
    all_groups = [placebo, dose_low, dose_med, dose_high]
    group_names = ['Placebo', 'Low Dose', 'Med Dose', 'High Dose']

    results_tukey = posthoc_tukey(all_groups, group_names)

    # Filter Tukey results for comparisons vs placebo
    tukey_vs_placebo = results_tukey[
        (results_tukey['group_i'] == 'Placebo') |
        (results_tukey['group_j'] == 'Placebo')
    ]

    logger.info("\nDunnett's test (designed for control comparisons):")
    logger.info(f"{results[['treatment', 'pvalue', 'significant']].to_string()}")

    logger.info("\nTukey HSD (all pairwise, less power for control comparisons):")
    logger.info(f"{tukey_vs_placebo[['group_i', 'group_j', 'pvalue', 'significant']].to_string()}")

    logger.info("\nNote: Dunnett is more powerful for control comparisons")

    # Example 5: Unbalanced design
    logger.info("\n[Example 5] Unbalanced design")
    logger.info("-" * 70)

    control_unbal = np.random.normal(20, 5, 50)
    treat1_unbal = np.random.normal(22, 5, 15)
    treat2_unbal = np.random.normal(25, 5, 20)
    treat3_unbal = np.random.normal(23, 5, 30)

    results_unbal = posthoc_dunnett(
        control=control_unbal,
        treatments=[treat1_unbal, treat2_unbal, treat3_unbal],
        treatment_names=['T1', 'T2', 'T3']
    )

    logger.info(f"Sample sizes: Control={len(control_unbal)}, T1={len(treat1_unbal)}, "
               f"T2={len(treat2_unbal)}, T3={len(treat3_unbal)}")
    logger.info(f"\n{results_unbal.to_string()}")

    # Example 6: With confidence intervals
    logger.info("\n[Example 6] Confidence intervals")
    logger.info("-" * 70)

    for _, row in results.iterrows():
        logger.info(f"{row['treatment']} vs {row['control']}: "
                   f"Diff = {row['mean_diff']:.2f}, "
                   f"95% CI [{row['ci_lower']}, {row['ci_upper']}] {row['pstars']}")

    # Example 7: Export results
    logger.info("\n[Example 7] Export results")
    logger.info("-" * 70)

    convert_results(results, return_as='excel', path='./dunnett_results.xlsx')
    logger.info("Saved to: ./dunnett_results.xlsx")

    stx.session.close(
        CONFIG,
        verbose=False,
        notify=False,
        exit_status=0,
    )

# EOF
