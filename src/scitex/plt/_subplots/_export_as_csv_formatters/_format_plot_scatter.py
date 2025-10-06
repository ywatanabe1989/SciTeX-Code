#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-03 02:47:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/plt/_subplots/_export_as_csv_formatters/_format_plot_scatter.py
# ----------------------------------------
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import pandas as pd

def _format_plot_scatter(id, tracked_dict, kwargs):
    """Format data from a plot_scatter call.

    The plot_scatter method stores data as:
        {"scatter_df": pd.DataFrame({"x": args[0], "y": args[1]})}
    """
    # Check if tracked_dict is empty or not a dictionary
    if not tracked_dict or not isinstance(tracked_dict, dict):
        return pd.DataFrame()

    # Get the scatter_df from tracked_dict
    scatter_df = tracked_dict.get('scatter_df')

    if scatter_df is not None and isinstance(scatter_df, pd.DataFrame):
        # Rename columns to include the id
        return scatter_df.rename(columns={
            'x': f'{id}_scatter_x',
            'y': f'{id}_scatter_y'
        })

    return pd.DataFrame()

# EOF
