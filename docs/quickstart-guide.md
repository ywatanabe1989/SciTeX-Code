# SciTeX Quick Start Guide

## 5-Minute Setup

### 1. Installation
```bash
pip install scitex
```

### 2. First Script
```python
import scitex as stx

# Save data
data = {'results': [1, 2, 3, 4, 5]}
stx.save(data, 'my_data')

# Load data
loaded = stx.load('my_data')
```

### 3. Quick Visualization
```python
import numpy as np

# Generate data
x = np.linspace(0, 10, 100)
y = np.sin(x)

# Create plot
fig, ax = stx.subplots()
ax.plot(x, y)
ax.set_title('Quick Plot')
stx.save_fig('sine_wave')
```

## Core Features

### I/O Operations
```python
# Save anything
stx.save(my_object, 'filename')

# Load automatically
data = stx.load('filename')
```

### Plotting
```python
# Create figures
fig, ax = stx.subplots(figsize=(10, 6))

# Save with timestamp
stx.save_fig('plot_name')
```

### Configuration
```python
# Access config
cfg = stx.config()
output_dir = cfg.paths.results
```

### Statistics
```python
# Brunner-Munzel test
stat, p_value = stx.stats.brunner_munzel(group1, group2)
```

## Project Structure
```
my_project/
├── scripts/
├── config/
│   ├── PATH.yaml
│   └── PARAMS.yaml
├── data/
└── results/
```

## Next Steps
- Read [comprehensive examples](../examples/)
- Explore [module documentation](modules/)
- Check [API reference](api/)