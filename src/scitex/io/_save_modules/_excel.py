#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-12 12:59:00 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/.claude-worktree/scitex_repo/src/scitex/io/_save_modules/_excel.py
# ----------------------------------------
import os

__FILE__ = "./src/scitex/io/_save_modules/_excel.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Excel saving functionality for scitex.io.save
"""

import pandas as pd
import numpy as np


def save_excel(obj, spath, **kwargs):
    """Handle Excel file saving.
    
    Parameters
    ----------
    obj : pd.DataFrame, dict, or np.ndarray
        Object to save as Excel file
    spath : str
        Path where Excel file will be saved
    **kwargs
        Additional keyword arguments passed to pandas.DataFrame.to_excel()
        
    Raises
    ------
    ValueError
        If object type cannot be saved as Excel file
    """
    if isinstance(obj, pd.DataFrame):
        obj.to_excel(spath, index=False, **kwargs)
    elif isinstance(obj, dict):
        df = pd.DataFrame(obj)
        df.to_excel(spath, index=False, **kwargs)
    elif isinstance(obj, np.ndarray):
        df = pd.DataFrame(obj)
        df.to_excel(spath, index=False, **kwargs)
    else:
        raise ValueError(f"Cannot save object of type {type(obj)} as Excel file")


# EOF