#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-18 18:14:26 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/_subplots/_export_as_csv_formatters/_format_sns_jointplot.py
# ----------------------------------------
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import numpy as np
import pandas as pd

def _format_sns_jointplot(id, tracked_dict, kwargs):
    """Format data from a sns_jointplot call."""
    # Check if tracked_dict is empty or not a dictionary
    if not tracked_dict or not isinstance(tracked_dict, dict):
        return pd.DataFrame()
    
    # Get the args from tracked_dict
    args = tracked_dict.get('args', [])
    
    # Joint distribution plot in seaborn
    if len(args) >= 1:
        data = args[0]
        
        # Get x and y variables from kwargs
        x_var = kwargs.get("x")
        y_var = kwargs.get("y")

        # Handle DataFrame input
        if isinstance(data, pd.DataFrame) and x_var and y_var:
            # Extract the relevant columns
            x_data = data[x_var]
            y_data = data[y_var]

            result = pd.DataFrame(
                {f"{id}_joint_{x_var}": x_data, f"{id}_joint_{y_var}": y_data}
            )
            return result

        # Handle direct x, y data arrays
        elif isinstance(data, pd.DataFrame):
            # If no x, y specified, return the whole dataframe
            result = data.copy()
            if id is not None:
                result.columns = [
                    f"{id}_joint_{col}" for col in result.columns
                ]
            return result

        # Handle numpy arrays directly
        elif (
            all(arg in args for arg in range(2))
            and isinstance(args[0], (np.ndarray, list))
            and isinstance(args[1], (np.ndarray, list))
        ):
            x_data, y_data = args[0], args[1]
            return pd.DataFrame(
                {f"{id}_joint_x": x_data, f"{id}_joint_y": y_data}
            )

    return pd.DataFrame()