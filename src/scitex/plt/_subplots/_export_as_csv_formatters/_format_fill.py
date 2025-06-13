#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-18 18:14:26 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/_subplots/_export_as_csv_formatters/_format_fill.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/plt/_subplots/_export_as_csv_formatters/_format_fill.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import pandas as pd

def _format_fill(id, tracked_dict, kwargs):
    """Format data from a fill call."""
    # Check if tracked_dict is empty or not a dictionary
    if not tracked_dict or not isinstance(tracked_dict, dict):
        return pd.DataFrame()
    
    # Get the args from tracked_dict
    args = tracked_dict.get('args', [])
    
    # Fill creates a polygon based on points
    if len(args) >= 2:
        # First arg is x, remaining args are y values
        x = args[0]
        data = {f"{id}_fill_x": x}

        for i, y in enumerate(args[1:]):
            data[f"{id}_fill_y{i:02d}"] = y

        return pd.DataFrame(data)
    return pd.DataFrame()