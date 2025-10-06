#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-18 18:14:26 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/_subplots/_export_as_csv_formatters/_format_plot_fillv.py
# ----------------------------------------
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import numpy as np
import pandas as pd

def _format_plot_fillv(id, tracked_dict, kwargs):
    """Format data from a plot_fillv call.
    
    Formats data similar to line plot format for better compatibility.
    
    Args:
        id (str): Identifier for the plot
        tracked_dict (dict): Dictionary containing tracked data
        kwargs (dict): Keyword arguments passed to plot_fillv
        
    Returns:
        pd.DataFrame: Formatted fillv data in a long-format dataframe
    """
    # Check if tracked_dict is empty or not a dictionary
    if not tracked_dict or not isinstance(tracked_dict, dict):
        return pd.DataFrame()
    
    # Try to get starts/ends directly from tracked_dict first
    starts = tracked_dict.get('starts')
    ends = tracked_dict.get('ends')
    
    # If not found, get from args
    if starts is None or ends is None:
        args = tracked_dict.get('args', [])
        
        # Extract data if available from args
        if len(args) >= 2:
            starts, ends = args[0], args[1]
    
    # If we have valid starts and ends, create a DataFrame in a format similar to line plot
    if starts is not None and ends is not None:
        # Convert to numpy arrays if they're lists for better handling
        if isinstance(starts, list):
            starts = np.array(starts)
        if isinstance(ends, list):
            ends = np.array(ends)
        
        # Create a DataFrame with x, y pairs for each fill span
        rows = []
        for start, end in zip(starts, ends):
            rows.append({
                f"{id}_x": start,
                f"{id}_y": 0,
                f"{id}_type": "start"
            })
            rows.append({
                f"{id}_x": end,
                f"{id}_y": 0,
                f"{id}_type": "end"
            })
        
        if rows:
            return pd.DataFrame(rows)
    
    return pd.DataFrame()