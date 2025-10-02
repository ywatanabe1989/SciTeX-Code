#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-18 18:14:26 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/_subplots/_export_as_csv_formatters/_format_sns_barplot.py
# ----------------------------------------
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import numpy as np
import pandas as pd

def _format_sns_barplot(id, tracked_dict, kwargs):
    """Format data from a sns_barplot call.
    
    Args:
        id (str): Identifier for the plot
        tracked_dict (dict): Dictionary containing tracked data
        kwargs (dict): Keyword arguments passed to sns_barplot
        
    Returns:
        pd.DataFrame: Formatted data for the plot
    """
    # Check if tracked_dict is empty or not a dictionary
    if not tracked_dict or not isinstance(tracked_dict, dict):
        return pd.DataFrame()
    
    # If 'data' key is in tracked_dict, use it
    if 'data' in tracked_dict:
        df = tracked_dict['data']
        if isinstance(df, pd.DataFrame):
            # Add the id prefix to all columns
            return df.add_prefix(f"{id}_")
    
    # Legacy handling for args
    if 'args' in tracked_dict:
        df = tracked_dict['args']
        if isinstance(df, pd.DataFrame):
            # When xyhue, without errorbar
            try:
                processed_df = pd.DataFrame(pd.Series(np.array(df).diagonal(), index=df.columns)).T
                return processed_df.add_prefix(f"{id}_")
            except (ValueError, TypeError, IndexError):
                # If processing fails, return the original dataframe
                return df.add_prefix(f"{id}_")
    
    # Default empty DataFrame if we can't process the input
    return pd.DataFrame()