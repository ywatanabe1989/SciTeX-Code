#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-18 18:14:26 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/_subplots/_export_as_csv_formatters/_format_plot_ecdf.py
# ----------------------------------------
import os
import pandas as pd

__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

def _format_plot_ecdf(id, tracked_dict, kwargs):
    """Format data from a plot_ecdf call.
    
    Args:
        id (str): Identifier for the plot
        tracked_dict (dict): Dictionary containing 'ecdf_df' key with ECDF data
        kwargs (dict): Keyword arguments passed to plot_ecdf
        
    Returns:
        pd.DataFrame: Formatted ECDF data
    """
    # Check if tracked_dict is empty or not a dictionary
    if not tracked_dict or not isinstance(tracked_dict, dict):
        return pd.DataFrame()
    
    # Get the ecdf_df from tracked_dict
    ecdf_df = tracked_dict.get('ecdf_df')
    
    if ecdf_df is None or not isinstance(ecdf_df, pd.DataFrame):
        return pd.DataFrame()
    
    # Create a copy to avoid modifying the original
    result = ecdf_df.copy()
    
    # Add prefix to column names if ID is provided
    if id is not None:
        # Rename columns with ID prefix
        result.columns = [f"{id}_ecdf_{col}" for col in result.columns]
    
    return result