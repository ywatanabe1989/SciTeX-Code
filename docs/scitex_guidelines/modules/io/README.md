# scitex.io Module Documentation

## Overview

The `scitex.io` module provides a unified interface for file input/output operations with automatic format detection, directory management, and enhanced functionality for scientific computing workflows.

## Core Philosophy

- **One function to load any file**: `scitex.io.load()`
- **One function to save any data**: `scitex.io.save()`
- **Automatic directory creation**
- **Format detection from extensions**
- **Consistent error handling**

## Key Functions

### scitex.io.load()
Universal file loader with automatic format detection.

```python
scitex.io.load(lpath: str, show: bool = False, verbose: bool = False, **kwargs) -> Any
```

#### Parameters
- `lpath` (str): Path to the file to load
- `show` (bool): Display information during loading
- `verbose` (bool): Print detailed output
- `**kwargs`: Format-specific options passed to underlying loaders

#### Supported Formats

**Data Formats**
- `.csv` - CSV files (returns pandas.DataFrame)
- `.tsv` - Tab-separated values (returns pandas.DataFrame)
- `.json` - JSON files (returns dict/list)
- `.yaml`, `.yml` - YAML files (returns dict/list)

**Scientific Formats**
- `.npy` - NumPy arrays
- `.npz` - Compressed NumPy arrays
- `.mat` - MATLAB files
- `.hdf5` - HDF5 files
- `.con` - Connectivity matrices

**Machine Learning**
- `.pth`, `.pt` - PyTorch models/tensors
- `.pkl` - Pickle files
- `.joblib` - Joblib files

**Documents**
- `.txt`, `.log`, `.event` - Text files (returns string)
- `.md` - Markdown files (returns string)
- `.docx` - Word documents
- `.pdf` - PDF files (text extraction)
- `.xml` - XML files

**Images**
- `.jpg`, `.jpeg`, `.png`, `.tiff`, `.tif` - Image files (returns PIL.Image or numpy array)

**Spreadsheets**
- `.xls`, `.xlsx`, `.xlsm`, `.xlsb` - Excel files (returns pandas.DataFrame)

**EEG Data**
- `.vhdr`, `.vmrk`, `.edf`, `.bdf`, `.gdf`, `.cnt`, `.egi`, `.eeg`, `.set`

**Database**
- `.db` - SQLite3 databases

#### Examples
```python
# Basic usage
data = scitex.io.load("data.csv")
config = scitex.io.load("config.yaml")
model = scitex.io.load("model.pth")

# With options
df = scitex.io.load("data.csv", encoding="utf-8")
model = scitex.io.load("model.pth", map_location="cpu")
```

### scitex.io.save()
Universal file saver with automatic directory creation.

```python
scitex.io.save(obj: Any, spath: str, verbose: bool = False, **kwargs) -> str
```

#### Parameters
- `obj`: Object to save
- `spath` (str): Save path (format detected from extension)
- `verbose` (bool): Print save information
- `**kwargs`: Format-specific options

#### Features
- **Automatic directory creation**: Parent directories created as needed
- **Symlink creation**: Creates symlinks for easy access
- **Plot data tracking**: When saving matplotlib figures, also saves the plotted data

#### Examples
```python
# Save various formats
scitex.io.save(df, "results/data.csv")
scitex.io.save(config, "config.yaml")
scitex.io.save(model.state_dict(), "model.pth")

# Save with compression
scitex.io.save(large_array, "data.npy", compress=True)

# Save figure with data
fig, ax = plt.subplots()
ax.plot(x, y)
scitex.io.save(fig, "plot.png")  # Also creates plot.png.csv
```

### scitex.io.load_configs()
Load all YAML configuration files from a directory.

```python
scitex.io.load_configs(IS_DEBUG: bool = False, _path: str = None) -> DotDict
```

#### Features
- Loads all `.yaml` files from `./config/` by default
- Merges configurations into a single DotDict
- Supports f-string variable resolution
- Dot-notation access to nested values

#### Example
```python
# config/model.yaml
model:
  name: ResNet
  layers: 50

# config/training.yaml  
training:
  epochs: 100
  batch_size: 32

# In Python
CONFIG = scitex.io.load_configs()
print(CONFIG.model.name)  # "ResNet"
print(CONFIG.training.epochs)  # 100
```

### scitex.io.glob()
Enhanced file pattern matching.

```python
scitex.io.glob(expression: str, verbose: bool = False) -> List[str]
```

#### Examples
```python
# Find all CSV files
csv_files = scitex.io.glob("./data/*.csv")

# Recursive search
all_results = scitex.io.glob("./experiments/**/results.json")

# Multiple patterns
files = scitex.io.glob("./data/*.{csv,xlsx,json}")
```

### scitex.io.find_latest()
Find the most recently modified file matching a pattern.

```python
scitex.io.find_latest(pattern: str) -> str
```

#### Example
```python
# Get latest checkpoint
latest_checkpoint = scitex.io.find_latest("./checkpoints/*.pth")

# Get latest log file
latest_log = scitex.io.find_latest("./logs/*.log")
```

## Advanced Features

### Path Handling
All paths in scitex.io are automatically cleaned and normalized:
- Expands user paths (`~` → `/home/user`)
- Resolves relative paths
- Handles environment variables

### Error Handling
scitex.io provides helpful error messages:
```python
try:
    data = scitex.io.load("nonexistent.csv")
except FileNotFoundError as e:
    # Error: ./nonexistent.csv not found.
```

### Format-Specific Options

#### CSV Options
```python
# Custom delimiter
df = scitex.io.load("data.tsv", delimiter="\t")

# Save without index
scitex.io.save(df, "output.csv", index=False)
```

#### PyTorch Options
```python
# Load to specific device
model = scitex.io.load("model.pth", map_location="cuda:0")

# Save with compression
scitex.io.save(state_dict, "model.pth", _use_new_zipfile_serialization=True)
```

#### Image Options
```python
# Load as numpy array
img_array = scitex.io.load("image.png", as_numpy=True)

# Save with quality
scitex.io.save(img, "output.jpg", quality=95)
```

## Best Practices

### DO ✅
```python
# Use relative paths
data = scitex.io.load("./data/file.csv")

# Let scitex create directories
scitex.io.save(results, "./output/results/data.csv")

# Use format-appropriate options
model = scitex.io.load("model.pth", map_location="cpu")
```

### DON'T ❌
```python
# Don't use absolute paths (unless necessary)
data = scitex.io.load("/home/user/project/data.csv")  # Bad

# Don't create directories manually
os.makedirs("output", exist_ok=True)  # Let scitex do this
scitex.io.save(data, "output/data.csv")

# Don't mix path styles
data = scitex.io.load("data\\file.csv")  # Use forward slashes
```

## Common Patterns

### Configuration-Driven Loading
```python
CONFIG = scitex.io.load_configs()
train_data = scitex.io.load(CONFIG.data.train_path)
val_data = scitex.io.load(CONFIG.data.val_path)
```

### Batch Processing
```python
from pathlib import Path

# Process all files
for file in Path("./data").glob("*.csv"):
    data = scitex.io.load(file)
    processed = process(data)
    scitex.io.save(processed, f"./output/{file.name}")
```

### Safe Loading with Fallbacks
```python
def load_or_compute(path, compute_fn, *args, **kwargs):
    """Load from cache or compute and save."""
    try:
        return scitex.io.load(path)
    except FileNotFoundError:
        result = compute_fn(*args, **kwargs)
        scitex.io.save(result, path)
        return result

# Usage
features = load_or_compute(
    "./cache/features.npy",
    extract_features,
    data
)
```

## Integration with Other Modules

### With scitex.plt
```python
# Plotting saves both image and data
fig, ax = scitex.plt.subplots()
ax.plot(x, y, label="signal")
scitex.io.save(fig, "analysis.png")
# Creates: analysis.png AND analysis.png.csv
```

### With scitex.gen
```python
# Automatic output directory management
CONFIG, _, _, _, _ = scitex.gen.start(sys, plt)
results = process_data()
scitex.io.save(results, "results.json")  # Saved in organized directory
```

## Troubleshooting

### Common Issues

1. **Module Import Errors**
```python
# If you get: "No module named 'yaml'"
# Install: pip install pyyaml
```

2. **Permission Errors**
```python
# Check write permissions
import os
os.access(directory, os.W_OK)
```

3. **Large File Handling**
```python
# For very large files, use streaming
# Or save in chunks
for i, chunk in enumerate(data_chunks):
    scitex.io.save(chunk, f"chunk_{i}.npy")
```

## See Also
- [scitex.gen](../gen/README.md) - Environment setup
- [scitex.plt](../plt/README.md) - Plotting integration
- [scitex.path](../path/README.md) - Path utilities