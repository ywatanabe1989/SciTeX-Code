#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-18 15:12:10 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/utils/_is_valid_axis.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/plt/utils/_is_valid_axis.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import inspect
import matplotlib

def is_valid_axis(axis):
    """
    Check if the provided object is a valid axis (matplotlib Axes or scitex AxisWrapper).
    
    Parameters
    ----------
    axis : object
        The object to check
        
    Returns
    -------
    bool
        True if the object is a valid axis, False otherwise
        
    Examples
    --------
    >>> import matplotlib.pyplot as plt
    >>> import scitex
    >>> fig, ax = plt.subplots()
    >>> is_valid_axis(ax)
    True
    >>> mfig, max = scitex.plt.subplots()
    >>> is_valid_axis(max)
    True
    """
    # Check if it's a matplotlib Axes directly
    if isinstance(axis, matplotlib.axes._axes.Axes):
        return True
    
    # Check if it's an AxisWrapper from scitex
    # This checks the class hierarchy to see if it has an AxisWrapper in its inheritance chain
    for cls in inspect.getmro(type(axis)):
        if cls.__name__ == 'AxisWrapper':
            return True
            
    # Check if it has common axis methods (fallback check)
    axis_methods = ['plot', 'scatter', 'set_xlabel', 'set_ylabel', 'get_figure']
    has_methods = all(hasattr(axis, method) for method in axis_methods)
    
    return has_methods

def assert_valid_axis(axis, error_message=None):
    """
    Assert that the provided object is a valid axis (matplotlib Axes or scitex AxisWrapper).
    
    Parameters
    ----------
    axis : object
        The object to check
    error_message : str, optional
        Custom error message if assertion fails
        
    Raises
    ------
    AssertionError
        If the provided object is not a valid axis
    """
    if error_message is None:
        error_message = "First argument must be a matplotlib axis or scitex axis wrapper"
        
    assert is_valid_axis(axis), error_message

# EOF