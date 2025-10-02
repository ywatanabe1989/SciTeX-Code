#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-02 18:41:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/ml/metrics/_calc_roc_auc.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
  - Calculates ROC AUC score from true labels and predicted probabilities
  - Demonstrates calc_roc_auc usage with example data
  - Saves results to _out directory

Dependencies:
  - packages:
    - numpy
    - scitex

IO:
  - output-files:
    - _calc_roc_auc_out/roc_auc_results.txt
"""

"""Imports"""
import argparse

import numpy as np
import scitex as stx
from scitex import logging
from scitex.ml.metrics.classification import calc_roc_auc

logger = logging.getLogger(__name__)

"""Functions & Classes"""
def main(args):
    """
    Demonstrate ROC AUC calculation.
    """
    # Example data - binary classification
    y_true = np.array([0, 1, 0, 1, 0, 1, 1, 0])
    y_proba = np.array([
        [0.8, 0.2],  # Pred: 0 (correct)
        [0.3, 0.7],  # Pred: 1 (correct)
        [0.9, 0.1],  # Pred: 0 (correct)
        [0.6, 0.4],  # Pred: 0 (wrong)
        [0.7, 0.3],  # Pred: 0 (correct)
        [0.2, 0.8],  # Pred: 1 (correct)
        [0.1, 0.9],  # Pred: 1 (correct)
        [0.4, 0.6],  # Pred: 1 (wrong)
    ])
    labels = ["Negative", "Positive"]

    # Calculate ROC AUC
    result = calc_roc_auc(
        y_true=y_true,
        y_proba=y_proba,
        labels=labels,
        fold=0,
        return_curve=True
    )

    # Log results
    logger.info(f"ROC AUC (Fold {result['fold']}): {result['value']:.4f}")
    logger.info(f"Labels: {result['labels']}")

    if 'curve' in result:
        logger.info(f"Curve data available with {len(result['curve']['fpr'])} points")

    # Save results
    results_text = f"""ROC AUC Results
===============
Fold: {result['fold']}
ROC AUC: {result['value']:.4f}
Labels: {result['labels']}
"""

    if 'curve' in result:
        results_text += f"\nCurve Points: {len(result['curve']['fpr'])}"

    stx.io.save(
        results_text,
        "roc_auc_results.txt",
        use_caller_path=True
    )

    logger.info("Saved ROC AUC results to _out directory")

    return 0


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Calculate ROC AUC from classification probabilities"
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
