# SciTeX Module Overview

## Core Modules

### 🔧 scitex.gen - General Utilities
**Purpose**: Environment setup and general utilities

**Key Functions**:
- `start()` - Initialize experiment environment
- `close()` - Clean shutdown
- `fix_seeds()` - Set random seeds
- `tee()` - Duplicate output streams

**Example**:
```python
CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.gen.start(sys, plt)
# ... your code ...
scitex.gen.close(CONFIG)
```

### 📁 scitex.io - Input/Output
**Purpose**: Universal file I/O with automatic format detection

**Key Functions**:
- `load()` - Load any file format
- `save()` - Save with auto directory creation
- `load_configs()` - Load YAML configurations
- `glob()` - Enhanced file pattern matching

**Supported Formats**:
- Data: CSV, JSON, YAML, Excel
- Scientific: NPY, NPZ, MAT, HDF5
- ML: PTH, PKL, JOBLIB
- Docs: TXT, MD, PDF, DOCX

**Example**:
```python
data = scitex.io.load("data.csv")
scitex.io.save(data, "output/results.json")
```

### 📊 scitex.plt - Enhanced Plotting
**Purpose**: Matplotlib wrapper with automatic data tracking

**Key Functions**:
- `subplots()` - Create tracked figure/axes
- `ax.set_xyt()` - Set xlabel, ylabel, title
- Color utilities and style management

**Features**:
- Automatic CSV export of plotted data
- Publication-ready defaults
- Integrated with scitex.io.save()

**Example**:
```python
fig, ax = scitex.plt.subplots()
ax.plot(x, y)
ax.set_xyt("Time (s)", "Amplitude", "Signal")
scitex.io.save(fig, "plot.png")  # Saves image + data
```

## Data Processing Modules

### 🔊 scitex.dsp - Digital Signal Processing
**Purpose**: Signal analysis and processing

**Key Functions**:
- `bandpass()`, `lowpass()`, `highpass()` - Filters
- `hilbert()` - Hilbert transform
- `psd()` - Power spectral density
- `pac()` - Phase-amplitude coupling
- `resample()` - Signal resampling

**Example**:
```python
filtered = scitex.dsp.bandpass(signal, low=1, high=50, fs=1000)
power = scitex.dsp.psd(filtered, fs=1000)
```

### 🐼 scitex.pd - Pandas Utilities
**Purpose**: Enhanced pandas operations

**Key Functions**:
- `round()` - Smart rounding
- `slice()` - Advanced DataFrame filtering
- `to_xyz()` - Coordinate conversions
- `merge_columns()` - Column operations

**Example**:
```python
df_rounded = scitex.pd.round(df, decimals=2)
subset = scitex.pd.slice(df, "column > 10")
```

### 📈 scitex.stats - Statistical Analysis
**Purpose**: Statistical tests and utilities

**Key Functions**:
- `corr_test()` - Correlation with p-values
- `p2stars()` - Convert p-values to stars
- `fdr_correction()` - Multiple comparison correction
- `describe()` - Enhanced descriptive stats

**Example**:
```python
result = scitex.stats.corr_test(x, y)
stars = scitex.stats.p2stars(result['p'])  # "**"
```

## Machine Learning Modules

### 🤖 scitex.ai - AI/ML Utilities
**Purpose**: Machine learning helpers

**Features**:
- Classification reporters
- Learning curve loggers
- Early stopping
- Metrics and losses

**Example**:
```python
reporter = scitex.ai.ClassificationReporter()
reporter.update(y_true, y_pred)
reporter.show()
```

### 🧠 scitex.nn - Neural Network Layers
**Purpose**: Custom PyTorch layers

**Layers**:
- Signal processing layers (Hilbert, PSD, etc.)
- Dropout variants
- Attention mechanisms

### 🔥 scitex.torch - PyTorch Utilities
**Purpose**: PyTorch helpers

**Functions**:
- Device management
- Tensor operations
- Model utilities

## Utility Modules

### 📂 scitex.path - Path Operations
**Purpose**: File path utilities

**Key Functions**:
- `find()` - Find files matching patterns
- `mk_spath()` - Make timestamped paths
- `get_spath()` - Get script output path
- `split()` - Enhanced path splitting

### 📝 scitex.str - String Utilities
**Purpose**: Text processing

**Key Functions**:
- `printc()` - Colored printing
- `print_block()` - Formatted blocks
- `grep()` - Text searching
- `gen_timestamp()` - Generate timestamps

**Example**:
```python
scitex.str.printc("Success!", c="green")
scitex.str.print_block("Section Title", char="=")
```

### 🎨 scitex.decorators - Function Decorators
**Purpose**: Enhance functions

**Decorators**:
- `@cache` - Cache results
- `@numpy_fn` - Convert args to numpy
- `@torch_fn` - Convert args to torch
- `@deprecated` - Mark deprecated

## Specialized Modules

### 🗄️ scitex.db - Database Operations
**Purpose**: Database interfaces

**Supports**:
- SQLite3
- PostgreSQL

### 🌐 scitex.web - Web Utilities
**Purpose**: Web scraping and APIs

**Functions**:
- `search_pubmed()` - PubMed search
- `summarize_url()` - Extract page content

### 🧬 scitex.resource - System Resources
**Purpose**: Monitor system resources

**Functions**:
- `get_specs()` - System specifications
- `limit_RAM()` - Limit memory usage

## Module Selection Guide

**For General Scripts**: Start with `gen`, `io`, `plt`

**For Data Analysis**: Add `pd`, `stats`, `dsp`

**For Machine Learning**: Include `ai`, `nn`, `torch`

**For File Management**: Use `path`, `str`

**For Specialized Tasks**: Explore `db`, `web`, `resource`

## Best Practices

1. **Import only what you need**:
```python
from scitex.io import load, save  # Good
import scitex  # Also fine for exploring
```

2. **Use module aliases for clarity**:
```python
import scitex.dsp as dsp
filtered = dsp.bandpass(signal, 1, 50)
```

3. **Combine modules effectively**:
```python
# Load → Process → Visualize → Save
data = scitex.io.load("data.csv")
results = scitex.stats.describe(data)
fig = scitex.plt.plot_results(results)
scitex.io.save(fig, "analysis.png")
```

## Next Steps

- Try [Common Workflows](04_common_workflows.md)
- Read detailed module guides in `docs/modules/`
- Explore module-specific examples