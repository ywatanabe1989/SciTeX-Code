#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-18 18:14:26 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/_subplots/_export_as_csv_formatters/_format_sns_violinplot.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/plt/_subplots/_export_as_csv_formatters/_format_sns_violinplot.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import pandas as pd
import numpy as np

def _format_sns_violinplot(id, tracked_dict, kwargs):
    """Format data from a sns_violinplot call.
    
    Args:
        id (str): Identifier for the plot
        tracked_dict (dict): Dictionary containing tracked data
        kwargs (dict): Keyword arguments passed to sns_violinplot
        
    Returns:
        pd.DataFrame: Formatted data for the plot
    """
    # Check if tracked_dict is empty
    if not tracked_dict:
        return pd.DataFrame()
    
    # If tracked_dict is a dictionary
    if isinstance(tracked_dict, dict):
        # First try to get data from the 'data' key
        if 'data' in tracked_dict:
            data = tracked_dict['data']
            
            # Handle pandas DataFrame
            if isinstance(data, pd.DataFrame):
                try:
                    df = data.copy()
                    # Add the id prefix to all columns
                    result_df = pd.DataFrame()
                    # Copy columns one by one to avoid ambiguity errors
                    for col in df.columns:
                        result_df[f"{id}_sns_violin_{col}"] = df[col]
                    return result_df
                except Exception:
                    # In case of any errors, try to convert to a simpler format
                    try:
                        # Extract x and y variables if available in kwargs
                        x_var = kwargs.get('x')
                        y_var = kwargs.get('y')
                        
                        # If we have both x and y variables, extract just those columns
                        if x_var in data.columns and y_var in data.columns:
                            return pd.DataFrame({
                                f"{id}_sns_violin_{x_var}": data[x_var],
                                f"{id}_sns_violin_{y_var}": data[y_var]
                            })
                        # Otherwise, just return the first column
                        elif len(data.columns) > 0:
                            first_col = data.columns[0]
                            return pd.DataFrame({
                                f"{id}_sns_violin_values": data[first_col]
                            })
                    except Exception:
                        # If all else fails, return an empty DataFrame
                        return pd.DataFrame()
            
            # Handle list or numpy array
            elif isinstance(data, (list, np.ndarray)):
                # Try to convert to DataFrame
                try:
                    if isinstance(data, list) and len(data) > 0 and all(isinstance(item, (list, np.ndarray)) for item in data):
                        # For list of lists/arrays (multiple violins)
                        result = pd.DataFrame()
                        for i, group_data in enumerate(data):
                            result[f"{id}_sns_violin_group{i:02d}"] = pd.Series(group_data)
                        return result
                    else:
                        # For a single list/array
                        return pd.DataFrame({f"{id}_sns_violin_values": data})
                except:
                    # Return empty DataFrame if conversion fails
                    return pd.DataFrame()
        
        # Legacy handling for args
        args = tracked_dict.get('args', [])
        if len(args) > 0:
            data = args[0]  # First arg to sns_violinplot is typically the data
            
            # Handle pandas DataFrame
            if isinstance(data, pd.DataFrame):
                df = data.copy()
                # Add the id prefix to all columns
                return df.add_prefix(f"{id}_sns_violin_")
            
            # Handle list or numpy array
            elif isinstance(data, (list, np.ndarray)):
                # Try to convert to DataFrame
                try:
                    if all(isinstance(item, (list, np.ndarray)) for item in data):
                        # For list of lists/arrays (multiple violins)
                        result = pd.DataFrame()
                        for i, group_data in enumerate(data):
                            result[f"{id}_sns_violin_group{i:02d}"] = pd.Series(group_data)
                        return result
                    else:
                        # For a single list/array
                        return pd.DataFrame({f"{id}_sns_violin_values": data})
                except:
                    # Return empty DataFrame if conversion fails
                    return pd.DataFrame()
    
    # If tracked_dict is a DataFrame directly
    elif isinstance(tracked_dict, pd.DataFrame):
        try:
            df = tracked_dict.copy()
            # Add the id prefix to all columns, column by column to avoid ambiguity
            result_df = pd.DataFrame()
            for col in df.columns:
                result_df[f"{id}_sns_violin_{col}"] = df[col]
            return result_df
        except Exception:
            # In case of any errors, try a simpler approach
            try:
                # Just take the first column if possible
                if len(tracked_dict.columns) > 0:
                    first_col = tracked_dict.columns[0]
                    return pd.DataFrame({
                        f"{id}_sns_violin_values": tracked_dict[first_col]
                    })
            except Exception:
                # If all else fails, return an empty DataFrame
                return pd.DataFrame()
    
    # If tracked_dict is a list or numpy array directly
    elif isinstance(tracked_dict, (list, np.ndarray)):
        # Try to convert to DataFrame
        try:
            if all(isinstance(item, (list, np.ndarray)) for item in tracked_dict):
                # For list of lists/arrays (multiple violins)
                result = pd.DataFrame()
                for i, group_data in enumerate(tracked_dict):
                    result[f"{id}_sns_violin_group{i:02d}"] = pd.Series(group_data)
                return result
            else:
                # For a single list/array
                return pd.DataFrame({f"{id}_sns_violin_values": tracked_dict})
        except:
            # Return empty DataFrame if conversion fails
            return pd.DataFrame()
    
    # Default empty DataFrame if we can't process the input
    return pd.DataFrame()