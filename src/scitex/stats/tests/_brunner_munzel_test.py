#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-10-07 22:30:46 (ywatanabe)"
# File: /home/ywatanabe/proj/_scitex_repo_openhands/src/scitex/stats/_brunner_munzel_test.py

"""
1. Functionality:
   - Calculates Brunner-Munzel test scores for two independent samples
2. Input:
   - Two arrays of numeric data values
3. Output:
   - Dictionary containing test results (w_statistic, p_value, sample sizes, degrees of freedom, effect size, test name, and null hypothesis)
4. Prerequisites:
   - NumPy, SciPy
"""

"""Imports"""
import numpy as np
from scipy import stats
import pandas as pd
import xarray as xr
import torch
from typing import (
    List,
    Tuple,
    Dict,
    Any,
    Union,
    Sequence,
    Literal,
    Iterable,
)
from ...types import ArrayLike
from ...decorators import numpy_fn


@numpy_fn
def brunner_munzel_test(
    x1: ArrayLike,
    x2: ArrayLike,
    distribution: str = "t",
    round_factor: int = 3,
) -> Dict[str, Union[float, int, str]]:
    """
    Calculate Brunner-Munzel test scores.

    Parameters
    ----------
    x1 : ArrayLike
        Numeric data values from sample 1.
    x2 : ArrayLike
        Numeric data values from sample 2.
    distribution : str, optional
        Distribution to use for the test. Can be "t" or "normal" (default is "t").
    round_factor : int, optional
        Number of decimal places to round the results (default is 3).

    Returns
    -------
    Dict[str, Union[float, int, str]]
        Dictionary containing test results including w_statistic, p_value, sample sizes, degrees of freedom, effect size, test name, and null hypothesis.

    Example
    -------
    >>> np.random.seed(42)
    >>> xx = np.random.rand(100)
    >>> yy = np.random.rand(100) + 0.1
    >>> result = brunner_munzel_test(xx, yy)
    >>> print(result)
    {'w_statistic': -2.089, 'p_value': 0.038, 'n1': 100, 'n2': 100, 'dof': 197.0, 'effsize': 0.438, 'test_name': 'Brunner-Munzel test', 'H0': 'The probability that a randomly selected value from one population is greater than a randomly selected value from the other population is equal to 0.5'}
    """
    if distribution not in ["t", "normal"]:
        raise ValueError("Distribution must be either 't' or 'normal'")

    x1, x2 = np.asarray(x1).astype(float), np.asarray(x2).astype(float)
    x1, x2 = x1[~np.isnan(x1)], x2[~np.isnan(x2)]
    n1, n2 = len(x1), len(x2)

    if n1 == 0 or n2 == 0:
        raise ValueError("Input arrays must not be empty after removing NaN values")

    R = stats.rankdata(np.concatenate([x1, x2]))
    R1, R2 = R[:n1], R[n1:]
    r1_mean, r2_mean = np.mean(R1), np.mean(R2)
    Ri1, Ri2 = stats.rankdata(x1), stats.rankdata(x2)
    var1 = np.var(R1 - Ri1, ddof=1)
    var2 = np.var(R2 - Ri2, ddof=1)

    w_statistic = ((n1 * n2) * (r2_mean - r1_mean)) / (
        (n1 + n2) * np.sqrt(n1 * var1 + n2 * var2)
    )

    if distribution == "t":
        dof = (n1 * var1 + n2 * var2) ** 2 / (
            (n1 * var1) ** 2 / (n1 - 1) + (n2 * var2) ** 2 / (n2 - 1)
        )
        c = stats.t.cdf(abs(w_statistic), dof) if not np.isinf(w_statistic) else 0.0
    else:
        dof = np.nan
        c = stats.norm.cdf(abs(w_statistic)) if not np.isinf(w_statistic) else 0.0

    p_value = min(c, 1.0 - c) * 2.0
    effsize = (r2_mean - r1_mean) / (n1 + n2) + 0.5

    return {
        "w_statistic": round(w_statistic, round_factor),
        "p_value": round(p_value, round_factor),
        "n1": n1,
        "n2": n2,
        "dof": round(dof, round_factor),
        "effsize": round(effsize, round_factor),
        "test_name": "Brunner-Munzel test",
        "H0": "The probability that a randomly selected value from one population is greater than a randomly selected value from the other population is equal to 0.5",
    }


# #!/usr/bin/env python3

# import numpy as np
# from scipy import stats


# def brunner_munzel_test(x1, x2, distribution="t", round_factor=3):
#     """Calculate Brunner-Munzel-test scores.
#     Parameters:
#       x1, x2: array_like
#         Numeric data values from sample 1, 2.
#     Returns:
#       w:
#         Calculated test statistic.
#       p_value:
#         Two-tailed p-value of test.
#       dof:
#         Degree of freedom.
#       p:
#         "P(x1 < x2) + 0.5 P(x1 = x2)" estimates.
#     References:
#       * https://oku.edu.mie-u.ac.jp/~okumura/stat/brunner-munzel.html
#     Example:
#       When sample number N is small, distribution='t' is recommended.
#       d1 = np.array([1,2,1,1,1,1,1,1,1,1,2,4,1,1])
#       d2 = np.array([3,3,4,3,1,2,3,1,1,5,4])
#       print(bmtest(d1, d2, distribution='t'))
#       print(bmtest(d1, d2, distribution='normal'))
#       When sample number N is large, distribution='normal' is recommended; however,
#       't' and 'normal' yield almost the same result.
#       d1 = np.random.rand(1000)*100
#       d2 = np.random.rand(10000)*110
#       print(bmtest(d1, d2, distribution='t'))
#       print(bmtest(d1, d2, distribution='normal'))
#     """

#     x1, x2 = np.hstack(x1), np.hstack(x2)
#     x1, x2 = x1[~np.isnan(x1)], x2[~np.isnan(x2)]
#     n1, n2 = len(x1), len(x2)
#     R = stats.rankdata(list(x1) + list(x2))
#     R1, R2 = R[:n1], R[n1:]
#     r1_mean, r2_mean = np.mean(R1), np.mean(R2)
#     Ri1, Ri2 = stats.rankdata(x1), stats.rankdata(x2)
#     var1 = np.var([r - ri for r, ri in zip(R1, Ri1)], ddof=1)
#     var2 = np.var([r - ri for r, ri in zip(R2, Ri2)], ddof=1)
#     w_statistic = ((n1 * n2) * (r2_mean - r1_mean)) / (
#         (n1 + n2) * np.sqrt(n1 * var1 + n2 * var2)
#     )
#     if distribution == "t":
#         dof = (n1 * var1 + n2 * var2) ** 2 / (
#             (n1 * var1) ** 2 / (n1 - 1) + (n2 * var2) ** 2 / (n2 - 1)
#         )
#         c = (
#             stats.t.cdf(abs(w_statistic), dof)
#             if not np.isinf(w_statistic)
#             else 0.0
#         )
#     if distribution == "normal":
#         dof = np.nan
#         c = (
#             stats.norm.cdf(abs(w_statistic))
#             if not np.isinf(w_statistic)
#             else 0.0
#         )
#     p_value = min(c, 1.0 - c) * 2.0
#     effsize = (r2_mean - r1_mean) / (n1 + n2) + 0.5
#     return dict(
#         w_statistic=round(w_statistic, round_factor),
#         p_value=round(p_value, round_factor),
#         n1=n1,
#         n2=n2,
#         dof=round(dof, round_factor),
#         effsize=round(effsize, round_factor),
#         test_name="Brunner-Munzel test",
#         H0="The probability that a randomly selected value from one population is greater than a randomly selected value from the other population is equal to 0.5",
#     )
