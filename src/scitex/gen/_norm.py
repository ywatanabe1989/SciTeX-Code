#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-19 01:09:55 (ywatanabe)"
# File: ./scitex_repo/src/scitex/gen/_norm.py

THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/gen/_norm.py"

import torch

from ..decorators import torch_fn
from ..torch import nanstd


@torch_fn
def to_z(x, axis=-1, dim=None, device="cuda"):
    """Standardizes tensor to zero mean and unit variance along specified dimension.

    Parameters
    ----------
    xx : torch.Tensor
        Input tensor
    dim : int, optional
        Dimension along which to standardize (preferred)
    axis : int, optional
        Alternative to dim for numpy compatibility
    device : str
        Device to use for computation

    Returns
    -------
    torch.Tensor
        Z-scored tensor
    """
    return (x - x.mean(dim=dim, keepdim=True)) / x.std(dim=dim, keepdim=True)


@torch_fn
def to_nanz(x, axis=-1, dim=None, device="cuda"):
    """Standardizes tensor handling NaN values along specified dimension.

    Parameters
    ----------
    xx : torch.Tensor
        Input tensor
    dim : int, optional
        Dimension along which to standardize (preferred)
    axis : int, optional
        Alternative to dim for numpy compatibility
    device : str
        Device to use for computation

    Returns
    -------
    torch.Tensor
        Z-scored tensor with NaN handling
    """
    nan_mean = torch.nanmean(x, dim=dim, keepdim=True)
    nan_std = nanstd(x, dim=dim, keepdim=True)
    return (x - nan_mean) / nan_std


@torch_fn
def to_01(x, axis=-1, dim=None, device="cuda"):
    """Min-max scales tensor to [0, 1] range along specified dimension.

    Parameters
    ----------
    xx : torch.Tensor
        Input tensor
    dim : int, optional
        Dimension along which to scale (preferred)
    axis : int, optional
        Alternative to dim for numpy compatibility
    device : str
        Device to use for computation

    Returns
    -------
    torch.Tensor
        Min-max scaled tensor
    """
    # Use dim if provided, otherwise use axis
    dimension = dim if dim is not None else axis
    
    if dimension is None:
        # Scale entire tensor
        x_min = x.min()
        x_max = x.max()
    else:
        # Scale along specified dimension
        x_min = x.min(dim=dimension, keepdim=True)[0]
        x_max = x.max(dim=dimension, keepdim=True)[0]
    
    # Avoid division by zero
    return (x - x_min) / (x_max - x_min + 1e-8)


@torch_fn
def to_nan01(x, axis=-1, dim=None, device="cuda"):
    """Min-max scales tensor handling NaN values along specified dimension.

    Parameters
    ----------
    xx : torch.Tensor
        Input tensor
    dim : int, optional
        Dimension along which to scale (preferred)
    axis : int, optional
        Alternative to dim for numpy compatibility
    device : str
        Device to use for computation

    Returns
    -------
    torch.Tensor
        Min-max scaled tensor with NaN handling
    """
    # Use dim if provided, otherwise use axis
    dimension = dim if dim is not None else axis
    
    if dimension is None:
        # Scale entire tensor
        x_min = torch.nanmin(x)
        x_max = torch.nanmax(x)
    else:
        # Scale along specified dimension
        x_min = torch.nanmin(x, dim=dimension, keepdim=True)[0]
        x_max = torch.nanmax(x, dim=dimension, keepdim=True)[0]
    
    # Avoid division by zero
    return (x - x_min) / (x_max - x_min + 1e-8)


@torch_fn
def unbias(x, axis=-1, dim=None, fn="mean", device="cuda"):
    """Removes bias from tensor using specified method along dimension.

    Parameters
    ----------
    xx : torch.Tensor
        Input tensor
    dim : int, optional
        Dimension along which to unbias (preferred)
    axis : int, optional
        Alternative to dim for numpy compatibility
    fn : str
        Method to use for unbiasing ('mean' or 'min')
    device : str
        Device to use for computation

    Returns
    -------
    torch.Tensor
        Unbiased tensor
    """
    if fn == "mean":
        return x - x.mean(dim=dim, keepdims=True)
    if fn == "min":
        return x - x.min(dim=dim, keepdims=True)[0]
    raise ValueError(f"Unsupported unbiasing method: {fn}")


@torch_fn
def clip_perc(x, lower_perc=2.5, upper_perc=97.5, low=None, high=None, axis=-1, dim=None, device="cuda"):
    """Clips tensor values between specified percentiles along dimension.

    Parameters
    ----------
    x : torch.Tensor
        Input tensor
    lower_perc : float
        Lower percentile (0-100)
    upper_perc : float
        Upper percentile (0-100)
    low : float, optional
        Alternative name for lower_perc
    high : float, optional
        Alternative name for upper_perc
    dim : int
        Dimension along which to compute percentiles (preferred)
    axis : int
        Alternative to dim for numpy compatibility
    device : str
        Device to use for computation

    Returns
    -------
    torch.Tensor
        Clipped tensor
    """
    # Handle alternative parameter names
    if low is not None:
        lower_perc = low
    if high is not None:
        upper_perc = high
        
    # Use dim if provided, otherwise use axis
    dimension = dim if dim is not None else axis
    
    lower = torch.quantile(x, lower_perc / 100, dim=dimension, keepdim=True)
    upper = torch.quantile(x, upper_perc / 100, dim=dimension, keepdim=True)
    return torch.clamp(x, min=lower, max=upper)


# EOF
