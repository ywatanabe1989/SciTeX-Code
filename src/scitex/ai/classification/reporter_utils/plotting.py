#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-22 02:28:36 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/ml/classification/reporter_utils/plotting.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/ml/classification/reporter_utils/plotting.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Plotting utilities for classification reporters.

Enhanced plotting with:
- Graceful error handling
- Fallback options when display is not available
- Optional plotting with proper disabling
- Better error messages
"""

import warnings
from pathlib import Path
from typing import Any, List, Optional, Union

import numpy as np

# Import plotting libraries with graceful fallbacks
try:
    # Set non-interactive backend if no display available
    import os

    import matplotlib

    if not os.environ.get("DISPLAY") and matplotlib.get_backend() != "Agg":
        matplotlib.use("Agg")

    import matplotlib.pyplot as plt
    import seaborn as sns

    PLOTTING_AVAILABLE = True
except ImportError:
    PLOTTING_AVAILABLE = False
    plt = None
    sns = None


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
        if not self.enabled:
            return None

        # Validate confusion matrix
        if confusion_matrix is None:
            return None

        # Handle dict wrapper from metric calculations
        if isinstance(confusion_matrix, dict):
            if "value" in confusion_matrix:
                confusion_matrix = confusion_matrix["value"]
            else:
                return None

        # Ensure it's a numpy array
        if not isinstance(confusion_matrix, np.ndarray):
            try:
                confusion_matrix = np.array(confusion_matrix)
            except:
                return None

        # Check dimensions
        if confusion_matrix.ndim != 2:
            warnings.warn(
                f"Confusion matrix must be 2D, got shape {confusion_matrix.shape}",
                UserWarning,
            )
            return None

        if confusion_matrix.size == 0:
            warnings.warn("Empty confusion matrix provided", UserWarning)
            return None

        try:
            fig, ax = plt.subplots(figsize=(8, 6))

            # Create heatmap
            if sns is not None:
                sns.heatmap(
                    confusion_matrix,
                    annot=True,
                    fmt="d",
                    cmap="Blues",
                    xticklabels=labels,
                    yticklabels=labels,
                    ax=ax,
                )
            else:
                # Fallback without seaborn
                im = ax.imshow(confusion_matrix, cmap="Blues")
                ax.set_xticks(range(len(labels or confusion_matrix.shape[1])))
                ax.set_yticks(range(len(labels or confusion_matrix.shape[0])))
                if labels:
                    ax.set_xticklabels(labels)
                    ax.set_yticklabels(labels)

                # Add text annotations
                for i in range(confusion_matrix.shape[0]):
                    for j in range(confusion_matrix.shape[1]):
                        ax.text(
                            j,
                            i,
                            str(confusion_matrix[i, j]),
                            ha="center",
                            va="center",
                        )

            ax.set_xlabel("Predicted")
            ax.set_ylabel("True")
            ax.set_title(title)

            if save_path:
                # save_path = Path(save_path)
                from scitex.io import save as stx_io_save

                stx_io_save(fig, save_path, verbose=verbose or self.verbose)
                # save_path.parent.mkdir(parents=True, exist_ok=True)
                # fig.savefig(save_path, dpi=300, bbox_inches="tight")

            plt.close(fig)  # Clean up
            return fig

        except Exception as e:
            warnings.warn(
                f"Failed to create confusion matrix plot: {e}", UserWarning
            )
            return None

    def create_roc_curve(
        self,
        y_true: np.ndarray,
        y_proba: np.ndarray,
        save_path: Optional[Union[str, Path]] = None,
        verbose: bool = True,
        title: str = "ROC Curve",
    ) -> Optional[Any]:
        """
        Create ROC curve plot with error handling.

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
        title : str, default "ROC Curve"
            Title for the plot

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

                fpr, tpr, _ = roc_curve(y_true, y_proba_pos)
                roc_auc = auc(fpr, tpr)

                fig, ax = plt.subplots(figsize=(8, 8))  # Square figure
                ax.plot(fpr, tpr, label=f"ROC Curve (AUC = {roc_auc:.3f})")
                ax.plot([0, 1], [0, 1], "k--", label="Random")
                ax.set_xlabel("False Positive Rate")
                ax.set_ylabel("True Positive Rate")
                ax.set_title(title)
                ax.set_xlim([0, 1])  # Set x range to [0,1]
                ax.set_ylim([0, 1])  # Set y range to [0,1]
                ax.set_aspect("equal")  # Equal aspect ratio
                ax.legend()
                ax.grid(True, alpha=0.3)

            else:
                # Multiclass - plot for each class
                fig, ax = plt.subplots(figsize=(10, 8))

                for i in range(y_proba.shape[1]):
                    y_true_binary = (y_true == i).astype(int)
                    fpr, tpr, _ = roc_curve(y_true_binary, y_proba[:, i])
                    roc_auc = auc(fpr, tpr)
                    ax.plot(fpr, tpr, label=f"Class {i} (AUC = {roc_auc:.3f})")

                ax.plot([0, 1], [0, 1], "k--", label="Random")
                ax.set_xlabel("False Positive Rate")
                ax.set_ylabel("True Positive Rate")
                ax.set_title("ROC Curves - Multiclass")
                ax.legend()
                ax.grid(True, alpha=0.3)

            if save_path:
                from scitex.io import save as stx_io_save

                stx_io_save(fig, save_path, verbose=verbose or self.verbose)
                # save_path = Path(save_path)
                # save_path.parent.mkdir(parents=True, exist_ok=True)
                # fig.savefig(save_path, dpi=300, bbox_inches="tight")

            plt.close(fig)  # Clean up
            return fig

        except Exception as e:
            warnings.warn(f"Failed to create ROC curve: {e}", UserWarning)
            return None

    def create_precision_recall_curve(
        self,
        y_true: np.ndarray,
        y_proba: np.ndarray,
        save_path: Optional[Union[str, Path]] = None,
        verbose: bool = True,
        title: str = "Precision-Recall Curve",
    ) -> Optional[Any]:
        """
        Create Precision-Recall curve plot with error handling.

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
        title : str, default "Precision-Recall Curve"
            Title for the plot

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
                ax.plot(
                    recall,
                    precision,
                    label=f"PR Curve (Average Precision (AP) = {avg_precision:.3f})",
                )
                ax.set_xlabel("Recall")
                ax.set_ylabel("Precision")
                ax.set_title(title)
                ax.set_xlim([0, 1])  # Set x range to [0,1]
                ax.set_ylim([0, 1])  # Set y range to [0,1]
                ax.set_aspect("equal")  # Equal aspect ratio
                ax.legend()
                ax.grid(True, alpha=0.3)

            else:
                # Multiclass not well-defined for PR curves, skip
                return None

            if save_path:
                from scitex.io import save as stx_io_save

                stx_io_save(fig, save_path)
                # save_path = Path(save_path)
                # save_path.parent.mkdir(parents=True, exist_ok=True)
                # fig.savefig(save_path, dpi=300, bbox_inches="tight")

            plt.close(fig)  # Clean up
            return fig

        except Exception as e:
            warnings.warn(f"Failed to create PR curve: {e}", UserWarning)
            return None

    def create_overall_roc_curve(
        self,
        y_true: np.ndarray,
        y_proba: np.ndarray,
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

                fpr, tpr, _ = roc_curve(y_true, y_proba_pos)
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
                from scitex.io import save as stx_io_save
                stx_io_save(fig, save_path, verbose=verbose or self.verbose)

            plt.close(fig)  # Clean up
            return fig

        except Exception as e:
            warnings.warn(f"Failed to create overall ROC curve: {e}", UserWarning)
            return None

    def create_overall_pr_curve(
        self,
        y_true: np.ndarray,
        y_proba: np.ndarray,
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
                
                ax.plot(
                    recall,
                    precision,
                    label=label,
                    linewidth=2
                )
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
                from scitex.io import save as stx_io_save
                stx_io_save(fig, save_path, verbose=verbose or self.verbose)

            plt.close(fig)  # Clean up
            return fig

        except Exception as e:
            warnings.warn(f"Failed to create overall PR curve: {e}", UserWarning)
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
