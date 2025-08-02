#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-16 12:19:07 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/io/_save_modules/_numpy.py

import numpy as np


def _save_npy(obj, spath):
    """
    Save a numpy array to .npy format.
    
    Parameters
    ----------
    obj : numpy.ndarray
        The numpy array to save.
    spath : str
        Path where the .npy file will be saved.
        
    Returns
    -------
    None
    """
    np.save(spath, obj)


def _save_npz(obj, spath):
    """
    Save numpy arrays to .npz format.
    
    Parameters
    ----------
    obj : dict or list/tuple of numpy.ndarray
        Either a dictionary of arrays or a list/tuple of arrays.
    spath : str
        Path where the .npz file will be saved.
        
    Returns
    -------
    None
    
    Raises
    ------
    ValueError
        If obj is not a dict of arrays or a list/tuple of arrays.
    """
    if isinstance(obj, dict):
        np.savez_compressed(spath, **obj)
    elif isinstance(obj, (list, tuple)) and all(
        isinstance(x, np.ndarray) for x in obj
    ):
        obj = {str(ii): obj[ii] for ii in range(len(obj))}
        np.savez_compressed(spath, **obj)
    else:
        raise ValueError(
            "For .npz files, obj must be a dict of arrays or a list/tuple of arrays."
        )
