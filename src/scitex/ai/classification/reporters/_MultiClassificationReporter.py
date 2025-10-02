#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-22 15:00:55 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/ml/classification/reporters/_MultiClassificationReporter.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Improved Multiple Tasks Classification Reporter with unified API.

Enhanced version that addresses all identified issues:
- Unified API interface matching SingleTaskClassificationReporter
- Lazy directory creation
- Numerical precision control
- Graceful plotting with error handling
- Consistent parameter names
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import numpy as np

# Import base class and improved single reporter
from ._BaseClassificationReporter import (BaseClassificationReporter,
                                          ReporterConfig)
from ._SingleClassificationReporter import SingleTaskClassificationReporter
from .reporter_utils.storage import MetricStorage


class MultipleTasksClassificationReporter(BaseClassificationReporter):
    """
    Improved multi-task classification reporter with unified API.

    This reporter manages multiple SingleTaskClassificationReporter instances,
    one for each target/task, providing a unified interface for multi-task scenarios.

    Key improvements:
    - Same API as SingleTaskClassificationReporter (calculate_metrics method)
    - Lazy directory creation (no empty folders)
    - Numerical precision control
    - Graceful plotting with proper error handling
    - Consistent parameter names across all methods

    Parameters
    ----------
    output_dir : Union[str, Path]
        Base directory for outputs. If None, creates timestamped directory.
    tasks : List[str], optional
        List of task names or identifiers
    config : ReporterConfig, optional
        Configuration object for advanced settings
    **kwargs
        Additional arguments passed to base class
    """

    def __init__(
        self,
        output_dir: Union[str, Path],
        tasks: Optional[List[str]] = None,
        config: Optional[ReporterConfig] = None,
        verbose: bool = True,
        **kwargs,
    ):
        # Use config or create default
        if config is None:
            config = ReporterConfig()

        # Initialize base class
        super().__init__(
            output_dir=output_dir, precision=config.precision, **kwargs
        )

        self.config = config
        self.storage = MetricStorage(self.output_dir, precision=self.precision)

        # Setup tasks
        self.tasks = tasks if tasks is not None else []
        self.verbose = verbose

        # Create individual reporters for each target
        self.reporters: Dict[str, SingleTaskClassificationReporter] = {}
        if self.tasks:
            self._setup_target_reporters()

        # Save configuration
        self._save_config()

        # Print initialization info if verbose
        if self.verbose:
            print(f"\n{'='*70}")
            print(f"Multi-Task Classification Reporter Initialized")
            print(f"{'='*70}")
            print(f"Output Directory: {self.output_dir.absolute()}")
            print(f"Tasks: {self.tasks}")
            print(f"{'='*70}\n")

    def _create_single_reporter(self, task: str) -> None:
        """Create a single task reporter."""
        task_output_dir = self.output_dir / task
        self.reporters[task] = SingleTaskClassificationReporter(
            output_dir=task_output_dir, config=self.config, verbose=False
        )

    def _setup_target_reporters(self) -> None:
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
        Calculate metrics for a specific task using unified API.

        This method has the same signature as SingleTaskClassificationReporter
        but with an additional 'task' parameter to specify which task.

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
            Task identifier. If None, uses first task.
        verbose : bool, default True
            Whether to print progress

        Returns
        -------
        Dict[str, Any]
            Dictionary of calculated metrics for the specified task
        """
        # Handle task parameter
        if task is None:
            # If no tasks defined yet, create a default task
            if not self.tasks:
                task = "default"
                self.tasks = [task]
                self._create_single_reporter(task)
            else:
                # Use first available task
                task = self.tasks[0]
        else:
            # If task is provided but not in reporters, create it dynamically
            if task not in self.reporters:
                if task not in self.tasks:
                    self.tasks.append(task)
                self._create_single_reporter(task)

        # Delegate to appropriate single-task reporter
        return self.reporters[task].calculate_metrics(
            y_true=y_true,
            y_pred=y_pred,
            y_proba=y_proba,
            labels=labels,
            fold=fold,
            verbose=verbose,
        )

    def calculate_metrics_for_all_targets(
        self,
        targets_data: Dict[str, Dict[str, np.ndarray]],
        fold: Optional[int] = None,
        verbose: bool = True,
    ) -> Dict[str, Dict[str, Any]]:
        """
        Calculate metrics for all targets in batch.

        Parameters
        ----------
        targets_data : Dict[str, Dict[str, np.ndarray]]
            Dictionary mapping target names to their data:
            {
                'target1': {
                    'y_true': np.array(...),
                    'y_pred': np.array(...),
                    'y_proba': np.array(...),  # optional
                    'labels': ['class1', 'class2']  # optional
                },
                'target2': {...}
            }
        fold : int, optional
            Fold index for cross-validation
        verbose : bool, default True
            Whether to print progress

        Returns
        -------
        Dict[str, Dict[str, Any]]
            Dictionary mapping target names to their metrics
        """
        all_results = {}

        for target_name, data in targets_data.items():
            if target_name not in self.reporters:
                print(f"Warning: Unknown target '{target_name}', skipping")
                continue

            # Extract data with defaults
            y_true = data["y_true"]
            y_pred = data["y_pred"]
            y_proba = data.get("y_proba", None)
            labels = data.get("labels", None)

            # Calculate metrics for this target
            all_results[target_name] = self.calculate_metrics(
                y_true=y_true,
                y_pred=y_pred,
                y_proba=y_proba,
                labels=labels,
                fold=fold,
                task=target_name,
                verbose=verbose,
            )

        return all_results

    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary of all calculated metrics across all targets.

        Returns
        -------
        Dict[str, Any]
            Summary statistics across all targets and folds
        """
        summary = {
            "tasks": self.tasks,
            "targets_summary": {},
        }

        # Get summary from each target reporter
        for target_name, reporter in self.reporters.items():
            target_summary = reporter.get_summary()
            summary["targets_summary"][target_name] = target_summary

        return summary

    def save_summary(self, filename: str = "multi_task_summary.json") -> Path:
        """
        Save multi-task summary to file.

        Parameters
        ----------
        filename : str, default "multi_task_summary.json"
            Filename for summary

        Returns
        -------
        Path
            Path to saved summary file
        """
        summary = self.get_summary()
        return self.storage.save(summary, filename)

    def get_reporter_for_target(
        self, target: str
    ) -> SingleTaskClassificationReporter:
        """
        Get the individual reporter for a specific target.

        Parameters
        ----------
        target : str
            Target identifier

        Returns
        -------
        SingleTaskClassificationReporter
            The reporter instance for the specified target
        """
        if target not in self.reporters:
            raise ValueError(
                f"Unknown target '{target}'. Available targets: {list(self.reporters.keys())}"
            )
        return self.reporters[target]

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
            Custom data to save (any format supported by stx.io.save)
        relative_path : Union[str, Path]
            Relative path from task/output directory. Examples:
            - When task is provided: saves to {task}/...
            - When fold is provided: saves to {task}/fold_{fold:02d}/...
            - When neither: saves to base output directory
        task : Optional[str], default None
            Task name. If provided, saves to task-specific directory
        fold : Optional[int], default None
            If provided, automatically prepends "fold_{fold:02d}/" to the path

        Returns
        -------
        Path
            Absolute path to the saved file

        Examples
        --------
        >>> # Save custom metrics for task1, fold 0
        >>> reporter.save(
        ...     {"metric1": 0.95},
        ...     "custom_metrics.json",
        ...     task="task1",
        ...     fold=0
        ... )  # Saves to: task1/fold_00/custom_metrics.json

        >>> # Save aggregated data for a specific task
        >>> reporter.save(
        ...     df_results,
        ...     "folds_all/analysis.csv",
        ...     task="task2"
        ... )  # Saves to: task2/folds_all/analysis.csv

        >>> # Save global summary across all tasks
        >>> reporter.save(
        ...     global_summary,
        ...     "overall_summary.json"
        ... )  # Saves to: overall_summary.json
        """
        if task is not None:
            # Delegate to the specific task's reporter
            if task not in self.reporters:
                # Dynamically create the task if it doesn't exist
                if task not in self.tasks:
                    self.tasks.append(task)
                self._create_single_reporter(task)
            return self.reporters[task].save(data, relative_path, fold=fold)
        else:
            # Save to base output directory
            if fold is not None:
                relative_path = f"fold_{fold:02d}/{relative_path}"
            return self.storage.save(data, relative_path)

    def _save_config(self) -> None:
        """Save configuration to file."""
        config_data = {
            "output_dir": str(self.output_dir),
            "tasks": self.tasks,
            "required_metrics": self.config.required_metrics,
            "precision": self.precision,
        }
        self.storage.save(config_data, "config.json")

    def __repr__(self) -> str:
        task_count = len(self.tasks)
        return (
            f"MultipleTasksClassificationReporter("
            f"tasks={task_count}, "
            f"output_dir='{self.output_dir}')"
        )


def create_multi_task_reporter(
    output_dir: Union[str, Path], tasks: Optional[List[str]] = None, **kwargs
) -> MultipleTasksClassificationReporter:
    """
    Convenience function to create a multi-task reporter.

    Parameters
    ----------
    tasks : List[str]
        List of task names
    output_dir : Union[str, Path], optional
        Output directory
    **kwargs
        Additional arguments

    Returns
    -------
    MultipleTasksClassificationReporter
        Configured multi-task reporter
    """
    return MultipleTasksClassificationReporter(
        tasks=tasks, output_dir=output_dir, **kwargs
    )

# EOF
