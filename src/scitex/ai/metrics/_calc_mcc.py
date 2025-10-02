#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-02 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/ml/metrics/_calc_mcc.py

"""Calculate Matthews Correlation Coefficient."""

__FILE__ = __file__

from typing import Any, Dict, List, Optional
import numpy as np
from sklearn.metrics import matthews_corrcoef
from ._normalize_labels import normalize_labels


def calc_mcc(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    labels: Optional[List] = None,
    fold: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Calculate Matthews Correlation Coefficient with robust label handling.

    Parameters
    ----------
    y_true : np.ndarray
        True labels (can be str or int)
    y_pred : np.ndarray
        Predicted labels (can be str or int)
    labels : List, optional
        Expected label list
    fold : int, optional
        Fold number for tracking

    Returns
    -------
    Dict[str, Any]
        {'metric': 'mcc', 'value': float, 'fold': int}
    """
    try:
        y_true_norm, y_pred_norm, label_names, _ = normalize_labels(
            y_true, y_pred, labels
        )
        value = matthews_corrcoef(y_true_norm, y_pred_norm)
        return {
            "metric": "mcc",
            "value": float(value),
            "fold": fold,
            "labels": label_names,
        }
    except Exception as e:
        return {
            "metric": "mcc",
            "value": np.nan,
            "fold": fold,
            "error": str(e),
        }


# EOF
