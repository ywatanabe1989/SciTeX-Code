#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-18 18:14:26 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/_subplots/_export_as_csv_formatters/_format_sns_lineplot.py
# ----------------------------------------
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import numpy as np
import pandas as pd

def _format_sns_lineplot(id, tracked_dict, kwargs):
    """Format data from a sns_lineplot call."""
    # Line plot with potential error bands from seaborn
    if len(args) >= 1:
        data = args[0]
        x_var = kwtracked_dict.get("x")
        y_var = kwtracked_dict.get("y")

        # Handle DataFrame input with x, y variables
        if isinstance(data, pd.DataFrame) and x_var and y_var:
            result = pd.DataFrame(
                {
                    f"{id}_line_{x_var}": data[x_var],
                    f"{id}_line_{y_var}": data[y_var],
                }
            )

            # Add grouping variable if present
            hue_var = kwtracked_dict.get("hue")
            if hue_var and hue_var in data.columns:
                result[f"{id}_line_{hue_var}"] = data[hue_var]

            return result

        # Handle direct x, y data arrays
        elif (
            len(args) > 1
            and isinstance(args[0], (np.ndarray, list))
            and isinstance(args[1], (np.ndarray, list))
        ):
            x_data, y_data = args[0], args[1]
            return pd.DataFrame(
                {f"{id}_line_x": x_data, f"{id}_line_y": y_data}
            )

        # Handle DataFrame input without x, y specified
        elif isinstance(data, pd.DataFrame):
            result = data.copy()
            if id is not None:
                result.columns = [f"{id}_line_{col}" for col in result.columns]
            return result

    return pd.DataFrame()