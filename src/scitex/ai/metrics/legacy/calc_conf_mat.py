#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-02 18:40:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/ml/metrics/_calc_conf_mat.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
  - Calculates confusion matrix from true and predicted labels
  - Demonstrates calc_confusion_matrix usage with example data
  - Saves results and visualizations to _out directory

Dependencies:
  - packages:
    - numpy
    - scitex

IO:
  - output-files:
    - _calc_conf_mat_out/confusion_matrix.csv
    - _calc_conf_mat_out/confusion_matrix.txt
"""

"""Imports"""
import argparse

import numpy as np
import scitex as stx
from scitex import logging
from scitex.ml.metrics.classification import calc_confusion_matrix

logger = logging.getLogger(__name__)

"""Functions & Classes"""
def main(args):
    """
    Demonstrate confusion matrix calculation.
    """
    # Example data
    y_true = np.array([0, 1, 0, 1, 0, 1, 1, 0])
    y_pred = np.array([0, 1, 0, 0, 0, 1, 1, 1])
    labels = ["Negative", "Positive"]

    # Calculate confusion matrix
    result = calc_confusion_matrix(
        y_true=y_true,
        y_pred=y_pred,
        labels=labels,
        fold=0,
        normalize=None
    )

    # Log results
    logger.info(f"Confusion Matrix (Fold {result['fold']}):")
    logger.info(f"\n{result['value']}")
    logger.info(f"Labels: {result['labels']}")

    # Save results
    if result['value'] is not None:
        stx.io.save(
            result['value'],
            "confusion_matrix.csv",
            use_caller_path=True
        )
        stx.io.save(
            result['value'].to_string(),
            "confusion_matrix.txt",
            use_caller_path=True
        )
        logger.info("Saved confusion matrix to _out directory")

    # Calculate normalized version
    result_norm = calc_confusion_matrix(
        y_true=y_true,
        y_pred=y_pred,
        labels=labels,
        fold=0,
        normalize="true"
    )

    logger.info(f"\nNormalized Confusion Matrix (Fold {result_norm['fold']}):")
    logger.info(f"\n{result_norm['value']}")

    if result_norm['value'] is not None:
        stx.io.save(
            result_norm['value'],
            "confusion_matrix_normalized.csv",
            use_caller_path=True
        )

    return 0


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Calculate confusion matrix from classification data"
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
