#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-01 21:47:27 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/stats/tests/correlation/_test_pearson.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/stats/tests/correlation/_test_pearson.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
  - Perform Pearson correlation test
  - Compute correlation coefficient with confidence intervals
  - Test significance of correlation
  - Generate scatter plots with regression lines
  - Support flexible output formats (dict or DataFrame)

Dependencies:
  - packages: numpy, pandas, scipy, matplotlib

IO:
  - input: Two continuous variables (arrays or Series)
  - output: Test results (dict or DataFrame) and optional figure
"""

"""Imports"""
import argparse
from typing import Literal, Optional, Union

import matplotlib.axes
import numpy as np
import pandas as pd
import scitex as stx
from scipy import stats
from scitex.logging import getLogger

logger = getLogger(__name__)

"""Functions"""


def test_pearson(
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
    Perform Pearson correlation test.

    Parameters
    ----------
    x, y : arrays or Series
        Two continuous variables
    var_x, var_y : str
        Labels for variables
    alternative : {'two-sided', 'less', 'greater'}, default 'two-sided'
        Alternative hypothesis
    alpha : float, default 0.05
        Significance level for confidence interval
    plot : bool, default False
        Whether to generate scatter plot
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
    results : dict or DataFrame
        Test results including:
        - test_method: 'Pearson correlation'
        - statistic: Pearson correlation coefficient
        - pvalue: p-value
        - stars: Significance stars
        - significant: Whether null hypothesis is rejected
        - ci_lower, ci_upper: Confidence interval bounds
        - r_squared: Coefficient of determination
        - effect_size: Correlation coefficient (same as statistic)
        - effect_size_metric: 'Pearson r'
        - effect_size_interpretation: Interpretation
        - n: Sample size (after removing NaN pairs)
        - var_x, var_y: Variable labels
        - H0: Null hypothesis description

    Notes
    -----
    Pearson correlation coefficient measures the linear relationship between
    two continuous variables.

    **Null Hypothesis (H0)**: No linear correlation (ρ = 0)

    **Pearson's r**:

    .. math::
        r = \\frac{\\sum(x_i - \\bar{x})(y_i - \\bar{y})}{\\sqrt{\\sum(x_i - \\bar{x})^2 \\sum(y_i - \\bar{y})^2}}

    Range: -1 ≤ r ≤ 1
    - r = 1: Perfect positive linear relationship
    - r = 0: No linear relationship
    - r = -1: Perfect negative linear relationship

    **Coefficient of determination (R²)**:

    .. math::
        R^2 = r^2

    R² represents the proportion of variance in y explained by x.

    **Interpretation (Cohen, 1988)**:
    - |r| < 0.1:  negligible
    - |r| < 0.3:  small
    - |r| < 0.5:  medium
    - |r| ≥ 0.5:  large

    **Assumptions**:
    1. **Linearity**: Relationship between variables is linear
    2. **Normality**: Both variables are normally distributed (for hypothesis testing)
    3. **Homoscedasticity**: Variance is constant across the range
    4. **Independence**: Observations are independent

    **When to use**:
    - Assessing linear relationship between two continuous variables
    - Both variables approximately normally distributed
    - No major outliers present
    - Relationship appears linear on scatter plot

    **When NOT to use**:
    - Non-linear relationships (consider transformation or Spearman)
    - Ordinal data (use Spearman)
    - Severe outliers present (use Spearman)
    - Non-normal distributions (use Spearman)

    **Confidence Interval**:
    Computed using Fisher's z-transformation:

    .. math::
        z = 0.5 \\ln\\left(\\frac{1+r}{1-r}\\right)

    References
    ----------
    .. [1] Pearson, K. (1896). "Mathematical contributions to the theory of
           evolution. III. Regression, heredity, and panmixia". Philosophical
           Transactions of the Royal Society of London. Series A, 187, 253-318.
    .. [2] Cohen, J. (1988). Statistical Power Analysis for the Behavioral
           Sciences (2nd ed.). Routledge.

    Examples
    --------
    >>> # Strong positive correlation
    >>> x = np.array([1, 2, 3, 4, 5])
    >>> y = np.array([2, 4, 5, 7, 8])
    >>> result = test_pearson(x, y)
    >>> result['statistic']
    0.98...

    >>> # With visualization
    >>> result, fig = test_pearson(x, y, plot=True)
    """
    from ...utils._formatters import p2stars
    from ...utils._normalizers import convert_results, force_dataframe

    # Convert to numpy arrays
    x = np.asarray(x)
    y = np.asarray(y)

    # Remove NaN pairs (pairwise deletion)
    valid_mask = ~(np.isnan(x) | np.isnan(y))
    x = x[valid_mask]
    y = y[valid_mask]

    n = len(x)

    if n < 3:
        raise ValueError("Pearson correlation requires at least 3 valid pairs")

    # Perform Pearson correlation test
    r, pvalue = stats.pearsonr(x, y)
    r = float(r)
    pvalue = float(pvalue)

    # Adjust p-value for alternative hypothesis
    if alternative == "less":
        if r > 0:
            pvalue = 1 - pvalue / 2
        else:
            pvalue = pvalue / 2
    elif alternative == "greater":
        if r < 0:
            pvalue = 1 - pvalue / 2
        else:
            pvalue = pvalue / 2

    # Determine rejection
    rejected = pvalue < alpha

    # Compute confidence interval using Fisher's z-transformation
    z = np.arctanh(r)  # Fisher's z
    se = 1 / np.sqrt(n - 3)  # Standard error of z
    z_crit = stats.norm.ppf(1 - alpha / 2)

    z_lower = z - z_crit * se
    z_upper = z + z_crit * se

    ci_lower = np.tanh(z_lower)
    ci_upper = np.tanh(z_upper)

    # Compute R-squared
    r_squared = r**2

    # Interpret effect size
    r_abs = abs(r)
    if r_abs < 0.1:
        effect_interp = "negligible"
    elif r_abs < 0.3:
        effect_interp = "small"
    elif r_abs < 0.5:
        effect_interp = "medium"
    else:
        effect_interp = "large"

    # Compile results
    result = {
        "test_method": "Pearson correlation",
        "statistic": round(r, decimals),
        "n": n,
        "var_x": var_x,
        "var_y": var_y,
        "pvalue": round(pvalue, decimals),
        "stars": p2stars(pvalue),
        "alpha": alpha,
        "significant": rejected,
        "ci_lower": round(ci_lower, decimals),
        "ci_upper": round(ci_upper, decimals),
        "r_squared": round(r_squared, decimals),
        "effect_size": round(r, decimals),
        "effect_size_metric": "Pearson r",
        "effect_size_interpretation": effect_interp,
        "H0": f"No linear correlation between {var_x} and {var_y}",
    }

    # Add interpretation
    if rejected:
        direction = "positive" if r > 0 else "negative"
        result["interpretation"] = (
            f"Significant {direction} correlation detected "
            f"(r = {r:.3f}, 95% CI [{ci_lower:.3f}, {ci_upper:.3f}])"
        )
    else:
        result["interpretation"] = (
            f"No significant correlation detected (r = {r:.3f})"
        )

    # Log results if verbose
    if verbose:
        logger.info(
            f"Pearson: r = {r:.3f}, p = {pvalue:.4f} {p2stars(pvalue)}"
        )
        logger.info(
            f"R² = {r_squared:.3f} ({effect_interp}), 95% CI [{ci_lower:.3f}, {ci_upper:.3f}]"
        )

    # Auto-enable plotting if ax is provided
    if ax is not None:
        plot = True

    # Generate plot if requested
    if plot:
        if ax is None:
            fig, ax = stx.plt.subplots()
        _plot_pearson(x, y, var_x, var_y, result, ax)

    # Convert to requested format
    if return_as == "dataframe":
        result = force_dataframe(result)
    elif return_as not in ["dict", "dataframe"]:
        return convert_results(result, return_as=return_as)

    return result


def _plot_pearson(x, y, var_x, var_y, result, ax):
    """Create scatter plot with regression line on given axes."""
    # Scatter plot
    ax.scatter(
        x,
        y,
        alpha=0.6,
        s=50,
        color="C0",
        edgecolors="white",
        linewidths=0.5,
        zorder=3,
    )

    # Regression line
    z = np.polyfit(x, y, 1)
    p = np.poly1d(z)
    x_line = np.linspace(np.min(x), np.max(x), 100)
    ax.plot(
        x_line,
        p(x_line),
        "r-",
        linewidth=2,
        label=f'r = {result["statistic"]:.3f}',
        zorder=2,
    )

    ax.set_xlabel(var_x)
    ax.set_ylabel(var_y)
    ax.set_title(
        f'Pearson Correlation\nr = {result["statistic"]:.3f}, p = {result["pvalue"]:.4f} {result["stars"]}'
    )
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Add text with results
    text_str = (
        f"r = {result['statistic']:.3f} {result['stars']}\n"
        f"p = {result['pvalue']:.4f}\n"
        f"95% CI [{result['ci_lower']:.3f}, {result['ci_upper']:.3f}]\n"
        f"R² = {result['r_squared']:.3f}\n"
        f"n = {result['n']}"
    )
    ax.text(
        0.02,
        0.98,
        text_str,
        transform=ax.transAxes,
        verticalalignment="top",
        bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5),
        fontsize=10,
    )


"""Main function"""


def main(args):
    """Demonstrate Pearson correlation functionality."""
    logger.info("Demonstrating Pearson correlation test")

    # Set random seed
    np.random.seed(42)

    # Example 1: Strong positive correlation
    logger.info("\n=== Example 1: Strong positive correlation ===")

    x1 = np.random.normal(0, 1, 50)
    y1 = 2 * x1 + np.random.normal(0, 0.5, 50)  # y ≈ 2x with noise

    result1 = test_pearson(x1, y1, var_x="X", var_y="Y", verbose=True)

    # Example 2: Negative correlation
    logger.info("\n=== Example 2: Negative correlation ===")

    x2 = np.random.normal(0, 1, 50)
    y2 = -1.5 * x2 + np.random.normal(0, 0.8, 50)

    result2 = test_pearson(
        x2, y2, var_x="Temperature", var_y="Ice Cream Sales", verbose=True
    )

    # Example 3: No correlation
    logger.info("\n=== Example 3: No correlation ===")

    x3 = np.random.normal(0, 1, 50)
    y3 = np.random.normal(0, 1, 50)  # Independent

    result3 = test_pearson(
        x3, y3, var_x="Variable A", var_y="Variable B", verbose=True
    )

    # Example 4: With visualization (demonstrates plt.gcf() and stx.io.save())
    logger.info("\n=== Example 4: With visualization ===")

    x4 = np.random.normal(100, 15, 60)
    y4 = 0.8 * x4 + 20 + np.random.normal(0, 10, 60)

    result4 = test_pearson(
        x4,
        y4,
        var_x="Study Hours",
        var_y="Test Score",
        plot=True,
        verbose=True,
    )

    # Save the figure using plt.gcf()
    stx.io.save(plt.gcf(), "./.dev/pearson_demo.jpg")
    plt.close()
    logger.info("Figure saved to ./.dev/pearson_demo.jpg")

    # Example 5: One-sided tests
    logger.info("\n=== Example 5: One-sided tests ===")

    x5 = np.random.normal(0, 1, 40)
    y5 = 1.2 * x5 + np.random.normal(0, 0.5, 40)

    result_two = test_pearson(x5, y5, alternative="two-sided")
    result_greater = test_pearson(x5, y5, alternative="greater")

    logger.info(f"Two-sided: p = {result_two['pvalue']:.4f}")
    logger.info(f"One-sided (greater): p = {result_greater['pvalue']:.4f}")

    # Example 6: Effect of sample size
    logger.info("\n=== Example 6: Effect of sample size ===")

    # Small sample
    x_small = np.random.normal(0, 1, 10)
    y_small = 0.5 * x_small + np.random.normal(0, 0.8, 10)

    # Large sample
    x_large = np.random.normal(0, 1, 100)
    y_large = 0.5 * x_large + np.random.normal(0, 0.8, 100)

    result_small = test_pearson(x_small, y_small)
    result_large = test_pearson(x_large, y_large)

    logger.info(
        f"Small sample (n=10):  r = {result_small['statistic']:.3f}, p = {result_small['pvalue']:.4f}"
    )
    logger.info(
        f"Large sample (n=100): r = {result_large['statistic']:.3f}, p = {result_large['pvalue']:.4f}"
    )
    logger.info("Note: Larger samples provide narrower confidence intervals")

    # Example 7: Effect of outliers
    logger.info("\n=== Example 7: Effect of outliers ===")

    x7 = np.random.normal(0, 1, 40)
    y7 = 0.5 * x7 + np.random.normal(0, 0.5, 40)

    # Without outliers
    result_clean = test_pearson(x7, y7)

    # With outliers
    x7_outlier = np.append(x7, [5, 5.5])
    y7_outlier = np.append(y7, [-3, -3.5])

    result_outlier = test_pearson(x7_outlier, y7_outlier)

    logger.info(f"Without outliers: r = {result_clean['statistic']:.3f}")
    logger.info(f"With outliers:    r = {result_outlier['statistic']:.3f}")
    logger.info(
        "Note: Pearson correlation is sensitive to outliers. Use Spearman if outliers present."
    )

    # Example 8: Comparison with Spearman
    logger.info(
        "\n=== Example 8: Pearson vs Spearman (non-linear relationship) ==="
    )

    x8 = np.linspace(0, 10, 50)
    y8 = x8**2 + np.random.normal(0, 5, 50)  # Quadratic relationship

    pearson_result = test_pearson(x8, y8)

    # Note: Spearman will be implemented separately
    logger.info(f"Pearson r = {pearson_result['statistic']:.3f}")
    logger.info(
        "Note: For non-linear monotonic relationships, use Spearman correlation"
    )

    # Example 9: Multiple correlations
    logger.info("\n=== Example 9: Multiple correlation analyses ===")

    # Correlation matrix scenario
    data = {
        "Age": np.random.normal(40, 10, 50),
        "Income": np.random.normal(50000, 15000, 50),
        "Education": np.random.normal(16, 3, 50),
    }

    # Income vs Age
    result_ia = test_pearson(
        data["Income"], data["Age"], var_x="Income", var_y="Age"
    )

    # Income vs Education
    result_ie = test_pearson(
        data["Income"], data["Education"], var_x="Income", var_y="Education"
    )

    # Age vs Education
    result_ae = test_pearson(
        data["Age"], data["Education"], var_x="Age", var_y="Education"
    )

    logger.info(
        f"Income vs Age:       r = {result_ia['statistic']:.3f}, p = {result_ia['pvalue']:.4f}"
    )
    logger.info(
        f"Income vs Education: r = {result_ie['statistic']:.3f}, p = {result_ie['pvalue']:.4f}"
    )
    logger.info(
        f"Age vs Education:    r = {result_ae['statistic']:.3f}, p = {result_ae['pvalue']:.4f}"
    )
    logger.info(
        "Note: For multiple comparisons, apply correction (e.g., Bonferroni)"
    )

    # Example 10: Export results
    logger.info("\n=== Example 10: Export results ===")

    from ...utils._normalizers import convert_results, force_dataframe

    test_results = [
        result1,
        result2,
        result3,
        result4,
        result_small,
        result_large,
    ]

    df = force_dataframe(test_results)
    logger.info(f"\nDataFrame shape: {df.shape}")

    stx.io.save(df, "./pearson_tests.xlsx")
    stx.io.save(df, "./pearson_tests.csv")

    # convert_results(test_results, return_as='excel', path='./pearson_tests.xlsx')
    # logger.info("Results exported to Excel")

    # convert_results(test_results, return_as='csv', path='./pearson_tests.csv')
    # logger.info("Results exported to CSV")

    return 0


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Demonstrate Pearson correlation test"
    )
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
