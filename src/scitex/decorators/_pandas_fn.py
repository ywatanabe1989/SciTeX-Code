#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-04-30 15:44:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/decorators/_pandas_fn.py
# ----------------------------------------
import os

__FILE__ = "./src/scitex/decorators/_pandas_fn.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/decorators/_pandas_fn.py"

from functools import wraps
from typing import Any as _Any
from typing import Callable

import numpy as np
import pandas as pd
import torch
import xarray as xr

from ._converters import is_nested_decorator


def pandas_fn(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args: _Any, **kwargs: _Any) -> _Any:
        # Skip conversion if already in a nested decorator context
        if is_nested_decorator():
            results = func(*args, **kwargs)
            return results

        # Set the current decorator context
        wrapper._current_decorator = "pandas_fn"

        # Store original object for type preservation
        original_object = args[0] if args else None

        # Convert args to pandas DataFrames
        def to_pandas(data):
            if data is None:
                return None
            elif isinstance(data, pd.DataFrame):
                return data
            elif isinstance(data, pd.Series):
                return pd.DataFrame(data)
            elif isinstance(data, np.ndarray):
                return pd.DataFrame(data)
            elif isinstance(data, list):
                try:
                    return pd.DataFrame(data)
                except:
                    # If list can't be converted to DataFrame, return as is
                    return data
            elif isinstance(data, torch.Tensor):
                return pd.DataFrame(data.detach().cpu().numpy())
            elif isinstance(data, xr.DataArray):
                return pd.DataFrame(data.values)
            elif isinstance(data, (int, float, str)):
                # Don't convert scalars to DataFrames
                return data
            else:
                try:
                    return pd.DataFrame([data])
                except:
                    # If conversion fails, return as is
                    return data

        converted_args = [to_pandas(arg) for arg in args]
        converted_kwargs = {k: to_pandas(v) for k, v in kwargs.items()}

        # Skip strict assertion for certain types
        validated_args = []
        for arg_index, arg in enumerate(converted_args):
            if isinstance(arg, pd.DataFrame):
                validated_args.append(arg)
            elif isinstance(arg, (int, float, str, type(None), pd.Series)):
                # Pass through scalars, strings, Series, and None unchanged
                validated_args.append(arg)
            elif isinstance(arg, list) and all(isinstance(item, pd.DataFrame) for item in arg):
                # List of DataFrames - pass through as is
                validated_args.append(arg)
            else:
                # Try one more conversion attempt
                try:
                    validated_args.append(pd.DataFrame(arg))
                except:
                    # If all else fails, pass through unchanged
                    validated_args.append(arg)

        results = func(*validated_args, **converted_kwargs)

        # Convert results back to original input types
        if isinstance(results, pd.DataFrame):
            if original_object is not None:
                if isinstance(original_object, list):
                    return results.values.tolist()
                elif isinstance(original_object, np.ndarray):
                    return results.values
                elif isinstance(original_object, torch.Tensor):
                    return torch.tensor(results.values)
                elif isinstance(original_object, pd.Series):
                    return (
                        pd.Series(results.iloc[:, 0])
                        if results.shape[1] > 0
                        else pd.Series()
                    )
                elif isinstance(original_object, xr.DataArray):
                    return xr.DataArray(results.values)
            return results

        return results

    # Mark as a wrapper for detection
    wrapper._is_wrapper = True
    wrapper._decorator_type = "pandas_fn"
    return wrapper


# EOF
