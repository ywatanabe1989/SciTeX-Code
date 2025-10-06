#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-01 21:00:00 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/stats/effect_sizes/_cliffs_delta.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
  - Compute Cliff's delta non-parametric effect size
  - Robust to outliers and non-normal distributions
  - Provide interpretation guidelines
  - Related to Mann-Whitney U statistic

Dependencies:
  - packages: numpy, pandas

IO:
  - input: Two samples (arrays or Series)
  - output: Effect size value (float, ranges from -1 to 1)
"""

"""Imports"""
import argparse
from typing import Union

import numpy as np
import pandas as pd
import scitex as stx
from scitex.logging import getLogger

logger = getLogger(__name__)

"""Functions"""


def cliffs_delta(
    x: Union[np.ndarray, pd.Series],
    y: Union[np.ndarray, pd.Series]
) -> float:
    """
    Compute Cliff's delta non-parametric effect size.

    Parameters
    ----------
    x : array or Series
        First sample
    y : array or Series
        Second sample

    Returns
    -------
    float
        Cliff's delta value (ranges from -1 to 1)

    Notes
    -----
    Cliff's delta is a non-parametric effect size measure that quantifies
    the degree of dominance of one distribution over another.

    It is calculated as:

    .. math::
        \\delta = \\frac{\\#(x_i > y_j) - \\#(x_i < y_j)}{n_x \\cdot n_y}

    Where:
    - #(x_i > y_j) is the number of times values in x are greater than values in y
    - #(x_i < y_j) is the number of times values in x are less than values in y

    Interpretation:
    - |δ| < 0.147: negligible
    - |δ| < 0.33:  small
    - |δ| < 0.474: medium
    - |δ| ≥ 0.474: large

    Advantages:
    - Non-parametric (no assumptions about distributions)
    - Robust to outliers
    - Easy to interpret (probability-based)
    - Related to Mann-Whitney U statistic

    The relation to Mann-Whitney U is:

    .. math::
        \\delta = 2 \\cdot \\frac{U}{n_x \\cdot n_y} - 1

    References
    ----------
    .. [1] Cliff, N. (1993). "Dominance statistics: Ordinal analyses to answer
           ordinal questions". Psychological Bulletin, 114(3), 494-509.
    .. [2] Romano, J., Kromrey, J. D., Coraggio, J., & Skowronek, J. (2006).
           "Appropriate statistics for ordinal level data: Should we really be
           using t-test and Cohen's d for evaluating group differences on the
           NSSE and other surveys?" Florida Association of Institutional Research.

    Examples
    --------
    >>> x = np.array([1, 2, 3, 4, 5])
    >>> y = np.array([2, 3, 4, 5, 6])
    >>> cliffs_delta(x, y)
    -0.6

    >>> # No difference
    >>> x = np.array([1, 2, 3, 4, 5])
    >>> y = np.array([1, 2, 3, 4, 5])
    >>> cliffs_delta(x, y)
    0.0

    >>> # Complete dominance
    >>> x = np.array([6, 7, 8, 9, 10])
    >>> y = np.array([1, 2, 3, 4, 5])
    >>> cliffs_delta(x, y)
    1.0
    """
    # Convert to numpy arrays
    x = np.asarray(x)
    y = np.asarray(y)

    # Remove NaN values
    x = x[~np.isnan(x)]
    y = y[~np.isnan(y)]

    nx = len(x)
    ny = len(y)

    # Count comparisons
    # Vectorized computation: create all pairwise comparisons
    # x[:, None] creates column vector, y creates row vector
    # Broadcasting creates matrix of all pairwise comparisons
    more = np.sum(x[:, None] > y)
    less = np.sum(x[:, None] < y)

    # Compute Cliff's delta
    delta = (more - less) / (nx * ny)

    return float(delta)


def interpret_cliffs_delta(delta: float) -> str:
    """
    Interpret Cliff's delta effect size.

    Parameters
    ----------
    delta : float
        Cliff's delta value

    Returns
    -------
    str
        Interpretation string

    Examples
    --------
    >>> interpret_cliffs_delta(0.1)
    'negligible'
    >>> interpret_cliffs_delta(0.25)
    'small'
    >>> interpret_cliffs_delta(0.4)
    'medium'
    >>> interpret_cliffs_delta(0.6)
    'large'
    """
    delta_abs = abs(delta)

    if delta_abs < 0.147:
        return 'negligible'
    elif delta_abs < 0.33:
        return 'small'
    elif delta_abs < 0.474:
        return 'medium'
    else:
        return 'large'


"""Main function"""


def main(args):
    """Demonstrate Cliff's delta computation."""
    logger.info("Demonstrating Cliff's delta effect size")

    # Set random seed
    np.random.seed(42)

    # Example 1: Basic usage
    logger.info("\n=== Example 1: Basic usage ===")

    x = np.array([1, 2, 3, 4, 5, 6, 7, 8])
    y = np.array([3, 4, 5, 6, 7, 8, 9, 10])

    delta = cliffs_delta(x, y)
    interpretation = interpret_cliffs_delta(delta)

    logger.info(f"Cliff's delta: {delta:.3f} ({interpretation})")
    logger.info(f"{abs(delta):.1%} dominance of one group over the other")

    # Example 2: Robustness to outliers
    logger.info("\n=== Example 2: Robustness to outliers ===")

    x_normal = np.array([1, 2, 3, 4, 5])
    y_normal = np.array([3, 4, 5, 6, 7])
    x_outlier = np.array([1, 2, 3, 4, 100])  # Extreme outlier
    y_outlier = np.array([3, 4, 5, 6, 7])

    delta_normal = cliffs_delta(x_normal, y_normal)
    delta_outlier = cliffs_delta(x_outlier, y_outlier)

    from ._cohens_d import cohens_d
    d_normal = cohens_d(x_normal, y_normal)
    d_outlier = cohens_d(x_outlier, y_outlier)

    logger.info(f"Without outlier: Cliff's δ = {delta_normal:.3f}, Cohen's d = {d_normal:.3f}")
    logger.info(f"With outlier:    Cliff's δ = {delta_outlier:.3f}, Cohen's d = {d_outlier:.3f}")
    logger.info("Cliff's delta is stable, Cohen's d is inflated by outlier")

    # Example 3: Different effect sizes
    logger.info("\n=== Example 3: Different effect sizes ===")

    control = np.random.normal(0, 1, 50)

    for shift in [0.0, 0.3, 0.6, 1.0]:
        treatment = np.random.normal(shift, 1, 50)
        delta = cliffs_delta(control, treatment)
        interpretation = interpret_cliffs_delta(delta)

        logger.info(
            f"Shift = {shift:.1f}: δ = {delta:.3f} ({interpretation})"
        )

    # Visualization
    logger.info("\n=== Creating visualization ===")

    fig, axes = stx.plt.subplots(1, 2, figsize=(12, 5))

    # Plot 1: Distribution comparison
    ax = axes[0]
    x_demo = np.random.exponential(2, 200)
    y_demo = np.random.exponential(3, 200)

    ax.hist(x_demo, bins=30, alpha=0.5, label='Group X', density=True)
    ax.hist(y_demo, bins=30, alpha=0.5, label='Group Y', density=True)

    delta_demo = cliffs_delta(x_demo, y_demo)
    ax.set_xlabel('Value')
    ax.set_ylabel('Density')
    ax.set_title(f"Distributions (Cliff's δ = {delta_demo:.2f})")
    ax.legend()

    # Plot 2: Effect size interpretation
    ax = axes[1]
    delta_values = np.linspace(-1, 1, 100)
    interpretations = [interpret_cliffs_delta(d) for d in delta_values]

    color_map = {'negligible': 'lightgray', 'small': 'yellow',
                 'medium': 'orange', 'large': 'red'}
    colors = [color_map[i] for i in interpretations]

    ax.scatter(delta_values, [0] * len(delta_values), c=colors, s=50, alpha=0.7)
    ax.set_xlabel("Cliff's δ")
    ax.set_yticks([])
    ax.set_title('Effect Size Interpretation')
    ax.axvline(0, color='black', linestyle='-', alpha=0.3)
    ax.axvline(0.147, color='black', linestyle='--', alpha=0.3)
    ax.axvline(0.33, color='black', linestyle='--', alpha=0.3)
    ax.axvline(0.474, color='black', linestyle='--', alpha=0.3)
    ax.axvline(-0.147, color='black', linestyle='--', alpha=0.3)
    ax.axvline(-0.33, color='black', linestyle='--', alpha=0.3)
    ax.axvline(-0.474, color='black', linestyle='--', alpha=0.3)

    stx.plt.tight_layout()
    stx.io.save(fig, './cliffs_delta_demo.jpg')
    logger.info("Visualization saved")

    return 0


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Demonstrate Cliff's delta effect size calculation"
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    return parser.parse_args()


def run_main():
    """Initialize SciTeX framework and run main."""
    global CONFIG, sys, plt, rng

    import sys
    import matplotlib.pyplot as plt

    args = parse_args()

    CONFIG, sys.stdout, sys.stderr, plt, CC, rng = stx.session.start(
        sys,
        plt,
        args=args,
        file=__file__,
        verbose=args.verbose,
        agg=True,
    )

    exit_status = main(args)

    stx.session.close(
        CONFIG,
        verbose=args.verbose,
        exit_status=exit_status,
    )


if __name__ == '__main__':
    run_main()

# EOF
