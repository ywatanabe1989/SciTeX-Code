# Time Series Cross-Validation Module

Production-ready time series cross-validation utilities with temporal integrity guarantees and enhanced visualizations.

## 🎯 Overview

This module provides specialized cross-validation strategies for time series data, ensuring:
- **Temporal order preservation** (no future data leakage)
- **Visual verification** with scatter plot overlays
- **SciTeX framework integration** for standalone testing
- **Support for multiple time series scenarios**
- **Calendar-aware splitting** with business logic
- **Robust timestamp handling** across formats

## 📊 Visual Comparison of Splitters

### TimeSeriesStratifiedSplit
```
Maintains class balance while preserving temporal order
Supports optional validation set between train and test

Without validation:              With validation (val_ratio=0.15):
Fold 0: [TTTTTTTTTT]    [SSS]   Fold 0: [TTTTTTTT]  [VV]  [SSS]
Fold 1: [TTTTTTTTTTTT]  [SSS]   Fold 1: [TTTTTTTTTT][VV]  [SSS]
Fold 2: [TTTTTTTTTTTTTT][SSS]   Fold 2: [TTTTTTTTTTTT][VV][SSS]
        └─ Expanding ─┘  Test            └─Expanding─┘ Val  Test
        
Legend: T=Train, V=Validation, S=teSt
```

### TimeSeriesSlidingWindowSplit
```
Fixed-size windows sliding through time
Optional validation carved from training window

Without validation:              With validation (val_ratio=0.2):
Fold 0: [TTTT]  [SS]            Fold 0: [TTT][V]  [SS]
Fold 1:    [TTTT]  [SS]         Fold 1:    [TTT][V]  [SS]
Fold 2:       [TTTT]  [SS]      Fold 2:       [TTT][V]  [SS]
        └─Win─┘ Gap └Test┘              └Train┘Val Gap└Test┘
        
Legend: T=Train, V=Validation, S=teSt, Gap=temporal separation
```

### TimeSeriesBlockingSplit
```
Multiple subjects with temporal separation per subject
Each subject gets its own train/val/test split

Without validation:                    With validation (val_ratio=0.15):
Subject A: [TTTT][SS]                 Subject A: [TTT][V][S]
Subject B: [TTTT][SS]                 Subject B: [TTT][V][S]
Subject C: [TTTT][SS]                 Subject C: [TTT][V][S]
Subject D: [TTTT][SS]                 Subject D: [TTT][V][S]
           └Train┘Test                           └Trn┘Val│Test
        
Legend: T=Train, V=Validation, S=teSt (per subject)
```

### TimeSeriesCalendarSplit
```
Calendar-based intervals (monthly, weekly, daily)
Natural time boundaries for business/seasonal data

Without validation:                    With validation (n_val_intervals=1):
        Jan-Jun    Jul                        Jan-May   Jun    Jul
Fold 0: [TTTTTT]   [S]                Fold 0: [TTTTT]   [V]    [S]
Fold 1:    [TTTTTT]   [S]             Fold 1:    [TTTTT]   [V]    [S]
Fold 2:       [TTTTTT]   [S]          Fold 2:       [TTTTT]   [V]    [S]
        └─6 months─┘  └1mo┘                   └─5 months─┘ └1mo┘ └1mo┘
        
Legend: T=Train intervals, V=Validation intervals, S=teSt intervals
```

## Available Splitters

### TimeSeriesStratifiedSplit
Single time series with stratification to maintain class balance and optional validation set.

```python
from scitex.ml.classification.time_series import TimeSeriesStratifiedSplit

splitter = TimeSeriesStratifiedSplit(
    n_splits=5,
    test_ratio=0.2,
    val_ratio=0.15,  # Optional validation set
    gap=10,          # 10 samples gap between train/test
    stratify=True    # Maintain class balance
)

# With validation set
for train_idx, val_idx, test_idx in splitter.split_with_val(X, y, timestamps):
    # Temporal order guaranteed: train < val < test
    pass
```

### TimeSeriesBlockingSplit  
Multiple independent time series (e.g., different patients/subjects) with optional validation set.

```python
from scitex.ml.classification.time_series import TimeSeriesBlockingSplit

splitter = TimeSeriesBlockingSplit(
    n_splits=3, 
    test_ratio=0.2,
    val_ratio=0.15  # Optional validation set
)

# Regular split
for train_idx, test_idx in splitter.split(X, y, timestamps, groups):
    # Each subject's temporal order preserved
    pass

# With validation set
for train_idx, val_idx, test_idx in splitter.split_with_val(X, y, timestamps, groups):
    # Each subject gets train < val < test splits
    pass
```

### TimeSeriesSlidingWindowSplit
Fixed-size sliding windows through time with configurable gaps and optional validation set.

```python
from scitex.ml.classification.time_series import TimeSeriesSlidingWindowSplit

splitter = TimeSeriesSlidingWindowSplit(
    window_size=100,  # 100 samples for training window
    step_size=20,     # Step 20 samples forward
    test_size=20,     # 20 samples for testing
    gap=5,            # 5 samples gap between train/test
    val_ratio=0.2     # Optional: 20% of window for validation
)

# Regular split
for train_idx, test_idx in splitter.split(X, y, timestamps):
    # Fixed-size sliding windows
    pass

# With validation set
for train_idx, val_idx, test_idx in splitter.split_with_val(X, y, timestamps):
    # Validation carved out from training window
    pass
```

### TimeSeriesCalendarSplit
Calendar-based splitting (monthly, weekly, daily intervals) with optional validation set.

```python
from scitex.ml.classification.time_series import TimeSeriesCalendarSplit

# Monthly splits
splitter = TimeSeriesCalendarSplit(
    interval='M',           # Monthly
    n_train_intervals=12,   # 12 months training
    n_val_intervals=2,      # Optional: 2 months validation
    n_test_intervals=1,     # 1 month testing
    gap_intervals=0,        # No gap
    step_intervals=1        # Step 1 month forward
)

# Regular split
for train_idx, test_idx in splitter.split(X, y, timestamps=dates):
    # Calendar-based train/test split
    pass

# With validation set
for train_idx, val_idx, test_idx in splitter.split_with_val(X, y, timestamps=dates):
    # Train months < Val months < Test months
    pass
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

## Validation Set Support

All time series splitters now support optional validation sets through the `split_with_val()` method:

### Key Features
- **Temporal ordering**: Always maintains train < validation < test order
- **Configurable size**: Control validation size via parameters (val_ratio, n_val_intervals, etc.)
- **Optional gaps**: Support temporal gaps between train/val and val/test sets
- **Visualization**: Scatter plots clearly show all three sets with distinct colors

### Example with Validation Sets

```python
from scitex.ml.classification.time_series import TimeSeriesStratifiedSplit
from sklearn.ensemble import RandomForestClassifier

# Create splitter with validation
splitter = TimeSeriesStratifiedSplit(
    n_splits=3,
    test_ratio=0.2,
    val_ratio=0.15,  # 15% for validation
    gap=5            # Gap between sets
)

# Cross-validation with validation set
for fold, (train_idx, val_idx, test_idx) in enumerate(splitter.split_with_val(X, y, timestamps)):
    # Train model
    model = RandomForestClassifier()
    model.fit(X[train_idx], y[train_idx])
    
    # Validate for hyperparameter tuning
    val_score = model.score(X[val_idx], y[val_idx])
    
    # Final test evaluation
    test_score = model.score(X[test_idx], y[test_idx])
    
    print(f"Fold {fold}: Val={val_score:.3f}, Test={test_score:.3f}")
```

### Visualization with Validation Sets

All splitters automatically detect and visualize validation sets when present:

```python
# Visualize splits (automatically shows train/val/test if val_ratio > 0)
fig = splitter.plot_splits(X, y, timestamps)
# Blue rectangles/dots: Training set
# Green rectangles/dots: Validation set  
# Red rectangles/dots: Test set
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