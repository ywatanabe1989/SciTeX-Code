# Migration to `ax=` Parameter Pattern

## Summary
Statistical test functions now use an `ax=` parameter instead of `plot=` for visualization. This provides better flexibility for users to control figure layout while keeping the API simple.

## Key Changes

### Before (old pattern with `plot=`)
```python
def test_function(..., plot: bool = False, ...) -> Union[dict, pd.DataFrame, Tuple]:
    # ... test logic ...

    fig = None
    if plot:
        fig = _plot_function(...)

    if plot:
        return result, fig
    else:
        return result
```

### After (new pattern with `ax=`)
```python
def test_function(..., ax: Optional[matplotlib.axes.Axes] = None, ...) -> Union[dict, pd.DataFrame]:
    # ... test logic ...

    if ax is not None:
        _plot_function(..., ax)

    return result  # Always return result only
```

## Benefits

1. **Simpler return type**: Functions always return test results only (never tuples)
2. **User controls figures**: Users create their own figures and axes
3. **Subplot integration**: Easy to place multiple tests in one figure
4. **Matplotlib convention**: Follows standard matplotlib pattern

## Updated Files

### Completed
- ✅ `tests/parametric/_test_ttest.py` (all 3 functions: ind, rel, 1samp)
- ✅ `tests/parametric/_test_anova.py`

### Remaining (16 files with `plot=` parameter)
- `tests/nonparametric/_test_brunner_munzel.py`
- `tests/nonparametric/_test_friedman.py`
- `tests/nonparametric/_test_kruskal.py`
- `tests/nonparametric/_test_mannwhitneyu.py`
- `tests/nonparametric/_test_wilcoxon.py`
- `tests/parametric/_test_anova_2way.py`
- `tests/parametric/_test_anova_rm.py`
- `tests/correlation/_test_kendall.py`
- `tests/correlation/_test_pearson.py`
- `tests/correlation/_test_spearman.py`
- `tests/categorical/_test_chi2.py`
- `tests/categorical/_test_cochran_q.py`
- `tests/categorical/_test_fisher.py`
- `tests/categorical/_test_mcnemar.py`
- `tests/normality/_test_ks.py`
- `tests/normality/_test_shapiro.py`

## Usage Examples

### Old way (with `plot=True`)
```python
# Returns tuple - awkward
result, fig = test_ttest_ind(x, y, plot=True)
plt.show()
```

### New way (with `ax=`)
```python
# Simple: always returns result
result = test_ttest_ind(x, y)

# With visualization
fig, ax = plt.subplots()
result = test_ttest_ind(x, y, ax=ax)
plt.show()

# In subplots
fig, axes = plt.subplots(2, 2)
result1 = test_ttest_ind(x1, y1, ax=axes[0, 0])
result2 = test_ttest_ind(x2, y2, ax=axes[0, 1])
result3 = test_anova([g1, g2, g3], ax=axes[1, 0])
plt.tight_layout()
```

## Implementation Checklist

For each function that needs migration:

1. **Function signature**:
   - [ ] Replace `plot: bool = False` with `ax: Optional[matplotlib.axes.Axes] = None`
   - [ ] Add `import matplotlib.axes` at top
   - [ ] Remove `Tuple` from return type annotation

2. **Docstring**:
   - [ ] Update Parameters section to describe `ax=`
   - [ ] Update Returns section to remove figure return
   - [ ] Update Examples to show new usage pattern

3. **Function body**:
   - [ ] Replace `if plot:` with `if ax is not None:`
   - [ ] Pass `ax` to plotting helper function
   - [ ] Remove `fig = None` and tuple return logic
   - [ ] Always `return result` (never return tuple)

4. **Helper plotting function**:
   - [ ] Add `ax` as last parameter
   - [ ] Remove `fig, axes = plt.subplots(...)` creation
   - [ ] Plot directly on provided `ax`
   - [ ] Remove `return fig`

5. **Examples in main()**:
   - [ ] Update any `plot=True` usage to create fig/ax first

## Notes

- Posthoc functions (tukey, games-howell, dunnett) don't have plotting - no changes needed
- The `ax=` parameter is always optional - if not provided, no plotting occurs
- Functions should not create figures internally - user's responsibility
