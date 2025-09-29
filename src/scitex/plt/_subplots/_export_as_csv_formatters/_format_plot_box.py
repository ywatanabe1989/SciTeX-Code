#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-18 18:14:26 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/_subplots/_export_as_csv_formatters/_format_plot_box.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/plt/_subplots/_export_as_csv_formatters/_format_plot_box.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import numpy as np
import pandas as pd

def _format_plot_box(id, tracked_dict, kwargs):
    """Format data from a plot_box call."""
    # Check if tracked_dict is empty or not a dictionary
    if not tracked_dict or not isinstance(tracked_dict, dict):
        return pd.DataFrame()
    
    # First try to get data directly from tracked_dict
    data = tracked_dict.get('data')
    
    # If no data key, get from args
    if data is None:
        args = tracked_dict.get('args', [])
        if len(args) >= 1:
            data = args[0]
        else:
            return pd.DataFrame()
    
    # If data is a simple array or list of values
    if isinstance(data, (np.ndarray, list)) and len(data) > 0:
        try:
            # Check if it's a simple list of values or a list of lists
            if isinstance(data[0], (int, float, np.number)):
                return pd.DataFrame({f"{id}_plot_box_values": data})
                
            # If data is a list of arrays (multiple box plots)
            elif isinstance(data, (list, tuple)) and all(
                isinstance(x, (list, np.ndarray)) for x in data
            ):
                result = pd.DataFrame()
                for i, values in enumerate(data):
                    try:
                        result[f"{id}_plot_box_group{i:02d}"] = pd.Series(values)
                    except:
                        # Handle case where values may not be convertible to Series
                        pass
                return result
        except (IndexError, TypeError):
            # Return empty DataFrame if we can't process the data
            pass
    
    # If data is a dictionary
    elif isinstance(data, dict):
        result = pd.DataFrame()
        for label, values in data.items():
            try:
                result[f"{id}_plot_box_{label}"] = pd.Series(values)
            except:
                # Handle case where values may not be convertible to Series
                pass
        return result
    
    # If data is a DataFrame
    elif isinstance(data, pd.DataFrame):
        result = pd.DataFrame()
        for col in data.columns:
            result[f"{id}_plot_box_{col}"] = data[col]
        return result
    
    # Default case: return empty DataFrame if nothing could be processed
    return pd.DataFrame()