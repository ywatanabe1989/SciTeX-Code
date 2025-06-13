#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-12-12 06:50:19 (ywatanabe)"
# File: ./scitex_repo/src/scitex/io/_load_modules/_catboost.py

from typing import Union

try:
    from catboost import CatBoostClassifier, CatBoostRegressor
    CATBOOST_AVAILABLE = True
except ImportError:
    CATBOOST_AVAILABLE = False
    # Create placeholder classes for testing
    class CatBoostClassifier:
        pass
    class CatBoostRegressor:
        pass


def _load_catboost(
    lpath: str, **kwargs
) -> Union["CatBoostClassifier", "CatBoostRegressor"]:
    """
    Loads a CatBoost model from a file.

    Parameters
    ----------
    lpath : str
        Path to the CatBoost model file (.cbm extension)
    **kwargs : dict
        Additional keyword arguments passed to load_model method

    Returns
    -------
    Union[CatBoostClassifier, CatBoostRegressor]
        Loaded CatBoost model object

    Raises
    ------
    ValueError
        If file extension is not .cbm
    FileNotFoundError
        If model file does not exist
    ImportError
        If CatBoost is not installed

    Examples
    --------
    >>> model = _load_catboost('model.cbm')
    >>> predictions = model.predict(X_test)
    """
    if not CATBOOST_AVAILABLE:
        raise ImportError("CatBoost is not installed. Please install with: pip install catboost")
    
    if not (lpath.endswith(".cbm") or lpath.endswith(".CBM")):
        raise ValueError("File must have .cbm extension")

    try:
        model = CatBoostClassifier().load_model(lpath, **kwargs)
    except:
        model = CatBoostRegressor().load_model(lpath, **kwargs)

    return model


# EOF
