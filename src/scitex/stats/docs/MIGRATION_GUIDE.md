# Statistical Test Functions: API Migration Guide

## New Standard Pattern

All statistical test functions now follow this pattern:
- `plot=False, ax=None, verbose=False`
- Violin + swarm plots (scatter in front)
- Always return results only (never tuples)

## Completed Files ✅

### Parametric Tests
- `tests/parametric/_test_ttest.py` (3 functions)
- `tests/parametric/_test_anova.py`

### Nonparametric Tests
- `tests/nonparametric/_test_brunner_munzel.py`
- `tests/nonparametric/_test_mannwhitneyu.py`
- `tests/nonparametric/_test_wilcoxon.py`
- `tests/nonparametric/_test_kruskal.py`
- `tests/nonparametric/_test_friedman.py`

## Files Remaining (11)

### Parametric Tests
- `tests/parametric/_test_anova_2way.py`
- `tests/parametric/_test_anova_rm.py`

### Correlation Tests
- `tests/correlation/_test_kendall.py`
- `tests/correlation/_test_pearson.py`
- `tests/correlation/_test_spearman.py`

### Categorical Tests
- `tests/categorical/_test_chi2.py`
- `tests/categorical/_test_cochran_q.py`
- `tests/categorical/_test_fisher.py`
- `tests/categorical/_test_mcnemar.py`

### Normality Tests
- `tests/normality/_test_ks.py`
- `tests/normality/_test_shapiro.py`

## Implementation Checklist

For each function:

### 1. Function Signature
```python
def test_function(
    ...,
    plot: bool = False,
    ax: Optional[matplotlib.axes.Axes] = None,
    return_as: Literal['dict', 'dataframe'] = 'dict',
    verbose: bool = False
) -> Union[dict, pd.DataFrame]:
```

### 2. Imports
```python
from typing import Union, Optional, Literal
import matplotlib.axes
```

### 3. Docstring Parameters
```python
    plot : bool, default False
        Whether to generate visualization
    ax : matplotlib.axes.Axes, optional
        Axes object to plot on. If None and plot=True, creates new figure.
        If provided, automatically enables plotting.
    return_as : {'dict', 'dataframe'}, default 'dict'
        Output format
    verbose : bool, default False
        Whether to print test results

    Returns
    -------
    results : dict or DataFrame
        Test results (never returns tuple)
```

### 4. Docstring Examples
```python
    Examples
    --------
    >>> # Basic usage
    >>> result = test_function(x, y)

    >>> # With auto-created figure
    >>> result = test_function(x, y, plot=True)

    >>> # Plot on existing axes
    >>> fig, ax = plt.subplots()
    >>> result = test_function(x, y, ax=ax)

    >>> # With verbose output
    >>> result = test_function(x, y, verbose=True)
```

### 5. Function Body (before return)
```python
    # Log results if verbose
    if verbose:
        logger.info(f"Test Name: statistic = {stat:.3f}, p = {pvalue:.4f} {p2stars(pvalue)}")
        logger.info(f"Effect size = {effect_size:.3f} ({interpretation})")

    # Auto-enable plotting if ax is provided
    if ax is not None:
        plot = True

    # Generate plot if requested
    if plot:
        if ax is None:
            fig, ax = stx.plt.subplots()
        _plot_function(..., ax)

    # Convert to requested format
    if return_as == 'dataframe':
        result = force_dataframe(result)

    return result
```

### 6. Plotting Function (Violin + Swarm)
```python
def _plot_function(..., ax):
    """Create violin+swarm visualization on given axes."""
    positions = [0, 1]
    data = [x, y]
    colors = ["C0", "C1"]

    # Violin plot (background, transparent)
    parts = ax.violinplot(
        data,
        positions=positions,
        widths=0.6,
        showmeans=False,
        showmedians=False,
        showextrema=False,
    )

    for i, pc in enumerate(parts["bodies"]):
        pc.set_facecolor(colors[i])
        pc.set_alpha(0.3)
        pc.set_edgecolor(colors[i])
        pc.set_linewidth(1.5)

    # Swarm plot (foreground - scatter in front!)
    np.random.seed(42)
    for i, vals in enumerate(data):
        y_vals = vals
        x_vals = np.random.normal(positions[i], 0.04, size=len(vals))
        ax.scatter(
            x_vals, y_vals,
            alpha=0.6,
            s=40,
            color=colors[i],
            edgecolors='white',
            linewidths=0.5,
            zorder=3  # In front!
        )

    # Add mean/median lines
    for i, vals in enumerate(data):
        central_tendency = np.mean(vals)  # or np.median(vals)
        ax.hlines(
            central_tendency,
            positions[i] - 0.3,
            positions[i] + 0.3,
            colors='black',
            linewidth=2,
            zorder=4
        )

    # Significance stars
    y_max = max(np.max(x), np.max(y))
    y_min = min(np.min(x), np.min(y))
    y_range = y_max - y_min
    sig_y = y_max + y_range * 0.05

    ax.plot([0, 1], [sig_y, sig_y], 'k-', linewidth=1.5)
    ax.text(
        0.5, sig_y + y_range * 0.02,
        result['pstars'],
        ha='center', va='bottom',
        fontsize=14, fontweight='bold'
    )

    ax.set_xticks(positions)
    ax.set_xticklabels([var_x, var_y])
    ax.set_ylabel('Value')
    ax.set_title(f"Test\nstat = {result['statistic']:.2f}, p = {result['pvalue']:.4f} {result['pstars']}")
    ax.grid(True, alpha=0.3, axis='y')
```

### 7. Update main() Function
Replace manual logger.info calls with `verbose=True`:
```python
# Before
result = test_function(x, y)
logger.info(f"stat = {result['statistic']:.3f}")
logger.info(f"p = {result['pvalue']:.4f}")

# After
result = test_function(x, y, verbose=True)
```

Replace manual plotting with `plot=True`:
```python
# Before
fig, ax = plt.subplots()
result = test_function(x, y, ax=ax)
stx.io.save(fig, './demo.jpg')

# After
result = test_function(x, y, plot=True, verbose=True)
```

## Key Principles

1. **Consistent API**: All test functions have the same parameter pattern
2. **Simple default**: No plotting, no logging by default
3. **Clean return**: Always return results only, never tuples
4. **Flexible plotting**:
   - `plot=True` → auto-create figure
   - `ax=provided` → use that axes (auto-enables plotting)
5. **Violin + Swarm**: Scatter points in front (zorder=3), not behind
6. **Verbose logging**: Implemented in function, not in main()
7. **User controls figures**: They can use `plt.gcf()` if needed

## Testing Pattern

```python
# Test all modes
result1 = test_function(x, y)  # No plot, no verbose
result2 = test_function(x, y, verbose=True)  # Verbose only
result3 = test_function(x, y, plot=True)  # Plot only
result4 = test_function(x, y, plot=True, verbose=True)  # Both

# Manual control
fig, axes = plt.subplots(2, 2)
test_function(x1, y1, ax=axes[0,0])  # Auto-enables plotting
test_function(x2, y2, ax=axes[0,1])
```

## Notes

- Import `stx.plt` not raw `plt` for consistency
- Use `logger.info()` not `print()` for verbose output
- Seed random for scatter: `np.random.seed(42)`
- Scatter zorder=3, mean lines zorder=4
- White edges on scatter: `edgecolors='white', linewidths=0.5`
