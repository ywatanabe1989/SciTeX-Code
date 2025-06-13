<!-- ---
!-- Timestamp: 2025-05-30 05:57:52
!-- Author: ywatanabe
!-- File: /ssh:ywatanabe@sp:/home/ywatanabe/proj/mngs_repo/project_management/bug-report/mngs_subplot_bug_report.md
!-- --- -->

# Bug Report: mngs.plt.subplots returns flattened array for 2D grid

## Issue Description
When calling `mngs.plt.subplots(rows, cols)` with rows > 1 and cols > 1, the function returns a flattened 1D array of axes instead of a 2D array as expected from matplotlib's behavior.

## Expected Behavior
```python
fig, axes = mngs.plt.subplots(4, 3)
# Should allow: axes[0, 0], axes[1, 2], etc.
```

## Actual Behavior
```python
fig, axes = mngs.plt.subplots(4, 3)
# Returns flattened array, must use: axes[0], axes[1], ..., axes[11]
```

## Impact
This breaks compatibility with standard matplotlib code patterns and requires rewriting axes indexing when migrating code to use mngs framework.

## Reproduction
```python
import mngs
fig, axes = mngs.plt.subplots(4, 3, figsize=(16, 12))
ax = axes[0, 0]  # AttributeError: 'numpy.ndarray' object has no attribute 'plot'
```

## Suggested Fix
Either:
1. Return a 2D array when rows > 1 and cols > 1 (matching matplotlib behavior)
2. Document this behavior clearly in the mngs documentation

## Workaround
Currently must use flattened indexing:
```python
# For a 4x3 grid:
ax = axes[row * 3 + col]  # Instead of axes[row, col]
```

<!-- EOF -->