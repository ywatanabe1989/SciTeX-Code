# SciTeX Quick Start Guide (5 Minutes)

## Installation
```bash
pip install scitex
# or for development:
pip install -e /path/to/scitex_repo
```

## Basic Script Template

```python
#!/usr/bin/env python3
import sys
import matplotlib.pyplot as plt
import scitex

# Start (handles all initialization)
CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.gen.start(sys, plt)

# Your code here
data = scitex.io.load("./data.csv")
# ... process ...
scitex.io.save(results, "results.csv")

# Close (ensures proper cleanup)
scitex.gen.close(CONFIG)
```

## Essential Functions

### 1. File I/O
```python
# Load any file type
data = scitex.io.load("file.ext")  # Auto-detects format

# Save with auto directory creation
scitex.io.save(obj, "path/to/file.ext")
```

### 2. Configuration
```python
# Load all YAML configs from ./config/
CONFIG = scitex.io.load_configs()
print(CONFIG.model.batch_size)  # Dot access
```

### 3. Plotting
```python
# Enhanced matplotlib
fig, ax = scitex.plt.subplots(figsize=(6, 4))
ax.plot(x, y)
ax.set_xyt("Time (s)", "Voltage (mV)", "Signal")  # Set all labels at once
scitex.io.save(fig, "plot.png")  # Saves image + data
```

### 4. Data Processing
```python
# Pandas utilities
df_rounded = scitex.pd.round(df, 3)

# Signal processing
filtered = scitex.dsp.bandpass(signal, 1, 50, fs=1000)

# Statistics
result = scitex.stats.corr_test(x, y)
```

## Project Structure
```
project/
├── config/          # YAML configs
├── data/           # Input data
├── scripts/        # Your scripts
│   └── script_out/ # Auto-created outputs
├── examples/
└── tests/
```

## Common Patterns

### Pattern 1: Experiment Script
```python
import scitex

# Load config
CONFIG = scitex.io.load_configs()

# Start with seed for reproducibility
CONFIG, _, _, plt, _ = scitex.gen.start(
    sys, plt, seed=CONFIG.seed
)

# Run experiment
for epoch in range(CONFIG.n_epochs):
    # ... training code ...
    scitex.io.save(model, f"model_epoch_{epoch}.pth")

scitex.gen.close(CONFIG)
```

### Pattern 2: Data Analysis
```python
import scitex

# Quick analysis without full setup
df = scitex.io.load("data.csv")
df_clean = scitex.pd.round(df, 2)

# Plot results
fig, axes = scitex.plt.subplots(2, 2)
for ax, col in zip(axes.flat, df.columns):
    ax.hist(df[col])
    ax.set_xyt(col, "Count", f"Distribution of {col}")

scitex.io.save(fig, "distributions.png")
```

### Pattern 3: Signal Processing
```python
import scitex

# Load and process signal
signal = scitex.io.load("signal.npy")
fs = 1000  # sampling frequency

# Apply filters
filtered = scitex.dsp.bandpass(signal, 1, 50, fs)
hilbert = scitex.dsp.hilbert(filtered)

# Save results
scitex.io.save({
    "original": signal,
    "filtered": filtered,
    "hilbert": hilbert
}, "processed_signals.npz")
```

## Tips for Success

1. **Always use relative paths** starting with `./`
2. **Run scripts from project root**
3. **Use `scitex.gen.start()` for reproducibility**
4. **Let scitex handle directory creation**
5. **Check `./script_out/` for outputs**

## Next Steps

- Read the [Core Concepts](02_core_concepts.md) guide
- Explore [Module Overview](03_module_overview.md)
- Try the [Common Workflows](04_common_workflows.md)

## Help & Debugging

```python
# Check scitex version
import scitex
print(scitex.__version__)

# List available functions in a module
print(dir(scitex.io))

# Get help on any function
help(scitex.io.load)
```