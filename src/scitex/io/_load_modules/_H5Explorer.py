#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-05 12:46:09 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/io/_H5Explorer.py
# ----------------------------------------
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import random
import time
import warnings

# Time-stamp: "2025-06-13 21:00:00 (ywatanabe)"

"""HDF5 file explorer for interactive data inspection."""

from typing import Any, Dict, List, Optional

import h5py
import numpy as np


class H5Explorer:
    """Interactive HDF5 file explorer.

    This class provides convenient methods to explore HDF5 files,
    inspect their structure, and load data.

    Example:
        >>> explorer = H5Explorer('data.h5')
        >>> explorer.explore()  # Display file structure
        >>> data = explorer.load('group1/dataset1')  # Load specific dataset
        >>> explorer.close()
    """

    def __init__(self, filepath: str, mode: str = "r"):
        """Initialize H5Explorer.

        Args:
            filepath: Path to HDF5 file
            mode: File opening mode ('r' for read, 'r+' for read/write)
        """
        self.filepath = filepath
        self.mode = mode
        self.file = h5py.File(filepath, mode)

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    def close(self):
        """Close the HDF5 file."""
        if hasattr(self, "file") and self.file:
            self.file.close()

    def explore(
        self, path: str = "/", max_depth: Optional[int] = None
    ) -> None:
        """Explore HDF5 file structure interactively."""
        self.show(path, max_depth)

    def show(
        self,
        path: str = "/",
        max_depth: Optional[int] = None,
        indent: str = "",
        _current_depth: int = 0,
    ) -> None:
        """Display HDF5 file structure.

        Args:
            path: Starting path in HDF5 file
            max_depth: Maximum depth to explore (None for unlimited)
            indent: Indentation string (used internally)
            _current_depth: Current depth (used internally)
        """
        if max_depth is not None and _current_depth > max_depth:
            return

        item = self.file[path] if path != "/" else self.file

        if isinstance(item, h5py.Group):
            if path != "/":
                print(f"{indent}[{path.split('/')[-1]}]")
            for key in sorted(item.keys()):
                subpath = f"{path}/{key}".replace("//", "/")
                self.show(
                    subpath, max_depth, indent + "  ", _current_depth + 1
                )
        elif isinstance(item, h5py.Dataset):
            name = path.split("/")[-1]
            shape = item.shape
            dtype = item.dtype
            size = item.size
            print(f"{indent}{name}: shape={shape}, dtype={dtype}, size={size}")

    def keys(self, path: str = "/") -> List[str]:
        """Get keys at specified path.

        Args:
            path: Path in HDF5 file

        Returns:
            List of keys at the specified path
        """
        item = self.file[path] if path != "/" else self.file
        if isinstance(item, h5py.Group):
            return list(item.keys())
        return []

    def load(self, path: str) -> Any:
        """Load data from specified path.

        Args:
            path: Path to dataset or group in HDF5 file

        Returns:
            Data from the specified path
        """
        item = self.file[path]

        if isinstance(item, h5py.Dataset):
            data = item[()]
            # Decode bytes to string if needed
            if isinstance(data, bytes):
                return data.decode("utf-8")
            # Handle pickled objects (stored as np.void)
            elif isinstance(data, np.void):
                import pickle

                return pickle.loads(data.tobytes())
            return data
        elif isinstance(item, h5py.Group):
            # Load group as dictionary
            result = {}
            for key in item.keys():
                result[key] = self.load(f"{path}/{key}".replace("//", "/"))
            # Also load attributes
            for key in item.attrs.keys():
                result[f"_attr_{key}"] = item.attrs[key]
            return result
        else:
            return item

    def get(self, path: str) -> Any:
        """Alias for load() method for compatibility.

        Args:
            path: Path to dataset or group in HDF5 file

        Returns:
            Data from the specified path
        """
        return self.load(path)

    def get_info(self, path: str = "/") -> Dict[str, Any]:
        """Get information about an item.

        Args:
            path: Path to item in HDF5 file

        Returns:
            Dictionary with item information
        """
        item = self.file[path] if path != "/" else self.file

        info = {
            "path": path,
            "type": type(item).__name__,
        }

        if isinstance(item, h5py.Dataset):
            info.update(
                {
                    "shape": item.shape,
                    "dtype": str(item.dtype),
                    "size": item.size,
                    "compression": item.compression,
                    "chunks": item.chunks,
                }
            )
        elif isinstance(item, h5py.Group):
            info["n_items"] = len(item.keys())
            info["keys"] = list(item.keys())

        # Add attributes
        if hasattr(item, "attrs") and len(item.attrs) > 0:
            info["attributes"] = dict(item.attrs)

        return info

    def find(self, pattern: str, path: str = "/") -> List[str]:
        """Find items matching pattern.

        Args:
            pattern: Pattern to search for in item names
            path: Starting path for search

        Returns:
            List of paths matching the pattern
        """
        matches = []

        def _search(current_path):
            item = (
                self.file[current_path] if current_path != "/" else self.file
            )

            if isinstance(item, h5py.Group):
                for key in item.keys():
                    subpath = f"{current_path}/{key}".replace("//", "/")
                    if pattern.lower() in key.lower():
                        matches.append(subpath)
                    _search(subpath)
            elif pattern.lower() in current_path.split("/")[-1].lower():
                matches.append(current_path)

        _search(path)
        return matches

    def get_shape(self, path: str) -> Optional[tuple]:
        """Get shape of a dataset.

        Args:
            path: Path to dataset

        Returns:
            Shape tuple or None if not a dataset
        """
        item = self.file[path]
        if isinstance(item, h5py.Dataset):
            return item.shape
        return None

    def get_dtype(self, path: str) -> Optional[np.dtype]:
        """Get dtype of a dataset.

        Args:
            path: Path to dataset

        Returns:
            Numpy dtype or None if not a dataset
        """
        item = self.file[path]
        if isinstance(item, h5py.Dataset):
            return item.dtype
        return None


# Convenience function


def explore_h5(filepath: str) -> None:
    """Explore HDF5 file structure.

    Args:
        filepath: Path to HDF5 file
    """
    if os.path.exists(filepath):
        explorer = H5Explorer(filepath)
        explorer.explore()
        explorer.close()
    else:
        warnings.warn(f"Warning: File does not exist: {filepath}")


def has_h5_key(h5_path, key, max_retries=3, action_on_corrupted="delete"):
    """
    Robust version of has_h5_key that handles corrupted files and lock conflicts.
    """
    h5_path = os.path.realpath(h5_path)

    if not os.path.exists(h5_path):
        return False

    for attempt in range(max_retries):
        try:
            with h5py.File(h5_path, "r") as h5_file:
                parts = [p for p in key.split("/") if p]
                current = h5_file

                for part in parts:
                    if part in current:
                        current = current[part]
                    else:
                        return False
                return True

        except (KeyError, FileNotFoundError):
            return False

        except (OSError, RuntimeError, ValueError) as e:
            error_msg = str(e).lower()

            lock_indicators = [
                "resource temporarily unavailable",
                "file is already open",
                "unable to lock file",
                "file locking failed",
            ]

            corruption_indicators = [
                "unable to synchronously",
                "bad symbol table",
                "free block size is zero",
                "truncated file",
                "unable to read signature",
                "corrupted",
                "invalid file signature",
                "unable to check link existence",
                "bad heap free list",
            ]

            if any(indicator in error_msg for indicator in lock_indicators):
                if attempt < max_retries - 1:
                    base_wait = 0.1 * (2**attempt)
                    jitter = random.uniform(0, base_wait * 0.5)
                    wait_time = base_wait + jitter
                    time.sleep(wait_time)
                    continue
                else:
                    return False

            elif any(
                indicator in error_msg for indicator in corruption_indicators
            ):
                if action_on_corrupted == "delete":
                    if _delete_corrupted_entry(h5_path, key):
                        return False
                return False
            else:
                raise e

    return False


def _delete_corrupted_entry(h5_path, key):
    """Delete corrupted entry from HDF5 file."""
    try:
        with h5py.File(h5_path, "r+") as h5_file:
            if key in h5_file:
                del h5_file[key]
                print(f"Deleted corrupted entry: {key}")
                return True
    except:
        pass
    return False

# EOF
