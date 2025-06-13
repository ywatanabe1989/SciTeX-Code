#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-04-27 19:59:11 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/pd/_force_df.py
# ----------------------------------------
import os

__FILE__ = "./src/scitex/pd/_force_df.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import numpy as np
import pandas as pd

from ..types import is_listed_X


def force_df(data, filler=np.nan):
    """
    Convert various data types to pandas DataFrame.
    
    Parameters
    ----------
    data : various
        The data to convert to DataFrame. Can be DataFrame, Series, ndarray, 
        list, tuple, dict, scalar value, etc.
    filler : any, optional
        Value to use for filling missing values, by default np.nan
        
    Returns
    -------
    pd.DataFrame
        Data converted to DataFrame
        
    Examples
    --------
    >>> import scitex
    >>> import pandas as pd
    >>> import numpy as np
    
    # DataFrame input returns the same DataFrame
    >>> df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
    >>> scitex.pd.force_df(df) is df
    True
    
    # Series input is converted to DataFrame
    >>> series = pd.Series([1, 2, 3], name='test')
    >>> scitex.pd.force_df(series)
       test
    0     1
    1     2
    2     3
    
    # NumPy array input is converted to DataFrame
    >>> arr = np.array([1, 2, 3])
    >>> scitex.pd.force_df(arr)
       value
    0      1
    1      2
    2      3
    
    # Scalar values are converted to single-value DataFrames
    >>> scitex.pd.force_df(42)
       value
    0     42
    
    # Lists and tuples are converted to DataFrame
    >>> scitex.pd.force_df([1, 2, 3])
       value
    0      1
    1      2
    2      3
    
    # Dictionaries are converted to DataFrame with appropriate handling
    # of different length values
    >>> data = {'A': [1, 2, 3], 'B': [4, 5]}
    >>> scitex.pd.force_df(data)
       A  B
    0  1  4
    1  2  5
    2  3  NaN
    """
    # Return None as empty DataFrame
    if data is None:
        return pd.DataFrame()
        
    # Return DataFrame as is
    if isinstance(data, pd.DataFrame):
        return data
        
    # Convert Series to DataFrame
    if isinstance(data, pd.Series):
        return data.to_frame()
        
    # Convert numpy array to DataFrame
    if isinstance(data, np.ndarray):
        # Handle 1D array
        if data.ndim == 1:
            return pd.DataFrame(data, columns=['value'])
        # Handle 2D array
        elif data.ndim == 2:
            return pd.DataFrame(data)
        # Handle higher dimensional arrays
        else:
            shape = data.shape
            reshaped = data.reshape(shape[0], -1)
            return pd.DataFrame(reshaped)
            
    # Handle scalar values (int, float, str, etc.)
    if isinstance(data, (int, float, str, bool)):
        return pd.DataFrame([data], columns=['value'])
            
    # Handle lists and tuples
    if isinstance(data, (list, tuple)):
        # Handle list of lists/arrays -> DataFrame
        if len(data) > 0 and isinstance(data[0], (list, tuple, np.ndarray)):
            return pd.DataFrame(data)
        # Handle simple list/tuple -> single column DataFrame
        else:
            return pd.DataFrame(data, columns=['value'])
    
    # Continue with the original implementation for dictionaries
    if isinstance(data, dict):
        # Original implementation
        permutable_dict = data.copy()
        
        # Get the lengths
        max_len = 0
        for k, v in permutable_dict.items():
            # Check if v is an iterable (but not string) or treat as single length otherwise
            if isinstance(v, (str, int, float)) or not hasattr(v, "__len__"):
                length = 1
            else:
                length = len(v)
            max_len = max(max_len, length)
        
        # Replace with appropriately filled list
        for k, v in permutable_dict.items():
            if isinstance(v, (str, int, float)) or not hasattr(v, "__len__"):
                permutable_dict[k] = [v] + [filler] * (max_len - 1)
            else:
                permutable_dict[k] = list(v) + [filler] * (max_len - len(v))
        
        # Puts them into a DataFrame
        return pd.DataFrame(permutable_dict)
    
    # For any other iterable type
    try:
        return pd.DataFrame(list(data), columns=['value'])
    except:
        raise TypeError(f"Cannot convert object of type {type(data)} to DataFrame")


# EOF
