#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-01 17:00:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/stats/tests/parametric/_test_anova_rm.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
  - Perform repeated measures ANOVA for within-subjects designs
  - Test sphericity assumption (Mauchly's test)
  - Apply Greenhouse-Geisser correction when sphericity violated
  - Compute partial eta-squared effect size
  - Generate profile plots and distribution visualizations

Dependencies:
  - packages: numpy, pandas, scipy, matplotlib, pingouin

IO:
  - input: Data in wide or long format (subjects × conditions)
  - output: Test results (dict or DataFrame) and optional figure
"""

"""Imports"""
import numpy as np
import pandas as pd
from typing import Union, Optional, Literal, Tuple, List
from scipy import stats
import matplotlib.pyplot as plt
import matplotlib.axes
from ...utils._formatters import p2stars
from ...utils._normalizers import convert_results

HAS_PLT = True

# Try importing pingouin for sphericity test
try:
    import pingouin as pg
    HAS_PINGOUIN = True
except ImportError:
    HAS_PINGOUIN = False


def mauchly_sphericity(data: np.ndarray) -> Tuple[float, float, float]:
    """
    Compute Mauchly's test of sphericity.

    Parameters
    ----------
    data : array, shape (n_subjects, n_conditions)
        Data matrix

    Returns
    -------
    W : float
        Mauchly's W statistic
    chi2 : float
        Chi-square statistic
    pvalue : float
        p-value

    Notes
    -----
    Tests whether the variances of differences between conditions are equal.
    If p < 0.05, sphericity is violated.
    """
    n, k = data.shape

    # Compute difference matrix
    diffs = []
    for i in range(k):
        for j in range(i + 1, k):
            diffs.append(data[:, i] - data[:, j])

    diff_matrix = np.array(diffs).T  # shape: (n_subjects, n_pairs)

    # Covariance matrix of differences
    S = np.cov(diff_matrix, rowvar=False)

    # Mauchly's W statistic
    W = np.linalg.det(S) / (np.trace(S) / S.shape[0]) ** S.shape[0]

    # Chi-square approximation
    df = k * (k - 1) / 2 - 1
    chi2 = -(n - 1 - (2*k**2 - 3*k + 3) / (6*(k-1))) * np.log(W)
    pvalue = 1 - stats.chi2.cdf(chi2, df)

    return float(W), float(chi2), float(pvalue)


def greenhouse_geisser_epsilon(data: np.ndarray) -> float:
    """
    Compute Greenhouse-Geisser epsilon correction factor.

    Parameters
    ----------
    data : array, shape (n_subjects, n_conditions)
        Data matrix

    Returns
    -------
    epsilon : float
        GG epsilon (between 1/(k-1) and 1.0)

    Notes
    -----
    Used to correct degrees of freedom when sphericity is violated.
    epsilon = 1.0 indicates perfect sphericity.
    """
    n, k = data.shape

    # Compute covariance matrix
    centered = data - data.mean(axis=1, keepdims=True)
    S = np.dot(centered.T, centered) / (n - 1)

    # Compute epsilon
    trace_S = np.trace(S)
    trace_S2 = np.trace(np.dot(S, S))

    numerator = (k * trace_S) ** 2
    denominator = (k - 1) * (k * trace_S2 - trace_S ** 2)

    if denominator == 0:
        return 1.0

    epsilon = numerator / denominator

    # Bound epsilon
    epsilon = max(1.0 / (k - 1), min(epsilon, 1.0))

    return float(epsilon)


def partial_eta_squared_rm(ss_effect: float, ss_error: float) -> float:
    """
    Compute partial eta-squared for repeated measures.

    Parameters
    ----------
    ss_effect : float
        Sum of squares for the effect
    ss_error : float
        Sum of squares for error

    Returns
    -------
    eta_p2 : float
        Partial eta-squared

    Notes
    -----
    Partial η² = SS_effect / (SS_effect + SS_error)
    """
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


def test_anova_rm(
    data: Union[np.ndarray, pd.DataFrame],
    subject_col: Optional[str] = None,
    condition_col: Optional[str] = None,
    value_col: Optional[str] = None,
    condition_names: Optional[List[str]] = None,
    alpha: float = 0.05,
    correction: Literal['auto', 'none', 'gg'] = 'auto',
    check_sphericity: bool = True,
    plot: bool = False,
    ax: Optional[matplotlib.axes.Axes] = None,
    return_as: Literal['dict', 'dataframe'] = 'dict',
    decimals: int = 3,
    verbose: bool = False
) -> Union[dict, pd.DataFrame, Tuple]:
    """
    Perform repeated measures ANOVA for within-subjects designs.

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
    correction : {'auto', 'none', 'gg'}, default 'auto'
        Correction method:
        - 'auto': Apply GG correction if sphericity violated
        - 'none': No correction
        - 'gg': Always apply Greenhouse-Geisser correction
    check_sphericity : bool, default True
        Whether to test sphericity assumption
    plot : bool, default False
        Whether to generate profile plot
    ax : matplotlib.axes.Axes, optional
        Axes object to plot on. If None and plot=True, creates new figure.
        If provided, automatically enables plotting.
    return_as : {'dict', 'dataframe'}, default 'dict'
        Output format
    decimals : int, default 3
        Number of decimal places for rounding
    verbose : bool, default False
        Whether to print test results

    Returns
    -------
    result : dict or DataFrame
        Test results including:
        - statistic: F-statistic
        - pvalue: p-value (possibly corrected)
        - df_effect: Degrees of freedom for effect
        - df_error: Degrees of freedom for error
        - effect_size: Partial eta-squared
        - sphericity_W: Mauchly's W (if checked)
        - sphericity_pvalue: Sphericity test p-value
        - sphericity_met: Whether sphericity assumption met
        - epsilon_gg: Greenhouse-Geisser epsilon
        - correction_applied: Which correction was applied
        - significant: Whether to reject null hypothesis

    If plot=True, returns tuple of (result, figure)

    Notes
    -----
    Repeated measures ANOVA tests whether the means differ across multiple
    conditions measured on the same subjects (within-subjects factor).

    **Null Hypothesis (H0)**: All condition means are equal

    **Assumptions**:
    1. **Independence of subjects**: Different subjects are independent
    2. **Normality**: Differences between conditions are normally distributed
    3. **Sphericity**: Variances of differences between all pairs of conditions
       are equal (tested with Mauchly's test)

    **Sphericity**:
    The sphericity assumption is unique to repeated measures ANOVA. If violated:
    - Greenhouse-Geisser correction: More conservative, use when ε < 0.75
    - Huynh-Feldt correction: Less conservative (not implemented)
    - Multivariate approach: MANOVA (not implemented)

    **Greenhouse-Geisser Correction**:
    Adjusts degrees of freedom by multiplying by epsilon (ε):
    - df_effect_adj = ε × df_effect
    - df_error_adj = ε × df_error

    **Effect Size (Partial η²)**:

    .. math::
        \\eta_p^2 = \\frac{SS_{effect}}{SS_{effect} + SS_{error}}

    Interpretation same as regular eta-squared:
    - < 0.01: negligible
    - < 0.06: small
    - < 0.14: medium
    - ≥ 0.14: large

    **Post-hoc tests**:
    If significant, use pairwise t-tests with correction:
    - test_ttest_rel() for all pairs
    - correct_bonferroni() or correct_holm() for multiple comparisons

    Examples
    --------
    >>> import numpy as np
    >>> from scitex.stats.tests.parametric import test_anova_rm
    >>>
    >>> # Wide format: subjects × conditions
    >>> data = np.array([
    ...     [5.2, 6.1, 7.3, 6.8],  # Subject 1
    ...     [4.8, 5.9, 6.7, 6.2],  # Subject 2
    ...     [5.5, 6.4, 7.1, 7.0],  # Subject 3
    ...     [4.9, 5.7, 6.9, 6.5],  # Subject 4
    ... ])
    >>>
    >>> result = test_anova_rm(
    ...     data,
    ...     condition_names=['Baseline', 'Week 1', 'Week 2', 'Week 3'],
    ...     plot=True
    ... )
    >>>
    >>> print(f"F = {result['statistic']:.2f}, p = {result['pvalue']:.4f}")
    >>> print(f"Sphericity met: {result['sphericity_met']}")
    >>> print(f"Partial η² = {result['effect_size']:.3f}")

    References
    ----------
    .. [1] Greenhouse, S. W., & Geisser, S. (1959). "On methods in the analysis
           of profile data". Psychometrika, 24(2), 95-112.
    .. [2] Mauchly, J. W. (1940). "Significance test for sphericity of a normal
           n-variate distribution". The Annals of Mathematical Statistics,
           11(2), 204-209.

    See Also
    --------
    test_anova : One-way ANOVA for independent samples
    test_friedman : Non-parametric alternative (no sphericity assumption)
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

    if n_conditions < 2:
        raise ValueError("Need at least 2 conditions for repeated measures ANOVA")

    if condition_names is None:
        condition_names = [f'Condition {i+1}' for i in range(n_conditions)]

    # Compute ANOVA
    grand_mean = data_array.mean()
    subject_means = data_array.mean(axis=1)
    condition_means = data_array.mean(axis=0)

    # Sum of squares
    ss_total = np.sum((data_array - grand_mean) ** 2)
    ss_subjects = n_conditions * np.sum((subject_means - grand_mean) ** 2)
    ss_conditions = n_subjects * np.sum((condition_means - grand_mean) ** 2)
    ss_error = ss_total - ss_subjects - ss_conditions

    # Degrees of freedom
    df_conditions = n_conditions - 1
    df_subjects = n_subjects - 1
    df_error = df_conditions * df_subjects

    # Mean squares
    ms_conditions = ss_conditions / df_conditions
    ms_error = ss_error / df_error

    # F-statistic
    F_stat = ms_conditions / ms_error

    # Initial p-value (uncorrected)
    pvalue = 1 - stats.f.cdf(F_stat, df_conditions, df_error)

    # Test sphericity
    sphericity_met = True
    sphericity_W = None
    sphericity_chi2 = None
    sphericity_pvalue = None
    epsilon_gg = None
    correction_applied = 'none'

    if check_sphericity and n_conditions > 2:
        try:
            if HAS_PINGOUIN:
                # Use pingouin for robust sphericity test
                spher = pg.sphericity(data_array, method='mauchly')
                sphericity_W = spher[0]
                sphericity_chi2 = spher[1]
                sphericity_pvalue = spher[2]
            else:
                # Use our implementation
                sphericity_W, sphericity_chi2, sphericity_pvalue = mauchly_sphericity(data_array)

            sphericity_met = sphericity_pvalue >= alpha

            # Compute Greenhouse-Geisser epsilon
            if HAS_PINGOUIN:
                epsilon_gg = pg.epsilon(data_array, correction='gg')
            else:
                epsilon_gg = greenhouse_geisser_epsilon(data_array)

            # Apply correction if needed
            if correction == 'gg' or (correction == 'auto' and not sphericity_met):
                # Adjust degrees of freedom
                df_conditions_adj = df_conditions * epsilon_gg
                df_error_adj = df_error * epsilon_gg
                pvalue = 1 - stats.f.cdf(F_stat, df_conditions_adj, df_error_adj)
                correction_applied = 'greenhouse-geisser'
                df_conditions = df_conditions_adj
                df_error = df_error_adj

        except Exception as e:
            # If sphericity test fails, continue without it
            import warnings
            warnings.warn(f"Sphericity test failed: {e}. Proceeding without correction.")
            sphericity_met = None

    # Compute effect size (partial eta-squared)
    partial_eta2 = partial_eta_squared_rm(ss_conditions, ss_error)
    eta2_interpretation = interpret_eta_squared(partial_eta2)

    # Build result dictionary
    result = {
        'test': 'Repeated Measures ANOVA',
        'statistic': round(float(F_stat), decimals),
        'pvalue': round(float(pvalue), decimals + 1),
        'df_effect': round(float(df_conditions), decimals),
        'df_error': round(float(df_error), decimals),
        'n_subjects': int(n_subjects),
        'n_conditions': int(n_conditions),
        'condition_names': condition_names,
        'effect_size': round(float(partial_eta2), decimals),
        'effect_size_metric': 'partial_eta_squared',
        'effect_size_interpretation': eta2_interpretation,
        'alpha': alpha,
        'significant': pvalue < alpha,
        'stars': p2stars(pvalue),
    }

    # Add sphericity results
    if sphericity_W is not None:
        result['sphericity_W'] = round(float(sphericity_W), decimals)
        result['sphericity_chi2'] = round(float(sphericity_chi2), decimals)
        result['sphericity_pvalue'] = round(float(sphericity_pvalue), decimals + 1)
        result['sphericity_met'] = sphericity_met
        result['epsilon_gg'] = round(float(epsilon_gg), decimals)
        result['correction_applied'] = correction_applied

    # Log results if verbose
    if verbose:
        from scitex.logging import getLogger
        logger = getLogger(__name__)
        logger.info(f"Repeated Measures ANOVA: F({result['df_effect']:.1f}, {result['df_error']:.1f}) = {result['statistic']:.3f}, p = {result['pvalue']:.4f} {result['stars']}")
        logger.info(f"Partial η² = {result['effect_size']:.3f} ({result['effect_size_interpretation']})")
        if 'sphericity_met' in result:
            logger.info(f"Sphericity met: {result['sphericity_met']}")

    # Auto-enable plotting if ax is provided
    if ax is not None:
        plot = True

    # Generate plot if requested
    fig = None
    if plot and HAS_PLT:
        if ax is None:
            fig = _plot_anova_rm(data_array, condition_names, result)
        else:
            # Use provided axes (not fully implemented for 1x3 layout)
            fig = _plot_anova_rm(data_array, condition_names, result)

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


def _plot_anova_rm(data, condition_names, result):
    """Create visualization for repeated measures ANOVA."""
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    n_subjects, n_conditions = data.shape
    conditions = np.arange(n_conditions)

    # Panel 1: Profile plot (individual subjects)
    ax = axes[0]
    for i in range(n_subjects):
        ax.plot(conditions, data[i, :], marker='o', alpha=0.3, color='gray', linewidth=0.5)

    # Add mean profile
    means = data.mean(axis=0)
    sems = data.std(axis=0) / np.sqrt(n_subjects)
    ax.plot(conditions, means, marker='o', color='red', linewidth=2.5, markersize=8,
           label='Mean', zorder=10)
    ax.fill_between(conditions, means - sems, means + sems, alpha=0.3, color='red',
                    label='±SEM')

    ax.set_xticks(conditions)
    ax.set_xticklabels(condition_names, rotation=45, ha='right')
    ax.set_xlabel('Condition', fontsize=12)
    ax.set_ylabel('Value', fontsize=12)
    ax.set_title('Profile Plot', fontsize=12, fontweight='bold')
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)

    # Panel 2: Box plots
    ax = axes[1]
    positions = np.arange(1, n_conditions + 1)
    bp = ax.boxplot([data[:, i] for i in range(n_conditions)],
                    positions=positions,
                    widths=0.6,
                    patch_artist=True)

    # Color boxes
    for patch in bp['boxes']:
        patch.set_facecolor('lightblue')
        patch.set_alpha(0.7)

    ax.set_xticks(positions)
    ax.set_xticklabels(condition_names, rotation=45, ha='right')
    ax.set_xlabel('Condition', fontsize=12)
    ax.set_ylabel('Value', fontsize=12)
    ax.set_title('Distribution by Condition', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')

    # Panel 3: Results summary
    ax = axes[2]
    ax.axis('off')

    result_text = "Repeated Measures ANOVA\n"
    result_text += "=" * 35 + "\n\n"
    result_text += f"F({result['df_effect']:.1f}, {result['df_error']:.1f}) = {result['statistic']:.3f}\n"
    result_text += f"p-value = {result['pvalue']:.4f} {result['stars']}\n\n"
    result_text += f"Partial η² = {result['effect_size']:.3f}\n"
    result_text += f"Interpretation: {result['effect_size_interpretation']}\n\n"

    if 'sphericity_W' in result:
        result_text += "Sphericity Test:\n"
        result_text += f"  Mauchly's W = {result['sphericity_W']:.3f}\n"
        result_text += f"  p = {result['sphericity_pvalue']:.4f}\n"
        result_text += f"  Met: {'Yes' if result['sphericity_met'] else 'No'}\n\n"
        if result['correction_applied'] != 'none':
            result_text += f"  ε_GG = {result['epsilon_gg']:.3f}\n"
            result_text += f"  Correction: {result['correction_applied']}\n\n"

    result_text += f"Subjects: {result['n_subjects']}\n"
    result_text += f"Conditions: {result['n_conditions']}\n"
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

"""Main function"""
def main(args):
    logger.info("=" * 70)
    logger.info("Repeated Measures ANOVA Examples")
    logger.info("=" * 70)

    # Example 1: Basic repeated measures (4 time points)
    logger.info("\n[Example 1] Basic repeated measures - 4 time points")
    logger.info("-" * 70)

    np.random.seed(42)
    n_subjects = 12
    # Simulate increasing trend over time
    time_effects = np.array([0, 0.5, 1.0, 0.8])
    data = np.random.normal(5, 1, (n_subjects, 4)) + time_effects

    result = test_anova_rm(
        data,
        condition_names=['Baseline', 'Week 1', 'Week 2', 'Week 3'],
        plot=True,
        verbose=True
    )
    stx.io.save(plt.gcf(), "./.dev/anova_rm_example1.jpg")
    plt.close()

    logger.info(f"F({result['df_effect']:.1f}, {result['df_error']:.1f}) = {result['statistic']:.3f}")
    logger.info(f"p-value = {result['pvalue']:.4f} {result['stars']}")
    logger.info(f"Partial η² = {result['effect_size']:.3f} ({result['effect_size_interpretation']})")
    if 'sphericity_met' in result:
        logger.info(f"Sphericity met: {result['sphericity_met']}")

    # Example 2: Sphericity violation
    logger.info("\n[Example 2] Data with sphericity violation")
    logger.info("-" * 70)

    # Create data that violates sphericity
    data_spher = np.random.normal(0, 1, (15, 4))
    data_spher[:, 1] += np.random.normal(0, 2, 15)  # High variance for condition 2
    data_spher[:, 2] += np.random.normal(0.5, 0.5, 15)

    result_spher = test_anova_rm(
        data_spher,
        condition_names=['T1', 'T2', 'T3', 'T4'],
        correction='auto',
        plot=True,
        verbose=True
    )
    stx.io.save(plt.gcf(), "./.dev/anova_rm_example2.jpg")
    plt.close()

    logger.info(f"Sphericity W = {result_spher.get('sphericity_W', 'N/A')}")
    logger.info(f"Sphericity p = {result_spher.get('sphericity_pvalue', 'N/A')}")
    logger.info(f"Correction applied: {result_spher.get('correction_applied', 'none')}")
    logger.info(f"Adjusted F({result_spher['df_effect']:.2f}, {result_spher['df_error']:.2f}) = {result_spher['statistic']:.3f}")
    logger.info(f"p-value = {result_spher['pvalue']:.4f}")

    # Example 3: Long format DataFrame
    logger.info("\n[Example 3] Long format DataFrame input")
    logger.info("-" * 70)

    # Create long format data
    subjects = np.repeat(np.arange(10), 3)
    conditions = np.tile(['Pre', 'Mid', 'Post'], 10)
    values = np.random.normal(10, 2, 30) + np.tile([0, 1, 1.5], 10)

    df_long = pd.DataFrame({
        'Subject': subjects,
        'TimePoint': conditions,
        'Score': values
    })

    result_long = test_anova_rm(
        df_long,
        subject_col='Subject',
        condition_col='TimePoint',
        value_col='Score',
        plot=True,
        verbose=True
    )
    stx.io.save(plt.gcf(), "./.dev/anova_rm_example3.jpg")
    plt.close()

    logger.info(f"F = {result_long['statistic']:.3f}, p = {result_long['pvalue']:.4f}")
    logger.info(f"Conditions: {result_long['condition_names']}")

    # Example 4: Wide format DataFrame
    logger.info("\n[Example 4] Wide format DataFrame")
    logger.info("-" * 70)

    df_wide = pd.DataFrame(
        np.random.normal(50, 10, (20, 5)),
        columns=['Drug_0mg', 'Drug_5mg', 'Drug_10mg', 'Drug_15mg', 'Drug_20mg']
    )
    # Add dose-response trend
    for i, dose in enumerate([0, 5, 10, 15, 20]):
        df_wide.iloc[:, i] += dose * 0.5

    result_wide = test_anova_rm(df_wide, plot=True, verbose=True)
    stx.io.save(plt.gcf(), "./.dev/anova_rm_example4.jpg")
    plt.close()

    logger.info(f"F = {result_wide['statistic']:.3f}, p = {result_wide['pvalue']:.4f}")
    logger.info(f"Partial η² = {result_wide['effect_size']:.3f}")

    # Example 5: Export results
    logger.info("\n[Example 5] Export results")
    logger.info("-" * 70)

    convert_results(result, return_as='excel', path='./.dev/anova_rm_results.xlsx')
    logger.info("Saved to: ./.dev/anova_rm_results.xlsx")

# EOF

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
