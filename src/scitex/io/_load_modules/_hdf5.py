#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-12 13:47:26 (ywatanabe)"
# File: /ssh:ywatanabe@sp:/home/ywatanabe/proj/.claude-worktree/scitex_repo/src/scitex/io/_load_modules/_hdf5.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/io/_load_modules/_hdf5.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

# Time-stamp: "2024-11-14 07:55:37 (ywatanabe)"

from typing import Any

import h5py
import numpy as np


def _load_group(group):
    """Recursively load an HDF5 group."""
    obj = {}
    for key in group.keys():
        if isinstance(group[key], h5py.Group):
            # Recursively load subgroups
            obj[key] = _load_group(group[key])
        else:
            # Load dataset
            dataset = group[key]
            # Check if it's a scalar dataset
            if dataset.shape == ():
                data = dataset[()]
            else:
                data = dataset[:]
            
            # Decode bytes to string if needed
            if isinstance(data, bytes):
                obj[key] = data.decode("utf-8")
            elif isinstance(data, np.void):
                # Handle pickled data
                import pickle
                obj[key] = pickle.loads(data.tobytes())
            else:
                obj[key] = data
    # Load attributes
    for key in group.attrs.keys():
        obj[key] = group.attrs[key]
    return obj


def _load_hdf5(lpath: str, group_path: str = None, **kwargs) -> Any:
    """Load HDF5 file with automatic group/root switching."""
    with h5py.File(lpath, "r") as hf:
        if group_path:
            if group_path not in hf:
                return None
            target = hf[group_path]
        else:
            target = hf

        obj = {}
        for key in target.keys():
            if isinstance(target[key], h5py.Group):
                # Recursively load groups
                obj[key] = _load_group(target[key])
            else:
                # Load dataset
                dataset = target[key]
                # Check if it's a scalar dataset
                if dataset.shape == ():
                    data = dataset[()]
                else:
                    data = dataset[:]
                
                # Decode bytes to string if needed
                if isinstance(data, bytes):
                    obj[key] = data.decode("utf-8")
                elif isinstance(data, np.void):
                    # Handle pickled data
                    import pickle
                    obj[key] = pickle.loads(data.tobytes())
                else:
                    obj[key] = data
        for key in target.attrs.keys():
            obj[key] = target.attrs[key]
        return obj


# def _load_hdf5(lpath: str, **kwargs) -> Any:
#     """Load HDF5 file."""
#     if not (lpath.endswith(".hdf5") or lpath.endswith(".h5")):
#         raise ValueError("File must have .hdf5 or .h5 extension")

#     def load_item(item):
#         """Recursively load items from HDF5."""
#         if isinstance(item, h5py.Group):
#             # Load groups as nested dicts
#             result = {}
#             for key in item.keys():
#                 result[key] = load_item(item[key])
#             return result
#         elif isinstance(item, h5py.Dataset):
#             # Load datasets
#             data = item[()]
#             # Check if it's a pickled object
#             if isinstance(data, np.void):
#                 import pickle

#                 return pickle.loads(data.tobytes())
#             # Convert bytes to string
#             elif isinstance(data, bytes):
#                 return data.decode("utf-8")
#             # Convert numpy scalars to Python types
#             elif isinstance(data, np.integer):
#                 return int(data)
#             elif isinstance(data, np.floating):
#                 return float(data)
#             elif isinstance(data, np.bool_):
#                 return bool(data)
#             else:
#                 return data
#         else:
#             return item

#     with h5py.File(lpath, "r") as hf:
#         return load_item(hf)


# def _load_hdf5_group(lpath: str, group_path: str = None, **kwargs) -> Any:
#     """Load specific group from HDF5 file."""
#     with h5py.File(lpath, "r") as hf:
#         if group_path:
#             if group_path not in hf:
#                 return None
#             group = hf[group_path]
#             result = {}
#             for key in group.keys():
#                 result[key] = group[key][:]
#             for key in group.attrs.keys():
#                 result[key] = group.attrs[key]
#             return result
#         else:
#             return _load_hdf5(lpath, **kwargs)

# # EOF

# EOF
