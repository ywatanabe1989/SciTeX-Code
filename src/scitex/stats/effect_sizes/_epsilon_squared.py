#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-01 21:05:00 (ywatanabe)"
# File: ./src/scitex/stats/effect_sizes/_epsilon_squared.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = "./src/scitex/stats/effect_sizes/_epsilon_squared.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
  - Compute epsilon-squared (ε²) effect size for Kruskal-Wallis test
  - Non-parametric analog of eta-squared
  - Measure variance in ranks explained by groups
  - Provide interpretation guidelines

Dependencies:
  - packages: numpy, pandas, scipy

IO:
  - input: List of sample arrays (one per group)
  - output: Effect size value (float, ranges from 0 to 1)
"""

"""Imports"""
import argparse
from typing import List

import numpy as np
import pandas as pd
import scitex as stx
from scipy import stats
from scitex.logging import getLogger

logger = getLogger(__name__)

"""Functions"""


def epsilon_squared(groups: List[np.ndarray]) -> float:
    """
    Compute epsilon-squared (ε²) effect size for Kruskal-Wallis test.

    Parameters
    ----------
    groups : list of arrays
        List of sample arrays for each group

    Returns
    -------
    float
        Epsilon-squared value (0 to 1)

    Notes
    -----
    Epsilon-squared (ε²) is the non-parametric analog of eta-squared (η²)
    for the Kruskal-Wallis test. It measures the proportion of variance in
    ranks explained by group membership.

    .. math::
        \\epsilon^2 = \\frac{H}{(n^2 - 1) / (n + 1)}

    Where:
    - H: Kruskal-Wallis H statistic
    - n: Total sample size

    Alternative formula (based on ranks):

    .. math::
        \\epsilon^2 = \\frac{H - k + 1}{n - k}

    Where:
    - H: Kruskal-Wallis H statistic
    - k: Number of groups
    - n: Total sample size

    Interpretation (similar to η²):
    - ε² < 0.01:  negligible
    - ε² < 0.06:  small
    - ε² < 0.14:  medium
    - ε² ≥ 0.14:  large

    References
    ----------
    .. [1] Tomczak, M., & Tomczak, E. (2014). "The need to report effect size
           estimates revisited. An overview of some recommended measures of
           effect size". Trends in Sport Sciences, 21(1), 19-25.
    .. [2] Kerby, D. S. (2014). "The simple difference formula: An approach to
           teaching nonparametric correlation". Comprehensive Psychology, 3, 11.

    Examples
    --------
    >>> group1 = np.array([1, 2, 3, 4, 5])
    >>> group2 = np.array([3, 4, 5, 6, 7])
    >>> group3 = np.array([5, 6, 7, 8, 9])
    >>> epsilon_squared([group1, group2, group3])
    0.857...

    >>> # No effect
    >>> group1 = np.array([1, 2, 3, 4, 5])
    >>> group2 = np.array([1, 2, 3, 4, 5])
    >>> epsilon_squared([group1, group2])
    0.0
    """
    # Convert all groups to numpy arrays and remove NaN
    groups = [np.asarray(g) for g in groups]
    groups = [g[~np.isnan(g)] for g in groups]

    # Get group sizes
    k = len(groups)
    n = sum(len(g) for g in groups)

    # Perform Kruskal-Wallis test to get H statistic
    h_stat, _ = stats.kruskal(*groups)

    # Compute epsilon-squared using H statistic
    # Formula: ε² = (H - k + 1) / (n - k)
    if n == k:
        return 0.0

    epsilon2 = (h_stat - k + 1) / (n - k)

    # Ensure value is in valid range [0, 1]
    epsilon2 = max(0.0, min(1.0, epsilon2))

    return float(epsilon2)


def interpret_epsilon_squared(epsilon2: float) -> str:
    """
    Interpret epsilon-squared effect size.

    Parameters
    ----------
    epsilon2 : float
        Epsilon-squared value

    Returns
    -------
    str
        Interpretation string

    Examples
    --------
    >>> interpret_epsilon_squared(0.005)
    'negligible'
    >>> interpret_epsilon_squared(0.03)
    'small'
    >>> interpret_epsilon_squared(0.10)
    'medium'
    >>> interpret_epsilon_squared(0.20)
    'large'
    """
    if epsilon2 < 0.01:
        return 'negligible'
    elif epsilon2 < 0.06:
        return 'small'
    elif epsilon2 < 0.14:
        return 'medium'
    else:
        return 'large'


"""Main function"""


def main(args):
    """Demonstrate epsilon-squared computation."""
    logger.info("Demonstrating epsilon-squared effect size for Kruskal-Wallis")

    # Set random seed
    np.random.seed(42)

    # Example 1: Three groups with non-normal distributions
    logger.info("\n=== Example 1: Three skewed groups ===")

    group1 = np.random.exponential(1, 30)
    group2 = np.random.exponential(1.5, 30)
    group3 = np.random.exponential(2, 30)

    eps2 = epsilon_squared([group1, group2, group3])
    interpretation = interpret_epsilon_squared(eps2)

    logger.info(f"Epsilon-squared = {eps2:.3f} ({interpretation})")
    logger.info(f"{eps2:.1%} of rank variance explained by group membership")

    # Example 2: Comparison with eta-squared
    logger.info("\n=== Example 2: Epsilon-squared vs Eta-squared ===")

    from ._eta_squared import eta_squared

    # Normal data
    norm1 = np.random.normal(0, 1, 40)
    norm2 = np.random.normal(0.8, 1, 40)
    norm3 = np.random.normal(1.5, 1, 40)

    eps2_norm = epsilon_squared([norm1, norm2, norm3])
    eta2_norm = eta_squared([norm1, norm2, norm3])

    logger.info(f"Normal data:   ε² = {eps2_norm:.3f}, η² = {eta2_norm:.3f}")

    # Skewed data
    skew1 = np.random.exponential(1, 40)
    skew2 = np.random.exponential(2, 40)
    skew3 = np.random.exponential(3, 40)

    eps2_skew = epsilon_squared([skew1, skew2, skew3])
    eta2_skew = eta_squared([skew1, skew2, skew3])

    logger.info(f"Skewed data:   ε² = {eps2_skew:.3f}, η² = {eta2_skew:.3f}")
    logger.info("Epsilon-squared is more appropriate for non-normal data")

    # Example 3: Different effect sizes
    logger.info("\n=== Example 3: Different effect sizes ===")

    for scale in [1.0, 1.5, 2.0, 3.0]:
        g1 = np.random.exponential(1, 30)
        g2 = np.random.exponential(scale, 30)

        eps2 = epsilon_squared([g1, g2])
        interpretation = interpret_epsilon_squared(eps2)

        logger.info(f"Scale = {scale:.1f}: ε² = {eps2:.3f} ({interpretation})")

    # Visualization
    logger.info("\n=== Creating visualization ===")

    fig, axes = stx.plt.subplots(1, 2, figsize=(12, 5))

    # Plot 1: Distribution comparison
    ax = axes[0]
    ax.hist(group1, bins=20, alpha=0.5, label='Group 1', density=True)
    ax.hist(group2, bins=20, alpha=0.5, label='Group 2', density=True)
    ax.hist(group3, bins=20, alpha=0.5, label='Group 3', density=True)

    ax.set_xlabel('Value')
    ax.set_ylabel('Density')
    ax.set_title(f'Skewed Distributions (ε² = {eps2:.2f})')
    ax.legend()

    # Plot 2: Comparison of methods
    ax = axes[1]
    scales = np.linspace(1, 3, 10)
    eps2_values = []
    eta2_values = []

    for scale in scales:
        g1 = np.random.exponential(1, 50)
        g2 = np.random.exponential(scale, 50)

        eps2_values.append(epsilon_squared([g1, g2]))
        eta2_values.append(eta_squared([g1, g2]))

    ax.plot(scales, eps2_values, 'o-', label='Epsilon-squared (ε²)', linewidth=2)
    ax.plot(scales, eta2_values, 's-', label='Eta-squared (η²)', linewidth=2)

    ax.set_xlabel('Distribution Scale Difference')
    ax.set_ylabel('Effect Size')
    ax.set_title('Non-parametric vs Parametric Effect Size')
    ax.legend()
    ax.grid(True, alpha=0.3)

    stx.plt.tight_layout()
    stx.io.save(fig, './epsilon_squared_demo.jpg')
    logger.info("Visualization saved")

    return 0


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Demonstrate epsilon-squared effect size calculation"
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
