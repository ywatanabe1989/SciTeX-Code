#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-16 12:29:11 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/io/_save_modules/_catboost.py


def _save_catboost(obj, spath):
    """
    Save a CatBoost model.
    
    Parameters
    ----------
    obj : catboost.CatBoost
        The CatBoost model to save.
    spath : str
        Path where the CatBoost model file will be saved.
        
    Returns
    -------
    None
    """
    obj.save_model(spath)
