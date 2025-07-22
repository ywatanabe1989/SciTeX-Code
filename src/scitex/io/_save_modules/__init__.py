#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-12 13:05:00 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/.claude-worktree/scitex_repo/src/scitex/io/_save_modules/__init__.py
# ----------------------------------------
import os

__FILE__ = "./src/scitex/io/_save_modules/__init__.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Save modules for scitex.io.save functionality

This package contains format-specific save handlers for various file types.
Each module provides a save_<format> function that handles saving objects
to that specific format.
"""

# Import save functions from individual modules
from ._csv import _save_csv as save_csv
from ._excel import save_excel
from ._numpy import _save_npy as save_npy, _save_npz as save_npz
from ._pickle import _save_pickle as save_pickle, _save_pickle_gz as save_pickle_compressed
from ._joblib import _save_joblib as save_joblib
from ._torch import _save_torch as save_torch
from ._json import _save_json as save_json
from ._yaml import _save_yaml as save_yaml
from ._hdf5 import _save_hdf5 as save_hdf5
from ._matlab import _save_matlab as save_matlab
from ._catboost import _save_catboost as save_catboost
from ._text import _save_text as save_text
from ._html import save_html
from ._image import save_image
from ._mp4 import _mk_mp4 as save_mp4
from ._zarr import _save_zarr as save_zarr
from ._bibtex import save_bibtex

# Import additional save utilities
from ._listed_dfs_as_csv import _save_listed_dfs_as_csv as save_listed_dfs_as_csv
from ._listed_scalars_as_csv import _save_listed_scalars_as_csv as save_listed_scalars_as_csv
from ._optuna_study_as_csv_and_pngs import save_optuna_study_as_csv_and_pngs

# Define what gets imported with "from scitex.io._save_modules import *"
__all__ = [
    "save_csv",
    "save_excel",
    "save_npy",
    "save_npz",
    "save_pickle",
    "save_pickle_compressed",
    "save_joblib",
    "save_torch",
    "save_json",
    "save_yaml",
    "save_hdf5",
    "save_matlab",
    "save_catboost",
    "save_text",
    "save_html",
    "save_image",
    "save_mp4",
    "save_zarr",
    "save_bibtex",
    "save_listed_dfs_as_csv",
    "save_listed_scalars_as_csv",
    "save_optuna_study_as_csv_and_pngs",
]

# EOF
