#!/usr/bin/env python3
# Time-stamp: "2025-01-15 00:00:00 (ywatanabe)"
# File: ./scitex_repo/src/scitex/stats/tests/correlation/_test_spearman.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/stats/tests/correlation/_test_spearman.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------


"""
Spearman's rank correlation coefficient test.

Non-parametric measure of rank correlation (monotonic relationship).
More robust to outliers than Pearson's r.
"""

from typing import Union, Optional, Literal, Tuple
import numpy as np
import pandas as pd
from scipy import stats
from ...utils._formatters import p2stars
from ...utils._normalizers import force_dataframe, convert_results

try:
    import matplotlib
    import matplotlib.pyplot as plt
    HAS_PLT = True
except ImportError:
    HAS_PLT = False


def test_spearman(
    x: Union[np.ndarray, pd.Series],
    y: Union[np.ndarray, pd.Series],
    var_x: str = 'x',
    var_y: str = 'y',
    alternative: Literal['two-sided', 'less', 'greater'] = 'two-sided',
    alpha: float = 0.05,
    plot: bool = False,
    return_as: Literal['dict', 'dataframe'] = 'dict',
    decimals: int = 3
) -> Union[dict, pd.DataFrame, Tuple]:
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
        raise ValueError(f"x and y must have same length (got {len(x)} and {len(y)})")

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
    rho_squared = rho ** 2

    # Check significance
    significant = pvalue < alpha
    stars = p2stars(pvalue)

    # Interpret effect size (same as Pearson)
    rho_abs = abs(rho)
    if rho_abs < 0.1:
        interpretation = 'negligible'
    elif rho_abs < 0.3:
        interpretation = 'small'
    elif rho_abs < 0.5:
        interpretation = 'medium'
    else:
        interpretation = 'large'

    # Build result
    result = {
        'test_method': "Spearman's rank correlation",
        'statistic': round(rho, decimals),
        'pvalue': round(pvalue, decimals),
        'alternative': alternative,
        'alpha': alpha,
        'significant': significant,
        'stars': stars,
        'effect_size': round(rho, decimals),
        'effect_size_metric': 'rho',
        'effect_size_interpretation': interpretation,
        'rho_squared': round(rho_squared, decimals),
        'n': n,
        'var_x': var_x,
        'var_y': var_y
    }

    # Generate plot if requested
    fig = None
    if plot and HAS_PLT:
        fig = _plot_spearman(x, y, rho, pvalue, var_x, var_y, alpha)

    # Convert to requested format
    if return_as == 'dataframe':
        result = force_dataframe(result)
    elif return_as not in ['dict', 'dataframe']:
        return convert_results(result, return_as=return_as)

    # Return based on plot option
    if plot and HAS_PLT:
        return result, fig
    else:
        return result


def _plot_spearman(x, y, rho, pvalue, var_x, var_y, alpha):
    """Create 2-panel visualization for Spearman correlation."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Panel 1: Scatter plot with original values
    ax = axes[0]
    ax.scatter(x, y, alpha=0.6, s=50, edgecolor='black', linewidth=0.5)
    ax.set_xlabel(var_x)
    ax.set_ylabel(var_y)
    ax.set_title(f"Original Data")
    ax.grid(True, alpha=0.3)

    # Add trend line (non-parametric: lowess smooth)
    try:
        from scipy.signal import savgol_filter
        sorted_idx = np.argsort(x)
        x_sorted = x[sorted_idx]
        y_sorted = y[sorted_idx]
        if len(x) >= 5:
            window = min(len(x) // 2 * 2 + 1, 51)
            y_smooth = savgol_filter(y_sorted, window_length=window, polyorder=3)
            ax.plot(x_sorted, y_smooth, 'r-', alpha=0.5, linewidth=2, label='Trend')
            ax.legend()
    except:
        pass

    # Panel 2: Scatter plot with ranks
    ax = axes[1]
    x_ranks = stats.rankdata(x)
    y_ranks = stats.rankdata(y)
    ax.scatter(x_ranks, y_ranks, alpha=0.6, s=50, edgecolor='black', linewidth=0.5)

    # Add regression line for ranks
    slope, intercept = np.polyfit(x_ranks, y_ranks, 1)
    x_line = np.array([x_ranks.min(), x_ranks.max()])
    y_line = slope * x_line + intercept
    ax.plot(x_line, y_line, 'r-', alpha=0.7, linewidth=2, label='Regression line')

    ax.set_xlabel(f'Rank({var_x})')
    ax.set_ylabel(f'Rank({var_y})')

    # Add title with statistics
    stars = p2stars(pvalue)
    title = f"Spearman Correlation: ρ = {rho:.3f} {stars}\n"
    title += f"ρ² = {rho**2:.3f}, n = {len(x)}"
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    ax.legend()

    plt.tight_layout()

    return fig


# Example usage
if __name__ == '__main__':
    import matplotlib
    matplotlib.use('Agg')
    from pathlib import Path

    output_dir = Path(__file__).parent / '_test_spearman_out'
    output_dir.mkdir(exist_ok=True)

    print("=" * 70)
    print("Spearman's Rank Correlation Test - Examples")
    print("=" * 70)

    # Example 1: Perfect monotonic relationship
    print("\nExample 1: Perfect monotonic (quadratic) relationship")
    print("-" * 70)
    x1 = np.array([1, 2, 3, 4, 5])
    y1 = np.array([1, 4, 9, 16, 25])
    result1, fig1 = test_spearman(x1, y1, var_x='x', var_y='y²', plot=True)
    print(force_dataframe(result1))
    fig1.savefig(output_dir / 'example1_perfect_monotonic.png', dpi=150, bbox_inches='tight')
    plt.close(fig1)

    # Example 2: Outlier comparison
    print("\nExample 2: Robustness to outliers")
    print("-" * 70)
    x2 = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 100])
    y2 = np.array([2, 4, 6, 8, 10, 12, 14, 16, 18, 20])

    from ..correlation._test_pearson import test_pearson
    spearman_result = test_spearman(x2, y2, var_x='x', var_y='y', plot=False)
    pearson_result = test_pearson(x2, y2, var_x='x', var_y='y', plot=False)

    print("With outlier (x=100):")
    print(f"  Spearman ρ = {spearman_result['statistic']:.3f}, p = {spearman_result['pvalue']:.4f}")
    print(f"  Pearson r = {pearson_result['statistic']:.3f}, p = {pearson_result['pvalue']:.4f}")
    print("→ Spearman is more robust to the outlier")

    # Example 3: Non-linear monotonic relationship
    print("\nExample 3: Non-linear monotonic (logarithmic) relationship")
    print("-" * 70)
    np.random.seed(42)
    x3 = np.linspace(1, 50, 50)
    y3 = np.log(x3) + np.random.normal(0, 0.2, size=50)
    result3, fig3 = test_spearman(x3, y3, var_x='x', var_y='log(x)', plot=True)
    print(force_dataframe(result3))
    fig3.savefig(output_dir / 'example3_logarithmic.png', dpi=150, bbox_inches='tight')
    plt.close(fig3)

    # Example 4: Ordinal data
    print("\nExample 4: Ordinal data (Likert scales)")
    print("-" * 70)
    np.random.seed(43)
    satisfaction = np.random.randint(1, 6, size=30)
    quality = satisfaction + np.random.randint(-1, 2, size=30)
    quality = np.clip(quality, 1, 5)
    result4, fig4 = test_spearman(satisfaction, quality,
                                   var_x='Satisfaction', var_y='Quality',
                                   plot=True)
    print(force_dataframe(result4))
    fig4.savefig(output_dir / 'example4_ordinal.png', dpi=150, bbox_inches='tight')
    plt.close(fig4)

    # Example 5: One-tailed test
    print("\nExample 5: One-tailed test (expect positive correlation)")
    print("-" * 70)
    np.random.seed(44)
    x5 = np.arange(30)
    y5 = x5 + np.random.normal(0, 3, size=30)
    result5_two = test_spearman(x5, y5, alternative='two-sided', plot=False)
    result5_greater = test_spearman(x5, y5, alternative='greater', plot=False)
    print("Two-tailed test:")
    print(f"  ρ = {result5_two['statistic']:.3f}, p = {result5_two['pvalue']:.4f}")
    print("One-tailed test (greater):")
    print(f"  ρ = {result5_greater['statistic']:.3f}, p = {result5_greater['pvalue']:.4f}")

    # Example 6: Exponential relationship
    print("\nExample 6: Exponential relationship")
    print("-" * 70)
    np.random.seed(45)
    x6 = np.linspace(0, 5, 40)
    y6 = np.exp(x6 * 0.5) + np.random.normal(0, 2, size=40)
    result6, fig6 = test_spearman(x6, y6, var_x='x', var_y='exp(0.5x)', plot=True)
    print(force_dataframe(result6))
    fig6.savefig(output_dir / 'example6_exponential.png', dpi=150, bbox_inches='tight')
    plt.close(fig6)

    # Example 7: No correlation
    print("\nExample 7: No correlation")
    print("-" * 70)
    np.random.seed(46)
    x7 = np.random.normal(0, 1, size=50)
    y7 = np.random.normal(0, 1, size=50)
    result7, fig7 = test_spearman(x7, y7, var_x='x', var_y='y', plot=True)
    print(force_dataframe(result7))
    fig7.savefig(output_dir / 'example7_no_correlation.png', dpi=150, bbox_inches='tight')
    plt.close(fig7)

    # Example 8: Compare Spearman vs Pearson on skewed data
    print("\nExample 8: Spearman vs Pearson on skewed data")
    print("-" * 70)
    np.random.seed(47)
    x8 = np.random.exponential(scale=2, size=60)
    y8 = x8 ** 0.8 + np.random.normal(0, 1, size=60)

    spearman_res = test_spearman(x8, y8, plot=False)
    pearson_res = test_pearson(x8, y8, plot=False)

    print("Exponential distribution with power relationship:")
    print(f"  Spearman ρ = {spearman_res['statistic']:.3f} ({spearman_res['effect_size_interpretation']})")
    print(f"  Pearson r = {pearson_res['statistic']:.3f} ({pearson_res['effect_size_interpretation']})")

    # Example 9: Export to multiple formats
    print("\nExample 9: Export to multiple formats")
    print("-" * 70)
    np.random.seed(48)
    x9 = np.arange(25)
    y9 = 2 * x9 + np.random.normal(0, 5, size=25)
    result9 = test_spearman(x9, y9, var_x='Time', var_y='Response', return_as='dataframe')

    convert_results(result9, return_as='csv', path=output_dir / 'spearman_demo.csv')
    convert_results(result9, return_as='latex', path=output_dir / 'spearman_demo.tex')
    print("Exported to CSV and LaTeX formats")
    print(result9)

    # Example 10: Large dataset
    print("\nExample 10: Large dataset with moderate correlation")
    print("-" * 70)
    np.random.seed(49)
    n_large = 500
    x10 = np.random.normal(100, 15, size=n_large)
    y10 = 0.6 * x10 + np.random.normal(0, 20, size=n_large)
    result10, fig10 = test_spearman(x10, y10, var_x='Predictor', var_y='Outcome', plot=True)
    print(force_dataframe(result10))
    fig10.savefig(output_dir / 'example10_large_dataset.png', dpi=150, bbox_inches='tight')
    plt.close(fig10)

    print(f"\n{'='*70}")
    print(f"All examples completed. Output saved to: {output_dir}")
    print(f"{'='*70}")
