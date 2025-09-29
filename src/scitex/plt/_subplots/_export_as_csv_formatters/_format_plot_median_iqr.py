#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-18 18:14:26 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/_subplots/_export_as_csv_formatters/_format_plot_median_iqr.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/plt/_subplots/_export_as_csv_formatters/_format_plot_median_iqr.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import pandas as pd

def _format_plot_median_iqr(id, tracked_dict, kwargs):
    """Format data from a plot_median_iqr call.
    
    Processes median with interquartile range band plot data for CSV export.
    
    Args:
        id (str): Identifier for the plot
        tracked_dict (dict): Contains 'plot_df' (pandas DataFrame with median and IQR data)
        kwargs (dict): Keyword arguments passed to plot_median_iqr
        
    Returns:
        pd.DataFrame: Formatted median and IQR data
    """
    # Median-IQR plot data is typically passed in the plot_df in the args dictionary
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
        result.columns = [f"{id}_median_iqr_{col}" for col in result.columns]
    
    return result