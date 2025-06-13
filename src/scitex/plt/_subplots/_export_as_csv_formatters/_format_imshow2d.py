#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-18 18:14:26 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/_subplots/_export_as_csv_formatters/_format_imshow2d.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/plt/_subplots/_export_as_csv_formatters/_format_imshow2d.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import pandas as pd

def _format_imshow2d(id, tracked_dict, kwargs):
    """Format data from an imshow2d call."""
    # Check if tracked_dict is empty or not a dictionary
    if not tracked_dict or not isinstance(tracked_dict, dict):
        return pd.DataFrame()
    
    # Get the args from tracked_dict
    args = tracked_dict.get('args', [])
    
    # Extract data if available
    if len(args) >= 1 and isinstance(args[0], pd.DataFrame):
        df = args[0].copy()
        # Add prefixes to columns and index if needed
        # df.columns = [f"{id}_imshow2d_{col}" for col in df.columns]
        # df.index = [f"{id}_imshow2d_{idx}" for idx in df.index]
        return df
    
    return pd.DataFrame()