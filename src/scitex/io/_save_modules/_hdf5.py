#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-24 20:04:55 (ywatanabe)"
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
import random
import shutil
import tempfile
import time
from contextlib import contextmanager

import h5py
import numpy as np


@contextmanager
def file_lock(file_path, timeout=300):
    """Context manager for file locking with timeout."""
    lock_file = file_path + ".lock"
    lock_fd = None

    try:
        # Try to create lock file
        lock_fd = os.open(lock_file, os.O_CREAT | os.O_EXCL | os.O_RDWR)
        fcntl.flock(lock_fd, fcntl.LOCK_EX)
        yield

    except OSError:
        # Lock file exists, wait and retry
        wait_time = 0
        while wait_time < timeout:
            sleep_interval = random.uniform(1, 5)
            time.sleep(sleep_interval)
            wait_time += sleep_interval

            try:
                lock_fd = os.open(
                    lock_file, os.O_CREAT | os.O_EXCL | os.O_RDWR
                )
                fcntl.flock(lock_fd, fcntl.LOCK_EX)
                yield
                break
            except OSError:
                continue
        else:
            raise TimeoutError(
                f"Could not acquire lock for {file_path} after {timeout} seconds"
            )

    finally:
        if lock_fd is not None:
            try:
                fcntl.flock(lock_fd, fcntl.LOCK_UN)
                os.close(lock_fd)
                os.unlink(lock_file)
            except:
                pass


def _save_hdf5(obj, spath, key=None, override=False, max_retries=5, **kwargs):
    """
    Robust HDF5 save function with file locking and atomic writes.

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
    max_retries : int
        Maximum number of retry attempts
    **kwargs
        Additional arguments for HDF5 dataset creation
    """
    if not isinstance(obj, dict):
        obj = {"data": obj}

    if "compression" not in kwargs:
        kwargs["compression"] = "gzip"

    # Retry logic for handling temporary failures
    for attempt in range(max_retries):
        try:
            with file_lock(spath):
                # Use atomic write: write to temp file, then move
                temp_file = None

                try:
                    # Create temporary file in same directory
                    temp_dir = os.path.dirname(spath) or "."
                    temp_fd, temp_file = tempfile.mkstemp(
                        suffix=".h5.tmp",
                        dir=temp_dir,
                        prefix=os.path.basename(spath) + "_",
                    )
                    os.close(temp_fd)  # Close the file descriptor

                    # If file exists, copy it to temp file first
                    if os.path.exists(spath):
                        shutil.copy2(spath, temp_file)
                        mode = "a"
                    else:
                        mode = "w"

                    # Write to temporary file
                    with h5py.File(temp_file, mode) as h5_file:
                        if key:
                            # Check if the full path exists
                            key_exists = False
                            try:
                                parts = [
                                    p for p in key.split("/") if p
                                ]  # Remove empty parts
                                current = h5_file
                                for part in parts:
                                    if part in current:
                                        current = current[part]
                                    else:
                                        break
                                else:
                                    key_exists = True
                            except:
                                key_exists = False

                            if not override and key_exists:
                                return

                            if override and key_exists:
                                del h5_file[key]

                            # Create the group structure
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

                        # Save datasets
                        for dataset_name, data in obj.items():
                            if isinstance(data, str):
                                target_group.create_dataset(
                                    dataset_name,
                                    data=data,
                                    dtype=h5py.string_dtype(),
                                )
                            else:
                                data_array = np.asarray(data)

                                if data_array.dtype == np.object_:
                                    pickled_data = pickle.dumps(data)
                                    target_group.create_dataset(
                                        dataset_name,
                                        data=np.void(pickled_data),
                                    )
                                elif data_array.ndim == 0:
                                    target_group.create_dataset(
                                        dataset_name, data=data
                                    )
                                else:
                                    target_group.create_dataset(
                                        dataset_name, data=data, **kwargs
                                    )

                        # Force flush to disk
                        h5_file.flush()

                    # Atomic move: replace original file
                    shutil.move(temp_file, spath)
                    temp_file = None  # Prevent cleanup

                    return  # Success

                except Exception as e:
                    if temp_file and os.path.exists(temp_file):
                        try:
                            os.unlink(temp_file)
                        except:
                            pass
                    raise e

        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = (2**attempt) + random.uniform(
                    0, 1
                )  # Exponential backoff
                print(
                    f"HDF5 save attempt {attempt + 1} failed: {e}. Retrying in {wait_time:.1f}s..."
                )
                time.sleep(wait_time)
            else:
                raise e

# EOF
