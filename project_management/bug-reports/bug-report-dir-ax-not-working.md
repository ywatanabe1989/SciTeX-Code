# Bug Report: dir(ax) does not work for fig, ax = scitex.plt.subplots()

## Issue
When using `scitex.plt.subplots()`, calling `dir(ax)` does not properly show all available methods, particularly the seaborn methods like `sns_barplot`, `sns_boxplot`, etc.

## Root Cause
The `__dir__` method in `AxisWrapper` was not properly including all methods from parent classes (mixins). It was only including direct class attributes and instance attributes, missing methods from parent classes like `SeabornMixin`, `MatplotlibPlotMixin`, etc.

## Fix Applied
Updated the `__dir__` method in `./src/scitex/plt/_subplots/_AxisWrapper.py` to:
1. Iterate through all parent classes using `__mro__` (Method Resolution Order)
2. Include all methods from parent classes including mixins
3. Add matplotlib axes methods safely
4. Filter out private attributes

## Test Script
```python
import scitex.plt

# Test single subplot
fig, ax = scitex.plt.subplots()
attrs = dir(ax)

# Check for seaborn methods
seaborn_methods = [attr for attr in attrs if attr.startswith('sns_')]
print(f"Found {len(seaborn_methods)} seaborn methods")
print("Seaborn methods:", seaborn_methods[:5], "...")  # Show first 5

# Check for matplotlib methods
mpl_methods = ['plot', 'scatter', 'bar', 'set_xlabel', 'set_ylabel']
for method in mpl_methods:
    if method in attrs:
        print(f"✓ {method} found")
    else:
        print(f"✗ {method} missing")

# Test multiple subplots
fig, axes = scitex.plt.subplots(2, 2)
ax = axes[0, 0]
attrs = dir(ax)
print(f"\nMultiple subplots: dir(ax[0,0]) has {len(attrs)} attributes")
```

## Available Seaborn Methods
After the fix, `dir(ax)` will show these seaborn methods:
- `sns_barplot`
- `sns_boxplot`
- `sns_heatmap`
- `sns_histplot`
- `sns_kdeplot`
- `sns_pairplot`
- `sns_scatterplot`
- `sns_swarmplot`
- `sns_stripplot`
- `sns_violinplot`
- `sns_jointplot`

Note: There is no generic `sns_plot` method. Each seaborn plotting function has its own specific method name.

## Status
✅ FIXED