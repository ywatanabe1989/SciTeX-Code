#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-14 07:41:33 (ywatanabe)"
# File: ./scitex_repo/src/scitex/io/_load_modules/_pickle.py

import pickle
import gzip


def _load_pickle(lpath, **kwargs):
    """Load pickle file (compressed or uncompressed)."""
    if lpath.endswith(".pkl.gz"):
        # Handle gzip compressed pickle
        with gzip.open(lpath, "rb") as f:
            return pickle.load(f, **kwargs)
    elif lpath.endswith(".pkl") or lpath.endswith(".pickle"):
        # Handle regular pickle
        with open(lpath, "rb") as f:
            return pickle.load(f, **kwargs)
    else:
        raise ValueError("File must have .pkl, .pickle, or .pkl.gz extension")


# EOF
