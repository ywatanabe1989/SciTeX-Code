# SciTeX Quick Start Guide

## Installation

```bash
pip install scitex
```

For optional features:
```bash
# Machine learning features
pip install scitex imbalanced-learn pytorch-optimizer

# PDF processing
pip install scitex PyPDF2 pdfplumber PyMuPDF

# Signal processing
pip install scitex wavelets-pytorch
```

## 5-Minute Tutorial

### 1. Basic Data Operations

```python
import scitex as stx
import numpy as np

# Data normalization
data = np.random.randn(1000) * 10 + 50
normalized = stx.gen.to_01(data)  # Normalize to [0,1]
z_scored = stx.gen.to_z(data)     # Z-score normalization

# Percentile clipping
clipped = stx.gen.clip_perc(data, low=5, high=95)
```

### 2. Scientific Plotting with Units

```python
# Create unit-aware plots
from scitex.units import Units, Q

# Create data with units
time = Q(np.linspace(0, 10, 100), Units.second)
voltage = Q(np.sin(time.value), Units.volt)

# Plot with automatic unit handling
fig, ax = stx.plt.subplots()
ax.plot_with_units(time, voltage)
# Automatically shows: Time (s) vs Voltage (V)
```

### 3. File I/O with Auto-organization

```python
# Save data - automatically organized by script/notebook name
df = pd.DataFrame({'x': [1, 2, 3], 'y': [4, 5, 6]})
stx.io.save(df, "results.csv")
# Saves to: ./script_name_out/results.csv

# Load with caching
data = stx.io.load("results.csv")  # Cached for performance
```

### 4. Statistical Analysis

```python
# Correlation with significance
x = np.random.randn(100)
y = x + np.random.randn(100) * 0.5

r, p = stx.stats.corr(x, y, method='spearman')
print(f"Correlation: {r:.3f}, p-value: {p:.3f}")
```

### 5. Machine Learning Utilities

```python
# Standardize features
X = np.random.randn(100, 10)
X_std = stx.ai.standardize(X)

# Handle imbalanced data (requires imbalanced-learn)
X, y = stx.ai.undersample(X, y)
```

## Common Workflows

### Scientific Paper Figures

```python
# Create publication-ready figure
fig, axes = stx.plt.subplots(2, 2, figsize=(10, 8))

# Plot with automatic styling
ax = axes[0, 0]
ax.plot(time, voltage)
ax.set_xlabel("Time", unit="s")
ax.set_ylabel("Voltage", unit="V")

# Add significance markers
stx.plt.add_significance(ax, x1=2, x2=4, p=0.001)

# Save with metadata
stx.io.save(fig, "figure_1.png", dpi=300)
```

### Data Pipeline

```python
# Load → Process → Analyze → Save
data = stx.io.load("raw_data.csv")
processed = stx.gen.to_z(data)  # Normalize
results = stx.stats.summary(processed)
stx.io.save(results, "analysis_results.csv")
```

### Reproducible Research

```python
# Set random seed
stx.gen.seed(42)

# Track environment
stx.repro.save_environment("experiment_env.yaml")

# Log parameters
params = {"learning_rate": 0.01, "epochs": 100}
stx.io.save(params, "parameters.json")
```

## Key Features

### 🎯 Smart Defaults
- Automatic output directory organization
- Intelligent file type detection
- Built-in caching for repeated operations

### 🔬 Scientific Focus
- Unit-aware plotting prevents errors
- Statistical functions with significance testing
- Publication-ready figure styling

### 🚀 Performance
- Efficient caching system
- Parallel processing support
- Memory-efficient operations

### 📚 Comprehensive
- 50+ modules for various scientific tasks
- Extensive examples in `/examples/notebooks/`
- Well-tested and documented

## Next Steps

1. **Explore Examples**: Check `/examples/notebooks/` for detailed tutorials
2. **Read Module Docs**: Each module has comprehensive documentation
3. **Check Features**: See `/docs/` for specific feature guides

## Getting Help

- **Issues**: [GitHub Issues](https://github.com/scitex/scitex)
- **Examples**: `/examples/notebooks/`
- **API Docs**: [Full API Reference](https://scitex.readthedocs.io)

---

Happy scientific computing with SciTeX! 🚀🔬