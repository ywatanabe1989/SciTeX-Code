#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-01 10:20:00 (ywatanabe)"
# File: ./scitex_repo/src/scitex/decorators/_combined.py

"""
Combined decorators with predefined application order to reduce complexity.

The order is always: type conversion → batch processing
This ensures consistent behavior and reduces unexpected interactions.
"""

from functools import wraps
from typing import Callable

from ._batch_fn import batch_fn
from ._torch_fn import torch_fn
from ._numpy_fn import numpy_fn
from ._pandas_fn import pandas_fn


def torch_batch_fn(func: Callable) -> Callable:
    """
    Combined decorator: torch_fn → batch_fn.
    
    Converts inputs to torch tensors, then processes in batches.
    This is the recommended order for PyTorch operations.
    
    Example
    -------
    >>> @torch_batch_fn
    ... def process_data(x, dim=None):
    ...     return x.mean(dim=dim)
    """
    @wraps(func)
    @torch_fn
    @batch_fn
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


def numpy_batch_fn(func: Callable) -> Callable:
    """
    Combined decorator: numpy_fn → batch_fn.
    
    Converts inputs to numpy arrays, then processes in batches.
    This is the recommended order for NumPy operations.
    
    Example
    -------
    >>> @numpy_batch_fn
    ... def process_data(x, axis=None):
    ...     return np.mean(x, axis=axis)
    """
    @wraps(func)
    @numpy_fn
    @batch_fn
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


def pandas_batch_fn(func: Callable) -> Callable:
    """
    Combined decorator: pandas_fn → batch_fn.
    
    Converts inputs to pandas DataFrames, then processes in batches.
    This is the recommended order for Pandas operations.
    
    Example
    -------
    >>> @pandas_batch_fn
    ... def process_data(df):
    ...     return df.describe()
    """
    @wraps(func)
    @pandas_fn
    @batch_fn
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


# Aliases for common use cases
batch_torch_fn = torch_batch_fn  # Alternative name
batch_numpy_fn = numpy_batch_fn  # Alternative name
batch_pandas_fn = pandas_batch_fn  # Alternative name


__all__ = [
    'torch_batch_fn',
    'numpy_batch_fn', 
    'pandas_batch_fn',
    'batch_torch_fn',
    'batch_numpy_fn',
    'batch_pandas_fn',
]