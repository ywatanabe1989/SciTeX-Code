#!/usr/bin/env python3
"""Scitex IO module with lazy imports to avoid circular dependencies."""

# Import commonly used functions directly
from ._save import save
from ._load import load
from ._load_configs import load_configs
from ._glob import glob
from ._reload import reload
from ._flush import flush
from ._cache import cache
from ._H5Explorer import H5Explorer, explore_h5

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

__all__ = [
    "save",
    "load", 
    "load_configs",
    "glob",
    "reload",
    "flush",
    "cache",
    "H5Explorer",
    "explore_h5",
    "path",
    "mv_to_tmp",
    "json2md"
]