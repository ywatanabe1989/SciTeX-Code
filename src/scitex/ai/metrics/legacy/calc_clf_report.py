#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-02 18:44:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/ml/metrics/_calc_clf_report.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
  - Generates classification report from true and predicted labels
  - Demonstrates calc_classification_report usage with example data
  - Saves results to _out directory

Dependencies:
  - packages:
    - numpy
    - scitex

IO:
  - output-files:
    - _calc_clf_report_out/classification_report.csv
    - _calc_clf_report_out/classification_report.txt
"""

"""Imports"""
import argparse

import numpy as np
import scitex as stx
from scitex import logging
from scitex.ml.metrics.classification import calc_classification_report

logger = logging.getLogger(__name__)

"""Functions & Classes"""
def main(args):
    """
    Demonstrate classification report generation.
    """
    # Example data
    y_true = np.array([0, 1, 0, 1, 0, 1, 1, 0])
    y_pred = np.array([0, 1, 0, 0, 0, 1, 1, 1])
    labels = ["Negative", "Positive"]

    # Generate classification report
    result = calc_classification_report(
        y_true=y_true,
        y_pred=y_pred,
        labels=labels,
        fold=0
    )

    # Log results
    logger.info(f"Classification Report (Fold {result['fold']}):")
    logger.info(f"\n{result['value']}")
    logger.info(f"Labels: {result['labels']}")

    # Save results
    if result['value'] is not None:
        stx.io.save(
            result['value'],
            "classification_report.csv",
            use_caller_path=True
        )
        stx.io.save(
            result['value'].to_string(),
            "classification_report.txt",
            use_caller_path=True
        )
        logger.info("Saved classification report to _out directory")

    return 0


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate classification report from classification data"
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
