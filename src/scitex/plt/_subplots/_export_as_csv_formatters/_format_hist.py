#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-18 18:14:26 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/_subplots/_export_as_csv_formatters/_format_hist.py
# ----------------------------------------
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import numpy as np
import pandas as pd

def _format_hist(id, tracked_dict, kwargs):
    """
    Format data from a hist call as a bar plot representation.
    
    This formatter extracts both the raw data and the binned data from histogram plots,
    returning them in a format that can be visualized as a bar plot.
    
    Args:
        id (str): Identifier for the plot
        tracked_dict (dict): Dictionary containing tracked data
        kwargs (dict): Keyword arguments passed to hist
        
    Returns:
        pd.DataFrame: DataFrame containing both raw data and bin information
    """
    # Check if tracked_dict is empty or not a dictionary
    if not tracked_dict or not isinstance(tracked_dict, dict):
        return pd.DataFrame()
    
    # Get the args from tracked_dict
    args = tracked_dict.get('args', [])
    
    # Check if histogram result (bin counts and edges) is available in tracked_dict
    hist_result = tracked_dict.get('hist_result', None)
    
    columns = {}
    
    # Extract raw data if available
    if len(args) >= 1:
        x = args[0]
        columns[f"{id}_raw_data"] = x
    
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
        
        # Create DataFrame with aligned length
        max_length = max(len(value) for value in columns.values())
        for key, value in list(columns.items()):
            if len(value) < max_length:
                # Pad with NaN if needed
                if isinstance(value, np.ndarray):
                    columns[key] = np.pad(value, (0, max_length - len(value)), 
                                          mode='constant', constant_values=np.nan)
                else:
                    padded = list(value) + [np.nan] * (max_length - len(value))
                    columns[key] = np.array(padded)
    
    # Return DataFrame or empty DataFrame if no data
    if columns:
        return pd.DataFrame(columns)
    
    return pd.DataFrame()