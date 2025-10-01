#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-01 14:50:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/stats/utils/_effect_size.py

"""
Functionalities:
  - Compute Cohen's d effect size for t-tests
  - Support both independent and paired samples
  - Handle various pooling methods
  - Provide interpretation guidelines

Dependencies:
  - packages: numpy, pandas, scipy

IO:
  - input: Two samples (arrays or Series)
  - output: Effect size value (float)
"""

"""Imports"""
import sys
import argparse
import numpy as np
import pandas as pd
from typing import Union, Optional, Literal, List
import scitex as stx
from scitex.logging import getLogger

logger = getLogger(__name__)

"""Functions"""
def cohens_d(
    x: Union[np.ndarray, pd.Series],
    y: Optional[Union[np.ndarray, pd.Series]] = None,
    paired: bool = False,
    correction: Literal['hedges', 'glass', None] = None
) -> float:
    """
    Compute Cohen's d effect size.

    Parameters
    ----------
    x : array or Series
        First sample
    y : array or Series, optional
        Second sample. If None, computes one-sample effect size against zero.
    paired : bool, default False
        Whether samples are paired
    correction : {'hedges', 'glass', None}, default None
        Correction method:
        - None: Standard Cohen's d
        - 'hedges': Hedges' g (corrected for small samples)
        - 'glass': Glass's delta (uses only control group SD)

    Returns
    -------
    float
        Effect size value

    Notes
    -----
    Cohen's d is calculated as:

    .. math::
        d = \\frac{\\bar{x}_1 - \\bar{x}_2}{s_{pooled}}

    where :math:`s_{pooled}` is the pooled standard deviation:

    .. math::
        s_{pooled} = \\sqrt{\\frac{(n_1-1)s_1^2 + (n_2-1)s_2^2}{n_1 + n_2 - 2}}

    Interpretation guidelines (Cohen, 1988):
    - Small effect: d = 0.2
    - Medium effect: d = 0.5
    - Large effect: d = 0.8

    For paired samples, d is computed as:

    .. math::
        d = \\frac{\\bar{d}}{s_d}

    where :math:`\\bar{d}` is the mean difference and :math:`s_d` is the
    standard deviation of differences.

    References
    ----------
    .. [1] Cohen, J. (1988). Statistical Power Analysis for the Behavioral
           Sciences (2nd ed.). Routledge.

    Examples
    --------
    >>> x = np.array([1, 2, 3, 4, 5])
    >>> y = np.array([2, 3, 4, 5, 6])
    >>> cohens_d(x, y)
    -1.0

    >>> # Paired samples
    >>> cohens_d(x, y, paired=True)
    -1.58...

    >>> # With Hedges' correction
    >>> cohens_d(x, y, correction='hedges')
    -0.95...
    """
    # Convert to numpy arrays
    x = np.asarray(x)
    if y is not None:
        y = np.asarray(y)

    # Remove NaN values
    x = x[~np.isnan(x)]
    if y is not None:
        y = y[~np.isnan(y)]

    # Compute effect size
    if y is None:
        # One-sample: compare to zero
        d = np.mean(x) / np.std(x, ddof=1)
    elif paired:
        # Paired samples
        if len(x) != len(y):
            raise ValueError("Paired samples must have same length")
        diff = x - y
        d = np.mean(diff) / np.std(diff, ddof=1)
    else:
        # Independent samples
        n1, n2 = len(x), len(y)
        mean_diff = np.mean(x) - np.mean(y)

        if correction == 'glass':
            # Glass's delta: use only control group (y) SD
            d = mean_diff / np.std(y, ddof=1)
        else:
            # Pooled standard deviation
            var1 = np.var(x, ddof=1)
            var2 = np.var(y, ddof=1)
            pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
            d = mean_diff / pooled_std

        # Apply Hedges' correction for small samples
        if correction == 'hedges':
            # Hedges' g correction factor
            correction_factor = 1 - (3 / (4 * (n1 + n2) - 9))
            d = d * correction_factor

    return float(d)


def cliffs_delta(
    x: Union[np.ndarray, pd.Series],
    y: Union[np.ndarray, pd.Series]
) -> float:
    """
    Compute Cliff's delta non-parametric effect size.

    Parameters
    ----------
    x : array or Series
        First sample
    y : array or Series
        Second sample

    Returns
    -------
    float
        Cliff's delta value (ranges from -1 to 1)

    Notes
    -----
    Cliff's delta is a non-parametric effect size measure that quantifies
    the degree of dominance of one distribution over another.

    It is calculated as:

    .. math::
        \\delta = \\frac{\\#(x_i > y_j) - \\#(x_i < y_j)}{n_x \\cdot n_y}

    Where:
    - #(x_i > y_j) is the number of times values in x are greater than values in y
    - #(x_i < y_j) is the number of times values in x are less than values in y

    Interpretation:
    - |δ| < 0.147: negligible
    - |δ| < 0.33:  small
    - |δ| < 0.474: medium
    - |δ| ≥ 0.474: large

    Advantages:
    - Non-parametric (no assumptions about distributions)
    - Robust to outliers
    - Easy to interpret (probability-based)
    - Related to Mann-Whitney U statistic

    The relation to Mann-Whitney U is:

    .. math::
        \\delta = 2 \\cdot \\frac{U}{n_x \\cdot n_y} - 1

    References
    ----------
    .. [1] Cliff, N. (1993). "Dominance statistics: Ordinal analyses to answer
           ordinal questions". Psychological Bulletin, 114(3), 494-509.
    .. [2] Romano, J., Kromrey, J. D., Coraggio, J., & Skowronek, J. (2006).
           "Appropriate statistics for ordinal level data: Should we really be
           using t-test and Cohen's d for evaluating group differences on the
           NSSE and other surveys?" Florida Association of Institutional Research.

    Examples
    --------
    >>> x = np.array([1, 2, 3, 4, 5])
    >>> y = np.array([2, 3, 4, 5, 6])
    >>> cliffs_delta(x, y)
    -0.6

    >>> # No difference
    >>> x = np.array([1, 2, 3, 4, 5])
    >>> y = np.array([1, 2, 3, 4, 5])
    >>> cliffs_delta(x, y)
    0.0

    >>> # Complete dominance
    >>> x = np.array([6, 7, 8, 9, 10])
    >>> y = np.array([1, 2, 3, 4, 5])
    >>> cliffs_delta(x, y)
    1.0
    """
    # Convert to numpy arrays
    x = np.asarray(x)
    y = np.asarray(y)

    # Remove NaN values
    x = x[~np.isnan(x)]
    y = y[~np.isnan(y)]

    nx = len(x)
    ny = len(y)

    # Count comparisons
    # Vectorized computation: create all pairwise comparisons
    # x[:, None] creates column vector, y creates row vector
    # Broadcasting creates matrix of all pairwise comparisons
    more = np.sum(x[:, None] > y)
    less = np.sum(x[:, None] < y)

    # Compute Cliff's delta
    delta = (more - less) / (nx * ny)

    return float(delta)


def prob_superiority(
    x: Union[np.ndarray, pd.Series],
    y: Union[np.ndarray, pd.Series]
) -> float:
    """
    Compute probability of superiority P(X > Y).

    Also known as the common language effect size or probabilistic index.

    Parameters
    ----------
    x : array or Series
        First sample
    y : array or Series
        Second sample

    Returns
    -------
    float
        Probability that a random value from X is greater than a random value from Y
        (ranges from 0 to 1)

    Notes
    -----
    The probability of superiority is defined as:

    .. math::
        P(X > Y) = \\frac{\\#(x_i > y_j)}{n_x \\cdot n_y}

    This is the probabilistic interpretation of effect size and is directly
    related to the Brunner-Munzel statistic and Cliff's delta:

    .. math::
        P(X > Y) = \\frac{1 + \\delta}{2}

    Where δ is Cliff's delta.

    Interpretation:
    - P(X > Y) = 0.50: No effect (chance level)
    - P(X > Y) = 0.56: Small effect (McGraw & Wong, 1992)
    - P(X > Y) = 0.64: Medium effect
    - P(X > Y) = 0.71: Large effect

    Advantages:
    - Intuitive probabilistic interpretation
    - Non-parametric (distribution-free)
    - Directly comparable across studies
    - Used in Brunner-Munzel test

    This is also called:
    - Common Language Effect Size (CLES)
    - Area Under the Curve (AUC) in ROC analysis
    - Mann-Whitney U / (nx * ny)

    References
    ----------
    .. [1] McGraw, K. O., & Wong, S. P. (1992). "A common language effect size
           statistic". Psychological Bulletin, 111(2), 361-365.
    .. [2] Brunner, E., & Munzel, U. (2000). "The nonparametric Behrens-Fisher
           problem: Asymptotic theory and a small-sample approximation".
           Biometrical Journal, 42(1), 17-25.

    Examples
    --------
    >>> x = np.array([1, 2, 3, 4, 5])
    >>> y = np.array([2, 3, 4, 5, 6])
    >>> prob_superiority(x, y)
    0.2

    >>> # 20% chance a random X value exceeds a random Y value

    >>> # No difference (chance level)
    >>> x = np.array([1, 2, 3, 4, 5])
    >>> y = np.array([1, 2, 3, 4, 5])
    >>> prob_superiority(x, y)
    0.5

    >>> # Complete dominance
    >>> x = np.array([6, 7, 8, 9, 10])
    >>> y = np.array([1, 2, 3, 4, 5])
    >>> prob_superiority(x, y)
    1.0
    """
    # Convert to numpy arrays
    x = np.asarray(x)
    y = np.asarray(y)

    # Remove NaN values
    x = x[~np.isnan(x)]
    y = y[~np.isnan(y)]

    nx = len(x)
    ny = len(y)

    # Count how many times x > y
    more = np.sum(x[:, None] > y)

    # Compute probability
    prob = more / (nx * ny)

    return float(prob)


def interpret_prob_superiority(prob: float) -> str:
    """
    Interpret probability of superiority effect size.

    Parameters
    ----------
    prob : float
        Probability of superiority P(X > Y)

    Returns
    -------
    str
        Interpretation string

    Examples
    --------
    >>> interpret_prob_superiority(0.51)
    'negligible'
    >>> interpret_prob_superiority(0.60)
    'small'
    >>> interpret_prob_superiority(0.68)
    'medium'
    >>> interpret_prob_superiority(0.75)
    'large'
    """
    # Convert to distance from 0.5 (chance)
    distance = abs(prob - 0.5)

    if distance < 0.06:
        return 'negligible'
    elif distance < 0.14:
        return 'small'
    elif distance < 0.21:
        return 'medium'
    else:
        return 'large'


def interpret_cliffs_delta(delta: float) -> str:
    """
    Interpret Cliff's delta effect size.

    Parameters
    ----------
    delta : float
        Cliff's delta value

    Returns
    -------
    str
        Interpretation string

    Examples
    --------
    >>> interpret_cliffs_delta(0.1)
    'negligible'
    >>> interpret_cliffs_delta(0.25)
    'small'
    >>> interpret_cliffs_delta(0.4)
    'medium'
    >>> interpret_cliffs_delta(0.6)
    'large'
    """
    delta_abs = abs(delta)

    if delta_abs < 0.147:
        return 'negligible'
    elif delta_abs < 0.33:
        return 'small'
    elif delta_abs < 0.474:
        return 'medium'
    else:
        return 'large'


def eta_squared(
    groups: List[Union[np.ndarray, pd.Series]],
    ddof: int = 1
) -> float:
    """
    Compute eta-squared (η²) effect size for ANOVA.

    Parameters
    ----------
    groups : list of arrays or Series
        List of samples, one per group
    ddof : int, default 1
        Degrees of freedom correction for variance

    Returns
    -------
    float
        Eta-squared value (ranges from 0 to 1)

    Notes
    -----
    Eta-squared (η²) measures the proportion of total variance explained
    by group membership in ANOVA designs.

    .. math::
        \\eta^2 = \\frac{SS_{between}}{SS_{total}}

    Where:
    - SS_between: Sum of squares between groups
    - SS_total: Total sum of squares

    Interpretation (Cohen, 1988):
    - η² < 0.01:  negligible
    - η² < 0.06:  small
    - η² < 0.14:  medium
    - η² ≥ 0.14:  large

    **Variants:**
    - η²: Biased, overestimates population effect
    - ω² (omega-squared): Less biased estimate
    - partial η²: Used in factorial designs

    Relationship to F-statistic:

    .. math::
        \\eta^2 = \\frac{F \\cdot df_{between}}{F \\cdot df_{between} + df_{within}}

    References
    ----------
    .. [1] Cohen, J. (1988). Statistical Power Analysis for the Behavioral
           Sciences (2nd ed.). Routledge.
    .. [2] Richardson, J. T. E. (2011). "Eta squared and partial eta squared
           as measures of effect size in educational research". Educational
           Research Review, 6(2), 135-147.

    Examples
    --------
    >>> group1 = np.array([1, 2, 3, 4, 5])
    >>> group2 = np.array([3, 4, 5, 6, 7])
    >>> group3 = np.array([5, 6, 7, 8, 9])
    >>> eta_squared([group1, group2, group3])
    0.857...

    >>> # No effect
    >>> group1 = np.array([1, 2, 3, 4, 5])
    >>> group2 = np.array([1, 2, 3, 4, 5])
    >>> eta_squared([group1, group2])
    0.0
    """
    # Convert all groups to numpy arrays and remove NaN
    groups = [np.asarray(g) for g in groups]
    groups = [g[~np.isnan(g)] for g in groups]

    # Compute grand mean
    all_data = np.concatenate(groups)
    grand_mean = np.mean(all_data)

    # Compute total sum of squares
    ss_total = np.sum((all_data - grand_mean) ** 2)

    # Compute between-group sum of squares
    ss_between = 0
    for group in groups:
        group_mean = np.mean(group)
        n_group = len(group)
        ss_between += n_group * (group_mean - grand_mean) ** 2

    # Compute eta-squared
    if ss_total == 0:
        return 0.0

    eta2 = ss_between / ss_total

    return float(eta2)


def interpret_eta_squared(eta2: float) -> str:
    """
    Interpret eta-squared effect size.

    Parameters
    ----------
    eta2 : float
        Eta-squared value

    Returns
    -------
    str
        Interpretation string

    Examples
    --------
    >>> interpret_eta_squared(0.005)
    'negligible'
    >>> interpret_eta_squared(0.03)
    'small'
    >>> interpret_eta_squared(0.10)
    'medium'
    >>> interpret_eta_squared(0.20)
    'large'
    """
    if eta2 < 0.01:
        return 'negligible'
    elif eta2 < 0.06:
        return 'small'
    elif eta2 < 0.14:
        return 'medium'
    else:
        return 'large'


def epsilon_squared(groups):
    """
    Compute epsilon-squared (ε²) effect size for Kruskal-Wallis test.

    Parameters
    ----------
    groups : list of arrays
        List of sample arrays for each group

    Returns
    -------
    float
        Epsilon-squared value (0 to 1)

    Notes
    -----
    Epsilon-squared (ε²) is the non-parametric analog of eta-squared (η²)
    for the Kruskal-Wallis test. It measures the proportion of variance in
    ranks explained by group membership.

    .. math::
        \\epsilon^2 = \\frac{H}{(n^2 - 1) / (n + 1)}

    Where:
    - H: Kruskal-Wallis H statistic
    - n: Total sample size

    Alternative formula (based on ranks):

    .. math::
        \\epsilon^2 = \\frac{H - k + 1}{n - k}

    Where:
    - H: Kruskal-Wallis H statistic
    - k: Number of groups
    - n: Total sample size

    Interpretation (similar to η²):
    - ε² < 0.01:  negligible
    - ε² < 0.06:  small
    - ε² < 0.14:  medium
    - ε² ≥ 0.14:  large

    References
    ----------
    .. [1] Tomczak, M., & Tomczak, E. (2014). "The need to report effect size
           estimates revisited. An overview of some recommended measures of
           effect size". Trends in Sport Sciences, 21(1), 19-25.
    .. [2] Kerby, D. S. (2014). "The simple difference formula: An approach to
           teaching nonparametric correlation". Comprehensive Psychology, 3, 11.

    Examples
    --------
    >>> group1 = np.array([1, 2, 3, 4, 5])
    >>> group2 = np.array([3, 4, 5, 6, 7])
    >>> group3 = np.array([5, 6, 7, 8, 9])
    >>> epsilon_squared([group1, group2, group3])
    0.857...

    >>> # No effect
    >>> group1 = np.array([1, 2, 3, 4, 5])
    >>> group2 = np.array([1, 2, 3, 4, 5])
    >>> epsilon_squared([group1, group2])
    0.0
    """
    from scipy import stats

    # Convert all groups to numpy arrays and remove NaN
    groups = [np.asarray(g) for g in groups]
    groups = [g[~np.isnan(g)] for g in groups]

    # Get group sizes
    k = len(groups)
    n = sum(len(g) for g in groups)

    # Perform Kruskal-Wallis test to get H statistic
    h_stat, _ = stats.kruskal(*groups)

    # Compute epsilon-squared using H statistic
    # Formula: ε² = (H - k + 1) / (n - k)
    if n == k:
        return 0.0

    epsilon2 = (h_stat - k + 1) / (n - k)

    # Ensure value is in valid range [0, 1]
    epsilon2 = max(0.0, min(1.0, epsilon2))

    return float(epsilon2)


def interpret_epsilon_squared(epsilon2: float) -> str:
    """
    Interpret epsilon-squared effect size.

    Parameters
    ----------
    epsilon2 : float
        Epsilon-squared value

    Returns
    -------
    str
        Interpretation string

    Examples
    --------
    >>> interpret_epsilon_squared(0.005)
    'negligible'
    >>> interpret_epsilon_squared(0.03)
    'small'
    >>> interpret_epsilon_squared(0.10)
    'medium'
    >>> interpret_epsilon_squared(0.20)
    'large'
    """
    if epsilon2 < 0.01:
        return 'negligible'
    elif epsilon2 < 0.06:
        return 'small'
    elif epsilon2 < 0.14:
        return 'medium'
    else:
        return 'large'


def interpret_cohens_d(d: float) -> str:
    """
    Interpret Cohen's d effect size.

    Parameters
    ----------
    d : float
        Cohen's d value

    Returns
    -------
    str
        Interpretation string

    Examples
    --------
    >>> interpret_cohens_d(0.3)
    'small'
    >>> interpret_cohens_d(0.6)
    'medium'
    >>> interpret_cohens_d(0.9)
    'large'
    """
    d_abs = abs(d)

    if d_abs < 0.2:
        return 'negligible'
    elif d_abs < 0.5:
        return 'small'
    elif d_abs < 0.8:
        return 'medium'
    else:
        return 'large'


"""Main function"""
def main(args):
    """Demonstrate effect size computation (Cohen's d, Cliff's delta, eta-squared)."""
    logger.info("Demonstrating effect size calculations")

    # Set random seed for reproducibility
    np.random.seed(42)

    # Example 1: Different effect sizes
    logger.info("\n=== Example 1: Different effect sizes ===")

    n = 50
    control = np.random.normal(0, 1, n)

    effect_sizes = [0.0, 0.2, 0.5, 0.8, 1.2]
    results = []

    for true_d in effect_sizes:
        # Generate treatment group with specified effect size
        treatment = np.random.normal(true_d, 1, n)

        # Compute Cohen's d
        computed_d = cohens_d(control, treatment)
        interpretation = interpret_cohens_d(computed_d)

        logger.info(
            f"True d = {true_d:.1f}, "
            f"Computed d = {computed_d:.3f}, "
            f"Interpretation: {interpretation}"
        )

        results.append({
            'true_d': true_d,
            'computed_d': computed_d,
            'interpretation': interpretation
        })

    # Example 2: Paired vs independent
    logger.info("\n=== Example 2: Paired vs Independent ===")

    # Generate correlated paired samples
    n_pairs = 30
    baseline = np.random.normal(0, 1, n_pairs)
    noise = np.random.normal(0, 0.3, n_pairs)
    followup = baseline + 0.5 + noise  # Effect size ~0.5

    d_independent = cohens_d(baseline, followup, paired=False)
    d_paired = cohens_d(baseline, followup, paired=True)

    logger.info(f"Independent samples d = {d_independent:.3f}")
    logger.info(f"Paired samples d = {d_paired:.3f}")
    logger.info(f"Paired is more sensitive due to correlation")

    # Example 3: Correction methods
    logger.info("\n=== Example 3: Correction methods ===")

    small_n = 10
    x_small = np.random.normal(0, 1, small_n)
    y_small = np.random.normal(0.5, 1, small_n)

    d_standard = cohens_d(x_small, y_small)
    d_hedges = cohens_d(x_small, y_small, correction='hedges')
    d_glass = cohens_d(x_small, y_small, correction='glass')

    logger.info(f"Standard Cohen's d = {d_standard:.3f}")
    logger.info(f"Hedges' g = {d_hedges:.3f} (corrected for small n)")
    logger.info(f"Glass's delta = {d_glass:.3f} (uses control SD only)")

    # Example 4: Cliff's delta and P(X>Y) (non-parametric)
    logger.info("\n=== Example 4: Non-parametric effect sizes ===")

    x_cliff = np.array([1, 2, 3, 4, 5, 6, 7, 8])
    y_cliff = np.array([3, 4, 5, 6, 7, 8, 9, 10])

    delta = cliffs_delta(x_cliff, y_cliff)
    prob = prob_superiority(x_cliff, y_cliff)
    d_cohen = cohens_d(x_cliff, y_cliff)

    logger.info(f"Cliff's delta:       {delta:.3f} ({interpret_cliffs_delta(delta)})")
    logger.info(f"P(X > Y):            {prob:.3f} ({interpret_prob_superiority(prob)})")
    logger.info(f"Cohen's d:           {d_cohen:.3f}")
    logger.info(f"Relationship: P(X>Y) = (1 + δ) / 2 = {(1 + delta) / 2:.3f}")
    logger.info("Non-parametric measures are robust to outliers and distribution shape")

    # Example 5: Cliff's delta with outliers
    logger.info("\n=== Example 5: Cliff's delta robustness to outliers ===")

    x_normal = np.array([1, 2, 3, 4, 5])
    y_normal = np.array([3, 4, 5, 6, 7])
    x_outlier = np.array([1, 2, 3, 4, 100])  # Extreme outlier
    y_outlier = np.array([3, 4, 5, 6, 7])

    delta_normal = cliffs_delta(x_normal, y_normal)
    delta_outlier = cliffs_delta(x_outlier, y_outlier)
    d_normal = cohens_d(x_normal, y_normal)
    d_outlier = cohens_d(x_outlier, y_outlier)

    logger.info(f"Without outlier: Cliff's δ = {delta_normal:.3f}, Cohen's d = {d_normal:.3f}")
    logger.info(f"With outlier:    Cliff's δ = {delta_outlier:.3f}, Cohen's d = {d_outlier:.3f}")
    logger.info("Cliff's delta is stable, Cohen's d is inflated by outlier")

    # Example 6: Eta-squared for ANOVA
    logger.info("\n=== Example 6: Eta-squared for ANOVA ===")

    group1 = np.random.normal(0, 1, 30)
    group2 = np.random.normal(0.5, 1, 30)
    group3 = np.random.normal(1.0, 1, 30)

    eta2 = eta_squared([group1, group2, group3])
    eta2_interp = interpret_eta_squared(eta2)

    logger.info(f"Eta-squared = {eta2:.3f} ({eta2_interp})")
    logger.info(f"{eta2:.1%} of variance explained by group membership")

    # Example 7: Eta-squared with different group variances
    logger.info("\n=== Example 7: Effect size comparison across methods ===")

    control = np.random.normal(0, 1, 40)
    treatment = np.random.normal(0.6, 1, 40)

    d = cohens_d(control, treatment)
    delta = cliffs_delta(control, treatment)
    eta2_groups = eta_squared([control, treatment])

    prob = prob_superiority(control, treatment)

    logger.info(f"Cohen's d:     {d:.3f} ({interpret_cohens_d(d)})")
    logger.info(f"Cliff's delta: {delta:.3f} ({interpret_cliffs_delta(delta)})")
    logger.info(f"P(X > Y):      {prob:.3f} ({interpret_prob_superiority(prob)})")
    logger.info(f"Eta-squared:   {eta2_groups:.3f} ({interpret_eta_squared(eta2_groups)})")

    # Create visualization
    logger.info("\n=== Creating visualization ===")

    fig, axes = stx.plt.subplots(2, 2, figsize=(12, 10))

    # Plot 1: Effect size comparison
    ax = axes[0, 0]
    df_results = pd.DataFrame(results)
    ax.scatter(df_results['true_d'], df_results['computed_d'], s=100)
    ax.plot([-0.5, 1.5], [-0.5, 1.5], 'k--', alpha=0.5, label='Perfect agreement')
    ax.set_xlabel('True Effect Size')
    ax.set_ylabel('Computed Cohen\'s d')
    ax.set_title('True vs Computed Effect Sizes')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Plot 2: Distribution visualization
    ax = axes[0, 1]
    control_demo = np.random.normal(0, 1, 1000)
    treatment_demo = np.random.normal(0.8, 1, 1000)

    ax.hist(control_demo, bins=30, alpha=0.5, label='Control', density=True)
    ax.hist(treatment_demo, bins=30, alpha=0.5, label='Treatment', density=True)

    d_demo = cohens_d(control_demo, treatment_demo)
    ax.axvline(np.mean(control_demo), color='blue', linestyle='--', alpha=0.7)
    ax.axvline(np.mean(treatment_demo), color='orange', linestyle='--', alpha=0.7)

    ax.set_xlabel('Value')
    ax.set_ylabel('Density')
    ax.set_title(f'Distributions (Cohen\'s d = {d_demo:.2f})')
    ax.legend()

    # Plot 3: Effect size interpretation
    ax = axes[1, 0]
    d_values = np.linspace(-1.5, 1.5, 100)
    interpretations = [interpret_cohens_d(d) for d in d_values]

    # Color map
    color_map = {'negligible': 'lightgray', 'small': 'yellow',
                 'medium': 'orange', 'large': 'red'}
    colors = [color_map[i] for i in interpretations]

    ax.scatter(d_values, [0] * len(d_values), c=colors, s=50, alpha=0.7)
    ax.set_xlabel('Cohen\'s d')
    ax.set_yticks([])
    ax.set_title('Effect Size Interpretation')
    ax.axvline(0, color='black', linestyle='-', alpha=0.3)
    ax.axvline(0.2, color='black', linestyle='--', alpha=0.3)
    ax.axvline(0.5, color='black', linestyle='--', alpha=0.3)
    ax.axvline(0.8, color='black', linestyle='--', alpha=0.3)

    # Add labels
    ax.text(0.1, 0.5, 'Negligible', ha='center', fontsize=9)
    ax.text(0.35, 0.5, 'Small', ha='center', fontsize=9)
    ax.text(0.65, 0.5, 'Medium', ha='center', fontsize=9)
    ax.text(1.15, 0.5, 'Large', ha='center', fontsize=9)

    # Plot 4: Sample size vs precision
    ax = axes[1, 1]
    sample_sizes = [10, 20, 30, 50, 100, 200]
    precisions = []

    for n in sample_sizes:
        # Simulate multiple experiments
        ds = []
        for _ in range(100):
            x = np.random.normal(0, 1, n)
            y = np.random.normal(0.5, 1, n)  # True d = 0.5
            ds.append(cohens_d(x, y))

        precisions.append(np.std(ds))

    ax.plot(sample_sizes, precisions, 'o-', linewidth=2)
    ax.set_xlabel('Sample Size (per group)')
    ax.set_ylabel('Std Dev of Cohen\'s d')
    ax.set_title('Effect Size Precision vs Sample Size')
    ax.grid(True, alpha=0.3)
    ax.set_xscale('log')

    plt.tight_layout()

    # Save
    stx.io.save(fig, './cohens_d_demo.jpg')
    logger.info("Visualization saved")

    return 0


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Demonstrate Cohen\'s d effect size calculation'
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
