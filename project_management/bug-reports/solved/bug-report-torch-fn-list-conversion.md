<!-- ---
!-- Timestamp: 2025-06-01 11:17:11
!-- Author: ywatanabe
!-- File: /ssh:ywatanabe@sp:/home/ywatanabe/proj/.claude-worktree/scitex_repo/project_management/bug-reports/bug-report-torch-fn-list-conversion.md
!-- --- -->

# Bug Report: torch_fn Decorator List Conversion Issue

## UPDATE: Additional Issue - Nested Decorator Conditions
The user has reported that `torch_fn`, `numpy_fn`, and `pandas_fn` decorators need to work properly in nested conditions as well.

---

# Original Bug Report: torch_fn Decorator List Conversion Issue

## Issue Summary
The `@torch_fn` decorator fails when processing nested lists/tuples because the `to_torch` converter returns a list of tensors instead of converting the entire structure to a single tensor.

## Error Details
```
TypeError: expected Tensor as element 0 in argument 0, but got list
AssertionError: Argument 1 not converted to torch.Tensor: <class 'int'>
```

## Root Cause
In `/src/scitex/decorators/_converters.py`, the `to_torch` function has this logic:

```python
# Handle collections
if isinstance(data, (tuple, list)):
    return [_to_torch(item) for item in data if item is not None]  # Returns list, not tensor!
```

This returns a list of converted items rather than converting the entire list to a tensor, which causes the assertion in `torch_fn` to fail:

```python
# In torch_fn decorator
for arg_index, arg in enumerate(converted_args):
    assert isinstance(arg, torch.Tensor), f"Argument {arg_index} not converted to torch.Tensor: {type(arg)}"
```

## Reproduction
```python
import torch
import scitex

# This fails:
features_pac_z = [[1, 2, 3], [4, 5, 6]]  # Nested list
result = scitex.stats.desc.describe(torch.tensor(features_pac_z))
```

## Proposed Fix
The `to_torch` function should check if the list/tuple contains numeric data and convert it to a tensor:

```python
# Handle collections
if isinstance(data, (tuple, list)):
    # Check if it's a numeric array-like structure
    try:
        # Try to convert to tensor directly
        new_data = torch.tensor(data).float()
        new_data = _try_device(new_data, device)
        if device == "cuda":
            _conversion_warning(data, new_data)
        return new_data
    except:
        # If conversion fails, process items individually
        return [_to_torch(item) for item in data if item is not None]
```

## Temporary Workaround
Users should ensure their input is already a tensor or numpy array before passing to functions decorated with `@torch_fn`:

```python
# Workaround:
features_pac_z = np.array([[1, 2, 3], [4, 5, 6]])
result = scitex.stats.desc.describe(features_pac_z)
```

## Impact
This affects all functions decorated with `@torch_fn` when users pass nested lists/tuples as arguments.

## Priority
High - This breaks a common use case where users pass lists of data to statistical functions.

<!-- EOF -->