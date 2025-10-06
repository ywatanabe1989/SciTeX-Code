# SciTeX Plotting API Best Practices

## Reference Implementation

The `scitex.stats.tests` module demonstrates excellent API design patterns that should be followed across all SciTeX plotting functions.

### Example: `test_pearson()` from `scitex.stats.tests.correlation`

```python
def test_pearson(
    x: Union[np.ndarray, pd.Series],
    y: Union[np.ndarray, pd.Series],
    var_x: str = "x",
    var_y: str = "y",
    alternative: Literal["two-sided", "less", "greater"] = "two-sided",
    alpha: float = 0.05,
    plot: bool = False,                              # ✓ plot parameter
    ax: Optional[matplotlib.axes.Axes] = None,        # ✓ ax parameter
    return_as: Literal["dict", "dataframe"] = "dict",
    decimals: int = 3,
    verbose: bool = False,
) -> Union[dict, pd.DataFrame]:
```

### Key Design Patterns

#### 1. `plot=False` Parameter ✓
- **Purpose**: Control whether visualization is generated
- **Default**: `False` (computation only, no plotting)
- **Benefits**:
  - Computation and visualization are decoupled
  - Can run tests/calculations without display
  - Useful for batch processing, testing, headless environments

#### 2. `ax=None` Parameter ✓
- **Purpose**: Allow plotting on existing axes
- **Default**: `None` (creates new figure if `plot=True`)
- **Behavior**:
  ```python
  if ax is None and plot:
      fig, ax = plt.subplots(figsize=(8, 6))
  elif ax is not None:
      plot = True  # Auto-enable plotting if ax provided
      fig = ax.get_figure()
  ```
- **Benefits**:
  - Enables multi-panel figures
  - Composable with other plots
  - Flexible layout control

#### 3. Return Values
```python
# From test_pearson implementation
if plot:
    # Returns results + figure
    return results, fig
else:
    # Returns only results
    return results
```

## Recommended Standard for scitex.ml.plt

### Function Signature Template

```python
def plot_<name>(
    data,                                    # Primary data
    *,                                       # Force keyword args
    ax: Optional[matplotlib.axes.Axes] = None,
    plot: bool = True,
    title: Optional[str] = None,
    labels: Optional[List[str]] = None,
    **kwargs
) -> Figure:
    """
    Plot <description>.

    Parameters
    ----------
    data : array-like
        Data to plot
    ax : matplotlib.axes.Axes, optional
        Axes to plot on. If None and plot=True, creates new figure.
    plot : bool, default True
        Whether to create visualization. If False, only validates/processes data.
    title : str, optional
        Plot title
    labels : list of str, optional
        Labels for data
    **kwargs
        Additional plotting parameters

    Returns
    -------
    fig : Figure
        Matplotlib figure (always returned, even if plot=False)

    Notes
    -----
    Plotting functions do NOT handle file saving. Use scitex.io.save() for that:

    >>> fig = plot_confusion_matrix(cm)
    >>> stx.io.save(fig, "confusion_matrix.png")
    """
    # Handle axes creation
    if ax is not None:
        # User provided ax - plot on it and return its figure
        fig = ax.get_figure()
    else:
        # No ax provided - create new figure with stx.plt.subplots
        fig, ax = stx.plt.subplots(figsize=kwargs.get('figsize', (8, 6)))

    if plot:
        # Plotting logic ONLY - NO FILE I/O
        # ...
        pass

    return fig  # Always return fig only
```

### Key Differences from stats.tests

1. **Default `plot=True` in plotting modules**
   - `scitex.stats.tests`: `plot=False` (computation-focused, returns `(results, fig)`)
   - `scitex.ml.plt`: `plot=True` (visualization-focused, returns `fig` only)

2. **Return value**
   - `scitex.stats.tests`: `(results, fig)` - computation + visualization
   - `scitex.ml.plt`: `fig` only - visualization focused
   - User already has `ax` if they provided it
   - Can get ax from `fig.axes` if needed

## Migration Checklist for scitex.ml.plt

### Plotter Class Methods

Current → Proposed:
```python
# Before
Plotter.create_confusion_matrix_plot(cm, labels, save_path, title)
# Returns: Optional[Any]

# After
Plotter.plot_confusion_matrix(cm, *, ax=None, plot=True, labels=None, save_path=None, title=None)
# Returns: tuple[Optional[Figure], Optional[Axes]]
```

### Standalone Functions

```python
# Before
conf_mat(plt, cm, y_true, y_pred, ...)
# Requires passing plt object, inconsistent return

# After
plot_confusion_matrix(cm, *, ax=None, plot=True, labels=None, ...)
# Returns: tuple[Optional[Figure], Optional[Axes]]
```

## Usage Examples

### Single Plot
```python
fig = plot_confusion_matrix(cm, labels=['A', 'B', 'C'])
stx.io.save(fig, "confusion_matrix.png")
```

### Multi-Panel Figure
```python
fig, axes = plt.subplots(2, 2, figsize=(12, 10))
plot_confusion_matrix(cm, ax=axes[0, 0], labels=['A', 'B'])
plot_roc_curve(y_true, y_proba, ax=axes[0, 1])
plot_pr_curve(y_true, y_proba, ax=axes[1, 0])
plot_feature_importance(importances, ax=axes[1, 1])
stx.io.save(fig, "multi_panel.png")
```

### Data Processing Only
```python
# Validate inputs without full rendering
fig = plot_confusion_matrix(cm, plot=False)
# Still creates figure but minimal rendering
```

### Integration with Plotter Class
```python
plotter = Plotter()
fig = plotter.plot_confusion_matrix(cm, labels=['A', 'B', 'C'])
stx.io.save(fig, "confusion_matrix.png")

# Or on existing axes
fig, axes = plt.subplots(1, 2)
plotter.plot_confusion_matrix(cm, ax=axes[0])
plotter.plot_roc_curve(y_true, y_proba, ax=axes[1])
stx.io.save(fig, "two_plots.png")
```

## Benefits

1. **Consistency**: Same pattern across entire SciTeX codebase
2. **Flexibility**: Works standalone or as part of multi-panel figures
3. **Testability**: Can validate without plotting in tests
4. **Discoverability**: Clear naming (`plot_*`) and signatures
5. **Composability**: Easy to build complex visualizations
6. **Backward Compatibility**: Old functions deprecated but still work

## Implementation Status

✅ **Reference Implementation**: `scitex.stats.tests` (already follows pattern)
📝 **Documentation**: This guide
⏳ **Implementation**: Planned for `scitex.ml.plt`

---
Generated: 2025-10-02 18:00:00
Author: Claude (Anthropic)
Reference: `src/scitex/stats/tests/correlation/_test_pearson.py`
