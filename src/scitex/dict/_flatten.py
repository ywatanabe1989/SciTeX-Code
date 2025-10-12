#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-07 21:42:24 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/dict/_flatten.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/dict/_flatten.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

def flatten(nested_dict, parent_key="", sep="_"):
    items = []
    for key, value in nested_dict.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else key
        if isinstance(value, dict):
            items.extend(flatten(value, new_key, sep=sep).items())
        elif isinstance(value, (list, tuple)):
            for idx, item in enumerate(value):
                items.append((f"{new_key}_{idx}", item))
        else:
            items.append((new_key, value))
    return dict(items)

# EOF
