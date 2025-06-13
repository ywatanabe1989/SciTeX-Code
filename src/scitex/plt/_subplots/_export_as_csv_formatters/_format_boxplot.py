#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-18 18:14:26 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/_subplots/_export_as_csv_formatters/_format_boxplot.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/plt/_subplots/_export_as_csv_formatters/_format_boxplot.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import numpy as np
import pandas as pd
import scitex

def _format_boxplot(id, tracked_dict, kwargs):
    """Format data from a boxplot call."""
    # Check if tracked_dict is empty or not a dictionary
    if not tracked_dict or not isinstance(tracked_dict, dict):
        return pd.DataFrame()
    
    # Get the args from tracked_dict
    args = tracked_dict.get('args', [])
    
    # Extract data if available
    if len(args) >= 1:
        x = args[0]
        
        # One box plot
        from scitex.types import is_listed_X as scitex_types_is_listed_X
        
        if isinstance(x, np.ndarray) or scitex_types_is_listed_X(x, [float, int]):
            df = pd.DataFrame(x)
        else:
            # Multiple boxes
            import scitex.pd
            df = scitex.pd.force_df({i_x: _x for i_x, _x in enumerate(x)})
        
        # Add prefix to columns
        df.columns = [f"{id}_boxplot_{col}_x" for col in df.columns]
        df = df.apply(lambda col: col.dropna().reset_index(drop=True))
        return df
    
    # No valid data available
    return pd.DataFrame()