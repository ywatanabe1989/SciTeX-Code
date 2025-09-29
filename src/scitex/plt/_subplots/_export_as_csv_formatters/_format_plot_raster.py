#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-18 18:14:26 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/_subplots/_export_as_csv_formatters/_format_plot_raster.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/plt/_subplots/_export_as_csv_formatters/_format_plot_raster.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import pandas as pd

def _format_plot_raster(id, tracked_dict, kwargs):
    """Format data from a plot_raster call.
    
    Args:
        id (str): Identifier for the plot
        tracked_dict (dict): Dictionary containing 'raster_digit_df' key with raster plot data
        kwargs (dict): Keyword arguments passed to plot_raster
        
    Returns:
        pd.DataFrame: Formatted raster plot data
    """
    # Check if args is empty or not a dictionary
    if not tracked_dict or not isinstance(tracked_dict, dict):
        return pd.DataFrame()
    
    # Get the raster_digit_df from args
    raster_df = tracked_dict.get('raster_digit_df')
    
    if raster_df is None or not isinstance(raster_df, pd.DataFrame):
        return pd.DataFrame()
    
    # Create a copy to avoid modifying the original
    result = raster_df.copy()
    
    # Add prefix to column names if ID is provided
    if id is not None:
        # Rename columns with ID prefix
        result.columns = [f"{id}_raster_{col}" for col in result.columns]
    
    return result