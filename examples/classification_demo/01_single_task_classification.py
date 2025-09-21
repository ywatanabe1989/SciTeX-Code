#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-22 01:51:55 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/examples/classification_demo/01_single_task_classification.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./examples/classification_demo/01_single_task_classification.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
  - Demonstrates single task binary classification workflow
  - Evaluates model using improved SingleTaskClassificationReporter
  - Saves comprehensive metrics including balanced accuracy, MCC, confusion matrix

Dependencies:
  - scripts:
    - 00_generate_data.py (to create input data)
  - packages:
    - numpy
    - pandas
    - sklearn
    - scitex

IO:
  - input-files:
    - ./data/binary_classification.csv

  - output-files:
    - ./results/single_task_classification/metrics/
    - ./results/single_task_classification/plots/
    - ./results/single_task_classification/summary.json
"""

"""Imports"""
import argparse

import numpy as np
import pandas as pd
import scitex as stx
from scitex.logging import getLogger
from scitex.ml.classification import (ReporterConfig,
                                      SingleTaskClassificationReporter)
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler

logger = getLogger(__name__)

"""Parameters"""
# CONFIG = stx.io.load_configs()

"""Functions & Classes"""
def main(args: argparse.Namespace) -> int:
    # Load data
    df = pd.read_csv(f"./data/datasets/binary_classification.csv")

    # Prepare features and target
    feature_cols = [col for col in df.columns if col.startswith("feature")]
    X = df[feature_cols].values
    y = df["target"].values

    # Configure and initialize reporter
    config = ReporterConfig()
    reporter = SingleTaskClassificationReporter(
        name="single_task_classification",
        output_dir=CONFIG.SDIR + "classification_results",
        config=config,
    )
    # Pass the session CONFIG for inclusion in reports
    reporter.set_session_config(CONFIG)

    # Perform 5-fold cross-validation
    n_folds = 5
    cv = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=42)

    for fold_idx, (train_idx, test_idx) in enumerate(cv.split(X, y)):
        # Split data for this fold
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]

        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        # Train model for this fold
        model = RandomForestClassifier(
            n_estimators=100, random_state=42 + fold_idx
        )
        model.fit(X_train_scaled, y_train)

        # Get predictions
        y_pred = model.predict(X_test_scaled)
        y_pred_proba = model.predict_proba(X_test_scaled)

        # Calculate and save metrics for this fold
        fold_metrics = reporter.calculate_metrics(
            y_true=y_test,
            y_pred=y_pred,
            y_proba=y_pred_proba,
            labels=["Negative", "Positive"],
            fold_idx=fold_idx,
        )

    # Save summary across all folds
    summary = reporter.get_summary()
    summary_path = reporter.save_summary("cv_summary.json")

    return 0


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Single task binary classification example"
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
