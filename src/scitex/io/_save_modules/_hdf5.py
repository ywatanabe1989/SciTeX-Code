#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-01 21:17:00 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/io/_save_modules/_hdf5.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/io/_save_modules/_hdf5.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import pickle
import h5py
import numpy as np


def _save_hdf5(obj, spath, key=None, override=False, **kwargs):
    """
    Simple HDF5 save function optimized for single-process usage.
    
    Parameters:
    -----------
    obj : dict or any
        Object to save. Will be converted to dict if not already.
    spath : str
        Path to HDF5 file
    key : str, optional
        Key/group path within HDF5 file
    override : bool
        Whether to override existing keys
    **kwargs
        Additional arguments for HDF5 dataset creation
    """
    if not isinstance(obj, dict):
        obj = {"data": obj}
    
    if "compression" not in kwargs:
        kwargs["compression"] = "gzip"
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(spath) or ".", exist_ok=True)
    
    # Determine file mode
    mode = "a" if os.path.exists(spath) else "w"
    
    try:
        with h5py.File(spath, mode) as h5_file:
            if key:
                # Check if key exists
                key_exists = key in h5_file
                
                if not override and key_exists:
                    return
                
                if override and key_exists:
                    del h5_file[key]
                
                # Create group structure
                parts = [p for p in key.split("/") if p]
                current_group = h5_file
                
                for part in parts[:-1]:
                    if part:
                        current_group = current_group.require_group(part)
                
                final_key = parts[-1] if parts else ""
                if final_key:
                    target_group = current_group.create_group(final_key)
                else:
                    target_group = current_group
            else:
                target_group = h5_file
            
            # Save datasets
            for dataset_name, data in obj.items():
                try:
                    if isinstance(data, str):
                        target_group.create_dataset(
                            dataset_name,
                            data=data,
                            dtype=h5py.string_dtype(),
                        )
                    else:
                        data_array = np.asarray(data)
                        
                        if data_array.dtype == np.object_:
                            # Pickle complex objects
                            pickled_data = pickle.dumps(data)
                            target_group.create_dataset(
                                dataset_name,
                                data=np.void(pickled_data),
                            )
                        elif data_array.ndim == 0:
                            # Scalar data
                            target_group.create_dataset(
                                dataset_name, data=data
                            )
                        else:
                            # Array data
                            target_group.create_dataset(
                                dataset_name, data=data, **kwargs
                            )
                except Exception as e:
                    print(f"Warning: Could not save dataset '{dataset_name}': {e}")
                    continue
            
            # Ensure data is written
            h5_file.flush()
            
    except Exception as e:
        print(f"Error saving HDF5 file {spath}: {e}")
        raise

# EOF
