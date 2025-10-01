#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-01 15:05:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/stats/correct/_correct_bonferroni.py

"""
Functionalities:
  - Apply Bonferroni correction for multiple comparisons
  - Adjust p-values and significance thresholds
  - Support both dict and DataFrame inputs
  - Maintain full result information with adjusted values

Dependencies:
  - packages: numpy, pandas

IO:
  - input: Test results with p-values (dict, list of dicts, or DataFrame)
  - output: Results with adjusted p-values and significance (same format as input)
"""

"""Imports"""
import sys
import argparse
import numpy as np
import pandas as pd
from typing import Union, List, Dict, Any
import scitex as stx
from scitex.logging import getLogger

logger = getLogger(__name__)

"""Functions"""
def correct_bonferroni(
    results: Union[Dict[str, Any], List[Dict[str, Any]], pd.DataFrame],
    alpha: float = 0.05,
    return_as: str = None
) -> Union[Dict[str, Any], List[Dict[str, Any]], pd.DataFrame]:
    """
    Apply Bonferroni correction for multiple comparisons.

    Parameters
    ----------
    results : dict, list of dict, or DataFrame
        Test results containing 'pvalue' field(s)
        - Single dict: one test result
        - List of dicts: multiple test results
        - DataFrame: multiple test results (one per row)
    alpha : float, default 0.05
        Family-wise error rate (FWER) to control
    return_as : {'dict', 'dataframe', None}, optional
        Force specific return format. If None, matches input format.

    Returns
    -------
    results : dict, list of dict, or DataFrame
        Results with added fields:
        - pvalue_adjusted: Bonferroni-adjusted p-value
        - alpha_adjusted: Bonferroni-adjusted alpha threshold
        - rejected: Whether null hypothesis is rejected (using adjusted values)
        - pstars: Significance stars (using adjusted p-value)

    Notes
    -----
    The Bonferroni correction is the most conservative method for controlling
    the family-wise error rate (FWER) in multiple comparisons.

    For m tests with family-wise error rate α:

    .. math::
        p_{adj,i} = \\min(m \\cdot p_i, 1.0)

    .. math::
        \\alpha_{adj} = \\frac{\\alpha}{m}

    The method guarantees:

    .. math::
        P(\\text{at least one false positive}) \\leq \\alpha

    **Advantages:**
    - Simple and intuitive
    - Strong FWER control
    - No assumptions about test dependencies

    **Disadvantages:**
    - Very conservative (low statistical power)
    - Power decreases linearly with number of tests
    - May miss true effects (Type II errors)

    **When to use:**
    - Small number of planned comparisons (m < 10)
    - Need strict control of false positives
    - Tests are independent or positively correlated

    References
    ----------
    .. [1] Bonferroni, C. E. (1936). "Teoria statistica delle classi e calcolo
           delle probabilità". Pubblicazioni del R Istituto Superiore di
           Scienze Economiche e Commerciali di Firenze, 8, 3-62.
    .. [2] Dunn, O. J. (1961). "Multiple Comparisons Among Means". Journal of
           the American Statistical Association, 56(293), 52-64.

    Examples
    --------
    >>> # Single test (no correction needed)
    >>> result = {'pvalue': 0.04, 'var_x': 'A', 'var_y': 'B'}
    >>> corrected = correct_bonferroni(result)
    >>> corrected['pvalue_adjusted']
    0.04

    >>> # Multiple tests
    >>> results = [
    ...     {'pvalue': 0.01, 'var_x': 'A', 'var_y': 'B'},
    ...     {'pvalue': 0.03, 'var_x': 'A', 'var_y': 'C'},
    ...     {'pvalue': 0.05, 'var_x': 'B', 'var_y': 'C'}
    ... ]
    >>> corrected = correct_bonferroni(results)
    >>> [r['pvalue_adjusted'] for r in corrected]
    [0.03, 0.09, 0.15]

    >>> # DataFrame input
    >>> df = pd.DataFrame({'pvalue': [0.01, 0.03, 0.05]})
    >>> df_corrected = correct_bonferroni(df)
    >>> df_corrected['alpha_adjusted'].iloc[0]
    0.0166...
    """
    from ..utils._formatters import p2stars
    from ..utils._normalizers import force_dataframe, to_dict

    # Store original input type
    input_type = type(results)
    is_single_dict = isinstance(results, dict)

    # Convert to DataFrame for processing
    if isinstance(results, dict):
        results_list = [results]
    elif isinstance(results, list):
        results_list = results
    else:  # DataFrame
        results_list = None

    if results_list is not None:
        df = force_dataframe(results_list, fill_na=False, enforce_types=False)
    else:
        df = results.copy()

    # Number of tests
    m = len(df)

    # Compute adjusted p-values (Bonferroni)
    df['pvalue_adjusted'] = np.minimum(df['pvalue'] * m, 1.0)

    # Compute adjusted alpha threshold
    if 'alpha' in df.columns:
        alpha_values = df['alpha'].fillna(alpha)
    else:
        alpha_values = alpha

    df['alpha_adjusted'] = alpha_values / m

    # Update rejection decisions based on adjusted values
    df['rejected'] = df['pvalue_adjusted'] < df['alpha_adjusted']

    # Update significance stars based on adjusted p-values
    df['pstars'] = df['pvalue_adjusted'].apply(p2stars)

    # Determine return format
    if return_as == 'dataframe':
        return df
    elif return_as == 'dict':
        if is_single_dict:
            return to_dict(df, row=0)
        else:
            return df.to_dict('records')
    else:
        # Match input format
        if input_type == dict:
            return to_dict(df, row=0)
        elif input_type == list:
            return df.to_dict('records')
        else:  # DataFrame
            return df


"""Main function"""
def main(args):
    """Demonstrate Bonferroni correction."""
    logger.info("Demonstrating Bonferroni correction")

    # Example 1: Single test (no correction needed)
    logger.info("\n=== Example 1: Single test ===")

    single_result = {
        'var_x': 'Control',
        'var_y': 'Treatment',
        'pvalue': 0.04,
        'alpha': 0.05
    }

    corrected_single = correct_bonferroni(single_result)

    logger.info(f"Original p-value: {single_result['pvalue']}")
    logger.info(f"Adjusted p-value: {corrected_single['pvalue_adjusted']:.4f}")
    logger.info(f"Adjusted alpha:   {corrected_single['alpha_adjusted']:.4f}")
    logger.info(f"Rejected: {corrected_single['rejected']}")

    # Example 2: Multiple tests
    logger.info("\n=== Example 2: Three pairwise comparisons ===")

    multiple_results = [
        {'var_x': 'A', 'var_y': 'B', 'pvalue': 0.01},
        {'var_x': 'A', 'var_y': 'C', 'pvalue': 0.03},
        {'var_x': 'B', 'var_y': 'C', 'pvalue': 0.05}
    ]

    corrected_multiple = correct_bonferroni(multiple_results, alpha=0.05)

    for i, (orig, corr) in enumerate(zip(multiple_results, corrected_multiple), 1):
        logger.info(
            f"Test {i} ({corr['var_x']} vs {corr['var_y']}): "
            f"p = {orig['pvalue']:.3f} → {corr['pvalue_adjusted']:.3f} "
            f"{corr['pstars']}, rejected = {corr['rejected']}"
        )

    # Example 3: Many tests (demonstrate conservativeness)
    logger.info("\n=== Example 3: Many tests (m=20) ===")

    np.random.seed(42)
    many_results = []

    for i in range(20):
        # Mix of significant and non-significant
        p = np.random.uniform(0.001, 0.1)
        many_results.append({
            'var_x': f'Var_{i}',
            'var_y': 'Control',
            'pvalue': p
        })

    corrected_many = correct_bonferroni(many_results)

    # Count rejections
    n_rejected_before = sum(r['pvalue'] < 0.05 for r in many_results)
    n_rejected_after = sum(r['rejected'] for r in corrected_many)

    logger.info(f"Tests with p < 0.05 before correction: {n_rejected_before}")
    logger.info(f"Tests rejected after correction:       {n_rejected_after}")
    logger.info(f"Adjusted alpha threshold: {corrected_many[0]['alpha_adjusted']:.4f}")

    # Example 4: DataFrame input/output
    logger.info("\n=== Example 4: DataFrame workflow ===")

    df_input = pd.DataFrame({
        'var_x': ['A', 'A', 'B'],
        'var_y': ['B', 'C', 'C'],
        'pvalue': [0.002, 0.025, 0.048],
        'effect_size': [0.8, 0.5, 0.3]
    })

    logger.info("\nBefore correction:")
    logger.info(df_input[['var_x', 'var_y', 'pvalue']])

    df_corrected = correct_bonferroni(df_input)

    logger.info("\nAfter correction:")
    logger.info(
        df_corrected[['var_x', 'var_y', 'pvalue', 'pvalue_adjusted',
                      'alpha_adjusted', 'pstars', 'rejected']]
    )

    # Create visualization
    logger.info("\n=== Creating visualization ===")

    fig, axes = stx.plt.subplots(2, 2, figsize=(12, 10))

    # Plot 1: Adjusted vs original p-values
    ax = axes[0, 0]

    m_vals = [3, 5, 10, 20]
    p_orig = 0.03

    for m in m_vals:
        p_adj = min(p_orig * m, 1.0)
        ax.scatter(m, p_adj, s=100, label=f'm = {m}')

    ax.axhline(0.05, color='red', linestyle='--', alpha=0.5, label='α = 0.05')
    ax.axhline(p_orig, color='blue', linestyle='--', alpha=0.5, label='Original p')
    ax.set_xlabel('Number of Tests (m)')
    ax.set_ylabel('Adjusted P-value')
    ax.set_title(f'Bonferroni Adjustment (p_original = {p_orig})')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Plot 2: Power loss with increasing tests
    ax = axes[0, 1]

    m_range = np.arange(1, 51)
    alpha = 0.05
    alpha_adj = alpha / m_range

    ax.plot(m_range, alpha_adj, linewidth=2)
    ax.axhline(0.05, color='red', linestyle='--', alpha=0.5, label='Original α')
    ax.set_xlabel('Number of Tests (m)')
    ax.set_ylabel('Adjusted α Threshold')
    ax.set_title('Bonferroni: Threshold Decreases Linearly')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_yscale('log')

    # Plot 3: Before/after comparison
    ax = axes[1, 0]

    # Generate test results
    np.random.seed(42)
    n_tests = 15
    p_values = np.random.beta(2, 20, n_tests)  # Mix of small p-values
    p_adjusted = np.minimum(p_values * n_tests, 1.0)

    x_pos = np.arange(n_tests)
    width = 0.35

    bars1 = ax.bar(x_pos - width/2, p_values, width, label='Original', alpha=0.7)
    bars2 = ax.bar(x_pos + width/2, p_adjusted, width, label='Adjusted', alpha=0.7)

    # Color bars by significance
    for i, (p_orig, p_adj) in enumerate(zip(p_values, p_adjusted)):
        if p_orig < 0.05:
            bars1[i].set_color('green')
        else:
            bars1[i].set_color('gray')

        if p_adj < 0.05:
            bars2[i].set_color('green')
        else:
            bars2[i].set_color('gray')

    ax.axhline(0.05, color='red', linestyle='--', alpha=0.5, linewidth=2)
    ax.set_xlabel('Test Index')
    ax.set_ylabel('P-value')
    ax.set_title('Before vs After Bonferroni Correction')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')

    # Plot 4: Comparison table
    ax = axes[1, 1]
    ax.axis('off')

    # Create comparison data
    methods_data = [
        ['Method', 'Adjusted α\n(m=10)', 'Power', 'FWER Control'],
        ['None', '0.050', 'High', 'No'],
        ['Bonferroni', '0.005', 'Low', 'Strong'],
        ['Holm', '0.005-0.05', 'Medium', 'Strong'],
        ['FDR', '~0.05', 'High', 'Weak (FDR)'],
    ]

    table = ax.table(
        cellText=methods_data,
        cellLoc='center',
        loc='center',
        bbox=[0, 0, 1, 1]
    )

    table.auto_set_font_size(False)
    table.set_fontsize(10)

    # Header styling
    for i in range(4):
        table[(0, i)].set_facecolor('#40466e')
        table[(0, i)].set_text_props(weight='bold', color='white')

    # Row styling
    for i in range(1, 5):
        for j in range(4):
            if i % 2 == 0:
                table[(i, j)].set_facecolor('#f0f0f0')

    ax.set_title('Multiple Comparison Methods Comparison', pad=20, fontweight='bold')

    plt.tight_layout()

    # Save
    stx.io.save(fig, './bonferroni_demo.png')
    logger.info("Visualization saved")

    return 0


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Demonstrate Bonferroni correction'
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
