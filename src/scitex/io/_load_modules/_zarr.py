#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-11 15:44:42 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/io/_load_modules/_zarr.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/io/_load_modules/_zarr.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
import pickle
from typing import Any, Optional

import zarr


def _load_zarr(lpath: str, key: Optional[str] = None, **kwargs) -> Any:
    """
    Load data from Zarr store.

    Parameters:
    -----------
    lpath : str
        Path to Zarr store (directory, .zarr.zip, or consolidated)
    key : str, optional
        Key/group path within Zarr store

    Returns:
    --------
    Any : Loaded data
    """
    from pathlib import Path
    
    lpath_obj = Path(lpath)
    
    try:
        # Check if it's a zip store
        if lpath.endswith('.zip') or lpath.endswith('.zarr.zip'):
            store = zarr.ZipStore(lpath, mode='r')
            root = zarr.open(store, mode='r')
        # Check if it's consolidated
        elif lpath_obj.joinpath('.zmetadata').exists():
            root = zarr.open_consolidated(lpath, mode='r')
        else:
            # Regular directory store
            root = zarr.open(lpath, mode="r")
    except ValueError as e:
        raise FileNotFoundError(f"Cannot open Zarr store: {lpath}")

    # Navigate to target
    if key:
        if key not in root:
            raise KeyError(f"Key '{key}' not found in Zarr store")
        target = root[key]
    else:
        target = root

    # Load data
    if hasattr(target, "keys"):  # Group
        result = {}

        for item_key in target.keys():
            item = target[item_key]

            if hasattr(item, "keys"):  # Nested group
                result[item_key] = _load_zarr_group(item)
            else:  # Dataset
                result[item_key] = _load_zarr_dataset(item)

        # Load attributes
        if hasattr(target, "attrs"):
            for attr_key, attr_value in target.attrs.items():
                result[f"_attr_{attr_key}"] = attr_value

        return result

    else:  # Dataset
        return _load_zarr_dataset(target)


def _load_zarr_group(group):
    """Recursively load Zarr group."""
    result = {}

    for key in group.keys():
        item = group[key]
        if hasattr(item, "keys"):  # Nested group
            result[key] = _load_zarr_group(item)
        else:  # Dataset
            result[key] = _load_zarr_dataset(item)

    # Load attributes
    if hasattr(group, "attrs"):
        for attr_key, attr_value in group.attrs.items():
            result[f"_attr_{attr_key}"] = attr_value

    return result


def _load_zarr_dataset(dataset):
    """Load individual Zarr dataset."""
    # Check if it's pickled data
    if hasattr(dataset, "attrs") and dataset.attrs.get("_type") == "pickled":
        pickled_bytes = dataset[:]
        return pickle.loads(pickled_bytes.tobytes())
    
    # Check if it's a string
    if hasattr(dataset, "attrs") and dataset.attrs.get("_type") == "string":
        data = dataset[:]
        return data.decode('utf-8') if hasattr(data, 'decode') else str(data)

    # Regular data
    # Handle 0-d arrays (scalars) differently
    if dataset.ndim == 0:
        data = dataset[()]
    else:
        data = dataset[:]

    # Handle string data
    if dataset.dtype.kind == "U":  # Unicode string
        return str(data) if dataset.ndim == 0 else data
    elif dataset.dtype.kind == "S":  # Byte string
        return data.decode('utf-8') if hasattr(data, 'decode') else str(data)

    return data

# EOF
