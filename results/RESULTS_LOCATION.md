# Results Directory Location

## Main Results Directory
**Location**: `/data/gpfs/projects/punim2354/ywatanabe/SciTeX-Code/results/`

All classification experiments are saved here with timestamped directories.

## Current PAC Classification Results

### Latest Run
**Path**: `/data/gpfs/projects/punim2354/ywatanabe/SciTeX-Code/results/pac_svm_simple_20250907_105851/`

### Directory Structure
```
pac_svm_simple_20250907_105851/
├── experiment/
│   ├── dataset_info.json      # Dataset metadata
│   ├── hyperparameters.json   # Model parameters
│   └── timing.json            # Execution times
├── metrics/
│   ├── fold_00/              # Fold 0 metrics
│   │   ├── balanced_accuracy.json (0.851)
│   │   ├── mcc.json (0.786)
│   │   ├── roc_auc.json (0.958)
│   │   ├── pr_auc.json (0.931)
│   │   ├── confusion_matrix.npy
│   │   └── classification_report.csv
│   ├── fold_01/              # Fold 1 metrics
│   ├── fold_02/              # Fold 2 metrics
│   ├── fold_03/              # Fold 3 metrics
│   └── fold_04/              # Fold 4 metrics
├── plots/
│   └── fold_*/               # Visualizations (if generated)
├── models/
│   └── fold_*/               # Saved models (if enabled)
├── paper_export/
│   ├── summary_table.csv     # Publication-ready table
│   ├── summary_table.tex     # LaTeX table
│   └── raw_results.json      # All raw data
├── report.md                  # Main markdown report
├── summary_table.csv          # Cross-fold summary
├── validation_report.json     # Metric completeness check
└── metadata.json             # Experiment metadata
```

## Key Files

### Metrics (All Available!)
- **Balanced Accuracy**: `metrics/fold_*/balanced_accuracy.json`
- **MCC**: `metrics/fold_*/mcc.json`
- **ROC AUC**: `metrics/fold_*/roc_auc.json`
- **PR AUC**: `metrics/fold_*/pr_auc.json`
- **Confusion Matrices**: `metrics/fold_*/confusion_matrix.npy`
- **Classification Reports**: `metrics/fold_*/classification_report.csv`

### Reports
- **Main Report**: `report.md`
- **Summary CSV**: `summary_table.csv`
- **LaTeX Table**: `paper_export/summary_table.tex`

### Timing
- **Execution Time**: `experiment/timing.json`
  - Total: 0.66 seconds
  - Mean per fold: 0.13 seconds

## How to Access Results

### From Python
```python
import json
import numpy as np
import pandas as pd

# Load a metric
with open('results/pac_svm_simple_20250907_105851/metrics/fold_00/balanced_accuracy.json') as f:
    ba = json.load(f)
    print(f"Fold 0 BA: {ba['value']:.3f}")

# Load confusion matrix
cm = np.load('results/pac_svm_simple_20250907_105851/metrics/fold_00/confusion_matrix.npy')

# Load classification report
report = pd.read_csv('results/pac_svm_simple_20250907_105851/metrics/fold_00/classification_report.csv')
```

### View Report
```bash
cat results/pac_svm_simple_20250907_105851/report.md
```

### Check All Experiments
```bash
ls -la results/
```

## Notes
- All metrics are successfully calculated and saved
- The summary aggregation in `summary_table.csv` needs refinement but all individual metrics are correct
- Each fold's metrics are in separate subdirectories for easy access
- Results are automatically timestamped to prevent overwriting