#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-18 18:14:26 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/_subplots/_export_as_csv_formatters/_format_sns_kdeplot.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/plt/_subplots/_export_as_csv_formatters/_format_sns_kdeplot.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import numpy as np
import pandas as pd

def _format_sns_kdeplot(id, tracked_dict, kwargs):
    """Format data from a sns_kdeplot call."""
    # Kernel density estimate plot
    if len(args) >= 1:
        data = args[0]
        x_var = kwtracked_dict.get("x")
        y_var = kwtracked_dict.get("y")

        # Handle DataFrame input with x, y variables
        if isinstance(data, pd.DataFrame) and x_var:
            if y_var:  # Bivariate KDE
                result = pd.DataFrame(
                    {
                        f"{id}_kde_{x_var}": data[x_var],
                        f"{id}_kde_{y_var}": data[y_var],
                    }
                )
            else:  # Univariate KDE
                result = pd.DataFrame({f"{id}_kde_{x_var}": data[x_var]})
            return result

        # Handle direct data array input
        elif isinstance(data, (np.ndarray, list)):
            y_data = (
                args[1]
                if len(args) > 1 and isinstance(args[1], (np.ndarray, list))
                else None
            )

            if y_data is not None:  # Bivariate KDE
                return pd.DataFrame(
                    {f"{id}_kde_x": data, f"{id}_kde_y": y_data}
                )
            else:  # Univariate KDE
                return pd.DataFrame({f"{id}_kde_x": data})

        # Handle DataFrame input without x, y specified
        elif isinstance(data, pd.DataFrame):
            result = data.copy()
            if id is not None:
                result.columns = [f"{id}_kde_{col}" for col in result.columns]
            return result

    return pd.DataFrame()