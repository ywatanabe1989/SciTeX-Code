#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-16 12:21:07 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/io/_save_modules/_pickle.py

import pickle
import gzip


def _save_pickle(obj, spath):
    """
    Save an object using Python's pickle serialization.
    
    Parameters
    ----------
    obj : Any
        Object to serialize.
    spath : str
        Path where the pickle file will be saved.
        
    Returns
    -------
    None
    """
    with open(spath, "wb") as s:
        pickle.dump(obj, s)


def _save_pickle_gz(obj, spath):
    """
    Save an object using Python's pickle serialization with gzip compression.
    
    Parameters
    ----------
    obj : Any
        Object to serialize.
    spath : str
        Path where the compressed pickle file will be saved.
        
    Returns
    -------
    None
    """
    with gzip.open(spath, "wb") as f:
        pickle.dump(obj, f)
