# Classification Module Demo

This example project demonstrates the usage of SciTeX classification modules with organized output structure.

## Directory Structure

```
classification_demo/
├── data/                    # Generated synthetic datasets
├── scripts/                 # Example scripts
├── outputs/                 # Organized classification outputs
└── run_all_examples.py     # Main runner script
```

## Examples Included

### 1. **Single Task Classification** (`01_single_task_classification.py`)
- Binary classification with `SingleTaskClassificationReporter`
- Generates organized metrics, confusion matrices, and reports
- Output structure:
  ```
  outputs/single_task_classification/
  ├── metrics/
  │   └── fold_00/
  │       ├── classification_metrics.csv
  │       └── classification_report.txt
  ├── confusion_matrices/
  │   └── fold_00/
  │       └── confusion_matrix.csv
  └── predictions/
      └── fold_00/
          └── predictions.csv
  ```

### 2. **Multi-Task Classification** (`02_multi_task_classification.py`)
- Multiple classification tasks with `MultipleTasksClassificationReporter`
- Independent reporting for each task
- Output structure:
  ```
  outputs/multi_task_classification/
  ├── task1_binary/
  │   ├── metrics/
  │   ├── confusion_matrices/
  │   └── predictions/
  ├── task2_count/
  │   └── ...
  └── task3_dominant/
      └── ...
  ```

### 3. **Time Series Cross-Validation** (`03_time_series_cv.py`)
- `TimeSeriesBlockingSplit` for multiple subjects
- `TimeSeriesStratifiedSplit` for temporal data with class balance
- Prevents temporal data leakage
- Output structure:
  ```
  outputs/time_series_blocking/
  ├── metrics/
  │   ├── fold_00/
  │   ├── fold_01/
  │   └── fold_02/
  └── ...
  ```

## Running the Examples

### Run all examples:
```bash
python run_all_examples.py
```

### Run individual examples:
```bash
cd scripts
python 00_generate_data.py          # Generate datasets first
python 01_single_task_classification.py
python 02_multi_task_classification.py
python 03_time_series_cv.py
```

## Output Organization

The classification reporters automatically organize outputs in a hierarchical structure:

- **Metrics**: Classification metrics (accuracy, precision, recall, F1, etc.)
- **Confusion Matrices**: Detailed confusion matrices
- **Predictions**: Actual predictions with probabilities
- **Reports**: Human-readable classification reports

Each fold in cross-validation gets its own subdirectory, making it easy to:
- Track performance across folds
- Aggregate results
- Generate publication-ready tables
- Debug specific folds

## Key Features Demonstrated

1. **Automatic Output Organization**: No manual file management needed
2. **Multi-Task Support**: Independent tracking for multiple targets
3. **Time Series Validation**: Proper temporal splits without leakage
4. **Stratification**: Maintains class balance in splits
5. **Comprehensive Metrics**: All standard classification metrics included
6. **Export Formats**: CSV, text reports, and LaTeX-ready tables

## Dependencies

- scikit-learn
- pandas
- numpy
- scitex (with classification module)

## Notes

- All outputs are organized in the `outputs/` directory
- Each run clears previous outputs to avoid confusion
- The synthetic data is regenerated each time for consistency
- Check the generated CSV files for detailed metrics