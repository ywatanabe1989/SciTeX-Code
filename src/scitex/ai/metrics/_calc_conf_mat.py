#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-02 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/ml/metrics/_calc_conf_mat.py

"""Calculate confusion matrix."""

__FILE__ = __file__

from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix as sklearn_confusion_matrix
from ._normalize_labels import normalize_labels


def calc_conf_mat(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    labels: Optional[List] = None,
    fold: Optional[int] = None,
    normalize: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Calculate confusion matrix with robust label handling.

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
    normalize : str, optional
        'true', 'pred', 'all', or None

    Returns
    -------
    Dict[str, Any]
        {
            'metric': 'confusion_matrix',
            'value': pd.DataFrame,
            'fold': int,
            'labels': list
        }
    """
    try:
        y_true_norm, y_pred_norm, label_names, _ = normalize_labels(
            y_true, y_pred, labels
        )

        # Calculate confusion matrix
        cm = sklearn_confusion_matrix(
            y_true_norm,
            y_pred_norm,
            labels=list(range(len(label_names))),
        )

        # Normalize if requested
        if normalize == "true":
            cm = cm.astype("float") / cm.sum(axis=1, keepdims=True)
        elif normalize == "pred":
            cm = cm.astype("float") / cm.sum(axis=0, keepdims=True)
        elif normalize == "all":
            cm = cm.astype("float") / cm.sum()

        # Convert to DataFrame
        cm_df = pd.DataFrame(cm, index=label_names, columns=label_names)

        return {
            "metric": "confusion_matrix",
            "value": cm_df,
            "fold": fold,
            "labels": label_names,
            "normalize": normalize,
        }
    except Exception as e:
        import sys
        print(f"ERROR in calc_conf_mat: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return {
            "metric": "confusion_matrix",
            "value": None,
            "fold": fold,
            "error": str(e),
        }


# EOF
