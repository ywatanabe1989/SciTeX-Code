<!-- ---
!-- title: ./scitex_repo/src/scitex/decorators/README.md
!-- author: ywatanabe
!-- date: 2024-11-25 13:37:09
!-- --- -->


# Decorators

**Note**: While these decorators can be complex when used together, they provide powerful functionality for handling various data types gracefully. The recent updates have improved their ability to handle edge cases and preserve important parameter types.

## 🎯 Auto-Ordering Feature (NEW)

To eliminate decorator ordering complexity, we now provide an **auto-ordering system** that automatically enforces the correct decorator order regardless of how you write them in your code!

**Note**: Auto-ordering is opt-in to maintain backward compatibility.

### Enable Auto-Ordering

```python
from scitex.decorators import enable_auto_order

# Enable auto-ordering at the start of your script
enable_auto_order()

# Now decorators will be automatically ordered correctly!
@torch_fn          # Will be reordered automatically
@batch_fn          # Even if written in "wrong" order
def my_function(x):
    return x.mean()
```

### How It Works

The auto-ordering system ensures decorators are always applied in this optimal order:
1. **Type conversion decorators** (`@torch_fn`, `@numpy_fn`, `@pandas_fn`) - applied first
2. **Batch processing** (`@batch_fn`) - applied last

This means you can write decorators in any order and they'll work correctly:

```python
# All of these will work identically with auto-ordering enabled:
@batch_fn
@torch_fn
def func1(x): ...

@torch_fn
@batch_fn  
def func2(x): ...

# Even multiple type converters are handled correctly
@batch_fn
@numpy_fn
@torch_fn
def func3(x): ...
```

### Disable Auto-Ordering

If needed, you can disable auto-ordering and return to manual control:

```python
from scitex.decorators import disable_auto_order
disable_auto_order()
```

## Manual Decorator Ordering (Legacy)

If auto-ordering is disabled, decorators must be manually ordered correctly:

1. **Type conversion decorators** (`@torch_fn`, `@numpy_fn`, `@pandas_fn`) - apply first (bottom)
2. **Batch processing** (`@batch_fn`) - apply last (top)

Example:
```python
@batch_fn          # Applied second (processes batches)
@torch_fn          # Applied first (converts to tensor)
def my_function(x):
    return x.mean()
```

## Recent Improvements 🚀

### Better Type Handling
- **Nested Lists/Tuples**: Decorators now properly handle nested structures without errors
- **Scalar Preservation**: Scalars (int, float, bool, str) are preserved and not converted
- **Dimension Tuples**: Parameters like `dim=(0, 1)` are kept as tuples, not converted to tensors
- **Parameter Conflicts**: Fixed axis/dim parameter conflicts in multi-decorator scenarios

### Enhanced Batch Processing
- **Scalar Results**: `batch_fn` now correctly handles functions that return scalars
- **Smart Stacking**: Automatically chooses the right stacking method (stack vs vstack)
- **Parameter Compatibility**: Only passes `batch_size` to functions that accept it

### Example of Improved Handling

```python
# These now work correctly without errors:
@torch_fn
def process_nested(x):
    # Works with nested lists like [[1, 2], [3, 4]]
    return torch.tensor(x).mean()

@batch_fn
@numpy_fn
def compute_stats(data, dim=(0, 1)):
    # dim tuple is preserved, not converted
    return np.mean(data, axis=dim)

@torch_fn
def keep_scalars(x, scale=2.5):
    # scale remains a float, not converted to tensor
    return x * scale
```

## batch_fn
A decorator for processing data in batches.

### Features
- Requires explicit `batch_size` keyword argument
  - Automatically applies `batch_size=-1` if not specified
- Supports multiple batch dimensions: 
  - Single dimension: `batch_size=4`
  - Multiple dimensions: `batch_size=(4, 8)`
- Guarantees consistent output regardless of batch size
- Supports NumPy arrays, PyTorch tensors, Pandas DataFrames
- **NEW**: Handles scalar results correctly
- **NEW**: Smart parameter passing (only passes batch_size when accepted)

## torch_fn
A decorator for PyTorch function compatibility.

### Features
- Handles nested torch_fn decorators
- Automatically converts `axis=X` to `dim=X` for torch functions
- Automatically applies `device="cuda"` if available
- Preserves input data types in output:
  - NumPy arrays → NumPy arrays
  - Pandas objects → Pandas objects
  - Xarray objects → Xarray objects
- **NEW**: Handles nested lists/tuples gracefully
- **NEW**: Preserves scalar parameters (int, float, bool, str)
- **NEW**: Preserves dimension tuples like `dim=(0, 1)`
- **NEW**: Fixed axis/dim parameter conflicts

### Example
```python
@torch_fn
def my_mean(x, dim=None):
    # Works with nested lists, preserves dim tuples
    return x.mean(dim=dim) if dim is not None else x.mean()
```

## numpy_fn
A decorator for NumPy function compatibility.

### Features
- Automatically converts torch tensors to numpy arrays
- Preserves input data types in output
- Handles axis-related parameter conversions
- **NEW**: Better handling of mixed data types
- **NEW**: Preserves scalar parameters
- **NEW**: Works seamlessly with batch_fn

## pandas_fn
A decorator for Pandas function compatibility.

### Features
- Automatically converts input data to pandas objects
- Preserves index and column information
- Handles DataFrame and Series operations consistently

## xarray_fn
A decorator for Xarray function compatibility.

### Features
- Automatically converts input data to xarray objects
- Preserves coordinate and dimension information
- Supports labeled dimension operations
