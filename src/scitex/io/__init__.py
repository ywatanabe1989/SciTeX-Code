#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-12 04:23:59 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/io/__init__.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/io/__init__.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
"""Scitex IO module with lazy imports to avoid circular dependencies."""

# Import commonly used functions directly
from ._save import save
from ._load import load
from ._load_configs import load_configs
from ._glob import glob, parse_glob
from ._reload import reload
from ._flush import flush
from ._cache import cache
from ._load_modules._H5Explorer import H5Explorer, explore_h5, has_h5_key
from ._load_modules._ZarrExplorer import ZarrExplorer, explore_zarr, has_zarr_key

# Import load cache control functions
from ._load_cache import (
    get_cache_info,
    configure_cache,
    clear_cache as clear_load_cache
)

# Import save module functions
try:
    from ._save_modules import (
        save_image,
        save_text,
        save_mp4,
        save_listed_dfs_as_csv,
        save_listed_scalars_as_csv,
        save_optuna_study_as_csv_and_pngs,
    )
except ImportError as e:
    # Fallback for missing functions
    save_image = None
    save_text = None
    save_mp4 = None
    save_listed_dfs_as_csv = None
    save_listed_scalars_as_csv = None
    save_optuna_study_as_csv_and_pngs = None

# Optional imports that might fail
try:
    from ._path import path
except ImportError:
    path = None

try:
    from ._mv_to_tmp import mv_to_tmp
except ImportError:
    mv_to_tmp = None

try:
    from ._json2md import json2md
except ImportError:
    json2md = None

# Import utils
try:
    from .utils import migrate_h5_to_zarr, migrate_h5_to_zarr_batch
except ImportError:
    migrate_h5_to_zarr = None
    migrate_h5_to_zarr_batch = None

__all__ = [
    "save",
    "load",
    "load_configs",
    "glob",
    "parse_glob",
    "reload",
    "flush",
    "cache",
    "H5Explorer",
    "explore_h5",
    "has_h5_key",
    "path",
    "mv_to_tmp",
    "json2md",
    "save_image",
    "save_text",
    "save_mp4",
    "save_listed_dfs_as_csv",
    "save_listed_scalars_as_csv",
    "save_optuna_study_as_csv_and_pngs",
    "ZarrExplorer",
    "explore_zarr",
    "has_zarr_key",
    "migrate_h5_to_zarr",
    "migrate_h5_to_zarr_batch",
    # Load cache control functions
    "get_cache_info",
    "configure_cache",
    "clear_load_cache",
]

# EOF
