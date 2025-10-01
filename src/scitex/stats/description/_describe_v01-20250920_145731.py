#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-12-05 09:20:53 (ywatanabe)"
# File: ./scitex_repo/src/scitex/stats/desc/_describe.py

THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/stats/desc/_describe.py"

"""
Functionality:
    - Computes descriptive statistics on PyTorch tensors
Input:
    - PyTorch tensor or numpy array
Output:
    - Descriptive statistics (mean, std, quantiles, etc.)
Prerequisites:
    - PyTorch, NumPy
"""

from typing import List, Optional, Tuple, Union

import numpy as np
import torch

from ...decorators import batch_fn, torch_fn
from ._nan import (
    nancount,
    nankurtosis,
    nanmax,
    nanmean,
    nanmin,
    nanq25,
    nanq50,
    nanq75,
    nanskewness,
    nanstd,
    nanvar,
)
from ._real import kurtosis, mean, q25, q50, q75, skewness, std


def verify_non_leakage(
    x: torch.Tensor,
    dim: Optional[Union[int, Tuple[int, ...]]] = None,
):
    """
    Verifies that statistics computation doesn't leak information across samples.

    Parameters
    ----------
    x : torch.Tensor
        Input tensor
    dim : Optional[Union[int, Tuple[int, ...]]]
        Dimension(s) used for computation

    Returns
    -------
    bool
        True if verification passes

    Raises
    ------
    AssertionError
        If statistics leak information across samples
    """
    # Full calculation
    described, _ = describe(x, dim=(1, 2))

    # Compute statistics on first sample
    x_first = x[:1]
    described_first, _ = describe(x_first, dim=dim)

    # Verify shapes match
    assert (
        described_first.shape == described[:1].shape
    ), f"Shape mismatch: {described_first.shape} != {described[:1].shape}"

    # Verify values match
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
    """
    Computes various descriptive statistics.

    Parameters
    ----------
    x : torch.Tensor
        Input tensor
    axis : int, default=-1
        Deprecated. Use dim instead
    dim : int or tuple of ints, optional
        Dimension(s) along which to compute statistics
    keepdims : bool, default=True
        Whether to keep reduced dimensions
    funcs : list of str or "all"
        Statistical functions to compute
    device : torch.device, optional
        Device to use for computation

    Returns
    -------
    Tuple[torch.Tensor, List[str]]
        Computed statistics and their names
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
        # "nanprod": nanprod,
        # "nanargmin": nanargmin,
        # "nanargmax": nanargmax,
    }

    if funcs == "all":
        _funcs = list(func_candidates.values())
        func_names = list(func_candidates.keys())
    else:
        _funcs = [func_candidates[ff] for ff in func_names]

    calculated = [ff(x, dim=dim, keepdims=keepdims) for ff in _funcs]
    return torch.stack(calculated, dim=-1), func_names


if __name__ == "__main__":
    from scitex.stats.desc._describe import describe, verify_non_leakage

    # x = np.random.rand(4, 3, 2)
    # x = np.random.rand(390, 250, 16, 100, 100)
    # print(scitex.stats.desc.nankurtosis(x, dim=(1,2)).shape)

    x = np.random.rand(10, 250, 16, 100, 100)

    described, _ = describe(x[:10], dim=(-2, -1), batch_size=1)
    # verify_non_leakage(x, dim=(1, 2))
    # # print(describe(x, dim=(1, 2), keepdims=False)[0].shape)
    # # print(describe(x, funcs="all", dim=(1, 2), keepdims=False)[0].shape)


"""
python ./scitex_repo/src/scitex/stats/desc/_describe.py
python -m src.scitex.stats.desc._describe
"""

# EOF
