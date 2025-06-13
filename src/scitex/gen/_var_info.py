#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-25 00:35:31 (ywatanabe)"
# File: ./scitex_repo/src/scitex/gen/_var_info.py

THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/gen/_var_info.py"

from typing import Any, Union
import numpy as np
import pandas as pd
import torch
import xarray as xr

ArrayLike = Union[
    list, tuple, np.ndarray, pd.Series, pd.DataFrame, xr.DataArray, torch.Tensor
]


def var_info(variable: Any) -> dict:
    """Returns type and structural information about a variable.

    Example
    -------
    >>> data = np.array([[1, 2], [3, 4]])
    >>> info = var_info(data)
    >>> print(info)
    {
        'type': 'numpy.ndarray',
        'length': 2,
        'shape': (2, 2),
        'dimensions': 2
    }

    Parameters
    ----------
    variable : Any
        Variable to inspect.

    Returns
    -------
    dict
        Dictionary containing variable information.
    """
    info = {"type": type(variable).__name__}

    # Length check
    if hasattr(variable, "__len__"):
        info["length"] = len(variable)

    # Shape check for array-like objects
    if isinstance(
        variable, (np.ndarray, pd.DataFrame, pd.Series, xr.DataArray, torch.Tensor)
    ):
        info["shape"] = variable.shape
        info["dimensions"] = len(variable.shape)

    # Special handling for nested lists
    elif isinstance(variable, list):
        if variable and isinstance(variable[0], list):
            depth = 1
            current = variable
            shape = [len(variable)]
            while current and isinstance(current[0], list):
                shape.append(len(current[0]))
                current = current[0]
                depth += 1
            info["shape"] = tuple(shape)
            info["dimensions"] = depth

    return info


# EOF
