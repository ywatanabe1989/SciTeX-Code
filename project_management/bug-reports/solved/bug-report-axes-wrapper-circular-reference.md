# Bug Report: AxisWrapper Circular Reference Causes IPython/ipdb Crash

## Description
When using `scitex.plt.subplots()` and trying to inspect the returned axis object with `ax?` in ipdb, it causes a crash with error: "Tcl_AsyncDelete: async handler deleted by the wrong thread"

## Steps to Reproduce
```python
import scitex
fig, ax = scitex.plt.subplots()
ax?  # This causes crash in ipdb
```

## Root Cause Analysis
The issue is in `/src/scitex/plt/_subplots/_AxisWrapper.py` in the `__dir__` method:

```python
def __dir__(self):
    # Combine attributes from both self and the wrapped matplotlib figure
    attrs = set(dir(self.__class__))
    attrs.update(object.__dir__(self))
    attrs.update(dir(self._axes_mpl))  # <-- This line can cause circular reference
    return sorted(attrs)
```

When IPython/ipdb tries to introspect the object, it calls `__dir__` which then calls `dir(self._axes_mpl)`. This can create a circular reference between the wrapper and the matplotlib axes object, especially in interactive environments with different threads.

## Proposed Solution
Modify the `__dir__` method to avoid the circular reference:

```python
def __dir__(self):
    # Combine attributes from both self and the wrapped matplotlib figure
    attrs = set(dir(self.__class__))
    attrs.update(object.__dir__(self))
    
    # Safely get matplotlib axes attributes without triggering circular reference
    try:
        # Use __dict__ instead of dir() to avoid recursive calls
        if hasattr(self._axes_mpl, '__dict__'):
            attrs.update(self._axes_mpl.__dict__.keys())
        # Add common matplotlib axes methods manually if needed
        attrs.update(['plot', 'scatter', 'bar', 'set_xlabel', 'set_ylabel', 'set_title', 'legend'])
    except Exception:
        # If any error occurs, just skip matplotlib attributes
        pass
    
    return sorted(attrs)
```

## Impact
- Severity: High - Causes complete crash when debugging
- Affected versions: Current
- Workaround: Avoid using `?` or `help()` on axis objects in interactive environments

## Environment
- Python 3.10
- IPython/ipdb interactive environment
- Threading issue with Tcl/Tk backend

## Related Files
- `/src/scitex/plt/_subplots/_AxisWrapper.py`
- `/src/scitex/plt/_subplots/_AxesWrapper.py`
- `/src/scitex/plt/_subplots/_FigWrapper.py`