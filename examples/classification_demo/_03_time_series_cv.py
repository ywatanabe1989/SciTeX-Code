#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-21 23:36:26 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/examples/classification_demo/03_time_series_cv.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./examples/classification_demo/03_time_series_cv.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Time Series Cross-Validation Example with SciTeX

Functionalities:
  1. Demonstrate TimeSeriesBlockingSplit for multiple subjects
  2. Demonstrate TimeSeriesStratifiedSplit for single time series
  3. Perform temporal validation without data leakage
  4. Report classification metrics for each fold

Dependencies:
  - Core libraries: numpy, pandas, scikit-learn
  - SciTeX modules: scitex.ml.classification, scitex.io, scitex.logging, scitex.session

IO:
  - Input:
      - ./data/time_series_classification.csv (for blocking split)
      - ./data/binary_classification.csv (for stratified split)
  - Output:
      - ./outputs/time_series_blocking/ (blocking split results)
      - ./outputs/time_series_stratified/ (stratified split results)
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import scitex as stx
from scitex.logging import getLogger
from scitex.ml.classification import (SingleTaskClassificationReporter,
                                      TimeSeriesBlockingSplit,
                                      TimeSeriesStratifiedSplit)
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, balanced_accuracy_score
from sklearn.preprocessing import StandardScaler

logger = getLogger(__name__)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Time series cross-validation example with SciTeX"
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("./data"),
        help="Directory containing input data (default: ./data)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,  # Will use CONFIG['SDIR'] if not specified
        help="Base output directory for results (default: uses SciTeX session directory)",
    )
    parser.add_argument(
        "--n-splits",
        type=int,
        default=3,
        help="Number of CV folds (default: 3)",
    )
    parser.add_argument(
        "--test-ratio",
        type=float,
        default=0.2,
        help="Proportion of data for testing in each fold (default: 0.2)",
    )
    parser.add_argument(
        "--gap",
        type=int,
        default=10,
        help="Gap between train and test sets in stratified split (default: 10)",
    )
    parser.add_argument(
        "--n-estimators",
        type=int,
        default=50,
        help="Number of trees in Random Forest (default: 50)",
    )
    parser.add_argument(
        "--random-state",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42)",
    )
    parser.add_argument(
        "--demo",
        type=str,
        choices=["blocking", "stratified", "both"],
        default="both",
        help="Which demo to run (default: both)",
    )
    return parser.parse_args()


def demonstrate_blocking_split(args):
    """Demonstrate TimeSeriesBlockingSplit for multiple subjects.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments

    Returns
    -------
    dict
        Results from blocking split CV
    """
    logger.info("\n" + "=" * 60)
    logger.info("Time Series Blocking Split (Multiple Subjects)")
    logger.info("=" * 60)

    # Load time series data
    data_path = args.data_dir / "time_series_classification.csv"
    df = stx.io.load(data_path)

    logger.info(f"Loaded dataset: {data_path}")
    logger.info(f"Shape: {df.shape}")
    logger.info(f"Subjects: {df['subject_id'].nunique()}")

    # Prepare data
    feature_cols = [col for col in df.columns if col.startswith("feature")]
    X = df[feature_cols].values
    y = df["target"].values
    timestamps = df["timestamp"].values
    groups = df["subject_id"].values

    # Initialize splitter
    tscv = TimeSeriesBlockingSplit(
        n_splits=args.n_splits, test_ratio=args.test_ratio
    )

    # Use SciTeX output directory if not specified
    if args.output_dir is None:
        base_output_dir = Path(CONFIG["SDIR"]) / "classification_results"
    else:
        base_output_dir = args.output_dir

    # Initialize reporter
    output_dir = base_output_dir / "time_series_blocking"
    reporter = SingleTaskClassificationReporter(
        name="time_series_blocking", output_dir=str(output_dir)
    )

    logger.info(f"Performing {tscv.n_splits}-fold blocking time series CV...")
    logger.info("Each subject's time series is split temporally")

    # Perform cross-validation
    fold_scores = []
    all_metrics = []

    for fold_idx, (train_idx, test_idx) in enumerate(
        tscv.split(X, y, timestamps, groups)
    ):
        logger.info(f"\n--- Fold {fold_idx + 1}/{tscv.n_splits} ---")

        # Get train/test data
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]

        # Check temporal ordering
        train_times = timestamps[train_idx]
        test_times = timestamps[test_idx]
        logger.info(
            f"Train samples: {len(train_idx)}, Test samples: {len(test_idx)}"
        )
        logger.info(
            f"Train time range: [{train_times.min():.2f}, {train_times.max():.2f}]"
        )
        logger.info(
            f"Test time range: [{test_times.min():.2f}, {test_times.max():.2f}]"
        )

        # Scale features
        scaler = StandardScaler()
        X_train = scaler.fit_transform(X_train)
        X_test = scaler.transform(X_test)

        # Train model
        model = RandomForestClassifier(
            n_estimators=args.n_estimators, random_state=args.random_state
        )
        model.fit(X_train, y_train)

        # Predict
        y_pred = model.predict(X_test)
        y_pred_proba = model.predict_proba(X_test)

        # Calculate metrics
        acc = accuracy_score(y_test, y_pred)
        bal_acc = balanced_accuracy_score(y_test, y_pred)
        fold_scores.append(bal_acc)

        logger.success(
            f"Accuracy: {acc:.3f}, Balanced Accuracy: {bal_acc:.3f}"
        )

        # Report metrics
        metrics = reporter.calculate_metrics(
            y_true=y_test,
            y_pred=y_pred,
            y_proba=y_pred_proba,
            labels=["Class_0", "Class_1"],
            fold_idx=fold_idx,
        )
        all_metrics.append(metrics)

    mean_score = np.mean(fold_scores)
    std_score = np.std(fold_scores)
    logger.success(
        f"\nMean Balanced Accuracy: {mean_score:.3f} ± {std_score:.3f}"
    )

    # Save CV summary
    cv_summary = pd.DataFrame(
        {"fold": range(len(fold_scores)), "balanced_accuracy": fold_scores}
    )
    summary_path = output_dir / "cv_summary.csv"
    stx.io.save(cv_summary, summary_path, symlink_from_cwd=True)

    return {
        "fold_scores": fold_scores,
        "mean_score": mean_score,
        "std_score": std_score,
        "metrics": all_metrics,
    }


def demonstrate_stratified_split(args):
    """Demonstrate TimeSeriesStratifiedSplit for single time series.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments

    Returns
    -------
    dict
        Results from stratified split CV
    """
    logger.info("\n" + "=" * 60)
    logger.info("Time Series Stratified Split (Single Time Series)")
    logger.info("=" * 60)

    # Use binary classification data as a single time series
    data_path = args.data_dir / "binary_classification.csv"
    df = stx.io.load(data_path)

    # Add synthetic timestamps
    df["timestamp"] = np.arange(len(df))

    logger.info(f"Loaded dataset: {data_path}")
    logger.info(f"Shape: {df.shape}")

    # Prepare data
    feature_cols = [col for col in df.columns if col.startswith("feature")]
    X = df[feature_cols].values
    y = df["target"].values
    timestamps = df["timestamp"].values

    # Initialize splitter with stratification
    tscv = TimeSeriesStratifiedSplit(
        n_splits=args.n_splits,
        test_ratio=args.test_ratio,
        gap=args.gap,
        stratify=True,
    )

    # Use SciTeX output directory if not specified
    if args.output_dir is None:
        base_output_dir = Path(CONFIG["SDIR"]) / "classification_results"
    else:
        base_output_dir = args.output_dir

    # Initialize reporter
    output_dir = base_output_dir / "time_series_stratified"
    reporter = SingleTaskClassificationReporter(
        name="time_series_stratified", output_dir=str(output_dir)
    )

    logger.info(
        f"Performing {tscv.n_splits}-fold stratified time series CV..."
    )
    logger.info(
        f"Gap of {tscv.gap} samples between train and test (prevents leakage)"
    )

    # Perform cross-validation
    fold_scores = []
    all_metrics = []

    for fold_idx, (train_idx, test_idx) in enumerate(
        tscv.split(X, y, timestamps)
    ):
        logger.info(f"\n--- Fold {fold_idx + 1}/{tscv.n_splits} ---")

        # Get train/test data
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]

        # Check class balance
        train_dist = np.bincount(y_train) / len(y_train)
        test_dist = np.bincount(y_test) / len(y_test)
        logger.info(
            f"Train samples: {len(train_idx)}, Test samples: {len(test_idx)}"
        )
        logger.info(f"Train class distribution: {train_dist}")
        logger.info(f"Test class distribution: {test_dist}")

        # Scale features
        scaler = StandardScaler()
        X_train = scaler.fit_transform(X_train)
        X_test = scaler.transform(X_test)

        # Train model
        model = RandomForestClassifier(
            n_estimators=args.n_estimators, random_state=args.random_state
        )
        model.fit(X_train, y_train)

        # Predict
        y_pred = model.predict(X_test)
        y_pred_proba = model.predict_proba(X_test)

        # Calculate metrics
        acc = accuracy_score(y_test, y_pred)
        bal_acc = balanced_accuracy_score(y_test, y_pred)
        fold_scores.append(bal_acc)

        logger.success(
            f"Accuracy: {acc:.3f}, Balanced Accuracy: {bal_acc:.3f}"
        )

        # Report metrics
        metrics = reporter.calculate_metrics(
            y_true=y_test,
            y_pred=y_pred,
            y_proba=y_pred_proba,
            labels=["Negative", "Positive"],
            fold_idx=fold_idx,
        )
        all_metrics.append(metrics)

    mean_score = np.mean(fold_scores)
    std_score = np.std(fold_scores)
    logger.success(
        f"\nMean Balanced Accuracy: {mean_score:.3f} ± {std_score:.3f}"
    )

    # Save CV summary
    cv_summary = pd.DataFrame(
        {"fold": range(len(fold_scores)), "balanced_accuracy": fold_scores}
    )
    summary_path = output_dir / "cv_summary.csv"
    stx.io.save(cv_summary, summary_path, symlink_from_cwd=True)

    return {
        "fold_scores": fold_scores,
        "mean_score": mean_score,
        "std_score": std_score,
        "metrics": all_metrics,
    }


def main(args):
    """Run time series CV examples.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments

    Returns
    -------
    dict
        Results from both CV strategies
    """
    logger.info("=" * 60)
    logger.info("Time Series Cross-Validation Examples")
    logger.info("=" * 60)

    results = {}

    # Demonstrate different time series CV strategies
    if args.demo in ["blocking", "both"]:
        results["blocking"] = demonstrate_blocking_split(args)

    if args.demo in ["stratified", "both"]:
        results["stratified"] = demonstrate_stratified_split(args)

    logger.success("\n" + "=" * 60)
    logger.success("Time series CV examples completed!")
    # Show correct output directory in message
    output_base = (
        args.output_dir
        if args.output_dir is not None
        else Path(CONFIG["SDIR"]) / "classification_results"
    )
    logger.success(f"Check {output_base} directory for organized results")
    logger.success("=" * 60)

    return 0  # Exit status


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
