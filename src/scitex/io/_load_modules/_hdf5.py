#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-24 20:04:35 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/io/_load_modules/_hdf5.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/io/_load_modules/_hdf5.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import warnings
from typing import Any

import h5py
import numpy as np


def _load_group(group):
    """Recursively load an HDF5 group with error handling."""
    obj = {}
    for key in group.keys():
        try:
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
        except (RuntimeError, OSError) as e:
            print(f"Warning: Could not load key '{key}' from group: {e}")
            continue

    # Load attributes
    try:
        for key in group.attrs.keys():
            obj[key] = group.attrs[key]
    except (RuntimeError, OSError) as e:
        print(f"Warning: Could not load attributes: {e}")

    return obj


def _load_hdf5(lpath: str, key: str = None, **kwargs) -> Any:
    """Load HDF5 file with automatic group/root switching and robust error handling."""
    try:
        with h5py.File(lpath, "r") as hf:
            if key:
                if key not in hf:
                    return None
                target = hf[key]
            else:
                target = hf

            obj = {}
            for key_name in target.keys():
                try:
                    if isinstance(target[key_name], h5py.Group):
                        obj[key_name] = _load_group(target[key_name])
                    else:
                        dataset = target[key_name]
                        if dataset.shape == ():
                            data = dataset[()]
                        else:
                            data = dataset[:]

                        if isinstance(data, bytes):
                            obj[key_name] = data.decode("utf-8")
                        elif isinstance(data, np.void):
                            import pickle

                            obj[key_name] = pickle.loads(data.tobytes())
                        else:
                            obj[key_name] = data
                except (RuntimeError, OSError) as e:
                    print(f"Warning: Could not load key '{key_name}': {e}")
                    continue

            try:
                for attr_name in target.attrs.keys():
                    obj[attr_name] = target.attrs[attr_name]
            except (RuntimeError, OSError) as e:
                print(f"Warning: Could not load attributes: {e}")

            return obj

    except (RuntimeError, OSError) as e:
        key_warning_str = f" with {key}" if key else ""
        warnings.warn(f"Error loading {lpath}{key_warning_str}:\n{e}")
        return None

# EOF
