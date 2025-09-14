# PAC Classification with SciTeX

This directory contains scripts for PAC (Phase-Amplitude Coupling) classification using the new SciTeX classification system.

## Quick Start

The new system is already exposed and ready to use! You can import it directly:

```python
from scitex.ai.classification import (
    SingleClassificationReporter,    # Enhanced v2 reporter
    CrossValidationExperiment,       # Full CV workflow
    quick_experiment                 # One-line experiments
)
```

## Usage Examples

### 1. Simplest - One-Line Classification

```python
from scitex.ai.classification import quick_experiment
from sklearn.svm import SVC

# Run complete experiment with one line
results = quick_experiment(
    X, y,
    model=SVC(probability=True),
    name="pac_classification"
)
```

### 2. Standard - Cross-Validation with Tracking

```python
from scitex.ai.classification import CrossValidationExperiment

# Create experiment
experiment = CrossValidationExperiment(
    name="pac_analysis",
    model_fn=lambda: SVC(probability=True),
    save_models=True
)

# Track hyperparameters
experiment.set_hyperparameters(C=1.0, kernel='rbf')

# Run with feature names
results = experiment.run(
    X, y,
    feature_names=['pac_1', 'pac_2', ...],
    class_names=['Low', 'Medium', 'High']
)
```

### 3. Custom - Full Control with Reporter

```python
from scitex.ai.classification import SingleClassificationReporter

# Initialize reporter
reporter = SingleClassificationReporter(
    name="pac_custom",
    required_metrics=['balanced_accuracy', 'mcc', 'roc_auc']
)

# For each fold
for fold_idx in range(n_folds):
    reporter.start_fold(fold_idx)
    
    # Train and predict...
    
    # Calculate metrics (auto-saved)
    reporter.calc_balanced_accuracy(y_test, y_pred)
    reporter.calc_mcc(y_test, y_pred)
    reporter.calc_roc_auc(y_test, y_proba)
    
    # Add custom PAC metrics
    reporter.add(pac_metrics, f"custom/pac_fold_{fold_idx:02d}.json")
    
    reporter.end_fold(fold_idx)

# Generate reports
paths = reporter.save()
```

## Running the PAC Classification Script

The `classify_with_scitex.py` script provides multiple modes:

### Simple Mode (Quickest)
```bash
python classify_with_scitex.py --mode simple --model svm
```

### Advanced Mode (More Control)
```bash
python classify_with_scitex.py --mode advanced --model rf --preprocess
```

### Custom Mode (Maximum Flexibility)
```bash
python classify_with_scitex.py --mode custom --output-dir ./my_results
```

### Model Comparison
```bash
python classify_with_scitex.py --mode compare
```

## Output Structure

All results are saved in organized directories:

```
results/pac_classification_TIMESTAMP/
├── metrics/              # All calculated metrics
│   ├── fold_00/         # Per-fold metrics
│   │   ├── balanced_accuracy.json
│   │   ├── mcc.json
│   │   ├── confusion_matrix.npy
│   │   └── roc_auc.json
│   └── fold_01/
├── plots/               # Generated visualizations
│   ├── fold_00/
│   │   ├── confusion_matrix.jpg
│   │   ├── roc_curve.jpg
│   │   └── pr_curve.jpg
├── models/              # Saved models (optional)
├── paper_export/        # Publication-ready files
│   ├── summary_table.csv
│   ├── summary_table.tex
│   └── raw_results.json
├── report.md            # Main report
├── summary_table.csv    # Cross-fold summary
└── validation_report.json  # Completeness check
```

## Key Features

1. **Automatic Output Directory**: Creates timestamped directories automatically
2. **Path-Based Organization**: `reporter.add(obj, "path/to/file.ext")`
3. **Validation**: Checks for required metrics completeness
4. **Publication Export**: LaTeX tables and formatted CSVs
5. **Hyperparameter Tracking**: Automatic logging of model parameters

## Current Status

✅ **The new system is fully exposed and functional!**

- All metrics are calculated and saved correctly
- Files are organized in subdirectories
- Reports are generated automatically
- The system validates completeness

Note: The summary statistics aggregation is still being refined, but all individual metrics are saved correctly in the `metrics/` directory.

## Tips

1. **For Quick Experiments**: Use `quick_experiment()` function
2. **For Research**: Use `CrossValidationExperiment` class
3. **For Custom Workflows**: Use `SingleClassificationReporter` directly
4. **Disable Plotting**: Set `plot=False` if visualization libraries cause issues
5. **Check Metrics**: All metrics are in `results/*/metrics/fold_*/`

## Next Steps

To use with real PAC data:

1. Replace the synthetic data loading in `load_pac_data()`
2. Add PAC-specific preprocessing in `preprocess_features()`
3. Add custom PAC metrics (e.g., coupling strength, peak frequencies)
4. Integrate with your existing PAC analysis pipeline