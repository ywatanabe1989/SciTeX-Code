# SciTeX Core Concepts

## Philosophy

SciTeX is built on the principle of **"Write less, do more"** for scientific Python programming.

### Design Principles

1. **Convention over Configuration**
   - Sensible defaults for scientific computing
   - Consistent patterns across modules
   - Minimal boilerplate code

2. **Unified Interfaces**
   - One function for loading any file type
   - One function for saving any data
   - Consistent API across modules

3. **Automatic Organization**
   - Output directories created automatically
   - Symlinks for easy access to latest results
   - Timestamped experiment tracking

4. **Reproducibility First**
   - Random seed management
   - Environment logging
   - Unique experiment IDs

## Key Concepts

### 1. The SciTeX Format

All Python scripts in SciTeX projects follow a standard structure:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-30 12:00:00 (username)"
# File: /path/to/script.py

import scitex
# ... other imports ...

# Parameters
PARAMS = {
    "seed": 42,
    "batch_size": 32,
}

# Functions
def main():
    """Main function."""
    pass

# Execution
if __name__ == "__main__":
    CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.gen.start(
        sys, plt, **PARAMS
    )
    main()
    scitex.gen.close(CONFIG)
```

### 2. Output Management

SciTeX automatically organizes outputs:

```
scripts/
└── your_script_out/
    ├── RUNNING/
    │   └── 2025Y-05M-30D-12h00m00s_AbCd/
    │       ├── stdout.log
    │       ├── stderr.log
    │       └── outputs/
    └── symlinks/
        └── latest -> ../RUNNING/2025Y-05M-30D-12h00m00s_AbCd/
```

### 3. Configuration System

Configurations are loaded from YAML files and accessed with dot notation:

```yaml
# config/experiment.yaml
model:
  name: "ResNet"
  layers: 50
training:
  epochs: 100
  batch_size: 32
```

```python
CONFIG = scitex.io.load_configs()
print(CONFIG.model.name)  # "ResNet"
print(CONFIG.training.epochs)  # 100
```

### 4. Data Tracking

When you plot with scitex, it automatically saves the data:

```python
fig, ax = scitex.plt.subplots()
ax.plot(x, y, label="signal")
scitex.io.save(fig, "plot.png")
# Creates: plot.png AND plot.png.csv with the plotted data
```

### 5. Module Organization

SciTeX modules are organized by functionality:

- **Core**: `gen`, `io`, `plt`
- **Data**: `pd`, `dsp`, `stats`
- **ML/AI**: `ai`, `nn`, `torch`
- **Utilities**: `path`, `str`, `dict`

## Important Patterns

### Pattern: Start-Process-Close

```python
# 1. Start (initialize environment)
CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.gen.start(sys, plt)

# 2. Process (your work)
data = scitex.io.load("data.csv")
results = process(data)
scitex.io.save(results, "results.csv")

# 3. Close (cleanup and finalize)
scitex.gen.close(CONFIG)
```

### Pattern: Lazy Loading

```python
# Don't load all data at once
# Bad:
all_data = [scitex.io.load(f"data_{i}.npy") for i in range(1000)]

# Good:
for i in range(1000):
    data = scitex.io.load(f"data_{i}.npy")
    process_and_save(data)
    del data  # Free memory
```

### Pattern: Batch Operations

```python
# Process multiple files efficiently
from pathlib import Path

files = Path("./data").glob("*.csv")
results = []

for file in files:
    df = scitex.io.load(file)
    result = analyze(df)
    results.append(result)
    
scitex.io.save(pd.DataFrame(results), "summary.csv")
```

## Error Handling

SciTeX provides helpful error messages:

```python
try:
    data = scitex.io.load("nonexistent.csv")
except FileNotFoundError as e:
    print(f"Error: {e}")
    # SciTeX will suggest checking the path

try:
    scitex.io.save(data, "invalid/\\/path.csv")
except ValueError as e:
    print(f"Error: {e}")
    # SciTeX will explain the issue
```

## Best Practices

### DO ✅
- Use relative paths starting with `./`
- Run scripts from project root
- Let scitex create directories
- Use scitex.gen.start() for experiments
- Save intermediate results frequently

### DON'T ❌
- Create output directories manually
- Use absolute paths
- Mix scitex with manual file operations
- Skip scitex.gen.close()
- Hardcode paths in scripts

## Advanced Features

### Custom Output Directories
```python
CONFIG, _, _, _, _ = scitex.gen.start(
    sdir="./custom_output_dir/",
    sdir_suffix="experiment_1"
)
```

### Matplotlib Customization
```python
CONFIG, _, _, plt, CC = scitex.gen.start(
    plt=plt,
    fig_size_mm=(180, 120),
    dpi_save=600,
    fontsize="large"
)
```

### Debug Mode
```python
# Create config/IS_DEBUG.yaml with:
# IS_DEBUG: true

# This will:
# - Use "DEBUG_" prefix for IDs
# - Enable verbose output
# - Skip certain optimizations
```

## Next Steps

- Explore [Module Overview](03_module_overview.md)
- Try [Common Workflows](04_common_workflows.md)
- Read module-specific guides in `docs/modules/`