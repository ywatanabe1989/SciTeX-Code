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


def _format_text(id, tracked_dict, kwargs):
    """Format data from a scatter call."""
    # Check if tracked_dict is empty or not a dictionary
    if not tracked_dict or not isinstance(tracked_dict, dict):
        return pd.DataFrame()

    # Get the args from tracked_dict
    args = tracked_dict.get("args", [])

    # Extract x and y data if available
    if len(args) >= 2:
        x, y = args[0], args[1]
        # df = pd.DataFrame({f"{id}_text_x": x, f"{id}_text_y": y})
        df = pd.DataFrame(pd.Series({f"{id}_text_x": x, f"{id}_text_y": y}))
        return df

    return pd.DataFrame()

# EOF
