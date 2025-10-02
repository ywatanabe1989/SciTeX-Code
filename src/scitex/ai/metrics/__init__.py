#!/usr/bin/env python3
"""Scitex metrics module.

Standardized naming convention:
- calc_* functions: Modern standardized metric calculations
- Legacy names (bACC, balanced_accuracy, etc.): For backward compatibility
"""

# Modern standardized calc_* functions
from ._normalize_labels import normalize_labels as _normalize_labels
from ._calc_bacc import calc_bacc
from ._calc_mcc import calc_mcc
from ._calc_conf_mat import calc_conf_mat
from ._calc_clf_report import calc_clf_report
from ._calc_roc_auc import calc_roc_auc
from ._calc_pre_rec_auc import calc_pre_rec_auc
from ._calc_bacc_from_conf_mat import calc_bacc_from_conf_mat
from ._calc_seizure_prediction_metrics import (
    calc_seizure_window_prediction_metrics,
    calc_seizure_event_prediction_metrics,
    calc_seizure_prediction_metrics,  # backward compat alias
)
from ._calc_silhouette_score import (
    calc_silhouette_score_slow,
    calc_silhouette_samples_slow,
    calc_silhouette_score_block,
    calc_silhouette_samples_block,
)
from ._calc_feature_importance import (
    calc_feature_importance,
    calc_permutation_importance,
)

__all__ = [
    "calc_bacc",
    "calc_mcc",
    "calc_conf_mat",
    "calc_clf_report",
    "calc_roc_auc",
    "calc_pre_rec_auc",
    "calc_bacc_from_conf_mat",
    "calc_seizure_window_prediction_metrics",
    "calc_seizure_event_prediction_metrics",
    "calc_seizure_prediction_metrics",  # backward compat alias
    "calc_silhouette_score_slow",
    "calc_silhouette_samples_slow",
    "calc_silhouette_score_block",
    "calc_silhouette_samples_block",
    "calc_feature_importance",
    "calc_permutation_importance",
    # # Legacy names for backward compatibility
    # "bACC",
    # "balanced_accuracy",
    # "bACC_from_conf_mat",
    # "balanced_accuracy_from_conf_mat",
]
