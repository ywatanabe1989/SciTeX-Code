#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-02 18:42:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/ml/metrics/_calc_pre_rec_auc.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
  - Calculates Precision-Recall AUC from true labels and predicted probabilities
  - Demonstrates calc_pr_auc usage with example data
  - Saves results to _out directory

Dependencies:
  - packages:
    - numpy
    - scitex

IO:
  - output-files:
    - _calc_pre_rec_auc_out/pr_auc_results.txt
"""

"""Imports"""
import argparse

import numpy as np
import scitex as stx
from scitex import logging
from scitex.ml.metrics.classification import calc_pr_auc

logger = logging.getLogger(__name__)

"""Functions & Classes"""
def main(args):
    """
    Demonstrate Precision-Recall AUC calculation.
    """
    # Example data - binary classification
    y_true = np.array([0, 1, 0, 1, 0, 1, 1, 0])
    y_proba = np.array([
        [0.8, 0.2],
        [0.3, 0.7],
        [0.9, 0.1],
        [0.6, 0.4],
        [0.7, 0.3],
        [0.2, 0.8],
        [0.1, 0.9],
        [0.4, 0.6],
    ])
    labels = ["Negative", "Positive"]

    # Calculate PR AUC
    result = calc_pr_auc(
        y_true=y_true,
        y_proba=y_proba,
        labels=labels,
        fold=0,
        return_curve=True
    )

    # Log results
    logger.info(f"PR AUC (Fold {result['fold']}): {result['value']:.4f}")
    logger.info(f"Labels: {result['labels']}")

    if 'curve' in result:
        logger.info(f"Curve data available with {len(result['curve']['precision'])} points")

    # Save results
    results_text = f"""Precision-Recall AUC Results
============================
Fold: {result['fold']}
PR AUC: {result['value']:.4f}
Labels: {result['labels']}
"""

    if 'curve' in result:
        results_text += f"\nCurve Points: {len(result['curve']['precision'])}"

    stx.io.save(
        results_text,
        "pr_auc_results.txt",
        use_caller_path=True
    )

    logger.info("Saved PR AUC results to _out directory")

    return 0


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Calculate Precision-Recall AUC from classification probabilities"
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
