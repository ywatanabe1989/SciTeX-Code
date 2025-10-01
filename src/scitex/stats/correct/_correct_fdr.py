#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-01 20:48:08 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/stats/correct/_correct_fdr.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/stats/correct/_correct_fdr.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
  - Apply False Discovery Rate (FDR) correction for multiple comparisons
  - Implement Benjamini-Hochberg and Benjamini-Yekutieli procedures
  - Support both dict and DataFrame inputs
  - Maintain full result information with adjusted values

Dependencies:
  - packages: numpy, pandas

IO:
  - input: Test results with p-values (dict, list of dicts, or DataFrame)
  - output: Results with adjusted p-values and significance (same format as input)
"""

"""Imports"""
import argparse
from typing import Any, Dict, List, Literal, Optional, Union

import matplotlib
import matplotlib.axes
import numpy as np
import pandas as pd
import scitex as stx
from scitex.logging import getLogger

logger = getLogger(__name__)

"""Functions"""


def correct_fdr(
    results: Union[Dict[str, Any], List[Dict[str, Any]], pd.DataFrame],
    alpha: float = 0.05,
    method: Literal["bh", "by"] = "bh",
    return_as: str = None,
    verbose: bool = True,
    plot: bool = False,
    ax: Optional[matplotlib.axes.Axes] = None,
) -> Union[Dict[str, Any], List[Dict[str, Any]], pd.DataFrame]:
    """
    Apply False Discovery Rate (FDR) correction for multiple comparisons.

    Parameters
    ----------
    results : dict, list of dict, or DataFrame
        Test results containing 'pvalue' field(s)
        - Single dict: one test result
        - List of dicts: multiple test results
        - DataFrame: multiple test results (one per row)
    alpha : float, default 0.05
        False discovery rate to control
    method : {'bh', 'by'}, default 'bh'
        FDR control method:
        - 'bh': Benjamini-Hochberg (assumes independence or positive dependence)
        - 'by': Benjamini-Yekutieli (valid under arbitrary dependence)
    return_as : {'dict', 'dataframe', None}, optional
        Force specific return format. If None, matches input format.
    verbose : bool, default True
        Whether to log progress information
    plot : bool, default False
        Whether to generate visualization
    ax : matplotlib.axes.Axes, optional
        Axes object to plot on. If None and plot=True, creates new figure.
        If provided, automatically enables plotting.

    Returns
    -------
    results : dict, list of dict, or DataFrame
        Results with added fields:
        - pvalue_adjusted: FDR-adjusted p-value (q-value)
        - alpha_adjusted: Effective alpha threshold for each test
        - rejected: Whether null hypothesis is rejected
        - pstars: Significance stars (using adjusted p-value)

    Notes
    -----
    **Benjamini-Hochberg (BH) Procedure:**

    For m tests with p-values p₁ ≤ p₂ ≤ ... ≤ pₘ:

    1. Order p-values from smallest to largest
    2. Find largest i such that: p_i ≤ (i/m) × α
    3. Reject H₀ for tests 1, 2, ..., i

    Adjusted p-values (q-values):

    .. math::
        q_i = \\min_{j \\geq i} \\left( \\frac{m \\cdot p_j}{j} \\right)

    **Benjamini-Yekutieli (BY) Procedure:**

    More conservative, valid under arbitrary dependence:

    .. math::
        q_i = c(m) \\cdot \\min_{j \\geq i} \\left( \\frac{m \\cdot p_j}{j} \\right)

    where :math:`c(m) = \\sum_{i=1}^{m} \\frac{1}{i} \\approx \\ln(m) + 0.5772`

    **FDR vs FWER:**

    - FWER (Bonferroni): Controls probability of ANY false positive
    - FDR: Controls expected proportion of false positives among rejections

    .. math::
        FDR = E\\left[\\frac{\\text{False Positives}}{\\text{Total Rejections}}\\right]

    **Advantages:**
    - More powerful than Bonferroni (especially with many tests)
    - Scales well to large m
    - Balances Type I and Type II errors

    **Disadvantages:**
    - Weaker control than FWER methods
    - May allow some false positives
    - BH requires independence assumption

    **When to use:**
    - Large number of tests (m > 10)
    - Exploratory analysis
    - Can tolerate some false positives
    - Need higher power than Bonferroni

    References
    ----------
    .. [1] Benjamini, Y., & Hochberg, Y. (1995). "Controlling the false
           discovery rate: a practical and powerful approach to multiple
           testing". Journal of the Royal Statistical Society, Series B, 57(1), 289-300.
    .. [2] Benjamini, Y., & Yekutieli, D. (2001). "The control of the false
           discovery rate in multiple testing under dependency". Annals of
           Statistics, 29(4), 1165-1188.

    Examples
    --------
    >>> # Multiple tests
    >>> results = [
    ...     {'pvalue': 0.001, 'var_x': 'A', 'var_y': 'B'},
    ...     {'pvalue': 0.010, 'var_x': 'A', 'var_y': 'C'},
    ...     {'pvalue': 0.050, 'var_x': 'B', 'var_y': 'C'},
    ...     {'pvalue': 0.100, 'var_x': 'A', 'var_y': 'D'}
    ... ]
    >>> corrected = correct_fdr(results)
    >>> [r['pvalue_adjusted'] for r in corrected]
    [0.004, 0.02, 0.0666..., 0.1]

    >>> # BH vs BY comparison
    >>> corrected_bh = correct_fdr(results, method='bh')
    >>> corrected_by = correct_fdr(results, method='by')
    >>> corrected_bh[0]['pvalue_adjusted'] < corrected_by[0]['pvalue_adjusted']
    True
    """
    from ..utils._formatters import p2stars
    from ..utils._normalizers import force_dataframe, to_dict

    if verbose:
        method_name = (
            "Benjamini-Hochberg" if method == "bh" else "Benjamini-Yekutieli"
        )
        logger.info(f"Applying FDR correction ({method_name})")

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

    # Store original order
    df["_original_order"] = np.arange(len(df))

    # Number of tests
    m = len(df)
    if verbose:
        logger.info(f"Number of tests: {m}, alpha: {alpha}")

    # Sort by p-value
    df_sorted = df.sort_values("pvalue").copy()
    pvalues = df_sorted["pvalue"].values

    # Compute adjusted p-values (q-values)
    if method == "bh":
        # Benjamini-Hochberg
        ranks = np.arange(1, m + 1)
        q_values = np.minimum.accumulate((pvalues * m / ranks)[::-1])[::-1]
        q_values = np.minimum(q_values, 1.0)

    elif method == "by":
        # Benjamini-Yekutieli
        # c(m) = sum(1/i) for i in 1:m ≈ ln(m) + γ (Euler-Mascheroni constant)
        c_m = np.sum(1.0 / np.arange(1, m + 1))
        ranks = np.arange(1, m + 1)
        q_values = np.minimum.accumulate((pvalues * m * c_m / ranks)[::-1])[
            ::-1
        ]
        q_values = np.minimum(q_values, 1.0)

    else:
        raise ValueError(f"Unknown method: {method}. Use 'bh' or 'by'.")

    df_sorted["pvalue_adjusted"] = q_values

    # Compute adjusted alpha threshold for each test
    if "alpha" in df.columns:
        alpha_values = df_sorted["alpha"].fillna(alpha)
    else:
        alpha_values = alpha

    # For FDR, the effective alpha threshold varies by rank
    ranks = np.arange(1, m + 1)
    if method == "bh":
        alpha_adj = alpha_values * ranks / m
    else:  # by
        c_m = np.sum(1.0 / np.arange(1, m + 1))
        alpha_adj = alpha_values * ranks / (m * c_m)

    df_sorted["alpha_adjusted"] = alpha_adj

    # Determine rejections using BH/BY procedure
    # Find largest i where p_i <= (i/m) * alpha
    if method == "bh":
        threshold = alpha * ranks / m
    else:
        c_m = np.sum(1.0 / np.arange(1, m + 1))
        threshold = alpha * ranks / (m * c_m)

    # Find the largest rank where p-value is below threshold
    significant = pvalues <= threshold
    if np.any(significant):
        max_significant_rank = np.max(np.where(significant)[0]) + 1
        df_sorted["rejected"] = np.arange(1, m + 1) <= max_significant_rank
    else:
        df_sorted["rejected"] = False

    # Update significance stars based on adjusted p-values
    df_sorted["pstars"] = df_sorted["pvalue_adjusted"].apply(p2stars)

    # Restore original order
    df_result = df_sorted.sort_values("_original_order").drop(
        columns=["_original_order"]
    )

    # Log results summary
    if verbose:
        rejections = df_result["rejected"].sum()
        logger.info(
            f"FDR correction complete: {rejections}/{m} hypotheses rejected"
        )

        # Log detailed results if not too many tests
        if m <= 10:
            logger.info("\nDetailed results:")
            for idx, row in df_result.iterrows():
                comparison = ""
                if "var_x" in row and "var_y" in row:
                    comparison = f"{row['var_x']} vs {row['var_y']}: "
                elif "test_method" in row:
                    comparison = f"{row['test_method']}: "
                elif "comparison" in row:
                    comparison = f"{row['comparison']}: "

                logger.info(
                    f"  {comparison}"
                    f"p = {row['pvalue']:.4f} → q = {row['pvalue_adjusted']:.4f} "
                    f"{row['pstars']}, rejected = {row['rejected']}"
                )

    # Auto-enable plotting if ax is provided
    if ax is not None:
        plot = True

    # Generate plot if requested
    if plot:
        if ax is None:
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots(figsize=(10, 6))
        _plot_fdr(df_result, alpha, method, ax)

    # Determine return format
    if return_as == "dataframe":
        return df_result
    elif return_as == "dict":
        if is_single_dict:
            return to_dict(df_result, row=0)
        else:
            return df_result.to_dict("records")
    else:
        # Match input format
        if input_type == dict:
            return to_dict(df_result, row=0)
        elif input_type == list:
            return df_result.to_dict("records")
        else:  # DataFrame
            return df_result


def _plot_fdr(df, alpha, method, ax):
    """Create visualization for FDR correction on given axes."""
    m = len(df)
    x = np.arange(m)

    # Plot original p-values and q-values
    ax.scatter(x, df["pvalue"], label="Original p-values", alpha=0.7, s=100, color="C0")
    ax.scatter(x, df["pvalue_adjusted"], label="Q-values (FDR-adjusted)", alpha=0.7, s=100, color="C1", marker="s")

    # Connect original to adjusted with lines
    for i in range(m):
        ax.plot([i, i], [df["pvalue"].iloc[i], df["pvalue_adjusted"].iloc[i]],
                "k-", alpha=0.3, linewidth=0.5)

    # Add significance threshold
    ax.axhline(alpha, color="red", linestyle="--", linewidth=2, alpha=0.5, label=f"α = {alpha}")

    # Formatting
    method_name = "Benjamini-Hochberg" if method == "bh" else "Benjamini-Yekutieli"
    ax.set_xlabel("Test Index")
    ax.set_ylabel("P-value / Q-value")
    rejections = df["rejected"].sum()
    ax.set_title(f"FDR Correction ({method_name}, m={m} tests)\n"
                 f"{rejections}/{m} hypotheses rejected")
    ax.set_yscale("log")
    ax.grid(True, alpha=0.3)
    ax.legend()

    # Set x-axis labels if there are comparison names
    if m <= 20:
        labels = []
        for idx, row in df.iterrows():
            if "var_x" in row and "var_y" in row:
                labels.append(f"{row['var_x']}\nvs\n{row['var_y']}")
            elif "test_method" in row:
                labels.append(row["test_method"])
            elif "comparison" in row:
                labels.append(row["comparison"])
            else:
                labels.append(f"Test {len(labels)+1}")
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=8)
    else:
        ax.set_xlabel(f"Test Index (1-{m})")


"""Main function"""


def main(args):
    """Demonstrate FDR correction."""
    logger.info("Demonstrating False Discovery Rate correction")

    # Example 1: Single test (no correction needed)
    logger.info("\n=== Example 1: Single test ===")

    single_result = {
        "var_x": "Control",
        "var_y": "Treatment",
        "pvalue": 0.04,
        "alpha": 0.05,
    }

    corrected_single = correct_fdr(single_result, verbose=args.verbose)

    # Example 2: Multiple tests - BH method
    logger.info("\n=== Example 2: Multiple tests (Benjamini-Hochberg) ===")

    multiple_results = [
        {"var_x": "A", "var_y": "B", "pvalue": 0.001},
        {"var_x": "A", "var_y": "C", "pvalue": 0.010},
        {"var_x": "A", "var_y": "D", "pvalue": 0.050},
        {"var_x": "B", "var_y": "C", "pvalue": 0.100},
        {"var_x": "B", "var_y": "D", "pvalue": 0.200},
    ]

    corrected_bh = correct_fdr(
        multiple_results, method="bh", alpha=0.05, verbose=args.verbose
    )

    # Example 3: BH vs BY comparison
    logger.info("\n=== Example 3: BH vs BY comparison ===")

    corrected_by = correct_fdr(
        multiple_results, method="by", alpha=0.05, verbose=args.verbose
    )

    # Example 4: Bonferroni vs FDR
    logger.info("\n=== Example 4: Bonferroni vs FDR comparison ===")

    from ._correct_bonferroni import correct_bonferroni

    corrected_bonf = correct_bonferroni(
        multiple_results, alpha=0.05, verbose=False
    )

    n_rejected_bonf = sum(r["rejected"] for r in corrected_bonf)
    n_rejected_fdr = sum(r["rejected"] for r in corrected_bh)

    logger.info(f"Bonferroni rejections: {n_rejected_bonf}")
    logger.info(f"FDR (BH) rejections:   {n_rejected_fdr}")
    logger.info(f"FDR is more powerful (rejects more tests)")

    # Example 5: Many tests
    logger.info("\n=== Example 5: Large scale comparison (m=100) ===")

    np.random.seed(42)

    # Simulate 100 tests: 20 true positives, 80 true negatives
    many_results = []

    # True positives (small p-values)
    for i in range(20):
        p = np.random.beta(1, 50)  # Small p-values
        many_results.append(
            {
                "var_x": f"Var_{i}",
                "var_y": "Control",
                "pvalue": p,
                "truth": "positive",
            }
        )

    # True negatives (large p-values)
    for i in range(20, 100):
        p = np.random.uniform(0.1, 1.0)  # Large p-values
        many_results.append(
            {
                "var_x": f"Var_{i}",
                "var_y": "Control",
                "pvalue": p,
                "truth": "negative",
            }
        )

    corrected_fdr_many = correct_fdr(many_results, method="bh", verbose=False)
    corrected_bonf_many = correct_bonferroni(many_results, verbose=False)

    # Calculate confusion metrics
    def calc_metrics(corrected, truth_col="truth"):
        tp = sum(
            1
            for r in corrected
            if r["rejected"] and r.get(truth_col) == "positive"
        )
        fp = sum(
            1
            for r in corrected
            if r["rejected"] and r.get(truth_col) == "negative"
        )
        fn = sum(
            1
            for r in corrected
            if not r["rejected"] and r.get(truth_col) == "positive"
        )
        tn = sum(
            1
            for r in corrected
            if not r["rejected"] and r.get(truth_col) == "negative"
        )
        return tp, fp, fn, tn

    tp_fdr, fp_fdr, fn_fdr, tn_fdr = calc_metrics(corrected_fdr_many)
    tp_bonf, fp_bonf, fn_bonf, tn_bonf = calc_metrics(corrected_bonf_many)

    logger.info("FDR (BH) Performance:")
    logger.info(f"  True Positives:  {tp_fdr} / 20")
    logger.info(f"  False Positives: {fp_fdr}")
    logger.info(f"  Power: {tp_fdr / 20:.2%}")
    if tp_fdr + fp_fdr > 0:
        logger.info(f"  FDR: {fp_fdr / (tp_fdr + fp_fdr):.2%}")

    logger.info("\nBonferroni Performance:")
    logger.info(f"  True Positives:  {tp_bonf} / 20")
    logger.info(f"  False Positives: {fp_bonf}")
    logger.info(f"  Power: {tp_bonf / 20:.2%}")
    if tp_bonf + fp_bonf > 0:
        logger.info(f"  FDR: {fp_bonf / (tp_bonf + fp_bonf):.2%}")

    # Create visualization
    logger.info("\n=== Creating visualization ===")

    fig, axes = stx.plt.subplots(2, 2, figsize=(12, 10))

    # Plot 1: Q-values vs P-values
    ax = axes[0, 0]

    test_pvalues = np.array([r["pvalue"] for r in corrected_bh])
    test_qvalues = np.array([r["pvalue_adjusted"] for r in corrected_bh])

    ax.scatter(test_pvalues, test_qvalues, s=100, alpha=0.6)
    ax.plot([0, 1], [0, 1], "k--", alpha=0.3, label="y = x")
    ax.set_xlabel("Original P-value")
    ax.set_ylabel("Adjusted P-value (Q-value)")
    ax.set_title("FDR: P-values vs Q-values")
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Plot 2: BH vs BY
    ax = axes[0, 1]

    bh_qvalues = np.array([r["pvalue_adjusted"] for r in corrected_bh])
    by_qvalues = np.array([r["pvalue_adjusted"] for r in corrected_by])

    ax.scatter(bh_qvalues, by_qvalues, s=100, alpha=0.6)
    ax.plot([0, 1], [0, 1], "k--", alpha=0.3, label="y = x")
    ax.set_xlabel("BH Q-value")
    ax.set_ylabel("BY Q-value")
    ax.set_title("BH vs BY (BY is more conservative)")
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Plot 3: Power comparison across m
    ax = axes[1, 0]

    m_vals = np.arange(5, 101, 5)
    alpha = 0.05
    alpha_bonf = alpha / m_vals
    alpha_fdr = alpha  # FDR maintains similar threshold

    ax.plot(m_vals, alpha_bonf, label="Bonferroni", linewidth=2)
    ax.axhline(
        alpha_fdr, color="green", linestyle="--", linewidth=2, label="FDR (BH)"
    )
    ax.set_xlabel("Number of Tests (m)")
    ax.set_ylabel("Effective α")
    ax.set_title("FDR Maintains Power vs Bonferroni")
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_yscale("log")

    # Plot 4: ROC-like comparison
    ax = axes[1, 1]

    # Vary alpha and compute rejections
    alphas = [0.001, 0.01, 0.05, 0.10, 0.20]
    bonf_tps = []
    bonf_fps = []
    fdr_tps = []
    fdr_fps = []

    for a in alphas:
        corr_bonf = correct_bonferroni(many_results, alpha=a, verbose=False)
        corr_fdr = correct_fdr(
            many_results, alpha=a, method="bh", verbose=False
        )

        tp_b, fp_b, _, _ = calc_metrics(corr_bonf)
        tp_f, fp_f, _, _ = calc_metrics(corr_fdr)

        bonf_tps.append(tp_b / 20)  # Sensitivity
        bonf_fps.append(fp_b / 80)  # FPR
        fdr_tps.append(tp_f / 20)
        fdr_fps.append(fp_f / 80)

    ax.plot(
        bonf_fps, bonf_tps, "o-", linewidth=2, markersize=8, label="Bonferroni"
    )
    ax.plot(
        fdr_fps, fdr_tps, "s-", linewidth=2, markersize=8, label="FDR (BH)"
    )
    ax.plot([0, 1], [0, 1], "k--", alpha=0.3)
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate (Power)")
    ax.set_title("Power vs FPR Trade-off")
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    # Save
    stx.io.save(fig, "./fdr_demo.jpg")
    logger.info("Visualization saved")

    return 0


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Demonstrate FDR correction")
    parser.add_argument(
        "--verbose", action="store_true", help="Enable verbose output"
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


if __name__ == "__main__":
    run_main()

# EOF
