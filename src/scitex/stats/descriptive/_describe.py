#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-20 15:05:08 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/stats/desc/_describe.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
- Computes comprehensive descriptive statistics on PyTorch tensors
- Provides batch processing for large datasets
- Validates non-leakage of information across samples
- Combines multiple statistical measures into single function
- Demonstrates statistical analysis with synthetic data

Dependencies:
- packages:
  - torch
  - numpy
  - scitex

IO:
- input-files:
  - PyTorch tensor or numpy array
- output-files:
  - Combined descriptive statistics results
"""

"""Imports"""
import argparse
from typing import List, Optional, Tuple, Union

import numpy as np
import scitex as stx
import torch
from scitex import logging

from ...decorators import batch_fn, torch_fn
from ._nan import (nancount, nankurtosis, nanmax, nanmean, nanmin, nanq25,
                   nanq50, nanq75, nanskewness, nanstd, nanvar)
from ._real import kurtosis, mean, q25, q50, q75, skewness, std

logger = logging.getLogger(__name__)

"""Functions & Classes"""
def verify_non_leakage(
    x: torch.Tensor,
    dim: Optional[Union[int, Tuple[int, ...]]] = None,
):
    """Verifies that statistics computation doesn't leak information across samples."""
    described, _ = describe(x, dim=(1, 2))
    x_first = x[:1]
    described_first, _ = describe(x_first, dim=dim)

    assert (
        described_first.shape == described[:1].shape
    ), f"Shape mismatch: {described_first.shape} != {described[:1].shape}"

    torch.testing.assert_close(
        described_first,
        described[:1],
        rtol=1e-5,
        atol=1e-8,
        msg="Statistics leak information across samples",
    )
    return True


@batch_fn
@torch_fn
def describe(
    x: torch.Tensor,
    axis: int = -1,
    dim: Optional[Union[int, Tuple[int, ...]]] = None,
    keepdims: bool = False,
    funcs: Union[List[str], str] = [
        "nanmean",
        "nanstd",
        "nankurtosis",
        "nanskewness",
        "nanq25",
        "nanq50",
        "nanq75",
    ],
    device: Optional[torch.device] = None,
    batch_size: int = -1,
) -> Tuple[torch.Tensor, List[str]]:
    """Compute descriptive statistics.

    Parameters
    ----------
    x : torch.Tensor
        Input tensor with batch dimension as first axis
    axis : int, default=-1
        Deprecated. Use dim instead
    dim : int or tuple of ints, optional
        Dimension(s) along which to compute statistics
    keepdims : bool, default=False
        Whether to keep reduced dimensions
    funcs : list of str or "all", default=["nanmean", "nanstd", "nankurtosis", "nanskewness", "nanq25", "nanq50", "nanq75"]
        Statistical functions to compute
    device : torch.device, optional
        Device to use for computation
    batch_size : int, default=-1
        Batch size for processing (handled by decorator)

    Returns
    -------
    Tuple[torch.Tensor, List[str]]
        Computed statistics stacked along last dimension and their names
    """

    dim = axis if dim is None else dim
    dim = (dim,) if isinstance(dim, int) else tuple(dim)

    func_names = funcs
    func_candidates = {
        "mean": mean,
        "std": std,
        "kurtosis": kurtosis,
        "skewness": skewness,
        "q25": q25,
        "q50": q50,
        "q75": q75,
        "nanmean": nanmean,
        "nanstd": nanstd,
        "nanvar": nanvar,
        "nankurtosis": nankurtosis,
        "nanskewness": nanskewness,
        "nanq25": nanq25,
        "nanq50": nanq50,
        "nanq75": nanq75,
        "nanmax": nanmax,
        "nanmin": nanmin,
        "nancount": nancount,
    }

    if funcs == "all":
        _funcs = list(func_candidates.values())
        func_names = list(func_candidates.keys())
    else:
        _funcs = [func_candidates[ff] for ff in func_names]

    calculated = [ff(x, dim=dim, keepdims=keepdims) for ff in _funcs]
    return torch.stack(calculated, dim=-1), func_names


def main(args) -> int:
    """Demonstrate comprehensive descriptive statistics with synthetic data."""
    x = np.random.rand(10, 250, 16, 100, 100)

    # Compute comprehensive statistics
    described, method_names = describe(x[:10], dim=(-2, -1), batch_size=1)

    # Store results
    results = {
        "input": x,
        "described": described,
        "method_names": method_names,
    }

    for k, v in results.items():
        if isinstance(v, (np.ndarray, torch.Tensor)):
            print(f"\n{k}, Type: {type(v)}, Shape: {v.shape}, Values: {v}")
        elif isinstance(v, list):
            print(f"\n{k}, Type: {type(v)}, Length: {len(v)}, Values: {v}")
        else:
            print(f"\n{k}, Type: {type(v)}, Values: {v}")

    return 0


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Demonstrate comprehensive descriptive statistics"
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
