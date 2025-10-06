#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-18 18:14:26 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/_subplots/_export_as_csv_formatters/_format_contour.py
# ----------------------------------------
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import pandas as pd

def _format_contour(id, tracked_dict, kwargs):
    """Format data from a contour call."""
    # Check if tracked_dict is empty or not a dictionary
    if not tracked_dict or not isinstance(tracked_dict, dict):
        return pd.DataFrame()
    
    # Get the args from tracked_dict
    args = tracked_dict.get('args', [])
    
    # Typical args: X, Y, Z where X and Y are 2D coordinate arrays and Z is the height array
    if len(args) >= 3:
        X, Y, Z = args[:3]
        # Convert mesh grids to column vectors for export
        X_flat = X.flatten()
        Y_flat = Y.flatten()
        Z_flat = Z.flatten()
        df = pd.DataFrame(
            {
                f"{id}_contour_x": X_flat,
                f"{id}_contour_y": Y_flat,
                f"{id}_contour_z": Z_flat,
            }
        )
        return df
    return pd.DataFrame()