#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-11 05:54:51 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/io/_load.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import glob
from pathlib import Path
from typing import Any, Union

from ..decorators import preserve_doc
from ..str._clean_path import clean_path
from ._load_cache import (
    cache_data,
    configure_cache,
    get_cache_info,
    get_cached_data,
    load_npy_cached,
)
from ._load_modules._bibtex import _load_bibtex

# from ._load_modules._catboost import _load_catboost
from ._load_modules._con import _load_con
from ._load_modules._docx import _load_docx
from ._load_modules._eeg import _load_eeg_data
from ._load_modules._hdf5 import _load_hdf5
from ._load_modules._image import _load_image
from ._load_modules._joblib import _load_joblib
from ._load_modules._json import _load_json
from ._load_modules._markdown import _load_markdown
from ._load_modules._matlab import _load_matlab
from ._load_modules._numpy import _load_npy
from ._load_modules._pandas import _load_csv, _load_excel, _load_tsv
from ._load_modules._pdf import _load_pdf
from ._load_modules._pickle import _load_pickle
from ._load_modules._sqlite3 import _load_db_sqlite3
from ._load_modules._torch import _load_torch
from ._load_modules._txt import _load_txt
from ._load_modules._xml import _load_xml
from ._load_modules._yaml import _load_yaml
from ._load_modules._zarr import _load_zarr


def load(
    lpath: Union[str, Path],
    show: bool = False,
    verbose: bool = False,
    cache: bool = True,
    **kwargs,
) -> Any:
    """
    Load data from various file formats.

    This function supports loading data from multiple file formats with optional caching.

    Parameters
    ----------
    lpath : Union[str, Path]
        The path to the file to be loaded. Can be a string or pathlib.Path object.
    show : bool, optional
        If True, display additional information during loading. Default is False.
    verbose : bool, optional
        If True, print verbose output during loading. Default is False.
    cache : bool, optional
        If True, enable caching for faster repeated loads. Default is True.
    **kwargs : dict
        Additional keyword arguments to be passed to the specific loading function.

    Returns
    -------
    object
        The loaded data object, which can be of various types depending on the input file format.

    Raises
    ------
    ValueError
        If the file extension is not supported.
    FileNotFoundError
        If the specified file does not exist.

    Supported Extensions
    -------------------
    - Data formats: .csv, .tsv, .xls, .xlsx, .xlsm, .xlsb, .json, .yaml, .yml
    - Scientific: .npy, .npz, .mat, .hdf5, .con
    - ML/DL: .pth, .pt, .cbm, .joblib, .pkl
    - Documents: .txt, .log, .event, .md, .docx, .pdf, .xml
    - Images: .jpg, .png, .tiff, .tif
    - EEG data: .vhdr, .vmrk, .edf, .bdf, .gdf, .cnt, .egi, .eeg, .set
    - Database: .db

    Examples
    --------
    >>> data = load('data.csv')
    >>> image = load('image.png')
    >>> model = load('model.pth')
    """

    # Don't use clean_path as it breaks relative paths like ./file.txt
    # lpath = clean_path(lpath)

    # Convert Path objects to strings for consistency
    if isinstance(lpath, Path):
        lpath = str(lpath)
        if verbose:
            print(f"[DEBUG] After Path conversion: {lpath}")

    # Check if it's a glob pattern
    if "*" in lpath or "?" in lpath or "[" in lpath:
        # Handle glob pattern
        matched_files = sorted(glob.glob(lpath))
        if not matched_files:
            raise FileNotFoundError(
                f"No files found matching pattern: {lpath}"
            )
        # Load all matched files
        results = []
        for file_path in matched_files:
            results.append(
                load(file_path, show=show, verbose=verbose, **kwargs)
            )
        return results

    # Handle broken symlinks - os.path.exists() returns False for broken symlinks
    if not os.path.exists(lpath):
        if os.path.islink(lpath):
            # For symlinks, resolve the target path relative to symlink's directory
            symlink_dir = os.path.dirname(os.path.abspath(lpath))
            target = os.readlink(lpath)
            resolved_target = os.path.join(symlink_dir, target)
            resolved_target = os.path.abspath(resolved_target)
            
            if os.path.exists(resolved_target):
                lpath = resolved_target
            else:
                raise FileNotFoundError(f"Symlink target not found: {resolved_target}")
        else:
            # Try general path resolution
            try:
                resolved_path = os.path.realpath(lpath)
                if os.path.exists(resolved_path):
                    lpath = resolved_path
                else:
                    raise FileNotFoundError(f"File not found: {lpath}")
            except Exception:
                raise FileNotFoundError(f"File not found: {lpath}")

    # Try to get from cache first
    if cache:
        cached_data = get_cached_data(lpath)
        if cached_data is not None:
            if verbose:
                print(f"[Cache HIT] Loaded from cache: {lpath}")
            return cached_data

    loaders_dict = {
        # Default
        "": _load_txt,
        # Config/Settings
        "yaml": _load_yaml,
        "yml": _load_yaml,
        "json": _load_json,
        "xml": _load_xml,
        # Bibliography
        "bib": _load_bibtex,
        # ML/DL Models
        "pth": _load_torch,
        "pt": _load_torch,
        # "cbm": _load_catboost,
        "joblib": _load_joblib,
        "pkl": _load_pickle,
        "pickle": _load_pickle,
        "gz": _load_pickle,  # For .pkl.gz files
        # Tabular Data
        "csv": _load_csv,
        "tsv": _load_tsv,
        "xls": _load_excel,
        "xlsx": _load_excel,
        "xlsm": _load_excel,
        "xlsb": _load_excel,
        "db": _load_db_sqlite3,
        # Scientific Data
        "npy": _load_npy,
        "npz": _load_npy,
        "mat": _load_matlab,
        "hdf5": _load_hdf5,
        "h5": _load_hdf5,
        "zarr": _load_zarr,
        "con": _load_con,
        # Documents
        "txt": _load_txt,
        "tex": _load_txt,
        "log": _load_txt,
        "event": _load_txt,
        "py": _load_txt,
        "sh": _load_txt,
        "md": _load_markdown,
        "docx": _load_docx,
        "pdf": _load_pdf,
        # Images
        "jpg": _load_image,
        "png": _load_image,
        "tiff": _load_image,
        "tif": _load_image,
        # EEG Data
        "vhdr": _load_eeg_data,
        "vmrk": _load_eeg_data,
        "edf": _load_eeg_data,
        "bdf": _load_eeg_data,
        "gdf": _load_eeg_data,
        "cnt": _load_eeg_data,
        "egi": _load_eeg_data,
        "eeg": _load_eeg_data,
        "set": _load_eeg_data,
    }

    ext = lpath.split(".")[-1] if "." in lpath else ""

    # Special handling for numpy files with caching
    if cache and ext in ["npy", "npz"]:
        return load_npy_cached(lpath, **kwargs)

    loader = preserve_doc(loaders_dict.get(ext, _load_txt))

    try:
        result = loader(lpath, **kwargs)

        # Cache the result if caching is enabled
        if cache:
            cache_data(lpath, result)
            if verbose:
                print(f"[Cache STORED] Cached data for: {lpath}")

        return result
    except (ValueError, FileNotFoundError) as e:
        raise ValueError(f"Error loading file {lpath}: {str(e)}")

# EOF
