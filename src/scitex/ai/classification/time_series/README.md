# Time Series Cross-Validation Module

Production-ready time series cross-validation utilities for machine learning classification tasks.

## Overview

This module provides specialized cross-validation strategies for time series data, ensuring:
- Temporal order preservation (no future data leakage)
- Support for multiple time series scenarios
- Calendar-aware splitting
- Robust timestamp handling

## Available Splitters

### TimeSeriesStratifiedSplit
Single time series with stratification to maintain class balance.

```python
from scitex.ml.classification import TimeSeriesStratifiedSplit

splitter = TimeSeriesStratifiedSplit(
    n_splits=5,
    test_ratio=0.2,
    gap=10  # 10 samples gap between train/test
)
```

### TimeSeriesBlockingSplit  
Multiple independent time series (e.g., different patients/subjects).

```python
from scitex.ml.classification import TimeSeriesBlockingSplit

splitter = TimeSeriesBlockingSplit(n_splits=3, test_ratio=0.2)
# Requires 'groups' parameter in split()
```

### TimeSeriesSlidingWindowSplit
Fixed-size sliding windows through time.

```python
from scitex.ml.classification import TimeSeriesSlidingWindowSplit

splitter = TimeSeriesSlidingWindowSplit(
    window_size=100,  # 100 samples for training
    step_size=20,     # Step 20 samples forward
    test_size=20      # 20 samples for testing
)
```

### TimeSeriesCalendarSplit
Calendar-based splitting (monthly, weekly, daily intervals).

```python
from scitex.ml.classification import TimeSeriesCalendarSplit

# Monthly splits
splitter = TimeSeriesCalendarSplit(
    interval='M',           # Monthly
    n_train_intervals=12,   # 12 months training
    n_test_intervals=1,     # 1 month testing
    gap_intervals=0,        # No gap
    step_intervals=1        # Step 1 month forward
)
```

## Timestamp Normalization

Handles various timestamp formats automatically:

```python
from scitex.ml.classification.time_series import normalize_timestamp

# Convert any format to standard string
normalized = normalize_timestamp("2023/01/15 14:30:00", return_as="str")
# Output: "2023-01-15 14:30:00.000000"

# Convert to datetime
dt = normalize_timestamp(1673794200, return_as="datetime")

# Convert to Unix timestamp
ts = normalize_timestamp("2023-01-15", return_as="unix")
```

## Usage with ClassificationReporter

All splitters integrate seamlessly with the unified ClassificationReporter:

```python
from scitex.ml.classification import ClassificationReporter, TimeSeriesCalendarSplit
from sklearn.ensemble import RandomForestClassifier
import pandas as pd

# Create timestamps
dates = pd.date_range('2023-01-01', '2023-12-31', freq='D')

# Initialize splitter
splitter = TimeSeriesCalendarSplit(interval='M', n_train_intervals=9)

# Initialize reporter
reporter = ClassificationReporter("./results")

# Cross-validation
for fold, (train_idx, test_idx) in enumerate(splitter.split(X, y, timestamps=dates)):
    # Train model
    model = RandomForestClassifier()
    model.fit(X[train_idx], y[train_idx])
    
    # Evaluate
    y_pred = model.predict(X[test_idx])
    y_proba = model.predict_proba(X[test_idx])
    
    # Report metrics
    reporter.calculate_metrics(
        y_true=y[test_idx],
        y_pred=y_pred,
        y_proba=y_proba,
        fold=fold
    )

# Save summary
reporter.save_summary()
```

## Production Considerations

### Data Requirements
- All splitters require temporal ordering via timestamps
- BlockingSplit requires group labels
- CalendarSplit works best with regular sampling intervals

### Performance
- All splitters are memory-efficient (yield indices, not data copies)
- Timestamp normalization handles timezone-aware and naive datetimes
- Robust to various timestamp formats (Unix, ISO, custom strings)

### Best Practices
1. Always validate temporal ordering before splitting
2. Use appropriate gap parameters to prevent leakage
3. Consider class imbalance when using stratification
4. For irregular sampling, consider aggregating to regular intervals

## Testing

Run module tests:
```bash
python -m pytest tests/test_time_series_cv.py
```

## Contributing

When adding new splitters:
1. Inherit from `sklearn.model_selection.BaseCrossValidator`
2. Implement `split()` and `get_n_splits()` methods
3. Add comprehensive docstrings with examples
4. Include in `__all__` export list
5. Add unit tests