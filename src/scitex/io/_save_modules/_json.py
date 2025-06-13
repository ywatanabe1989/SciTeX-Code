#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-16 12:27:18 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/io/_save_modules/_json.py

import json


def _save_json(obj, spath):
    """
    Save a Python object as a JSON file.
    
    Parameters
    ----------
    obj : dict or list
        The object to serialize to JSON.
    spath : str
        Path where the JSON file will be saved.
        
    Returns
    -------
    None
    """
    with open(spath, "w") as f:
        json.dump(obj, f, indent=4)
