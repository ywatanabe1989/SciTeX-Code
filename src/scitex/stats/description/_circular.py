#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-20 17:17:21 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/stats/desc/_circular.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/stats/desc/_circular.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from typing import List, Optional, Tuple, Union

"""
Functionalities:
- Computes circular mean of angles with histogram values
- Calculates circular concentration (mean resultant length)
- Computes circular skewness for asymmetry measurement
- Calculates circular kurtosis for tail behavior analysis
- Warns if input appears to be in degrees instead of radians
- Demonstrates circular statistics with synthetic data
- Saves visualization and statistical results

Dependencies:
- packages:
  - torch
  - numpy
  - scitex
  - matplotlib

IO:
- input-files:
  - angles in radians as torch.Tensor
  - histogram values as torch.Tensor
- output-files:
  - ./circular_stats_demo.jpg
  - ./circular_statistics.pkl
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
# @batch_fn
@torch_fn
def describe_circular(
    angles: torch.Tensor,
    values: torch.Tensor,
    axis: int = -1,
    dim: Optional[Union[int, Tuple[int, ...]]] = None,
    keepdims: bool = False,
    funcs: Union[List[str], str] = [
        "circular_mean",
        "circular_concentration",
        "circular_skewness",
        "circular_kurtosis",
    ],
    device: Optional[torch.device] = None,
    batch_size: int = -1,
) -> Tuple[torch.Tensor, List[str]]:
    """Computes various circular descriptive statistics.

    Parameters
    ----------
    angles : torch.Tensor
        Input angles in radians with batch dimension as first axis
    values : torch.Tensor
        Histogram values for each angle (must match angles shape)
    axis : int, default=-1
        Deprecated. Use dim instead
    dim : int or tuple of ints, optional
        Dimension(s) along which to compute statistics
    keepdims : bool, default=False
        Whether to keep reduced dimensions
    funcs : list of str or "all"
        Circular statistical functions to compute
    device : torch.device, optional
        Device to use for computation
    batch_size : int, default=-1
        Batch size for processing (handled by decorator)

    Returns
    -------
    Tuple[torch.Tensor, List[str]]
        Computed circular statistics and their names
    """
    dim = axis if dim is None else dim
    dim = (dim,) if isinstance(dim, int) else tuple(dim)

    func_names = funcs
    func_candidates = {
        "circular_mean": circular_mean,
        "circular_concentration": circular_concentration,
        "circular_skewness": circular_skewness,
        "circular_kurtosis": circular_kurtosis,
    }

    if funcs == "all":
        _funcs = list(func_candidates.values())
        func_names = list(func_candidates.keys())
    else:
        _funcs = [func_candidates[ff] for ff in func_names]

    calculated = [
        ff(angles, values, dim=dim, keepdims=keepdims) for ff in _funcs
    ]

    return torch.stack(calculated, dim=-1), func_names


def _ensure_more_than_2d(data: torch.Tensor) -> None:
    assert (
        data.ndim >= 2
    ), f"Input tensor must be more than 2 dimensional with batch dimension as first axis, got {data.ndim}"


def _check_angle_units(angles: torch.Tensor) -> None:
    """Check if angles might be in degrees and warn user.

    Parameters
    ----------
    angles : torch.Tensor
        Input angles to check
    """
    max_val = torch.max(torch.abs(angles)).item()
    if max_val > 2 * torch.pi:
        logger.warning(
            f"Maximum angle value is {max_val:.2f} (>2π). "
            f"Consider using torch.deg2rad() or angle wrapping."
        )


# @batch_fn
@torch_fn
def circular_mean(
    angles: torch.Tensor,
    values: torch.Tensor,
    axis: int = -1,
    dim: int = None,
    batch_size: int = None,
    keepdims: bool = False,
) -> torch.Tensor:
    """Compute circular mean of angles weighted by histogram values.

    Parameters
    ----------
    angles : torch.Tensor
        Input angles in radians with batch dimension as first axis
    values : torch.Tensor
        Histogram values for each angle (must match angles shape)
    axis : int, default=-1
        Axis along which to compute mean (deprecated, use dim)
    dim : int, optional
        Dimension along which to compute mean
    batch_size : int, optional
        Batch size for processing (handled by decorator)
    keepdims : bool, default=False
        Whether to keep reduced dimensions

    Returns
    -------
    torch.Tensor
        Circular mean in range [0, 2π]
    """

    _ensure_more_than_2d(angles)
    _check_angle_units(angles)
    assert (
        angles.shape == values.shape
    ), f"angles shape {angles.shape} must match values shape {values.shape}"

    dim = axis if dim is None else dim
    cos_angles = torch.cos(angles)
    sin_angles = torch.sin(angles)

    cos_component = torch.sum(values * cos_angles, dim=dim, keepdim=True)
    sin_component = torch.sum(values * sin_angles, dim=dim, keepdim=True)
    value_sum = torch.sum(values, dim=dim, keepdim=True)
    cos_component = cos_component / value_sum
    sin_component = sin_component / value_sum

    mean_angle = torch.atan2(sin_component, cos_component)
    mean_angle = torch.where(
        mean_angle < 0, mean_angle + 2 * np.pi, mean_angle
    )

    return mean_angle if keepdims else mean_angle.squeeze(dim)


# @batch_fn
@torch_fn
def circular_concentration(
    angles: torch.Tensor,
    values: torch.Tensor,
    axis: int = -1,
    dim: int = None,
    batch_size: int = None,
    keepdims: bool = False,
) -> torch.Tensor:
    """Compute circular concentration (mean resultant length).

    Parameters
    ----------
    angles : torch.Tensor with batch dimension as first axis
        Input angles in radians
    values : torch.Tensor
        Histogram values for each angle (must match angles shape)
    axis : int, default=-1
        Axis along which to compute concentration (deprecated, use dim)
    dim : int, optional
        Dimension along which to compute concentration
    batch_size : int, optional
        Batch size for processing (handled by decorator)
    keepdims : bool, default=False
        Whether to keep reduced dimensions

    Returns
    -------
    torch.Tensor
        Concentration parameter in range [0, 1]
    """
    _ensure_more_than_2d(angles)
    _check_angle_units(angles)
    assert (
        angles.shape == values.shape
    ), f"angles shape {angles.shape} must match values shape {values.shape}"

    dim = axis if dim is None else dim
    cos_angles = torch.cos(angles)
    sin_angles = torch.sin(angles)

    cos_component = torch.sum(values * cos_angles, dim=dim, keepdim=keepdims)
    sin_component = torch.sum(values * sin_angles, dim=dim, keepdim=keepdims)
    value_sum = torch.sum(values, dim=dim, keepdim=keepdims)
    vector_length = torch.sqrt(cos_component**2 + sin_component**2) / value_sum

    return vector_length


# @batch_fn
@torch_fn
def circular_skewness(
    angles: torch.Tensor,
    values: torch.Tensor,
    axis: int = -1,
    dim: int = None,
    batch_size: int = None,
    keepdims: bool = False,
) -> torch.Tensor:
    """Compute circular skewness.

    Parameters
    ----------
    angles : torch.Tensor with batch dimension as first axis
        Input angles in radians
    values : torch.Tensor
        Histogram values for each angle (must match angles shape)
    axis : int, default=-1
        Axis along which to compute skewness (deprecated, use dim)
    dim : int, optional
        Dimension along which to compute skewness
    batch_size : int, optional
        Batch size for processing (handled by decorator)
    keepdims : bool, default=False
        Whether to keep reduced dimensions

    Returns
    -------
    torch.Tensor
        Circular skewness
    """
    _ensure_more_than_2d(angles)
    _check_angle_units(angles)
    assert (
        angles.shape == values.shape
    ), f"angles shape {angles.shape} must match values shape {values.shape}"

    dim = axis if dim is None else dim
    cos_angles = torch.cos(angles)
    sin_angles = torch.sin(angles)
    cos_2angles = torch.cos(2 * angles)
    sin_2angles = torch.sin(2 * angles)

    value_sum = torch.sum(values, dim=dim, keepdim=True)
    c1 = torch.sum(values * cos_angles, dim=dim, keepdim=True) / value_sum
    s1 = torch.sum(values * sin_angles, dim=dim, keepdim=True) / value_sum
    c2 = torch.sum(values * cos_2angles, dim=dim, keepdim=True) / value_sum
    s2 = torch.sum(values * sin_2angles, dim=dim, keepdim=True) / value_sum

    skewness = (c2 * s1 - s2 * c1) / (1 - (c1**2 + s1**2)) ** (3 / 2)
    return skewness if keepdims else skewness.squeeze(dim)


# @batch_fn
@torch_fn
def circular_kurtosis(
    angles: torch.Tensor,
    values: torch.Tensor,
    axis: int = -1,
    dim: int = None,
    batch_size: int = None,
    keepdims: bool = False,
) -> torch.Tensor:
    """Compute circular kurtosis.

    Parameters
    ----------
    angles : torch.Tensor
        Input angles in radians with batch dimension as first axis
    values : torch.Tensor
        Histogram values for each angle (must match angles shape)
    axis : int, default=-1
        Axis along which to compute kurtosis (deprecated, use dim)
    dim : int, optional
        Dimension along which to compute kurtosis
    batch_size : int, optional
        Batch size for processing (handled by decorator)
    keepdims : bool, default=False
        Whether to keep reduced dimensions

    Returns
    -------
    torch.Tensor
        Circular kurtosis
    """
    _ensure_more_than_2d(angles)
    _check_angle_units(angles)
    assert (
        angles.shape == values.shape
    ), f"angles shape {angles.shape} must match values shape {values.shape}"

    dim = axis if dim is None else dim
    cos_angles = torch.cos(angles)
    sin_angles = torch.sin(angles)
    cos_2angles = torch.cos(2 * angles)
    sin_2angles = torch.sin(2 * angles)

    value_sum = torch.sum(values, dim=dim, keepdim=True)
    c1 = torch.sum(values * cos_angles, dim=dim, keepdim=True) / value_sum
    s1 = torch.sum(values * sin_angles, dim=dim, keepdim=True) / value_sum
    c2 = torch.sum(values * cos_2angles, dim=dim, keepdim=True) / value_sum
    s2 = torch.sum(values * sin_2angles, dim=dim, keepdim=True) / value_sum

    kurtosis = (c2 * c1 + s2 * s1) / (1 - (c1**2 + s1**2)) ** 2
    return kurtosis if keepdims else kurtosis.squeeze(dim)


def main(args) -> int:
    """Demonstrate circular statistics functions with synthetic data."""

    # Generate synthetic circular histogram data
    angles = torch.tensor([0.5, 1.2, 2.1, 3.8, 4.9, 5.7])
    values = torch.tensor([1.0, 2.0, 1.5, 1.0, 3.0, 1.2])

    angles = angles.reshape(1, -1)
    values = values.reshape(1, -1)

    # All at once
    described, methods = describe_circular(angles, values)
    described, methods = described[0], methods
    for i_dd, dd in enumerate(described):
        print(f"{methods[i_dd]}: {dd}")

    # Compute circular statistics
    c_mean = circular_mean(angles, values)
    c_concentration = circular_concentration(angles, values)
    c_skewness = circular_skewness(angles, values)
    c_kurtosis = circular_kurtosis(angles, values)

    # Store results
    ii = 0
    results = {
        "angles": angles[ii],
        "values": values[ii],
        "circular_mean": c_mean[ii],
        "circular_concentration": c_concentration[ii],
        "circular_skewness": c_skewness[ii],
        "circular_kurtosis": c_kurtosis[ii],
    }

    for k, v in results.items():
        if isinstance(v, (np.ndarray, torch.Tensor)):
            print(f"\n{k}, Type: {type(v)}, Shape: {v.shape}, Values: {v}")
        elif isinstance(v, list):
            print(f"\n{k}, Type: {type(v)}, Length: {len(v)}, Values: {v}")
        else:
            print(f"\n{k}, Type: {type(v)}, Values: {v}")

    # Create visualization
    fig, axes = plt.subplots(
        2, 2, figsize=(12, 10), subplot_kw=dict(projection="polar")
    )

    # Plot 1: Histogram visualization
    axes[0, 0].bar(
        results["angles"],
        results["values"],
        width=0.3,
        alpha=0.7,
        color="blue",
    )
    axes[0, 0].axvline(
        c_mean.item(),
        color="red",
        linewidth=2,
        label=f"Mean: {c_mean.item():.2f}",
    )
    axes[0, 0].set_title("Circular Histogram")
    axes[0, 0].legend()

    # Plot 2: Concentration visualization
    theta = torch.linspace(0, 2 * np.pi, 100)
    radius = torch.ones_like(theta) * c_concentration.item()
    axes[0, 1].plot(
        theta,
        radius,
        "g-",
        linewidth=2,
        label=f"Concentration: {c_concentration.item():.3f}",
    )
    axes[0, 1].bar(
        results["angles"],
        results["values"],
        width=0.3,
        alpha=0.5,
        color="blue",
    )
    axes[0, 1].set_title("Concentration Circle")
    axes[0, 1].legend()

    # Plot 3: Mean direction
    axes[1, 0].bar(
        results["angles"],
        results["values"],
        width=0.3,
        alpha=0.7,
        color="blue",
    )
    axes[1, 0].arrow(
        0,
        0,
        np.cos(c_mean.item()) * c_concentration.item(),
        np.sin(c_mean.item()) * c_concentration.item(),
        head_width=0.1,
        head_length=0.1,
        fc="red",
        ec="red",
    )
    axes[1, 0].set_title("Mean Vector")

    # Plot 4: Statistics summary
    axes[1, 1].axis("off")
    stats_text = f"""Circular Statistics:

Mean: {c_mean.item():.3f} rad ({np.degrees(c_mean.item()):.1f}°)
Concentration: {c_concentration.item():.3f}
Skewness: {c_skewness.item():.3f}
Kurtosis: {c_kurtosis.item():.3f}"""

    axes[1, 1].text(
        0.1,
        0.5,
        stats_text,
        transform=axes[1, 1].transAxes,
        fontsize=12,
        verticalalignment="center",
    )
    axes[1, 1].set_title("Statistics Summary")

    plt.tight_layout()
    stx.io.save(fig, "./circular_stats_demo.jpg")

    # Save results
    stx.io.save(results, "./circular_statistics.pkl")

    # Log results
    logger.info(
        f"Circular mean: {c_mean.item():.3f} rad ({np.degrees(c_mean.item()):.1f}°)"
    )
    logger.info(f"Circular concentration: {c_concentration.item():.3f}")
    logger.info(f"Circular skewness: {c_skewness.item():.3f}")
    logger.info(f"Circular kurtosis: {c_kurtosis.item():.3f}")

    return 0


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Demonstrate circular statistics functions for histogram data"
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
