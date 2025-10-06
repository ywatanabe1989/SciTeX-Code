#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-18 18:14:26 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/_subplots/_export_as_csv_formatters/_format_sns_histplot.py
# ----------------------------------------
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import numpy as np
import pandas as pd

def _format_sns_histplot(id, tracked_dict, kwargs):
    """
    Format data from a sns_histplot call as a bar plot representation.
    
    This formatter extracts both the raw data and the binned data from seaborn histogram plots,
    returning them in a format that can be visualized as a bar plot.
    
    Args:
        id (str): Identifier for the plot
        tracked_dict (dict): Dictionary containing tracked data
        kwargs (dict): Keyword arguments passed to sns_histplot
        
    Returns:
        pd.DataFrame: Formatted data for the plot including bin information
    """
    # Check if tracked_dict is empty or not a dictionary
    if not tracked_dict or not isinstance(tracked_dict, dict):
        return pd.DataFrame()
    
    columns = {}
    
    # Check if histogram result is available in tracked_dict
    hist_result = tracked_dict.get('hist_result', None)
    
    # If we have histogram result (counts and bin edges)
    if hist_result is not None:
        counts, bin_edges = hist_result
        
        # Calculate bin centers for bar plot representation
        bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])
        bin_widths = bin_edges[1:] - bin_edges[:-1]
        
        # Add bin information to DataFrame
        columns[f"{id}_bin_centers"] = bin_centers
        columns[f"{id}_bin_counts"] = counts
        columns[f"{id}_bin_widths"] = bin_widths
        columns[f"{id}_bin_edges_left"] = bin_edges[:-1]
        columns[f"{id}_bin_edges_right"] = bin_edges[1:]
    
    # Get raw data if available
    if 'data' in tracked_dict:
        df = tracked_dict['data']
        if isinstance(df, pd.DataFrame):
            # Extract column data from kwargs if available
            x_col = kwargs.get('x')
            if x_col and x_col in df.columns:
                columns[f"{id}_raw_data"] = df[x_col].values
    
    # Legacy handling for args
    elif 'args' in tracked_dict:
        args = tracked_dict['args']
        if len(args) >= 1:
            # First argument is typically the data
            x = args[0]
            if hasattr(x, 'values'):  # pandas Series or DataFrame
                columns[f"{id}_raw_data"] = x.values
            else:
                columns[f"{id}_raw_data"] = x
    
    # If we have data to return
    if columns:
        # Ensure all arrays are the same length by padding with NaN
        max_length = max(len(value) for value in columns.values() if hasattr(value, '__len__'))
        for key, value in list(columns.items()):
            if hasattr(value, '__len__') and len(value) < max_length:
                # Pad with NaN if needed
                if isinstance(value, np.ndarray):
                    columns[key] = np.pad(value, (0, max_length - len(value)), 
                                         mode='constant', constant_values=np.nan)
                else:
                    padded = list(value) + [np.nan] * (max_length - len(value))
                    columns[key] = np.array(padded)
        
        return pd.DataFrame(columns)
    
    # Default empty DataFrame if we can't process the input
    return pd.DataFrame()