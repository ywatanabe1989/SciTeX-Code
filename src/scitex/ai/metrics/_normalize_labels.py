#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-02 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/ml/metrics/_normalize_labels.py

"""Label normalization utility for classification metrics."""

__FILE__ = __file__

from typing import List, Optional, Tuple
import numpy as np
from sklearn.preprocessing import LabelEncoder


def normalize_labels(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    labels: Optional[List] = None,
) -> Tuple[np.ndarray, np.ndarray, List, LabelEncoder]:
    """
    Normalize labels using sklearn.preprocessing.LabelEncoder.

    Parameters
    ----------
    y_true : np.ndarray
        True labels (can be str or int)
    y_pred : np.ndarray
        Predicted labels (can be str or int)
    labels : List, optional
        Expected label list. If provided, will be used as display names.

    Returns
    -------
    y_true_norm : np.ndarray
        Normalized true labels (integers 0, 1, 2, ...)
    y_pred_norm : np.ndarray
        Normalized predicted labels (integers 0, 1, 2, ...)
    label_names : List
        List of label names in order
    encoder : LabelEncoder
        Fitted encoder for inverse transform

    Notes
    -----
    Uses sklearn.preprocessing.LabelEncoder for robust label handling.
    Handles the edge case where data contains integers but labels are strings
    (e.g., y_true=[0,1,0,1] with labels=['Negative', 'Positive']).
    """
    # Get unique values from data
    all_data_labels = np.unique(np.concatenate([y_true, y_pred]))

    # Create encoder
    le = LabelEncoder()

    # Handle edge case: integer data with string label names
    if labels is not None:
        # Check if data is integers but labels are strings
        data_is_int = isinstance(all_data_labels[0], (int, np.integer))
        labels_are_str = isinstance(labels[0], str)

        if data_is_int and labels_are_str:
            # Data: [0, 1], labels: ['Negative', 'Positive']
            # Fit encoder on the integer data
            le.fit(all_data_labels)
            # But use provided labels as names for display
            label_names = labels
        else:
            # Normal case: fit on provided labels
            le.fit(labels)
            label_names = list(le.classes_)
    else:
        # No labels provided: fit on observed data
        le.fit(all_data_labels)
        label_names = list(le.classes_)

    # Transform to integers
    y_true_norm = le.transform(y_true)
    y_pred_norm = le.transform(y_pred)

    return y_true_norm, y_pred_norm, label_names, le


# EOF
