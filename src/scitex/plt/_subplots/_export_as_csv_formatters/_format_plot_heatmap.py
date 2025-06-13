#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-18 18:14:26 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/_subplots/_export_as_csv_formatters/_format_plot_heatmap.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/plt/_subplots/_export_as_csv_formatters/_format_plot_heatmap.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import numpy as np
import pandas as pd

def _format_plot_heatmap(id, tracked_dict, kwargs):
    """Format data from a plot_heatmap call.
    
    Exports heatmap data in xyz format (x, y, value) for better compatibility.
    
    Args:
        id (str): Identifier for the plot
        tracked_dict (dict): Dictionary containing tracked data
        kwargs (dict): Keyword arguments passed to plot_heatmap
        
    Returns:
        pd.DataFrame: Formatted heatmap data in xyz format
    """
    # Check if tracked_dict is empty or not a dictionary
    if not tracked_dict or not isinstance(tracked_dict, dict):
        return pd.DataFrame()
        
    # Extract data from tracked_dict
    data = tracked_dict.get('data')
    x_labels = tracked_dict.get('x_labels')
    y_labels = tracked_dict.get('y_labels')
    
    if data is not None and hasattr(data, "shape") and len(data.shape) == 2:
        rows, cols = data.shape
        row_indices, col_indices = np.meshgrid(
            range(rows), range(cols), indexing="ij"
        )
        
        # Format data in xyz format (x, y, value)
        df = pd.DataFrame(
            {
                f"{id}_x": col_indices.flatten(),  # x is column
                f"{id}_y": row_indices.flatten(),  # y is row
                f"{id}_value": data.flatten(),     # z is intensity/value
            }
        )
        
        # Add label information if available
        if x_labels is not None and len(x_labels) == cols:
            # Map column indices to x labels (columns are x)
            x_label_map = {i: label for i, label in enumerate(x_labels)}
            df[f"{id}_x_label"] = df[f"{id}_x"].map(x_label_map)
            
        if y_labels is not None and len(y_labels) == rows:
            # Map row indices to y labels (rows are y)
            y_label_map = {i: label for i, label in enumerate(y_labels)}
            df[f"{id}_y_label"] = df[f"{id}_y"].map(y_label_map)
            
        return df
        
    return pd.DataFrame()