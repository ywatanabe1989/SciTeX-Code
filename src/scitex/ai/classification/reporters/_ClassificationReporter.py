#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-22 14:48:00 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/ml/classification/reporters/_ClassificationReporter.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/ml/classification/reporters/_ClassificationReporter.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
"""
Unified Classification Reporter.

A single, unified reporter that handles both single-task and multi-task
classification scenarios seamlessly.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import numpy as np

# Import base class and single reporter for internal use
from ._BaseClassificationReporter import (BaseClassificationReporter,
                                          ReporterConfig)
from ._SingleClassificationReporter import SingleTaskClassificationReporter
from .reporter_utils.storage import MetricStorage


class ClassificationReporter(BaseClassificationReporter):
    """
    Unified classification reporter for single and multi-task scenarios.

    This reporter automatically adapts to your use case:
    - Single task: Just use it without specifying tasks
    - Multiple tasks: Specify tasks upfront or create them dynamically
    - Seamless switching between single and multi-task workflows

    Parameters
    ----------
    output_dir : Union[str, Path]
        Base directory for outputs. If None, creates timestamped directory.
    tasks : List[str], optional
        List of task names. If None, tasks are created dynamically as needed.
    precision : int, default 3
        Number of decimal places for numerical outputs
    required_metrics : List[str], optional
        List of metrics to calculate. Defaults to comprehensive set.
    verbose : bool, default True
        Whether to print initialization messages
    **kwargs
        Additional arguments passed to base class

    Examples
    --------
    >>> # Single task usage (no tasks specified)
    >>> reporter = ClassificationReporter("./results")
    >>> reporter.calculate_metrics(y_true, y_pred, y_proba)

    >>> # Multi-task with predefined tasks
    >>> reporter = ClassificationReporter("./results", tasks=["binary", "multiclass"])
    >>> reporter.calculate_metrics(y_true, y_pred, task="binary")

    >>> # Dynamic task creation
    >>> reporter = ClassificationReporter("./results")
    >>> reporter.calculate_metrics(y_true1, y_pred1, task="task1")
    >>> reporter.calculate_metrics(y_true2, y_pred2, task="task2")
    """

    def __init__(
        self,
        output_dir: Union[str, Path],
        tasks: Optional[List[str]] = None,
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
        verbose: bool = True,
        **kwargs,
    ):
        # Set default metrics if not provided
        if required_metrics is None:
            required_metrics = [
                "balanced_accuracy",
                "mcc",
                "confusion_matrix",
                "classification_report",
                "roc_auc",
                "roc_curve",
                "pre_rec_auc",
                "pre_rec_curve",
            ]

        # Create internal config from parameters
        self.config = ReporterConfig(
            precision=precision, required_metrics=required_metrics
        )

        # Initialize base class
        super().__init__(output_dir=output_dir, precision=precision, **kwargs)

        self.precision = precision
        self.required_metrics = required_metrics
        self.storage = MetricStorage(self.output_dir, precision=self.precision)

        # Setup tasks
        self.tasks = tasks if tasks is not None else []
        self.verbose = verbose

        # Create individual reporters for each task
        self.reporters: Dict[str, SingleTaskClassificationReporter] = {}

        # Single mode: Create a single reporter at the root level
        # Multi mode: Create reporters in subdirectories
        if not self.tasks:
            # Single-task mode - use output_dir directly
            self._single_reporter = SingleTaskClassificationReporter(
                output_dir=self.output_dir, config=self.config, verbose=False
            )
        else:
            # Multi-task mode - create subdirectories
            self._single_reporter = None
            self._setup_task_reporters()

        # Save configuration
        self._save_config()

        # Print initialization info if verbose
        if self.verbose and self.tasks:
            print(f"\n{'='*70}")
            print(f"Classification Reporter Initialized")
            print(f"{'='*70}")
            print(f"Output Directory: {self.output_dir.absolute()}")
            print(f"Tasks: {self.tasks}")
            print(f"{'='*70}\n")

    def _create_single_reporter(self, task: str) -> None:
        """Create a single task reporter."""
        task_output_dir = self.output_dir / task
        self.reporters[task] = SingleTaskClassificationReporter(
            output_dir=task_output_dir,
            config=self.config,
            verbose=False,  # Suppress individual reporter messages
        )

    def _setup_task_reporters(self) -> None:
        """Setup individual reporters for each task."""
        for task in self.tasks:
            self._create_single_reporter(task)

    def calculate_metrics(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_proba: Optional[np.ndarray] = None,
        labels: Optional[List[str]] = None,
        fold: Optional[int] = None,
        task: Optional[str] = None,
        verbose: bool = True,
    ) -> Dict[str, Any]:
        """
        Calculate metrics for classification.

        Automatically handles single vs multi-task scenarios:
        - If no task specified and no tasks defined: creates "default" task
        - If no task specified but tasks exist: uses first task
        - If task specified: uses/creates that specific task

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
        task : str, optional
            Task identifier. If None and no tasks exist, creates "default" task.
        verbose : bool, default True
            Whether to print progress

        Returns
        -------
        Dict[str, Any]
            Dictionary of calculated metrics
        """
        # Single-task mode (tasks=None)
        if not self.tasks and self._single_reporter:
            if task is not None:
                # Convert to multi-task mode on the fly
                self.tasks = [task]
                self._single_reporter = None
                self._create_single_reporter(task)
                return self.reporters[task].calculate_metrics(
                    y_true=y_true,
                    y_pred=y_pred,
                    y_proba=y_proba,
                    labels=labels,
                    fold=fold,
                    verbose=verbose,
                )
            else:
                # Stay in single-task mode
                return self._single_reporter.calculate_metrics(
                    y_true=y_true,
                    y_pred=y_pred,
                    y_proba=y_proba,
                    labels=labels,
                    fold=fold,
                    verbose=verbose,
                )

        # Multi-task mode
        if task is None:
            # Use first available task
            task = self.tasks[0]
        else:
            # Task explicitly specified - create if doesn't exist
            if task not in self.reporters:
                if task not in self.tasks:
                    self.tasks.append(task)
                self._create_single_reporter(task)

        # Delegate to task-specific reporter
        return self.reporters[task].calculate_metrics(
            y_true=y_true,
            y_pred=y_pred,
            y_proba=y_proba,
            labels=labels,
            fold=fold,
            verbose=verbose,
        )

    def save(
        self,
        data: Any,
        relative_path: Union[str, Path],
        task: Optional[str] = None,
        fold: Optional[int] = None,
    ) -> Path:
        """
        Save custom data with automatic task/fold organization.

        Parameters
        ----------
        data : Any
            Data to save (any format supported by stx.io.save)
        relative_path : Union[str, Path]
            Relative path from output directory
        task : Optional[str], default None
            Task name. If provided, saves to task-specific directory
        fold : Optional[int], default None
            If provided, automatically prepends "fold_{fold:02d}/" to path

        Returns
        -------
        Path
            Absolute path to the saved file

        Examples
        --------
        >>> # Single task mode (no task specified)
        >>> reporter.save({"accuracy": 0.95}, "metrics.json")

        >>> # Multi-task mode
        >>> reporter.save(results, "results.csv", task="binary", fold=0)
        """
        # Single-task mode
        if not self.tasks and self._single_reporter:
            if task is not None:
                # Convert to multi-task mode
                self.tasks = [task]
                self._single_reporter = None
                self._create_single_reporter(task)
                return self.reporters[task].save(
                    data, relative_path, fold=fold
                )
            else:
                # Use single reporter's save
                return self._single_reporter.save(
                    data, relative_path, fold=fold
                )

        # Multi-task mode
        if task is not None:
            # Delegate to task-specific reporter
            if task not in self.reporters:
                # Create task if it doesn't exist
                if task not in self.tasks:
                    self.tasks.append(task)
                self._create_single_reporter(task)
            return self.reporters[task].save(data, relative_path, fold=fold)
        else:
            # Save to base output directory
            if fold is not None:
                relative_path = f"fold_{fold:02d}/{relative_path}"
            return self.storage.save(data, relative_path)

    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary of all calculated metrics.

        Returns
        -------
        Dict[str, Any]
            Summary of metrics across all tasks and folds
        """
        # Single-task mode
        if not self.tasks and self._single_reporter:
            return self._single_reporter.get_summary()

        # Multi-task mode
        if not self.reporters:
            return {"message": "No metrics calculated yet"}

        if len(self.reporters) == 1:
            # Only one task but in multi-task mode
            task_name = list(self.reporters.keys())[0]
            return self.reporters[task_name].get_summary()
        else:
            # Multiple tasks - aggregate summaries
            summary = {"n_tasks": len(self.reporters), "tasks": {}}
            for task_name, reporter in self.reporters.items():
                summary["tasks"][task_name] = reporter.get_summary()
            return summary

    def save_summary(
        self, filename: str = "summary.json", verbose: bool = True
    ) -> Path:
        """
        Save summary to file.

        Parameters
        ----------
        filename : str
            Filename for summary
        verbose : bool
            Whether to print summary

        Returns
        -------
        Path
            Path to saved summary file
        """
        # Single-task mode - delegate to single reporter
        if not self.tasks and self._single_reporter:
            return self._single_reporter.save_summary(
                filename, verbose=verbose
            )

        # Multi-task mode
        summary = self.get_summary()

        if len(self.reporters) == 1:
            # Only one task but in multi-task mode
            task_name = list(self.reporters.keys())[0]
            return self.reporters[task_name].save_summary(
                filename, verbose=verbose
            )
        else:
            # Multiple tasks - save in root directory
            return self.storage.save(summary, filename)

    def _save_config(self) -> None:
        """Save configuration to file."""
        config_data = {
            "output_dir": str(self.output_dir),
            "tasks": self.tasks,
            "precision": self.precision,
            "required_metrics": self.required_metrics,
        }
        self.storage.save(config_data, "config.json")

    def __repr__(self) -> str:
        if not self.tasks:
            return f"ClassificationReporter(output_dir='{self.output_dir}', tasks=None)"
        elif len(self.tasks) == 1:
            return f"ClassificationReporter(output_dir='{self.output_dir}', task='{self.tasks[0]}')"
        else:
            return f"ClassificationReporter(output_dir='{self.output_dir}', tasks={len(self.tasks)})"


# Convenience function for backwards compatibility
def create_classification_reporter(
    output_dir: Union[str, Path], tasks: Optional[List[str]] = None, **kwargs
) -> ClassificationReporter:
    """
    Create a unified classification reporter.

    Parameters
    ----------
    output_dir : Union[str, Path]
        Output directory for results
    tasks : List[str], optional
        List of task names (for multi-task)
    **kwargs
        Additional configuration options

    Returns
    -------
    ClassificationReporter
        Configured reporter instance
    """
    return ClassificationReporter(output_dir, tasks=tasks, **kwargs)

# EOF
