#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-04 02:30:00 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/SciTeX-Code/src/scitex/plt/_subplots/_export_as_csv_formatters/_format_annotate.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import pandas as pd


def _make_column_name(id, suffix, method="annotate"):
    """Create column name with method descriptor, avoiding duplication.

    For example:
    - id="annotate_0", suffix="x" -> "annotate_0_x"
    - id="plot_5", suffix="x" -> "plot_5_annotate_x"
    """
    # Check if method name is already in the ID
    id_parts = id.rsplit('_', 1)
    if len(id_parts) == 2 and id_parts[0].endswith(method):
        # Method already in ID, don't duplicate
        return f"{id}_{suffix}"
    else:
        # Method not in ID, add it for clarity
        return f"{id}_{method}_{suffix}"


def _format_annotate(id, tracked_dict, kwargs):
    """Format data from an annotate call.

    matplotlib annotate signature: annotate(text, xy, xytext=None, **kwargs)
    - text: The text of the annotation
    - xy: The point (x, y) to annotate
    - xytext: The position (x, y) to place the text at (optional)
    """
    # Check if tracked_dict is empty or not a dictionary
    if not tracked_dict or not isinstance(tracked_dict, dict):
        return pd.DataFrame()

    # Get the args from tracked_dict
    args = tracked_dict.get("args", [])

    # Extract text and xy coordinates if available
    if len(args) >= 2:
        text_content = args[0]
        xy = args[1]

        # xy should be a tuple (x, y)
        if hasattr(xy, '__len__') and len(xy) >= 2:
            x, y = xy[0], xy[1]
        else:
            return pd.DataFrame()

        data = {
            _make_column_name(id, "x"): [x],
            _make_column_name(id, "y"): [y],
            _make_column_name(id, "content"): [text_content]
        }

        # Check if xytext was provided (either as third arg or in kwargs)
        xytext = None
        if len(args) >= 3:
            xytext = args[2]
        elif "xytext" in kwargs:
            xytext = kwargs["xytext"]

        if xytext is not None and hasattr(xytext, '__len__') and len(xytext) >= 2:
            data[_make_column_name(id, "text_x")] = [xytext[0]]
            data[_make_column_name(id, "text_y")] = [xytext[1]]

        # Create DataFrame with proper column names (use dict with list values)
        df = pd.DataFrame(data)
        return df

    return pd.DataFrame()

# EOF
