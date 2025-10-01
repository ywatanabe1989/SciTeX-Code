#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-01 22:22:16 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/stats/tests/correlation/_test_kendall.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/stats/tests/correlation/_test_kendall.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import argparse

"""
Functionalities:
  - Perform Kendall's tau correlation test
  - Compute tau-b (accounts for ties)
  - Generate scatter plots with rank visualization
  - Support one-sided and two-sided tests

Dependencies:
  - packages: numpy, pandas, scipy, matplotlib

IO:
  - input: Two continuous or ordinal variables
  - output: Test results (dict or DataFrame) and optional figure
"""

"""Imports"""
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


def interpret_kendall_tau(tau: float) -> str:
    """
    Interpret Kendall's tau effect size.

    Parameters
    ----------
    tau : float
        Kendall's tau coefficient

    Returns
    -------
    interpretation : str
        Interpretation of effect size
    """
    tau_abs = abs(tau)
    if tau_abs < 0.1:
        return "negligible"
    elif tau_abs < 0.3:
        return "small"
    elif tau_abs < 0.5:
        return "medium"
    else:
        return "large"


def test_kendall(
    x: Union[np.ndarray, pd.Series],
    y: Union[np.ndarray, pd.Series],
    var_x: str = "x",
    var_y: str = "y",
    alternative: Literal["two-sided", "less", "greater"] = "two-sided",
    variant: Literal["b", "c"] = "b",
    alpha: float = 0.05,
    plot: bool = False,
    ax: Optional[matplotlib.axes.Axes] = None,
    return_as: Literal["dict", "dataframe"] = "dict",
    decimals: int = 3,
    verbose: bool = False,
) -> Union[dict, pd.DataFrame]:
    """
    Perform Kendall's tau correlation test.

    Parameters
    ----------
    x : array or Series
        First variable
    y : array or Series
        Second variable
    var_x : str, default 'x'
        Name for x variable
    var_y : str, default 'y'
        Name for y variable
    alternative : {'two-sided', 'less', 'greater'}, default 'two-sided'
        Alternative hypothesis:
        - 'two-sided': tau ≠ 0
        - 'less': tau < 0 (negative association)
        - 'greater': tau > 0 (positive association)
    variant : {'b', 'c'}, default 'b'
        Tau variant:
        - 'b': tau-b (Kendall's tau-b, accounts for ties)
        - 'c': tau-c (Stuart's tau-c, for contingency tables)
    alpha : float, default 0.05
        Significance level
    plot : bool, default False
        Whether to generate scatter plot
    ax : matplotlib.axes.Axes, optional
        Axes to plot on. If provided, plot is set to True
    return_as : {'dict', 'dataframe'}, default 'dict'
        Output format
    decimals : int, default 3
        Number of decimal places for rounding
    verbose : bool, default False
        If True, print test results to logger

    Returns
    -------
    result : dict or DataFrame
        Test results including:
        - test_method: Name of test
        - statistic: Kendall's tau coefficient
        - pvalue: p-value
        - tau_squared: tau²  (proportion of variance explained)
        - effect_size: tau (same as statistic)
        - effect_size_interpretation: interpretation
        - n: Sample size
        - n_concordant: Number of concordant pairs
        - n_discordant: Number of discordant pairs
        - n_ties: Number of tied pairs
        - significant: Whether to reject null hypothesis
        - stars: Significance stars

    Notes
    -----
    Kendall's tau is a non-parametric measure of monotonic association between
    two variables. It is based on concordant and discordant pairs.

    **Null Hypothesis (H0)**: No monotonic association (tau = 0)

    **Alternative Hypothesis (H1)**: Monotonic association exists

    **Concordant vs Discordant Pairs**:
    For pairs (x_i, y_i) and (x_j, y_j):
    - Concordant: (x_i < x_j and y_i < y_j) or (x_i > x_j and y_i > y_j)
    - Discordant: (x_i < x_j and y_i > y_j) or (x_i > x_j and y_i < y_j)

    **Kendall's tau-b** (accounts for ties):

    .. math::
        \\tau_b = \\frac{n_c - n_d}{\\sqrt{(n_0 - n_1)(n_0 - n_2)}}

    Where:
    - n_c: Number of concordant pairs
    - n_d: Number of discordant pairs
    - n_0: n(n-1)/2 (total possible pairs)
    - n_1: Sum of t_i(t_i-1)/2 for ties in x
    - n_2: Sum of u_j(u_j-1)/2 for ties in y

    **Interpretation**:
    - tau = 1: Perfect positive association
    - tau = 0: No association
    - tau = -1: Perfect negative association

    Effect size interpretation (same as correlation):
    - |tau| < 0.1: negligible
    - |tau| < 0.3: small
    - |tau| < 0.5: medium
    - |tau| ≥ 0.5: large

    **Advantages over Spearman**:
    - More robust to outliers
    - Better for small samples
    - Better interpretation (probability of concordance)
    - More accurate p-values with ties

    **Disadvantages**:
    - Computationally more expensive (O(n²))
    - Generally smaller magnitude than Spearman's rho
    - Less intuitive interpretation than Pearson

    **When to use Kendall's tau**:
    - Small sample sizes (n < 30)
    - Data with many ties
    - Ordinal data
    - Non-normal data with outliers

    Examples
    --------
    >>> import numpy as np
    >>> from scitex.stats.tests.correlation import test_kendall
    >>>
    >>> # Monotonic relationship with ties
    >>> x = np.array([1, 2, 2, 3, 4, 4, 5, 6, 7])
    >>> y = np.array([2, 3, 3, 5, 6, 6, 8, 9, 10])
    >>>
    >>> result = test_kendall(x, y, var_x='Treatment Dose', var_y='Response',
    ...                       plot=True)
    >>> print(f"τ = {result['statistic']:.3f}, p = {result['pvalue']:.4f}")
    >>> print(f"Concordant pairs: {result['n_concordant']}")

    References
    ----------
    .. [1] Kendall, M. G. (1938). "A New Measure of Rank Correlation".
           Biometrika, 30(1/2), 81-93.
    .. [2] Kendall, M. G. (1945). "The treatment of ties in ranking problems".
           Biometrika, 33(3), 239-251.

    See Also
    --------
    test_spearman : Alternative rank correlation
    test_pearson : Parametric correlation
    """
    # Convert to arrays
    x = np.asarray(x)
    y = np.asarray(y)

    # Check shapes
    if x.shape != y.shape:
        raise ValueError("x and y must have the same shape")

    if x.ndim != 1:
        raise ValueError("x and y must be 1-dimensional")

    # Remove missing values
    mask = ~(np.isnan(x) | np.isnan(y))
    x = x[mask]
    y = y[mask]

    n = len(x)

    if n < 2:
        raise ValueError("Need at least 2 observations")

    # Compute Kendall's tau
    if variant == "b":
        tau, pvalue = stats.kendalltau(
            x, y, alternative=alternative, variant="b"
        )
    elif variant == "c":
        tau, pvalue = stats.kendalltau(
            x, y, alternative=alternative, variant="c"
        )
    else:
        raise ValueError(f"Unknown variant: {variant}. Use 'b' or 'c'.")

    # Compute tau-squared (proportion of variance explained)
    tau_squared = tau**2

    # Count concordant, discordant, and tied pairs
    # This is computationally expensive but informative
    n_concordant = 0
    n_discordant = 0
    n_ties_x = 0
    n_ties_y = 0
    n_ties_both = 0

    for i in range(n):
        for j in range(i + 1, n):
            dx = x[j] - x[i]
            dy = y[j] - y[i]

            if dx == 0 and dy == 0:
                n_ties_both += 1
            elif dx == 0:
                n_ties_x += 1
            elif dy == 0:
                n_ties_y += 1
            elif (dx > 0 and dy > 0) or (dx < 0 and dy < 0):
                n_concordant += 1
            else:
                n_discordant += 1

    n_ties = n_ties_x + n_ties_y + n_ties_both

    # Interpret effect size
    tau_interpretation = interpret_kendall_tau(tau)

    # Build result dictionary
    result = {
        "test_method": f"Kendall's tau-{variant}",
        "var_x": var_x,
        "var_y": var_y,
        "statistic": round(float(tau), decimals),
        "pvalue": round(float(pvalue), decimals + 1),
        "tau_squared": round(float(tau_squared), decimals),
        "effect_size": round(float(tau), decimals),
        "effect_size_metric": "kendall_tau",
        "effect_size_interpretation": tau_interpretation,
        "n": int(n),
        "n_concordant": int(n_concordant),
        "n_discordant": int(n_discordant),
        "n_ties_x": int(n_ties_x),
        "n_ties_y": int(n_ties_y),
        "n_ties_both": int(n_ties_both),
        "n_ties": int(n_ties),
        "alternative": alternative,
        "alpha": alpha,
        "significant": pvalue < alpha,
        "stars": p2stars(pvalue),
    }

    # Log results if verbose
    if verbose:
        logger.info(
            f"Kendall: τ = {tau:.3f}, p = {pvalue:.4f} {p2stars(pvalue)}"
        )
        logger.info(f"τ² = {tau_squared:.3f} ({tau_interpretation})")
        logger.info(
            f"Concordant: {n_concordant}, Discordant: {n_discordant}, Ties: {n_ties}"
        )

    # Auto-enable plotting if ax is provided
    if ax is not None:
        plot = True

    # Generate plot if requested
    if plot:
        if ax is None:
            fig, ax = stx.plt.subplots()
        _plot_kendall(x, y, result, var_x, var_y, ax)

    # Convert to requested format
    if return_as == "dataframe":
        result = force_dataframe(result)
    elif return_as not in ["dict", "dataframe"]:
        return convert_results(result, return_as=return_as)

    return result


def _plot_kendall(x, y, result, var_x, var_y, ax):
    """Create scatter plot with rank-based visualization on given axes."""
    # Convert to ranks
    ranks_x = stats.rankdata(x)
    ranks_y = stats.rankdata(y)

    # Scatter plot of ranks
    ax.scatter(
        ranks_x,
        ranks_y,
        alpha=0.6,
        s=50,
        color="C0",
        edgecolors="white",
        linewidths=0.5,
        zorder=3,
    )

    # Add regression line for ranks
    z = np.polyfit(ranks_x, ranks_y, 1)
    p = np.poly1d(z)
    x_line = np.linspace(ranks_x.min(), ranks_x.max(), 100)
    ax.plot(
        x_line,
        p(x_line),
        "r-",
        linewidth=2,
        label=f'τ = {result["statistic"]:.3f}',
        zorder=2,
    )

    # Labels and title
    ax.set_xlabel(f"Rank({var_x})")
    ax.set_ylabel(f"Rank({var_y})")
    stars = result["stars"]
    ax.set_title(f"Kendall: τ = {result['statistic']:.3f} {stars}")
    ax.legend()
    ax.grid(True, alpha=0.3, zorder=1)


"""Main function"""


def main(args):
    logger.info("=" * 70)
    logger.info("Kendall's Tau Correlation Examples")
    logger.info("=" * 70)

    # Example 1: Basic usage with ties
    logger.info("\n[Example 1] Basic Kendall's tau with tied values")
    logger.info("-" * 70)

    np.random.seed(42)
    x = np.array([1, 2, 2, 3, 4, 4, 5, 6, 7, 8, 9, 10])
    y = np.array([2, 3, 3, 5, 6, 6, 8, 9, 10, 11, 12, 13])

    result = test_kendall(
        x, y, var_x="Treatment Dose", var_y="Response", plot=True, verbose=True
    )
    stx.io.save(stx.plt.gcf(), "kendall_example1.jpg")
    stx.plt.close()

    # Example 2: Comparison with Spearman
    logger.info("\n[Example 2] Kendall vs Spearman comparison")
    logger.info("-" * 70)

    from . import test_spearman

    logger.info("Kendall:")
    result_kendall = test_kendall(x, y, verbose=True)
    logger.info("\nSpearman:")
    result_spearman = test_spearman(x, y, verbose=True)
    logger.info("\nNote: Kendall's tau is generally smaller but more robust")

    # Example 3: Small sample size
    logger.info("\n[Example 3] Small sample (n=8)")
    logger.info("-" * 70)

    x_small = np.array([1, 2, 3, 4, 5, 6, 7, 8])
    y_small = np.array([2, 4, 3, 7, 6, 9, 8, 10])

    logger.info("With small samples, Kendall's tau is preferred over Spearman")
    result_small = test_kendall(x_small, y_small, plot=True, verbose=True)
    stx.io.save(stx.plt.gcf(), "kendall_example3.jpg")
    stx.plt.close()

    # Example 4: Ordinal data (Likert scale)
    logger.info("\n[Example 4] Ordinal data (Likert scales)")
    logger.info("-" * 70)

    satisfaction = np.array([1, 2, 3, 3, 4, 4, 4, 5, 5, 5, 5])
    loyalty = np.array([1, 2, 2, 3, 3, 4, 4, 4, 5, 5, 5])

    logger.info("Ideal for ordinal data with limited unique values")
    result_ordinal = test_kendall(
        satisfaction,
        loyalty,
        var_x="Satisfaction (1-5)",
        var_y="Loyalty (1-5)",
        plot=True,
        verbose=True,
    )
    stx.io.save(stx.plt.gcf(), "kendall_example4.jpg")
    stx.plt.close()

    # Example 5: One-sided test
    logger.info("\n[Example 5] One-sided test (positive association)")
    logger.info("-" * 70)

    logger.info("Two-sided test:")
    result_two = test_kendall(x, y, alternative="two-sided", verbose=True)
    logger.info("\nOne-sided test (greater):")
    result_one_sided = test_kendall(x, y, alternative="greater", verbose=True)
    logger.info("Note: One-sided test has more power when direction is known")

    # Example 6: DataFrame output
    logger.info("\n[Example 6] DataFrame output")
    logger.info("-" * 70)

    result_df = test_kendall(x, y, return_as="dataframe", verbose=True)
    logger.info(
        f"\n{result_df[['var_x', 'var_y', 'statistic', 'pvalue', 'n_concordant', 'n_discordant']].to_string()}"
    )

    # Example 7: Export results
    logger.info("\n[Example 7] Export results")
    logger.info("-" * 70)

    stx.io.save(result_df, "./kendall_results.csv")
    stx.io.save(result_df, "./kendall_results.xlsx")

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
