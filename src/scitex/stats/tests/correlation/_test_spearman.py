#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-01 22:17:48 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/stats/tests/correlation/_test_spearman.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Spearman's rank correlation coefficient test.

Non-parametric measure of rank correlation (monotonic relationship).
More robust to outliers than Pearson's r.
"""

import argparse
from typing import Literal, Optional, Union

import matplotlib.axes
import numpy as np
import pandas as pd
import scitex as stx
from scipy import stats
from scitex.logging import getLogger

from ...utils._formatters import p2stars
from ...utils._normalizers import convert_results, force_dataframe

logger = getLogger(__name__)


def test_spearman(
    x: Union[np.ndarray, pd.Series],
    y: Union[np.ndarray, pd.Series],
    var_x: str = "x",
    var_y: str = "y",
    alternative: Literal["two-sided", "less", "greater"] = "two-sided",
    alpha: float = 0.05,
    plot: bool = False,
    ax: Optional[matplotlib.axes.Axes] = None,
    return_as: Literal["dict", "dataframe"] = "dict",
    decimals: int = 3,
    verbose: bool = False,
) -> Union[dict, pd.DataFrame]:
    """
    Spearman's rank correlation coefficient test.

    Non-parametric measure of monotonic relationship between two variables.
    Uses rank-transformed data, more robust to outliers than Pearson.

    Parameters
    ----------
    x : array-like
        First variable
    y : array-like
        Second variable (same length as x)
    var_x : str, default 'x'
        Name of first variable
    var_y : str, default 'y'
        Name of second variable
    alternative : {'two-sided', 'less', 'greater'}, default 'two-sided'
        Alternative hypothesis:
        - 'two-sided': ρ ≠ 0
        - 'less': ρ < 0
        - 'greater': ρ > 0
    alpha : float, default 0.05
        Significance level
    plot : bool, default False
        If True, create visualization with scatter plot of ranks
    return_as : {'dict', 'dataframe'}, default 'dict'
        Return format
    decimals : int, default 3
        Number of decimal places for rounding

    Returns
    -------
    result : dict or DataFrame or (dict, Figure)
        Test results with:
        - test_method: Name of test
        - statistic: Spearman's rho (ρ)
        - pvalue: p-value
        - alternative: Alternative hypothesis
        - alpha: Significance level
        - significant: Whether result is significant
        - stars: Significance stars
        - effect_size: Same as statistic (ρ)
        - effect_size_metric: 'rho'
        - effect_size_interpretation: Interpretation
        - rho_squared: Proportion of variance explained
        - n: Sample size
        - var_x: First variable name
        - var_y: Second variable name

    Notes
    -----
    Spearman's ρ is the Pearson correlation of rank-transformed variables.

    Assumptions:
    - Observations are independent
    - Variables are at least ordinal

    Interpretation (same as Pearson):
    - |ρ| < 0.1: negligible
    - |ρ| < 0.3: small
    - |ρ| < 0.5: medium
    - |ρ| ≥ 0.5: large

    References
    ----------
    Spearman, C. (1904). The proof and measurement of association between
    two things. American Journal of Psychology, 15, 72-101.

    Examples
    --------
    >>> import numpy as np
    >>> from scitex.stats.tests.correlation import test_spearman

    # Example 1: Perfect monotonic relationship
    >>> x = np.array([1, 2, 3, 4, 5])
    >>> y = np.array([1, 4, 9, 16, 25])  # Quadratic relationship
    >>> result = test_spearman(x, y, var_x='x', var_y='y²', plot=True)
    >>> print(result)

    # Example 2: Outlier-robust correlation
    >>> x = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 100])  # Outlier
    >>> y = np.array([2, 4, 6, 8, 10, 12, 14, 16, 18, 20])
    >>> result = test_spearman(x, y, plot=True)
    >>> print(f"Spearman ρ = {result['statistic']:.3f}, p = {result['pvalue']:.4f}")

    # Example 3: Compare with Pearson
    >>> from scitex.stats.tests.correlation import test_pearson
    >>> x = np.random.exponential(scale=2, size=50)
    >>> y = x + np.random.normal(0, 1, size=50)
    >>> spearman_result = test_spearman(x, y)
    >>> pearson_result = test_pearson(x, y)
    >>> print(f"Spearman: ρ = {spearman_result['statistic']:.3f}")
    >>> print(f"Pearson: r = {pearson_result['statistic']:.3f}")

    # Example 4: Ordinal data
    >>> satisfaction = np.array([1, 2, 3, 4, 5, 1, 2, 3, 4, 5])
    >>> quality = np.array([2, 3, 4, 4, 5, 1, 2, 3, 5, 4])
    >>> result = test_spearman(satisfaction, quality,
    ...                        var_x='Satisfaction', var_y='Quality',
    ...                        plot=True)

    # Example 5: One-tailed test
    >>> x = np.arange(20)
    >>> y = x + np.random.normal(0, 2, size=20)
    >>> result = test_spearman(x, y, alternative='greater')
    >>> print(f"One-tailed p-value: {result['pvalue']:.4f}")

    # Example 6: Non-linear monotonic relationship
    >>> x = np.linspace(0, 10, 50)
    >>> y = np.log(x + 1) + np.random.normal(0, 0.1, size=50)
    >>> result = test_spearman(x, y, var_x='x', var_y='log(x+1)', plot=True)

    # Example 7: Export to various formats
    >>> result = test_spearman(x, y, return_as='dataframe')
    >>> convert_results(result, return_as='latex', path='spearman.tex')
    >>> convert_results(result, return_as='csv', path='spearman.csv')
    """
    # Convert to arrays
    x = np.asarray(x)
    y = np.asarray(y)

    # Check lengths
    if len(x) != len(y):
        raise ValueError(
            f"x and y must have same length (got {len(x)} and {len(y)})"
        )

    # Remove NaN pairs
    mask = ~(np.isnan(x) | np.isnan(y))
    x = x[mask]
    y = y[mask]
    n = len(x)

    if n < 3:
        raise ValueError(f"Need at least 3 valid pairs (got {n})")

    # Compute Spearman correlation
    rho, pvalue = stats.spearmanr(x, y, alternative=alternative)
    rho = float(rho)
    pvalue = float(pvalue)

    # Compute rho-squared (proportion of variance explained by ranks)
    rho_squared = rho**2

    # Check significance
    significant = pvalue < alpha
    stars = p2stars(pvalue)

    # Interpret effect size (same as Pearson)
    rho_abs = abs(rho)
    if rho_abs < 0.1:
        interpretation = "negligible"
    elif rho_abs < 0.3:
        interpretation = "small"
    elif rho_abs < 0.5:
        interpretation = "medium"
    else:
        interpretation = "large"

    # Build result
    result = {
        "test_method": "Spearman's rank correlation",
        "statistic": round(rho, decimals),
        "pvalue": round(pvalue, decimals),
        "alternative": alternative,
        "alpha": alpha,
        "significant": significant,
        "stars": stars,
        "effect_size": round(rho, decimals),
        "effect_size_metric": "rho",
        "effect_size_interpretation": interpretation,
        "rho_squared": round(rho_squared, decimals),
        "n": n,
        "var_x": var_x,
        "var_y": var_y,
    }

    # Log results if verbose
    if verbose:
        logger.info(
            f"Spearman: ρ = {rho:.3f}, p = {pvalue:.4f} {p2stars(pvalue)}"
        )
        logger.info(f"ρ² = {rho_squared:.3f} ({interpretation})")

    # Auto-enable plotting if ax is provided
    if ax is not None:
        plot = True

    # Generate plot if requested
    if plot:
        if ax is None:
            fig, ax = stx.plt.subplots()
        _plot_spearman(x, y, rho, pvalue, var_x, var_y, alpha, ax)

    # Convert to requested format
    if return_as == "dataframe":
        result = force_dataframe(result)
    elif return_as not in ["dict", "dataframe"]:
        return convert_results(result, return_as=return_as)

    return result


def _plot_spearman(x, y, rho, pvalue, var_x, var_y, alpha, ax):
    """Create scatter plot with rank-based regression line on given axes."""
    # Convert to ranks
    x_ranks = stats.rankdata(x)
    y_ranks = stats.rankdata(y)

    # Scatter plot of ranks
    ax.scatter(
        x_ranks,
        y_ranks,
        alpha=0.6,
        s=50,
        color="C0",
        edgecolors="white",
        linewidths=0.5,
        zorder=3,
    )

    # Add regression line for ranks
    z = np.polyfit(x_ranks, y_ranks, 1)
    p = np.poly1d(z)
    x_line = np.linspace(x_ranks.min(), x_ranks.max(), 100)
    ax.plot(
        x_line, p(x_line), "r-", linewidth=2, label=f"ρ = {rho:.3f}", zorder=2
    )

    # Labels and title
    ax.set_xlabel(f"Rank({var_x})")
    ax.set_ylabel(f"Rank({var_y})")
    stars = p2stars(pvalue)
    ax.set_title(f"Spearman: ρ = {rho:.3f} {stars}")
    ax.legend()
    ax.grid(True, alpha=0.3, zorder=1)


# Example usage
"""Main function"""


def main(args):
    """Demonstrate Spearman correlation test functionality."""
    logger.info("=" * 70)
    logger.info("Spearman's Rank Correlation Test - Examples")
    logger.info("=" * 70)

    # Example 1: Perfect monotonic relationship
    logger.info("\nExample 1: Perfect monotonic (quadratic) relationship")
    logger.info("-" * 70)
    x1 = np.array([1, 2, 3, 4, 5])
    y1 = np.array([1, 4, 9, 16, 25])
    result1 = test_spearman(
        x1, y1, var_x="x", var_y="y²", plot=True, verbose=True
    )
    logger.info(force_dataframe(result1))

    # Save the figure using plt.gcf()
    stx.io.save(stx.plt.gcf(), "example1_perfect_monotonic.jpg")
    stx.plt.close()

    # Example 2: Outlier comparison
    logger.info("\nExample 2: Robustness to outliers")
    logger.info("-" * 70)
    x2 = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 100])
    y2 = np.array([2, 4, 6, 8, 10, 12, 14, 16, 18, 20])

    from ..correlation._test_pearson import test_pearson

    logger.info("With outlier (x=100):")
    logger.info("Spearman:")
    spearman_result = test_spearman(x2, y2, var_x="x", var_y="y", verbose=True)
    logger.info("Pearson:")
    pearson_result = test_pearson(x2, y2, var_x="x", var_y="y", verbose=True)
    logger.info("→ Spearman is more robust to the outlier")

    # Example 3: Non-linear monotonic relationship
    logger.info("\nExample 3: Non-linear monotonic (logarithmic) relationship")
    logger.info("-" * 70)
    np.random.seed(42)
    x3 = np.linspace(1, 50, 50)
    y3 = np.log(x3) + np.random.normal(0, 0.2, size=50)
    result3 = test_spearman(
        x3, y3, var_x="x", var_y="log(x)", plot=True, verbose=True
    )
    logger.info(force_dataframe(result3))
    stx.io.save(stx.plt.gcf(), "example3_logarithmic.jpg")
    stx.plt.close()

    # Example 4: Ordinal data
    logger.info("\nExample 4: Ordinal data (Likert scales)")
    logger.info("-" * 70)
    np.random.seed(43)
    satisfaction = np.random.randint(1, 6, size=30)
    quality = satisfaction + np.random.randint(-1, 2, size=30)
    quality = np.clip(quality, 1, 5)
    result4 = test_spearman(
        satisfaction,
        quality,
        var_x="Satisfaction",
        var_y="Quality",
        plot=True,
        verbose=True,
    )
    logger.info(force_dataframe(result4))
    stx.io.save(stx.plt.gcf(), "example4_ordinal.jpg")
    stx.plt.close()

    # Example 5: One-tailed test
    logger.info("\nExample 5: One-tailed test (expect positive correlation)")
    logger.info("-" * 70)
    np.random.seed(44)
    x5 = np.arange(30)
    y5 = x5 + np.random.normal(0, 3, size=30)
    logger.info("Two-tailed test:")
    result5_two = test_spearman(x5, y5, alternative="two-sided", verbose=True)
    logger.info("\nOne-tailed test (greater):")
    result5_greater = test_spearman(
        x5, y5, alternative="greater", verbose=True
    )

    # Example 6: Exponential relationship
    logger.info("\nExample 6: Exponential relationship")
    logger.info("-" * 70)
    np.random.seed(45)
    x6 = np.linspace(0, 5, 40)
    y6 = np.exp(x6 * 0.5) + np.random.normal(0, 2, size=40)
    result6 = test_spearman(
        x6, y6, var_x="x", var_y="exp(0.5x)", plot=True, verbose=True
    )
    logger.info(force_dataframe(result6))
    stx.io.save(stx.plt.gcf(), "example6_exponential.jpg")
    stx.plt.close()

    # Example 7: No correlation
    logger.info("\nExample 7: No correlation")
    logger.info("-" * 70)
    np.random.seed(46)
    x7 = np.random.normal(0, 1, size=50)
    y7 = np.random.normal(0, 1, size=50)
    result7 = test_spearman(x7, y7, var_x="x", var_y="y", verbose=True)
    logger.info(force_dataframe(result7))

    # Example 8: Compare Spearman vs Pearson on skewed data
    logger.info("\nExample 8: Spearman vs Pearson on skewed data")
    logger.info("-" * 70)
    np.random.seed(47)
    x8 = np.random.exponential(scale=2, size=60)
    y8 = x8**0.8 + np.random.normal(0, 1, size=60)

    logger.info("Exponential distribution with power relationship:")
    logger.info("Spearman:")
    spearman_res = test_spearman(x8, y8, verbose=True)
    logger.info("Pearson:")
    pearson_res = test_pearson(x8, y8, verbose=True)

    # Example 9: Export to multiple formats
    logger.info("\nExample 9: Export to multiple formats")
    logger.info("-" * 70)
    np.random.seed(48)
    x9 = np.arange(25)
    y9 = 2 * x9 + np.random.normal(0, 5, size=25)
    result9 = test_spearman(
        x9,
        y9,
        var_x="Time",
        var_y="Response",
        return_as="dataframe",
        verbose=True,
    )

    # Save
    stx.io.save(result9, "./spearman_demo.csv")
    stx.io.save(result9, "./spearman_demo.tex")

    # Example 10: Large dataset
    logger.info("\nExample 10: Large dataset with moderate correlation")
    logger.info("-" * 70)
    np.random.seed(49)
    n_large = 500
    x10 = np.random.normal(100, 15, size=n_large)
    y10 = 0.6 * x10 + np.random.normal(0, 20, size=n_large)
    result10 = test_spearman(
        x10, y10, var_x="Predictor", var_y="Outcome", plot=True, verbose=True
    )
    logger.info(force_dataframe(result10))
    stx.io.save(stx.plt.gcf(), "example10_large_dataset.jpg")
    stx.plt.close()

    logger.info(f"\n{'='*70}")
    logger.info("All examples completed")
    logger.info(f"{'='*70}")

    return 0


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="")
    parser.add_argument(
        "--verbose", action="store_true", help="Enable verbose output"
    )
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
