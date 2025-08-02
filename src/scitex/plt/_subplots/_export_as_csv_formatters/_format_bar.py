#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-19 15:45:51 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/_subplots/_export_as_csv_formatters/_format_bar.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/plt/_subplots/_export_as_csv_formatters/_format_bar.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import pandas as pd
import numpy as np

def _format_bar(id, tracked_dict, kwargs):
    """Format data from a bar call for CSV export.
    
    Simplified to focus only on essential x and y values.
    
    Args:
        id: The identifier for the plot
        tracked_dict: Dictionary of tracked data
        kwargs: Original keyword arguments
        
    Returns:
        pd.DataFrame: Formatted data ready for CSV export with just x and y values
    """
    # Check if tracked_dict is empty or not a dictionary
    if not tracked_dict or not isinstance(tracked_dict, dict):
        return pd.DataFrame()
    
    # Check if we have the newer format with bar_data
    if 'bar_data' in tracked_dict and isinstance(tracked_dict['bar_data'], pd.DataFrame):
        # Use the pre-formatted DataFrame but keep only x and height (y)
        df = tracked_dict['bar_data'].copy()
        
        # Keep only essential columns
        essential_cols = [col for col in df.columns if col in ['x', 'height']]
        if essential_cols:
            df = df[essential_cols]
            
            # Rename height to y for consistency
            if 'height' in df.columns:
                df = df.rename(columns={'height': 'y'})
                
            # Add identifier to column names
            df.columns = [f"{id}_{col}" for col in df.columns]
            return df
    
    # Legacy format - get the args from tracked_dict
    args = tracked_dict.get('args', [])
    
    # Extract x and y data if available
    if len(args) >= 2:
        x, y = args[0], args[1]
        
        # Convert to arrays if possible for consistent handling
        try:
            x_array = np.asarray(x)
            y_array = np.asarray(y)
            
            # Create DataFrame with just x and y data
            data = {
                f"{id}_x": x_array,
                f"{id}_y": y_array,
            }
                
            return pd.DataFrame(data)
            
        except (TypeError, ValueError):
            # Fall back to direct values if conversion fails
            return pd.DataFrame({f"{id}_x": x, f"{id}_y": y})
    
    # If we have tracked data in another format (like our MatplotlibPlotMixin bar method)
    result = {}
    
    # Check for x position (might be in different keys)
    for x_key in ['x', 'xs', 'positions']:
        if x_key in tracked_dict:
            result[f"{id}_x"] = tracked_dict[x_key]
            break
            
    # Check for y values (might be in different keys)
    for y_key in ['y', 'ys', 'height', 'heights', 'values']:
        if y_key in tracked_dict:
            result[f"{id}_y"] = tracked_dict[y_key]
            break
    
    return pd.DataFrame(result) if result else pd.DataFrame()