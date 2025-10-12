#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: ./scitex_repo/src/scitex/stats/tests/correlation/_test_theilsen.py

"""
Theil-Sen robust regression estimator.

A non-parametric regression method that is robust to outliers.
Computes the median of slopes between all pairs of points.
"""

import warnings
from typing import Union

import numpy as np
import pandas as pd
from scipy import stats


def test_theilsen(
    x: Union[np.ndarray, pd.Series, list],
    y: Union[np.ndarray, pd.Series, list],
    var_x: str = "x",
    var_y: str = "y",
    return_as: str = "dict",
    verbose: bool = True,
) -> Union[dict, pd.DataFrame]:
    """
    Theil-Sen robust regression estimator.

    A robust non-parametric regression method that estimates the slope as the
    median of all pairwise slopes. Highly resistant to outliers (up to 29.3%
    breakdown point).

    Parameters
    ----------
    x : array-like
        Independent variable
    y : array-like
        Dependent variable
    var_x : str, default="x"
        Name of independent variable (for reporting)
    var_y : str, default="y"
        Name of dependent variable (for reporting)
    return_as : str, default="dict"
        Format of return value: "dict" or "dataframe"
    verbose : bool, default=True
        Whether to print results

    Returns
    -------
    dict or pd.DataFrame
        Dictionary or DataFrame containing:
        - slope : float
            Theil-Sen slope estimate (median of pairwise slopes)
        - intercept : float
            Intercept of the regression line
        - low_slope : float
            Lower bound of slope confidence interval
        - high_slope : float
            Upper bound of slope confidence interval
        - var_x : str
            Name of independent variable
        - var_y : str
            Name of dependent variable

    Notes
    -----
    The Theil-Sen estimator:
    - Is robust to outliers (up to ~29% outliers)
    - Has no distributional assumptions
    - Is asymptotically normal
    - Has ~64% efficiency compared to OLS for normal data
    - Computational complexity: O(n²)

    References
    ----------
    .. [1] Theil, H. (1950). "A rank-invariant method of linear and polynomial
           regression analysis". Indagationes Mathematicae, 12, 85-91.
    .. [2] Sen, P.K. (1968). "Estimates of the regression coefficient based on
           Kendall's tau". Journal of the American Statistical Association, 63,
           1379-1389.

    Examples
    --------
    >>> import numpy as np
    >>> from scitex.stats.tests.correlation import test_theilsen
    >>> x = np.array([1, 2, 3, 4, 5])
    >>> y = np.array([2, 4, 6, 8, 10])
    >>> result = test_theilsen(x, y, verbose=False)
    >>> print(f"Slope: {result['slope']:.3f}")
    Slope: 2.000

    >>> # With outlier
    >>> y_outlier = np.array([2, 4, 6, 8, 100])  # One extreme outlier
    >>> result = test_theilsen(x, y_outlier, verbose=False)
    >>> print(f"Robust slope: {result['slope']:.3f}")
    Robust slope: 2.000
    """
    # Convert inputs to numpy arrays
    x = np.asarray(x).flatten()
    y = np.asarray(y).flatten()

    # Remove NaN/Inf
    mask = np.isfinite(x) & np.isfinite(y)
    if not mask.all():
        n_removed = (~mask).sum()
        warnings.warn(
            f"Removed {n_removed} NaN/Inf values from input data",
            UserWarning,
        )
        x = x[mask]
        y = y[mask]

    # Check for sufficient data
    if len(x) < 3:
        raise ValueError(
            f"Need at least 3 valid data points, got {len(x)}"
        )

    # Check for variation
    if len(np.unique(x)) < 2:
        raise ValueError(
            "Independent variable has no variation (constant values)"
        )

    # Compute Theil-Sen estimator
    result = stats.theilslopes(y, x, alpha=0.95)

    # Prepare output dictionary
    output = {
        "slope": result.slope,
        "intercept": result.intercept,
        "low_slope": result.low_slope,
        "high_slope": result.high_slope,
        "var_x": var_x,
        "var_y": var_y,
    }

    # Print results if verbose
    if verbose:
        print("\n" + "=" * 70)
        print("Theil-Sen Robust Regression")
        print("=" * 70)
        print(f"Variables: {var_y} ~ {var_x}")
        print(f"Sample size: n = {len(x)}")
        print(f"\nResults:")
        print(f"  Slope:     {output['slope']:.6f}")
        print(f"  Intercept: {output['intercept']:.6f}")
        print(f"  95% CI:    [{output['low_slope']:.6f}, {output['high_slope']:.6f}]")
        print(f"\nInterpretation:")
        print(f"  For each unit increase in {var_x},")
        print(f"  {var_y} changes by {output['slope']:.6f} units (median slope)")
        print("=" * 70 + "\n")

    # Return as requested format
    if return_as == "dataframe":
        return pd.DataFrame([output])
    elif return_as == "dict":
        return output
    else:
        raise ValueError(
            f"return_as must be 'dict' or 'dataframe', got '{return_as}'"
        )


if __name__ == "__main__":
    # Example usage
    np.random.seed(42)

    # Clean data
    print("Example 1: Clean linear data")
    x = np.linspace(0, 10, 50)
    y = 2 * x + 1 + np.random.normal(0, 1, 50)
    result = test_theilsen(x, y, var_x="x", var_y="y")

    # Data with outliers
    print("\n" + "=" * 70)
    print("Example 2: Data with outliers")
    x_out = np.linspace(0, 10, 50)
    y_out = 2 * x_out + 1 + np.random.normal(0, 1, 50)
    # Add outliers
    y_out[[10, 20, 30]] += np.array([20, -15, 25])
    result_out = test_theilsen(x_out, y_out, var_x="x", var_y="y")

    # Compare with OLS
    from scipy.stats import linregress
    ols = linregress(x_out, y_out)
    print(f"\nComparison:")
    print(f"  Theil-Sen slope: {result_out['slope']:.6f}")
    print(f"  OLS slope:       {ols.slope:.6f}")
    print(f"  True slope:      2.000000")
    print(f"\nTheil-Sen is more robust to the {((y_out[[10,20,30]] - (2*x_out[[10,20,30]] + 1)) != 0).sum()} outliers!")
