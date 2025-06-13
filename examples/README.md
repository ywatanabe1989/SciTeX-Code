# SciTeX Examples

This directory contains practical examples demonstrating how to use the scitex framework effectively.

## Structure

The examples are organized to mirror the scitex module structure:

```
examples/
├── scitex/
│   ├── io/           # File I/O examples
│   ├── gen/          # Environment setup examples
│   ├── plt/          # Enhanced plotting examples
│   ├── pd/           # Pandas utilities examples
│   ├── dsp/          # Digital signal processing examples
│   ├── stats/        # Statistical analysis examples
│   ├── ai/           # AI/ML examples
│   ├── nn/           # Neural network examples
│   ├── db/           # Database examples
│   └── workflows/    # Complete workflow examples
└── README.md         # This file
```

## Running Examples

All examples can be run directly from the project root:

```bash
# Basic file operations
python examples/scitex/io/basic_file_operations.py

# Complete experiment workflow
python examples/scitex/gen/experiment_workflow.py

# Enhanced plotting capabilities
python examples/scitex/plt/enhanced_plotting.py

# Pandas DataFrame operations
python examples/scitex/pd/dataframe_operations.py

# Digital signal processing
python examples/scitex/dsp/signal_processing.py

# Statistical analysis
python examples/scitex/stats/statistical_analysis.py

# Machine learning workflow
python examples/scitex/ai/machine_learning_workflow.py

# Neural network layers
python examples/scitex/nn/neural_network_layers.py

# Database operations
python examples/scitex/db/database_operations.py

# Complete scientific pipeline
python examples/scitex/workflows/scientific_data_pipeline.py
```

## Example Descriptions

### 1. `io/basic_file_operations.py`
Demonstrates fundamental file I/O operations:
- Loading and saving various file formats (numpy, pandas, json, yaml, text)
- Automatic directory creation
- Working with compressed data
- Handling collections and nested structures

### 2. `gen/experiment_workflow.py`
Shows a complete scientific experiment workflow:
- Setting up reproducible environment with scitex.gen.start
- Automatic logging and output management
- Random seed control for reproducibility
- Generating synthetic data and analysis
- Creating visualizations and reports
- Proper cleanup with scitex.gen.close

### 3. `plt/enhanced_plotting.py`
Illustrates advanced plotting features:
- Using scitex.plt.subplots for automatic data tracking
- Multi-panel figures with different plot types
- Statistical visualizations with error bars
- Custom styling and formatting
- Automatic CSV export of plotted data

### 4. `pd/dataframe_operations.py`
Demonstrates pandas utility functions:
- DataFrame creation and type conversion with force_df
- Column operations (melt, merge, find)
- Advanced filtering and slicing with conditions
- Type conversions and data cleaning
- Coordinate transformations (xyz format)
- Missing value handling and interpolation

### 5. `dsp/signal_processing.py`
Shows digital signal processing capabilities:
- Signal filtering (bandpass, lowpass, highpass)
- Power Spectral Density (PSD) analysis
- Time-frequency analysis with wavelets
- Hilbert transform for phase and amplitude
- Phase-Amplitude Coupling (PAC) analysis
- Multi-channel signal processing
- Signal resampling and normalization

### 6. `stats/statistical_analysis.py`
Covers statistical analysis workflows:
- Descriptive statistics with NaN handling
- Correlation analysis (Pearson, Spearman, partial)
- Statistical tests (Brunner-Munzel, t-test)
- Multiple comparison corrections (Bonferroni, FDR)
- P-value formatting and visualization
- Outlier detection (Smirnov-Grubbs)
- Complete analysis pipeline example

### 7. `ai/machine_learning_workflow.py`
Demonstrates machine learning capabilities:
- Setting up reproducible ML experiments
- Training multiple classifiers (RF, XGBoost, SVM, LR)
- Model evaluation and comparison
- Classification reporting with detailed metrics
- Feature importance analysis
- Confusion matrix visualization
- Comprehensive ML report generation

### 8. `nn/neural_network_layers.py`
Demonstrates SciTeX neural network layers:
- Signal processing layers (Filters, Hilbert, PSD, Wavelet)
- Data augmentation layers (ChannelGainChanger, FreqGainChanger, SwapChannels)
- Analysis layers (PAC, ModulationIndex)
- Complete model integration with PyTorch
- Custom layer parameters and learning
- Visualization of layer outputs
- Multi-channel signal processing in neural networks

### 9. `db/database_operations.py`
Shows comprehensive database operations:
- SQLite database creation and connection
- Table creation with foreign keys
- CRUD operations (Create, Read, Update, Delete)
- Efficient batch operations
- NumPy array storage as BLOBs with metadata
- Transaction management for data integrity
- CSV import/export functionality
- Database maintenance (backup, optimization)
- Complex queries with joins
- Index creation for performance

### 10. `workflows/scientific_data_pipeline.py`
Shows a complete end-to-end scientific workflow:
- Multi-module integration (gen, io, pd, dsp, stats, plt)
- Synthetic physiological data generation
- Signal preprocessing and filtering
- Feature extraction from time-series data
- Statistical analysis with multiple comparisons
- Time-frequency analysis
- Automated report generation
- Publication-ready visualizations

## Key Features Demonstrated

1. **Automatic Output Management**: All examples save outputs to organized directories
2. **Data Tracking**: Plots automatically export their data as CSV files
3. **Reproducibility**: Examples show how to set random seeds and track experiments
4. **Error Handling**: Examples include proper try-finally blocks where appropriate
5. **Documentation**: Each example is thoroughly commented

## Output Structure

After running the examples, you'll find outputs organized as:

```
output/
├── arrays/           # NumPy arrays and compressed data
├── dataframes/       # CSV files from pandas DataFrames
├── configs/          # JSON and YAML configuration files
├── reports/          # Text and markdown reports
├── plots/            # PNG images AND their corresponding CSV data
└── collections/      # Combined datasets
```

## Tips for Using Examples

1. **Start Simple**: Begin with `basic_file_operations.py` to understand core concepts
2. **Check Outputs**: Always examine the generated files to understand what scitex creates
3. **Read Comments**: Examples include detailed comments explaining each step
4. **Modify and Experiment**: Feel free to modify examples for your needs
5. **Use as Templates**: These examples can serve as templates for your own scripts

## Integration with Your Projects

To use these patterns in your own work:

```python
# Minimal usage
import scitex
data = scitex.io.load("your_data.csv")
scitex.io.save(results, "output.json")

# Full workflow
import sys
import matplotlib.pyplot as plt
import scitex

CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.gen.start(sys, plt)
# Your experiment code here
scitex.gen.close(CONFIG)
```

## Next Steps

After exploring these examples:
1. Read the full documentation in `docs/scitex_guidelines/`
2. Check out the module-specific guides
3. Explore the test files for more usage patterns
4. Start building your own projects with scitex!

## Contributing

If you create useful examples, consider contributing them back to the project!