#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-01 21:00:00 (ywatanabe)"
# File: ./src/scitex/stats/effect_sizes/_prob_superiority.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = "./src/scitex/stats/effect_sizes/_prob_superiority.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
  - Compute probability of superiority P(X > Y)
  - Common language effect size
  - Related to Brunner-Munzel test and Cliff's delta
  - Provide interpretation guidelines

Dependencies:
  - packages: numpy, pandas

IO:
  - input: Two samples (arrays or Series)
  - output: Probability value (float, ranges from 0 to 1)
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


def prob_superiority(
    x: Union[np.ndarray, pd.Series],
    y: Union[np.ndarray, pd.Series]
) -> float:
    """
    Compute probability of superiority P(X > Y).

    Also known as the common language effect size or probabilistic index.

    Parameters
    ----------
    x : array or Series
        First sample
    y : array or Series
        Second sample

    Returns
    -------
    float
        Probability that a random value from X is greater than a random value from Y
        (ranges from 0 to 1)

    Notes
    -----
    The probability of superiority is defined as:

    .. math::
        P(X > Y) = \\frac{\\#(x_i > y_j)}{n_x \\cdot n_y}

    This is the probabilistic interpretation of effect size and is directly
    related to the Brunner-Munzel statistic and Cliff's delta:

    .. math::
        P(X > Y) = \\frac{1 + \\delta}{2}

    Where δ is Cliff's delta.

    Interpretation:
    - P(X > Y) = 0.50: No effect (chance level)
    - P(X > Y) = 0.56: Small effect (McGraw & Wong, 1992)
    - P(X > Y) = 0.64: Medium effect
    - P(X > Y) = 0.71: Large effect

    Advantages:
    - Intuitive probabilistic interpretation
    - Non-parametric (distribution-free)
    - Directly comparable across studies
    - Used in Brunner-Munzel test

    This is also called:
    - Common Language Effect Size (CLES)
    - Area Under the Curve (AUC) in ROC analysis
    - Mann-Whitney U / (nx * ny)

    References
    ----------
    .. [1] McGraw, K. O., & Wong, S. P. (1992). "A common language effect size
           statistic". Psychological Bulletin, 111(2), 361-365.
    .. [2] Brunner, E., & Munzel, U. (2000). "The nonparametric Behrens-Fisher
           problem: Asymptotic theory and a small-sample approximation".
           Biometrical Journal, 42(1), 17-25.

    Examples
    --------
    >>> x = np.array([1, 2, 3, 4, 5])
    >>> y = np.array([2, 3, 4, 5, 6])
    >>> prob_superiority(x, y)
    0.2

    >>> # 20% chance a random X value exceeds a random Y value

    >>> # No difference (chance level)
    >>> x = np.array([1, 2, 3, 4, 5])
    >>> y = np.array([1, 2, 3, 4, 5])
    >>> prob_superiority(x, y)
    0.5

    >>> # Complete dominance
    >>> x = np.array([6, 7, 8, 9, 10])
    >>> y = np.array([1, 2, 3, 4, 5])
    >>> prob_superiority(x, y)
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

    # Count how many times x > y
    more = np.sum(x[:, None] > y)

    # Compute probability
    prob = more / (nx * ny)

    return float(prob)


def interpret_prob_superiority(prob: float) -> str:
    """
    Interpret probability of superiority effect size.

    Parameters
    ----------
    prob : float
        Probability of superiority P(X > Y)

    Returns
    -------
    str
        Interpretation string

    Examples
    --------
    >>> interpret_prob_superiority(0.51)
    'negligible'
    >>> interpret_prob_superiority(0.60)
    'small'
    >>> interpret_prob_superiority(0.68)
    'medium'
    >>> interpret_prob_superiority(0.75)
    'large'
    """
    # Convert to distance from 0.5 (chance)
    distance = abs(prob - 0.5)

    if distance < 0.06:
        return 'negligible'
    elif distance < 0.14:
        return 'small'
    elif distance < 0.21:
        return 'medium'
    else:
        return 'large'


"""Main function"""


def main(args):
    """Demonstrate probability of superiority computation."""
    logger.info("Demonstrating probability of superiority P(X > Y)")

    # Set random seed
    np.random.seed(42)

    # Example 1: Relationship with Cliff's delta
    logger.info("\n=== Example 1: Relationship with Cliff's delta ===")

    x = np.array([1, 2, 3, 4, 5, 6, 7, 8])
    y = np.array([3, 4, 5, 6, 7, 8, 9, 10])

    from ._cliffs_delta import cliffs_delta
    prob = prob_superiority(x, y)
    delta = cliffs_delta(x, y)

    logger.info(f"P(X > Y) = {prob:.3f} ({interpret_prob_superiority(prob)})")
    logger.info(f"Cliff's delta = {delta:.3f}")
    logger.info(f"Relationship: P(X>Y) = (1 + δ) / 2 = {(1 + delta) / 2:.3f}")

    # Example 2: Different effect sizes
    logger.info("\n=== Example 2: Different effect sizes ===")

    control = np.random.normal(0, 1, 50)

    for shift in [0.0, 0.3, 0.6, 1.0]:
        treatment = np.random.normal(shift, 1, 50)
        prob = prob_superiority(treatment, control)
        interpretation = interpret_prob_superiority(prob)

        logger.info(
            f"Shift = {shift:.1f}: P(Treatment > Control) = {prob:.3f} ({interpretation})"
        )

    # Visualization
    logger.info("\n=== Creating visualization ===")

    fig, ax = stx.plt.subplots(figsize=(10, 6))

    # Generate data for visualization
    shifts = np.linspace(0, 2, 20)
    probs = []

    for shift in shifts:
        treatment = np.random.normal(shift, 1, 100)
        control = np.random.normal(0, 1, 100)
        probs.append(prob_superiority(treatment, control))

    ax.plot(shifts, probs, 'o-', linewidth=2, markersize=8)
    ax.axhline(0.5, color='red', linestyle='--', alpha=0.5, label='Chance level')
    ax.axhline(0.56, color='orange', linestyle='--', alpha=0.5, label='Small effect')
    ax.axhline(0.64, color='yellow', linestyle='--', alpha=0.5, label='Medium effect')
    ax.axhline(0.71, color='green', linestyle='--', alpha=0.5, label='Large effect')

    ax.set_xlabel('Mean Shift (Cohen\'s d)')
    ax.set_ylabel('P(Treatment > Control)')
    ax.set_title('Probability of Superiority vs Effect Size')
    ax.legend()
    ax.grid(True, alpha=0.3)

    stx.plt.tight_layout()
    stx.io.save(fig, './prob_superiority_demo.jpg')
    logger.info("Visualization saved")

    return 0


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Demonstrate probability of superiority calculation"
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
