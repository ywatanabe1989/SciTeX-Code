#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-18 18:14:26 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/_subplots/_export_as_csv_formatters/_format_plot_joyplot.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/plt/_subplots/_export_as_csv_formatters/_format_plot_joyplot.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import numpy as np
import pandas as pd
from scitex.pd import force_df

def _format_plot_joyplot(id, tracked_dict, kwargs):
    """Format data from a plot_joyplot call.
    
    Args:
        id (str): Identifier for the plot
        tracked_dict (dict): Dictionary containing 'joyplot_data' key with joyplot data
        kwargs (dict): Keyword arguments passed to plot_joyplot
        
    Returns:
        pd.DataFrame: Formatted joyplot data
    """
    # Check if tracked_dict is empty or not a dictionary
    if not tracked_dict or not isinstance(tracked_dict, dict):
        return pd.DataFrame()
    
    # Get joyplot_data from tracked_dict
    data = tracked_dict.get('joyplot_data')
    
    if data is None:
        return pd.DataFrame()

    # Handle different data types
    if isinstance(data, pd.DataFrame):
        # Make a copy to avoid modifying original
        result = data.copy()
        # Add prefix to column names if ID is provided
        if id is not None:
            result.columns = [f"{id}_joyplot_{col}" for col in result.columns]
        return result

    elif isinstance(data, dict):
        # Convert dictionary to DataFrame
        result = pd.DataFrame()
        for group, values in data.items():
            result[f"{id}_joyplot_{group}"] = pd.Series(values)
        return result

    elif isinstance(data, (list, tuple)) and all(
        isinstance(x, (np.ndarray, list)) for x in data
    ):
        # Convert list of arrays to DataFrame
        result = pd.DataFrame()
        for i, values in enumerate(data):
            result[f"{id}_joyplot_group{i:02d}"] = pd.Series(values)
        return result
    
    # Try to force to DataFrame as a last resort
    try:
        return force_df({f"{id}_joyplot_data": data})
    except:
        return pd.DataFrame()