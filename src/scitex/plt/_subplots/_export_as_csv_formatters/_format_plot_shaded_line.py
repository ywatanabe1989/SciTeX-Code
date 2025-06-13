#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-18 18:14:26 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/_subplots/_export_as_csv_formatters/_format_plot_shaded_line.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/plt/_subplots/_export_as_csv_formatters/_format_plot_shaded_line.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import pandas as pd

def _format_plot_shaded_line(id, tracked_dict, kwargs):
    """Format data from a plot_shaded_line call.
    
    Args:
        id (str): Identifier for the plot
        tracked_dict (dict): Dictionary containing tracked data
        kwargs (dict): Keyword arguments passed to plot_shaded_line
        
    Returns:
        pd.DataFrame: Formatted shaded line data
    """
    # Check if tracked_dict is empty or not a dictionary
    if not tracked_dict or not isinstance(tracked_dict, dict):
        return pd.DataFrame()
        
    # If we have a plot_df from plotting methods, use that directly
    if 'plot_df' in tracked_dict and isinstance(tracked_dict['plot_df'], pd.DataFrame):
        plot_df = tracked_dict['plot_df']
        # Add the id prefix to all columns
        return plot_df.add_prefix(f"{id}_")
        
    # Try getting the individual components
    x = tracked_dict.get('x') 
    y_middle = tracked_dict.get('y_middle')
    y_lower = tracked_dict.get('y_lower')
    y_upper = tracked_dict.get('y_upper')
    
    # If we have all necessary components
    if x is not None and y_middle is not None and y_lower is not None:
        data = {
            f"{id}_shaded_line_x": x,
            f"{id}_shaded_line_y": y_middle,
            f"{id}_shaded_line_lower": y_lower,
        }
        
        if y_upper is not None:
            data[f"{id}_shaded_line_upper"] = y_upper
        else:
            # If only y_lower is provided, assume it's symmetric around y_middle
            data[f"{id}_shaded_line_upper"] = y_middle + (y_middle - y_lower)
            
        return pd.DataFrame(data)
        
    return pd.DataFrame()