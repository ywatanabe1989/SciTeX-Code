#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-18 18:14:26 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/_subplots/_export_as_csv_formatters/_format_sns_heatmap.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/plt/_subplots/_export_as_csv_formatters/_format_sns_heatmap.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import pandas as pd
import numpy as np

def _format_sns_heatmap(id, tracked_dict, kwargs):
    """Format data from a sns_heatmap call.
    
    Args:
        id (str): Identifier for the plot
        tracked_dict (dict): Dictionary containing tracked data
        kwargs (dict): Keyword arguments passed to sns_heatmap
        
    Returns:
        pd.DataFrame: Formatted data for the plot
    """
    # Check if tracked_dict is empty
    if not tracked_dict:
        return pd.DataFrame()
    
    # If tracked_dict is a dictionary
    if isinstance(tracked_dict, dict):
        # If 'data' key is in tracked_dict, use it
        if 'data' in tracked_dict:
            data = tracked_dict['data']
            
            # Handle pandas DataFrame
            if isinstance(data, pd.DataFrame):
                df = data.copy()
                # Add the id prefix to all columns
                return df.add_prefix(f"{id}_sns_heatmap_")
            
            # Handle numpy array
            elif isinstance(data, np.ndarray):
                # Create DataFrame from array with simple column names
                rows, cols = data.shape if len(data.shape) >= 2 else (data.shape[0], 1)
                df = pd.DataFrame(
                    data,
                    columns=[f"col_{i}" for i in range(cols)]
                )
                # Add the id prefix to all columns
                return df.add_prefix(f"{id}_sns_heatmap_")
        
        # Legacy handling for args
        args = tracked_dict.get('args', [])
        if len(args) > 0:
            data = args[0]  # First arg to sns_heatmap is typically the data matrix
            
            # Handle pandas DataFrame
            if isinstance(data, pd.DataFrame):
                df = data.copy()
                # Add the id prefix to all columns
                return df.add_prefix(f"{id}_sns_heatmap_")
            
            # Handle numpy array
            elif isinstance(data, np.ndarray):
                # Create DataFrame from array with simple column names
                rows, cols = data.shape if len(data.shape) >= 2 else (data.shape[0], 1)
                df = pd.DataFrame(
                    data,
                    columns=[f"col_{i}" for i in range(cols)]
                )
                # Add the id prefix to all columns
                return df.add_prefix(f"{id}_sns_heatmap_")
    
    # If tracked_dict is a DataFrame directly
    elif isinstance(tracked_dict, pd.DataFrame):
        df = tracked_dict.copy()
        # Add the id prefix to all columns
        return df.add_prefix(f"{id}_sns_heatmap_")
    
    # If tracked_dict is a numpy array directly
    elif isinstance(tracked_dict, np.ndarray):
        # Create DataFrame from array with simple column names
        rows, cols = tracked_dict.shape if len(tracked_dict.shape) >= 2 else (tracked_dict.shape[0], 1)
        df = pd.DataFrame(
            tracked_dict,
            columns=[f"col_{i}" for i in range(cols)]
        )
        # Add the id prefix to all columns
        return df.add_prefix(f"{id}_sns_heatmap_")
    
    # Default empty DataFrame if we can't process the input
    return pd.DataFrame()