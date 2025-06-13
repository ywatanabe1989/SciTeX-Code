#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-18 18:14:26 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/_subplots/_export_as_csv_formatters/_format_plot_kde.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/plt/_subplots/_export_as_csv_formatters/_format_plot_kde.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import pandas as pd
from scitex.pd import force_df

def _format_plot_kde(id, tracked_dict, kwargs):
    """Format data from a plot_kde call.
    
    Processes kernel density estimation plot data.
    
    Args:
        id (str): Identifier for the plot
        tracked_dict (dict): Dictionary containing 'x', 'kde', and 'n' keys
        kwargs (dict): Keyword arguments passed to plot_kde
        
    Returns:
        pd.DataFrame: Formatted KDE data
    """
    # Check if tracked_dict is empty or not a dictionary
    if not tracked_dict or not isinstance(tracked_dict, dict):
        return pd.DataFrame()
    
    x = tracked_dict.get('x')
    kde = tracked_dict.get('kde')
    n = tracked_dict.get('n')
    
    if x is None or kde is None:
        return pd.DataFrame()
    
    df = pd.DataFrame({
        f"{id}_kde_x": x,
        f"{id}_kde_density": kde
    })
    
    # Add sample count if available
    if n is not None:
        # If n is a scalar, create a list with the same length as x
        if not hasattr(n, '__len__'):
            n = [n] * len(x)
        df[f"{id}_kde_n"] = n
        
    return df