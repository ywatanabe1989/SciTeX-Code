#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-02 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/ml/metrics/_calc_clf_report.py

"""Generate classification report."""

__FILE__ = __file__

from typing import Any, Dict, List, Optional
import pandas as pd
from sklearn.metrics import classification_report
from ._normalize_labels import normalize_labels


def calc_clf_report(
    y_true,
    y_pred,
    labels: Optional[List] = None,
    fold: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Generate classification report with robust label handling.

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
        {
            'metric': 'classification_report',
            'value': pd.DataFrame,
            'fold': int,
            'labels': list
        }
    """
    try:
        y_true_norm, y_pred_norm, label_names, _ = normalize_labels(
            y_true, y_pred, labels
        )

        # Get classification report
        report_dict = classification_report(
            y_true_norm,
            y_pred_norm,
            target_names=[str(l) for l in label_names],
            output_dict=True,
            zero_division=0,
        )

        # Convert to DataFrame
        report_df = pd.DataFrame(report_dict).T

        return {
            "metric": "classification_report",
            "value": report_df,
            "fold": fold,
            "labels": label_names,
        }
    except Exception as e:
        return {
            "metric": "classification_report",
            "value": None,
            "fold": fold,
            "error": str(e),
        }


# EOF
