#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-11 15:45:49 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/io/_ZarrExplorer.py
# ----------------------------------------
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from typing import Any, List, Optional

import zarr
from ._zarr import _load_zarr_dataset


class ZarrExplorer:
    """Interactive Zarr store explorer."""

    def __init__(self, storepath: str, mode: str = "r"):
        self.storepath = storepath
        self.mode = mode
        self.store = zarr.open(storepath, mode=mode)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass  # Zarr doesn't need explicit closing

    def explore(self, path: str = "/", max_depth: Optional[int] = None):
        """Explore Zarr store structure."""
        self.show(path, max_depth)

    def show(
        self,
        path: str = "/",
        max_depth: Optional[int] = None,
        indent: str = "",
        _current_depth: int = 0,
    ):
        """Display Zarr store structure."""
        if max_depth is not None and _current_depth > max_depth:
            return

        if path == "/":
            target = self.store
        else:
            target = self.store[path.lstrip("/")]

        if hasattr(target, "keys"):  # Group
            if path != "/":
                print(f"{indent}[{path.split('/')[-1]}]")

            for key in sorted(target.keys()):
                subpath = f"{path}/{key}".replace("//", "/")
                self.show(
                    subpath, max_depth, indent + "  ", _current_depth + 1
                )

        else:  # Array
            name = path.split("/")[-1]
            shape = target.shape
            dtype = target.dtype
            size = target.size
            compressor = getattr(target, "compressor", None)
            compressed_size = getattr(target, "nbytes_stored", "unknown")

            print(
                f"{indent}{name}: shape={shape}, dtype={dtype}, "
                f"size={size}, compressor={compressor}, "
                f"compressed_size={compressed_size}"
            )

    def keys(self, path: str = "/") -> List[str]:
        """Get keys at specified path."""
        if path == "/":
            target = self.store
        else:
            target = self.store[path.lstrip("/")]

        if hasattr(target, "keys"):
            return list(target.keys())
        return []

    def load(self, path: str) -> Any:
        """Load data from specified path."""
        return _load_zarr_dataset(self.store[path.lstrip("/")])

    def has_key(self, path: str) -> bool:
        """Check if key exists (no locking issues!)."""
        try:
            _ = self.store[path.lstrip("/")]
            return True
        except KeyError:
            return False


def explore_zarr(storepath: str) -> None:
    """Explore Zarr store structure."""
    explorer = ZarrExplorer(storepath)
    explorer.explore()


def has_zarr_key(zarr_path: str, key: str) -> bool:
    """Check if key exists in Zarr store (no locking issues!)."""
    try:
        store = zarr.open(zarr_path, mode="r")
        _ = store[key.lstrip("/")]
        return True
    except (KeyError, ValueError):
        return False

# EOF
