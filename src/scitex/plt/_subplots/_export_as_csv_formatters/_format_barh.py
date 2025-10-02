#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-18 18:14:26 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/_subplots/_export_as_csv_formatters/_format_barh.py
# ----------------------------------------
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import pandas as pd

def _format_barh(id, tracked_dict, kwargs):
    """Format data from a barh call."""
    # Check if tracked_dict is empty or not a dictionary
    if not tracked_dict or not isinstance(tracked_dict, dict):
        return pd.DataFrame()
    
    # Get the args from tracked_dict
    args = tracked_dict.get('args', [])
    
    # Extract x and y data if available
    if len(args) >= 2:
        # Note: in barh, x is height, y is width (visually transposed from bar)
        x, y = args[0], args[1]
        
        # Get xerr from kwargs
        xerr = kwargs.get("xerr")
        
        # Convert single values to Series
        if isinstance(x, (int, float)):
            x = pd.Series(x, name="x")
        if isinstance(y, (int, float)):
            y = pd.Series(y, name="y")
    else:
        # Not enough arguments
        return pd.DataFrame()

    df = pd.DataFrame(
        {f"{id}_barh_y": x, f"{id}_barh_x": y}
    )  # Swap x/y for barh

    if xerr is not None:
        if isinstance(xerr, (int, float)):
            xerr = pd.Series(xerr, name="xerr")
        df[f"{id}_barh_xerr"] = xerr
    return df