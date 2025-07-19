#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-14 05:28:34 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/io/_save_modules/_hdf5.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/io/_save_modules/_hdf5.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import fcntl
import pickle
import shutil
import tempfile
import time

import h5py
import numpy as np


class SWMRFile:
    """Context manager for SWMR-enabled HDF5 files."""

    def __init__(self, filepath, mode="r", swmr=True, timeout=300):
        self.filepath = filepath
        self.mode = mode
        self.swmr = swmr
        self.timeout = timeout
        self.file = None
        self.temp_file = None

    def __enter__(self):
        start_time = time.time()

        while time.time() - start_time < self.timeout:
            try:
                if self.mode in ["w", "w-"]:
                    # For write mode, create new file
                    self.file = h5py.File(
                        self.filepath, self.mode, libver="latest"
                    )
                    if self.swmr:
                        self.file.swmr_mode = True
                    return self.file

                elif self.mode == "a":
                    # For append mode, handle SWMR carefully
                    if os.path.exists(self.filepath):
                        # Try to open in read mode first to check SWMR status
                        try:
                            with h5py.File(self.filepath, "r") as test_file:
                                is_swmr = test_file.swmr_mode
                        except:
                            is_swmr = False

                        if is_swmr:
                            # File is in SWMR mode, we need to copy and modify
                            self.temp_file = tempfile.NamedTemporaryFile(
                                delete=False, suffix=".h5"
                            )
                            shutil.copy2(self.filepath, self.temp_file.name)
                            self.file = h5py.File(
                                self.temp_file.name, "r+", libver="latest"
                            )
                        else:
                            # Normal append mode
                            self.file = h5py.File(
                                self.filepath, "r+", libver="latest"
                            )
                            if self.swmr:
                                self.file.swmr_mode = True
                    else:
                        # Create new file
                        self.file = h5py.File(
                            self.filepath, "w", libver="latest"
                        )
                        if self.swmr:
                            self.file.swmr_mode = True
                    return self.file

                elif self.mode == "r":
                    # Read mode with SWMR
                    self.file = h5py.File(
                        self.filepath, "r", libver="latest", swmr=True
                    )
                    return self.file

            except (OSError, IOError) as e:
                if "Resource temporarily unavailable" in str(e):
                    time.sleep(
                        0.1 * (2 ** min(5, (time.time() - start_time) / 10))
                    )
                else:
                    raise

        raise TimeoutError(
            f"Could not open {self.filepath} within {self.timeout} seconds"
        )

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.file:
            self.file.close()

        # If we used a temp file, move it back
        if self.temp_file and exc_type is None:
            shutil.move(self.temp_file.name, self.filepath)
        elif self.temp_file:
            os.unlink(self.temp_file.name)


def _save_hdf5(
    obj,
    spath,
    key=None,
    override=False,
    swmr=True,
    compression="gzip",
    compression_opts=4,
    max_retries=10,
    **kwargs,
):
    """
    HDF5 save function with SWMR support for HPC environments.

    Parameters:
    -----------
    obj : dict or any
        Object to save
    spath : str
        Path to HDF5 file
    key : str, optional
        Key/group path within HDF5 file
    override : bool
        Whether to override existing keys
    swmr : bool
        Enable SWMR mode (default: True)
    compression : str
        Compression algorithm (default: 'gzip')
    compression_opts : int
        Compression level (default: 4)
    max_retries : int
        Maximum number of retry attempts
    """
    if not isinstance(obj, dict):
        obj = {"data": obj}

    # Ensure directory exists
    os.makedirs(os.path.dirname(spath) or ".", exist_ok=True)

    # Lock file for coordination
    lock_file = f"{spath}.lock"

    for attempt in range(max_retries):
        try:
            # Use file locking for write coordination
            with open(lock_file, "w") as lock_fd:
                fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)

                try:
                    mode = "a" if os.path.exists(spath) else "w"

                    with SWMRFile(spath, mode, swmr=swmr) as h5_file:
                        if key:
                            # Check if key exists
                            if key in h5_file and not override:
                                return

                            if key in h5_file and override:
                                del h5_file[key]

                            # Create group structure
                            parts = [p for p in key.split("/") if p]
                            current_group = h5_file

                            for part in parts[:-1]:
                                if part:
                                    current_group = (
                                        current_group.require_group(part)
                                    )

                            final_key = parts[-1] if parts else ""
                            if final_key:
                                target_group = current_group.create_group(
                                    final_key
                                )
                            else:
                                target_group = current_group
                        else:
                            target_group = h5_file

                        # Save datasets with chunking for large arrays
                        for dataset_name, data in obj.items():
                            _save_dataset(
                                target_group,
                                dataset_name,
                                data,
                                compression,
                                compression_opts,
                                **kwargs,
                            )

                        # Flush to ensure data is written
                        h5_file.flush()

                finally:
                    fcntl.flock(lock_fd, fcntl.LOCK_UN)

                return  # Success

        except (OSError, IOError) as e:
            if attempt < max_retries - 1:
                time.sleep(0.1 * (2**attempt))
            else:
                raise

    raise RuntimeError(
        f"Failed to save to {spath} after {max_retries} attempts"
    )


def _save_dataset(group, name, data, compression, compression_opts, **kwargs):
    """Save a single dataset with appropriate settings."""
    try:
        if isinstance(data, str):
            group.create_dataset(name, data=data, dtype=h5py.string_dtype())

        elif hasattr(data, "__array__"):
            # NumPy arrays and array-like objects
            data_array = np.asarray(data)

            # Determine chunk size for large arrays
            chunks = None
            if data_array.size > 1000:
                chunks = True  # Let h5py auto-determine chunks

            # Check if we should use compression
            use_compression = compression if data_array.size > 100 else None

            group.create_dataset(
                name,
                data=data_array,
                compression=use_compression,
                compression_opts=compression_opts if use_compression else None,
                chunks=chunks,
                **kwargs,
            )

        elif isinstance(data, (list, tuple)) and len(data) > 0:
            # Try to convert to array
            try:
                data_array = np.asarray(data)
                if data_array.dtype != np.object_:
                    group.create_dataset(name, data=data_array)
                else:
                    # Pickle complex objects
                    pickled_data = pickle.dumps(data)
                    group.create_dataset(name, data=np.void(pickled_data))
            except:
                # Pickle if conversion fails
                pickled_data = pickle.dumps(data)
                group.create_dataset(name, data=np.void(pickled_data))

        else:
            # For all other types, try direct save or pickle
            try:
                group.create_dataset(name, data=data)
            except:
                pickled_data = pickle.dumps(data)
                group.create_dataset(name, data=np.void(pickled_data))

    except Exception as e:
        print(f"Warning: Could not save dataset '{name}': {e}")

# EOF
