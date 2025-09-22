#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: 04_calendar_split_demo.py

"""
Calendar-based time series splitting demonstration.

Shows how to use TimeSeriesCalendarSplit for monthly, weekly, or daily intervals.
"""

import numpy as np
import pandas as pd
from scitex.ml.classification import TimeSeriesCalendarSplit, ClassificationReporter
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler


def demo_monthly_splits():
    """Demonstrate monthly calendar-based splitting."""
    print("\n" + "="*60)
    print("MONTHLY CALENDAR SPLITTING DEMO")
    print("="*60)
    
    # Create sample data with daily timestamps over 2 years
    np.random.seed(42)
    dates = pd.date_range('2022-01-01', '2023-12-31', freq='D')
    n_samples = len(dates)
    n_features = 10
    
    # Generate features with temporal patterns
    X = np.random.randn(n_samples, n_features)
    # Add trend
    for i in range(n_features):
        X[:, i] += np.linspace(0, 2, n_samples) * (i / n_features)
    
    # Generate binary classification target with temporal dependency
    y = (X[:, 0] + 0.5 * X[:, 1] + np.random.randn(n_samples) * 0.5) > 0.5
    y = y.astype(int)
    
    print(f"Data shape: {X.shape}")
    print(f"Date range: {dates[0]} to {dates[-1]}")
    print(f"Class distribution: {np.bincount(y)}")
    
    # Create calendar splitter for monthly intervals
    # 12 months train, 1 month test, step by 1 month
    splitter = TimeSeriesCalendarSplit(
        interval='M',
        n_train_intervals=12,  # 12 months for training
        n_test_intervals=1,     # 1 month for testing
        gap_intervals=0,        # No gap between train and test
        step_intervals=3        # Move forward 3 months for next fold
    )
    
    # Initialize reporter
    reporter = ClassificationReporter("./calendar_split_results")
    
    # Perform cross-validation
    print("\nPerforming monthly cross-validation...")
    for fold, (train_idx, test_idx) in enumerate(splitter.split(X, y, timestamps=dates)):
        print(f"\nFold {fold}:")
        print(f"  Train: {dates[train_idx[0]]:%Y-%m-%d} to {dates[train_idx[-1]]:%Y-%m-%d} ({len(train_idx)} samples)")
        print(f"  Test:  {dates[test_idx[0]]:%Y-%m-%d} to {dates[test_idx[-1]]:%Y-%m-%d} ({len(test_idx)} samples)")
        
        # Get train/test data
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train model
        model = RandomForestClassifier(n_estimators=100, random_state=42 + fold)
        model.fit(X_train_scaled, y_train)
        
        # Get predictions
        y_pred = model.predict(X_test_scaled)
        y_proba = model.predict_proba(X_test_scaled)
        
        # Calculate metrics
        metrics = reporter.calculate_metrics(
            y_true=y_test,
            y_pred=y_pred,
            y_proba=y_proba,
            labels=["Class 0", "Class 1"],
            fold=fold,
            verbose=False
        )
        
        accuracy = np.mean(y_pred == y_test)
        print(f"  Accuracy: {accuracy:.3f}")
        
        # Save custom calendar info for this fold
        fold_info = {
            "train_start": str(dates[train_idx[0]]),
            "train_end": str(dates[train_idx[-1]]),
            "test_start": str(dates[test_idx[0]]),
            "test_end": str(dates[test_idx[-1]]),
            "n_train_samples": len(train_idx),
            "n_test_samples": len(test_idx),
            "accuracy": float(accuracy)
        }
        reporter.save(fold_info, "calendar_fold_info.json", fold=fold)
    
    # Save summary
    summary = reporter.get_summary()
    reporter.save_summary("calendar_cv_summary.json", verbose=False)
    
    print("\n" + "="*60)
    print("Monthly calendar splitting completed successfully!")
    print("Results saved to: ./calendar_split_results/")
    print("="*60)


def demo_weekly_splits():
    """Demonstrate weekly calendar-based splitting."""
    print("\n" + "="*60)
    print("WEEKLY CALENDAR SPLITTING DEMO")
    print("="*60)
    
    # Create sample data with hourly timestamps over 3 months
    np.random.seed(42)
    dates = pd.date_range('2023-10-01', '2023-12-31', freq='H')
    n_samples = len(dates)
    n_features = 5
    
    X = np.random.randn(n_samples, n_features)
    y = (X[:, 0] > 0).astype(int)
    
    print(f"Data shape: {X.shape}")
    print(f"Date range: {dates[0]} to {dates[-1]}")
    
    # Weekly splits: 4 weeks train, 1 week test
    splitter = TimeSeriesCalendarSplit(
        interval='W',
        n_train_intervals=4,   # 4 weeks for training
        n_test_intervals=1,     # 1 week for testing
        gap_intervals=0,        # No gap
        step_intervals=1        # Move forward 1 week for next fold
    )
    
    print("\nWeekly splits preview:")
    for fold, (train_idx, test_idx) in enumerate(splitter.split(X, y, timestamps=dates)):
        if fold < 3:  # Show first 3 folds
            print(f"Fold {fold}: Train weeks from {dates[train_idx[0]]:%Y-W%V}, Test week {dates[test_idx[0]]:%Y-W%V}")
    
    n_splits = splitter.get_n_splits(X, y, timestamps=dates)
    print(f"\nTotal number of weekly splits possible: {n_splits}")


if __name__ == "__main__":
    # Run demonstrations
    demo_monthly_splits()
    demo_weekly_splits()