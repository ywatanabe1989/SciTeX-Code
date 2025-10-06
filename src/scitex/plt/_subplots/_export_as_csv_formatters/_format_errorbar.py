#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-18 18:14:26 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/_subplots/_export_as_csv_formatters/_format_errorbar.py
# ----------------------------------------
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import numpy as np
import pandas as pd
import scitex

def _format_errorbar(id, tracked_dict, kwargs):
    """Format data from an errorbar call."""
    # Check if tracked_dict is empty or not a dictionary
    if not tracked_dict or not isinstance(tracked_dict, dict):
        return pd.DataFrame()
    
    # Get the args from tracked_dict
    args = tracked_dict.get('args', [])
    
    # Typical args: x, y
    # Typical kwargs: xerr, yerr
    if len(args) >= 2:
        x, y = args[:2]
        xerr = kwargs.get("xerr")
        yerr = kwargs.get("yerr")

        try:
            # Try using scitex.pd.force_df if available
            try:
                import scitex.pd

                data = {f"{id}_errorbar_x": x, f"{id}_errorbar_y": y}

                if xerr is not None:
                    if isinstance(xerr, (list, tuple)) and len(xerr) == 2:
                        # Asymmetric error
                        data[f"{id}_errorbar_xerr_neg"] = xerr[0]
                        data[f"{id}_errorbar_xerr_pos"] = xerr[1]
                    else:
                        # Symmetric error
                        data[f"{id}_errorbar_xerr"] = xerr

                if yerr is not None:
                    if isinstance(yerr, (list, tuple)) and len(yerr) == 2:
                        # Asymmetric error
                        data[f"{id}_errorbar_yerr_neg"] = yerr[0]
                        data[f"{id}_errorbar_yerr_pos"] = yerr[1]
                    else:
                        # Symmetric error
                        data[f"{id}_errorbar_yerr"] = yerr

                # Use scitex.pd.force_df to handle different length arrays
                df = scitex.pd.force_df(data)
                return df
            except (ImportError, AttributeError):
                # Fall back to pandas with manual padding
                max_len = max(
                    [
                        len(arr) if hasattr(arr, "__len__") else 1
                        for arr in [x, y, xerr, yerr]
                        if arr is not None
                    ]
                )

                # Function to pad arrays to the same length
                def pad_to_length(arr, length):
                    if arr is None:
                        return None
                    if not hasattr(arr, "__len__"):
                        # Handle scalar values
                        return [arr] * length
                    if len(arr) >= length:
                        return arr
                    # Pad with NaN
                    return np.pad(
                        arr,
                        (0, length - len(arr)),
                        "constant",
                        constant_values=np.nan,
                    )

                # Pad all arrays
                x_padded = pad_to_length(x, max_len)
                y_padded = pad_to_length(y, max_len)

                data = {
                    f"{id}_errorbar_x": x_padded,
                    f"{id}_errorbar_y": y_padded,
                }

                if xerr is not None:
                    if isinstance(xerr, (list, tuple)) and len(xerr) == 2:
                        xerr_neg_padded = pad_to_length(xerr[0], max_len)
                        xerr_pos_padded = pad_to_length(xerr[1], max_len)
                        data[f"{id}_errorbar_xerr_neg"] = xerr_neg_padded
                        data[f"{id}_errorbar_xerr_pos"] = xerr_pos_padded
                    else:
                        xerr_padded = pad_to_length(xerr, max_len)
                        data[f"{id}_errorbar_xerr"] = xerr_padded

                if yerr is not None:
                    if isinstance(yerr, (list, tuple)) and len(yerr) == 2:
                        yerr_neg_padded = pad_to_length(yerr[0], max_len)
                        yerr_pos_padded = pad_to_length(yerr[1], max_len)
                        data[f"{id}_errorbar_yerr_neg"] = yerr_neg_padded
                        data[f"{id}_errorbar_yerr_pos"] = yerr_pos_padded
                    else:
                        yerr_padded = pad_to_length(yerr, max_len)
                        data[f"{id}_errorbar_yerr"] = yerr_padded

                return pd.DataFrame(data)
        except Exception as e:
            # If all else fails, return an empty DataFrame
            import warnings

            warnings.warn(f"Error formatting errorbar data: {str(e)}")
            return pd.DataFrame()

    return pd.DataFrame()