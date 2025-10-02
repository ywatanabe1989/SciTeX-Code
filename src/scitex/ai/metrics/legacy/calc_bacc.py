#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-02 18:43:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/ml/metrics/_calc_bacc.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
  - Calculates balanced accuracy from true and predicted labels
  - Demonstrates calc_balanced_accuracy usage with example data
  - Saves results to _out directory

Dependencies:
  - packages:
    - numpy
    - scitex

IO:
  - output-files:
    - _calc_bacc_out/balanced_accuracy_results.txt
"""

"""Imports"""
import argparse

import numpy as np
import scitex as stx
from scitex import logging
from scitex.ml.metrics.classification import calc_balanced_accuracy

logger = logging.getLogger(__name__)

"""Functions & Classes"""
def main(args):
    """
    Demonstrate balanced accuracy calculation.
    """
    # Example data
    y_true = np.array([0, 1, 0, 1, 0, 1, 1, 0])
    y_pred = np.array([0, 1, 0, 0, 0, 1, 1, 1])
    labels = ["Negative", "Positive"]

    # Calculate balanced accuracy
    result = calc_balanced_accuracy(
        y_true=y_true,
        y_pred=y_pred,
        labels=labels,
        fold=0
    )

    # Log results
    logger.info(f"Balanced Accuracy (Fold {result['fold']}): {result['value']:.4f}")
    logger.info(f"Labels: {result['labels']}")

    # Save results
    results_text = f"""Balanced Accuracy Results
=========================
Fold: {result['fold']}
Balanced Accuracy: {result['value']:.4f}
Labels: {result['labels']}
"""

    stx.io.save(
        results_text,
        "balanced_accuracy_results.txt",
        use_caller_path=True
    )

    logger.info("Saved balanced accuracy results to _out directory")

    return 0


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Calculate balanced accuracy from classification data"
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
