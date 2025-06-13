#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-18 18:14:26 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/_subplots/_export_as_csv_formatters/_format_sns_swarmplot.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/plt/_subplots/_export_as_csv_formatters/_format_sns_swarmplot.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import pandas as pd

def _format_sns_swarmplot(id, tracked_dict, kwargs):
    """Format data from a sns_swarmplot call.
    
    Args:
        id (str): Identifier for the plot
        tracked_dict (dict): Dictionary containing tracked data
        kwargs (dict): Keyword arguments passed to sns_swarmplot
        
    Returns:
        pd.DataFrame: Formatted data for the plot
    """
    # Check if tracked_dict is empty or not a dictionary
    if not tracked_dict or not isinstance(tracked_dict, dict):
        return pd.DataFrame()
    
    # If 'data' key is in tracked_dict, use it
    if 'data' in tracked_dict:
        data = tracked_dict['data']
        
        # Handle DataFrame input with x and/or y variables
        if isinstance(data, pd.DataFrame):
            result = pd.DataFrame()
            
            # Extract variables from kwargs
            x_var = kwargs.get("x")
            y_var = kwargs.get("y")
            
            # Add x variable if specified
            if x_var and x_var in data.columns:
                result[f"{id}_swarm_{x_var}"] = data[x_var]
                
            # Add y variable if specified
            if y_var and y_var in data.columns:
                result[f"{id}_swarm_{y_var}"] = data[y_var]
                
            # Add grouping variable if present
            hue_var = kwargs.get("hue")
            if hue_var and hue_var in data.columns:
                result[f"{id}_swarm_{hue_var}"] = data[hue_var]
                
            # If we've added columns, return the result
            if not result.empty:
                return result
                
            # If no columns were explicitly specified, return all columns
            result = data.copy()
            result.columns = [f"{id}_swarm_{col}" for col in result.columns]
            return result
    
    # Legacy handling for args
    if 'args' in tracked_dict and len(tracked_dict['args']) >= 1:
        data = tracked_dict['args'][0]
        
        # Handle DataFrame input
        if isinstance(data, pd.DataFrame):
            result = data.copy()
            result.columns = [f"{id}_swarm_{col}" for col in result.columns]
            return result
    
    # Default empty DataFrame if we can't process the input
    return pd.DataFrame()