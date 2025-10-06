# SciTeX Classification Module

A comprehensive classification module for scientific machine learning experiments with standardized reporting, validation, and publication-ready outputs.

## Overview

The classification module provides:
- **Modular reporter utilities** for metric calculation and storage
- **Single and multi-task classification reporters** with automatic file organization
- **Validation utilities** to ensure completeness and scientific rigor
- **Publication-ready exports** in multiple formats (CSV, LaTeX, Markdown)
- **Decoupled architecture** without hard dependencies on scitex.io

## Directory Structure

```
src/scitex/ai/classification/
├── __init__.py
├── README.md (this file)
├── _Classifiers.py              # Classifier implementations
├── Classifier.py          # Server for classifier services
├── _ClassificationReporter.py   # Base reporter class
├── _SingleClassificationReporter.py    # Single-task reporter
├── _MultiClassificationReporter.py     # Multi-task reporter
└── reporter_utils/              # Modular utilities
    ├── __init__.py
    ├── metrics.py               # Pure metric calculations
    ├── storage.py               # Standalone storage (no scitex.io dependency)
    ├── data_models.py           # Type-safe data models
    ├── validation.py            # Validation and completeness checks
    ├── aggregation.py           # Cross-fold aggregation
    └── reporting.py             # Report generation utilities
```

## Quick Start

### Basic Usage

```python
from scitex.ai.classification.reporter_utils import (
    calc_bacc,
    calc_mcc,
    MetricStorage,
    create_summary_table,
    generate_markdown_report
)

# Calculate metrics
ba = calc_bacc(y_true, y_pred, fold=0)
mcc = calc_mcc(y_true, y_pred, fold=0)

# Store results
storage = MetricStorage("./results")
storage.save(ba, "metrics/fold_00/balanced_accuracy.json")
storage.save(mcc, "metrics/fold_00/mcc.json")

# Create summary
summary_df = create_summary_table(fold_results, include_stats=True)
storage.save(summary_df, "summary.csv")
```

### Using SingleClassificationReporter

```python
from scitex.ai.classification import SingleClassificationReporter

# Initialize reporter
reporter = SingleClassificationReporter(
    name="my_experiment",
    output_dir="./results"
)

# For each fold
for fold in range(n_folds):
    # Train model and get predictions
    y_pred, y_proba = train_and_predict(...)
    
    # Calculate and save metrics (automatically organized)
    reporter.calc_bacc(y_true, y_pred, fold)
    reporter.calc_mcc(y_true, y_pred, fold)
    reporter.calc_conf_mat(y_true, y_pred, fold)
    
    # Add custom objects with path-based API
    reporter.add(fig, f"plots/roc_curve_fold_{fold:02d}.jpg")
    reporter.add(model_params, f"models/params_fold_{fold:02d}.json")

# Save all results
reporter.save()

# Generate report
reporter.generate_report()
```

## Key Features

### 1. Modular Metric Calculations

All metric calculations are pure functions without side effects:

```python
from scitex.ai.classification.reporter_utils import calc_bacc

result = calc_bacc(y_true, y_pred, fold=0)
# Returns: {'metric': 'balanced_accuracy', 'value': 0.85, 'fold': 0}
```

### 2. Decoupled Storage

Storage utilities work independently without scitex.io dependencies:

```python
from scitex.ai.classification.reporter_utils import MetricStorage

storage = MetricStorage("./results")

# Automatic format detection from extension
storage.save(metric_dict, "metrics/accuracy.json")  # JSON
storage.save(dataframe, "tables/results.csv")       # CSV
storage.save(confusion_matrix, "arrays/cm.npy")     # NumPy
storage.save(figure, "plots/roc.jpg")               # Image
```

### 3. Validation and Completeness Checking

Ensure all required metrics are present and valid:

```python
from scitex.ai.classification.reporter_utils import MetricValidator

validator = MetricValidator(["balanced_accuracy", "mcc", "roc_auc"])
report = validator.validate_all_folds(fold_results)
validator.print_summary()
```

### 4. Publication-Ready Exports

Generate tables and reports for academic papers:

```python
from scitex.ai.classification.reporter_utils import export_for_paper

paths = export_for_paper(results, "./paper_exports")
# Creates:
# - summary_table.csv (with mean ± std format)
# - summary_table.tex (LaTeX table)
# - raw_results.json (all data)
# - README.md (usage instructions)
```

### 5. Cross-Fold Aggregation

Aggregate metrics across folds with statistics:

```python
from scitex.ai.classification.reporter_utils import (
    aggregate_fold_metrics,
    create_summary_table
)

# Aggregate metrics
aggregated = aggregate_fold_metrics(fold_results)

# Create summary table with statistics
summary_df = create_summary_table(fold_results, include_stats=True)
```

## API Design Philosophy

### Path-Based File Organization

The module uses an intuitive path-based API for file organization:

```python
# Instead of complex routing logic:
# reporter.add(obj, name="accuracy", type="metric", fold=0)

# Simply specify the path:
reporter.add(obj, "metrics/fold_00/accuracy.json")
```

### Type Detection from Extensions

File types are automatically determined from extensions:
- `.json` → JSON format (for scalars and metadata)
- `.csv` → CSV format (for DataFrames)
- `.npy` → NumPy binary (for arrays)
- `.jpg`, `.png` → Image formats (for figures)

### Standardization for Scientific Requirements

The module enforces strict standardization:
- Required metrics validation
- Consistent file organization
- Reproducible outputs
- Complete metadata tracking

## Testing

Run the comprehensive test suite:

```bash
python ./.dev/test_reporter_utils/test_reporter_system.py
```

The test suite validates:
- Metric calculations
- Storage functionality
- Validation logic
- Aggregation utilities
- Report generation
- Full workflow integration

## Migration from Previous Versions

If migrating from older reporter implementations:

1. **File organization**: Files are now organized in subdirectories by type
2. **API change**: Use path-based `add()` method instead of name-based
3. **Scalars**: Now saved as JSON instead of pickle for readability
4. **Metrics**: Methods are now instance methods with auto-saving

## Examples

See `./.dev/test_reporter_utils/` for complete working examples including:
- Basic metric calculations
- Full cross-validation workflow
- Publication-ready exports
- Custom metric integration

## Dependencies

Core dependencies:
- `numpy`: Numerical computations
- `pandas`: Data manipulation
- `scikit-learn`: ML metrics
- `matplotlib`: Plotting (optional)

The module is designed to work without scitex.io.save, making it portable and reusable.

## Contributing

When adding new features:
1. Add pure calculation functions to `metrics.py`
2. Keep storage logic in `storage.py`
3. Add validation rules to `validation.py`
4. Update aggregation logic if needed
5. Add tests to the test suite

## License

Part of the SciTeX project. See main project license.