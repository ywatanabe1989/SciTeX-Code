#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-01 17:00:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/stats/correct/_correct_holm.py

"""
Functionalities:
  - Perform Holm-Bonferroni correction for multiple comparisons
  - More powerful than standard Bonferroni while controlling FWER
  - Sequential rejection procedure
  - Support dict, list, or DataFrame inputs

Dependencies:
  - packages: numpy, pandas

IO:
  - input: Test results (dict, list of dicts, or DataFrame)
  - output: Corrected results with adjusted p-values
"""

"""Imports"""
import sys
import argparse
import numpy as np
import pandas as pd
from typing import Union, List, Dict
import scitex as stx
from scitex.logging import getLogger

logger = getLogger(__name__)

"""Functions"""
def correct_holm(
    results: Union[Dict, List[Dict], pd.DataFrame],
    alpha: float = 0.05
) -> Union[List[Dict], pd.DataFrame]:
    """
    Apply Holm-Bonferroni correction for multiple comparisons.

    Parameters
    ----------
    results : dict, list of dicts, or DataFrame
        Statistical test results containing 'pvalue' field
    alpha : float, default 0.05
        Family-wise error rate (FWER)

    Returns
    -------
    corrected_results : list of dicts or DataFrame
        Results with added fields:
        - pvalue_adjusted: Adjusted p-value
        - alpha_adjusted: Adjusted alpha threshold (for reference)
        - rejected: Whether null hypothesis is rejected after correction

    Notes
    -----
    The Holm-Bonferroni method (Holm, 1979) is a sequentially rejective
    multiple testing procedure that controls the family-wise error rate (FWER).
    It is uniformly more powerful than the standard Bonferroni correction.

    **Procedure**:
    1. Order p-values from smallest to largest: p₁ ≤ p₂ ≤ ... ≤ pₘ
    2. For each i = 1, 2, ..., m:
       - Compare pᵢ with α/(m - i + 1)
       - Reject H₀ᵢ if pᵢ ≤ α/(m - i + 1)
       - Stop at the first i where pᵢ > α/(m - i + 1)
       - Reject all H₀₁, ..., H₀ᵢ₋₁; accept all others

    **Adjusted p-values**:
    For reporting, adjusted p-values are computed as:

    .. math::
        \\tilde{p}_i = \\max_{j \\leq i} \\{(m - j + 1) p_j\\}

    Ensuring monotonicity: p̃₁ ≤ p̃₂ ≤ ... ≤ p̃ₘ

    **Advantages over Bonferroni**:
    - More powerful (detects more true positives)
    - Still controls FWER at level α
    - Simple step-down procedure
    - No independence assumption required

    **When to use**:
    - Multiple pairwise comparisons (e.g., post-hoc tests after ANOVA)
    - Want stronger control than FDR but more power than Bonferroni
    - Number of tests is moderate (m < 100)

    **Comparison with other methods**:
    - **Bonferroni**: More conservative, less powerful
    - **FDR (Benjamini-Hochberg)**: More powerful, controls different error rate
    - **Šidák**: Similar to Bonferroni, assumes independence

    References
    ----------
    .. [1] Holm, S. (1979). "A simple sequentially rejective multiple test
           procedure". Scandinavian Journal of Statistics, 6(2), 65-70.
    .. [2] Aickin, M., & Gensler, H. (1996). "Adjusting for multiple testing
           when reporting research results: the Bonferroni vs Holm methods".
           American Journal of Public Health, 86(5), 726-728.

    Examples
    --------
    >>> # Single test result
    >>> result = {'pvalue': 0.01, 'test_method': 'test'}
    >>> corrected = correct_holm(result)
    >>> corrected[0]['pvalue_adjusted']
    0.01

    >>> # Multiple tests
    >>> results = [
    ...     {'pvalue': 0.001, 'test_method': 't-test'},
    ...     {'pvalue': 0.04, 'test_method': 't-test'},
    ...     {'pvalue': 0.03, 'test_method': 't-test'}
    ... ]
    >>> corrected = correct_holm(results, alpha=0.05)
    >>> [r['rejected'] for r in corrected]
    [True, False, True]

    >>> # As DataFrame
    >>> import pandas as pd
    >>> df = pd.DataFrame(results)
    >>> df_corrected = correct_holm(df)
    """
    from ..utils._normalizers import force_dataframe

    # Convert to list of dicts if needed
    return_as_dataframe = isinstance(results, pd.DataFrame)

    if isinstance(results, dict):
        results = [results]
    elif isinstance(results, pd.DataFrame):
        results = results.to_dict('records')

    # Extract p-values
    if not results:
        raise ValueError("Empty results provided")

    if 'pvalue' not in results[0]:
        raise ValueError("Results must contain 'pvalue' field")

    m = len(results)

    # Create indexed results for tracking original order
    indexed_results = [(i, r) for i, r in enumerate(results)]

    # Sort by p-value (ascending)
    sorted_results = sorted(indexed_results, key=lambda x: x[1]['pvalue'])

    # Compute adjusted p-values using Holm's method
    adjusted_pvalues = []
    for i, (orig_idx, result) in enumerate(sorted_results):
        p = result['pvalue']

        # Holm adjustment: p_adj = max over j≤i of (m - j + 1) * p_j
        # This ensures monotonicity
        adj_p = (m - i) * p  # Initial adjustment

        # Enforce monotonicity: adjusted p-values must be non-decreasing
        if i > 0:
            adj_p = max(adj_p, adjusted_pvalues[i - 1])

        # Cap at 1.0
        adj_p = min(adj_p, 1.0)

        adjusted_pvalues.append(adj_p)

    # Apply corrections to results
    corrected_results = []
    for i, (orig_idx, result) in enumerate(sorted_results):
        corrected = result.copy()
        corrected['pvalue_adjusted'] = round(adjusted_pvalues[i], 6)
        corrected['alpha_adjusted'] = round(alpha / (m - i), 6)  # For reference
        corrected['rejected'] = adjusted_pvalues[i] <= alpha

        # Add original index for restoration
        corrected['_orig_idx'] = orig_idx

        corrected_results.append(corrected)

    # Restore original order
    corrected_results.sort(key=lambda x: x['_orig_idx'])

    # Remove temporary index field
    for r in corrected_results:
        del r['_orig_idx']

    # Convert to DataFrame if input was DataFrame
    if return_as_dataframe:
        return force_dataframe(corrected_results)

    return corrected_results


"""Main function"""
def main(args):
    """Demonstrate Holm correction functionality."""
    logger.info("Demonstrating Holm-Bonferroni correction")

    # Example 1: Basic usage with multiple tests
    logger.info("\n=== Example 1: Basic usage ===")

    results = [
        {'test_method': 'Test 1', 'pvalue': 0.001},
        {'test_method': 'Test 2', 'pvalue': 0.040},
        {'test_method': 'Test 3', 'pvalue': 0.030},
        {'test_method': 'Test 4', 'pvalue': 0.015},
        {'test_method': 'Test 5', 'pvalue': 0.060},
    ]

    corrected = correct_holm(results, alpha=0.05)

    logger.info("\nOriginal p-values:")
    for i, r in enumerate(results):
        logger.info(f"  {r['test_method']}: p = {r['pvalue']:.4f}")

    logger.info("\nAfter Holm correction:")
    for r in corrected:
        logger.info(
            f"  {r['test_method']}: "
            f"p_adj = {r['pvalue_adjusted']:.4f}, "
            f"rejected = {r['rejected']}"
        )

    # Example 2: Comparison with Bonferroni
    logger.info("\n=== Example 2: Holm vs Bonferroni comparison ===")

    from ._correct_bonferroni import correct_bonferroni

    results = [
        {'test_method': 'Comparison A', 'pvalue': 0.005},
        {'test_method': 'Comparison B', 'pvalue': 0.015},
        {'test_method': 'Comparison C', 'pvalue': 0.025},
        {'test_method': 'Comparison D', 'pvalue': 0.035},
        {'test_method': 'Comparison E', 'pvalue': 0.045},
    ]

    holm_results = correct_holm(results, alpha=0.05)
    bonf_results = correct_bonferroni(results, alpha=0.05)

    logger.info("\nHolm vs Bonferroni (alpha = 0.05):")
    logger.info(f"{'Test':<15} {'p-value':<10} {'Holm adj':<12} {'Holm rej':<10} {'Bonf adj':<12} {'Bonf rej':<10}")
    logger.info("-" * 75)

    for orig, holm, bonf in zip(results, holm_results, bonf_results):
        logger.info(
            f"{orig['test_method']:<15} "
            f"{orig['pvalue']:<10.4f} "
            f"{holm['pvalue_adjusted']:<12.4f} "
            f"{str(holm['rejected']):<10} "
            f"{bonf['pvalue_adjusted']:<12.4f} "
            f"{str(bonf['rejected']):<10}"
        )

    # Count rejections
    holm_rejections = sum(r['rejected'] for r in holm_results)
    bonf_rejections = sum(r['rejected'] for r in bonf_results)

    logger.info(f"\nHolm rejections: {holm_rejections}/5")
    logger.info(f"Bonferroni rejections: {bonf_rejections}/5")
    logger.info("Note: Holm is uniformly more powerful than Bonferroni")

    # Example 3: Post-hoc after ANOVA
    logger.info("\n=== Example 3: Post-hoc pairwise comparisons after ANOVA ===")

    np.random.seed(42)

    from ..tests.parametric._test_anova import test_anova
    from ..tests.parametric._test_ttest import test_ttest_ind

    # Three groups with differences
    group1 = np.random.normal(5, 1, 30)
    group2 = np.random.normal(7, 1, 30)
    group3 = np.random.normal(9, 1, 30)

    groups = [group1, group2, group3]
    names = ['Group A', 'Group B', 'Group C']

    # Overall ANOVA
    anova_result = test_anova(groups, var_names=names)
    logger.info(f"Overall ANOVA: F = {anova_result['statistic']:.3f}, p = {anova_result['pvalue']:.4f}")

    if anova_result['rejected']:
        logger.info("\nPerforming pairwise t-tests:")

        # Pairwise comparisons
        pairwise_results = []
        for i in range(len(groups)):
            for j in range(i + 1, len(groups)):
                result = test_ttest_ind(
                    groups[i], groups[j],
                    var_x=names[i], var_y=names[j]
                )
                pairwise_results.append(result)

                logger.info(
                    f"  {names[i]} vs {names[j]}: "
                    f"t = {result['statistic']:.3f}, "
                    f"p = {result['pvalue']:.4f}"
                )

        # Apply Holm correction
        holm_corrected = correct_holm(pairwise_results, alpha=0.05)

        logger.info("\nAfter Holm correction:")
        for r in holm_corrected:
            logger.info(
                f"  {r['var_x']} vs {r['var_y']}: "
                f"p_adj = {r['pvalue_adjusted']:.4f}, "
                f"rejected = {r['rejected']}"
            )

    # Example 4: DataFrame input/output
    logger.info("\n=== Example 4: DataFrame input/output ===")

    df_input = pd.DataFrame([
        {'comparison': 'A vs B', 'pvalue': 0.001, 'effect_size': 0.8},
        {'comparison': 'A vs C', 'pvalue': 0.020, 'effect_size': 0.5},
        {'comparison': 'A vs D', 'pvalue': 0.030, 'effect_size': 0.4},
        {'comparison': 'B vs C', 'pvalue': 0.015, 'effect_size': 0.6},
        {'comparison': 'B vs D', 'pvalue': 0.040, 'effect_size': 0.3},
        {'comparison': 'C vs D', 'pvalue': 0.050, 'effect_size': 0.2},
    ])

    df_corrected = correct_holm(df_input, alpha=0.05)

    logger.info("\nInput DataFrame:")
    logger.info(df_input[['comparison', 'pvalue']].to_string(index=False))

    logger.info("\nCorrected DataFrame:")
    logger.info(
        df_corrected[['comparison', 'pvalue', 'pvalue_adjusted', 'rejected']]
        .to_string(index=False)
    )

    # Example 5: Edge cases
    logger.info("\n=== Example 5: Edge cases ===")

    # Single test (m=1)
    single = [{'test_method': 'Single test', 'pvalue': 0.04}]
    single_corr = correct_holm(single, alpha=0.05)
    logger.info(f"Single test: p = 0.04 → p_adj = {single_corr[0]['pvalue_adjusted']:.4f}")

    # All very small p-values
    small_ps = [{'test_method': f'Test {i}', 'pvalue': 0.0001 * (i + 1)} for i in range(5)]
    small_corr = correct_holm(small_ps, alpha=0.05)
    rejections = sum(r['rejected'] for r in small_corr)
    logger.info(f"All small p-values: {rejections}/5 rejected")

    # All large p-values
    large_ps = [{'test_method': f'Test {i}', 'pvalue': 0.1 + 0.1 * i} for i in range(5)]
    large_corr = correct_holm(large_ps, alpha=0.05)
    rejections = sum(r['rejected'] for r in large_corr)
    logger.info(f"All large p-values: {rejections}/5 rejected")

    # Example 6: Export corrected results
    logger.info("\n=== Example 6: Export corrected results ===")

    from ..utils._normalizers import convert_results

    # Use pairwise results from Example 3
    if anova_result['rejected']:
        # Export to Excel
        convert_results(holm_corrected, return_as='excel', path='./holm_corrected.xlsx')
        logger.info("Corrected results exported to Excel")

        # Export to CSV
        convert_results(holm_corrected, return_as='csv', path='./holm_corrected.csv')
        logger.info("Corrected results exported to CSV")

    # Example 7: Power comparison with different α levels
    logger.info("\n=== Example 7: Different alpha levels ===")

    results = [
        {'test_method': f'Test {i}', 'pvalue': 0.01 * (i + 1)}
        for i in range(10)
    ]

    for alpha_level in [0.01, 0.05, 0.10]:
        corrected = correct_holm(results, alpha=alpha_level)
        rejections = sum(r['rejected'] for r in corrected)
        logger.info(f"α = {alpha_level:.2f}: {rejections}/10 tests rejected")

    return 0


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Demonstrate Holm-Bonferroni correction'
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
