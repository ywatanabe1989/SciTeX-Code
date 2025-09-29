#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-22 15:33:02 (ywatanabe)"
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
Time Series Cross-Validation Example

Demonstrates all available time series CV splitters:
- TimeSeriesStratifiedSplit: Single time series with class balance
- TimeSeriesBlockingSplit: Multiple subjects/groups
- TimeSeriesSlidingWindowSplit: Fixed-size sliding windows
- TimeSeriesCalendarSplit: Calendar-based intervals

Features:
- Unified ClassificationReporter API
- Automatic timestamp normalization
- Comprehensive metrics and organized output
"""

import argparse

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scitex as stx
from scitex.ml.classification import (ClassificationReporter,
                                      TimeSeriesBlockingSplit,
                                      TimeSeriesCalendarSplit,
                                      TimeSeriesSlidingWindowSplit,
                                      TimeSeriesStratifiedSplit)
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler


def main(args: argparse.Namespace) -> int:
    # Load time series data
    df = stx.io.load("./data/datasets/time_series_classification.csv")

    # Prepare features and target
    feature_cols = [col for col in df.columns if col.startswith("feature")]
    X = df[feature_cols].values
    y = df["target"].values
    timestamps = pd.to_datetime(df["timestamp"])

    # Create subject groups for blocking split demo
    if "subject" in df.columns:
        groups = df["subject"].values
    else:
        # Synthetic groups: 3 subjects
        n_subjects = 3
        samples_per_subject = len(df) // n_subjects
        groups = np.repeat(range(n_subjects), samples_per_subject)
        groups = np.pad(
            groups,
            (0, len(df) - len(groups)),
            mode="constant",
            constant_values=n_subjects - 1,
        )

    print(
        f"Dataset: {X.shape[0]} samples, {X.shape[1]} features, {len(np.unique(y))} classes"
    )
    print(f"Time range: {timestamps.min()} to {timestamps.max()}")
    print(f"Groups: {len(np.unique(groups))} subjects")

    # =================================================================
    # DEMO 1: TimeSeriesStratifiedSplit
    # =================================================================
    print("\n" + "=" * 60)
    print("DEMO 1: TimeSeriesStratifiedSplit")
    print("Single time series with stratification")
    print("=" * 60)

    splitter1 = TimeSeriesStratifiedSplit(
        n_splits=3, test_ratio=0.2, val_ratio=0.1, gap=5, stratify=True
    )

    reporter1 = ClassificationReporter(CONFIG.SDIR + "time_series_stratified")

    for fold, (train_idx, test_idx) in enumerate(
        splitter1.split(X, y, timestamps=timestamps)
    ):
        print(f"\nFold {fold}:")
        print(f"  Train: {len(train_idx)} samples")
        print(f"  Test:  {len(test_idx)} samples")

        accuracy = train_and_evaluate(
            X, y, train_idx, test_idx, reporter1, fold
        )
        print(f"  Accuracy: {accuracy:.3f}")

    reporter1.save_summary("stratified_cv_summary.json", verbose=False)
    
    # Visualize stratified splits
    print("\nVisualizing stratified splits...")
    fig = splitter1.plot_splits(X, timestamps=timestamps)
    reporter1.save(fig, "cv_summary/stratified_splits.png")
    plt.close(fig)

    # =================================================================
    # DEMO 2: TimeSeriesBlockingSplit
    # =================================================================
    print("\n" + "=" * 60)
    print("DEMO 2: TimeSeriesBlockingSplit")
    print("Multiple subjects - no mixing between subjects")
    print("=" * 60)

    splitter2 = TimeSeriesBlockingSplit(n_splits=3, test_ratio=0.3)

    reporter2 = ClassificationReporter(CONFIG.SDIR + "time_series_blocking")

    for fold, (train_idx, test_idx) in enumerate(
        splitter2.split(X, y, timestamps=timestamps, groups=groups)
    ):
        train_subjects = set(groups[train_idx])
        test_subjects = set(groups[test_idx])

        print(f"\nFold {fold}:")
        print(
            f"  Train: {len(train_idx)} samples from subjects {sorted(train_subjects)}"
        )
        print(
            f"  Test:  {len(test_idx)} samples from subjects {sorted(test_subjects)}"
        )
        print(f"  No overlap: {len(train_subjects & test_subjects) == 0}")

        accuracy = train_and_evaluate(
            X, y, train_idx, test_idx, reporter2, fold
        )
        print(f"  Accuracy: {accuracy:.3f}")

    reporter2.save_summary("blocking_cv_summary.json", verbose=False)
    
    # Visualize blocking splits
    print("\nVisualizing blocking splits...")
    fig = splitter2.plot_splits(X, timestamps=timestamps, groups=groups)
    reporter2.save(fig, "cv_summary/blocking_splits.png")
    plt.close(fig)

    # =================================================================
    # DEMO 3: TimeSeriesSlidingWindowSplit
    # =================================================================
    print("\n" + "=" * 60)
    print("DEMO 3: TimeSeriesSlidingWindowSplit")
    print("Fixed-size sliding windows")
    print("=" * 60)

    splitter3 = TimeSeriesSlidingWindowSplit(
        window_size=60, step_size=20, test_size=20, gap=5
    )

    reporter3 = ClassificationReporter(CONFIG.SDIR + "time_series_sliding")

    for fold, (train_idx, test_idx) in enumerate(
        splitter3.split(X, y, timestamps=timestamps)
    ):
        if fold >= 3:  # Limit to 3 folds for demo
            break

        print(f"\nFold {fold}:")
        print(
            f"  Train: samples {train_idx[0]}-{train_idx[-1]} ({len(train_idx)} samples)"
        )
        print(
            f"  Test:  samples {test_idx[0]}-{test_idx[-1]} ({len(test_idx)} samples)"
        )

        accuracy = train_and_evaluate(
            X, y, train_idx, test_idx, reporter3, fold
        )
        print(f"  Accuracy: {accuracy:.3f}")

    reporter3.save_summary("sliding_cv_summary.json", verbose=False)
    
    # Visualize sliding window splits
    print("\nVisualizing sliding window splits...")
    fig = splitter3.plot_splits(X, timestamps=timestamps)
    reporter3.save(fig, "cv_summary/sliding_window_splits.png")
    plt.close(fig)

    # =================================================================
    # DEMO 4: TimeSeriesCalendarSplit
    # =================================================================
    print("\n" + "=" * 60)
    print("DEMO 4: TimeSeriesCalendarSplit")
    print("Calendar-based monthly intervals")
    print("=" * 60)

    # Create synthetic monthly timestamps for demo
    monthly_dates = pd.date_range(
        "2023-01-01", periods=len(X), freq="6H"
    )  # Every 6 hours

    splitter4 = TimeSeriesCalendarSplit(
        interval="M", n_train_intervals=6, n_test_intervals=1, step_intervals=2
    )

    reporter4 = ClassificationReporter(CONFIG.SDIR + "time_series_calendar")

    try:
        for fold, (train_idx, test_idx) in enumerate(
            splitter4.split(X, y, timestamps=monthly_dates)
        ):
            if fold >= 2:  # Limit to 2 folds for demo
                break

            print(f"\nFold {fold}:")
            print(
                f"  Train: {monthly_dates[train_idx[0]].strftime('%Y-%m')} to {monthly_dates[train_idx[-1]].strftime('%Y-%m')}"
            )
            print(
                f"  Test:  {monthly_dates[test_idx[0]].strftime('%Y-%m')} ({len(test_idx)} samples)"
            )

            accuracy = train_and_evaluate(
                X, y, train_idx, test_idx, reporter4, fold
            )
            print(f"  Accuracy: {accuracy:.3f}")

        reporter4.save_summary("calendar_cv_summary.json", verbose=False)
        
        # Visualize calendar splits
        print("\nVisualizing calendar splits...")
        fig = splitter4.plot_splits(X, timestamps=monthly_dates)
        reporter4.save(fig, "cv_summary/calendar_splits.png")
        plt.close(fig)
    except Exception as e:
        print(f"Calendar split demo skipped: {str(e)}")

    # =================================================================
    # DEMO 5: Train-Validation-Test Split Example
    # =================================================================
    print("\n" + "=" * 60)
    print("DEMO 5: Train-Validation-Test Split")
    print("Time series split with validation set (green) - maintains temporal order")
    print("=" * 60)

    splitter5 = TimeSeriesStratifiedSplit(
        n_splits=3, test_ratio=0.2, val_ratio=0.15, gap=3, stratify=True
    )

    reporter5 = ClassificationReporter(CONFIG.SDIR + "time_series_val_split")

    print("\nTrain-Validation-Test configuration:")
    print(f"  - Train: ~{100 - 20 - 15}% of data (expanding window)")
    print(f"  - Validation: {15}% of data") 
    print(f"  - Test: {20}% of data")
    print(f"  - Gap: {3} samples between sets")
    print(f"  - Stratification: Enabled (temporal-aware - preserves chronological order)")

    # Run one fold as example
    for fold, (train_idx, val_idx, test_idx) in enumerate(
        splitter5.split_with_val(X, y, timestamps=timestamps)
    ):
        if fold >= 1:  # Just show first fold
            break
            
        print(f"\nFold {fold} breakdown:")
        print(f"  Train: {len(train_idx)} samples")
        print(f"  Validation: {len(val_idx)} samples") 
        print(f"  Test: {len(test_idx)} samples")
        
        # Proper train-validation-test workflow
        val_accuracy, test_accuracy = train_validate_and_test(
            X, y, train_idx, val_idx, test_idx, reporter5, fold
        )
        print(f"  Validation accuracy: {val_accuracy:.3f}")
        print(f"  Test accuracy: {test_accuracy:.3f}")

    reporter5.save_summary("val_split_cv_summary.json", verbose=False)
    
    # Visualize train-validation-test splits  
    print("\nVisualizing train-validation-test splits...")
    fig = splitter5.plot_splits(X, timestamps=timestamps)
    reporter5.save(fig, "cv_summary/train_val_test_splits.png")
    plt.close(fig)

    # =================================================================
    # Additional Configuration Examples
    # =================================================================
    print("\n" + "=" * 60)
    print("ADDITIONAL SPLITTER CONFIGURATIONS")
    print("=" * 60)

    print("\n# Weekly calendar splits:")
    print("# splitter = TimeSeriesCalendarSplit(")
    print("#     interval='W',           # Weekly")
    print("#     n_train_intervals=8,    # 8 weeks training")
    print("#     n_test_intervals=2,     # 2 weeks testing")
    print("#     gap_intervals=1         # 1 week gap")
    print("# )")

    print("\n# Larger sliding windows:")
    print("# splitter = TimeSeriesSlidingWindowSplit(")
    print("#     window_size=200,        # Larger windows")
    print("#     step_size=50,           # Larger steps")
    print("#     test_size=50            # Larger test windows")
    print("# )")
    
    print("\n# Train-Validation-Test splits:")
    print("# splitter = TimeSeriesStratifiedSplit(")
    print("#     n_splits=3,")
    print("#     test_ratio=0.2,          # 20% test")
    print("#     val_ratio=0.15,          # 15% validation")
    print("#     gap=5,                   # 5 sample gap")
    print("#     stratify=True            # Maintain class balance")
    print("# )")
    print("# # Use val_ratio > 0 to get train-val-test splits")
    
    print("\n# Visualize any splitter:")
    print("# fig = splitter.plot_splits(X, timestamps=timestamps)")
    print("# reporter.save(fig, 'cv_summary/my_splits.png')  # Save via reporter")
    print("# fig.savefig('my_splits.png')                   # Or save directly")

    print("\n# Stratified with validation set:")
    print("# splitter = TimeSeriesStratifiedSplit(")
    print("#     n_splits=5,")
    print("#     test_ratio=0.15,        # Smaller test")
    print("#     val_ratio=0.1,          # Add validation")
    print("#     gap=10,                 # Larger gap")
    print("#     stratify=False          # No stratification")
    print("# )")

    print("\n" + "=" * 60)
    print("Time series CV demonstrations completed!")
    print("Check output directories for:")
    print("  - Comprehensive classification metrics and summaries")
    print("  - Split visualizations in cv_summary/ subdirectories")
    print("  - Train (blue), Validation (green), Test (red) split plots")
    print("=" * 60)

    return 0


def train_and_evaluate(X, y, train_idx, test_idx, reporter, fold):
    """Train model and calculate metrics."""
    # Split data
    X_train, X_test = X[train_idx], X[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]

    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Train model
    model = RandomForestClassifier(n_estimators=50, random_state=42 + fold)
    model.fit(X_train_scaled, y_train)

    # Get predictions
    y_pred = model.predict(X_test_scaled)
    y_proba = model.predict_proba(X_test_scaled)

    # Calculate metrics
    class_names = [f"Class_{i}" for i in range(len(np.unique(y)))]
    reporter.calculate_metrics(
        y_true=y_test,
        y_pred=y_pred,
        y_proba=y_proba,
        labels=class_names,
        fold=fold,
        verbose=False,
    )

    return np.mean(y_pred == y_test)


def train_validate_and_test(X, y, train_idx, val_idx, test_idx, reporter, fold):
    """Train model, validate for hyperparameters, then test - proper 3-way split."""
    # Split data into train, validation, and test
    X_train, X_val, X_test = X[train_idx], X[val_idx], X[test_idx]
    y_train, y_val, y_test = y[train_idx], y[val_idx], y[test_idx]

    # Scale features (fit on train, transform val and test)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)
    X_test_scaled = scaler.transform(X_test)

    # Train model on training set
    model = RandomForestClassifier(n_estimators=50, random_state=42 + fold)
    model.fit(X_train_scaled, y_train)

    # Validate on validation set
    y_val_pred = model.predict(X_val_scaled)
    val_accuracy = np.mean(y_val_pred == y_val)

    # Final evaluation on test set
    y_test_pred = model.predict(X_test_scaled)
    y_test_proba = model.predict_proba(X_test_scaled)
    test_accuracy = np.mean(y_test_pred == y_test)

    # Report metrics on test set (the final evaluation)
    class_names = [f"Class_{i}" for i in range(len(np.unique(y)))]
    reporter.calculate_metrics(
        y_true=y_test,
        y_pred=y_test_pred,
        y_proba=y_test_proba,
        labels=class_names,
        fold=fold,
        verbose=False,
    )

    return val_accuracy, test_accuracy


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Time series cross-validation example"
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
