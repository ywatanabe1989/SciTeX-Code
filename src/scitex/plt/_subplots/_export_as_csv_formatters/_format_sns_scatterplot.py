#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-18 18:14:26 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/_subplots/_export_as_csv_formatters/_format_sns_scatterplot.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/plt/_subplots/_export_as_csv_formatters/_format_sns_scatterplot.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import numpy as np
import pandas as pd

def _format_sns_scatterplot(id, tracked_dict, kwargs=None):
    """Format data from a sns_scatterplot call.
    
    Args:
        id (str): Identifier for the plot (already unpacked from the record tuple)
        tracked_dict (dict): Tracked data dictionary from the record tuple
        kwargs (dict): Keyword arguments from the record tuple
        
    Returns:
        pd.DataFrame: Formatted data for the plot
    """
    # Look for the DataFrame in the kwargs dictionary if provided
    if kwargs and isinstance(kwargs, dict) and 'data' in kwargs:
        data = kwargs['data']
        if isinstance(data, pd.DataFrame):
            # Use the DataFrame provided in kwargs
            result = pd.DataFrame()
            
            # If x and y variables are specified in kwargs, use them to extract columns
            x_var = kwargs.get('x')
            y_var = kwargs.get('y')
            
            if x_var and y_var and x_var in data.columns and y_var in data.columns:
                # Extract these specific columns
                result[f"{id}_x"] = data[x_var]
                result[f"{id}_y"] = data[y_var]
                
                # Also extract hue, size, style if they are specified
                for extra_var in ['hue', 'size', 'style']:
                    var_name = kwargs.get(extra_var)
                    if var_name and var_name in data.columns:
                        result[f"{id}_{extra_var}"] = data[var_name]
                
                return result
            else:
                # If columns aren't specified, include all columns
                for col in data.columns:
                    result[f"{id}_{col}"] = data[col]
                return result
    
    # Alternative: try to find a DataFrame in tracked_dict
    if tracked_dict and isinstance(tracked_dict, dict):
        # Search for 'data' key
        if 'data' in tracked_dict and isinstance(tracked_dict['data'], pd.DataFrame):
            data = tracked_dict['data']
            result = pd.DataFrame()
            
            # Just copy all columns from the data
            for col in data.columns:
                result[f"{id}_{col}"] = data[col]
            
            return result
    
    # If all else fails, return an empty DataFrame
    return pd.DataFrame()