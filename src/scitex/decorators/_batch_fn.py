#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-01 09:18:26 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/decorators/_batch_fn.py
# ----------------------------------------
import os

__FILE__ = "./src/scitex/decorators/_batch_fn.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
from typing import Any as _Any

from functools import wraps
from typing import Callable

import numpy as np
import torch
from tqdm import tqdm as _tqdm

from ._converters import is_nested_decorator


def batch_fn(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(x: _Any, *args: _Any, **kwargs: _Any) -> _Any:
        # Skip batching if in a nested decorator context and batch_size is already set
        if is_nested_decorator() and "batch_size" in kwargs:
            return func(x, *args, **kwargs)

        # Set the current decorator context
        wrapper._current_decorator = "batch_fn"
        
        # Mark that batch_fn has been applied
        if not hasattr(wrapper, '_decorator_order'):
            wrapper._decorator_order = []
        wrapper._decorator_order.append('batch_fn')

        batch_size = int(kwargs.pop("batch_size", 4))
        if len(x) <= batch_size:
            # Only pass batch_size if the function accepts it
            import inspect
            try:
                sig = inspect.signature(func)
                if 'batch_size' in sig.parameters:
                    return func(x, *args, **kwargs, batch_size=batch_size)
                else:
                    return func(x, *args, **kwargs)
            except:
                # Fallback for wrapped functions
                return func(x, *args, **kwargs)

        n_batches = (len(x) + batch_size - 1) // batch_size
        results = []

        for i_batch in _tqdm(range(n_batches)):
            start = i_batch * batch_size
            end = min((i_batch + 1) * batch_size, len(x))

            # Only pass batch_size if the function accepts it
            import inspect
            try:
                sig = inspect.signature(func)
                if 'batch_size' in sig.parameters:
                    batch_result = func(x[start:end], *args, **kwargs, batch_size=batch_size)
                else:
                    batch_result = func(x[start:end], *args, **kwargs)
            except:
                # Fallback for wrapped functions
                batch_result = func(x[start:end], *args, **kwargs)

            if isinstance(batch_result, torch.Tensor):
                batch_result = batch_result.cpu()
            elif isinstance(batch_result, tuple):
                batch_result = tuple(
                    val.cpu() if isinstance(val, torch.Tensor) else val
                    for val in batch_result
                )

            results.append(batch_result)

        if isinstance(results[0], tuple):
            n_vars = len(results[0])
            combined_results = []
            for i_var in range(n_vars):
                # Check if this element is stackable (tensor/array) or should be kept as-is
                first_elem = results[0][i_var]
                if isinstance(first_elem, (torch.Tensor, np.ndarray)):
                    # Stack tensors/arrays
                    if isinstance(first_elem, torch.Tensor):
                        if first_elem.ndim == 0:
                            combined = torch.stack([res[i_var] for res in results])
                        else:
                            combined = torch.vstack([res[i_var] for res in results])
                    else:
                        combined = np.vstack([res[i_var] for res in results])
                    combined_results.append(combined)
                else:
                    # For non-tensor elements (like lists), just take the first one
                    # (assuming they're all the same across batches)
                    combined_results.append(first_elem)
            return tuple(combined_results)
        elif isinstance(results[0], torch.Tensor):
            # Check if results are 0-D tensors (scalars)
            if results[0].ndim == 0:
                return torch.stack(results)
            else:
                return torch.vstack(results)
        elif isinstance(results[0], np.ndarray):
            # Handle numpy arrays
            if results[0].ndim == 0:
                return np.array(results)
            else:
                return np.vstack(results)
        elif isinstance(results[0], (int, float)):
            # Handle scalar results
            return np.array(results) if len(results) > 1 else results[0]
        else:
            # For lists and other types
            return sum(results, [])

    # Mark as a wrapper for detection
    wrapper._is_wrapper = True
    wrapper._decorator_type = "batch_fn"
    return wrapper


# EOF
