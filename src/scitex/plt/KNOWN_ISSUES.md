# Known Issues - scitex.plt

## AxisWrapper Incompatibility with axes_grid1.divider

**Status**: Blocking
**Affected**: `stx.plt.subplots()` when used with `mpl_toolkits.axes_grid1`
**Discovered**: 2025-10-02

### Description
When using `stx.plt.subplots()`, the returned axes are wrapped in `AxisWrapper`. However, when matplotlib's `axes_grid1.divider.append_axes()` tries to create new axes (e.g., for colorbars), it fails because `AxisWrapper.__init__()` requires a `track` argument that the divider doesn't provide.

### Error
```python
TypeError: AxisWrapper.__init__() missing 1 required positional argument: 'track'
```

### Affected Code
```python
# This fails:
import scitex as stx
fig, ax = stx.plt.subplots()
divider = make_axes_locatable(ax)
cax = divider.append_axes("right", size="5%", pad=0.1)  # ← Fails here
```

### Workaround
Use `matplotlib.pyplot.subplots()` directly until this is fixed:
```python
import matplotlib.pyplot as plt
fig, ax = plt.subplots()
divider = make_axes_locatable(ax)
cax = divider.append_axes("right", size="5%", pad=0.1)  # ← Works
```

### Impact
- `scitex.ml.plt.plot_conf_mat` - Cannot use stx.plt.subplots (uses divider for colorbar)
- Any plotting function that uses axes_grid1 features

### Root Cause
`AxisWrapper` class requires additional parameters beyond what matplotlib's standard axes initialization provides. The divider assumes standard matplotlib axes interface.

### Proposed Fix
1. Make `track` parameter optional with a default value in `AxisWrapper.__init__()`
2. Or: Detect when axes are being created by divider and handle gracefully
3. Or: Provide a custom axes_class that properly wraps AxisWrapper

---

## Demo Functions Still Use Old API

**Status**: Non-blocking (demos only)
**Discovered**: 2025-10-02

### Description
Demo/test functions in plotting modules may still pass `plt` as first parameter even though it's been deprecated and moved to end as optional parameter.

### Affected
- `scitex.ml.plt.plot_conf_mat.main()`
- `scitex.ml.plt.plot_roc_curve.main()`
- `scitex.ml.plt.plot_pre_rec_curve.main()`

### Workaround
Update demo functions to use new API without `plt` parameter.

---

**Last Updated**: 2025-10-02
**Maintainer**: ywatanabe
