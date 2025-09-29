#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-16 12:22:56 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/io/_save_modules/_joblib.py

import joblib


def _save_joblib(obj, spath):
    """
    Save an object using joblib serialization.
    
    Parameters
    ----------
    obj : Any
        Object to serialize.
    spath : str
        Path where the joblib file will be saved.
        
    Returns
    -------
    None
    """
    with open(spath, "wb") as s:
        joblib.dump(obj, s, compress=3)
