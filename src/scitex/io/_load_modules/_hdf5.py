#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-12 07:04:14 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/io/_load_modules/_hdf5.py
# ----------------------------------------
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import time

import h5py
import numpy as np

from .._save_modules._hdf5 import SWMRFile


def _load_hdf5(lpath, key=None, swmr=True, max_retries=10, **kwargs):
    """Load HDF5 file with SWMR support."""
    for attempt in range(max_retries):
        try:
            with SWMRFile(lpath, "r", swmr=swmr) as h5_file:
                if key:
                    if key not in h5_file:
                        return None
                    target = h5_file[key]
                else:
                    target = h5_file

                # Load data recursively
                return _load_h5_object(target)

        except (OSError, IOError) as e:
            if attempt < max_retries - 1:
                time.sleep(0.1 * (2**attempt))
            else:
                raise

    return None


def _load_h5_object(h5_obj):
    """Recursively load HDF5 object."""
    if isinstance(h5_obj, h5py.Group):
        result = {}
        # Load datasets
        for key in h5_obj.keys():
            result[key] = _load_h5_object(h5_obj[key])
        # Load attributes
        for key in h5_obj.attrs.keys():
            result[f"_attr_{key}"] = h5_obj.attrs[key]
        return result

    elif isinstance(h5_obj, h5py.Dataset):
        data = h5_obj[()]

        # Handle different data types
        if isinstance(data, bytes):
            return data.decode("utf-8")
        elif isinstance(data, np.void):
            # Unpickle data
            import pickle

            return pickle.loads(data.tobytes())
        else:
            return data
    else:
        return h5_obj

# EOF
