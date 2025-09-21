#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-17 21:17:13 (ywatanabe)"
# File: ./scitex_repo/src/scitex/stats/desc/_real.py

THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/stats/desc/_real.py"

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


import numpy as np
import torch

from ...decorators import torch_fn


@torch_fn
def mean(x, axis=-1, dim=None, keepdims=False):
    return x.mean(dim, keepdims=keepdims)


@torch_fn
def std(x, axis=-1, dim=None, keepdims=False):
    return x.std(dim, keepdims=keepdims)


@torch_fn
def var(x, axis=-1, dim=None, keepdims=False):
    return x.var(dim, keepdims=keepdims)


@torch_fn
def zscore(x, axis=-1, dim=None, keepdims=True):
    _mean = mean(x, dim=dim, keepdims=True)
    _std = std(x, dim=dim, keepdims=True)
    zscores = (x - _mean) / _std
    return zscores if keepdims else zscores.squeeze(dim)


@torch_fn
def skewness(x, axis=-1, dim=None, keepdims=False):
    zscores = zscore(x, axis=axis, keepdims=True)
    return torch.mean(torch.pow(zscores, 3.0), dim=dim, keepdims=keepdims)


@torch_fn
def kurtosis(x, axis=-1, dim=None, keepdims=False):
    zscores = zscore(x, axis=axis, keepdims=True)
    return torch.mean(torch.pow(zscores, 4.0), dim=dim, keepdims=keepdims) - 3.0


@torch_fn
def quantile(x, q, axis=-1, dim=None, keepdims=False):
    dim = axis if dim is None else dim
    if isinstance(dim, (tuple, list)):
        for d in sorted(dim, reverse=True):
            x = torch.quantile(x, q / 100, dim=d, keepdims=keepdims)
    else:
        x = torch.quantile(x, q / 100, dim=dim, keepdims=keepdims)
    return x


@torch_fn
def q25(x, axis=-1, dim=None, keepdims=False):
    return quantile(x, 25, axis=axis, dim=dim, keepdims=keepdims)


@torch_fn
def q50(x, axis=-1, dim=None, keepdims=False):
    return quantile(x, 50, axis=axis, dim=dim, keepdims=keepdims)


@torch_fn
def q75(x, axis=-1, dim=None, keepdims=False):
    return quantile(x, 75, axis=axis, dim=dim, keepdims=keepdims)


if __name__ == "__main__":
    # from scitex.stats.desc import *

    x = np.random.rand(4, 3, 2)
    print(describe(x, dim=(1, 2), keepdims=False)[0].shape)
    print(describe(x, funcs="all", dim=(1, 2), keepdims=False)[0].shape)

# EOF
