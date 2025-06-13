#!/usr/bin/env python3
"""Scitex desc module."""

from ._describe import describe, verify_non_leakage
from ._nan import nanargmax, nanargmin, nancount, nancumprod, nancumsum, nankurtosis, nanmax, nanmean, nanmin, nanprod, nanq25, nanq50, nanq75, nanquantile, nanskewness, nanstd, nansum, nanvar, nanzscore
from ._real import kurtosis, mean, q25, q50, q75, quantile, skewness, std, var, zscore

__all__ = [
    "describe",
    "kurtosis",
    "mean",
    "nanargmax",
    "nanargmin",
    "nancount",
    "nancumprod",
    "nancumsum",
    "nankurtosis",
    "nanmax",
    "nanmean",
    "nanmin",
    "nanprod",
    "nanq25",
    "nanq50",
    "nanq75",
    "nanquantile",
    "nanskewness",
    "nanstd",
    "nansum",
    "nanvar",
    "nanzscore",
    "q25",
    "q50",
    "q75",
    "quantile",
    "skewness",
    "std",
    "var",
    "verify_non_leakage",
    "zscore",
]
