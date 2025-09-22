#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-22 15:06:39 (ywatanabe)"
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
from scitex.ml.classification import ClassificationReporter
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler

logger = getLogger(__name__)

"""Parameters"""
# CONFIG = stx.io.load_configs()

"""Functions & Classes"""
def main(args: argparse.Namespace) -> int:
    # Load data
    df = stx.io.load("./data/datasets/binary_classification.csv")

    # Prepare features and target
    feature_cols = [col for col in df.columns if col.startswith("feature")]
    X = df[feature_cols].values
    y = df["target"].values

    # Initialize unified reporter (single-task mode)
    reporter = ClassificationReporter(
        CONFIG.SDIR + "classification_results",
    )

    # Perform 5-fold cross-validation
    n_folds = 5
    cv = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=42)

    for fold, (train_idx, test_idx) in enumerate(cv.split(X, y)):
        # Split data for this fold
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]

        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        # Train model for this fold
        model = RandomForestClassifier(
            n_estimators=100, random_state=42 + fold
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
            fold=fold,
        )

        # Save custom data for this fold using real model outputs
        # Save actual feature importances from the trained model
        feature_importance = {
            f"feature_{i}": importance
            for i, importance in enumerate(model.feature_importances_)
        }
        reporter.save(feature_importance, "feature_importance.json", fold=fold)

        # Save predictions with sample indices
        fold_predictions = pd.DataFrame(
            {
                "sample_idx": test_idx,
                "y_true": y_test,
                "y_pred": y_pred,
                "y_proba_positive": (
                    y_pred_proba[:, 1]
                    if y_pred_proba.ndim == 2
                    else y_pred_proba
                ),
            }
        )
        reporter.save(fold_predictions, "predictions.csv", fold=fold)

        # Save model coefficients/parameters
        model_info = {
            "n_estimators": model.n_estimators,
            "max_features": model.max_features,
            "n_features_in": model.n_features_in_,
            "n_classes": model.n_classes_,
            "feature_importances": model.feature_importances_.tolist(),
        }
        reporter.save(model_info, "model_info.json", fold=fold)

    # Save summary across all folds
    summary = reporter.get_summary()
    summary_path = reporter.save_summary("cv_summary.json")

    # Save aggregated custom analysis to cv_summary
    # Convert numpy types to Python types for JSON serialization
    unique_vals, counts = np.unique(y, return_counts=True)
    aggregated_analysis = {
        "dataset_info": {
            "n_samples": int(X.shape[0]),
            "n_features": int(X.shape[1]),
            "n_classes": 2,
            "class_balance": {
                int(val): int(count) for val, count in zip(unique_vals, counts)
            },
        },
        "cv_strategy": "StratifiedKFold",
        "n_folds": 5,
        "model_type": "RandomForestClassifier",
        "timestamp": pd.Timestamp.now().isoformat(),
    }
    reporter.save(aggregated_analysis, "cv_summary/experiment_metadata.json")

    # Save a custom markdown report
    balanced_acc_mean = summary.get("balanced_accuracy", {}).get("mean", 0.0)
    roc_auc_mean = summary.get("roc_auc", {}).get("mean", 0.0)
    pr_auc_mean = summary.get("pr_auc", {}).get("mean", 0.0)

    custom_report = f"""# Custom Analysis Report

## Experiment Overview
- Dataset: Make classification (sklearn)
- Model: Random Forest Classifier
- CV Strategy: 5-fold Stratified Cross-Validation
- Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

## Key Findings
- Mean Balanced Accuracy: {balanced_acc_mean:.3f}
- Mean ROC-AUC: {roc_auc_mean:.3f}
- Mean PR-AUC: {pr_auc_mean:.3f}

## Notes
This demonstrates the custom data saving functionality of the reporter.
You can save any data format to any location within the organized structure.
"""
    reporter.save(custom_report, "reports/custom_analysis.md")

    logger.info("Custom data saved successfully")

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
