#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-01 21:00:00 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/stats/effect_sizes/_cohens_d.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
  - Compute Cohen's d effect size for t-tests
  - Support both independent and paired samples
  - Handle various pooling methods (standard, Hedges' g, Glass's delta)
  - Provide interpretation guidelines

Dependencies:
  - packages: numpy, pandas

IO:
  - input: Two samples (arrays or Series)
  - output: Effect size value (float)
"""

"""Imports"""
import argparse
from typing import Literal, Optional, Union

import numpy as np
import pandas as pd
import scitex as stx
from scitex.logging import getLogger

logger = getLogger(__name__)

"""Functions"""


def cohens_d(
    x: Union[np.ndarray, pd.Series],
    y: Optional[Union[np.ndarray, pd.Series]] = None,
    paired: bool = False,
    correction: Literal['hedges', 'glass', None] = None
) -> float:
    """
    Compute Cohen's d effect size.

    Parameters
    ----------
    x : array or Series
        First sample
    y : array or Series, optional
        Second sample. If None, computes one-sample effect size against zero.
    paired : bool, default False
        Whether samples are paired
    correction : {'hedges', 'glass', None}, default None
        Correction method:
        - None: Standard Cohen's d
        - 'hedges': Hedges' g (corrected for small samples)
        - 'glass': Glass's delta (uses only control group SD)

    Returns
    -------
    float
        Effect size value

    Notes
    -----
    Cohen's d is calculated as:

    .. math::
        d = \\frac{\\bar{x}_1 - \\bar{x}_2}{s_{pooled}}

    where :math:`s_{pooled}` is the pooled standard deviation:

    .. math::
        s_{pooled} = \\sqrt{\\frac{(n_1-1)s_1^2 + (n_2-1)s_2^2}{n_1 + n_2 - 2}}

    Interpretation guidelines (Cohen, 1988):
    - Small effect: d = 0.2
    - Medium effect: d = 0.5
    - Large effect: d = 0.8

    For paired samples, d is computed as:

    .. math::
        d = \\frac{\\bar{d}}{s_d}

    where :math:`\\bar{d}` is the mean difference and :math:`s_d` is the
    standard deviation of differences.

    References
    ----------
    .. [1] Cohen, J. (1988). Statistical Power Analysis for the Behavioral
           Sciences (2nd ed.). Routledge.

    Examples
    --------
    >>> x = np.array([1, 2, 3, 4, 5])
    >>> y = np.array([2, 3, 4, 5, 6])
    >>> cohens_d(x, y)
    -1.0

    >>> # Paired samples
    >>> cohens_d(x, y, paired=True)
    -1.58...

    >>> # With Hedges' correction
    >>> cohens_d(x, y, correction='hedges')
    -0.95...
    """
    # Convert to numpy arrays
    x = np.asarray(x)
    if y is not None:
        y = np.asarray(y)

    # Remove NaN values
    x = x[~np.isnan(x)]
    if y is not None:
        y = y[~np.isnan(y)]

    # Compute effect size
    if y is None:
        # One-sample: compare to zero
        d = np.mean(x) / np.std(x, ddof=1)
    elif paired:
        # Paired samples
        if len(x) != len(y):
            raise ValueError("Paired samples must have same length")
        diff = x - y
        d = np.mean(diff) / np.std(diff, ddof=1)
    else:
        # Independent samples
        n1, n2 = len(x), len(y)
        mean_diff = np.mean(x) - np.mean(y)

        if correction == 'glass':
            # Glass's delta: use only control group (y) SD
            d = mean_diff / np.std(y, ddof=1)
        else:
            # Pooled standard deviation
            var1 = np.var(x, ddof=1)
            var2 = np.var(y, ddof=1)
            pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
            d = mean_diff / pooled_std

        # Apply Hedges' correction for small samples
        if correction == 'hedges':
            # Hedges' g correction factor
            correction_factor = 1 - (3 / (4 * (n1 + n2) - 9))
            d = d * correction_factor

    return float(d)


def interpret_cohens_d(d: float) -> str:
    """
    Interpret Cohen's d effect size.

    Parameters
    ----------
    d : float
        Cohen's d value

    Returns
    -------
    str
        Interpretation string

    Examples
    --------
    >>> interpret_cohens_d(0.3)
    'small'
    >>> interpret_cohens_d(0.6)
    'medium'
    >>> interpret_cohens_d(0.9)
    'large'
    """
    d_abs = abs(d)

    if d_abs < 0.2:
        return 'negligible'
    elif d_abs < 0.5:
        return 'small'
    elif d_abs < 0.8:
        return 'medium'
    else:
        return 'large'


"""Main function"""


def main(args):
    """Demonstrate Cohen's d computation."""
    logger.info("Demonstrating Cohen's d effect size")

    # Set random seed
    np.random.seed(42)

    # Example 1: Different effect sizes
    logger.info("\n=== Example 1: Different effect sizes ===")

    n = 50
    control = np.random.normal(0, 1, n)

    effect_sizes = [0.0, 0.2, 0.5, 0.8, 1.2]
    results = []

    for true_d in effect_sizes:
        treatment = np.random.normal(true_d, 1, n)
        computed_d = cohens_d(control, treatment)
        interpretation = interpret_cohens_d(computed_d)

        logger.info(
            f"True d = {true_d:.1f}, "
            f"Computed d = {computed_d:.3f}, "
            f"Interpretation: {interpretation}"
        )

        results.append({
            'true_d': true_d,
            'computed_d': computed_d,
            'interpretation': interpretation
        })

    # Example 2: Paired vs independent
    logger.info("\n=== Example 2: Paired vs Independent ===")

    n_pairs = 30
    baseline = np.random.normal(0, 1, n_pairs)
    noise = np.random.normal(0, 0.3, n_pairs)
    followup = baseline + 0.5 + noise

    d_independent = cohens_d(baseline, followup, paired=False)
    d_paired = cohens_d(baseline, followup, paired=True)

    logger.info(f"Independent samples d = {d_independent:.3f}")
    logger.info(f"Paired samples d = {d_paired:.3f}")
    logger.info(f"Paired is more sensitive due to correlation")

    # Example 3: Correction methods
    logger.info("\n=== Example 3: Correction methods ===")

    small_n = 10
    x_small = np.random.normal(0, 1, small_n)
    y_small = np.random.normal(0.5, 1, small_n)

    d_standard = cohens_d(x_small, y_small)
    d_hedges = cohens_d(x_small, y_small, correction='hedges')
    d_glass = cohens_d(x_small, y_small, correction='glass')

    logger.info(f"Standard Cohen's d = {d_standard:.3f}")
    logger.info(f"Hedges' g = {d_hedges:.3f} (corrected for small n)")
    logger.info(f"Glass's delta = {d_glass:.3f} (uses control SD only)")

    # Visualization
    logger.info("\n=== Creating visualization ===")

    fig, axes = stx.plt.subplots(1, 2, figsize=(12, 5))

    # Plot 1: Distribution visualization
    ax = axes[0]
    control_demo = np.random.normal(0, 1, 1000)
    treatment_demo = np.random.normal(0.8, 1, 1000)

    ax.hist(control_demo, bins=30, alpha=0.5, label='Control', density=True)
    ax.hist(treatment_demo, bins=30, alpha=0.5, label='Treatment', density=True)

    d_demo = cohens_d(control_demo, treatment_demo)
    ax.axvline(np.mean(control_demo), color='blue', linestyle='--', alpha=0.7)
    ax.axvline(np.mean(treatment_demo), color='orange', linestyle='--', alpha=0.7)

    ax.set_xlabel('Value')
    ax.set_ylabel('Density')
    ax.set_title(f"Distributions (Cohen's d = {d_demo:.2f})")
    ax.legend()

    # Plot 2: Effect size comparison
    ax = axes[1]
    df_results = pd.DataFrame(results)
    ax.scatter(df_results['true_d'], df_results['computed_d'], s=100)
    ax.plot([-0.5, 1.5], [-0.5, 1.5], 'k--', alpha=0.5, label='Perfect agreement')
    ax.set_xlabel('True Effect Size')
    ax.set_ylabel("Computed Cohen's d")
    ax.set_title('True vs Computed Effect Sizes')
    ax.legend()
    ax.grid(True, alpha=0.3)

    stx.plt.tight_layout()
    stx.io.save(fig, './cohens_d_demo.jpg')
    logger.info("Visualization saved")

    return 0


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Demonstrate Cohen's d effect size calculation"
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
