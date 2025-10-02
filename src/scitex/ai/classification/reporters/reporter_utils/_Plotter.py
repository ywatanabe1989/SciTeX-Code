#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-02 18:55:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/ml/classification/reporters/reporter_utils/_Plotter.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = "./src/scitex/ml/classification/reporters/reporter_utils/_Plotter.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Classification Plotter - Delegates to stx.ml.plt functions.

This module provides a Plotter class that delegates to centralized
plotting functions in scitex.ml.plt to maintain DRY principle.

Features:
- Graceful error handling
- Headless environment support (Agg backend)
- Optional plotting with proper disabling
- Delegates to:
  * stx.ml.plt.conf_mat (confusion matrices)
  * stx.ml.plt.roc_auc (ROC curves)
  * stx.ml.plt.pre_rec_auc (Precision-Recall curves)
"""

import warnings
from pathlib import Path
from typing import Any, List, Optional, Union

import numpy as np

# Import centralized plotting functions from stx.ml.plt
try:
    import matplotlib
    import matplotlib.pyplot as plt

    # Try to import seaborn for enhanced visualizations
    try:
        import seaborn as sns
    except ImportError:
        sns = None

    # Import scitex plotting functions
    import scitex as stx
    from scitex.ml.plt.plot_conf_mat import plot_conf_mat as conf_mat
    from scitex.ml.plt.plot_roc_curve import plot_roc_curve as roc_auc
    from scitex.ml.plt.plot_pre_rec_curve import plot_pre_rec_curve as pre_rec_auc

    PLOTTING_AVAILABLE = True
except ImportError:
    PLOTTING_AVAILABLE = False
    plt = None
    sns = None
    conf_mat = None
    roc_auc = None
    pre_rec_auc = None


class Plotter:
    """
    Enhanced plotter with graceful error handling.

    Features:
    - Automatically disables if plotting libraries unavailable
    - Uses non-interactive backend when no display available
    - Provides informative error messages
    - Supports fallback options
    """

    def __init__(
        self,
        enable_plotting: bool = True,
        save_dir: Optional[Path] = None,
        verbose: bool = True,
    ):
        """
        Initialize plotter.

        Parameters
        ----------
        enable_plotting : bool, default True
            Whether to attempt plotting
        save_dir : Path, optional
            Directory to save plots
        """
        self.enabled = enable_plotting and PLOTTING_AVAILABLE
        self.save_dir = Path(save_dir) if save_dir else None
        self.verbose = verbose

        if enable_plotting and not PLOTTING_AVAILABLE:
            warnings.warn(
                "Plotting libraries not available. Plotting disabled.",
                UserWarning,
            )

    def create_confusion_matrix_plot(
        self,
        confusion_matrix: np.ndarray,
        labels: Optional[List[str]] = None,
        save_path: Optional[Union[str, Path]] = None,
        verbose: bool = True,
        title: str = "Confusion Matrix",
    ) -> Optional[Any]:
        """
        Create confusion matrix plot with error handling.

        Parameters
        ----------
        confusion_matrix : np.ndarray
            Confusion matrix
        labels : List[str], optional
            Class labels
        save_path : Union[str, Path], optional
            Path to save plot
        verbose : bool
            Whether to print messages
        title : str, default "Confusion Matrix"
            Title for the plot

        Returns
        -------
        Optional[Any]
            Matplotlib figure or None if plotting failed
        """
        if not self.enabled or confusion_matrix is None:
            return None

        try:
            # Delegate to centralized conf_mat function from stx.ml.plt
            fig = conf_mat(
                cm=confusion_matrix,
                labels=labels,
                title=title,
                spath=save_path,
            )
            return fig
        except Exception as e:
            if self.verbose:
                warnings.warn(
                    f"Failed to create confusion matrix plot: {e}", UserWarning
                )
            return None

    def create_roc_curve(
        self,
        y_true: np.ndarray,
        y_proba: np.ndarray,
        labels: Optional[List[str]] = None,
        save_path: Optional[Union[str, Path]] = None,
        verbose: bool = True,
        title: str = "ROC Curve",
    ) -> Optional[Any]:
        """
        Create ROC curve plot - delegates to stx.ml.plt.roc_auc.

        Parameters
        ----------
        y_true : np.ndarray
            True labels
        y_proba : np.ndarray
            Prediction probabilities
        labels : List[str], optional
            Class labels
        save_path : Union[str, Path], optional
            Path to save plot
        verbose : bool
            Whether to print messages
        title : str, default "ROC Curve"
            Title for the plot

        Returns
        -------
        Optional[Any]
            Matplotlib figure or None if plotting failed
        """
        if not self.enabled or y_true is None or y_proba is None:
            return None

        try:
            # Delegate to centralized roc_auc function from stx.ml.plt
            fig, _ = roc_auc(
                true_class=y_true,
                pred_proba=y_proba,
                labels=labels or [],
                spath=save_path,
            )
            return fig
        except Exception as e:
            import sys
            print(f"ERROR in create_roc_curve: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            if self.verbose:
                warnings.warn(f"Failed to create ROC curve: {e}", UserWarning)
            return None

    def create_precision_recall_curve(
        self,
        y_true: np.ndarray,
        y_proba: np.ndarray,
        labels: Optional[List[str]] = None,
        save_path: Optional[Union[str, Path]] = None,
        verbose: bool = True,
        title: str = "Precision-Recall Curve",
    ) -> Optional[Any]:
        """
        Create Precision-Recall curve plot - delegates to stx.ml.plt.pre_rec_auc.

        Parameters
        ----------
        y_true : np.ndarray
            True labels
        y_proba : np.ndarray
            Prediction probabilities
        labels : List[str], optional
            Class labels
        save_path : Union[str, Path], optional
            Path to save plot
        verbose : bool
            Whether to print messages
        title : str, default "Precision-Recall Curve"
            Title for the plot

        Returns
        -------
        Optional[Any]
            Matplotlib figure or None if plotting failed
        """
        if not self.enabled or y_true is None or y_proba is None:
            return None

        try:
            # Delegate to centralized pre_rec_auc function from stx.ml.plt
            fig, _ = pre_rec_auc(
                true_class=y_true,
                pred_proba=y_proba,
                labels=labels or [],
                spath=save_path,
            )
            return fig
        except Exception as e:
            import sys
            print(f"ERROR in create_precision_recall_curve: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            if self.verbose:
                warnings.warn(f"Failed to create PR curve: {e}", UserWarning)
            return None

    def create_overall_roc_curve(
        self,
        y_true: np.ndarray,
        y_proba: np.ndarray,
        labels: Optional[List[str]] = None,
        save_path: Optional[Union[str, Path]] = None,
        verbose: bool = True,
        title: str = "ROC Curve (Overall)",
        auc_mean: Optional[float] = None,
        auc_std: Optional[float] = None,
    ) -> Optional[Any]:
        """
        Create overall ROC curve plot with AUC statistics.

        Parameters
        ----------
        y_true : np.ndarray
            True labels
        y_proba : np.ndarray
            Prediction probabilities
        save_path : Union[str, Path], optional
            Path to save plot
        verbose : bool
            Whether to print messages
        title : str
            Title for the plot
        auc_mean : float, optional
            Mean AUC across folds
        auc_std : float, optional
            Standard deviation of AUC across folds

        Returns
        -------
        Optional[Any]
            Matplotlib figure or None if plotting failed
        """
        if not self.enabled:
            return None

        try:
            from sklearn.metrics import auc, roc_curve

            # Handle binary vs multiclass
            if y_proba.ndim == 1 or y_proba.shape[1] == 2:
                # Binary classification
                if y_proba.ndim == 2:
                    y_proba_pos = y_proba[:, 1]
                else:
                    y_proba_pos = y_proba

                # Determine pos_label for string labels
                pos_label = None
                if labels and len(labels) >= 2:
                    pos_label = labels[1]  # Second label is positive class

                fpr, tpr, _ = roc_curve(y_true, y_proba_pos, pos_label=pos_label)
                roc_auc = auc(fpr, tpr)

                fig, ax = plt.subplots(figsize=(8, 8))  # Square figure

                # Use provided mean/std if available, otherwise use calculated AUC
                if auc_mean is not None and auc_std is not None:
                    label = f"ROC Curve (AUC = {auc_mean:.3f} ± {auc_std:.3f})"
                else:
                    label = f"ROC Curve (AUC = {roc_auc:.3f})"

                ax.plot(fpr, tpr, label=label, linewidth=2)
                ax.plot([0, 1], [0, 1], "k--", label="Random", alpha=0.5)
                ax.set_xlabel("False Positive Rate")
                ax.set_ylabel("True Positive Rate")
                ax.set_title(title)
                ax.set_xlim([0, 1])
                ax.set_ylim([0, 1])
                ax.set_aspect("equal")
                ax.legend(loc="lower right")
                ax.grid(True, alpha=0.3)

            else:
                # Multiclass - not fully supported for overall curves yet
                return None

            if save_path:
                try:
                    from pathlib import Path
                    from scitex.io import save as stx_io_save

                    # Resolve to absolute path to prevent _out directory creation
                    save_path_abs = Path(save_path).resolve() if isinstance(save_path, (str, Path)) else save_path
                    stx_io_save(fig, str(save_path_abs), verbose=True, use_caller_path=False)
                except Exception as save_error:
                    print(f"ERROR: Failed to save ROC curve: {save_error}")
                    import traceback
                    traceback.print_exc()

            plt.close(fig)  # Clean up
            return fig

        except Exception as e:
            print(f"ERROR in create_overall_roc_curve: {e}")
            import traceback
            traceback.print_exc()
            warnings.warn(
                f"Failed to create overall ROC curve: {e}", UserWarning
            )
            return None

    def create_overall_pr_curve(
        self,
        y_true: np.ndarray,
        y_proba: np.ndarray,
        labels: Optional[List[str]] = None,
        save_path: Optional[Union[str, Path]] = None,
        verbose: bool = True,
        title: str = "Precision-Recall Curve (Overall)",
        ap_mean: Optional[float] = None,
        ap_std: Optional[float] = None,
    ) -> Optional[Any]:
        """
        Create overall Precision-Recall curve plot with AP statistics.

        Parameters
        ----------
        y_true : np.ndarray
            True labels
        y_proba : np.ndarray
            Prediction probabilities
        save_path : Union[str, Path], optional
            Path to save plot
        verbose : bool
            Whether to print messages
        title : str
            Title for the plot
        ap_mean : float, optional
            Mean Average Precision across folds
        ap_std : float, optional
            Standard deviation of AP across folds

        Returns
        -------
        Optional[Any]
            Matplotlib figure or None if plotting failed
        """
        if not self.enabled:
            return None

        try:
            from sklearn.metrics import (average_precision_score,
                                         precision_recall_curve)

            # Handle binary classification
            if y_proba.ndim == 1 or y_proba.shape[1] == 2:
                if y_proba.ndim == 2:
                    y_proba_pos = y_proba[:, 1]
                else:
                    y_proba_pos = y_proba

                precision, recall, _ = precision_recall_curve(
                    y_true, y_proba_pos
                )
                avg_precision = average_precision_score(y_true, y_proba_pos)

                fig, ax = plt.subplots(figsize=(8, 8))  # Square figure

                # Use provided mean/std if available, otherwise use calculated AP
                if ap_mean is not None and ap_std is not None:
                    label = f"PR Curve (Average Precision (AP) = {ap_mean:.3f} ± {ap_std:.3f})"
                else:
                    label = f"PR Curve (Average Precision (AP) = {avg_precision:.3f})"

                ax.plot(recall, precision, label=label, linewidth=2)
                ax.set_xlabel("Recall")
                ax.set_ylabel("Precision")
                ax.set_title(title)
                ax.set_xlim([0, 1])
                ax.set_ylim([0, 1])
                ax.set_aspect("equal")
                ax.legend(loc="best")
                ax.grid(True, alpha=0.3)

            else:
                # Multiclass not well-defined for PR curves
                return None

            if save_path:
                from pathlib import Path
                from scitex.io import save as stx_io_save

                # Resolve to absolute path to prevent _out directory creation
                save_path_abs = Path(save_path).resolve() if isinstance(save_path, (str, Path)) else save_path
                stx_io_save(fig, str(save_path_abs), verbose=verbose or self.verbose, use_caller_path=False)

            plt.close(fig)  # Clean up
            return fig

        except Exception as e:
            warnings.warn(
                f"Failed to create overall PR curve: {e}", UserWarning
            )
            return None


    def create_metrics_visualization(
        self,
        metrics: dict,
        y_true: Optional[np.ndarray] = None,
        y_pred: Optional[np.ndarray] = None,
        y_proba: Optional[np.ndarray] = None,
        labels: Optional[List[str]] = None,
        save_path: Optional[Union[str, Path]] = None,
        title: str = "Classification Metrics Summary",
        fold: Optional[int] = None,
        verbose: bool = True,
    ) -> Optional[Any]:
        """
        Create comprehensive metrics visualization dashboard.

        This generalized method creates a multi-panel figure showing:
        - Confusion matrix (if y_true and y_pred available)
        - ROC curve (if y_true and y_proba available)
        - Precision-Recall curve (if y_true and y_proba available)
        - Key metrics summary table

        Parameters
        ----------
        metrics : dict
            Dictionary of calculated metrics (balanced_accuracy, mcc, etc.)
        y_true : np.ndarray, optional
            True labels
        y_pred : np.ndarray, optional
            Predicted labels
        y_proba : np.ndarray, optional
            Prediction probabilities
        labels : List[str], optional
            Class labels
        save_path : Union[str, Path], optional
            Path to save the visualization
        title : str, default "Classification Metrics Summary"
            Overall title for the figure
        fold : int, optional
            Fold number (for cross-validation)
        verbose : bool, default True
            Whether to print messages

        Returns
        -------
        Optional[Any]
            Matplotlib figure or None if plotting failed

        Examples
        --------
        >>> plotter = Plotter(enable_plotting=True)
        >>> metrics = {
        ...     'balanced_accuracy': 0.85,
        ...     'mcc': 0.75,
        ...     'roc_auc': 0.90
        ... }
        >>> fig = plotter.create_metrics_visualization(
        ...     metrics, y_true, y_pred, y_proba,
        ...     save_path='metrics_summary.png'
        ... )
        """
        if not self.enabled:
            return None

        try:
            # Determine layout based on available data
            has_cm = y_true is not None and y_pred is not None
            has_roc = y_true is not None and y_proba is not None
            has_pr = has_roc  # Same requirements

            # Count available plots
            n_plots = sum([has_cm, has_roc, has_pr, True])  # +1 for metrics table

            # Create figure with appropriate layout
            if n_plots == 4:
                fig = plt.figure(figsize=(16, 12))
                gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
                positions = [(0, 0), (0, 1), (1, 0), (1, 1)]
            elif n_plots == 3:
                fig = plt.figure(figsize=(16, 6))
                gs = fig.add_gridspec(1, 3, hspace=0.3, wspace=0.3)
                positions = [(0, 0), (0, 1), (0, 2)]
            elif n_plots == 2:
                fig = plt.figure(figsize=(12, 6))
                gs = fig.add_gridspec(1, 2, hspace=0.3, wspace=0.3)
                positions = [(0, 0), (0, 1)]
            else:
                fig = plt.figure(figsize=(8, 6))
                gs = fig.add_gridspec(1, 1)
                positions = [(0, 0)]

            # Set overall title
            fold_suffix = f" (Fold {fold})" if fold is not None else ""
            fig.suptitle(f"{title}{fold_suffix}", fontsize=16, fontweight='bold')

            plot_idx = 0

            # Plot 1: Confusion Matrix
            if has_cm:
                ax = fig.add_subplot(gs[positions[plot_idx]])
                plot_idx += 1

                # Get confusion matrix from metrics or calculate
                cm = metrics.get('confusion_matrix')
                if cm is not None:
                    if isinstance(cm, dict) and 'value' in cm:
                        cm = cm['value']

                    if sns is not None:
                        sns.heatmap(
                            cm,
                            annot=True,
                            fmt='d',
                            cmap='Blues',
                            xticklabels=labels,
                            yticklabels=labels,
                            ax=ax,
                            cbar_kws={'label': 'Count'}
                        )
                    else:
                        im = ax.imshow(cm, cmap='Blues')
                        # Add annotations
                        for i in range(cm.shape[0]):
                            for j in range(cm.shape[1]):
                                ax.text(j, i, str(cm[i, j]),
                                       ha='center', va='center')

                    ax.set_xlabel('Predicted Label')
                    ax.set_ylabel('True Label')
                    ax.set_title('Confusion Matrix')

            # Plot 2: ROC Curve
            if has_roc:
                ax = fig.add_subplot(gs[positions[plot_idx]])
                plot_idx += 1

                from sklearn.metrics import auc, roc_curve

                # Handle binary vs multiclass
                if y_proba.ndim == 1 or y_proba.shape[1] == 2:
                    # Binary
                    if y_proba.ndim == 2:
                        y_proba_pos = y_proba[:, 1]
                    else:
                        y_proba_pos = y_proba

                    # Determine pos_label for string labels
                    pos_label = None
                    if labels and len(labels) >= 2:
                        pos_label = labels[1]  # Second label is positive class

                    fpr, tpr, _ = roc_curve(y_true, y_proba_pos, pos_label=pos_label)
                    roc_auc = auc(fpr, tpr)

                    ax.plot(fpr, tpr, label=f'AUC = {roc_auc:.3f}', linewidth=2)
                    ax.plot([0, 1], [0, 1], 'k--', label='Random', alpha=0.5)
                else:
                    # Multiclass - plot each class
                    for i in range(y_proba.shape[1]):
                        y_true_binary = (y_true == i).astype(int)
                        fpr, tpr, _ = roc_curve(y_true_binary, y_proba[:, i])
                        roc_auc = auc(fpr, tpr)
                        class_label = labels[i] if labels else f'Class {i}'
                        ax.plot(fpr, tpr, label=f'{class_label} (AUC={roc_auc:.3f})')

                    ax.plot([0, 1], [0, 1], 'k--', label='Random', alpha=0.5)

                ax.set_xlabel('False Positive Rate')
                ax.set_ylabel('True Positive Rate')
                ax.set_title('ROC Curve')
                ax.set_xlim([0, 1])
                ax.set_ylim([0, 1])
                ax.legend(loc='lower right')
                ax.grid(True, alpha=0.3)

            # Plot 3: Precision-Recall Curve
            if has_pr and (y_proba.ndim == 1 or y_proba.shape[1] == 2):
                ax = fig.add_subplot(gs[positions[plot_idx]])
                plot_idx += 1

                from sklearn.metrics import (average_precision_score,
                                           precision_recall_curve)

                if y_proba.ndim == 2:
                    y_proba_pos = y_proba[:, 1]
                else:
                    y_proba_pos = y_proba

                # Convert string labels to integer indices if needed
                y_true_for_pr = y_true
                if y_true.dtype.kind in ('U', 'S', 'O'):  # Unicode, bytes, or object (string)
                    if labels:
                        label_to_idx = {label: idx for idx, label in enumerate(labels)}
                        y_true_for_pr = np.array([label_to_idx[yt] for yt in y_true])
                    else:
                        unique_labels = np.unique(y_true)
                        label_to_idx = {label: idx for idx, label in enumerate(unique_labels)}
                        y_true_for_pr = np.array([label_to_idx[yt] for yt in y_true])

                precision, recall, _ = precision_recall_curve(y_true_for_pr, y_proba_pos)
                avg_precision = average_precision_score(y_true_for_pr, y_proba_pos)

                ax.plot(recall, precision,
                       label=f'AP = {avg_precision:.3f}', linewidth=2)
                ax.set_xlabel('Recall')
                ax.set_ylabel('Precision')
                ax.set_title('Precision-Recall Curve')
                ax.set_xlim([0, 1])
                ax.set_ylim([0, 1])
                ax.legend(loc='lower left')
                ax.grid(True, alpha=0.3)

            # Plot 4: Metrics Summary Table
            ax = fig.add_subplot(gs[positions[plot_idx]])
            ax.axis('off')

            # Prepare metrics table
            metric_names = []
            metric_values = []

            # Standard metrics to display
            display_metrics = {
                'balanced_accuracy': 'Balanced Accuracy',
                'mcc': 'Matthews Corr Coef',
                'roc_auc': 'ROC AUC',
                'pr_auc': 'PR AUC',
                'pre_rec_auc': 'PR AUC',
                'accuracy': 'Accuracy',
                'precision': 'Precision',
                'recall': 'Recall',
                'f1_score': 'F1 Score',
            }

            for key, display_name in display_metrics.items():
                if key in metrics:
                    value = metrics[key]
                    # Extract value if wrapped in dict
                    if isinstance(value, dict) and 'value' in value:
                        value = value['value']
                    if value is not None:
                        metric_names.append(display_name)
                        if isinstance(value, (int, float)):
                            metric_values.append(f'{value:.4f}')
                        else:
                            metric_values.append(str(value))

            # Create table
            if metric_names:
                table_data = list(zip(metric_names, metric_values))
                table = ax.table(
                    cellText=table_data,
                    colLabels=['Metric', 'Value'],
                    cellLoc='left',
                    loc='center',
                    colWidths=[0.6, 0.4]
                )
                table.auto_set_font_size(False)
                table.set_fontsize(10)
                table.scale(1, 2)

                # Style header
                for i in range(2):
                    table[(0, i)].set_facecolor('#40466e')
                    table[(0, i)].set_text_props(weight='bold', color='white')

                # Alternate row colors
                for i in range(1, len(metric_names) + 1):
                    if i % 2 == 0:
                        for j in range(2):
                            table[(i, j)].set_facecolor('#f0f0f0')

            ax.set_title('Performance Metrics', fontweight='bold', pad=20)

            # Save figure
            if save_path:
                from pathlib import Path
                from scitex.io import save as stx_io_save
                # Resolve to absolute path to prevent _out directory creation
                save_path_abs = Path(save_path).resolve() if isinstance(save_path, (str, Path)) else save_path
                stx_io_save(fig, str(save_path_abs), verbose=verbose or self.verbose, use_caller_path=False)

            return fig

        except Exception as e:
            warnings.warn(
                f"Failed to create metrics visualization: {e}",
                UserWarning
            )
            import traceback
            traceback.print_exc()
            return None


    def create_feature_importance_plot(
        self,
        feature_importance: Union[np.ndarray, dict],
        feature_names: Optional[List[str]] = None,
        top_n: int = 20,
        save_path: Optional[Union[str, Path]] = None,
        verbose: bool = True,
        title: str = "Feature Importance",
    ) -> Optional[Any]:
        """
        Create feature importance plot.

        Parameters
        ----------
        feature_importance : np.ndarray or dict
            Feature importance values or dict with 'importance' key
        feature_names : List[str], optional
            Feature names
        top_n : int, default 20
            Number of top features to display
        save_path : Union[str, Path], optional
            Path to save plot
        verbose : bool
            Whether to print messages
        title : str
            Title for the plot

        Returns
        -------
        Optional[Any]
            Matplotlib figure or None if plotting failed
        """
        if not self.enabled:
            return None

        try:
            # Extract importance values
            if isinstance(feature_importance, dict):
                importance = feature_importance.get('importance', feature_importance.get('value'))
                if importance is None:
                    return None
            else:
                importance = feature_importance

            importance = np.array(importance)

            # Create feature names if not provided
            if feature_names is None:
                feature_names = [f'Feature {i}' for i in range(len(importance))]

            # Sort by importance
            indices = np.argsort(importance)[::-1][:top_n]
            sorted_importance = importance[indices]
            sorted_names = [feature_names[i] for i in indices]

            # Create horizontal bar plot
            fig, ax = plt.subplots(figsize=(10, max(6, top_n * 0.3)))
            y_pos = np.arange(len(sorted_names))

            ax.barh(y_pos, sorted_importance, align='center', alpha=0.7, color='steelblue')
            ax.set_yticks(y_pos)
            ax.set_yticklabels(sorted_names)
            ax.invert_yaxis()  # Top feature at top
            ax.set_xlabel('Importance')
            ax.set_title(title)
            ax.grid(True, alpha=0.3, axis='x')

            plt.tight_layout()

            if save_path:
                from scitex.io import save as stx_io_save
                stx_io_save(fig, save_path, verbose=verbose or self.verbose, use_caller_path=False)

            plt.close(fig)
            return fig

        except Exception as e:
            warnings.warn(f"Failed to create feature importance plot: {e}", UserWarning)
            return None

    def create_cv_aggregation_plot(
        self,
        fold_predictions: List[Dict[str, Any]],
        curve_type: str = 'roc',
        class_labels: Optional[List[str]] = None,
        save_path: Optional[Union[str, Path]] = None,
        verbose: bool = True,
        title: Optional[str] = None,
        show_mean: bool = True,
        show_individual_folds: bool = True,
        fold_alpha: float = 0.15,
    ) -> Optional[Any]:
        """
        Create CV aggregation plot with faded individual fold lines.

        This creates publication-quality cross-validation plots showing:
        - Individual fold curves (faded/transparent)
        - Mean curve across folds (bold)
        - Optional confidence intervals

        Parameters
        ----------
        fold_predictions : List[Dict[str, Any]]
            List of dicts with 'y_true', 'y_proba', and 'fold' keys
        curve_type : str, default 'roc'
            Type of curve: 'roc' or 'pr' (precision-recall)
        class_labels : List[str], optional
            Class labels for multiclass
        save_path : Union[str, Path], optional
            Path to save plot
        verbose : bool, default True
            Whether to print messages
        title : str, optional
            Custom title (auto-generated if None)
        show_mean : bool, default True
            Whether to show mean curve
        show_individual_folds : bool, default True
            Whether to show individual fold curves
        fold_alpha : float, default 0.15
            Transparency for individual fold curves (0-1)

        Returns
        -------
        Optional[Any]
            Matplotlib figure or None if plotting failed

        Examples
        --------
        >>> # ROC curve with faded fold lines
        >>> plotter.create_cv_aggregation_plot(
        ...     fold_predictions,
        ...     curve_type='roc',
        ...     title='Cross-Validation ROC Curves',
        ...     save_path='cv_roc.png'
        ... )
        >>> # PR curve without individual folds
        >>> plotter.create_cv_aggregation_plot(
        ...     fold_predictions,
        ...     curve_type='pr',
        ...     show_individual_folds=False,
        ...     save_path='cv_pr_mean_only.png'
        ... )
        """
        if not self.enabled:
            return None

        try:
            if curve_type not in ['roc', 'pr']:
                raise ValueError("curve_type must be 'roc' or 'pr'")

            from sklearn.metrics import (auc, average_precision_score,
                                       precision_recall_curve, roc_curve)

            fig, ax = plt.subplots(figsize=(8, 8))

            # Storage for interpolated curves
            if curve_type == 'roc':
                mean_fpr = np.linspace(0, 1, 100)
                tprs = []
                aucs = []
            else:  # pr
                mean_recall = np.linspace(0, 1, 100)
                precisions = []
                aps = []

            # Plot individual fold curves (faded)
            for fold_data in fold_predictions:
                y_true = fold_data['y_true']
                y_proba = fold_data['y_proba']
                fold_idx = fold_data.get('fold', 0)

                # Convert string labels to integer indices if needed
                y_true_numeric = y_true
                if y_true.dtype.kind in ('U', 'S', 'O'):  # Unicode, bytes, or object (string)
                    if class_labels and len(class_labels) >= 2:
                        label_to_idx = {label: idx for idx, label in enumerate(class_labels)}
                        y_true_numeric = np.array([label_to_idx.get(yt, 0) for yt in y_true])
                    else:
                        # Infer labels from unique values
                        unique_labels = np.unique(y_true)
                        label_to_idx = {label: idx for idx, label in enumerate(unique_labels)}
                        y_true_numeric = np.array([label_to_idx[yt] for yt in y_true])

                # Handle binary classification
                if y_proba.ndim == 2 and y_proba.shape[1] == 2:
                    y_proba_pos = y_proba[:, 1]
                elif y_proba.ndim == 1:
                    y_proba_pos = y_proba
                else:
                    # Multiclass - use first class for now
                    # TODO: Extend for multiclass support
                    y_proba_pos = y_proba[:, 0]
                    y_true_numeric = (y_true_numeric == 0).astype(int)

                if curve_type == 'roc':
                    fpr, tpr, _ = roc_curve(y_true_numeric, y_proba_pos)
                    roc_auc = auc(fpr, tpr)
                    aucs.append(roc_auc)

                    if show_individual_folds:
                        ax.plot(fpr, tpr, alpha=fold_alpha, color='gray',
                               label=f'Fold {fold_idx}' if fold_idx == 0 else None)

                    # Interpolate for mean calculation
                    interp_tpr = np.interp(mean_fpr, fpr, tpr)
                    interp_tpr[0] = 0.0
                    tprs.append(interp_tpr)

                else:  # pr
                    precision, recall, _ = precision_recall_curve(y_true_numeric, y_proba_pos)
                    ap = average_precision_score(y_true_numeric, y_proba_pos)
                    aps.append(ap)

                    if show_individual_folds:
                        ax.plot(recall, precision, alpha=fold_alpha, color='gray',
                               label=f'Fold {fold_idx}' if fold_idx == 0 else None)

                    # Interpolate for mean calculation (reverse recall for interpolation)
                    interp_precision = np.interp(mean_recall, recall[::-1], precision[::-1])
                    precisions.append(interp_precision)

            # Plot mean curve
            if show_mean:
                if curve_type == 'roc':
                    mean_tpr = np.mean(tprs, axis=0)
                    mean_tpr[-1] = 1.0
                    mean_auc = np.mean(aucs)
                    std_auc = np.std(aucs)

                    ax.plot(mean_fpr, mean_tpr, color='b', linewidth=2,
                           label=f'Mean ROC (AUC = {mean_auc:.3f} ± {std_auc:.3f})')

                    # Optional: Add confidence interval
                    std_tpr = np.std(tprs, axis=0)
                    tpr_upper = np.minimum(mean_tpr + std_tpr, 1)
                    tpr_lower = np.maximum(mean_tpr - std_tpr, 0)
                    ax.fill_between(mean_fpr, tpr_lower, tpr_upper,
                                   color='b', alpha=0.2, label='± 1 std. dev.')

                    # Chance line
                    ax.plot([0, 1], [0, 1], 'k--', alpha=0.5, label='Chance')

                    ax.set_xlabel('False Positive Rate', fontsize=12)
                    ax.set_ylabel('True Positive Rate', fontsize=12)
                    if title is None:
                        title = f'ROC Curves - Cross Validation (n={len(fold_predictions)} folds)'

                else:  # pr
                    mean_precision = np.mean(precisions, axis=0)
                    mean_ap = np.mean(aps)
                    std_ap = np.std(aps)

                    ax.plot(mean_recall, mean_precision, color='b', linewidth=2,
                           label=f'Mean PR (AP = {mean_ap:.3f} ± {std_ap:.3f})')

                    # Optional: Add confidence interval
                    std_precision = np.std(precisions, axis=0)
                    precision_upper = np.minimum(mean_precision + std_precision, 1)
                    precision_lower = np.maximum(mean_precision - std_precision, 0)
                    ax.fill_between(mean_recall, precision_lower, precision_upper,
                                   color='b', alpha=0.2, label='± 1 std. dev.')

                    ax.set_xlabel('Recall', fontsize=12)
                    ax.set_ylabel('Precision', fontsize=12)
                    if title is None:
                        title = f'Precision-Recall Curves - Cross Validation (n={len(fold_predictions)} folds)'

            ax.set_xlim([0.0, 1.0])
            ax.set_ylim([0.0, 1.05])
            ax.set_title(title, fontsize=14, fontweight='bold')
            ax.legend(loc='best', fontsize=10)
            ax.grid(True, alpha=0.3)
            ax.set_aspect('equal')

            plt.tight_layout()

            if save_path:
                from scitex.io import save as stx_io_save
                stx_io_save(fig, save_path, verbose=verbose or self.verbose, use_caller_path=False)

            return fig

        except Exception as e:
            warnings.warn(f"Failed to create CV aggregation plot: {e}", UserWarning)
            import traceback
            traceback.print_exc()
            return None


def safe_plot_wrapper(func):
    """Decorator to wrap plotting functions with error handling."""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            warnings.warn(f"Plotting failed: {e}", UserWarning)
            return None

    return wrapper

# EOF
