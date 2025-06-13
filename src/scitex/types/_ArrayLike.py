#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-01 09:21:23 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/types/_ArrayLike.py
# ----------------------------------------
import os

__FILE__ = "./src/scitex/types/_ArrayLike.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from typing import List as _List
from typing import Tuple as _Tuple
from typing import Union as _Union

import numpy as _np
import pandas as _pd
import torch as _torch
import xarray as _xr

ArrayLike = _Union[
    _List,
    _Tuple,
    _np.ndarray,
    _pd.Series,
    _pd.DataFrame,
    _xr.DataArray,
    _torch.tensor,
]


def is_array_like(obj) -> bool:
    """Check if object is array-like.
    
    Returns:
        bool: True if object is array-like, False otherwise.
    """
    return isinstance(
        obj,
        (_List, _Tuple, _np.ndarray, _pd.Series, _pd.DataFrame, _xr.DataArray),
    ) or _torch.is_tensor(obj)


# EOF
