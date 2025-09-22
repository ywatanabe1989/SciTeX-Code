#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-22 01:50:08 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/ml/classification/_BaseClassificationReporter.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/ml/classification/_BaseClassificationReporter.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Base Classification Reporter - Unified API Interface.

This module provides the base class and interface for all classification reporters,
ensuring consistent APIs and behavior across single-task and multi-task scenarios.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import numpy as np
from scitex import logging

logger = logging.getLogger(__name__)


class BaseClassificationReporter(ABC):
    """
    Abstract base class for all classification reporters.

    This class defines the unified API that all classification reporters must implement,
    ensuring consistent parameter names, method signatures, and behavior.

    Parameters
    ----------
    name : str
        Experiment name
    output_dir : Union[str, Path], optional
        Base directory for outputs. If None, creates timestamped directory.
    precision : int, default 3
        Number of decimal places for numerical outputs
    """

    def __init__(
        self,
        name: str,
        output_dir: Union[str, Path] = None,
        precision: int = 3,
        verbose=True,
    ):
        self.name = name
        self.precision = precision
        self._dirs_created = False

        # Set default output directory if not provided
        if output_dir is None:
            from datetime import datetime

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = Path(f"./results/{name}_{timestamp}")

        self.output_dir = Path(output_dir)

        if verbose:
            logger.info(
                (
                    f"Classifcation reporter initialized "
                    f"(name: {name}, output directory: {str(output_dir)})"
                )
            )

    def _create_subdir_if_needed(self, subdir: str) -> Path:
        """Create a subdirectory only when needed."""
        subdir_path = self.output_dir / subdir
        subdir_path.mkdir(parents=True, exist_ok=True)
        return subdir_path

    def _round_numeric(self, value: Any) -> Any:
        """Round numeric values to specified precision."""
        if isinstance(value, (int, float, np.integer, np.floating)):
            return round(float(value), self.precision)
        elif isinstance(value, dict):
            return {k: self._round_numeric(v) for k, v in value.items()}
        elif isinstance(value, (list, tuple)):
            return type(value)(self._round_numeric(v) for v in value)
        else:
            return value

    @abstractmethod
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
        Calculate and save classification metrics.

        This is the unified method signature that all reporters must implement.

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
        pass

    @abstractmethod
    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary of all calculated metrics.

        Returns
        -------
        Dict[str, Any]
            Summary of metrics across all folds/tasks
        """
        pass

    def get_output_paths(self) -> Dict[str, Path]:
        """
        Get dictionary of output paths for different content types.

        Returns
        -------
        Dict[str, Path]
            Mapping of content types to their paths
        """
        return {
            "base": self.output_dir,
            "metrics": self.output_dir / "metrics",
            "plots": self.output_dir / "plots",
            "tables": self.output_dir / "tables",
            "reports": self.output_dir / "reports",
        }

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(name='{self.name}', "
            f"output_dir='{self.output_dir}')"
        )


class ReporterConfig:
    """
    Configuration class for classification reporters.

    This class encapsulates all configuration settings for classification
    reporters, providing a centralized way to manage reporting behavior,
    output formatting, and metric requirements.

    Attributes
    ----------
    precision : int
        Number of decimal places for numerical outputs in reports
    required_metrics : List[str]
        List of metric names that must be calculated and reported

    Examples
    --------
    >>> # Create default configuration
    >>> config = ReporterConfig()
    >>>
    >>> # Create custom configuration with higher precision
    >>> config = ReporterConfig(precision=5)
    >>>
    >>> # Create configuration with specific required metrics
    >>> config = ReporterConfig(
    ...     precision=4,
    ...     required_metrics=["balanced_accuracy", "mcc", "roc_auc"]
    ... )
    >>>
    >>> # Convert to dictionary for serialization
    >>> config_dict = config.to_dict()
    """

    def __init__(
        self,
        precision: int = 3,
        required_metrics: Optional[List[str]] = [
            "balanced_accuracy",
            "mcc",
            "confusion_matrix",
            "classification_report",
            "roc_auc",
            "roc_curve",
            "pre_rec_auc",
            "pre_rec_curve",
        ],
        verbose=True,
    ):
        """
        Initialize ReporterConfig with specified settings.

        Parameters
        ----------
        precision : int, default 3
            Number of decimal places for numerical outputs.
            Controls the precision of all floating-point values in reports,
            metrics, and summaries. Higher values provide more detail but
            may introduce numerical noise.

        required_metrics : List[str], optional
            List of metric names that must be calculated and reported.
            If None, defaults to a comprehensive set including:
            - balanced_accuracy: Accuracy adjusted for class imbalance
            - mcc: Matthews Correlation Coefficient
            - confusion_matrix: True/predicted class counts
            - classification_report: Per-class precision/recall/F1
            - roc_auc: Area under ROC curve (binary/multiclass)
            - roc_curve: ROC curve data points
            - pre_rec_auc: Area under Precision-Recall curve
            - pre_rec_curve: PR curve data points

        Notes
        -----
        The precision setting affects:
        - Metric values in reports and summaries
        - CSV and JSON output files
        - Console display formatting
        - Plot annotations and labels

        The required_metrics list is used for:
        - Validation of calculated metrics
        - Determining which plots to generate
        - Structuring output directories
        - Creating comprehensive reports
        """
        self.precision = precision

        # Set default comprehensive metrics if not provided
        self.required_metrics = required_metrics

        required_metrics_str = ""
        for required_metric in required_metrics:
            required_metrics_str += f"        {required_metric}\n"
        if verbose:
            logger.info(
                (
                    f"Config set as:\n"
                    f"    precision: {precision}\n"
                    f"    required_metrics:\n"
                    f"{required_metrics_str}"
                )
            )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary format.

        Useful for serialization, logging, and saving configuration
        alongside experiment results.

        Returns
        -------
        Dict[str, Any]
            Dictionary containing all configuration parameters with keys:
            - 'precision': int, decimal precision setting
            - 'required_metrics': List[str], required metric names

        Examples
        --------
        >>> config = ReporterConfig(precision=4)
        >>> config_dict = config.to_dict()
        >>> print(config_dict)
        {'precision': 4, 'required_metrics': [...]}
        """
        return {
            "precision": self.precision,
            "required_metrics": self.required_metrics,
        }

# EOF
