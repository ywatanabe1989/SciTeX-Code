# SciTeX Advanced Features Review - 2025-10-02

## 1. scitex.plt.subplots Wrapper ✅

### Status: Implemented and Feature-Rich

**Location:** `src/scitex/plt/_subplots/_SubplotsWrapper.py`

### Key Features

#### 1.1 Data Tracking
```python
fig, ax = stx.plt.subplots(track=True)  # Default
ax.plot([1, 2, 3], [4, 5, 6], id="my_plot")
ax.scatter([4, 5, 6], [1, 2, 3], id="my_scatter")

# Export plotted data to CSV (SigmaPlot compatible)
df = ax.export_as_csv()
# Columns: my_plot_plot_x, my_plot_plot_y, my_scatter_scatter_x, my_scatter_scatter_y
```

#### 1.2 Enhanced Layouts
- Automatic constrained layout for better spacing
- Prevents colorbar overlap
- Configurable padding: `w_pad`, `h_pad`, `wspace`, `hspace`

#### 1.3 Wrapped Objects
- `FigWrapper`: Enhanced matplotlib Figure
- `AxisWrapper`: Enhanced matplotlib Axes
- `AxesWrapper`: Array of AxisWrapper objects

#### 1.4 Drop-in Replacement
```python
# Can be used exactly like matplotlib.pyplot.subplots
import scitex as stx

# Single axes
fig, ax = stx.plt.subplots()

# Grid of axes
fig, axes = stx.plt.subplots(2, 3, figsize=(12, 8))

# Works with all matplotlib parameters
fig, ax = stx.plt.subplots(sharex=True, sharey=False)
```

### Integration with scitex.io.save

```python
fig, ax = stx.plt.subplots()
ax.plot([1, 2, 3], [4, 5, 6], id="data1")
ax.scatter([4, 5, 6], [1, 2, 3], id="data2")

# Save figure
stx.io.save(fig, "plot.png")

# Save plotted data as CSV
ax.export_as_csv("data.csv")
```

### Architecture

```
SubplotsWrapper
├── __call__(*args, track=True, **kwargs)
│   ├── Calls plt.subplots() (native matplotlib)
│   ├── Wraps Figure → FigWrapper
│   ├── Wraps Axes → AxisWrapper
│   └── Returns (FigWrapper, AxisWrapper/AxesWrapper)
│
FigWrapper(fig_mpl)
├── Wraps matplotlib.figure.Figure
├── .axes → AxisWrapper or AxesWrapper
└── Enhanced methods for SciTeX features

AxisWrapper(fig, ax_mpl, track=True)
├── Wraps matplotlib.axes.Axes
├── Tracks all plot calls (plot, scatter, bar, etc.)
├── export_as_csv() → DataFrame
└── Compatible with all matplotlib Axes methods
```

### Usage Examples

#### Basic Plotting with Export
```python
import scitex as stx

fig, ax = stx.plt.subplots()
ax.plot([1, 2, 3], [4, 5, 6], id="line1", label="Data 1")
ax.plot([4, 5, 6], [1, 2, 3], id="line2", label="Data 2")
ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.legend()

# Save plot
stx.io.save(fig, "my_plot.png")

# Export data
data_df = ax.export_as_csv("my_data.csv")
print(data_df)
#    line1_plot_x  line1_plot_y  line2_plot_x  line2_plot_y
# 0           1.0           4.0           4.0           1.0
# 1           2.0           5.0           5.0           2.0
# 2           3.0           6.0           6.0           3.0
```

#### Multi-Panel with Individual Exports
```python
fig, axes = stx.plt.subplots(1, 2, figsize=(12, 5))

# Left panel
axes[0].plot([1, 2, 3], [4, 5, 6], id="left_data")
axes[0].set_title("Left Panel")

# Right panel
axes[1].scatter([4, 5, 6], [1, 2, 3], id="right_data")
axes[1].set_title("Right Panel")

# Save figure
stx.io.save(fig, "two_panel.png")

# Export data from each panel
left_data = axes[0].export_as_csv("left_panel_data.csv")
right_data = axes[1].export_as_csv("right_panel_data.csv")
```

#### Disable Tracking for Performance
```python
# Large datasets - disable tracking
fig, ax = stx.plt.subplots(track=False)
ax.plot(large_x_array, large_y_array)
stx.io.save(fig, "large_plot.png")
# No CSV export available (track=False)
```

### Benefits

1. **Data Provenance**: Plot data can be exported alongside visualizations
2. **Reproducibility**: CSV exports enable data sharing and verification
3. **SigmaPlot Compatible**: CSV format works with scientific plotting software
4. **Transparent**: Behaves exactly like matplotlib.pyplot.subplots
5. **Lazy Loading**: No performance penalty when not used

## 2. scitex.io.save ✅

### Status: Implemented, `smart_spath` Not Yet Added

**Location:** `src/scitex/io/_save.py`

### Current Features

#### 2.1 Universal Save Function
Saves any object to appropriate format based on extension:

```python
stx.io.save(obj, "path/to/file.ext")
```

**Supported Formats:**
- **Images**: PNG, JPG, SVG, PDF (matplotlib figures)
- **Data**: CSV, NPY, NPZ, HDF5, Zarr, Excel
- **Serialization**: PKL, Joblib, JSON, YAML
- **ML Models**: PTH (PyTorch), MAT (MATLAB), CBM (CatBoost)
- **Documents**: HTML, TeX, BibTeX
- **Video**: MP4

#### 2.2 Automatic CSV Export for Plots
```python
fig, ax = stx.plt.subplots()
ax.plot([1, 2, 3], [4, 5, 6], id="data")

# Saves both PNG and CSV automatically
stx.io.save(fig, "plot.png")
# Creates: plot.png, plot.csv
```

#### 2.3 Options
- `makedirs=True`: Create parent directories
- `verbose=True`: Print save confirmation
- `symlink_from_cwd=True`: Create symlink from current directory
- `dry_run=True`: Test without saving
- `no_csv=True`: Disable automatic CSV export for plots

### Missing Feature: smart_spath

**Proposed:** Intelligent path handling based on context

```python
# Current (manual path management)
stx.io.save(fig, "./results/experiment1/plots/confusion_matrix.png")

# Proposed with smart_spath=True
stx.io.save(fig, "confusion_matrix.png", smart_spath=True)
# Automatically determines save location based on:
# - Current session
# - Experiment context
# - Project structure
# - Configuration file
```

**Implementation Ideas:**
1. Read from config file (e.g., `CONFIG.yaml`)
2. Use session-based directories
3. Integrate with experiment tracking
4. Support templates: `{session}/{experiment}/{timestamp}_{filename}`

## 3. Classification Reporter + LabelEncoder

### Status: Not Implemented

**Current State:**
- Classification reporters handle integer labels with string names
- Manual label handling in `_normalize_labels()` function
- Works but could be more robust

**Proposed Enhancement:**
```python
from sklearn.preprocessing import LabelEncoder

class SingleTaskClassificationReporter:
    def __init__(self, ..., auto_encode_labels=True):
        self.label_encoder = LabelEncoder() if auto_encode_labels else None

    def calculate_metrics(self, y_true, y_pred, labels=None, ...):
        # Auto-encode if needed
        if self.label_encoder:
            y_true_encoded = self.label_encoder.fit_transform(y_true)
            y_pred_encoded = self.label_encoder.transform(y_pred)
            label_names = self.label_encoder.classes_
        else:
            # Current manual handling
            y_true_encoded, y_pred_encoded, label_names = self._normalize_labels(...)
```

**Benefits:**
- More robust label handling
- Standard sklearn approach
- Handles edge cases automatically
- Inverse transform available: `label_encoder.inverse_transform()`

## Recommendations

### Priority 1: Documentation
- ✅ Document `scitex.plt.subplots` advanced features
- ✅ Document `scitex.io.save` current capabilities
- [ ] Create user guide with examples

### Priority 2: smart_spath Implementation
- [ ] Design configuration schema
- [ ] Implement context-aware path resolution
- [ ] Add template support
- [ ] Integrate with experiment tracking

### Priority 3: LabelEncoder Integration
- [ ] Add `auto_encode_labels` parameter to reporters
- [ ] Integrate sklearn LabelEncoder
- [ ] Update tests
- [ ] Update documentation

### Priority 4: API Standardization
- [ ] Implement `plot_*` naming convention
- [ ] Standardize signatures: `ax=None, plot=True`
- [ ] Always return `fig`
- [ ] Delegate saving to `stx.io.save`

## Summary

**Existing Advanced Features:**
- ✅ `scitex.plt.subplots`: Fully implemented with data tracking and CSV export
- ✅ `scitex.io.save`: Universal save function with automatic CSV for plots

**Missing Features:**
- ❌ `smart_spath`: Context-aware path management
- ❌ LabelEncoder integration in reporters

**Next Steps:**
1. Update `scitex.ml.plt` to use `scitex.plt.subplots`
2. Implement `smart_spath` option
3. Integrate LabelEncoder for robust label handling
4. Complete API standardization

---
Generated: 2025-10-02 18:30:00
Author: Claude (Anthropic)
