# Plotting API Standardization Plan

## Current State

### Naming Inconsistencies
- ✅ `plot_confusion_matrix()` - has `plot_` prefix
- ✅ `plot_confusion_matrix_from_predictions()` - has `plot_` prefix
- ❌ `conf_mat()` - missing `plot_` prefix
- ❌ `learning_curve()` - missing `plot_` prefix
- ❌ `optuna_study()` - missing `plot_` prefix
- ❌ Plotter class methods: `create_*` instead of `plot_*`

### Signature Inconsistencies
Current functions have varying signatures:
- Some return `fig`
- Some return `(fig, ax)`
- Some return `None`
- Some accept `plot=` parameter
- Some accept `ax=` parameter
- Inconsistent parameter ordering

## Proposed Standard

### Naming Convention
All plotting functions should have `plot_` prefix:
```python
# Current → Proposed
conf_mat() → plot_confusion_matrix()  # Already exists
learning_curve() → plot_learning_curve()
optuna_study() → plot_optuna_study()

# Plotter class methods
Plotter.create_confusion_matrix_plot() → Plotter.plot_confusion_matrix()
Plotter.create_roc_curve() → Plotter.plot_roc_curve()
Plotter.create_precision_recall_curve() → Plotter.plot_precision_recall_curve()
```

### Signature Standard
```python
def plot_<name>(
    data,                    # Primary data (required)
    *,                       # Force keyword arguments
    ax=None,                 # Optional axes to plot on
    plot=True,               # Whether to create plot
    save_path=None,          # Optional save path
    **kwargs                 # Additional plot-specific params
) -> tuple[Figure, Axes]:
    """
    Plot <description>.

    Parameters
    ----------
    data : array-like
        Data to plot
    ax : Axes, optional
        Matplotlib axes to plot on. If None, creates new figure.
    plot : bool, default True
        Whether to create the plot. If False, only prepares data.
    save_path : Path, optional
        Path to save the plot
    **kwargs
        Additional plotting parameters

    Returns
    -------
    fig : Figure
        Matplotlib figure
    ax : Axes
        Matplotlib axes
    """
    if not plot:
        return None, None

    if ax is None:
        fig, ax = plt.subplots(figsize=kwargs.get('figsize', (8, 6)))
    else:
        fig = ax.get_figure()

    # Plotting logic here

    if save_path:
        fig.savefig(save_path)

    return fig, ax
```

### Benefits
1. **Consistency**: All functions follow same pattern
2. **Flexibility**: Can plot on existing axes or create new figure
3. **Testability**: `plot=False` allows data preparation without plotting
4. **Composability**: Easy to create multi-panel figures
5. **Discoverability**: `plot_*` prefix makes functions easy to find

## Migration Strategy

### Phase 1: Add New API (Non-Breaking)
1. Add new `plot_*` functions alongside existing ones
2. Mark old functions as deprecated with warnings
3. Update documentation to recommend new functions

### Phase 2: Update Internal Usage
1. Update classification reporters to use new API
2. Update example scripts to use new API
3. Update tests to use new API

### Phase 3: Remove Old API (Breaking)
1. Remove deprecated functions in next major version
2. Update CHANGELOG with breaking changes

## Implementation Checklist

### Core Functions
- [ ] `plot_confusion_matrix()` - already exists, verify signature
- [ ] Deprecate `conf_mat()`, create `plot_confusion_matrix_v2()`
- [ ] Deprecate `learning_curve()`, create `plot_learning_curve()`
- [ ] Deprecate `optuna_study()`, create `plot_optuna_study()`

### Plotter Class Methods
- [ ] Rename `create_confusion_matrix_plot()` → `plot_confusion_matrix()`
- [ ] Rename `create_roc_curve()` → `plot_roc_curve()`
- [ ] Rename `create_precision_recall_curve()` → `plot_pr_curve()`
- [ ] Rename `create_feature_importance_plot()` → `plot_feature_importance()`
- [ ] Rename `create_metrics_visualization()` → `plot_metrics_dashboard()`
- [ ] Rename `create_cv_aggregation_plot()` → `plot_cv_aggregation()`

### Signature Standardization
- [ ] All functions return `(fig, ax)`
- [ ] All functions accept `ax=None`
- [ ] All functions accept `plot=True`
- [ ] All functions accept `save_path=None`
- [ ] Consistent parameter ordering

## Example Usage

```python
# Single plot
fig, ax = plot_confusion_matrix(cm, labels=['A', 'B'])

# Multi-panel figure
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
plot_confusion_matrix(cm, ax=axes[0], labels=['A', 'B'])
plot_roc_curve(y_true, y_proba, ax=axes[1])

# Data preparation only
_, _ = plot_confusion_matrix(cm, plot=False)  # Validates data without plotting

# Using Plotter class
plotter = Plotter()
fig, ax = plotter.plot_confusion_matrix(cm, labels=['A', 'B'])
```

## Current Status

✅ **Completed:**
- Separated metrics from plotting (SoC)
- Centralized metrics in `scitex.ml.metrics`
- Centralized plotting in `scitex.ml.plt`

⏳ **In Progress:**
- API standardization design

❌ **Not Started:**
- Implementation of standardized API
- Deprecation warnings
- Migration of existing code

---
Generated: 2025-10-02 17:45:00
Author: Claude (Anthropic)
