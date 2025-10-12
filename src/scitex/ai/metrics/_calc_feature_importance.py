#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-03 04:00:00 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/ml/metrics/_calc_feature_importance.py

"""
Calculate feature importance from trained models.

This module provides a unified interface for extracting feature importance
from various model types (tree-based, linear models, etc.).
"""

from typing import Dict, List, Optional, Tuple
import numpy as np


def calc_feature_importance(
    model,
    feature_names: Optional[List[str]] = None,
    top_n: Optional[int] = None,
) -> Tuple[Dict[str, float], np.ndarray]:
    """
    Calculate feature importance from a trained model.

    Parameters
    ----------
    model : object
        Trained model with feature importance attributes
        Supports:
        - Tree-based: feature_importances_ (RandomForest, XGBoost, etc.)
        - Linear: coef_ (LogisticRegression, LinearSVC, etc.)
    feature_names : List[str], optional
        Names of features. If None, uses feature_0, feature_1, ...
    top_n : int, optional
        Return only top N most important features

    Returns
    -------
    importance_dict : Dict[str, float]
        Dictionary mapping feature names to importance scores
    importance_array : np.ndarray
        Array of importance scores (same order as feature_names)

    Raises
    ------
    ValueError
        If model doesn't support feature importance extraction

    Examples
    --------
    >>> from sklearn.ensemble import RandomForestClassifier
    >>> import numpy as np
    >>> X = np.random.rand(100, 5)
    >>> y = np.random.randint(0, 2, 100)
    >>> model = RandomForestClassifier().fit(X, y)
    >>> importance_dict, importance_array = calc_feature_importance(
    ...     model, feature_names=['f1', 'f2', 'f3', 'f4', 'f5']
    ... )
    """
    # Extract importance scores based on model type
    if hasattr(model, "feature_importances_"):
        # Tree-based models (RandomForest, XGBoost, etc.)
        importances = model.feature_importances_
    elif hasattr(model, "coef_"):
        # Linear models (LogisticRegression, LinearSVC, etc.)
        coef = model.coef_
        if coef.ndim == 2:
            # For multiclass, use mean absolute coefficient
            importances = np.abs(coef).mean(axis=0)
        else:
            importances = np.abs(coef)
    else:
        raise ValueError(
            f"Model {type(model).__name__} does not support feature importance extraction. "
            f"Model must have either 'feature_importances_' or 'coef_' attribute."
        )

    # Generate feature names if not provided
    if feature_names is None:
        n_features = len(importances)
        feature_names = [f"feature_{i}" for i in range(n_features)]

    # Validate feature names match importance array length
    if len(feature_names) != len(importances):
        raise ValueError(
            f"Number of feature names ({len(feature_names)}) "
            f"does not match number of importances ({len(importances)})"
        )

    # Create dictionary
    importance_dict = {
        name: float(imp) for name, imp in zip(feature_names, importances)
    }

    # Sort by importance
    sorted_items = sorted(
        importance_dict.items(), key=lambda x: x[1], reverse=True
    )

    # Apply top_n filter if requested
    if top_n is not None:
        sorted_items = sorted_items[:top_n]

    # Return sorted dictionary and original array
    return dict(sorted_items), importances


def calc_permutation_importance(
    model,
    X: np.ndarray,
    y: np.ndarray,
    feature_names: Optional[List[str]] = None,
    n_repeats: int = 10,
    random_state: Optional[int] = None,
    scoring: Optional[str] = None,
) -> Tuple[Dict[str, float], Dict[str, float]]:
    """
    Calculate permutation feature importance.

    More reliable than built-in importance for some models, but slower.

    Parameters
    ----------
    model : object
        Trained model
    X : np.ndarray
        Feature matrix
    y : np.ndarray
        Target vector
    feature_names : List[str], optional
        Names of features
    n_repeats : int, default 10
        Number of times to permute each feature
    random_state : int, optional
        Random seed for reproducibility
    scoring : str, optional
        Scoring metric (default uses model's score method)

    Returns
    -------
    importance_mean : Dict[str, float]
        Mean importance for each feature
    importance_std : Dict[str, float]
        Standard deviation of importance for each feature
    """
    from sklearn.inspection import permutation_importance

    # Calculate permutation importance
    result = permutation_importance(
        model,
        X,
        y,
        n_repeats=n_repeats,
        random_state=random_state,
        scoring=scoring,
    )

    # Generate feature names if not provided
    if feature_names is None:
        n_features = X.shape[1]
        feature_names = [f"feature_{i}" for i in range(n_features)]

    # Create dictionaries
    importance_mean = {
        name: float(imp)
        for name, imp in zip(feature_names, result.importances_mean)
    }
    importance_std = {
        name: float(imp)
        for name, imp in zip(feature_names, result.importances_std)
    }

    # Sort by mean importance
    sorted_names = sorted(
        importance_mean.keys(), key=lambda x: importance_mean[x], reverse=True
    )
    importance_mean = {name: importance_mean[name] for name in sorted_names}
    importance_std = {name: importance_std[name] for name in sorted_names}

    return importance_mean, importance_std


# EOF
