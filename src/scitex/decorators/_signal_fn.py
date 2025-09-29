#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-31 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/decorators/_signal_fn.py
# ----------------------------------------
import os

__FILE__ = "./src/scitex/decorators/_signal_fn.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from functools import wraps
from typing import Any as _Any
from typing import Callable

import numpy as np
import pandas as pd
import torch
import xarray as xr

from ._converters import _return_always, is_nested_decorator, to_torch


def signal_fn(func: Callable) -> Callable:
    """Decorator for signal processing functions that converts only the first argument (signal) to torch tensor.

    This decorator is designed for DSP functions where:
    - The first argument is the signal data that should be converted to torch tensor
    - Other arguments (like sampling frequency, bands, etc.) should remain as-is
    """

    @wraps(func)
    def wrapper(*args: _Any, **kwargs: _Any) -> _Any:
        # Skip conversion if already in a nested decorator context
        if is_nested_decorator():
            results = func(*args, **kwargs)
            return results

        # Set the current decorator context
        wrapper._current_decorator = "signal_fn"

        # Store original object for type preservation
        original_object = args[0] if args else None

        # Convert only the first argument (signal) to torch tensor
        if args:
            # Convert first argument to torch
            converted_first_arg = to_torch(args[0], return_fn=_return_always)[0][0]

            # Keep other arguments as-is
            converted_args = (converted_first_arg,) + args[1:]
        else:
            converted_args = args

        results = func(*converted_args, **kwargs)

        # Convert results back to original input types
        if isinstance(results, torch.Tensor):
            if original_object is not None:
                if isinstance(original_object, list):
                    return results.detach().cpu().numpy().tolist()
                elif isinstance(original_object, np.ndarray):
                    return results.detach().cpu().numpy()
                elif isinstance(original_object, pd.DataFrame):
                    return pd.DataFrame(results.detach().cpu().numpy())
                elif isinstance(original_object, pd.Series):
                    return pd.Series(results.detach().cpu().numpy().flatten())
                elif isinstance(original_object, xr.DataArray):
                    return xr.DataArray(results.detach().cpu().numpy())
            return results

        # Handle tuple returns (e.g., (signal, frequencies))
        elif isinstance(results, tuple):
            converted_results = []
            for r in results:
                if isinstance(r, torch.Tensor):
                    if original_object is not None and isinstance(
                        original_object, np.ndarray
                    ):
                        converted_results.append(r.detach().cpu().numpy())
                    else:
                        converted_results.append(r)
                else:
                    converted_results.append(r)
            return tuple(converted_results)

        return results

    # Mark as a wrapper for detection
    wrapper._is_wrapper = True
    wrapper._decorator_type = "signal_fn"
    return wrapper


# EOF
