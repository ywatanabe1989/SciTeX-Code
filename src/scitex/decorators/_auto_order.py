#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-01 10:30:00 (ywatanabe)"
# File: ./scitex_repo/src/scitex/decorators/_auto_order.py

"""
Auto-ordering decorator system that enforces predefined order regardless of 
how decorators are written in code.

The enforced order is:
1. Type conversion (innermost): torch_fn, numpy_fn, pandas_fn
2. Batch processing (outermost): batch_fn

This uses a delayed application approach where decorators are collected
and then applied in the correct order when the function is first called.

Example
-------
>>> from scitex.decorators import enable_auto_order
>>> enable_auto_order()
>>> 
>>> # These will all work identically:
>>> @batch_fn
>>> @torch_fn
>>> def func1(x):
...     return x.mean()
>>> 
>>> @torch_fn
>>> @batch_fn  # Order doesn't matter!
>>> def func2(x):
...     return x.mean()

The auto-ordering system eliminates decorator ordering complexity and
prevents common errors from incorrect decorator stacking.
"""

from functools import wraps
from typing import Callable, List, Tuple, Any

# Import original decorators
from ._torch_fn import torch_fn as _orig_torch_fn
from ._numpy_fn import numpy_fn as _orig_numpy_fn
from ._pandas_fn import pandas_fn as _orig_pandas_fn
from ._batch_fn import batch_fn as _orig_batch_fn


# Decorator priority (higher = inner/applied first)
DECORATOR_PRIORITY = {
    'torch_fn': 100,
    'numpy_fn': 100,
    'pandas_fn': 100,
    'batch_fn': 10,
}

# Original decorator mapping
ORIGINAL_DECORATORS = {
    'torch_fn': _orig_torch_fn,
    'numpy_fn': _orig_numpy_fn,
    'pandas_fn': _orig_pandas_fn,
    'batch_fn': _orig_batch_fn,
}


class AutoOrderDecorator:
    """Decorator that collects and applies decorators in predefined order."""
    
    def __init__(self, name: str):
        self.name = name
        self.priority = DECORATOR_PRIORITY[name]
        self.original = ORIGINAL_DECORATORS[name]
    
    def __call__(self, func: Callable) -> Callable:
        # Initialize or get pending decorators list
        if not hasattr(func, '_pending_decorators'):
            # First decorator - create the wrapper
            original_func = func
            
            @wraps(func)
            def auto_ordered_wrapper(*args, **kwargs):
                # On first call, apply decorators in correct order
                if hasattr(auto_ordered_wrapper, '_pending_decorators'):
                    # Sort by priority (descending = innermost first)
                    decorators = sorted(
                        auto_ordered_wrapper._pending_decorators,
                        key=lambda x: x[1],
                        reverse=True
                    )
                    
                    # Apply decorators in order
                    final_func = original_func
                    for dec_name, _, dec_func in decorators:
                        final_func = dec_func(final_func)
                    
                    # Replace this wrapper with the final decorated function
                    auto_ordered_wrapper._final_func = final_func
                    delattr(auto_ordered_wrapper, '_pending_decorators')
                
                # Call the final decorated function
                if hasattr(auto_ordered_wrapper, '_final_func'):
                    return auto_ordered_wrapper._final_func(*args, **kwargs)
                else:
                    return original_func(*args, **kwargs)
            
            auto_ordered_wrapper._pending_decorators = []
            func = auto_ordered_wrapper
        
        # Add this decorator to pending list
        func._pending_decorators.append((self.name, self.priority, self.original))
        
        return func


# Create auto-ordering versions
torch_fn = AutoOrderDecorator('torch_fn')
numpy_fn = AutoOrderDecorator('numpy_fn')
pandas_fn = AutoOrderDecorator('pandas_fn')
batch_fn = AutoOrderDecorator('batch_fn')


# Enable auto-ordering globally
def enable_auto_order():
    """
    Enable auto-ordering for all decorators in the scitex.decorators module.
    
    This replaces the standard decorators with auto-ordering versions.
    
    Example
    -------
    >>> import scitex
    >>> scitex.decorators.enable_auto_order()
    >>> 
    >>> # Now decorators will auto-order regardless of how they're written
    >>> @scitex.decorators.batch_fn
    >>> @scitex.decorators.torch_fn
    >>> def my_func(x):
    ...     return x.mean()
    """
    import scitex.decorators as decorators_module
    
    # Replace with auto-ordering versions
    decorators_module.torch_fn = torch_fn
    decorators_module.numpy_fn = numpy_fn
    decorators_module.pandas_fn = pandas_fn
    decorators_module.batch_fn = batch_fn
    
    print("Auto-ordering enabled for scitex decorators!")
    print("Decorators will now apply in predefined order:")
    print("  1. Type conversion (torch_fn, numpy_fn, pandas_fn)")
    print("  2. Batch processing (batch_fn)")


def disable_auto_order():
    """Disable auto-ordering and restore original decorators."""
    import scitex.decorators as decorators_module
    
    # Restore original decorators
    decorators_module.torch_fn = _orig_torch_fn
    decorators_module.numpy_fn = _orig_numpy_fn
    decorators_module.pandas_fn = _orig_pandas_fn
    decorators_module.batch_fn = _orig_batch_fn
    
    print("Auto-ordering disabled. Using original decorators.")


__all__ = [
    'torch_fn',
    'numpy_fn',
    'pandas_fn',
    'batch_fn',
    'enable_auto_order',
    'disable_auto_order',
]