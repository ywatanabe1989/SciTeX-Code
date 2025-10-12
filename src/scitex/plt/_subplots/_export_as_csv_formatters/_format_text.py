#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-21 02:39:14 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/plt/_subplots/_export_as_csv_formatters/_format_text.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import pandas as pd


def _make_column_name(id, suffix, method="text"):
    """Create column name with method descriptor, avoiding duplication.

    For example:
    - id="text_0", suffix="x" -> "text_0_x"
    - id="plot_5", suffix="x" -> "plot_5_text_x"
    """
    # Check if method name is already in the ID
    id_parts = id.rsplit('_', 1)
    if len(id_parts) == 2 and id_parts[0].endswith(method):
        # Method already in ID, don't duplicate
        return f"{id}_{suffix}"
    else:
        # Method not in ID, add it for clarity
        return f"{id}_{method}_{suffix}"


def _format_text(id, tracked_dict, kwargs):
    """Format data from a text call."""
    # Check if tracked_dict is empty or not a dictionary
    if not tracked_dict or not isinstance(tracked_dict, dict):
        return pd.DataFrame()

    # Get the args from tracked_dict
    args = tracked_dict.get("args", [])

    # Extract x, y, and text content if available
    if len(args) >= 2:
        x, y = args[0], args[1]
        text_content = args[2] if len(args) >= 3 else None

        data = {
            _make_column_name(id, "x"): [x],
            _make_column_name(id, "y"): [y]
        }

        if text_content is not None:
            data[_make_column_name(id, "content")] = [text_content]

        # Create DataFrame with proper column names (use dict with list values)
        df = pd.DataFrame(data)
        return df

    return pd.DataFrame()

# EOF
