#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-18 18:14:26 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/_subplots/_export_as_csv_formatters/_format_plot_violin.py
# ----------------------------------------
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import numpy as np
import pandas as pd

def _format_plot_violin(id, tracked_dict, kwargs):
    """Format data from a plot_violin call.
    
    Formats data in a long-format for better compatibility.
    
    Args:
        id (str): Identifier for the plot
        tracked_dict (dict): Dictionary containing tracked data
        kwargs (dict): Keyword arguments passed to plot_violin
        
    Returns:
        pd.DataFrame: Formatted violin plot data in long format
    """
    # Check if tracked_dict is empty or not a dictionary
    if not tracked_dict or not isinstance(tracked_dict, dict):
        return pd.DataFrame()
        
    # Extract data from tracked_dict
    data = tracked_dict.get('data')
    
    if data is not None:
        # If data is a simple array or list
        if isinstance(data, (np.ndarray, list)) and not isinstance(
            data[0], (list, np.ndarray, dict)
        ):
            # Convert to long format with group and value columns
            rows = [{'group': '0', 'value': val} for val in data]
            df = pd.DataFrame(rows)
            # Prefix columns with id
            df.columns = [f"{id}_plot_violin_{col}" for col in df.columns]
            return df

        # If data is a list of arrays (multiple violin plots)
        elif isinstance(data, (list, tuple)) and all(
            isinstance(x, (list, np.ndarray)) for x in data
        ):
            # Get labels if available
            labels = tracked_dict.get('labels')
            
            # Convert to long format
            rows = []
            for i, values in enumerate(data):
                # Use label if available, otherwise use index
                group = labels[i] if labels and i < len(labels) else f"group{i:02d}"
                for val in values:
                    rows.append({'group': str(group), 'value': val})
            
            if rows:
                df = pd.DataFrame(rows)
                # Prefix columns with id
                df.columns = [f"{id}_plot_violin_{col}" for col in df.columns]
                return df

        # If data is a dictionary
        elif isinstance(data, dict):
            # Convert to long format
            rows = []
            for group, values in data.items():
                for val in values:
                    rows.append({'group': str(group), 'value': val})
            
            if rows:
                df = pd.DataFrame(rows)
                # Prefix columns with id
                df.columns = [f"{id}_plot_violin_{col}" for col in df.columns]
                return df

        # If data is a DataFrame
        elif isinstance(data, pd.DataFrame):
            # For DataFrame data with x and y columns
            x = tracked_dict.get('x')
            y = tracked_dict.get('y')
            
            if x is not None and y is not None and x in data.columns and y in data.columns:
                # Convert to long format
                rows = []
                for group_name, group_data in data.groupby(x):
                    for val in group_data[y]:
                        rows.append({'group': str(group_name), 'value': val})
                
                if rows:
                    df = pd.DataFrame(rows)
                    # Prefix columns with id
                    df.columns = [f"{id}_plot_violin_{col}" for col in df.columns]
                    return df
            else:
                # For other dataframes, melt to long format
                try:
                    # Try to melt to long format
                    result = pd.melt(data)
                    # Use variable column as group, value column as values
                    result.columns = ['group', 'value']
                    # Prefix columns with id
                    result.columns = [f"{id}_plot_violin_{col}" for col in result.columns]
                    return result
                except Exception:
                    # If melt fails, just return the original with prefixed columns
                    result = data.copy()
                    result.columns = [f"{id}_plot_violin_{col}" for col in result.columns]
                    return result

    return pd.DataFrame()