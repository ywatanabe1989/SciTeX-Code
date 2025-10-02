#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-02 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/ml/metrics/_calc_pre_rec_auc.py

"""Calculate Precision-Recall AUC."""

__FILE__ = __file__

from typing import Any, Dict, List, Optional
import numpy as np
from sklearn.metrics import average_precision_score, precision_recall_curve


def calc_pre_rec_auc(
    y_true: np.ndarray,
    y_proba: np.ndarray,
    labels: Optional[List] = None,
    fold: Optional[int] = None,
    return_curve: bool = False,
) -> Dict[str, Any]:
    """
    Calculate Precision-Recall AUC with robust handling.

    Parameters
    ----------
    y_true : np.ndarray
        True labels (can be str or int)
    y_proba : np.ndarray
        Predicted probabilities
    labels : List, optional
        Expected label list
    fold : int, optional
        Fold number for tracking
    return_curve : bool
        Whether to return PR curve data

    Returns
    -------
    Dict[str, Any]
        {'metric': 'pr_auc', 'value': float, 'fold': int}
    """
    try:
        # Normalize labels
        if labels is not None:
            unique_labels = np.unique(y_true)
            label_names = labels
            # If data contains integers, assume they map to label indices
            if isinstance(unique_labels[0], (int, np.integer)):
                y_true_norm = y_true.astype(int)
            else:
                # Data contains label names
                label_map = {label: idx for idx, label in enumerate(labels)}
                y_true_norm = np.array([label_map[y] for y in y_true])
        else:
            unique_labels = sorted(np.unique(y_true))
            label_names = unique_labels
            if isinstance(unique_labels[0], (int, np.integer)):
                y_true_norm = y_true.astype(int)
            else:
                label_map = {label: idx for idx, label in enumerate(unique_labels)}
                y_true_norm = np.array([label_map[y] for y in y_true])

        # Handle binary vs multiclass
        if y_proba.ndim == 2 and y_proba.shape[1] == 2:
            # Binary with 2 columns
            y_proba_pos = y_proba[:, 1]
            auc_score = average_precision_score(y_true_norm, y_proba_pos)
        elif y_proba.ndim == 2 and y_proba.shape[1] > 2:
            # Multiclass
            from sklearn.preprocessing import label_binarize

            n_classes = y_proba.shape[1]
            y_true_bin = label_binarize(y_true_norm, classes=range(n_classes))
            auc_score = average_precision_score(
                y_true_bin, y_proba, average="weighted"
            )
        else:
            # 1D array
            auc_score = average_precision_score(y_true_norm, y_proba)

        result = {
            "metric": "pr_auc",
            "value": float(auc_score),
            "fold": fold,
            "labels": label_names,
        }

        if return_curve and y_proba.ndim <= 2 and (
            y_proba.ndim == 1 or y_proba.shape[1] == 2
        ):
            # Only for binary classification
            try:
                y_proba_curve = y_proba[:, 1] if y_proba.ndim == 2 else y_proba
                precision, recall, thresholds = precision_recall_curve(
                    y_true_norm, y_proba_curve
                )
                result["curve"] = {
                    "precision": precision.tolist(),
                    "recall": recall.tolist(),
                    "thresholds": thresholds.tolist(),
                }
            except:
                pass

        return result
    except Exception as e:
        return {
            "metric": "pr_auc",
            "value": np.nan,
            "fold": fold,
            "error": str(e),
        }


# EOF
