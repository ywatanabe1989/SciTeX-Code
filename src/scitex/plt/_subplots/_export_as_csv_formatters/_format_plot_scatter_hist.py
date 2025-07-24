#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-18 18:14:26 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/_subplots/_export_as_csv_formatters/_format_plot_scatter_hist.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/plt/_subplots/_export_as_csv_formatters/_format_plot_scatter_hist.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import numpy as np
import pandas as pd

def _format_plot_scatter_hist(id, tracked_dict, kwargs):
    """Format data from a plot_scatter_hist call.
    
    Args:
        id (str): Identifier for the plot
        tracked_dict (dict): Dictionary containing tracked data
        kwargs (dict): Keyword arguments passed to plot_scatter_hist
        
    Returns:
        pd.DataFrame: Formatted scatter histogram data
    """
    # Check if tracked_dict is empty or not a dictionary
    if not tracked_dict or not isinstance(tracked_dict, dict):
        return pd.DataFrame()
        
    # Extract data from tracked_dict
    x = tracked_dict.get('x')
    y = tracked_dict.get('y')
    
    if x is not None and y is not None:
        # Create base DataFrame with x and y values
        df = pd.DataFrame({
            f"{id}_scatter_hist_x": x, 
            f"{id}_scatter_hist_y": y
        })
        
        # Add histogram data if available
        hist_x = tracked_dict.get('hist_x')
        hist_y = tracked_dict.get('hist_y')
        bin_edges_x = tracked_dict.get('bin_edges_x')
        bin_edges_y = tracked_dict.get('bin_edges_y')
        
        # If we have histogram data
        if hist_x is not None and bin_edges_x is not None:
            # Calculate bin centers for x-axis histogram
            bin_centers_x = 0.5 * (bin_edges_x[1:] + bin_edges_x[:-1])
            
            # Create a DataFrame for x histogram data
            hist_x_df = pd.DataFrame({
                f"{id}_hist_x_bin_centers": bin_centers_x,
                f"{id}_hist_x_counts": hist_x
            })
            
            # Add it to the main DataFrame using a MultiIndex
            for i, (center, count) in enumerate(zip(bin_centers_x, hist_x)):
                df.loc[f"hist_x_{i}", f"{id}_hist_x_bin"] = center
                df.loc[f"hist_x_{i}", f"{id}_hist_x_count"] = count
        
        # If we have y histogram data
        if hist_y is not None and bin_edges_y is not None:
            # Calculate bin centers for y-axis histogram
            bin_centers_y = 0.5 * (bin_edges_y[1:] + bin_edges_y[:-1])
            
            # Create a DataFrame for y histogram data
            hist_y_df = pd.DataFrame({
                f"{id}_hist_y_bin_centers": bin_centers_y,
                f"{id}_hist_y_counts": hist_y
            })
            
            # Add it to the main DataFrame using a MultiIndex
            for i, (center, count) in enumerate(zip(bin_centers_y, hist_y)):
                df.loc[f"hist_y_{i}", f"{id}_hist_y_bin"] = center
                df.loc[f"hist_y_{i}", f"{id}_hist_y_count"] = count
                
        return df
        
    return pd.DataFrame()