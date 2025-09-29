#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-22 15:10:54 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/ml/classification/reporters/_SingleClassificationReporter.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/ml/classification/reporters/_SingleClassificationReporter.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from pprint import pprint

"""
Improved Single Classification Reporter with unified API.

Enhanced version that addresses all identified issues:
- Unified API interface
- Lazy directory creation
- Numerical precision control
- Graceful plotting with error handling
- Consistent parameter names
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import numpy as np
import pandas as pd
from scitex.logging import getLogger

# Import base class and utilities
from ._BaseClassificationReporter import (BaseClassificationReporter,
                                          ReporterConfig)
# Import original metric calculation functions (these are good)
from .reporter_utils import (calc_balanced_accuracy,
                             calc_classification_report, calc_confusion_matrix,
                             calc_mcc, calc_pr_auc, calc_roc_auc)
from .reporter_utils.plotting import Plotter
from .reporter_utils.reporting import (create_summary_statistics,
                                       generate_latex_report,
                                       generate_markdown_report,
                                       generate_org_report)
from .reporter_utils.storage import MetricStorage, save_metric

logger = getLogger(__name__)


class SingleTaskClassificationReporter(BaseClassificationReporter):
    """
    Improved single-task classification reporter with unified API.

    Key improvements:
    - Inherits from BaseClassificationReporter for consistent API
    - Lazy directory creation (no empty folders)
    - Numerical precision control
    - Graceful plotting with proper error handling
    - Consistent parameter names across all methods

    Parameters
    ----------
    output_dir : Union[str, Path]
        Base directory for outputs. If None, creates timestamped directory.
    config : ReporterConfig, optional
        Configuration object for advanced settings
    **kwargs
        Additional arguments passed to base class
    """

    def __init__(
        self,
        output_dir: Union[str, Path],
        config: Optional[ReporterConfig] = None,
        verbose: bool = True,
        **kwargs,
    ):
        # Use config or create default
        if config is None:
            config = ReporterConfig()

        # Initialize base class with config settings
        super().__init__(
            output_dir=output_dir,
            precision=config.precision,
            **kwargs,
        )

        self.config = config
        self.session_config = (
            None  # Will store SciTeX session CONFIG if provided
        )
        self.storage = MetricStorage(self.output_dir, precision=self.precision)
        self.plotter = Plotter(enable_plotting=True)

        # Track calculated metrics for summary
        self.fold_metrics: Dict[int, Dict[str, Any]] = {}

        # Store all predictions for overall curves
        self.all_predictions: List[Dict[str, Any]] = []

    def set_session_config(self, config: Any) -> None:
        """
        Set the SciTeX session CONFIG object for inclusion in reports.

        Parameters
        ----------
        config : Any
            The SciTeX session CONFIG object
        """
        self.session_config = config

    def calculate_metrics(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_proba: Optional[np.ndarray] = None,
        labels: Optional[List[str]] = None,
        fold: Optional[int] = None,
        verbose=True,
    ) -> Dict[str, Any]:
        """
        Calculate and save classification metrics using unified API.

        Parameters
        ----------
        y_true : np.ndarray
            True class labels
        y_pred : np.ndarray
            Predicted class labels
        y_proba : np.ndarray, optional
            Prediction probabilities (required for AUC metrics)
        labels : List[str], optional
            Class labels for display
        fold : int, optional
            Fold index for cross-validation

        Returns
        -------
        Dict[str, Any]
            Dictionary of calculated metrics
        """
        if verbose:
            if fold:
                print()
                logger.info(f"Calculating metrics for fold #{fold:02d}...")
            else:
                logger.info(f"Calculating metrics...")

        # Validate inputs
        if len(y_true) != len(y_pred):
            raise ValueError("y_true and y_pred must have same length")

        if y_proba is not None and len(y_true) != len(y_proba):
            raise ValueError("y_true and y_proba must have same length")

        # Set default fold index
        if fold is None:
            fold = 0

        # Set default labels if not provided
        if labels is None:
            unique_labels = sorted(np.unique(np.concatenate([y_true, y_pred])))
            labels = [f"Class_{i}" for i in unique_labels]

        # Calculate all metrics
        metrics = {}

        # Core metrics (always calculated) - pass fold to all metrics
        metrics["balanced_accuracy"] = calc_balanced_accuracy(
            y_true, y_pred, fold=fold
        )
        metrics["mcc"] = calc_mcc(y_true, y_pred, fold=fold)
        metrics["confusion_matrix"] = calc_confusion_matrix(
            y_true, y_pred, fold=fold
        )
        metrics["classification_report"] = calc_classification_report(
            y_true, y_pred, labels, fold=fold
        )

        # AUC metrics (only if probabilities available)
        if y_proba is not None:
            try:
                metrics["roc_auc"] = calc_roc_auc(y_true, y_proba, fold=fold)
                metrics["pr_auc"] = calc_pr_auc(y_true, y_proba, fold=fold)
            except Exception as e:
                print(f"Warning: Could not calculate AUC metrics: {e}")

        # Round all numerical values
        metrics = self._round_numeric(metrics)

        # Add labels to metrics for later use
        metrics["labels"] = labels

        if verbose:
            logger.info(f"Metrics calculated:")
            pprint(metrics)

        # Store metrics for summary
        self.fold_metrics[fold] = metrics.copy()

        # Store predictions for overall curves
        if y_proba is not None:
            self.all_predictions.append(
                {
                    "fold": fold,
                    "y_true": y_true.copy(),
                    "y_proba": y_proba.copy(),
                }
            )

        # Save metrics if requested
        self._save_fold_metrics(metrics, fold, labels)

        # Generate plots if requested
        self._create_plots(y_true, y_pred, y_proba, labels, fold, metrics)

        return metrics

    def _save_fold_metrics(
        self, metrics: Dict[str, Any], fold: int, labels: List[str]
    ) -> None:
        """Save metrics for a specific fold in shallow directory structure."""
        fold_dir = f"fold_{fold:02d}"

        # Extract metric values for filenames
        balanced_acc = self._extract_metric_value(
            metrics.get("balanced_accuracy")
        )
        mcc_value = self._extract_metric_value(metrics.get("mcc"))
        roc_auc_value = self._extract_metric_value(metrics.get("roc_auc"))
        pr_auc_value = self._extract_metric_value(metrics.get("pr_auc"))

        # Save individual metrics with values in filenames
        for metric_name, metric_value in metrics.items():
            # Extract actual value if it's a wrapped dict with 'value' key
            if isinstance(metric_value, dict) and "value" in metric_value:
                actual_value = metric_value["value"]
            else:
                actual_value = metric_value

            if metric_name == "confusion_matrix":
                # Save confusion matrix as CSV with proper formatting and metric in filename
                cm_df = pd.DataFrame(
                    actual_value,
                    index=[f"True_{label}" for label in labels],
                    columns=[f"Pred_{label}" for label in labels],
                )

                # Create filename with balanced accuracy
                if balanced_acc is not None:
                    cm_filename = f"confusion_matrix_fold_{fold:02d}_bacc_{balanced_acc:.3f}.csv"
                else:
                    cm_filename = f"confusion_matrix_fold_{fold:02d}.csv"

                # Ensure index is saved in CSV
                self.storage.save(cm_df, f"{fold_dir}/{cm_filename}")

            elif metric_name == "classification_report":
                # Save classification report with consistent naming
                report_filename = f"classification_report_fold_{fold:02d}.csv"
                if isinstance(actual_value, pd.DataFrame):
                    # Already a DataFrame
                    self.storage.save(
                        actual_value, f"{fold_dir}/{report_filename}"
                    )
                elif isinstance(actual_value, dict):
                    # Try to create DataFrame from dict
                    try:
                        report_df = pd.DataFrame(actual_value).transpose()
                        self.storage.save(
                            report_df, f"{fold_dir}/{report_filename}"
                        )
                    except:
                        # Save as JSON if DataFrame conversion fails
                        report_filename = (
                            f"classification_report_fold_{fold:02d}.json"
                        )
                        self.storage.save(
                            actual_value,
                            f"{fold_dir}/{report_filename}",
                        )
                else:
                    # String or other format
                    report_filename = (
                        f"classification_report_fold_{fold:02d}.txt"
                    )
                    self.storage.save(
                        actual_value, f"{fold_dir}/{report_filename}"
                    )

            elif (
                metric_name == "balanced_accuracy" and balanced_acc is not None
            ):
                # Save with value in filename
                filename = f"balanced_accuracy_fold_{fold:02d}_{balanced_acc:.3f}.json"
                save_metric(
                    actual_value,
                    self.output_dir / f"{fold_dir}/{filename}",
                    fold=fold,
                    precision=self.precision,
                )
            elif metric_name == "mcc" and mcc_value is not None:
                # Save with value in filename
                filename = f"mcc_fold_{fold:02d}_{mcc_value:.3f}.json"
                save_metric(
                    actual_value,
                    self.output_dir / f"{fold_dir}/{filename}",
                    fold=fold,
                    precision=self.precision,
                )
            elif metric_name == "roc_auc" and roc_auc_value is not None:
                # Save with value in filename
                filename = f"roc_auc_fold_{fold:02d}_{roc_auc_value:.3f}.json"
                save_metric(
                    actual_value,
                    self.output_dir / f"{fold_dir}/{filename}",
                    fold=fold,
                    precision=self.precision,
                )
            elif metric_name == "pr_auc" and pr_auc_value is not None:
                # Save with value in filename
                filename = f"pr_auc_fold_{fold:02d}_{pr_auc_value:.3f}.json"
                save_metric(
                    actual_value,
                    self.output_dir / f"{fold_dir}/{filename}",
                    fold=fold,
                    precision=self.precision,
                )

    def _extract_metric_value(self, metric_data: Any) -> Optional[float]:
        """Extract numeric value from metric data."""
        if metric_data is None:
            return None
        if isinstance(metric_data, dict) and "value" in metric_data:
            return float(metric_data["value"])
        if isinstance(metric_data, (int, float, np.number)):
            return float(metric_data)
        return None

    def _save_curve_data(
        self,
        y_true: np.ndarray,
        y_proba: Optional[np.ndarray],
        fold: int,
        metrics: Dict[str, Any],
    ) -> None:
        """Save ROC and PR curve data as CSV files with metric values in filenames."""
        if y_proba is None:
            return

        from sklearn.metrics import (auc, average_precision_score,
                                     precision_recall_curve, roc_curve)

        fold_dir = f"fold_{fold:02d}"

        # Handle binary vs multiclass
        if y_proba.ndim == 1 or y_proba.shape[1] == 2:
            # Binary classification
            if y_proba.ndim == 2:
                y_proba_pos = y_proba[:, 1]
            else:
                y_proba_pos = y_proba

            # ROC curve data
            fpr, tpr, _ = roc_curve(y_true, y_proba_pos)
            roc_auc = auc(fpr, tpr)

            # Create ROC curve DataFrame with just FPR and TPR columns
            roc_df = pd.DataFrame({"FPR": fpr, "TPR": tpr})

            # Save with AUC value in filename
            roc_filename = f"roc_curve_fold_{fold:02d}_auc_{roc_auc:.3f}.csv"
            self.storage.save(roc_df, f"{fold_dir}/{roc_filename}")

            # PR curve data
            precision, recall, _ = precision_recall_curve(y_true, y_proba_pos)
            avg_precision = average_precision_score(y_true, y_proba_pos)

            # Create PR curve DataFrame with Recall and Precision columns
            pr_df = pd.DataFrame({"Recall": recall, "Precision": precision})

            # Save with AP value in filename
            pr_filename = (
                f"pr_curve_fold_{fold:02d}_ap_{avg_precision:.3f}.csv"
            )
            self.storage.save(pr_df, f"{fold_dir}/{pr_filename}")

    def _create_plots(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_proba: Optional[np.ndarray],
        labels: List[str],
        fold: int,
        metrics: Dict[str, Any],
    ) -> None:
        """Create and save plots with metric-based filenames in unified structure."""
        # Use unified fold directory
        fold_dir = self._create_subdir_if_needed(f"fold_{fold:02d}")
        fold_dir.mkdir(parents=True, exist_ok=True)

        # Save curve data for external plotting
        self._save_curve_data(y_true, y_proba, fold, metrics)

        # Confusion matrix plot with metric in filename
        if "confusion_matrix" in metrics:
            # Extract actual confusion matrix value if wrapped in dict
            cm_data = metrics["confusion_matrix"]
            if isinstance(cm_data, dict) and "value" in cm_data:
                cm_data = cm_data["value"]

            # Get balanced accuracy for title and filename
            balanced_acc = metrics.get("balanced_accuracy", {})
            if isinstance(balanced_acc, dict) and "value" in balanced_acc:
                balanced_acc = balanced_acc["value"]
            elif isinstance(balanced_acc, (float, np.floating)):
                balanced_acc = float(balanced_acc)
            else:
                balanced_acc = None

            # Create title with balanced accuracy and filename with fold and metric
            if balanced_acc is not None:
                title = f"Confusion Matrix (Fold {fold:02d}) - Balanced Acc: {balanced_acc:.3f}"
                filename = f"confusion_matrix_fold_{fold:02d}_bacc_{balanced_acc:.3f}.jpg"
            else:
                title = f"Confusion Matrix (Fold {fold:02d})"
                filename = f"confusion_matrix_fold_{fold:02d}.jpg"

            self.plotter.create_confusion_matrix_plot(
                cm_data,
                labels=labels,
                save_path=fold_dir / filename,
                title=title,
            )

        # ROC curve with AUC in filename (if probabilities available)
        if y_proba is not None:
            # Get AUC for filename
            roc_auc = metrics.get("roc_auc", {})
            if isinstance(roc_auc, dict) and "value" in roc_auc:
                roc_auc_val = roc_auc["value"]
                roc_filename = (
                    f"roc_curve_fold_{fold:02d}_auc_{roc_auc_val:.3f}.jpg"
                )
            else:
                roc_filename = f"roc_curve_fold_{fold:02d}.jpg"

            self.plotter.create_roc_curve(
                y_true,
                y_proba,
                save_path=fold_dir / roc_filename,
                title=f"ROC Curve (Fold {fold:02d})",
            )

            # PR curve with AP in filename
            pr_auc = metrics.get("pr_auc", {})
            if isinstance(pr_auc, dict) and "value" in pr_auc:
                pr_auc_val = pr_auc["value"]
                pr_filename = (
                    f"pr_curve_fold_{fold:02d}_ap_{pr_auc_val:.3f}.jpg"
                )
            else:
                pr_filename = f"pr_curve_fold_{fold:02d}.jpg"

            self.plotter.create_precision_recall_curve(
                y_true,
                y_proba,
                save_path=fold_dir / pr_filename,
                title=f"Precision-Recall Curve (Fold {fold:02d})",
            )

    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary of all calculated metrics across folds.

        Returns
        -------
        Dict[str, Any]
            Summary statistics across all folds
        """
        if not self.fold_metrics:
            return {"error": "No metrics calculated yet"}

        summary = {
            "output_dir": str(self.output_dir),
            "total_folds": len(self.fold_metrics),
            "metrics_summary": {},
        }

        # Aggregate confusion matrices across all folds
        confusion_matrices = []
        for fold_metrics in self.fold_metrics.values():
            if "confusion_matrix" in fold_metrics:
                cm_data = fold_metrics["confusion_matrix"]
                # Extract actual value if wrapped in dict
                if isinstance(cm_data, dict) and "value" in cm_data:
                    cm_data = cm_data["value"]
                if cm_data is not None:
                    confusion_matrices.append(cm_data)

        if confusion_matrices:
            # Sum all confusion matrices to get overall counts
            overall_cm = np.sum(confusion_matrices, axis=0)
            summary["overall_confusion_matrix"] = overall_cm.tolist()

            # Also calculate normalized version (as percentages)
            overall_cm_normalized = overall_cm / overall_cm.sum()
            summary["overall_confusion_matrix_normalized"] = (
                self._round_numeric(overall_cm_normalized.tolist())
            )

        # Calculate summary statistics for scalar metrics
        scalar_metrics = ["balanced_accuracy", "mcc", "roc_auc", "pr_auc"]

        for metric_name in scalar_metrics:
            values = []
            for fold_metrics in self.fold_metrics.values():
                if metric_name in fold_metrics:
                    # Extract actual value if it's wrapped in dict
                    metric_val = fold_metrics[metric_name]
                    if isinstance(metric_val, dict) and "value" in metric_val:
                        values.append(metric_val["value"])
                    else:
                        values.append(metric_val)

            if values:
                values = np.array(values)
                summary["metrics_summary"][metric_name] = {
                    "mean": self._round_numeric(np.mean(values)),
                    "std": self._round_numeric(np.std(values)),
                    "min": self._round_numeric(np.min(values)),
                    "max": self._round_numeric(np.max(values)),
                    "values": self._round_numeric(values.tolist()),
                }

        return summary

    def create_cv_summary_curves(self, summary: Dict[str, Any]) -> None:
        """
        Create CV summary ROC and PR curves from aggregated predictions.
        """
        if not self.all_predictions:
            logger.warning("No predictions stored for CV summary curves")
            return

        # Aggregate all predictions
        all_y_true = np.concatenate(
            [p["y_true"] for p in self.all_predictions]
        )
        all_y_proba = np.concatenate(
            [p["y_proba"] for p in self.all_predictions]
        )

        # Get per-fold metrics for mean and std
        roc_values = []
        pr_values = []
        for metrics in self.fold_metrics.values():
            if "roc_auc" in metrics:
                val = metrics["roc_auc"]
                if isinstance(val, dict) and "value" in val:
                    roc_values.append(val["value"])
                else:
                    roc_values.append(val)
            if "pr_auc" in metrics:
                val = metrics["pr_auc"]
                if isinstance(val, dict) and "value" in val:
                    pr_values.append(val["value"])
                else:
                    pr_values.append(val)

        # Calculate mean and std
        n_folds = len(self.fold_metrics)
        if roc_values:
            roc_mean = np.mean(roc_values)
            roc_std = np.std(roc_values)
        else:
            from .reporter_utils.metrics import calc_roc_auc

            overall_roc = calc_roc_auc(all_y_true, all_y_proba)
            roc_mean = overall_roc["value"]
            roc_std = 0.0

        if pr_values:
            pr_mean = np.mean(pr_values)
            pr_std = np.std(pr_values)
        else:
            from .reporter_utils.metrics import calc_pr_auc

            overall_pr = calc_pr_auc(all_y_true, all_y_proba)
            pr_mean = overall_pr["value"]
            pr_std = 0.0

        # Create cv_summary directory
        cv_summary_dir = self._create_subdir_if_needed("cv_summary")
        cv_summary_dir.mkdir(parents=True, exist_ok=True)

        # Save CV summary curve data
        self._save_cv_summary_curve_data(
            all_y_true,
            all_y_proba,
            roc_mean,
            roc_std,
            pr_mean,
            pr_std,
            n_folds,
        )

        # ROC Curve with mean±std and n_folds in filename
        roc_title = f"ROC Curve (CV Summary) - AUC: {roc_mean:.3f} ± {roc_std:.3f} (n={n_folds})"
        roc_filename = f"roc_curve_cv_summary_auc_{roc_mean:.3f}_{roc_std:.3f}_n{n_folds}.jpg"
        self.plotter.create_overall_roc_curve(
            all_y_true,
            all_y_proba,
            save_path=cv_summary_dir / roc_filename,
            title=roc_title,
            auc_mean=roc_mean,
            auc_std=roc_std,
        )

        # PR Curve with mean±std and n_folds in filename
        pr_title = f"Precision-Recall Curve (CV Summary) - AP: {pr_mean:.3f} ± {pr_std:.3f} (n={n_folds})"
        pr_filename = (
            f"pr_curve_cv_summary_ap_{pr_mean:.3f}_{pr_std:.3f}_n{n_folds}.jpg"
        )
        self.plotter.create_overall_pr_curve(
            all_y_true,
            all_y_proba,
            save_path=cv_summary_dir / pr_filename,
            title=pr_title,
            ap_mean=pr_mean,
            ap_std=pr_std,
        )

        logger.info(
            f"Created CV summary ROC curve: AUC = {roc_mean:.3f} ± {roc_std:.3f} (n={n_folds})"
        )
        logger.info(
            f"Created CV summary PR curve: AP = {pr_mean:.3f} ± {pr_std:.3f} (n={n_folds})"
        )

    def _save_cv_summary_curve_data(
        self,
        y_true: np.ndarray,
        y_proba: np.ndarray,
        roc_mean: float,
        roc_std: float,
        pr_mean: float,
        pr_std: float,
        n_folds: int,
    ) -> None:
        """Save CV summary ROC and PR curve data as CSV files with metric values in filenames."""
        from sklearn.metrics import (auc, average_precision_score,
                                     precision_recall_curve, roc_curve)

        cv_summary_dir = "cv_summary"

        # Handle binary vs multiclass
        if y_proba.ndim == 1 or y_proba.shape[1] == 2:
            # Binary classification
            if y_proba.ndim == 2:
                y_proba_pos = y_proba[:, 1]
            else:
                y_proba_pos = y_proba

            # ROC curve data
            fpr, tpr, _ = roc_curve(y_true, y_proba_pos)
            roc_auc = auc(fpr, tpr)

            # Create ROC curve DataFrame with just FPR and TPR columns
            roc_df = pd.DataFrame({"FPR": fpr, "TPR": tpr})

            # Save with mean±std and n_folds in filename
            roc_filename = f"roc_curve_cv_summary_auc_{roc_mean:.3f}_{roc_std:.3f}_n{n_folds}.csv"
            self.storage.save(roc_df, f"{cv_summary_dir}/{roc_filename}")

            # PR curve data
            precision, recall, _ = precision_recall_curve(y_true, y_proba_pos)
            avg_precision = average_precision_score(y_true, y_proba_pos)

            # Create PR curve DataFrame with Recall and Precision columns
            pr_df = pd.DataFrame({"Recall": recall, "Precision": precision})

            # Save with mean±std and n_folds in filename
            pr_filename = f"pr_curve_cv_summary_ap_{pr_mean:.3f}_{pr_std:.3f}_n{n_folds}.csv"
            self.storage.save(pr_df, f"{cv_summary_dir}/{pr_filename}")

    def save_cv_summary_confusion_matrix(
        self, summary: Dict[str, Any]
    ) -> None:
        """
        Save and plot the CV summary confusion matrix.

        Parameters
        ----------
        summary : Dict[str, Any]
            Summary dictionary containing overall_confusion_matrix
        """
        # Aggregate confusion matrices across all folds
        confusion_matrices = []
        for fold_metrics in self.fold_metrics.values():
            if "confusion_matrix" in fold_metrics:
                cm_data = fold_metrics["confusion_matrix"]
                # Extract actual value if wrapped in dict
                if isinstance(cm_data, dict) and "value" in cm_data:
                    cm_data = cm_data["value"]
                if cm_data is not None:
                    confusion_matrices.append(cm_data)

        if not confusion_matrices:
            return

        # Sum all confusion matrices to get overall counts
        overall_cm = np.sum(confusion_matrices, axis=0)

        # Get labels from one of the folds
        labels = None
        for fold_metrics in self.fold_metrics.values():
            # Labels are stored directly in fold_metrics now
            if "labels" in fold_metrics:
                labels = fold_metrics["labels"]
                break
            # Fallback: check if labels are in confusion_matrix dict
            elif "confusion_matrix" in fold_metrics:
                cm_data = fold_metrics["confusion_matrix"]
                if isinstance(cm_data, dict) and "labels" in cm_data:
                    labels = cm_data["labels"]
                    break

        # Save as CSV with labels in cv_summary directory
        cv_summary_dir = self._create_subdir_if_needed("cv_summary")
        cv_summary_dir.mkdir(parents=True, exist_ok=True)

        # Get balanced accuracy stats for filename
        balanced_acc_mean = None
        balanced_acc_std = None
        n_folds = len(self.fold_metrics)
        if "metrics_summary" in summary:
            if "balanced_accuracy" in summary["metrics_summary"]:
                balanced_acc_stats = summary["metrics_summary"][
                    "balanced_accuracy"
                ]
                balanced_acc_mean = balanced_acc_stats.get("mean")
                balanced_acc_std = balanced_acc_stats.get("std")

        # Create filename with mean±std and n_folds
        if balanced_acc_mean is not None and balanced_acc_std is not None:
            cm_filename = f"confusion_matrix_cv_summary_bacc_{balanced_acc_mean:.3f}_{balanced_acc_std:.3f}_n{n_folds}.csv"
        else:
            cm_filename = f"confusion_matrix_cv_summary_n{n_folds}.csv"

        if labels:
            cm_df = pd.DataFrame(
                overall_cm,
                index=[f"True_{label}" for label in labels],
                columns=[f"Pred_{label}" for label in labels],
            )
        else:
            cm_df = pd.DataFrame(overall_cm)

        # Save with proper filename
        self.storage.save(cm_df, f"cv_summary/{cm_filename}")

        # Create plot for CV summary confusion matrix
        cv_summary_dir = self._create_subdir_if_needed("cv_summary")
        cv_summary_dir.mkdir(parents=True, exist_ok=True)

        # Calculate balanced accuracy mean and std for overall confusion matrix title
        balanced_acc_mean = None
        balanced_acc_std = None
        if "metrics_summary" in self.get_summary():
            metrics_summary = self.get_summary()["metrics_summary"]
            if "balanced_accuracy" in metrics_summary:
                balanced_acc_stats = metrics_summary["balanced_accuracy"]
                balanced_acc_mean = balanced_acc_stats.get("mean")
                balanced_acc_std = balanced_acc_stats.get("std")

        # Create title with balanced accuracy stats and filename with mean±std and n_folds
        if balanced_acc_mean is not None and balanced_acc_std is not None:
            title = f"Confusion Matrix (CV Summary) - Balanced Acc: {balanced_acc_mean:.3f} ± {balanced_acc_std:.3f} (n={n_folds})"
            filename = f"confusion_matrix_cv_summary_bacc_{balanced_acc_mean:.3f}_{balanced_acc_std:.3f}_n{n_folds}.jpg"
        else:
            title = f"Confusion Matrix (CV Summary) (n={n_folds})"
            filename = f"confusion_matrix_cv_summary_n{n_folds}.jpg"

        # Create the plot with enhanced title
        self.plotter.create_confusion_matrix_plot(
            overall_cm,
            labels=labels,
            save_path=cv_summary_dir / filename,
            title=title,
        )

    def generate_reports(self) -> Dict[str, Path]:
        """
        Generate comprehensive reports in multiple formats.

        Returns
        -------
        Dict[str, Path]
            Paths to generated report files
        """
        # Prepare results dictionary for report generation
        results = {
            "config": {
                "n_folds": len(self.fold_metrics),
                "output_dir": str(self.output_dir),
            },
            "session_config": self.session_config,  # Pass the SciTeX CONFIG
            "summary": {},
            "folds": [],
            "plots": {},
        }

        # Get summary statistics
        summary = self.get_summary()

        # Extract summary statistics for reporting
        if "metrics_summary" in summary:
            results["summary"] = summary["metrics_summary"]

        # Add per-fold results
        for fold, fold_data in self.fold_metrics.items():
            fold_result = {"fold_id": fold}
            fold_result.update(fold_data)
            results["folds"].append(fold_result)

        # Add plot references with unified structure
        # CV summary plots in cv_summary directory
        cv_summary_dir = self.output_dir / "cv_summary"
        if cv_summary_dir.exists():
            for plot_file in cv_summary_dir.glob("*.jpg"):
                plot_key = f"cv_summary_{plot_file.stem}"
                results["plots"][plot_key] = str(
                    plot_file.relative_to(self.output_dir)
                )

        # Per-fold plots in fold directories
        for fold_dir in sorted(self.output_dir.glob("fold_*")):
            fold_num = fold_dir.name.replace("fold_", "")
            for plot_file in fold_dir.glob("*.jpg"):
                plot_key = f"fold_{fold_num}_{plot_file.stem}"
                results["plots"][plot_key] = str(
                    plot_file.relative_to(self.output_dir)
                )

        # Generate reports
        reports_dir = self._create_subdir_if_needed("reports")
        generated_files = {}

        # Org-mode report (primary format) - will generate other formats via pandoc
        org_path = reports_dir / "classification_report.org"
        generate_org_report(
            results, org_path, include_plots=True, convert_formats=True
        )
        generated_files["org"] = org_path
        logger.info(f"Generated org-mode report: {org_path}")

        # Note: Markdown, HTML, LaTeX, and DOCX are now generated via pandoc from org
        # This ensures consistency across all formats

        # Try to compile LaTeX to PDF
        try:
            import shutil
            import subprocess

            if shutil.which("pdflatex"):
                # Change to reports directory for compilation
                original_dir = Path.cwd()
                try:
                    import os

                    os.chdir(reports_dir)

                    # Run pdflatex twice for proper references
                    for _ in range(2):
                        result = subprocess.run(
                            [
                                "pdflatex",
                                "-interaction=nonstopmode",
                                "classification_report.tex",
                            ],
                            capture_output=True,
                            text=True,
                            timeout=30,
                        )

                    pdf_path = reports_dir / "classification_report.pdf"
                    if pdf_path.exists():
                        generated_files["pdf"] = pdf_path
                        logger.info(f"Generated PDF report: {pdf_path}")

                        # Clean up LaTeX auxiliary files
                        for ext in [".aux", ".log", ".out", ".toc"]:
                            aux_file = (
                                reports_dir / f"classification_report{ext}"
                            )
                            if aux_file.exists():
                                aux_file.unlink()
                finally:
                    os.chdir(original_dir)
            else:
                logger.warning("pdflatex not found. Skipping PDF generation.")
        except Exception as e:
            logger.warning(f"Could not generate PDF report: {e}")

        # Skip paper_exports - all data is already available in fold_XX/ and cv_summary/
        # with descriptive filenames perfect for sharing

        return generated_files

    def save_summary(
        self, filename: str = "cv_summary/summary.json", verbose: bool = True
    ) -> Path:
        """
        Save summary to file, create CV summary visualizations, and generate reports.

        Parameters
        ----------
        filename : str, default "cv_summary/summary.json"
            Filename for summary (now in cv_summary directory)

        Returns
        -------
        Path
            Path to saved summary file
        """
        summary = self.get_summary()

        # Try to load and include configuration
        try:
            # Try different possible locations for CONFIG.yaml
            possible_paths = [
                self.output_dir.parent
                / "CONFIGS"
                / "CONFIG.yaml",  # ../CONFIGS/CONFIG.yaml
                self.output_dir.parent.parent
                / "CONFIGS"
                / "CONFIG.yaml",  # ../../CONFIGS/CONFIG.yaml
                self.output_dir
                / "CONFIGS"
                / "CONFIG.yaml",  # ./CONFIGS/CONFIG.yaml
            ]

            config_path = None
            for path in possible_paths:
                if path.exists():
                    config_path = path
                    break

            if config_path and config_path.exists():
                import yaml

                with open(config_path, "r") as config_file:
                    config_data = yaml.safe_load(config_file)
                    summary["experiment_configuration"] = config_data
        except Exception as e:
            logger.warning(f"Could not load CONFIG.yaml: {e}")

        # Save CV summary metrics with proper filenames
        self._save_cv_summary_metrics(summary)

        # Save and plot CV summary confusion matrix
        self.save_cv_summary_confusion_matrix(summary)

        # Create CV summary ROC and PR curves
        self.create_cv_summary_curves(summary)

        # Save CV summary classification report
        self._save_cv_summary_classification_report(summary)

        # Generate comprehensive reports in multiple formats
        self.generate_reports()

        # Ensure cv_summary directory exists
        cv_summary_dir = self._create_subdir_if_needed("cv_summary")
        cv_summary_dir.mkdir(parents=True, exist_ok=True)

        if verbose:
            print()
            logger.info("Summary:")
            pprint(summary)

        # Save summary in cv_summary directory
        return self.storage.save(summary, "cv_summary/summary.json")

    def _save_cv_summary_metrics(self, summary: Dict[str, Any]) -> None:
        """
        Save individual CV summary metrics with mean/std/n_folds in filenames.
        """
        if "metrics_summary" not in summary:
            return

        n_folds = len(self.fold_metrics)
        cv_summary_dir = "cv_summary"

        for metric_name, stats in summary["metrics_summary"].items():
            if isinstance(stats, dict) and "mean" in stats:
                mean_val = stats.get("mean", 0)
                std_val = stats.get("std", 0)

                # Create filename with mean_std_n format
                filename = f"{metric_name}_mean_{mean_val:.3f}_std_{std_val:.3f}_n{n_folds}.json"

                # Save metric statistics
                self.storage.save(stats, f"{cv_summary_dir}/{filename}")

    def _save_cv_summary_classification_report(
        self, summary: Dict[str, Any]
    ) -> None:
        """
        Save CV summary classification report with mean ± std (n_folds=X) format.
        """
        n_folds = len(self.fold_metrics)
        cv_summary_dir = "cv_summary"

        # Collect classification reports from all folds
        all_reports = []
        for fold_metrics in self.fold_metrics.values():
            if "classification_report" in fold_metrics:
                report = fold_metrics["classification_report"]
                if isinstance(report, dict) and "value" in report:
                    report = report["value"]
                if isinstance(report, dict):
                    all_reports.append(report)

        if not all_reports:
            return

        # Calculate mean and std for each metric in the classification report
        summary_report = {}

        # Get all class labels (excluding summary rows)
        all_classes = set()
        for report in all_reports:
            all_classes.update(
                [
                    k
                    for k in report.keys()
                    if k not in ["accuracy", "macro avg", "weighted avg"]
                ]
            )

        # Process each class
        for cls in sorted(all_classes):
            cls_metrics = {
                "precision": [],
                "recall": [],
                "f1-score": [],
                "support": [],
            }

            for report in all_reports:
                if cls in report:
                    for metric in [
                        "precision",
                        "recall",
                        "f1-score",
                        "support",
                    ]:
                        if metric in report[cls]:
                            cls_metrics[metric].append(report[cls][metric])

            summary_report[cls] = {}
            for metric, values in cls_metrics.items():
                if values:
                    if metric == "support":
                        # Support is usually the same across folds
                        summary_report[cls][metric] = int(np.mean(values))
                    else:
                        mean_val = np.mean(values)
                        std_val = np.std(values)
                        summary_report[cls][
                            metric
                        ] = f"{mean_val:.3f} ± {std_val:.3f} (n={n_folds})"

        # Process summary rows (macro avg, weighted avg)
        for avg_type in ["macro avg", "weighted avg"]:
            avg_metrics = {"precision": [], "recall": [], "f1-score": []}

            for report in all_reports:
                if avg_type in report:
                    for metric in ["precision", "recall", "f1-score"]:
                        if metric in report[avg_type]:
                            avg_metrics[metric].append(
                                report[avg_type][metric]
                            )

            if any(avg_metrics.values()):
                summary_report[avg_type] = {}
                for metric, values in avg_metrics.items():
                    if values:
                        mean_val = np.mean(values)
                        std_val = np.std(values)
                        summary_report[avg_type][
                            metric
                        ] = f"{mean_val:.3f} ± {std_val:.3f} (n={n_folds})"

        # Convert to DataFrame for better visualization
        if summary_report:
            report_df = pd.DataFrame(summary_report).T

            # Save as CSV
            self.storage.save(
                report_df,
                f"{cv_summary_dir}/classification_report_cv_summary.csv",
            )

    def save(
        self,
        data: Any,
        relative_path: Union[str, Path],
        fold: Optional[int] = None,
    ) -> Path:
        """
        Save custom data with automatic fold organization.

        Parameters
        ----------
        data : Any
            Custom data to save (any format supported by stx.io.save)
        relative_path : Union[str, Path]
            Relative path from output_dir or fold directory. Examples:
            - When fold is provided: "custom_metrics.json" → "fold_00/custom_metrics.json"
            - When fold is None: "cv_summary/results.csv" → "cv_summary/results.csv"
        fold : Optional[int], default None
            If provided, automatically prepends "fold_{fold:02d}/" to the path

        Returns
        -------
        Path
            Absolute path to the saved file

        Examples
        --------
        >>> # Save custom metrics for fold 0 (automatic fold directory)
        >>> reporter.save(
        ...     {"metric1": 0.95, "metric2": 0.87},
        ...     "custom_metrics.json",
        ...     fold=0
        ... )  # Saves to: fold_00/custom_metrics.json

        >>> # Save to cv_summary (no fold)
        >>> reporter.save(
        ...     df_results,
        ...     "cv_summary/final_analysis.csv"
        ... )

        >>> # Save to reports directory
        >>> reporter.save(
        ...     report_content,
        ...     "reports/analysis.md"
        ... )
        """
        # Automatically prepend fold directory if fold is provided
        if fold is not None:
            relative_path = f"fold_{fold:02d}/{relative_path}"

        # Use the existing storage.save method which already handles everything
        return self.storage.save(data, relative_path)

    def __repr__(self) -> str:
        fold_count = len(self.fold_metrics)
        return (
            f"SingleTaskClassificationReporter("
            f"folds={fold_count}, "
            f"output_dir='{self.output_dir}')"
        )

# EOF
