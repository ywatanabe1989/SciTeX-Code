#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-18 18:14:26 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/_subplots/_export_as_csv_formatters/_format_eventplot.py
# ----------------------------------------
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import numpy as np
import pandas as pd
import scitex

def _format_eventplot(id, tracked_dict, kwargs):
    """Format data from an eventplot call."""
    # Check if tracked_dict is empty or not a dictionary
    if not tracked_dict or not isinstance(tracked_dict, dict):
        return pd.DataFrame()
    
    # Get the args from tracked_dict
    args = tracked_dict.get('args', [])
    
    # Eventplot displays multiple sets of events as parallel lines
    if len(args) >= 1:
        positions = args[0]

        try:
            # Try using scitex.pd.force_df if available
            try:
                import scitex.pd

                # If positions is a single array
                if isinstance(
                    positions, (list, np.ndarray)
                ) and not isinstance(positions[0], (list, np.ndarray)):
                    return pd.DataFrame({f"{id}_eventplot_events": positions})

                # If positions is a list of arrays (multiple event sets)
                elif isinstance(positions, (list, np.ndarray)):
                    data = {}
                    for i, events in enumerate(positions):
                        data[f"{id}_eventplot_events{i:02d}"] = events

                    # Use force_df to handle different length arrays
                    return scitex.pd.force_df(data)

            except (ImportError, AttributeError):
                # Fall back to pandas with manual Series creation
                # If positions is a single array
                if isinstance(
                    positions, (list, np.ndarray)
                ) and not isinstance(positions[0], (list, np.ndarray)):
                    return pd.DataFrame({f"{id}_eventplot_events": positions})

                # If positions is a list of arrays (multiple event sets)
                elif isinstance(positions, (list, np.ndarray)):
                    # Create a DataFrame where each column is a Series that can handle varying lengths
                    df = pd.DataFrame()
                    for i, events in enumerate(positions):
                        df[f"{id}_eventplot_events{i:02d}"] = pd.Series(events)
                    return df
        except Exception as e:
            # If all else fails, return an empty DataFrame
            import warnings

            warnings.warn(f"Error formatting eventplot data: {str(e)}")
            return pd.DataFrame()

    return pd.DataFrame()