#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-18 18:14:26 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/_subplots/_export_as_csv_formatters/_format_plot.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/plt/_subplots/_export_as_csv_formatters/_format_plot.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from collections import OrderedDict
import numpy as np
import pandas as pd
import xarray as xr

def _format_plot(id, tracked_dict, kwargs):
    """Format data from a plot call.

    Args:
        id (str): Identifier for the plot
        tracked_dict (dict): Dictionary containing tracked data
        kwargs (dict): Keyword arguments passed to plot

    Returns:
        pd.DataFrame: Formatted data from plot
    """
    # Check if tracked_dict is empty or not a dictionary
    if not tracked_dict or not isinstance(tracked_dict, dict):
        return pd.DataFrame()
    
    # For plot_line, we expect a 'plot_df' key
    if 'plot_df' in tracked_dict:
        plot_df = tracked_dict['plot_df']
        if isinstance(plot_df, pd.DataFrame):
            # Add the id prefix to all columns
            return plot_df.add_prefix(f"{id}_")
    
    # Legacy handling for tracked args (should be deprecated)
    if 'args' in tracked_dict:
        args = tracked_dict['args']
        if isinstance(args, tuple) and len(args) > 0:
            if len(args) == 1:
                args_value = args[0]
                if hasattr(args_value, 'ndim') and args_value.ndim == 2:
                    x, y = args_value[:, 0], args_value[:, 1]
                    df = pd.DataFrame({f"{id}_plot_x": x, f"{id}_plot_y": y})
                    return df

            elif len(args) == 2:
                x, y = args
                if isinstance(y, (np.ndarray, xr.DataArray)):
                    if y.ndim == 2:
                        out = OrderedDict()
                        for ii in range(y.shape[1]):
                            out[f"{id}_plot_x{ii:02d}"] = x
                            out[f"{id}_plot_y{ii:02d}"] = y[:, ii]
                        df = pd.DataFrame(out)
                        return df

                if isinstance(y, pd.DataFrame):
                    df = pd.DataFrame(
                        {
                            f"{id}_plot_x": x,
                            **{
                                f"{id}_plot_y{ii:02d}": np.array(y[col])
                                for ii, col in enumerate(y.columns)
                            },
                        }
                    )
                    return df

                if isinstance(y, (np.ndarray, xr.DataArray, list)):
                    df = pd.DataFrame({f"{id}_plot_x": x, f"{id}_plot_y": y})
                    return df

    # Default empty DataFrame if we can't process the input
    return pd.DataFrame()