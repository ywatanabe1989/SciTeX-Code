#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-18 18:14:26 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/_subplots/_export_as_csv_formatters/_format_plot_image.py
# ----------------------------------------
import os
import numpy as np
import pandas as pd

__FILE__ = (
    "./src/scitex/plt/_subplots/_export_as_csv_formatters/_format_plot_image.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

def _format_plot_image(id, tracked_dict, kwargs):
    """Format data from a plot_image call.
    
    Exports image data in long-format xyz format for better compatibility.
    Also saves channel data for RGB/RGBA images.
    
    Args:
        id (str or int): Identifier for the plot
        tracked_dict (dict): Dictionary containing tracked data
        kwargs (dict): Keyword arguments passed to plot_image
        
    Returns:
        pd.DataFrame: Formatted image data in xyz format
    """
    # Check if tracked_dict is not a dictionary or is empty
    if not tracked_dict or not isinstance(tracked_dict, dict):
        return pd.DataFrame()
        
    # Check if image_df is available and use it if present
    if "image_df" in tracked_dict:
        image_df = tracked_dict.get("image_df")
        if isinstance(image_df, pd.DataFrame):
            # Add prefix if ID is provided
            if id is not None:
                image_df = image_df.copy()
                id_str = str(id)
                image_df.columns = [f"{id_str}_{col}" if not col.startswith(f"{id_str}_") else col for col in image_df.columns]
            return image_df
    
    # If we have image data
    if "image" in tracked_dict:
        img = tracked_dict["image"]
        id_str = str(id) if id is not None else "image"
        
        # Handle 2D grayscale images - create xyz format (x, y, value)
        if isinstance(img, np.ndarray) and img.ndim == 2:
            rows, cols = img.shape
            row_indices, col_indices = np.meshgrid(
                range(rows), range(cols), indexing="ij"
            )

            # Create xyz format
            df = pd.DataFrame(
                {
                    f"{id_str}_x": col_indices.flatten(),  # x is column
                    f"{id_str}_y": row_indices.flatten(),  # y is row
                    f"{id_str}_value": img.flatten(),      # z is intensity
                }
            )
            return df

        # Handle RGB/RGBA images - create xyz format with additional channel information
        elif isinstance(img, np.ndarray) and img.ndim == 3:
            rows, cols, channels = img.shape
            row_indices, col_indices = np.meshgrid(
                range(rows), range(cols), indexing="ij"
            )

            # Create a list to hold rows for a long-format DataFrame
            data_rows = []
            channel_names = ["r", "g", "b", "a"]
            
            # Create long-format data (x, y, channel, value)
            for r in range(rows):
                for c in range(cols):
                    for ch in range(min(channels, len(channel_names))):
                        data_rows.append({
                            f"{id_str}_x": c,                      # x is column
                            f"{id_str}_y": r,                      # y is row
                            f"{id_str}_channel": channel_names[ch],  # channel name
                            f"{id_str}_value": img[r, c, ch]        # channel value
                        })
            
            # Return long-format DataFrame
            return pd.DataFrame(data_rows)
    
    # Skip CSV export if no suitable data format found
    return pd.DataFrame()