#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-18 18:14:26 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/_subplots/_export_as_csv_formatters/_format_plot_rectangle.py
# ----------------------------------------
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import numpy as np
import pandas as pd

def _format_plot_rectangle(id, tracked_dict, kwargs):
    """Format data from a plot_rectangle call."""
    # Check if tracked_dict is empty or not a dictionary
    if not tracked_dict or not isinstance(tracked_dict, dict):
        return pd.DataFrame()
    
    # Try to get rectangle parameters directly from tracked_dict
    x = tracked_dict.get('x')
    y = tracked_dict.get('y')
    width = tracked_dict.get('width')
    height = tracked_dict.get('height')
    
    # If direct parameters aren't available, try the args
    if any(param is None for param in [x, y, width, height]):
        args = tracked_dict.get('args', [])
        
        # Rectangles defined by [x, y, width, height]
        if len(args) >= 4:
            x, y, width, height = args[0], args[1], args[2], args[3]
    
    # If we have all required parameters, create the DataFrame
    if all(param is not None for param in [x, y, width, height]):
        try:
            # Handle single rectangle
            if all(isinstance(val, (int, float, np.number)) for val in [x, y, width, height]):
                return pd.DataFrame(
                    {
                        f"{id}_rectangle_x": [x],
                        f"{id}_rectangle_y": [y],
                        f"{id}_rectangle_width": [width],
                        f"{id}_rectangle_height": [height],
                    }
                )
            
            # Handle multiple rectangles (arrays)
            elif all(
                isinstance(val, (np.ndarray, list))
                for val in [x, y, width, height]
            ):
                try:
                    result_df = pd.DataFrame(
                        {
                            f"{id}_rectangle_x": x,
                            f"{id}_rectangle_y": y,
                            f"{id}_rectangle_width": width,
                            f"{id}_rectangle_height": height,
                        }
                    )
                    return result_df
                except ValueError:
                    # Handle case where arrays might be different lengths
                    result = pd.DataFrame()
                    result[f"{id}_rectangle_x"] = pd.Series(x)
                    result[f"{id}_rectangle_y"] = pd.Series(y)
                    result[f"{id}_rectangle_width"] = pd.Series(width)
                    result[f"{id}_rectangle_height"] = pd.Series(height)
                    return result
        except Exception:
            # Fallback for rectangle in case of any errors
            try:
                return pd.DataFrame({
                    f"{id}_rectangle_x": [float(x) if x is not None else 0],
                    f"{id}_rectangle_y": [float(y) if y is not None else 0],
                    f"{id}_rectangle_width": [float(width) if width is not None else 0],
                    f"{id}_rectangle_height": [float(height) if height is not None else 0],
                })
            except (TypeError, ValueError):
                pass
    
    # Check directly in the kwtracked_dict for the parameters
    rect_x = kwargs.get('x')
    rect_y = kwargs.get('y')
    rect_w = kwargs.get('width')
    rect_h = kwargs.get('height')
    
    if all(param is not None for param in [rect_x, rect_y, rect_w, rect_h]):
        try:
            return pd.DataFrame({
                f"{id}_rectangle_x": [float(rect_x)],
                f"{id}_rectangle_y": [float(rect_y)],
                f"{id}_rectangle_width": [float(rect_w)],
                f"{id}_rectangle_height": [float(rect_h)],
            })
        except (TypeError, ValueError):
            pass
    
    # Default empty DataFrame if nothing could be processed
    return pd.DataFrame()