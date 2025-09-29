#!/usr/bin/env python3
"""
Pure metric calculation functions.

These functions only calculate metrics - no file I/O or side effects.
Each returns both the metric value and a standardized dict format.
"""

import numpy as np
import pandas as pd
from sklearn.metrics import (
    balanced_accuracy_score,
    matthews_corrcoef,
    confusion_matrix,
    classification_report,
    roc_auc_score,
    average_precision_score,
    roc_curve,
    precision_recall_curve
)
from typing import Tuple, Dict, Any, List, Optional


def calc_balanced_accuracy(
    y_true: np.ndarray, 
    y_pred: np.ndarray,
    fold: Optional[int] = None
) -> Dict[str, Any]:
    """
    Calculate balanced accuracy score.
    
    Parameters
    ----------
    y_true : np.ndarray
        True labels
    y_pred : np.ndarray
        Predicted labels
    fold : int, optional
        Fold number for tracking
        
    Returns
    -------
    Dict[str, Any]
        {'metric': 'balanced_accuracy', 'value': float, 'fold': int}
        
    Examples
    --------
    >>> result = calc_balanced_accuracy(y_true, y_pred, fold=1)
    >>> print(f"Balanced Accuracy: {result['value']:.3f}")
    """
    value = balanced_accuracy_score(y_true, y_pred)
    return {
        'metric': 'balanced_accuracy',
        'value': float(value),
        'fold': fold
    }


def calc_mcc(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    fold: Optional[int] = None
) -> Dict[str, Any]:
    """
    Calculate Matthews Correlation Coefficient.
    
    Parameters
    ----------
    y_true : np.ndarray
        True labels
    y_pred : np.ndarray
        Predicted labels
    fold : int, optional
        Fold number for tracking
        
    Returns
    -------
    Dict[str, Any]
        {'metric': 'mcc', 'value': float, 'fold': int}
    """
    value = matthews_corrcoef(y_true, y_pred)
    return {
        'metric': 'mcc',
        'value': float(value),
        'fold': fold
    }


def calc_confusion_matrix(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    labels: Optional[List[str]] = None,
    fold: Optional[int] = None
) -> Dict[str, Any]:
    """
    Calculate confusion matrix.
    
    Parameters
    ----------
    y_true : np.ndarray
        True labels
    y_pred : np.ndarray
        Predicted labels
    labels : List[str], optional
        Class label names. If None, will use unique values from y_true.
    fold : int, optional
        Fold number for tracking
        
    Returns
    -------
    Dict[str, Any]
        {'metric': 'confusion_matrix', 'value': np.ndarray, 'fold': int}
    """
    cm = confusion_matrix(y_true, y_pred)
    
    # Infer labels if not provided
    if labels is None:
        unique_labels = np.unique(np.concatenate([y_true, y_pred]))
        labels = [str(label) for label in unique_labels]
    
    return {
        'metric': 'confusion_matrix',
        'value': cm,
        'fold': fold,
        'labels': labels
    }


def calc_classification_report(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    labels: Optional[List[str]] = None,
    additional_metrics: Optional[Dict[str, float]] = None,
    fold: Optional[int] = None
) -> Dict[str, Any]:
    """
    Generate classification report with optional additional metrics.
    
    Parameters
    ----------
    y_true : np.ndarray
        True labels
    y_pred : np.ndarray
        Predicted labels
    labels : List[str], optional
        Class label names. If None, will use unique values from y_true.
    additional_metrics : Dict[str, float], optional
        Additional metrics to include (e.g., {'balanced_accuracy': 0.85, 'mcc': 0.7})
    fold : int, optional
        Fold number for tracking
        
    Returns
    -------
    Dict[str, Any]
        {'metric': 'classification_report', 'value': pd.DataFrame, 'fold': int}
    """
    # Infer labels if not provided
    if labels is None:
        unique_labels = np.unique(np.concatenate([y_true, y_pred]))
        labels = [str(label) for label in unique_labels]
    
    # Get sklearn classification report
    report_dict = classification_report(
        y_true, y_pred,
        target_names=labels,
        output_dict=True
    )
    
    report_df = pd.DataFrame(report_dict).T
    
    # Add additional metrics if provided
    if additional_metrics:
        for metric_name, metric_value in additional_metrics.items():
            report_df[metric_name] = metric_value
    
    # Clean up index
    report_df = report_df.round(3)
    
    return {
        'metric': 'classification_report',
        'value': report_df,
        'fold': fold,
        'n_classes': len(labels),
        'labels': labels
    }


def calc_roc_auc(
    y_true: np.ndarray,
    y_proba: np.ndarray,
    fold: Optional[int] = None,
    return_curve: bool = False
) -> Dict[str, Any]:
    """
    Calculate ROC AUC score.
    
    Parameters
    ----------
    y_true : np.ndarray
        True labels (binary or multiclass)
    y_proba : np.ndarray
        Predicted probabilities. Can be:
        - 1D array of positive class probabilities for binary
        - 2D array with shape (n_samples, 2) for binary 
        - 2D array with shape (n_samples, n_classes) for multiclass
    fold : int, optional
        Fold number for tracking
    return_curve : bool
        Whether to return the ROC curve data
        
    Returns
    -------
    Dict[str, Any]
        {'metric': 'roc_auc', 'value': float, 'fold': int, 'curve': optional}
    """
    # Handle different input formats
    if y_proba.ndim == 2:
        if y_proba.shape[1] == 2:
            # Binary classification with 2 columns - use positive class probabilities
            y_proba_positive = y_proba[:, 1]
            auc_score = roc_auc_score(y_true, y_proba_positive)
        else:
            # Multiclass case
            auc_score = roc_auc_score(y_true, y_proba, multi_class='ovr')
    else:
        # 1D array - already positive class probabilities
        auc_score = roc_auc_score(y_true, y_proba)
    
    result = {
        'metric': 'roc_auc',
        'value': float(auc_score),
        'fold': fold
    }
    
    if return_curve:
        # ROC curve only works for binary classification
        # For multiclass, would need per-class curves
        if not (y_proba.ndim == 2 and y_proba.shape[1] > 2):
            try:
                # Use the same probabilities we used for AUC calculation
                if y_proba.ndim == 2 and y_proba.shape[1] == 2:
                    y_proba_for_curve = y_proba[:, 1]
                else:
                    y_proba_for_curve = y_proba
                    
                fpr, tpr, thresholds = roc_curve(y_true, y_proba_for_curve)
                result['curve'] = {
                    'fpr': fpr.tolist(),
                    'tpr': tpr.tolist(),
                    'thresholds': thresholds.tolist()
                }
            except:
                pass  # Skip curve if it fails
    
    return result


def calc_pr_auc(
    y_true: np.ndarray,
    y_proba: np.ndarray,
    fold: Optional[int] = None,
    return_curve: bool = False
) -> Dict[str, Any]:
    """
    Calculate Precision-Recall AUC score.
    
    Parameters
    ----------
    y_true : np.ndarray
        True labels (binary or multiclass)
    y_proba : np.ndarray
        Predicted probabilities. Can be:
        - 1D array of positive class probabilities for binary
        - 2D array with shape (n_samples, 2) for binary 
        - 2D array with shape (n_samples, n_classes) for multiclass
    fold : int, optional
        Fold number for tracking
    return_curve : bool
        Whether to return the PR curve data
        
    Returns
    -------
    Dict[str, Any]
        {'metric': 'pr_auc', 'value': float, 'fold': int, 'curve': optional}
    """
    # Handle different input formats
    if y_proba.ndim == 2:
        if y_proba.shape[1] == 2:
            # Binary classification with 2 columns - use positive class probabilities
            y_proba_positive = y_proba[:, 1]
            auc_score = average_precision_score(y_true, y_proba_positive)
        else:
            # Multiclass case
            from sklearn.preprocessing import label_binarize
            n_classes = y_proba.shape[1]
            y_true_bin = label_binarize(y_true, classes=range(n_classes))
            auc_score = average_precision_score(y_true_bin, y_proba, average='weighted')
    else:
        # 1D array - already positive class probabilities
        auc_score = average_precision_score(y_true, y_proba)
    
    result = {
        'metric': 'pr_auc',
        'value': float(auc_score),
        'fold': fold
    }
    
    if return_curve:
        # PR curve only works for binary classification
        # For multiclass, would need per-class curves
        if not (y_proba.ndim == 2 and y_proba.shape[1] > 2):
            try:
                precision, recall, thresholds = precision_recall_curve(y_true, y_proba)
                result['curve'] = {
                    'precision': precision.tolist(),
                    'recall': recall.tolist(),
                    'thresholds': thresholds.tolist()
                }
            except:
                pass  # Skip curve if it fails
    
    return result