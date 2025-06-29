#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-24 20:04:02 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/io/_H5Explorer.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/io/_H5Explorer.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import shutil
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


def has_h5_key(h5_path, key, max_retries=3):
    """
    Robust version of has_h5_key that handles corrupted files.

    Parameters:
    -----------
    h5_path : str
        Path to HDF5 file
    key : str
        Key to check for existence
    max_retries : int
        Maximum number of attempts to read the file

    Returns:
    --------
    bool
        True if key exists, False if key doesn't exist or file is corrupted
    """
    h5_path = os.path.realpath(h5_path)

    if not os.path.exists(h5_path):
        return False

    for attempt in range(max_retries):
        try:
            with h5py.File(h5_path, "r") as h5_file:
                parts = [p for p in key.split("/") if p]  # Remove empty parts
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
            corruption_indicators = [
                "unable to synchronously",
                "bad symbol table",
                "free block size is zero",
                "truncated file",
                "unable to read signature",
                "corrupted",
                "invalid file signature",
                "unable to check link existence",
            ]

            if any(
                indicator in error_msg for indicator in corruption_indicators
            ):
                print(
                    f"HDF5 file corruption detected on attempt {attempt + 1}: {e}"
                )

                if attempt < max_retries - 1:
                    # Try to repair or recreate the file
                    if _attempt_h5_repair(h5_path):
                        print(f"File repair attempted, retrying...")
                        continue
                    else:
                        print(f"File repair failed, treating as missing key")
                        return False
                else:
                    # Final attempt failed, treat as file doesn't contain the key
                    print(f"Final attempt failed, treating key as missing")
                    return False
            else:
                # Non-corruption error, re-raise
                raise e

    return False


def _attempt_h5_repair(h5_path):
    """
    Attempt to repair corrupted HDF5 file by creating backup and rebuilding.

    Parameters:
    -----------
    h5_path : str
        Path to corrupted HDF5 file

    Returns:
    --------
    bool
        True if repair was attempted, False if repair failed
    """
    try:
        backup_path = h5_path + ".corrupted_backup"

        # Create backup of corrupted file
        if os.path.exists(h5_path):
            shutil.copy2(h5_path, backup_path)
            print(f"Created backup: {backup_path}")

        # Try to read any salvageable data
        salvaged_data = {}
        try:
            with h5py.File(h5_path, "r") as f:
                _recursively_salvage_data(f, salvaged_data, "")
        except:
            print("Could not salvage any data from corrupted file")

        # Remove corrupted file
        if os.path.exists(h5_path):
            os.remove(h5_path)

        # Recreate file with salvaged data if any
        if salvaged_data:
            with h5py.File(h5_path, "w") as f:
                _restore_salvaged_data(f, salvaged_data)
            print(
                f"Recreated file with {len(salvaged_data)} salvaged datasets"
            )
            return True
        else:
            print("No data could be salvaged, file will be recreated empty")
            # Create empty file
            with h5py.File(h5_path, "w") as f:
                pass
            return True

    except Exception as e:
        print(f"File repair failed: {e}")
        return False


def _recursively_salvage_data(h5_group, salvaged_data, path_prefix):
    """Recursively try to salvage data from corrupted HDF5 group."""
    try:
        for key in h5_group.keys():
            current_path = f"{path_prefix}/{key}".strip("/")
            try:
                item = h5_group[key]
                if isinstance(item, h5py.Dataset):
                    salvaged_data[current_path] = item[()]
                elif isinstance(item, h5py.Group):
                    _recursively_salvage_data(
                        item, salvaged_data, current_path
                    )
            except:
                print(f"Could not salvage: {current_path}")
                continue
    except:
        pass


def _restore_salvaged_data(h5_file, salvaged_data):
    """Restore salvaged data to new HDF5 file."""
    for path, data in salvaged_data.items():
        try:
            # Create groups as needed
            parts = path.split("/")
            current_group = h5_file

            for part in parts[:-1]:
                if part not in current_group:
                    current_group = current_group.create_group(part)
                else:
                    current_group = current_group[part]

            # Create dataset
            dataset_name = parts[-1]
            current_group.create_dataset(dataset_name, data=data)
        except Exception as e:
            print(f"Could not restore {path}: {e}")

# EOF
