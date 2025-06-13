# Bug Report: plot_line Method Not Implemented in export_as_csv

## Description
The `export_as_csv` function in `/src/scitex/plt/_subplots/_export_as_csv.py` throws warnings when encountering a `plot_line` method, indicating it's not implemented. This causes data loss when trying to export plotting data.

## Error Messages
```
UserWarning: Method 'plot_line' is not implemented in export_as_csv. Record id: 0, args length: 1
UserWarning: No valid plotting records could be formatted from 1 records. Failed records: [id=0, method=plot_line (returned empty)]. Check that supported plot types (plot, scatter, bar, hist, boxplot, etc.) are being used.
```

## Root Cause Analysis
Looking at the `format_record` function in `_export_as_csv.py`, there's no handler for the `plot_line` method. The function has handlers for many matplotlib methods including:
- `plot`
- `scatter`
- `bar`, `barh`
- `hist`
- `boxplot`, `violinplot`
- etc.

But `plot_line` is missing from the implementation.

## Impact
- Users cannot export data from plots created with `plot_line` method
- Data is lost when trying to save plotting history
- Warnings clutter the output

## Proposed Solution

Add a handler for `plot_line` in the `format_record` function. Based on the pattern for other plotting methods, it should be similar to the `plot` method handler:

```python
elif method == "plot_line":
    # Convert torch tensors to numpy arrays if needed
    def to_numpy(data):
        if hasattr(data, 'numpy'):  # torch tensor
            return data.detach().numpy() if hasattr(data, 'detach') else data.numpy()
        elif hasattr(data, 'values'):  # pandas series/dataframe
            return data.values
        else:
            return np.asarray(data)
    
    # Extract x, y data - assuming plot_line has similar signature to plot
    if len(args) == 1:
        # Single argument: y values with implicit x
        y = to_numpy(args[0])
        x = np.arange(len(y))
    elif len(args) >= 2:
        x = to_numpy(args[0])
        y = to_numpy(args[1])
    else:
        return None
        
    # Format the data
    df = pd.DataFrame({f"{id}_{method}_x": x, f"{id}_{method}_y": y})
    return df
```

## Workaround
Users can use the standard `plot` method instead of `plot_line` until this is fixed.

## Additional Notes
- Need to verify the exact signature and behavior of `plot_line` method
- Should check if there are other custom plotting methods that need export support
- Consider adding a more generic fallback handler for unknown methods that follow common patterns

## Environment
- File: `/src/scitex/plt/_subplots/_export_as_csv.py`
- Lines affected: Around line 671 (warning location)
- Function: `format_record`

## Priority
Medium - Causes data loss but has a workaround (use `plot` instead of `plot_line`)