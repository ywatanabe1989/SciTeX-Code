#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-03 04:30:00 (ywatanabe)"
# File: feature_selection.py

"""
Feature selection utilities for classification tasks.

This module provides comprehensive feature selection and importance analysis:
- Feature importance extraction from various model types
- Univariate feature selection (ANOVA F-test, chi2, mutual_info)
- Model-based feature selection (tree importances, L1 coefficients)
- Recursive feature elimination (RFE)
- Cross-fold feature consistency analysis
- Feature importance aggregation and visualization
"""

from __future__ import annotations

import warnings
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from sklearn.feature_selection import (
    SelectKBest,
    chi2,
    f_classif,
    mutual_info_classif,
)
from sklearn.impute import SimpleImputer


def extract_feature_importance(
    model,
    feature_names: List[str],
    method: str = "auto",
) -> Optional[Dict[str, float]]:
    """Extract feature importance from trained model.

    Args:
        model: Trained classifier
        feature_names: List of feature names
        method: Method to extract importance:
            - "auto": Automatically detect best method
            - "tree": Use feature_importances_ (tree-based models)
            - "coef": Use coefficients (linear models)
            - "permutation": Use permutation importance (any model)

    Returns:
        Dictionary mapping feature names to importance values,
        or None if extraction fails
    """
    try:
        # Auto-detect method
        if method == "auto":
            if hasattr(model, "feature_importances_"):
                method = "tree"
            elif hasattr(model, "coef_"):
                method = "coef"
            else:
                warnings.warn(
                    f"Model {type(model).__name__} does not support "
                    f"feature importance extraction"
                )
                return None

        # Extract importance
        if method == "tree":
            if not hasattr(model, "feature_importances_"):
                raise ValueError(
                    f"Model {type(model).__name__} does not have "
                    f"feature_importances_ attribute"
                )
            importances = model.feature_importances_

        elif method == "coef":
            if not hasattr(model, "coef_"):
                raise ValueError(
                    f"Model {type(model).__name__} does not have "
                    f"coef_ attribute"
                )
            # Use absolute values for multi-class or single coefficient vector
            coef = model.coef_
            if coef.ndim > 1:
                # Multi-class: average absolute coefficients across classes
                importances = np.mean(np.abs(coef), axis=0)
            else:
                importances = np.abs(coef)

        elif method == "permutation":
            raise NotImplementedError(
                "Permutation importance requires validation data. "
                "Use extract_permutation_importance() instead."
            )

        else:
            raise ValueError(f"Unknown method: {method}")

        # Normalize to sum to 1
        importances = importances / importances.sum()

        # Create dictionary sorted by importance
        importance_dict = dict(zip(feature_names, importances))
        importance_dict = dict(
            sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)
        )

        return importance_dict

    except Exception as e:
        warnings.warn(f"Failed to extract feature importance: {e}")
        return None


def select_features_univariate(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_val: np.ndarray,
    feature_names: List[str],
    k: int = 10,
    score_func: str = "f_classif",
    impute_strategy: str = "median",
) -> Tuple[np.ndarray, np.ndarray, List[int], List[str], object]:
    """Select top k features using univariate statistical tests.

    This prevents data leakage by:
    1. Fitting the selector only on training data
    2. Transforming validation/test data with the fitted selector

    Args:
        X_train: Training features
        y_train: Training labels
        X_val: Validation features
        feature_names: List of feature names
        k: Number of features to select
        score_func: Scoring function:
            - "f_classif": ANOVA F-test (default)
            - "chi2": Chi-squared test (requires non-negative features)
            - "mutual_info": Mutual information
        impute_strategy: Strategy for imputing missing values:
            - "median" (default), "mean", "most_frequent", "constant"

    Returns:
        X_train_selected: Selected training features
        X_val_selected: Selected validation features
        feature_indices: Indices of selected features
        selected_names: Names of selected features
        imputer: Fitted imputer for test data
    """
    # Map string to function
    score_func_map = {
        "f_classif": f_classif,
        "chi2": chi2,
        "mutual_info": mutual_info_classif,
    }

    if score_func not in score_func_map:
        raise ValueError(
            f"Unknown score_func: {score_func}. "
            f"Choose from {list(score_func_map.keys())}"
        )

    score_func_callable = score_func_map[score_func]

    # Impute NaN values
    imputer = SimpleImputer(strategy=impute_strategy)
    X_train_imputed = imputer.fit_transform(X_train)
    X_val_imputed = imputer.transform(X_val)

    # Select features
    k_actual = min(k, X_train.shape[1])
    selector = SelectKBest(score_func_callable, k=k_actual)
    X_train_selected = selector.fit_transform(X_train_imputed, y_train)
    X_val_selected = selector.transform(X_val_imputed)

    # Get selected feature information
    feature_indices = selector.get_support(indices=True).tolist()
    selected_names = [feature_names[i] for i in feature_indices]

    return (
        X_train_selected,
        X_val_selected,
        feature_indices,
        selected_names,
        imputer,
    )


def analyze_feature_consistency(
    selected_features_per_fold: List[List[str]],
) -> Dict[str, Union[int, float, Dict[str, int]]]:
    """Analyze feature selection consistency across CV folds.

    Args:
        selected_features_per_fold: List of feature lists, one per fold

    Returns:
        Dictionary containing:
        - "feature_frequency": Dict mapping features to selection count
        - "n_folds": Total number of folds
        - "n_unique_features": Number of unique features selected
        - "consistency_score": Average selection frequency (0-1)
        - "stable_features": Features selected in all folds
        - "unstable_features": Features selected in only one fold
    """
    if not selected_features_per_fold:
        return {}

    n_folds = len(selected_features_per_fold)

    # Count feature occurrences
    all_features = set()
    for features in selected_features_per_fold:
        all_features.update(features)

    feature_frequency = {f: 0 for f in all_features}
    for features in selected_features_per_fold:
        for f in features:
            feature_frequency[f] += 1

    # Sort by frequency
    feature_frequency = dict(
        sorted(feature_frequency.items(), key=lambda x: x[1], reverse=True)
    )

    # Identify stable and unstable features
    stable_features = [
        f for f, count in feature_frequency.items() if count == n_folds
    ]
    unstable_features = [
        f for f, count in feature_frequency.items() if count == 1
    ]

    # Calculate consistency score (average selection frequency)
    consistency_score = (
        np.mean(list(feature_frequency.values())) / n_folds
        if feature_frequency
        else 0.0
    )

    return {
        "feature_frequency": feature_frequency,
        "n_folds": n_folds,
        "n_unique_features": len(all_features),
        "consistency_score": round(consistency_score, 3),
        "stable_features": stable_features,
        "unstable_features": unstable_features,
    }


def aggregate_feature_importances(
    importances_per_fold: List[Dict[str, float]],
    method: str = "mean",
) -> Dict[str, Dict[str, float]]:
    """Aggregate feature importances across CV folds.

    Args:
        importances_per_fold: List of importance dicts, one per fold
        method: Aggregation method:
            - "mean": Average importance across folds
            - "median": Median importance across folds
            - "max": Maximum importance across folds

    Returns:
        Dictionary containing:
        - "mean": Mean importance per feature
        - "std": Standard deviation per feature
        - "min": Minimum importance per feature
        - "max": Maximum importance per feature
        - "cv": Coefficient of variation (std/mean) per feature
    """
    if not importances_per_fold:
        return {}

    # Collect all features
    all_features = set()
    for imp_dict in importances_per_fold:
        all_features.update(imp_dict.keys())

    # Build matrix: (n_folds, n_features)
    importance_matrix = np.zeros((len(importances_per_fold), len(all_features)))
    feature_list = sorted(list(all_features))

    for fold_idx, imp_dict in enumerate(importances_per_fold):
        for feat_idx, feat in enumerate(feature_list):
            importance_matrix[fold_idx, feat_idx] = imp_dict.get(feat, 0.0)

    # Calculate statistics
    mean_importance = importance_matrix.mean(axis=0)
    std_importance = importance_matrix.std(axis=0)
    min_importance = importance_matrix.min(axis=0)
    max_importance = importance_matrix.max(axis=0)

    # Coefficient of variation (handle division by zero)
    with np.errstate(divide="ignore", invalid="ignore"):
        cv_importance = std_importance / mean_importance
        cv_importance[~np.isfinite(cv_importance)] = 0.0

    # Create result dictionary
    result = {
        "mean": dict(zip(feature_list, mean_importance)),
        "std": dict(zip(feature_list, std_importance)),
        "min": dict(zip(feature_list, min_importance)),
        "max": dict(zip(feature_list, max_importance)),
        "cv": dict(zip(feature_list, cv_importance)),
    }

    # Sort each by mean importance
    for key in result:
        result[key] = dict(
            sorted(
                result[key].items(),
                key=lambda x: result["mean"][x[0]],
                reverse=True,
            )
        )

    return result


def create_feature_importance_dataframe(
    aggregated_importances: Dict[str, Dict[str, float]],
) -> pd.DataFrame:
    """Create a formatted DataFrame from aggregated feature importances.

    Args:
        aggregated_importances: Output from aggregate_feature_importances()

    Returns:
        DataFrame with columns: feature, mean, std, min, max, cv
        Sorted by mean importance (descending)
    """
    if not aggregated_importances or "mean" not in aggregated_importances:
        return pd.DataFrame()

    features = list(aggregated_importances["mean"].keys())

    df = pd.DataFrame(
        {
            "feature": features,
            "mean": [aggregated_importances["mean"][f] for f in features],
            "std": [aggregated_importances["std"][f] for f in features],
            "min": [aggregated_importances["min"][f] for f in features],
            "max": [aggregated_importances["max"][f] for f in features],
            "cv": [aggregated_importances["cv"][f] for f in features],
        }
    )

    # Sort by mean importance
    df = df.sort_values("mean", ascending=False).reset_index(drop=True)

    return df


__all__ = [
    "extract_feature_importance",
    "select_features_univariate",
    "analyze_feature_consistency",
    "aggregate_feature_importances",
    "create_feature_importance_dataframe",
]

# EOF
