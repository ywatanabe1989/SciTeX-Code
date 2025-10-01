#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-20 16:01:20 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/stats/desc/_nan.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/stats/desc/_nan.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
- Computes NaN-aware descriptive statistics on PyTorch tensors
- Provides robust statistical measures that handle missing values
- Calculates mean, std, variance, skewness, kurtosis with NaN handling
- Computes quantiles and extreme values ignoring NaN
- Demonstrates NaN-robust statistical computations

Dependencies:
- packages:
  - torch
  - numpy
  - scitex

IO:
- input-files:
  - PyTorch tensor or numpy array with potential NaN values
- output-files:
  - NaN-robust statistical results
"""

"""Imports"""
import argparse

import numpy as np
import scitex as stx
import torch
from scitex import logging

from ...decorators import batch_fn, torch_fn

logger = logging.getLogger(__name__)

"""Functions & Classes"""
@torch_fn
@batch_fn
def nanmax(x, axis=-1, dim=None, batch_size=None, keepdims=False):
    min_value = torch.finfo(x.dtype).min
    dim = axis if dim is None else dim
    if isinstance(dim, (tuple, list)):
        for d in sorted(dim, reverse=True):
            x = x.nan_to_num(min_value).max(dim=d, keepdims=keepdims)[0]
    else:
        x = x.nan_to_num(min_value).max(dim=dim, keepdims=keepdims)[0]
    return x


@torch_fn
@batch_fn
def nanmin(x, axis=-1, dim=None, batch_size=None, keepdims=False):
    max_value = torch.finfo(x.dtype).max
    dim = axis if dim is None else dim
    if isinstance(dim, (tuple, list)):
        for d in sorted(dim, reverse=True):
            x = x.nan_to_num(max_value).min(dim=d, keepdims=keepdims)[0]
    else:
        x = x.nan_to_num(max_value).min(dim=dim, keepdims=keepdims)[0]
    return x


@torch_fn
@batch_fn
def nansum(x, axis=-1, dim=None, batch_size=None, keepdims=False):
    return torch.nansum(x, dim=dim, keepdims=keepdims)


@torch_fn
@batch_fn
def nanmean(x, axis=-1, dim=None, batch_size=None, keepdims=False):
    return torch.nanmean(x, dim=dim, keepdims=keepdims)


@torch_fn
@batch_fn
def nanvar(x, axis=-1, dim=None, batch_size=None, keepdims=False):
    tensor_mean = nanmean(x, dim=dim, keepdims=True)
    return (x - tensor_mean).square().nanmean(dim=dim, keepdims=keepdims)


@torch_fn
@batch_fn
def nanstd(x, axis=-1, dim=None, batch_size=None, keepdims=False):
    return torch.sqrt(nanvar(x, dim=dim, keepdims=keepdims))


# @torch_fn
# def nanzscore(x, axis=-1, dim=None, batch_size=None, keepdims=True):
#     _mean = nanmean(x, dim=dim, keepdims=True)
#     _std = nanstd(x, dim=dim, keepdims=True)
#     zscores = (x - _mean) / _std
#     return zscores if keepdims else zscores.squeeze(dim)
@torch_fn
@batch_fn
def nanzscore(x, axis=-1, dim=None, batch_size=None, keepdims=True):
    dim = axis if dim is None else dim
    if isinstance(dim, (tuple, list)):
        _mean = nanmean(x, dim=dim, keepdims=True)
        _std = nanstd(x, dim=dim, keepdims=True)
    else:
        _mean = nanmean(x, dim=dim, keepdims=True)
        _std = nanstd(x, dim=dim, keepdims=True)
    zscores = (x - _mean) / _std
    return zscores if keepdims else zscores.squeeze(dim)


# @torch_fn
# def nankurtosis(x, axis=-1, dim=None, batch_size=None, keepdims=False):
#     zscores = nanzscore(x, axis=axis, keepdims=True)
#     n = (~torch.isnan(x)).sum(dim=dim, keepdim=True).to(x.dtype)  # Changed this line
#     k = torch.nanmean(torch.pow(zscores, 4.0), dim=dim, keepdims=keepdims)
#     correction = (n * (n + 1)) / ((n - 1) * (n - 2) * (n - 3))
#     return correction * k - 3 * (n - 1)**2 / ((n - 2) * (n - 3))


# @torch_fn
# def nankurtosis(x, axis=-1, dim=None, batch_size=None, keepdims=False):
#     dim = axis if dim is None else dim
#     if isinstance(dim, (tuple, list)):
#         zscores = nanzscore(x, dim=dim, keepdims=True)
#         n = (~torch.isnan(x)).sum(dim=dim, keepdim=True).to(x.dtype)
#         k = torch.nanmean(torch.pow(zscores, 4.0), dim=dim, keepdims=keepdims)
#         correction = (n * (n + 1)) / ((n - 1) * (n - 2) * (n - 3))
#         result = correction * k - 3 * (n - 1)**2 / ((n - 2) * (n - 3))
#         return result.squeeze() if not keepdims else result
#     else:
#         # Original code for single dimension
#         zscores = nanzscore(x, dim=dim, keepdims=True)
#         n = (~torch.isnan(x)).sum(dim=dim, keepdim=True).to(x.dtype)
#         k = torch.nanmean(torch.pow(zscores, 4.0), dim=dim, keepdims=keepdims)
#         correction = (n * (n + 1)) / ((n - 1) * (n - 2) * (n - 3))
#         result = correction * k - 3 * (n - 1)**2 / ((n - 2) * (n - 3))
#         return result.squeeze() if not keepdims else result

# @torch_fn
# def nanskewness(x, axis=-1, dim=None, batch_size=None, keepdims=False):
#     zscores = nanzscore(x, axis=axis, keepdims=True)
#     n = (~torch.isnan(x)).sum(dim=dim, keepdim=True).to(x.dtype)  # Changed this line
#     s = torch.nanmean(torch.pow(zscores, 3.0), dim=dim, keepdims=keepdims)
#     correction = n**2 / ((n - 1) * (n - 2))
#     return correction * s


@torch_fn
@batch_fn
def nankurtosis(x, axis=-1, dim=None, batch_size=None, keepdims=False):
    zscores = nanzscore(x, axis=axis, keepdims=True)
    return (
        torch.nanmean(torch.pow(zscores, 4.0), dim=dim, keepdims=keepdims)
        - 3.0
    )


@torch_fn
@batch_fn
def nanskewness(x, axis=-1, dim=None, batch_size=None, keepdims=False):
    zscores = nanzscore(x, axis=axis, keepdims=True)
    return torch.nanmean(torch.pow(zscores, 3.0), dim=dim, keepdims=keepdims)


@torch_fn
@batch_fn
def nanprod(x, axis=-1, dim=None, batch_size=None, keepdims=False):
    dim = axis if dim is None else dim
    if isinstance(dim, (tuple, list)):
        for d in sorted(dim, reverse=True):
            x = x.nan_to_num(1).prod(dim=d, keepdims=keepdims)
    else:
        x = x.nan_to_num(1).prod(dim=dim, keepdims=keepdims)
    return x


@torch_fn
@batch_fn
def nancumprod(x, axis=-1, dim=None, batch_size=None, keepdims=False):
    dim = axis if dim is None else dim
    if isinstance(dim, (tuple, list)):
        raise ValueError("cumprod does not support multiple dimensions")
    return x.nan_to_num(1).cumprod(dim=dim)


@torch_fn
@batch_fn
def nancumsum(x, axis=-1, dim=None, batch_size=None, keepdims=False):
    dim = axis if dim is None else dim
    if isinstance(dim, (tuple, list)):
        raise ValueError("cumsum does not support multiple dimensions")
    return x.nan_to_num(0).cumsum(dim=dim)


@torch_fn
@batch_fn
def nanargmin(x, axis=-1, dim=None, batch_size=None, keepdims=False):
    max_value = torch.finfo(x.dtype).max
    dim = axis if dim is None else dim
    if isinstance(dim, (tuple, list)):
        for d in sorted(dim, reverse=True):
            x = x.nan_to_num(max_value).argmin(dim=d, keepdims=keepdims)
    else:
        x = x.nan_to_num(max_value).argmin(dim=dim, keepdims=keepdims)
    return x


@torch_fn
@batch_fn
def nanargmax(x, axis=-1, dim=None, batch_size=None, keepdims=False):
    min_value = torch.finfo(x.dtype).min
    dim = axis if dim is None else dim
    if isinstance(dim, (tuple, list)):
        for d in sorted(dim, reverse=True):
            x = x.nan_to_num(min_value).argmax(dim=d, keepdims=keepdims)
    else:
        x = x.nan_to_num(min_value).argmax(dim=dim, keepdims=keepdims)
    return x


@torch_fn
@batch_fn
def nanquantile(x, q, axis=-1, dim=None, batch_size=None, keepdims=False):
    dim = axis if dim is None else dim
    if isinstance(dim, (tuple, list)):
        # For multiple dimensions, flatten them first
        # Save original shape for potential keepdims
        original_shape = x.shape

        # Calculate new shape: keep dimensions not in dim, flatten those in dim
        dim_list = list(dim) if isinstance(dim, tuple) else dim
        # Normalize negative dimensions
        dim_list = [d if d >= 0 else len(original_shape) + d for d in dim_list]

        # Determine which dimensions to keep
        keep_dims = [
            i for i in range(len(original_shape)) if i not in dim_list
        ]

        # Permute tensor to move dims to reduce to the end
        perm_dims = keep_dims + dim_list
        x_perm = x.permute(perm_dims)

        # Reshape to flatten the dimensions to reduce
        new_shape = [original_shape[i] for i in keep_dims] + [-1]
        x_flat = x_perm.reshape(new_shape)

        # Apply nanquantile on the flattened dimension
        mask = ~torch.isnan(x_flat)
        x_filtered = torch.where(mask, x_flat, torch.tensor(float("inf")))
        result = torch.quantile(x_filtered, q / 100, dim=-1, keepdim=keepdims)

        # If keepdims, reshape back with singleton dimensions
        if keepdims:
            final_shape = list(original_shape)
            for d in dim_list:
                final_shape[d] = 1
            result = result.reshape(final_shape)

        return result
    else:
        mask = ~torch.isnan(x)
        x_filtered = torch.where(mask, x, torch.tensor(float("inf")))
        x = torch.quantile(x_filtered, q / 100, dim=dim, keepdim=keepdims)
    return x


def nanq25(x, axis=-1, dim=None, batch_size=None, keepdims=False):
    kwargs = {"axis": axis, "dim": dim, "keepdims": keepdims}
    if batch_size is not None:
        kwargs["batch_size"] = batch_size
    return nanquantile(x, 25, **kwargs)


def nanq50(x, axis=-1, dim=None, batch_size=None, keepdims=False):
    kwargs = {"axis": axis, "dim": dim, "keepdims": keepdims}
    if batch_size is not None:
        kwargs["batch_size"] = batch_size
    return nanquantile(x, 50, **kwargs)


def nanq75(x, axis=-1, dim=None, batch_size=None, keepdims=False):
    kwargs = {"axis": axis, "dim": dim, "keepdims": keepdims}
    if batch_size is not None:
        kwargs["batch_size"] = batch_size
    return nanquantile(x, 75, **kwargs)


@torch_fn
@batch_fn
def nancount(x, axis=-1, dim=None, batch_size=None, keepdims=False):
    """Count number of non-NaN values along specified dimensions.

    Parameters
    ----------
    x : torch.Tensor
        Input tensor
    axis : int, default=-1
        Deprecated. Use dim instead
    dim : int or tuple of ints, optional
        Dimension(s) along which to count
    keepdims : bool, default=True
        Whether to keep reduced dimensions

    Returns
    -------
    torch.Tensor
        Count of non-NaN values
    """
    dim = axis if dim is None else dim
    mask = ~torch.isnan(x)

    if isinstance(dim, (tuple, list)):
        for d in sorted(dim, reverse=True):
            mask = mask.sum(dim=d, keepdims=keepdims)
    else:
        mask = mask.sum(dim=dim, keepdims=keepdims)

    return mask


# @torch_fn
# @batch_fn
# def nanmax(x, axis=-1, dim=None, batch_size=None, keepdims=False):
#     min_value = torch.finfo(x.dtype).min
#     dim = axis if dim is None else dim
#     if isinstance(dim, (tuple, list)):
#         for d in sorted(dim, reverse=True):
#             x = x.nan_to_num(min_value).max(dim=d, keepdims=keepdims)[0]
#     else:
#         x = x.nan_to_num(min_value).max(dim=dim, keepdims=keepdims)[0]
#     return x


# @torch_fn
# @batch_fn
# def nanmin(x, axis=-1, dim=None, batch_size=None, keepdims=False):
#     max_value = torch.finfo(x.dtype).max
#     dim = axis if dim is None else dim
#     if isinstance(dim, (tuple, list)):
#         for d in sorted(dim, reverse=True):
#             x = x.nan_to_num(max_value).min(dim=d, keepdims=keepdims)[0]
#     else:
#         x = x.nan_to_num(max_value).min(dim=dim, keepdims=keepdims)[0]
#     return x


# @torch_fn
# @batch_fn
# def nansum(x, axis=-1, dim=None, batch_size=None, keepdims=False):
#     return torch.nansum(x, dim=dim, keepdims=keepdims)


# @torch_fn
# @batch_fn
# def nanmean(x, axis=-1, dim=None, batch_size=None, keepdims=False):
#     return torch.nanmean(x, dim=dim, keepdims=keepdims)


# @torch_fn
# @batch_fn
# def nanvar(x, axis=-1, dim=None, batch_size=None, keepdims=False):
#     tensor_mean = nanmean(x, dim=dim, keepdims=True)
#     return (x - tensor_mean).square().nanmean(dim=dim, keepdims=keepdims)


# @torch_fn
# @batch_fn
# def nanstd(x, axis=-1, dim=None, batch_size=None, keepdims=False):
#     return torch.sqrt(nanvar(x, dim=dim, keepdims=keepdims))


# @torch_fn
# @batch_fn
# def nanzscore(x, axis=-1, dim=None, batch_size=None, keepdims=True):
#     dim = axis if dim is None else dim
#     if isinstance(dim, (tuple, list)):
#         _mean = nanmean(x, dim=dim, keepdims=True)
#         _std = nanstd(x, dim=dim, keepdims=True)
#     else:
#         _mean = nanmean(x, dim=dim, keepdims=True)
#         _std = nanstd(x, dim=dim, keepdims=True)
#     zscores = (x - _mean) / _std
#     return zscores if keepdims else zscores.squeeze(dim)


# @torch_fn
# @batch_fn
# def nankurtosis(x, axis=-1, dim=None, batch_size=None, keepdims=False):
#     zscores = nanzscore(x, axis=axis, keepdims=True)
#     return (
#         torch.nanmean(torch.pow(zscores, 4.0), dim=dim, keepdims=keepdims)
#         - 3.0
#     )


# @torch_fn
# @batch_fn
# def nanskewness(x, axis=-1, dim=None, batch_size=None, keepdims=False):
#     zscores = nanzscore(x, axis=axis, keepdims=True)
#     return torch.nanmean(torch.pow(zscores, 3.0), dim=dim, keepdims=keepdims)


# @torch_fn
# @batch_fn
# def nancount(x, axis=-1, dim=None, batch_size=None, keepdims=False):
#     """Count number of non-NaN values along specified dimensions."""
#     dim = axis if dim is None else dim
#     mask = ~torch.isnan(x)
#     if isinstance(dim, (tuple, list)):
#         for d in sorted(dim, reverse=True):
#             mask = mask.sum(dim=d, keepdims=keepdims)
#     else:
#         mask = mask.sum(dim=dim, keepdims=keepdims)
#     return mask


def main(args) -> int:
    """Demonstrate NaN-aware statistics functions with synthetic data."""
    x = np.random.rand(10, 5, 3)

    # Introduce some NaN values
    x_with_nan = x.copy()
    x_with_nan[0, 0, 0] = np.nan
    x_with_nan[2, 1, 1] = np.nan
    x = torch.tensor(x_with_nan)

    # Compute NaN-aware statistics
    x_nanmean = nanmean(x)
    x_nanstd = nanstd(x)
    x_nanvar = nanvar(x)
    x_nanskew = nanskewness(x)
    x_nankurt = nankurtosis(x)
    x_nanmax = nanmax(x)
    x_nanmin = nanmin(x)
    x_nancount = nancount(x)

    # Store results
    results = {
        "input": x,
        "nan_mean": x_nanmean,
        "nan_std": x_nanstd,
        "nan_var": x_nanvar,
        "nan_skew": x_nanskew,
        "nan_kurt": x_nankurt,
        "nan_max": x_nanmax,
        "nan_min": x_nanmin,
        "nan_count": x_nancount,
    }

    for k, v in results.items():
        if isinstance(v, (np.ndarray, torch.Tensor)):
            print(f"\n{k}, Type: {type(v)}, Shape: {v.shape}, Values: {v}")
        elif isinstance(v, list):
            print(f"\n{k}, Type: {type(v)}, Length: {len(v)}, Values: {v}")
        else:
            print(f"\n{k}, Type: {type(v)}, Values: {v}")

    # # Save results
    # stx.io.save(results, "./nan_statistics.pkl")

    # # Log results
    # logger.info(f"NaN-aware mean: {x_nanmean}")
    # logger.info(f"NaN-aware std: {x_nanstd}")
    # logger.info(f"Non-NaN count: {x_nancount}")

    return 0


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Demonstrate NaN-aware statistics functions"
    )
    args = parser.parse_args()
    return args


def run_main() -> None:
    """Initialize scitex framework, run main function, and cleanup."""
    global CONFIG, CC, sys, plt, rng
    import sys

    import matplotlib.pyplot as plt
    import scitex as stx

    args = parse_args()
    CONFIG, sys.stdout, sys.stderr, plt, CC, rng = stx.session.start(
        sys,
        plt,
        args=args,
        file=__FILE__,
        sdir_suffix=None,
        verbose=False,
        agg=True,
    )

    exit_status = main(args)

    stx.session.close(
        CONFIG,
        verbose=False,
        notify=False,
        message="",
        exit_status=exit_status,
    )


if __name__ == "__main__":
    run_main()

# EOF
