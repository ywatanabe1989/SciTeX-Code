#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-16 12:27:18 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/io/_save_modules/_json.py

import json
from typing import Any


def _convert_to_serializable(obj: Any) -> Any:
    """
    Convert non-JSON-serializable objects to serializable format.

    Handles:
    - DotDict -> dict
    - DataFrame -> dict of lists
    - numpy arrays -> lists
    - etc.
    """
    # Handle DotDict
    if hasattr(obj, '__class__') and obj.__class__.__name__ == 'DotDict':
        return _convert_to_serializable(dict(obj))

    # Handle pandas DataFrame
    if hasattr(obj, '__class__') and obj.__class__.__name__ == 'DataFrame':
        return obj.to_dict('list')

    # Handle numpy arrays
    if hasattr(obj, 'tolist'):
        return obj.tolist()

    # Handle dict recursively
    if isinstance(obj, dict):
        return {key: _convert_to_serializable(value) for key, value in obj.items()}

    # Handle list recursively
    if isinstance(obj, list):
        return [_convert_to_serializable(item) for item in obj]

    # Handle tuple
    if isinstance(obj, tuple):
        return list(obj)

    # Default: return as-is and let json.dump handle or error
    return obj


def _save_json(obj, spath):
    """
    Save a Python object as a JSON file.

    Automatically converts DotDict objects and pandas DataFrames
    to JSON-serializable formats.

    Parameters
    ----------
    obj : dict, list, DotDict, or other JSON-serializable object
        The object to serialize to JSON.
    spath : str
        Path where the JSON file will be saved.

    Returns
    -------
    None
    """
    # Convert to serializable format
    serializable_obj = _convert_to_serializable(obj)

    with open(spath, "w") as f:
        json.dump(serializable_obj, f, indent=4)
