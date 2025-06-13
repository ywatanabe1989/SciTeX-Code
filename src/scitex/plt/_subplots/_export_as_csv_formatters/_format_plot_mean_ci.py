#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-18 18:14:26 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/_subplots/_export_as_csv_formatters/_format_plot_mean_ci.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/plt/_subplots/_export_as_csv_formatters/_format_plot_mean_ci.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import pandas as pd

def _format_plot_mean_ci(id, tracked_dict, kwargs):
    """Format data from a plot_mean_ci call.
    
    Processes mean with confidence interval band plot data for CSV export.
    
    Args:
        id (str): Identifier for the plot
        tracked_dict (dict): Contains 'plot_df' (pandas DataFrame with mean and CI data)
        kwargs (dict): Keyword arguments passed to plot_mean_ci
        
    Returns:
        pd.DataFrame: Formatted mean and CI data
    """
    # Mean-CI plot data is typically passed in the plot_df in the args dictionary
    if not args:
        return pd.DataFrame()
    
    # Get the plot_df from args
    plot_df = tracked_dict.get('plot_df')
    
    if plot_df is None or not isinstance(plot_df, pd.DataFrame):
        return pd.DataFrame()
    
    # Create a copy to avoid modifying the original
    result = plot_df.copy()
    
    # Add prefix to column names if ID is provided
    if id is not None:
        # Rename columns with ID prefix
        result.columns = [f"{id}_mean_ci_{col}" for col in result.columns]
    
    return result