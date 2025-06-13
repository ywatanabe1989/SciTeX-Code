# scitex.plt Module Documentation

## Overview

The `scitex.plt` module is an enhanced wrapper around matplotlib that provides data tracking capabilities, simplified plotting interfaces, and seamless integration with the scitex ecosystem. It maintains full compatibility with matplotlib.pyplot while adding powerful features for scientific data visualization.

## Key Features

- **Data Tracking**: Automatically tracks all plotted data for reproducibility
- **CSV Export**: Export all plot data to CSV format for use in other tools (e.g., SigmaPlot)
- **matplotlib Compatibility**: Drop-in replacement for matplotlib.pyplot
- **Enhanced Axes**: Additional convenience methods for common operations
- **Integrated Saving**: Works seamlessly with `scitex.io.save()` for figure and data export

## Core Components

### `scitex.plt.subplots()`

Enhanced version of matplotlib's subplots that tracks plotted data.

```python
import scitex.plt as plt

# Basic usage - creates tracked figure and axes
fig, ax = plt.subplots()

# Multiple subplots
fig, axes = plt.subplots(2, 2, figsize=(10, 8))

# Disable tracking when not needed
fig, ax = plt.subplots(track=False)
```

**Key differences from matplotlib:**
- Returns wrapper objects that track plotting operations
- Automatically exports data when saving figures with `scitex.io.save()`
- Provides enhanced methods on axes objects

### Enhanced Axes Methods

#### `ax.set_xyt()`
Set xlabel, ylabel, and title in one call.

```python
# Instead of three separate calls
ax.set_xlabel('Time (s)')
ax.set_ylabel('Amplitude')
ax.set_title('Signal Analysis')

# Use single method
ax.set_xyt('Time (s)', 'Amplitude', 'Signal Analysis')
```

#### `ax.export_as_csv()`
Export all plotted data as a pandas DataFrame.

```python
# Plot multiple datasets
ax.plot([1, 2, 3], [4, 5, 6], id="dataset1")
ax.scatter([2, 3, 4], [5, 6, 7], id="dataset2")

# Export to DataFrame
df = ax.export_as_csv()
print(df.columns)
# ['dataset1_plot_x', 'dataset1_plot_y', 'dataset2_scatter_x', 'dataset2_scatter_y']

# Save to file
ax.export_as_csv("./plot_data.csv")
```

### Color Management

#### Color cycles
Access consistent color palettes through the CC (Color Cycle) dictionary.

```python
CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.gen.start(sys, plt)

# Use predefined colors
ax.plot(x, y1, color=CC["blue"], label="Method A")
ax.plot(x, y2, color=CC["red"], label="Method B")
ax.plot(x, y3, color=CC["green"], label="Method C")
```

#### `scitex.plt.color`
Utilities for color manipulation and palette generation.

```python
# Get colors from colormap
colors = scitex.plt.color.get_colors_from_cmap('viridis', n=5)

# Interpolate between colors
gradient = scitex.plt.color.interpolate(color1, color2, steps=10)

# Add hue column to DataFrame for seaborn
df = scitex.plt.color.add_hue_col(df, group_col='category')
```

### Specialized Plotting Functions

#### `scitex.plt.ax` submodule
Contains specialized plotting functions for common scientific visualizations.

```python
# Confusion matrix
scitex.plt.ax.plot_conf_mat(ax, y_true, y_pred)

# Shaded error regions
scitex.plt.ax.plot_shaded_line(ax, x, y_mean, y_std)

# Raster plots
scitex.plt.ax.plot_raster(ax, spike_times, neuron_ids)

# Heatmaps with proper aspect ratio
scitex.plt.ax.plot_heatmap(ax, data, cmap='hot')

# Circular histograms
scitex.plt.ax.plot_circular_hist(ax, angles, bins=36)
```

## Data Tracking System

### How It Works

1. **Automatic Tracking**: When you create a figure with `scitex.plt.subplots()`, all plotting operations are automatically tracked.

2. **ID System**: Each plot can be assigned an ID for easy identification in exported data.

```python
ax.plot(x1, y1, id="control")
ax.plot(x2, y2, id="treatment")
```

3. **Export Integration**: When saving figures with `scitex.io.save()`, data is automatically exported as CSV.

```python
fig, ax = scitex.plt.subplots()
ax.plot(time, signal)
ax.set_xyt('Time (s)', 'Voltage (mV)', 'Neural Recording')

# Saves both figure and data
scitex.io.save(fig, "./results/recording.png")
# Creates: recording.png AND recording.csv
```

### Supported Plot Types

The tracking system supports all major matplotlib plot types:

- `plot()` - Line plots
- `scatter()` - Scatter plots
- `bar()` - Bar charts
- `hist()` - Histograms
- `boxplot()` - Box plots
- `violinplot()` - Violin plots
- `errorbar()` - Error bar plots
- `fill_between()` - Filled regions

## matplotlib Compatibility

`scitex.plt` is designed as a drop-in replacement for `matplotlib.pyplot`:

```python
# Standard matplotlib
import matplotlib.pyplot as plt

# scitex enhanced version
import scitex.plt as plt

# All matplotlib functions work identically
plt.figure()
plt.plot([1, 2, 3], [4, 5, 6])
plt.xlabel('X axis')
plt.ylabel('Y axis')
plt.title('My Plot')
plt.legend()
plt.grid(True)
plt.show()
```

## Best Practices

### 1. Use IDs for Multi-Dataset Plots
```python
fig, ax = scitex.plt.subplots()

for method, data in results.items():
    ax.plot(data['x'], data['y'], id=method, label=method)
    
ax.legend()
df = ax.export_as_csv()  # Columns named by IDs
```

### 2. Leverage Enhanced Methods
```python
# Configure multiple axes efficiently
fig, axes = scitex.plt.subplots(2, 2)

for i, ax in enumerate(axes.flat):
    ax.plot(data[i])
    ax.set_xyt(f'X{i}', f'Y{i}', f'Plot {i}')
```

### 3. Combine with scitex.gen for Complete Workflow
```python
import sys
import scitex
import scitex.plt as plt

# Initialize with scitex.gen
CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.gen.start(sys, plt)

# Create tracked plots
fig, ax = plt.subplots()
ax.plot(x, y, color=CC["blue"])
ax.set_xyt('Time', 'Value', 'Experiment Results')

# Save with automatic data export
scitex.io.save(fig, "./results.png", symlink_from_cwd=True)

# Cleanup
scitex.gen.close(CONFIG)
```

### 4. Disable Tracking When Not Needed
```python
# For temporary/debugging plots
fig, ax = scitex.plt.subplots(track=False)
ax.plot(quick_data)  # Won't be tracked
```

## Common Use Cases

### 1. Scientific Paper Figures
```python
# Set publication-ready settings
fig, ax = scitex.plt.subplots(figsize=(3.5, 2.5))

# Plot with specific colors and styles
ax.plot(x, control, 'o-', color=CC["black"], label='Control')
ax.plot(x, treatment, 's-', color=CC["red"], label='Treatment')

# Clean styling
ax.set_xyt('Concentration (μM)', 'Response', '')
ax.legend(frameon=False)

# Save at high DPI
scitex.io.save(fig, "./figures/fig2a.png", dpi=300)
```

### 2. Multi-Panel Figures
```python
fig, axes = scitex.plt.subplots(2, 3, figsize=(12, 8))

datasets = load_all_datasets()
for (i, j), ax in np.ndenumerate(axes):
    idx = i * 3 + j
    if idx < len(datasets):
        ax.plot(datasets[idx]['x'], datasets[idx]['y'])
        ax.set_xyt('', '', f'Dataset {idx+1}')

# Save entire figure with all data
scitex.io.save(fig, "./analysis/all_datasets.png")
```

### 3. Statistical Plots
```python
fig, (ax1, ax2) = scitex.plt.subplots(1, 2, figsize=(10, 5))

# Box plot with individual points
ax1.boxplot([group1, group2, group3], labels=['A', 'B', 'C'])
for i, group in enumerate([group1, group2, group3], 1):
    ax1.scatter([i]*len(group), group, alpha=0.3, s=20)

# Correlation plot
ax2.scatter(x, y, alpha=0.5)
ax2.plot(x_fit, y_fit, 'r-', label=f'r={correlation:.3f}')
ax2.legend()

scitex.io.save(fig, "./stats/comparison.png")
```

### 4. Time Series Analysis
```python
fig, axes = scitex.plt.subplots(3, 1, sharex=True, figsize=(10, 8))

# Raw signal
axes[0].plot(time, signal, id='raw')
axes[0].set_xyt('', 'Raw', 'Signal Processing')

# Filtered signal
axes[1].plot(time, filtered, id='filtered', color=CC["blue"])
axes[1].set_xyt('', 'Filtered', '')

# Frequency spectrum
axes[2].plot(freqs, spectrum, id='spectrum', color=CC["red"])
axes[2].set_xyt('Frequency (Hz)', 'Power', '')

# Export all data together
df = fig.export_as_csv()
scitex.io.save(df, "./analysis/signal_data.csv")
```

## Advanced Features

### Custom Axes Styling
```python
# Use ax style methods
ax.hide_spines(['top', 'right'])
ax.set_n_ticks(5, 4)  # 5 x-ticks, 4 y-ticks
ax.sci_note(True, True)  # Scientific notation on both axes
ax.rotate_labels(45, 0)  # Rotate x-labels by 45 degrees
```

### Panel Management
```python
# Add panel labels
for i, ax in enumerate(axes.flat):
    ax.add_panel(chr(65+i))  # A, B, C, ...
```

### Export Options
```python
# Export with custom column names
df = ax.export_as_csv()
df.columns = ['time', 'control', 'treatment']

# Export only specific plots
df = ax.export_as_csv(ids=['control', 'treatment'])
```

## Troubleshooting

### Issue: Data not being tracked
```python
# Ensure using scitex.plt, not matplotlib.pyplot
import scitex.plt as plt  # Correct
# import matplotlib.pyplot as plt  # Wrong

# Check tracking is enabled
fig, ax = plt.subplots(track=True)  # Default is True
```

### Issue: CSV not being created
```python
# Use scitex.io.save, not plt.savefig
scitex.io.save(fig, "plot.png")  # Creates plot.png AND plot.csv
# plt.savefig("plot.png")  # Only creates plot.png
```

### Issue: Memory usage with large datasets
```python
# Disable tracking for large exploratory plots
fig, ax = scitex.plt.subplots(track=False)

# Or clear tracked data manually
ax.clear_tracked_data()
```

## See Also

- [scitex.gen](../gen/README.md) - Environment initialization
- [scitex.io](../io/README.md) - File I/O operations
- [matplotlib documentation](https://matplotlib.org/) - Original matplotlib docs
- [Agent Guidelines](../../agent_guidelines/03_module_overview.md) - Module overview