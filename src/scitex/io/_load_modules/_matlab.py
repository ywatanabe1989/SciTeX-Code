#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-04-10 08:07:03 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/io/_load_modules/_matlab.py
# ----------------------------------------
import os

__FILE__ = "/ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/io/_load_modules/_matlab.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from typing import Any


def _load_matlab(lpath: str, **kwargs) -> Any:
    """Load MATLAB file."""
    if not lpath.endswith(".mat"):
        raise ValueError("File must have .mat extension")

    # Try using scipy.io first for binary .mat files
    try:
        # For MATLAB v7.3 files (HDF5 format)
        from scipy.io import loadmat

        return loadmat(lpath, **kwargs)
    except Exception as e1:
        # If scipy fails, try pymatreader  or older MAT files
        try:
            from pymatreader import read_mat

            return read_mat(lpath, **kwargs)
        except Exception as e2:
            # Both methods failed
            raise ValueError(f"Error loading file {lpath}: {str(e1)}\nAnd: {str(e2)}")


# EOF
