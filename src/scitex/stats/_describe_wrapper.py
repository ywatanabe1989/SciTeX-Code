#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-05-30 22:00:00 (Claude)"
# File: ./scitex_repo/src/scitex/stats/_describe_wrapper.py

"""
Wrapper for describe function to provide a more user-friendly interface.
"""

import numpy as np
import torch
from .desc._describe import describe as _describe_internal


def describe(data, **kwargs):
    """
    Compute descriptive statistics for the input data.

    Parameters
    ----------
    data : array-like
        Input data
    **kwargs : dict
        Additional arguments passed to the internal describe function

    Returns
    -------
    dict
        Dictionary containing descriptive statistics
    """
    # Convert to numpy array if needed
    if not isinstance(data, (np.ndarray, torch.Tensor)):
        data = np.array(data)

    # Get the internal result
    try:
        stats_tensor, stat_names = _describe_internal(data, **kwargs)

        # Convert tensor to numpy if needed
        if isinstance(stats_tensor, torch.Tensor):
            stats_values = stats_tensor.cpu().numpy()
        else:
            stats_values = stats_tensor

        # If stats_values is multidimensional, flatten or take mean
        if stats_values.ndim > 1:
            # Take the first element if batch dimension exists
            stats_values = stats_values.reshape(-1)[: len(stat_names)]

        # Create dictionary mapping stat names to values
        result = {}
        for i, name in enumerate(stat_names):
            if i < len(stats_values):
                result[name] = float(stats_values[i])

        # Ensure expected keys exist with reasonable defaults
        if "mean" not in result and "nanmean" in result:
            result["mean"] = result["nanmean"]
        if "std" not in result and "nanstd" in result:
            result["std"] = result["nanstd"]
        if "min" not in result and "nanmin" in result:
            result["min"] = result["nanmin"]
        if "max" not in result and "nanmax" in result:
            result["max"] = result["nanmax"]

        # If still missing basic stats, calculate them
        if "mean" not in result:
            result["mean"] = float(np.nanmean(data))
        if "std" not in result:
            result["std"] = float(np.nanstd(data))
        if "min" not in result:
            result["min"] = float(np.nanmin(data))
        if "max" not in result:
            result["max"] = float(np.nanmax(data))

        return result

    except Exception as e:
        # Fallback to simple numpy calculations
        return {
            "mean": float(np.nanmean(data)),
            "std": float(np.nanstd(data)),
            "min": float(np.nanmin(data)),
            "max": float(np.nanmax(data)),
            "count": int(np.sum(~np.isnan(data))) if hasattr(data, "__len__") else 1,
        }


# Export the wrapper as the main describe function
__all__ = ["describe"]
