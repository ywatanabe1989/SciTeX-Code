#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: 05_timestamp_normalization_demo.py

"""
Demonstration of timestamp normalization with TimeSeriesCalendarSplit.

Shows how the normalizer handles various timestamp formats automatically.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from scitex.ml.classification import (
    TimeSeriesCalendarSplit, 
    ClassificationReporter
)
from scitex.ml.classification.time_series import normalize_timestamp
from sklearn.ensemble import RandomForestClassifier


def demo_mixed_timestamp_formats():
    """Demonstrate handling of various timestamp formats."""
    print("\n" + "="*60)
    print("MIXED TIMESTAMP FORMATS DEMO")
    print("="*60)
    
    # Create sample data with various timestamp formats
    np.random.seed(42)
    n_samples = 365  # One year of daily data
    
    # Generate different timestamp formats
    base_date = datetime(2023, 1, 1)
    timestamps = []
    
    for i in range(n_samples):
        current_date = base_date + timedelta(days=i)
        
        # Use different formats for different portions of data
        if i % 4 == 0:
            # ISO format with T
            ts = current_date.strftime("%Y-%m-%dT%H:%M:%S")
        elif i % 4 == 1:
            # Standard format with microseconds
            ts = current_date.strftime("%Y-%m-%d %H:%M:%S.%f")
        elif i % 4 == 2:
            # Unix timestamp
            ts = current_date.timestamp()
        else:
            # Alternative format with slashes
            ts = current_date.strftime("%Y/%m/%d %H:%M:%S")
        
        timestamps.append(ts)
    
    # Generate features and target
    X = np.random.randn(n_samples, 10)
    y = (X[:, 0] > 0).astype(int)
    
    print(f"Sample timestamp formats in data:")
    for i in [0, 1, 2, 3]:
        print(f"  Sample {i}: {timestamps[i]} (type: {type(timestamps[i]).__name__})")
    
    # Normalize all timestamps for display
    normalized = [normalize_timestamp(ts) for ts in timestamps[:4]]
    print(f"\nAfter normalization:")
    for i, norm_ts in enumerate(normalized):
        print(f"  Sample {i}: {norm_ts}")
    
    # Use TimeSeriesCalendarSplit - it will handle mixed formats automatically
    splitter = TimeSeriesCalendarSplit(
        interval='M',
        n_train_intervals=9,
        n_test_intervals=1,
        step_intervals=1
    )
    
    print(f"\nPerforming cross-validation with mixed timestamp formats...")
    
    # Initialize reporter
    reporter = ClassificationReporter("./timestamp_demo_results")
    
    # Perform splits - the splitter will normalize timestamps internally
    for fold, (train_idx, test_idx) in enumerate(splitter.split(X, y, timestamps=timestamps)):
        if fold >= 2:  # Just show first 2 folds
            break
            
        print(f"\nFold {fold}:")
        print(f"  Train: {len(train_idx)} samples")
        print(f"  Test:  {len(test_idx)} samples")
        
        # Train simple model
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]
        
        model = RandomForestClassifier(n_estimators=50, random_state=42)
        model.fit(X_train, y_train)
        
        # Get predictions
        y_pred = model.predict(X_test)
        accuracy = np.mean(y_pred == y_test)
        print(f"  Accuracy: {accuracy:.3f}")
    
    print("\n" + "="*60)
    print("Successfully handled mixed timestamp formats!")
    print("="*60)


def demo_timestamp_utilities():
    """Demonstrate various timestamp utility functions."""
    print("\n" + "="*60)
    print("TIMESTAMP UTILITIES DEMO")
    print("="*60)
    
    from scitex.ml.classification.time_series import (
        format_for_filename,
        format_for_display,
        get_time_delta_seconds,
        validate_timestamp_format
    )
    
    # Test timestamp
    test_dt = datetime(2023, 6, 15, 14, 30, 45, 123456)
    test_str = "2023-06-15 14:30:45.123456"
    
    print(f"Original datetime: {test_dt}")
    print(f"Original string:   {test_str}")
    print()
    
    # Format for filename
    filename_str = format_for_filename(test_dt)
    print(f"Filename format:   {filename_str}")
    
    # Format for display
    display_str = format_for_display(test_dt)
    print(f"Display format:    {display_str}")
    
    # Validate format
    is_valid = validate_timestamp_format(test_str)
    print(f"Is valid format:   {is_valid}")
    
    # Calculate time delta
    start = datetime(2023, 1, 1, 10, 0, 0)
    end = datetime(2023, 1, 2, 14, 30, 0)
    delta_seconds = get_time_delta_seconds(start, end)
    delta_hours = delta_seconds / 3600
    print(f"\nTime delta:")
    print(f"  Start: {start}")
    print(f"  End:   {end}")
    print(f"  Delta: {delta_seconds:.0f} seconds ({delta_hours:.1f} hours)")
    
    print("\n" + "="*60)
    print("Timestamp utilities demonstrated!")
    print("="*60)


if __name__ == "__main__":
    # Run demonstrations
    demo_mixed_timestamp_formats()
    demo_timestamp_utilities()