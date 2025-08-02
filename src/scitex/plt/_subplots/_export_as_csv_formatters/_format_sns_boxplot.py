#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-18 18:14:26 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/_subplots/_export_as_csv_formatters/_format_sns_boxplot.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/plt/_subplots/_export_as_csv_formatters/_format_sns_boxplot.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import pandas as pd
import numpy as np

def _format_sns_boxplot(id, tracked_dict, kwargs):
    """Format data from a sns_boxplot call.
    
    Args:
        id (str): Identifier for the plot
        tracked_dict (dict): Dictionary containing tracked data
        kwargs (dict): Keyword arguments passed to sns_boxplot
        
    Returns:
        pd.DataFrame: Formatted boxplot data
    """
    # Check if tracked_dict is empty or not a dictionary
    if not tracked_dict:
        return pd.DataFrame()
    
    # If tracked_dict is a dictionary, try to extract the data from it
    if isinstance(tracked_dict, dict):
        # First try to get 'data' key which is used in seaborn functions
        if 'data' in tracked_dict:
            data = tracked_dict['data']
            if isinstance(data, pd.DataFrame):
                result = data.copy()
                # Add prefix to column names
                result.columns = [f"{id}_sns_boxplot_{col}" for col in result.columns]
                return result
        
        # If no 'data' key, try to get data from args
        args = tracked_dict.get('args', [])
        if len(args) > 0:
            # First arg is often the data for seaborn plots
            data = args[0]
            if isinstance(data, pd.DataFrame):
                result = data.copy()
                # Add prefix to column names
                result.columns = [f"{id}_sns_boxplot_{col}" for col in result.columns]
                return result
            
            # Handle list or array data
            elif isinstance(data, (list, np.ndarray)):
                # Try to convert to DataFrame
                try:
                    if all(isinstance(item, (list, np.ndarray)) for item in data):
                        # For list of lists/arrays (multiple groups)
                        data_dict = {}
                        for i, group_data in enumerate(data):
                            data_dict[f"{id}_sns_boxplot_group{i:02d}"] = group_data
                        return pd.DataFrame(data_dict)
                    else:
                        # For a single list/array
                        return pd.DataFrame({f"{id}_sns_boxplot_values": data})
                except:
                    pass
    
    # If tracked_dict is a DataFrame already, use it directly
    elif isinstance(tracked_dict, pd.DataFrame):
        result = tracked_dict.copy()
        # Add prefix to column names
        result.columns = [f"{id}_sns_boxplot_{col}" for col in result.columns]
        return result
    
    # If tracked_dict is list-like, try to convert it to a DataFrame
    elif hasattr(tracked_dict, "__iter__") and not isinstance(tracked_dict, str):
        try:
            # For list-like data
            if all(isinstance(item, (list, np.ndarray)) for item in tracked_dict):
                # For list of lists/arrays (multiple groups)
                data_dict = {}
                for i, group_data in enumerate(tracked_dict):
                    data_dict[f"{id}_sns_boxplot_group{i:02d}"] = group_data
                return pd.DataFrame(data_dict)
            else:
                # For a single list/array
                return pd.DataFrame({f"{id}_sns_boxplot_values": tracked_dict})
        except:
            pass
    
    # Return empty DataFrame if we couldn't extract useful data
    return pd.DataFrame()