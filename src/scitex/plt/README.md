<!-- ---
!-- Timestamp: 2025-06-04 10:29:38
!-- Author: ywatanabe
!-- File: /ssh:ywatanabe@sp:/home/ywatanabe/proj/.claude-worktree/scitex_repo/src/scitex/plt/README.md
!-- --- -->

# SciTeX-Code: Scientific Computing Foundation (formerly scitex.plt)

*Part of the revolutionary **SciTeX Ecosystem** for complete scientific workflow automation*

A revolutionary plotting module that extends matplotlib with automatic data tracking, scientific caption generation, and manuscript integration. From experimental data to publication-ready figures with comprehensive documentation - all in one command.

## Table of Contents
- [Quick Start](#quick-start)
- [🚀 New: Scientific Caption System](#-new-scientific-caption-system)
- [Core Features](#core-features)
- [Basic Plot Types](#basic-plot-types)
- [Statistical Plot Types](#statistical-plot-types)
- [Scientific Plot Types](#scientific-plot-types)
- [🎯 Advanced Scientific Features](#-advanced-scientific-features)
- [Seaborn Integration](#seaborn-integration)
- [Styling and Layout](#styling-and-layout)
- [Color Utilities](#color-utilities)
- [Data Export](#data-export)
- [📋 Manuscript Integration](#-manuscript-integration)
- [Complete API Reference](#complete-api-reference)

## Quick Start

```python
import scitex
import numpy as np

# Create figure with tracking enabled (default)
fig, ax = scitex.plt.subplots()

# Plot data - automatically tracked
x = np.linspace(0, 10, 100)
ax.plot(x, np.sin(x), label='sin(x)', id='sin_wave')
ax.plot(x, np.cos(x), label='cos(x)', id='cos_wave')

# Style the plot (clean separation of concerns)
ax.set_xyt(x='Time (s)', y='Amplitude', t='Trigonometric Functions')
ax.legend()

# Set comprehensive scientific metadata
ax.set_meta(
    caption='Trigonometric functions showing sine and cosine waves over time.',
    keywords=['trigonometry', 'oscillations', 'mathematical_functions'],
    experimental_details={'n_points': 100, 'domain': '0 to 10'},
    journal_style='nature'
)

# Save figure and data - all metadata automatically exported!
scitex.io.save(fig, 'my_plot.png')
# Automatically saves:
# - my_plot.png (figure)
# - my_plot.csv (data)
# - my_plot_for_sigmaplot.csv (SigmaPlot format)  
# - my_plot_metadata.yaml (structured metadata)
```

## 🚀 New: Scientific Metadata System

scitex.plt now includes a revolutionary metadata system with clean separation of concerns and YAML export:

### Single Panel with Comprehensive Metadata
```python
# Create figure and plot
fig, ax = scitex.plt.subplots()
dose = np.logspace(-2, 2, 50)
response = 100 / (1 + (5.2/dose)**2.1)

ax.semilogx(dose, response, 'o-', id='dose_response')

# Clean separation: styling vs metadata
ax.set_xyt(x='Dose (mg/kg)', y='Response (%)', t='Dose-Response Curve')

ax.set_meta(
    caption='Dose-response curve showing EC50 = 5.2 ± 0.3 mg/kg with Hill coefficient = 2.1 ± 0.2.',
    methods='Dose-response curves generated using 8-point serial dilutions in triplicate.',
    stats='EC50 values calculated using four-parameter logistic regression (n=6, p<0.001).',
    keywords=['pharmacology', 'dose_response', 'EC50', 'hill_coefficient'],
    experimental_details={
        'n_experiments': 6,
        'n_concentrations': 8,
        'replicates': 3,
        'curve_fit': 'four_parameter_logistic',
        'temperature': 37,
        'incubation_time': 24
    },
    journal_style='nature'
)

scitex.io.save(fig, 'dose_response.png')  # YAML metadata automatically saved!
```

### Multi-Panel Figure with Structured Metadata
![Multi-panel Example](../../examples/plt_gallery/figures/03_multipanel_scientific_figure.gif)
```python
# Create multi-panel figure
fig, ((ax1, ax2), (ax3, ax4)) = scitex.plt.subplots(2, 2)

# Panel A: Time-series data
t = np.linspace(0, 20, 1000)
signal = np.exp(-t/5) * np.sin(2*np.pi*t)
ax1.plot(t, signal, id='timeseries')
ax1.set_xyt(x='Time (s)', y='Amplitude', t='A. Time Series')
ax1.set_meta(
    caption='Time-series data showing exponential decay with τ = 5 seconds.',
    methods='Synthetic signal generated with exponential decay and sinusoidal oscillation.',
    keywords=['time_series', 'exponential_decay', 'oscillation'],
    experimental_details={'tau': 5, 'frequency': 1, 'duration': 20}
)

# Panel B: Frequency spectrum  
freq = np.fft.fftfreq(len(signal), t[1]-t[0])
spectrum = np.abs(np.fft.fft(signal))
ax2.semilogy(freq[:len(freq)//2], spectrum[:len(freq)//2], id='spectrum')
ax2.set_xyt(x='Frequency (Hz)', y='Power', t='B. Frequency Spectrum')
ax2.set_meta(
    caption='Frequency spectrum revealing 1 Hz fundamental frequency.',
    methods='Fast Fourier Transform (FFT) analysis using numpy.fft.',
    keywords=['frequency_analysis', 'FFT', 'power_spectrum'],
    experimental_details={'sampling_rate': 50, 'window': 'none', 'n_points': 1000}
)

# Panel C: Statistical distribution
data = np.random.normal(50, 10, 1000)
ax3.hist(data, bins=30, alpha=0.7, id='distribution')
ax3.set_xyt(x='Value', y='Count', t='C. Distribution')
ax3.set_meta(
    caption='Normal distribution with μ = 50, σ = 10.',
    stats='Kolmogorov-Smirnov test confirms normality (p > 0.05).',
    keywords=['normal_distribution', 'histogram', 'statistics'],
    experimental_details={'n_samples': 1000, 'mean': 50, 'std': 10, 'bins': 30}
)

# Panel D: Correlation analysis
x_corr = np.random.randn(100)
y_corr = 0.89*x_corr + 0.45*np.random.randn(100)
ax4.scatter(x_corr, y_corr, alpha=0.6, id='correlation')
ax4.set_xyt(x='X Variable', y='Y Variable', t='D. Correlation')
ax4.set_meta(
    caption='Strong positive correlation with R² = 0.89, p < 0.001.',
    stats='Pearson correlation analysis with 95% confidence intervals.',
    keywords=['correlation', 'linear_regression', 'scatter_plot'],
    experimental_details={'n_points': 100, 'r_squared': 0.89, 'correlation': 0.89}
)

# Set figure-level metadata
ax1.set_figure_meta(
    caption='Comprehensive signal analysis workflow demonstrating (A) temporal dynamics, (B) spectral characteristics, (C) statistical properties, and (D) correlation structure.',
    significance='This multi-panel analysis demonstrates fundamental signal processing techniques.',
    funding='Supported by research grant XYZ-123.',
    data_availability='Synthetic data and analysis code available at github.com/example/repo'
)

scitex.io.save(fig, 'multi_panel_analysis.png')
```

### Example YAML Metadata Output
```yaml
figure_metadata:
  main_caption: "Comprehensive signal analysis workflow..."
  significance: "This multi-panel analysis demonstrates..."
  funding: "Supported by research grant XYZ-123"
  data_availability: "Synthetic data available at github.com/example/repo"
  created_timestamp: "2025-06-04T11:35:00"

panel_metadata:
  panel_1:
    caption: "Time-series data showing exponential decay..."
    methods: "Synthetic signal generated with exponential decay..."
    keywords: ["time_series", "exponential_decay", "oscillation"]
    experimental_details:
      tau: 5
      frequency: 1
      duration: 20
    created_timestamp: "2025-06-04T11:35:00"
    scitex_version: "1.11.0"
  
  panel_2:
    caption: "Frequency spectrum revealing 1 Hz fundamental..."
    methods: "Fast Fourier Transform (FFT) analysis..."
    keywords: ["frequency_analysis", "FFT", "power_spectrum"]
    experimental_details:
      sampling_rate: 50
      window: "none"
      n_points: 1000

export_info:
  timestamp: "2025-06-04T11:35:00"
  scitex_version: "1.11.0"
```

## Core Features

### 🎯 Automatic Data Tracking
- Every plot call is automatically tracked with its data
- Assign unique IDs to plots for easy identification
- Export all plotted data to CSV for reproducibility

### 🎨 Enhanced Styling
- Simplified axis labeling with `set_xyt()`
- Advanced legend positioning (including outside plot area)
- Easy spine and tick customization
- Built-in scientific notation support

### 📊 Extended Plot Types
- Statistical plots (mean±std, confidence intervals, etc.)
- Specialized plots (raster, ECDF, confusion matrix, etc.)
- Seamless Seaborn integration
- Custom SciTeX plot types

### 💾 Export Capabilities
- Export all plotted data to CSV
- SigmaPlot-compatible CSV format with visual parameters
- Automatic CSV generation when saving figures

---

## Basic Plot Types

### `ax.plot()` - Line Plot
![ax.plot](../../examples/plt_gallery/figures/ax.plot.gif)
```python
# Arrange
fig, ax = scitex.plt.subplots()
x = np.linspace(0, 10, 100)
y = np.sin(x)

# Act
ax.plot(x, y, label='Sine Wave', color='blue', linewidth=2, id='sine_plot')
ax.set_xyt(x='Time (s)', y='Amplitude', t='Basic Line Plot')
ax.set_meta(
    caption='Fundamental sine wave demonstrating oscillatory behavior with period T = 2π and unit amplitude.',
    keywords=['trigonometry', 'sine_wave', 'oscillation'],
    experimental_details={'period': '2π', 'amplitude': 1, 'frequency': '1/(2π)'}
)
ax.legend()

# Assert (Save)
scitex.io.save(fig, "basic_line_plot.gif")
```

### `ax.scatter()` - Scatter Plot
![ax.scatter](../../examples/plt_gallery/figures/ax.scatter.gif)
```python
# Arrange
fig, ax = scitex.plt.subplots()
n = 100
x = np.random.randn(n)
y = 2 * x + np.random.randn(n) * 0.5
colors = np.random.rand(n)

# Act
ax.scatter(x, y, c=colors, cmap='viridis', alpha=0.6, s=50, id='scatter_data')
ax.set_xyt(x='X values', y='Y values', t='Scatter Plot with Color Mapping')
ax.set_meta(
    caption='Scatter plot showing linear relationship with added noise and color-coded data points using viridis colormap.',
    methods='Random data generated with linear relationship y = 2x + noise.',
    keywords=['scatter_plot', 'linear_relationship', 'colormap'],
    experimental_details={'n_points': 100, 'slope': 2, 'noise_std': 0.5, 'colormap': 'viridis'}
)

# Assert (Save)
scitex.io.save(fig, "scatter_plot.gif")
```

### `ax.bar()` - Bar Plot
![ax.bar](../../examples/plt_gallery/figures/ax.bar.gif)
```python
# Arrange
fig, ax = scitex.plt.subplots()
categories = ['A', 'B', 'C', 'D', 'E']
values = [23, 45, 56, 78, 32]
errors = [2, 3, 4, 3, 2]

# Act
ax.bar(categories, values, yerr=errors, capsize=5, alpha=0.7, id='bar_data')
ax.set_xytc(x='Categories', y='Values', t='Bar Plot with Error Bars',
           c='Categorical data comparison with error bars representing standard deviation across experimental conditions.')

# Assert (Save)
scitex.io.save(fig, "bar_plot.gif")
```

### `ax.hist()` - Histogram
![ax.hist](../../examples/plt_gallery/figures/ax.hist.gif)
```python
# Arrange
fig, ax = scitex.plt.subplots()
data = np.random.normal(0, 1, 1000)

# Act
ax.hist(data, bins=30, alpha=0.7, color='skyblue', edgecolor='black', id='histogram')
ax.set_xytc(x='Value', y='Frequency', t='Histogram of Normal Distribution',
           c='Normal distribution histogram with n=1000 samples, μ=0, σ=1, demonstrating central limit theorem.')

# Assert (Save)
scitex.io.save(fig, "histogram.gif")
```

### `ax.boxplot()` - Box Plot
![ax.boxplot](../../examples/plt_gallery/figures/ax.boxplot.gif)
```python
# Arrange
fig, ax = scitex.plt.subplots()
data_list = [np.random.normal(i, 1, 100) for i in range(1, 5)]
labels = ['Group 1', 'Group 2', 'Group 3', 'Group 4']

# Act
ax.boxplot(data_list, labels=labels, patch_artist=True, id='boxplot')
ax.set_xytc(x='Groups', y='Values', t='Box Plot Comparison',
           c='Statistical comparison across groups showing median, quartiles, and outliers.')

# Assert (Save)
scitex.io.save(fig, "boxplot.gif")
```

### `ax.pie()` - Pie Chart
![ax.pie](../../examples/plt_gallery/figures/ax.pie.gif)
```python
# Arrange
fig, ax = scitex.plt.subplots()
sizes = [30, 25, 20, 15, 10]
labels = ['A', 'B', 'C', 'D', 'E']
explode = (0, 0.1, 0, 0, 0)

# Act
ax.pie(sizes, labels=labels, explode=explode, autopct='%1.1f%%', 
       startangle=90, id='pie_chart')
ax.set_xyt(t='Pie Chart Distribution')

# Assert (Save)
scitex.io.save(fig, "pie_chart.gif")
```

### `ax.errorbar()` - Error Bar Plot
![ax.errorbar](../../examples/plt_gallery/figures/ax.errorbar.gif)
```python
# Arrange
fig, ax = scitex.plt.subplots()
x = np.linspace(0, 10, 10)
y = np.sin(x)
yerr = 0.1 * np.random.rand(len(x))
xerr = 0.1 * np.random.rand(len(x))

# Act
ax.errorbar(x, y, yerr=yerr, xerr=xerr, fmt='o-', capsize=5, id='errorbar')
ax.set_xytc(x='X values', y='Y values', t='Error Bar Plot',
           c='Data points with bidirectional error bars representing measurement uncertainty.')

# Assert (Save)
scitex.io.save(fig, "errorbar_plot.gif")
```

### `ax.fill_between()` - Fill Between
![ax.fill_between](../../examples/plt_gallery/figures/ax.fill_between.gif)
```python
# Arrange
fig, ax = scitex.plt.subplots()
x = np.linspace(0, 10, 100)
y1 = np.sin(x)
y2 = np.cos(x)

# Act
ax.fill_between(x, y1, y2, alpha=0.3, color='green', label='Between sine and cosine', id='fill_between')
ax.plot(x, y1, 'b-', label='sin(x)', id='sine')
ax.plot(x, y2, 'r-', label='cos(x)', id='cosine')
ax.set_xyt(x='X values', y='Y values', t='Fill Between Curves')
ax.legend()

# Assert (Save)
scitex.io.save(fig, "fill_between.gif")
```

---

## Statistical Plot Types

### `ax.plot_mean_std()` - Mean ± Standard Deviation
![ax.plot_mean_std](../../examples/plt_gallery/figures/ax.plot_mean_std.gif)
```python
# Arrange
fig, ax = scitex.plt.subplots()
x = np.linspace(0, 10, 50)
# Generate multiple samples (trials x time_points)
data = np.array([np.sin(x) + 0.2 * np.random.randn(len(x)) for _ in range(20)])

# Act
ax.plot_mean_std(x, data, color='blue', alpha=0.3, label='Mean ± SD', id='mean_std')
ax.set_xyt(x='Time', y='Value', t='Mean with Standard Deviation')
ax.set_meta(
    caption='Time series analysis showing population mean with standard deviation envelope (n=20 trials).',
    methods='Statistical summary computed across 20 independent trials.',
    stats='Mean ± standard deviation calculated pointwise across trials.',
    keywords=['time_series', 'statistics', 'mean', 'standard_deviation'],
    experimental_details={'n_trials': 20, 'n_timepoints': 50, 'statistic': 'mean_std'}
)
ax.legend()

# Assert (Save)
scitex.io.save(fig, "plot_mean_std.gif")
```

### `ax.plot_mean_ci()` - Mean with Confidence Interval
![ax.plot_mean_ci](../../examples/plt_gallery/figures/ax.plot_mean_ci.gif)
```python
# Arrange
fig, ax = scitex.plt.subplots()
x = np.linspace(0, 10, 50)
data = np.array([np.sin(x) + 0.2 * np.random.randn(len(x)) for _ in range(30)])

# Act
ax.plot_mean_ci(x, data, confidence=0.95, color='red', alpha=0.3, label='Mean ± 95% CI', id='mean_ci')
ax.set_xyt(x='Time', y='Value', t='Mean with 95% Confidence Interval')
ax.legend()

# Assert (Save)
scitex.io.save(fig, "plot_mean_ci.gif")
```

### `ax.plot_median_iqr()` - Median with IQR
![ax.plot_median_iqr](../../examples/plt_gallery/figures/ax.plot_median_iqr.gif)
```python
# Arrange
fig, ax = scitex.plt.subplots()
x = np.linspace(0, 10, 50)
data = np.array([np.sin(x) + 0.3 * np.random.randn(len(x)) for _ in range(25)])

# Act
ax.plot_median_iqr(x, data, color='green', alpha=0.3, label='Median ± IQR', id='median_iqr')
ax.set_xyt(x='Time', y='Value', t='Median with Interquartile Range')
ax.legend()

# Assert (Save)
scitex.io.save(fig, "plot_median_iqr.gif")
```

### `ax.plot_shaded_line()` - Shaded Line Plot
![ax.plot_shaded_line](../../examples/plt_gallery/figures/ax.plot_shaded_line.gif)
```python
# Arrange
fig, ax = scitex.plt.subplots()
x = np.linspace(0, 10, 100)
y = np.sin(x)
lower = y - 0.2
upper = y + 0.2

# Act
ax.plot_shaded_line(x, y, lower, upper, color='purple', alpha=0.3, 
                    label='Shaded line', id='shaded_line')
ax.set_xyt(x='X values', y='Y values', t='Shaded Line Plot')
ax.legend()

# Assert (Save)
scitex.io.save(fig, "plot_shaded_line.gif")
```

### `ax.plot_kde()` - Kernel Density Estimation
![ax.plot_kde](../../examples/plt_gallery/figures/ax.plot_kde.gif)
```python
# Arrange
fig, ax = scitex.plt.subplots()
data = np.random.normal(0, 1, 1000)

# Act
ax.plot_kde(data, bw_method=0.3, color='orange', fill=True, alpha=0.6, id='kde')
ax.set_xyt(x='Value', y='Density', t='Kernel Density Estimation')

# Assert (Save)
scitex.io.save(fig, "plot_kde.gif")
```

---

## Scientific Plot Types

### `ax.plot_raster()` - Raster Plot (Spike Trains)
![ax.plot_raster](../../examples/plt_gallery/figures/ax.plot_raster.gif)
```python
# Arrange
fig, ax = scitex.plt.subplots()
# Simulate spike times for 3 neurons
spike_times = [
    np.random.uniform(0, 10, size=50),  # Neuron 1
    np.random.uniform(0, 10, size=30),  # Neuron 2
    np.random.uniform(0, 10, size=40)   # Neuron 3
]
trial_ids = [0, 1, 2]

# Act
ax.plot_raster(spike_times, trial_ids, color='black', marker='|', markersize=8, id='raster')
ax.set_xytc(x='Time (s)', y='Trial/Neuron', t='Raster Plot of Spike Trains',
           c='Neural spike timing analysis across multiple trials showing temporal firing patterns.')

# Assert (Save)
scitex.io.save(fig, "plot_raster.gif")
```

### `ax.plot_conf_mat()` - Confusion Matrix
![ax.plot_conf_mat](../../examples/plt_gallery/figures/ax.plot_conf_mat.gif)
```python
# Arrange
fig, ax = scitex.plt.subplots()
conf_mat = np.array([[50, 3, 2], [5, 40, 5], [2, 3, 45]])
class_names = ['Class A', 'Class B', 'Class C']

# Act
ax.plot_conf_mat(conf_mat, x_labels=class_names, y_labels=class_names,
                annot=True, fmt='d', cmap='Blues', id='conf_matrix')
ax.set_xyt(x='Predicted', y='Actual', t='Confusion Matrix')

# Assert (Save)
scitex.io.save(fig, "plot_conf_mat.gif")
```

### `ax.plot_ecdf()` - Empirical Cumulative Distribution Function
![ax.plot_ecdf](../../examples/plt_gallery/figures/ax.plot_ecdf.gif)
```python
# Arrange
fig, ax = scitex.plt.subplots()
data1 = np.random.normal(0, 1, 1000)
data2 = np.random.normal(2, 1.5, 1000)

# Act
ax.plot_ecdf(data1, label='Dataset 1', color='blue', id='ecdf1')
ax.plot_ecdf(data2, label='Dataset 2', color='red', id='ecdf2')
ax.set_xyt(x='Value', y='Cumulative Probability', t='Empirical CDF Comparison')
ax.legend()

# Assert (Save)
scitex.io.save(fig, "plot_ecdf.gif")
```

### `ax.plot_heatmap()` - Enhanced Heatmap
![ax.plot_heatmap](../../examples/plt_gallery/figures/ax.plot_heatmap.gif)
```python
# Arrange
fig, ax = scitex.plt.subplots()
data_2d = np.random.randn(10, 12)

# Act
ax.plot_heatmap(data_2d, cmap='viridis', annot=True, fmt='.2f', id='heatmap')
ax.set_xyt(x='Columns', y='Rows', t='Data Heatmap')

# Assert (Save)
scitex.io.save(fig, "plot_heatmap.gif")
```

### `ax.plot_violin()` - Violin Plot
![ax.plot_violin](../../examples/plt_gallery/figures/ax.plot_violin.gif)
```python
# Arrange
fig, ax = scitex.plt.subplots()
data_list = [np.random.normal(i, 1, 100) for i in range(1, 5)]
positions = [1, 2, 3, 4]

# Act
ax.plot_violin(data_list, positions=positions, widths=0.5, showmeans=True, id='violin')
ax.set_xyt(x='Groups', y='Values', t='Violin Plot Distribution')

# Assert (Save)
scitex.io.save(fig, "plot_violin.gif")
```

### `ax.plot_circular_hist()` - Circular Histogram
![ax.plot_circular_hist](../../examples/plt_gallery/figures/ax.plot_circular_hist.gif)
```python
# Arrange
fig, ax = scitex.plt.subplots(subplot_kw=dict(projection='polar'))
angles = np.random.vonmises(0, 2, 1000)  # Von Mises distributed angles

# Act
ax.plot_circular_hist(angles, bins=20, alpha=0.7, color='green', id='circular_hist')
ax.set_xyt(t='Circular Histogram of Angular Data')

# Assert (Save)
scitex.io.save(fig, "plot_circular_hist.gif")
```

### `ax.plot_fillv()` - Vertical Fill Regions
![ax.plot_fillv](../../examples/plt_gallery/figures/ax.plot_fillv.gif)
```python
# Arrange
fig, ax = scitex.plt.subplots()
x = np.linspace(0, 10, 100)
y = np.sin(x)

# Act
ax.plot(x, y, 'b-', label='Signal', id='signal')
ax.plot_fillv(2, 4, color='red', alpha=0.3, label='Region 1', id='region1')
ax.plot_fillv(6, 8, color='green', alpha=0.3, label='Region 2', id='region2')
ax.set_xyt(x='Time', y='Amplitude', t='Signal with Highlighted Regions')
ax.legend()

# Assert (Save)
scitex.io.save(fig, "plot_fillv.gif")
```

### `ax.plot_scatter_hist()` - Scatter with Marginal Histograms
![ax.plot_scatter_hist](../../examples/plt_gallery/figures/ax.plot_scatter_hist.gif)
```python
# Arrange
fig, ax = scitex.plt.subplots()
x = np.random.randn(1000)
y = 2 * x + np.random.randn(1000)

# Act
ax.plot_scatter_hist(x, y, hist_bins=30, alpha=0.6, id='scatter_hist')
ax.set_xyt(x='X values', y='Y values', t='Scatter Plot with Marginal Histograms')

# Assert (Save)
scitex.io.save(fig, "plot_scatter_hist.gif")
```

### `ax.plot_joyplot()` - Joy Plot (Ridgeline)
![ax.plot_joyplot](../../examples/plt_gallery/figures/ax.plot_joyplot.gif)
```python
# Arrange
fig, ax = scitex.plt.subplots()
data_groups = [np.random.normal(i, 1, 200) for i in range(5)]

# Act
ax.plot_joyplot(data_groups, overlap=0.5, alpha=0.7, colors=['C{}'.format(i) for i in range(5)], id='joyplot')
ax.set_xyt(x='Value', y='Group', t='Joy Plot (Ridgeline Plot)')

# Assert (Save)
scitex.io.save(fig, "plot_joyplot.gif")
```

---

## Seaborn Integration

### `ax.sns_barplot()` - Seaborn Bar Plot
![ax.sns_barplot](../../examples/plt_gallery/figures/ax.sns_barplot.gif)
```python
# Arrange
fig, ax = scitex.plt.subplots()
import pandas as pd
df = pd.DataFrame({
    'category': ['A', 'B', 'C', 'D'] * 25,
    'value': np.random.randn(100),
    'group': ['X', 'Y'] * 50
})

# Act
ax.sns_barplot(data=df, x='category', y='value', hue='group', id='sns_bar')
ax.set_xyt(x='Category', y='Value', t='Seaborn Bar Plot with Hue')

# Assert (Save)
scitex.io.save(fig, "sns_barplot.gif")
```

### `ax.sns_boxplot()` - Seaborn Box Plot
![ax.sns_boxplot](../../examples/plt_gallery/figures/ax.sns_boxplot.gif)
```python
# Arrange
fig, ax = scitex.plt.subplots()
df = pd.DataFrame({
    'category': ['A', 'B', 'C'] * 50,
    'value': np.random.randn(150),
    'group': ['X', 'Y'] * 75
})

# Act
ax.sns_boxplot(data=df, x='category', y='value', hue='group', id='sns_box')
ax.set_xyt(x='Category', y='Value', t='Seaborn Box Plot')

# Assert (Save)
scitex.io.save(fig, "sns_boxplot.gif")
```

### `ax.sns_violinplot()` - Seaborn Violin Plot
![ax.sns_violinplot](../../examples/plt_gallery/figures/ax.sns_violinplot.gif)
```python
# Arrange
fig, ax = scitex.plt.subplots()
df = pd.DataFrame({
    'category': ['A', 'B', 'C', 'D'] * 30,
    'value': np.random.randn(120),
    'group': ['X', 'Y'] * 60
})

# Act
ax.sns_violinplot(data=df, x='category', y='value', hue='group', split=True, id='sns_violin')
ax.set_xyt(x='Category', y='Value', t='Seaborn Violin Plot')

# Assert (Save)
scitex.io.save(fig, "sns_violinplot.gif")
```

### `ax.sns_heatmap()` - Seaborn Heatmap
![ax.sns_heatmap](../../examples/plt_gallery/figures/ax.sns_heatmap.gif)
```python
# Arrange
fig, ax = scitex.plt.subplots()
data_2d = np.random.randn(8, 6)
row_names = [f'Row {i}' for i in range(8)]
col_names = [f'Col {i}' for i in range(6)]

# Act
ax.sns_heatmap(data_2d, annot=True, cmap='coolwarm', 
               xticklabels=col_names, yticklabels=row_names, id='sns_heatmap')
ax.set_xyt(t='Seaborn Heatmap with Annotations')

# Assert (Save)
scitex.io.save(fig, "sns_heatmap.gif")
```

### `ax.sns_scatterplot()` - Seaborn Scatter Plot
![ax.sns_scatterplot](../../examples/plt_gallery/figures/ax.sns_scatterplot.gif)
```python
# Arrange
fig, ax = scitex.plt.subplots()
df = pd.DataFrame({
    'x': np.random.randn(100),
    'y': np.random.randn(100),
    'size': np.random.randint(20, 200, 100),
    'color': np.random.choice(['A', 'B', 'C'], 100)
})

# Act
ax.sns_scatterplot(data=df, x='x', y='y', size='size', hue='color', id='sns_scatter')
ax.set_xyt(x='X values', y='Y values', t='Seaborn Scatter Plot')

# Assert (Save)
scitex.io.save(fig, "sns_scatterplot.gif")
```

---

## 🎯 Advanced Scientific Features

### Factor-Out-of-Digits for Clean Scientific Notation
![Factor Out Digits](../../examples/plt_gallery/figures/05_text_formatting_showcase.gif)
```python
# Arrange
fig, ax = scitex.plt.subplots()
x = np.linspace(0, 1e-6, 100)
y = x * 1e9  # Very small x, very large y

# Act
ax.plot(x, y, id='scientific_data')
scitex.str.auto_factor_axis(ax, axis='both', precision=2, min_factor_power=3)
ax.set_xytc(x='Distance', y='Force', t='Automatically Factored Scientific Notation',
           c='Force vs distance plot with automatic factor-out notation for enhanced readability in scientific publications.')

# Assert (Save)
scitex.io.save(fig, 'factor_out_digits.png')
```

### Enhanced Log Scale with Minor Ticks
![Log Scale Minor Ticks](../../examples/plt_gallery/figures/02_log_scale_minor_ticks.gif)
```python
# Arrange
fig, ax = scitex.plt.subplots()
f = np.logspace(0, 3, 1000)  # 1 Hz to 1 kHz
power = 1/f**2  # Power spectrum

# Act
ax.loglog(f, power, id='power_spectrum')
scitex.plt.ax.set_log_scale(ax, axis='both', show_minor_ticks=True, grid=True, minor_grid=True)
ax.set_xytc(x='Frequency (Hz)', y='Power', t='Power Spectrum with Enhanced Log Scale',
           c='Power spectrum analysis demonstrating 1/f² scaling relationship with enhanced logarithmic visualization including minor ticks and grid.')

# Assert (Save)
scitex.io.save(fig, 'log_scale_demo.png')
```

### Text Formatting with Scientific Conventions
![Text Formatting](../../examples/plt_gallery/figures/05_text_formatting_showcase.gif)
```python
# Arrange
fig, ax = scitex.plt.subplots()
x = np.linspace(0, 10, 100)
y = np.sin(x)

# Act
ax.plot(x, y, id='formatted_text')
formatted_xlabel = scitex.str.format_axis_label('time', unit='seconds', capitalize=True)
formatted_ylabel = scitex.str.format_axis_label('voltage', unit='mV', capitalize=True)
ax.set_xytc(x=formatted_xlabel, y=formatted_ylabel, t='Scientific Text Formatting',
           c='Demonstration of automatic scientific text formatting with proper capitalization, unit handling, and LaTeX support.')

# Assert (Save)
scitex.io.save(fig, 'text_formatting.png')
```

### Enhanced Spine Control
![Spine Styling](../../examples/plt_gallery/figures/04_spine_styling_examples.gif)
```python
# Arrange
fig, ((ax1, ax2), (ax3, ax4)) = scitex.plt.subplots(2, 2)
x = np.linspace(0, 10, 50)
y = np.sin(x)

# Act - Different spine styles
ax1.plot(x, y, id='classic_spines')
scitex.plt.ax.show_classic_spines(ax1)  # Bottom and left only
ax1.set_xytc(t='Classic Style', c='Traditional scientific plot style with bottom and left spines only.')

ax2.plot(x, y, id='all_spines')
scitex.plt.ax.show_all_spines(ax2)  # All four spines
ax2.set_xytc(t='All Spines', c='Complete frame style with all four axis spines visible.')

ax3.plot(x, y, id='no_spines')
ax3.hide_spines(top=True, right=True, bottom=True, left=True)
ax3.set_xytc(t='No Spines', c='Minimal style with all spines hidden for clean presentation.')

ax4.plot(x, y, id='custom_spines')
scitex.plt.ax.show_spines(ax4, top=False, right=False, spine_width=2.0)
ax4.set_xytc(t='Custom Style', c='Custom spine configuration with enhanced line width.')

# Set figure-level caption
ax1.set_supxytc(title='Spine Styling Options for Scientific Publications',
               caption='Comparison of different axis spine styling approaches commonly used in scientific publications, demonstrating flexibility in plot aesthetics.')

# Assert (Save)
scitex.io.save(fig, 'spine_styles.png')
```

### Enhanced Raster Plot with Position Control
![Enhanced Raster](../../examples/plt_gallery/figures/01_enhanced_raster_plot.gif)
```python
# Arrange
fig, ax = scitex.plt.subplots()
# Simulate neural spike data with different trial positions
spike_times = [np.random.uniform(0, 10, 30) for _ in range(5)]
trial_positions = [0, 1.2, 2.4, 3.6, 4.8]  # Custom spacing

# Act
ax.plot_raster(spike_times, y_offset=trial_positions, color='black', 
               apply_set_n_ticks=True, n_xticks=6, id='neural_spikes')
ax.set_xytc(x='Time (s)', y='Trial', t='Neural Spike Trains with Custom Positioning',
           c='Neural spike raster plot demonstrating custom trial positioning and automatic tick control for electrophysiology data visualization.')

# Assert (Save)
scitex.io.save(fig, 'enhanced_raster.png')
```

---

## Styling and Layout

### `ax.set_xytc()` - Set Labels, Title, and Caption
![ax.set_xytc](../../examples/plt_gallery/figures/ax.set_xyt.gif)
```python
# Arrange
fig, ax = scitex.plt.subplots()
x = np.linspace(0, 10, 100)
y = np.sin(x)

# Act
ax.plot(x, y, id='sine_wave')
ax.set_xytc(x='Time (seconds)', y='Amplitude (volts)', t='Sine Wave Signal',
           c='Pure sine wave demonstrating periodic oscillation with automatic caption integration.')

# Assert (Save) - Caption automatically saved!
scitex.io.save(fig, "set_xytc_example.gif")
```

### `ax.hide_spines()` - Hide Axis Spines
![ax.hide_spines](../../examples/plt_gallery/figures/ax.hide_spines.gif)
```python
# Arrange
fig, ax = scitex.plt.subplots()
x = np.linspace(0, 10, 100)
y = np.sin(x)

# Act
ax.plot(x, y, 'b-', linewidth=2, id='clean_plot')
ax.hide_spines(top=True, right=True)  # Hide top and right spines
ax.set_xyt(x='X axis', y='Y axis', t='Clean Plot Style')

# Assert (Save)
scitex.io.save(fig, "hide_spines.gif")
```

### `ax.set_n_ticks()` - Set Number of Ticks
![ax.set_n_ticks](../../examples/plt_gallery/figures/ax.set_n_ticks.gif)
```python
# Arrange
fig, ax = scitex.plt.subplots()
x = np.linspace(0, 100, 1000)
y = np.sin(x/10)

# Act
ax.plot(x, y, id='controlled_ticks')
ax.set_n_ticks(n_xticks=5, n_yticks=3)
ax.set_xyt(x='X values', y='Y values', t='Controlled Tick Density')

# Assert (Save)
scitex.io.save(fig, "set_n_ticks.gif")
```

### `ax.rotate_labels()` - Rotate Tick Labels
![ax.rotate_labels](../../examples/plt_gallery/figures/ax.rotate_labels.gif)
```python
# Arrange
fig, ax = scitex.plt.subplots()
categories = ['Very Long Category Name ' + str(i) for i in range(5)]
values = [20, 35, 30, 35, 27]

# Act
ax.bar(categories, values, id='rotated_labels')
ax.rotate_labels(x=45)  # Rotate x-axis labels 45 degrees
ax.set_xyt(x='Categories', y='Values', t='Bar Plot with Rotated Labels')

# Assert (Save)
scitex.io.save(fig, "rotate_labels.gif")
```

### `ax.extend()` - Extend Axis Limits
![ax.extend](../../examples/plt_gallery/figures/ax.extend.gif)
```python
# Arrange
fig, ax = scitex.plt.subplots()
x = np.linspace(0, 10, 100)
y = np.sin(x)

# Act
ax.plot(x, y, 'o-', id='extended_plot')
ax.extend(x_ratio=1.2, y_ratio=1.3)  # Extend x by 20%, y by 30%
ax.set_xyt(x='X values', y='Y values', t='Plot with Extended Limits')

# Assert (Save)
scitex.io.save(fig, "extend_limits.gif")
```

### Legend Positioning
![legend_positioning](../../examples/plt_gallery/figures/legend_positioning.gif)
```python
# Arrange
fig, ax = scitex.plt.subplots()
x = np.linspace(0, 10, 100)

# Act
ax.plot(x, np.sin(x), label='sin(x)', id='sin')
ax.plot(x, np.cos(x), label='cos(x)', id='cos')
ax.plot(x, np.tan(x/2), label='tan(x/2)', id='tan')
ax.legend(loc='upper right out')  # Legend outside plot area
ax.set_xyt(x='X values', y='Y values', t='Plot with External Legend')

# Assert (Save)
scitex.io.save(fig, "legend_positioning.gif")
```

---

## Color Utilities

### Color Generation from Colormap
![colormap_colors](../../examples/plt_gallery/figures/colormap_colors.gif)
```python
# Arrange
fig, ax = scitex.plt.subplots()
x = np.linspace(0, 10, 100)
n_lines = 5

# Act
colors = scitex.plt.color.get_colors_from_conf_matap(n=n_lines, cmap='viridis')
for i, color in enumerate(colors):
    y = np.sin(x + i * np.pi/4)
    ax.plot(x, y, color=color, label=f'Line {i+1}', linewidth=2, id=f'line_{i}')

ax.set_xyt(x='X values', y='Y values', t='Multiple Lines with Viridis Colors')
ax.legend()

# Assert (Save)
scitex.io.save(fig, "colormap_colors.gif")
```

### Color Interpolation
![color_interpolation](../../examples/plt_gallery/figures/color_interpolation.gif)
```python
# Arrange
fig, ax = scitex.plt.subplots()
x = np.linspace(0, 10, 100)
start_colors = ['red', 'blue', 'green']

# Act
interpolated_colors = scitex.plt.color.interpolate(start_colors, n=10)
for i, color in enumerate(interpolated_colors):
    y = np.sin(x + i * np.pi/10) + i * 0.2
    ax.plot(x, y, color=color, linewidth=2, id=f'interp_line_{i}')

ax.set_xyt(x='X values', y='Y values', t='Color Interpolation Demo')

# Assert (Save)
scitex.io.save(fig, "color_interpolation.gif")
```

### Color Visualization
![color_visualization](../../examples/plt_gallery/figures/color_visualization.gif)
```python
# Arrange
colors = ['red', 'blue', 'green', 'yellow', 'purple', 'orange']

# Act
scitex.plt.color.vizualize_colors(colors)

# Assert (no save needed - this function creates its own figure)
```

---

## Data Export

### Automatic Export with Figure Save
![automatic_export](../../examples/plt_gallery/figures/automatic_export.gif)
```python
# Arrange
fig, ax = scitex.plt.subplots()
x = np.linspace(0, 10, 50)
y1 = np.sin(x)
y2 = np.cos(x)

# Act
ax.plot(x, y1, label='sin(x)', id='sin_data')
ax.scatter(x[::5], y2[::5], label='cos samples', color='red', id='cos_samples')
ax.set_xytc(x='Time', y='Amplitude', t='Data Export Example',
           c='Demonstration of automatic data export functionality with mixed plot types.')
ax.legend()

# Assert (Save - automatically creates CSV and caption files)
scitex.io.save(fig, 'export_demo.png')  # Creates PNG, CSV, SigmaPlot CSV, and caption files
```

### Manual Data Export
![manual_export](../../examples/plt_gallery/figures/manual_export.gif)
```python
# Arrange
fig, ax = scitex.plt.subplots()
x = np.linspace(0, 10, 20)
y = np.sin(x)

# Act
ax.plot(x, y, 'o-', label='Data', id='manual_export')
ax.set_xyt(x='X', y='Y', t='Manual Export Demo')

# Export data manually
standard_df = ax.export_as_csv()
sigmaplot_df = ax.export_as_csv_for_sigmaplot()

# Assert (Save data)
standard_df.to_csv('manual_export_standard.csv', index=False)
sigmaplot_df.to_csv('manual_export_sigmaplot.csv', index=False)
scitex.io.save(fig, 'manual_export.gif')
```

---

## Multiple Subplots Example

![multiple_subplots](../../examples/plt_gallery/figures/multiple_subplots.gif)
```python
# Arrange
fig, axes = scitex.plt.subplots(2, 3, figsize=(15, 10))
x = np.linspace(0, 10, 100)

# Act - Different plot types in each subplot
# Line plot
axes[0, 0].plot(x, np.sin(x), 'b-', id='subplot_sin')
axes[0, 0].set_xyt(t='Line Plot')

# Scatter plot
axes[0, 1].scatter(x[::10], np.cos(x[::10]), color='red', id='subplot_scatter')
axes[0, 1].set_xyt(t='Scatter Plot')

# Bar plot
categories = ['A', 'B', 'C', 'D']
values = [1, 3, 2, 4]
axes[0, 2].bar(categories, values, id='subplot_bar')
axes[0, 2].set_xyt(t='Bar Plot')

# Histogram
data = np.random.normal(0, 1, 1000)
axes[1, 0].hist(data, bins=30, alpha=0.7, id='subplot_hist')
axes[1, 0].set_xytc(t='Histogram', c='Distribution analysis')

# Heatmap
heatmap_data = np.random.randn(5, 5)
axes[1, 1].plot_heatmap(heatmap_data, cmap='viridis', id='subplot_heatmap')
axes[1, 1].set_xyt(t='Heatmap')

# Violin plot
violin_data = [np.random.normal(i, 1, 100) for i in range(3)]
axes[1, 2].plot_violin(violin_data, id='subplot_violin')
axes[1, 2].set_xyt(t='Violin Plot')

# Figure-level caption using any axis
axes[0, 0].set_supxytc(title='Multiple Plot Types Demonstration', 
                      caption='Comprehensive demonstration of various plot types including line plots, scatter plots, bar charts, histograms, heatmaps, and violin plots.')

# Assert (Save)
scitex.io.save(fig, "multiple_subplots_demo.gif")
```

---

## 📋 Manuscript Integration

The revolutionary caption system integrates seamlessly with manuscript preparation workflows, supporting multiple output formats for different journal requirements.

### Automatic Caption Generation
```python
# Single figure with comprehensive caption
fig, ax = scitex.plt.subplots()
x = np.logspace(-2, 2, 50)
y = 100 / (1 + (10/x)**2)

ax.semilogx(x, y, 'o-', markersize=6, linewidth=2, id='dose_response')
ax.set_xytc(
    x='Concentration (μM)', 
    y='Response (%)', 
    t='Dose-Response Analysis',
    c='Dose-response curve showing concentration-dependent activation with EC50 = 10.0 ± 0.5 μM and Hill coefficient = 2.0 ± 0.1 (n=3 experiments, mean ± SEM).'
)

scitex.io.save(fig, 'figure_1.png')
# Generates: figure_1.png, figure_1.csv, figure_1_caption.txt, figure_1_caption.tex, figure_1_caption.md
```

### Multi-Panel Figure Workflow
```python
# Complete manuscript figure with panel captions
fig, ((ax1, ax2), (ax3, ax4)) = scitex.plt.subplots(2, 2, figsize=(12, 10))

# Panel A: Time course
time = np.linspace(0, 60, 300)
signal = 100 * (1 - np.exp(-time/15))
ax1.plot(time, signal, 'b-', linewidth=2, id='time_course')
ax1.set_xytc(x='Time (min)', y='Signal (%)', t='A. Time Course',
            c='Time-dependent signal activation showing exponential kinetics with τ = 15 min.')

# Panel B: Dose response
dose = np.logspace(-2, 2, 20)
response = 100 / (1 + (5/dose)**1.5)
ax2.semilogx(dose, response, 'ro-', markersize=6, id='dose_response')
ax2.set_xytc(x='Dose (μM)', y='Response (%)', t='B. Dose Response',
            c='Concentration-response relationship with EC50 = 5.0 μM.')

# Panel C: Statistical comparison
groups = ['Control', 'Treatment A', 'Treatment B']
means = [20, 45, 65]
errors = [3, 5, 4]
ax3.bar(groups, means, yerr=errors, capsize=5, alpha=0.8, id='statistics')
ax3.set_xytc(x='Groups', y='Response (AU)', t='C. Statistical Analysis',
            c='Comparative analysis showing significant increase in response (p < 0.001, ANOVA).')

# Panel D: Correlation
x_data = np.random.normal(50, 10, 100)
y_data = 1.2*x_data + np.random.normal(0, 5, 100)
ax4.scatter(x_data, y_data, alpha=0.6, s=30, id='correlation')
ax4.set_xytc(x='Variable X', y='Variable Y', t='D. Correlation Analysis',
            c='Strong positive correlation between variables (R² = 0.85, p < 0.001).')

# Figure-level caption
ax1.set_supxytc(
    title='Comprehensive Experimental Analysis',
    caption='Multi-panel analysis of experimental results. (A) Time course showing exponential activation kinetics. (B) Dose-response curve demonstrating concentration-dependent effects. (C) Statistical comparison across treatment groups. (D) Correlation analysis revealing linear relationship between measured variables. Data represent mean ± SEM from n=3-5 independent experiments.'
)

scitex.io.save(fig, 'figure_2_comprehensive.png')
```

### Journal-Specific Caption Formats
```python
# Configure caption style for different journals
from scitex.plt.utils._scientific_captions import configure_caption_style

# Nature style (concise, technical)
configure_caption_style('nature', 
                       max_length=500, 
                       technical_terms=True, 
                       statistical_details=True)

# Science style (detailed methodology)
configure_caption_style('science',
                       max_length=750,
                       methodology_emphasis=True,
                       sample_size_required=True)

# IEEE style (technical precision)
configure_caption_style('ieee',
                       max_length=600,
                       equation_numbers=True,
                       technical_precision=True)
```

### SciTeX-Paper Integration for Seamless LaTeX Workflow
```python
# Direct integration with SciTeX-Paper compilation system
from scitex.plt.utils._scientific_captions import export_for_scitex

# Create figures with automatic SciTeX-Paper compatibility
fig, ax = scitex.plt.subplots()
ax.plot(dose, response, 'o-', id='dose_response')
ax.set_xytc(x='Dose (μM)', y='Response (%)', t='Dose-Response Analysis',
           c='Pharmacological dose-response relationship showing EC50 = 10.2 ± 0.5 μM with Hill coefficient = 1.8 ± 0.2 (n=6 experiments, mean ± SEM). Statistical analysis performed using one-way ANOVA followed by Tukey post-hoc test.')

# Export directly for SciTeX-Paper system
export_for_scitex(fig, 'figure_1', 
                  scitex_dir='~/proj/SciTeX-Paper/',
                  include_methods=True,
                  include_stats=True)

# Generates SciTeX-Paper compatible files:
# ~/proj/SciTeX-Paper/figures/figure_1.pdf (high-quality vector)
# ~/proj/SciTeX-Paper/figures/figure_1.png (raster backup)
# ~/proj/SciTeX-Paper/captions/figure_1.tex (LaTeX caption)
# ~/proj/SciTeX-Paper/data/figure_1.csv (raw data)
# ~/proj/SciTeX-Paper/methods/figure_1_methods.tex (auto-generated methods)
```

### Automatic SciTeX-Paper Manuscript Integration
```python
# Multi-panel figure with SciTeX-Paper workflow
fig, ((ax1, ax2), (ax3, ax4)) = scitex.plt.subplots(2, 2, figsize=(12, 10))

# Panel A: Time course with detailed methodology
ax1.plot(time, signal, 'b-', linewidth=2, id='kinetics')
ax1.set_xytc(x='Time (min)', y='Response (%)', t='A. Kinetic Analysis',
            c='Time-dependent activation kinetics fitted to single exponential model (τ = 12.3 ± 1.2 min, R² = 0.97).',
            methods='Time course measurements performed at 37°C with 5-minute intervals over 60 minutes.',
            stats='Data fitted using non-linear least squares regression with 95% confidence intervals.')

# Panel B: Dose response with statistical details  
ax2.semilogx(dose, response, 'ro-', markersize=6, id='dose_response')
ax2.set_xytc(x='Dose (μM)', y='Response (%)', t='B. Concentration-Response',
            c='Sigmoidal dose-response curve with EC50 = 5.2 ± 0.3 μM and Hill coefficient = 1.9 ± 0.1.',
            methods='Concentration-response curves generated using 8-point serial dilutions in triplicate.',
            stats='EC50 values calculated using four-parameter logistic regression (n=6, p<0.001).')

# Panel C: Statistical comparison with detailed analysis
ax3.bar(groups, means, yerr=errors, capsize=5, alpha=0.8, id='comparison')
ax3.set_xytc(x='Treatment Groups', y='Response (fold change)', t='C. Treatment Comparison',
            c='Significant increase in response across treatment groups (****p<0.0001, one-way ANOVA F(2,15)=45.7).',
            methods='Treatments applied for 24h at indicated concentrations with vehicle controls.',
            stats='Statistical analysis: one-way ANOVA followed by Tukey multiple comparisons test.')

# Panel D: Correlation with regression analysis
ax4.scatter(x_data, y_data, alpha=0.6, s=30, id='correlation')
ax4.set_xytc(x='Parameter X', y='Parameter Y', t='D. Correlation Analysis',
            c='Strong positive correlation between experimental parameters (Pearson r = 0.89, p < 0.001).',
            methods='Correlation analysis performed on n=100 paired measurements.',
            stats='Pearson correlation coefficient with 95% confidence intervals [0.84, 0.93].')

# Figure-level caption with comprehensive description
ax1.set_supxytc(
    title='Comprehensive Pharmacological Analysis',
    caption='Multi-panel characterization of compound X effects. (A) Kinetic analysis revealing time-dependent activation. (B) Concentration-response relationship demonstrating potent activity. (C) Statistical comparison across treatment conditions. (D) Correlation analysis between key parameters. All experiments performed in biological triplicate with technical duplicates.',
    methods='All experiments conducted using standardized protocols with appropriate controls and statistical analysis.',
    significance='This work demonstrates the potential therapeutic application of compound X with nanomolar potency.'
)

# Export for SciTeX-Paper with complete manuscript integration
export_for_scitex(fig, 'figure_2_comprehensive',
                  scitex_dir='~/proj/SciTeX-Paper/',
                  generate_methods=True,
                  generate_stats_section=True,
                  generate_figure_list=True,
                  include_supplementary=True)
```

### SciTeX-Paper Automatic Document Generation
```python
# Complete manuscript integration
from scitex.plt.utils._scitex_integration import SciTeXManager

# Initialize SciTeX-Paper manager
stm = SciTeXManager('~/proj/SciTeX-Paper/')

# Figures automatically registered during save
scitex.io.save(fig1, 'figure_1.png')  # Auto-registered in SciTeX-Paper
scitex.io.save(fig2, 'figure_2.png')  # Auto-registered in SciTeX-Paper

# Generate complete manuscript sections
stm.generate_methods_section()      # ~/proj/SciTeX-Paper/sections/methods_figures.tex
stm.generate_results_section()      # ~/proj/SciTeX-Paper/sections/results_figures.tex  
stm.generate_figure_legends()       # ~/proj/SciTeX-Paper/sections/figure_legends.tex
stm.generate_supplementary()        # ~/proj/SciTeX-Paper/supplementary/

# Compile with SciTeX-Paper system
stm.compile_manuscript()            # Automatic LaTeX compilation
stm.generate_submission_package()   # Ready-to-submit manuscript package
```

### Traditional LaTeX Integration (Alternative)
```python
# For standard LaTeX workflows (non-SciTeX-Paper)
from scitex.plt.utils._scientific_captions import generate_latex_figure

latex_code = generate_latex_figure(
    'figure_2_comprehensive.png',
    label='fig:comprehensive_analysis',
    placement='htbp',
    width='\\textwidth',
    short_caption='Comprehensive experimental analysis',
    include_subfigures=True
)

print(latex_code)
# Output:
# \begin{figure}[htbp]
#     \centering
#     \includegraphics[width=\textwidth]{figure_2_comprehensive.png}
#     \caption[Comprehensive experimental analysis]{Multi-panel analysis...}
#     \label{fig:comprehensive_analysis}
# \end{figure}
```

### Manuscript Figure Database
```python
# Automatically track all figures for manuscript
from scitex.plt.utils._scientific_captions import ManuScript

ms = ManuScript("research_paper_2024")

# Figures are automatically registered when saved with captions
scitex.io.save(fig1, 'figure_1.png')  # Auto-registered
scitex.io.save(fig2, 'figure_2.png')  # Auto-registered

# Generate complete figure list
ms.generate_figure_list('figures.tex', format='latex')
ms.generate_figure_list('figures.md', format='markdown')
ms.generate_figure_list('figures.docx', format='word')

# Generate supplementary materials
ms.generate_supplementary_data('supplementary_data.zip')  # All CSV files
ms.generate_methods_section('figure_methods.tex')  # Auto-generated methods
```

### Citation Integration
```python
# Link figures to citations and references
ax.set_xytc(
    x='Time (s)', y='Signal', t='Replication Study',
    c='Experimental replication of findings from Smith et al. (2023) showing consistent results across laboratories.',
    references=['Smith2023', 'Johnson2022'],
    methods_ref='section_3_2'
)

# Auto-generate reference list
ms.compile_references('figure_references.bib')
```

---

## Terminal Plotting

![terminal_plotting](../../examples/plt_gallery/figures/terminal_plotting.gif)
```python
# Arrange
x = np.linspace(0, 10, 100)
y = np.sin(x)

# Act & Assert (Display in terminal)
scitex.plt.tpl(x, y)  # Creates ASCII plot in terminal
```

---

## Complete API Reference

### Main Functions
- **`scitex.plt.subplots(*args, track=True, **kwargs)`** - Enhanced subplot creation
- **`scitex.plt.close(fig=None)`** - Close figures
- **`scitex.plt.tpl(x, y)`** - Terminal plotting

### Basic Plot Methods (with tracking)
- **`plot()`**, **`scatter()`**, **`bar()`**, **`hist()`**, **`boxplot()`**, **`pie()`**
- **`errorbar()`**, **`fill_between()`**, **`step()`**, **`stem()`**

### Statistical Plot Methods
- **`plot_mean_std()`**, **`plot_mean_ci()`**, **`plot_median_iqr()`**
- **`plot_shaded_line()`**, **`plot_kde()`**

### Scientific Plot Methods
- **`plot_raster()`**, **`plot_conf_mat()`**, **`plot_ecdf()`**, **`plot_heatmap()`**
- **`plot_violin()`**, **`plot_circular_hist()`**, **`plot_fillv()`**
- **`plot_scatter_hist()`**, **`plot_joyplot()`**

### Seaborn Methods
- **`sns_barplot()`**, **`sns_boxplot()`**, **`sns_violinplot()`**, **`sns_heatmap()`**
- **`sns_scatterplot()`**, **`sns_histplot()`**, **`sns_kdeplot()`**

### Styling Methods
- **`set_xyt()`** - Set labels and title (clean separation of concerns)
- **`set_meta()`** - Set comprehensive scientific metadata with YAML export
- **`set_figure_meta()`** - Set figure-level metadata for multi-panel figures
- **`set_supxyt()`**, **`set_supxytc()`** - Set figure-level labels (legacy support)
- **`hide_spines()`**, **`show_spines()`**, **`show_classic_spines()`**, **`show_all_spines()`**
- **`set_n_ticks()`**, **`rotate_labels()`**, **`extend()`**, **`shift()`**

### Export Methods
- **`export_as_csv()`**, **`export_as_csv_for_sigmaplot()`**

### Color Utilities
- **`scitex.plt.color.get_colors_from_conf_matap()`**, **`interpolate()`**, **`vizualize_colors()`**

### Advanced Scientific Features  
- **`scitex.str.auto_factor_axis()`** - Automatic factor-out-of-digits notation
- **`scitex.plt.ax.set_log_scale()`** - Enhanced logarithmic scaling with minor ticks
- **`scitex.str.format_axis_label()`**, **`format_plot_text()`** - Scientific text formatting
- **`scitex.plt.ax.show_classic_spines()`**, **`show_all_spines()`** - Enhanced spine control

### Scientific Metadata System (New!)
- **`set_meta()`** - Comprehensive metadata with YAML export
- **`set_figure_meta()`** - Figure-level metadata for multi-panel figures
- **`export_metadata_yaml()`** - Direct YAML export functionality

### SciTeX Ecosystem Integration
- **SciTeX-Code** - AI-powered code generation from metadata
- **SciTeX-Paper** - Automated LaTeX manuscript generation  
- **SigMacro (SciTeX-Vis)** - Advanced publication-ready visualization
- **Complete AI Workflow** - Raw data to published paper automation

## 🔄 Complete Automated Scientific Workflow (LLM Agentic Era)

### The SciTeX Ecosystem: SciTeX + SciTeX-Code + SciTeX-Paper + SigMacro
```python
# REVOLUTIONARY: From Raw Data to Published Paper with AI Agents

# 1. DATA ANALYSIS WITH SciTeX (The Foundation)
import scitex
import numpy as np

# Load experimental data with automatic preprocessing
data = scitex.io.load('experiment_data.csv')
time = data['time']
signal = data['voltage']

# AI-assisted analysis with automated insights
fig, ax = scitex.plt.subplots(figsize=(8, 6))
ax.plot(time, signal, 'b-', linewidth=2, id='neural_recording')

# 2. COMPREHENSIVE METADATA WITH STRUCTURED YAML
ax.set_xyt(x='Time (ms)', y='Membrane Potential (mV)', t='Intracellular Neural Recording')
ax.set_meta(
    caption='Intracellular recording from layer 2/3 pyramidal neuron showing spontaneous action potentials with amplitude of -65 ± 5 mV and frequency of 12 ± 2 Hz (n=15 cells, mean ± SEM).',
    methods='Whole-cell patch-clamp recordings performed in acute brain slices using borosilicate electrodes (3-5 MΩ resistance) at 32°C in oxygenated ACSF.',
    stats='Statistical analysis performed using paired t-test with Bonferroni correction for multiple comparisons (α = 0.05).',
    keywords=['electrophysiology', 'patch_clamp', 'pyramidal_neuron', 'action_potential'],
    experimental_details={
        'n_cells': 15,
        'layer': '2/3',
        'cell_type': 'pyramidal',
        'temperature': 32,
        'electrode_resistance': '3-5 MΩ',
        'recording_duration': 300,
        'amplitude_mean': -65,
        'amplitude_sem': 5,
        'frequency_mean': 12,
        'frequency_sem': 2
    },
    journal_style='nature',
    significance='Novel insights into spontaneous activity patterns in cortical circuits.'
)

# 3. SCITEX-CODE INTEGRATION (AI-Powered Code Generation)
from scitex_code import AICodeGenerator
code_gen = AICodeGenerator()

# AI generates analysis code based on metadata
analysis_code = code_gen.generate_from_metadata(fig)
# → Automatic generation of statistical analysis, data processing, and visualization code

# 4. SCITEX-PAPER INTEGRATION (LaTeX Manuscript Automation)  
from scitex_paper import ManuscriptGenerator
manuscript = ManuscriptGenerator('~/proj/SciTeX-Paper/')

# AI-powered manuscript writing from figure metadata
manuscript.auto_generate_sections(fig)
# → Automatic Methods, Results, and Discussion sections from YAML metadata

# 5. SIGMACRO INTEGRATION (SciTeX-Vis: Advanced Visualization)
from sigmacro import AdvancedVisualization
sigmacro = AdvancedVisualization()

# AI-enhanced figure generation with publication standards
sigmacro.enhance_figure(fig, style='publication_ready')
# → Automatic color optimization, font standardization, and journal formatting

# 6. COMPLETE AUTOMATION PIPELINE
scitex.io.save(fig, 'neural_recording.png')  # Triggers the entire ecosystem

# GENERATED ECOSYSTEM OUTPUT:
# ~/proj/SciTeX-Paper/
# ├── figures/neural_recording.pdf           # High-quality publication figure
# ├── data/neural_recording.csv              # Raw experimental data
# ├── metadata/neural_recording.yaml         # Structured scientific metadata
# ├── code/neural_recording_analysis.py      # AI-generated analysis code
# ├── sections/methods_neural.tex            # Auto-generated methods section
# ├── sections/results_neural.tex            # Auto-generated results section
# ├── sections/discussion_neural.tex         # AI-assisted discussion points
# └── manuscript_neural_recording.pdf        # Complete manuscript draft
```

### Multi-Study AI-Powered Manuscript Generation
```python
# ULTIMATE AUTOMATION: AI Agents Managing Complete Research Workflow

from scitex_ecosystem import ScientificAI

# Initialize AI research assistant
ai_researcher = ScientificAI(
    data_sources=['~/experiments/', '~/literature/'],
    target_journal='nature_neuroscience',
    research_domain='computational_neuroscience'
)

# AI processes multiple experiments automatically
studies = [
    'experiment_1_patch_clamp.csv',
    'experiment_2_optical_recording.csv', 
    'experiment_3_behavioral_data.csv'
]

# AI-driven analysis and figure generation
for study in studies:
    # Automatic data loading and preprocessing
    data = ai_researcher.load_and_preprocess(study)
    
    # AI-generated hypotheses and analysis
    hypotheses = ai_researcher.generate_hypotheses(data)
    
    # Automated figure creation with metadata
    figures = ai_researcher.create_publication_figures(data, hypotheses)
    
    # AI literature review and contextualization
    context = ai_researcher.literature_context(hypotheses)

# AI writes complete manuscript
manuscript = ai_researcher.write_manuscript(
    figures=figures,
    context=context,
    target_journal='nature_neuroscience'
)

# Output: Complete research paper from raw data to submission!
# - AI-generated hypotheses based on data patterns
# - Publication-quality figures with comprehensive metadata
# - Literature-contextualized discussion
# - Journal-specific formatting and submission package
```

### Multi-Study Manuscript Compilation
```python
# Complete manuscript with multiple figures
from scitex.plt.utils._scitex_integration import SciTeXManager

# Initialize manuscript manager
manuscript = SciTeXManager('~/proj/SciTeX-Paper/')

# Generate all figure components automatically
manuscript.compile_all_figures()          # Process all saved figures
manuscript.generate_figure_legends()      # Create figure legends section  
manuscript.generate_methods_section()     # Compile methods from all figures
manuscript.generate_results_section()     # Auto-generate results text
manuscript.generate_supplementary()       # Create supplementary materials

# Final manuscript compilation
manuscript.compile_manuscript()           # Full LaTeX compilation
manuscript.generate_submission_package()  # Journal-ready submission

# Output: Complete manuscript with:
# - Main text with embedded figures
# - Figure legends with detailed captions
# - Methods section with experimental details
# - Statistical analysis summary
# - Supplementary data package
# - Journal-specific formatting
```

## Best Practices

1. **Always use tracking** - It's enabled by default, don't disable it
2. **Assign unique IDs** - Use the `id` parameter for easy data identification  
3. **Separate styling from metadata** - Use `set_xyt()` for labels, `set_meta()` for scientific metadata
4. **Structure experimental details** - Use dictionaries for machine-readable experimental parameters
5. **Include comprehensive keywords** - Enable AI agents to categorize and process figures automatically
6. **Specify journal styles early** - Set target journal in metadata for automatic formatting
7. **Document statistical methods** - Include complete statistical analysis details in YAML
8. **Plan for AI integration** - Structure metadata for SciTeX ecosystem processing
9. **Use figure-level metadata** - Apply `set_figure_meta()` for multi-panel comprehensive descriptions
10. **Export YAML for reproducibility** - All metadata automatically preserved for AI agent processing

### SciTeX Ecosystem Workflow
```python
# Optimal workflow for AI-powered scientific automation
ax.set_xyt(x='Parameter', y='Response', t='Experiment Results')  # Clean styling
ax.set_meta(                                                     # Structured metadata
    caption='Scientific description with statistical details...',
    methods='Experimental methodology for reproducibility...',
    stats='Complete statistical analysis with significance...',
    keywords=['domain_specific', 'method_tags', 'data_type'],
    experimental_details={'n_samples': 100, 'conditions': 'controlled'},
    journal_style='nature'  # AI-ready journal formatting
)
scitex.io.save(fig, 'experiment.png')  # → Triggers SciTeX ecosystem integration
```

### 🔧 SciTeX Ecosystem Setup
```python
# One-time ecosystem configuration
from scitex.plt.utils._scitex_config import configure_scitex_ecosystem
configure_scitex_ecosystem()

# Creates complete directory structure:
# ~/.scitex/config.yaml              # Central configuration
# ~/proj/SciTeX-Paper/               # LaTeX manuscripts  
# ~/proj/SciTeX-Code/                # AI-generated code
# ~/proj/SigMacro/                   # Advanced visualization
# ~/proj/emacs-claude-code/          # Core AI engine integration
```

### 🚀 Complete Ecosystem Status

**Current Implementation:**
- ✅ **SciTeX Foundation** - Scientific data analysis with YAML metadata
- ✅ **Clean Architecture** - Separation of styling and metadata
- ✅ **AI-Ready Format** - Structured YAML for LLM agent processing
- ✅ **SciTeX Integration** - Unified configuration and workflow
- 🔄 **SciTeX-Code** - AI code generation (in development)
- 🔄 **SciTeX-Paper** - Automated manuscript writing (in development)  
- 🔄 **SigMacro Enhancement** - Publication visualization (in development)
- ✅ **Emacs-Claude Core** - AI development engine integration

**Vision Achievement:**
```
Raw Data → SciTeX Analysis → YAML Metadata → AI Processing → Publication
    ↓           ↓              ↓              ↓            ↓
  CSV        PNG/PDF         YAML       LaTeX/Code    Manuscript
```

This represents the **complete automation of scientific workflow** from experimental data to published paper, powered by AI agents in the LLM era.

---

## Contact
Yusuke Watanabe (ywatanabe@scitex.ai)

**SciTeX Ecosystem**: Revolutionizing scientific computing for the AI age 🚀

<!-- EOF -->