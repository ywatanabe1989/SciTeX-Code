# SciTeX Plotting - Quick Start Guide

Create publication-ready scientific figures with automatic unit handling and styling.

## Basic Plotting

### Simple Plot

```python
import scitex as stx
import numpy as np

# Create figure
fig, ax = stx.plt.subplots()

# Plot data
x = np.linspace(0, 10, 100)
y = np.sin(x)
ax.plot(x, y)

# Save
stx.io.save(fig, "sine_wave.png")
```

## Unit-Aware Plotting (New Feature!)

### Automatic Unit Handling

```python
from scitex.units import Units, Q

# Create data with units
time = Q(np.linspace(0, 5, 100), Units.millisecond)
voltage = Q(np.random.randn(100) * 10, Units.millivolt)

# Plot with automatic unit conversion and labeling
fig, ax = stx.plt.subplots()
ax.plot_with_units(time, voltage)
# Automatically shows: Time (ms) vs Voltage (mV)

# Mix different units - automatic conversion!
time_seconds = Q(np.array([1, 2, 3]), Units.second)
voltage_volts = Q(np.array([0.1, 0.2, 0.15]), Units.volt)
ax.plot_with_units(time_seconds, voltage_volts, 'ro')
# Converts to match first plot: s→ms, V→mV
```

### Manual Unit Specification

```python
# Override detected units
ax.plot_with_units(x_data, y_data, 
                   x_unit='Hz', y_unit='dB')

# Validate units match
ax.plot_with_units(time, voltage, validate_units=True)
# Raises error if subsequent plots have incompatible units
```

## Publication-Ready Figures

### Multi-Panel Figures

```python
fig, axes = stx.plt.subplots(2, 2, figsize=(10, 8))

# Panel A: Time series
ax = axes[0, 0]
ax.plot(time, voltage)
ax.set_xlabel("Time", unit="ms")
ax.set_ylabel("Voltage", unit="mV")
ax.panel_label("A")

# Panel B: Histogram
ax = axes[0, 1]
ax.hist(voltage.value, bins=30)
ax.set_xlabel("Voltage (mV)")
ax.set_ylabel("Count")
ax.panel_label("B")

# Panel C: Scatter with significance
ax = axes[1, 0]
x = np.random.randn(50)
y = x + np.random.randn(50) * 0.5
ax.scatter(x, y, alpha=0.6)
ax.set_xlabel("Variable X")
ax.set_ylabel("Variable Y")
r, p = stx.stats.corr(x, y)
ax.text(0.1, 0.9, f"r={r:.2f}, p={p:.3f}", 
        transform=ax.transAxes)
ax.panel_label("C")

# Panel D: Bar plot with error bars
ax = axes[1, 1]
groups = ['Control', 'Treatment A', 'Treatment B']
means = [1.0, 1.5, 1.8]
sems = [0.1, 0.15, 0.12]
ax.bar(groups, means, yerr=sems, capsize=5)
ax.set_ylabel("Response")
ax.panel_label("D")

# Add significance markers
stx.plt.add_significance(ax, x1=0, x2=1, p=0.05, y=2.0)
stx.plt.add_significance(ax, x1=0, x2=2, p=0.001, y=2.2)

plt.tight_layout()
stx.io.save(fig, "figure_1.png", dpi=300)
```

## Specialized Plots

### Correlation Matrix

```python
# Generate correlation data
data = np.random.randn(100, 5)
corr_matrix = np.corrcoef(data.T)

# Plot with significance
fig, ax = stx.plt.subplots()
im = ax.imshow(corr_matrix, cmap='RdBu_r', vmin=-1, vmax=1)
plt.colorbar(im, ax=ax, label='Correlation')

# Add significance stars
for i in range(5):
    for j in range(5):
        if i != j:
            _, p = stx.stats.corr(data[:, i], data[:, j])
            if p < 0.001:
                ax.text(j, i, '***', ha='center', va='center')
            elif p < 0.01:
                ax.text(j, i, '**', ha='center', va='center')
            elif p < 0.05:
                ax.text(j, i, '*', ha='center', va='center')
```

### Time-Frequency Plot

```python
# Generate signal
fs = 1000  # Hz
t = np.linspace(0, 2, 2*fs)
signal = np.sin(2*np.pi*10*t) + np.sin(2*np.pi*50*t*(1+0.5*t))

# Compute spectrogram
fig, (ax1, ax2) = stx.plt.subplots(2, 1, figsize=(10, 8))

# Time series
ax1.plot(t, signal)
ax1.set_xlabel("Time (s)")
ax1.set_ylabel("Amplitude")

# Spectrogram
f, t_spec, Sxx = scipy.signal.spectrogram(signal, fs)
ax2.pcolormesh(t_spec, f, 10*np.log10(Sxx), shading='gouraud')
ax2.set_ylabel('Frequency (Hz)')
ax2.set_xlabel('Time (s)')
ax2.set_ylim(0, 100)
plt.colorbar(ax2.collections[0], ax=ax2, label='Power (dB)')
```

## Styling and Customization

### Journal-Specific Styles

```python
# Nature style
stx.plt.set_style('nature')
fig, ax = stx.plt.subplots(figsize=(3.5, 2.5))

# Science style  
stx.plt.set_style('science')
fig, ax = stx.plt.subplots(figsize=(3.25, 2.5))

# Reset to default
stx.plt.set_style('default')
```

### Custom Colors

```python
# Use colorblind-friendly palette
colors = stx.plt.get_colors('colorblind')
for i, (x, y) in enumerate(datasets):
    ax.plot(x, y, color=colors[i], label=f'Dataset {i+1}')

# Scientific color maps
cmap = stx.plt.get_cmap('scientific')
```

## Interactive Features

### Exportable Data

```python
# Plot with automatic data export
fig, ax = stx.plt.subplots()
ax.plot(x, y, label='Signal')
ax.plot(x, y_fit, '--', label='Fit')

# Export plot data to CSV
ax.export_as_csv("figure_data.csv")
# Creates CSV with columns: x, Signal, Fit

# Export for SigmaPlot
ax.export_as_csv_for_sigmaplot("figure_sigmaplot.csv")
```

### Metadata Tracking

```python
# Add metadata to plots
ax.set_meta(
    experiment="Voltage Recording",
    date="2025-08-01",
    subject="Mouse_01",
    conditions="Room temperature"
)

# Metadata saved with figure file
```

## Tips for Publication

1. **Resolution**: Always save at 300+ DPI
   ```python
   stx.io.save(fig, "figure.png", dpi=300)
   ```

2. **Vector Format**: Use PDF/SVG for line plots
   ```python
   stx.io.save(fig, "figure.pdf")
   ```

3. **Font Sizes**: Ensure readability
   ```python
   stx.plt.set_font_size(8)  # For journals
   ```

4. **Panel Labels**: Use consistent labeling
   ```python
   ax.panel_label("A", fontweight='bold')
   ```

5. **Units**: Always specify units
   ```python
   ax.set_xlabel("Time", unit="s")
   ax.set_ylabel("Current", unit="μA")
   ```

## Common Patterns

### Error Bars and Confidence Intervals

```python
# Standard error bars
ax.errorbar(x, y_mean, yerr=y_sem, fmt='o-', capsize=5)

# Confidence interval shading
ax.plot(x, y_mean, 'b-')
ax.fill_between(x, y_mean-y_ci, y_mean+y_ci, alpha=0.3)
```

### Annotations

```python
# Add arrows and text
ax.annotate('Peak response', xy=(x_peak, y_peak),
            xytext=(x_peak+1, y_peak+0.5),
            arrowprops=dict(arrowstyle='->', color='red'))

# Highlight regions
ax.axvspan(stim_start, stim_end, alpha=0.2, color='yellow',
           label='Stimulus')
```

---

Create beautiful, accurate scientific figures with SciTeX! 📊🎨