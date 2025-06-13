# Why Use SciTeX?

SciTeX (Monogusa - "lazy person" in Japanese) is a comprehensive Python utility package designed to simplify scientific computing and research workflows.

## Key Benefits

### 1. **Unified I/O Interface**
```python
# Instead of remembering different functions for each format:
import pandas as pd
import numpy as np
import json
import yaml
df = pd.read_csv("data.csv")
arr = np.load("array.npy")
with open("config.json") as f:
    config = json.load(f)

# Just use scitex:
import scitex
df = scitex.io.load("data.csv")
arr = scitex.io.load("array.npy")
config = scitex.io.load("config.json")
```

### 2. **Automatic Output Management**
```python
# Traditional approach:
os.makedirs("outputs/experiment_1/plots", exist_ok=True)
plt.savefig("outputs/experiment_1/plots/figure1.png")
df.to_csv("outputs/experiment_1/data/results.csv")

# With scitex:
scitex.io.save(fig, "figure1.png")  # Automatically creates directories
scitex.io.save(df, "results.csv")   # Saves with symlinks for easy access
```

### 3. **Reproducible Research**
```python
# Start any script with:
CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.gen.start(
    sys, plt, seed=42
)
# This automatically:
# - Sets random seeds for all libraries
# - Configures matplotlib for publication-quality plots
# - Creates timestamped output directories
# - Logs all output to files
# - Generates unique experiment IDs
```

### 4. **Enhanced Data Visualization**
```python
# Matplotlib with data tracking:
fig, ax = scitex.plt.subplots()
ax.plot(x, y, label="data")
scitex.io.save(fig, "plot.png")
# Automatically saves both image AND the plotted data as CSV!
```

### 5. **Scientific Computing Tools**
```python
# Signal processing
filtered = scitex.dsp.bandpass(signal, low=1, high=50, fs=1000)
pac_values = scitex.dsp.pac(phase_signal, amplitude_signal)

# Statistics with proper formatting
result = scitex.stats.corr_test(x, y)
print(f"r={result['r']:.3f}, p={result['p']:.4f}")
stars = scitex.stats.p2stars(result['p'])  # Returns: "**"
```

### 6. **Time-Saving Utilities**
```python
# Pretty printing
scitex.str.printc("Important message", c="red")

# Path handling
latest_file = scitex.io.find_latest("./results/*.csv")

# Configuration management
CONFIG = scitex.io.load_configs()  # Loads all YAML files from ./config/
print(CONFIG.experiment.learning_rate)  # Dot-accessible
```

## When to Use SciTeX

✅ **Perfect for:**
- Scientific Python projects
- Machine learning experiments
- Data analysis pipelines
- Research requiring reproducibility
- Projects with mixed file formats

❌ **Not ideal for:**
- Production web applications
- Minimal dependency requirements
- Non-scientific Python projects

## Core Philosophy

SciTeX follows the principle of "convention over configuration":
- Assumes you're running from project root
- Automatically organizes outputs
- Provides sensible defaults
- Makes common tasks one-liners

## Getting Started

```python
import scitex

# Start your experiment
CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.gen.start(sys, plt)

# Your code here
data = scitex.io.load("./data/dataset.csv")
# ... process data ...
scitex.io.save(results, "results.csv")

# Clean shutdown
scitex.gen.close(CONFIG)
```

This approach ensures consistent, reproducible, and well-organized research code.