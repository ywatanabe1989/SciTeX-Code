#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-16 12:28:15 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/io/_save_modules/_matlab.py

import scipy.io


def _save_matlab(obj, spath):
    """
    Save a Python dictionary to a MATLAB .mat file.
    
    Parameters
    ----------
    obj : dict
        Dictionary of arrays to save in MATLAB format.
    spath : str
        Path where the MATLAB file will be saved.
        
    Returns
    -------
    None
    """
    scipy.io.savemat(spath, obj)
