#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-02 06:38:58 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/ml/classification/reporters/_ClassificationReporter.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
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

    Features:
    - Comprehensive metrics calculation (balanced accuracy, MCC, ROC-AUC, PR-AUC, etc.)
    - Automated visualization generation:
      * Confusion matrices
      * ROC and Precision-Recall curves
      * Feature importance plots (via plotter)
      * CV aggregation plots with faded fold lines
      * Comprehensive metrics dashboard
    - Multi-format report generation (Org, Markdown, LaTeX, HTML, DOCX, PDF)
    - Cross-validation support with automatic fold aggregation
    - Multi-task classification tracking

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

    >>> # Feature importance visualization (via plotter)
    >>> reporter._single_reporter.plotter.create_feature_importance_plot(
    ...     feature_importance=importances,
    ...     feature_names=feature_names,
    ...     save_path="./results/feature_importance.png"
    ... )

    >>> # CV aggregation plots (automatically created on save_summary)
    >>> for fold in range(5):
    ...     metrics = reporter.calculate_metrics(y_true, y_pred, y_proba, fold=fold)
    >>> reporter.save_summary()  # Creates CV aggregation plots with faded fold lines
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
        model=None,
        feature_names: Optional[List[str]] = None,
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
        model : object, optional
            Trained model for automatic feature importance extraction
        feature_names : List[str], optional
            Feature names for feature importance (required if model is provided)

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
                    model=model,
                    feature_names=feature_names,
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
                    model=model,
                    feature_names=feature_names,
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
            model=model,
            feature_names=feature_names,
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

    def save_feature_importance(
        self,
        model,
        feature_names: List[str],
        fold: Optional[int] = None,
        task: Optional[str] = None,
    ) -> Dict[str, float]:
        """
        Calculate and save feature importance for tree-based models.

        Parameters
        ----------
        model : object
            Fitted classifier (must have feature_importances_)
        feature_names : List[str]
            Names of features
        fold : int, optional
            Fold number for tracking
        task : str, optional
            Task name for multi-task mode

        Returns
        -------
        Dict[str, float]
            Dictionary of feature importances {feature_name: importance}
        """
        # Single-task mode
        if not self.tasks and self._single_reporter:
            return self._single_reporter.save_feature_importance(
                model, feature_names, fold
            )

        # Multi-task mode
        if task is not None and task in self.reporters:
            return self.reporters[task].save_feature_importance(
                model, feature_names, fold
            )

        return {}

    def save_feature_importance_summary(
        self,
        all_importances: List[Dict[str, float]],
        task: Optional[str] = None,
    ) -> None:
        """
        Create summary visualization of feature importances across all folds.

        Parameters
        ----------
        all_importances : List[Dict[str, float]]
            List of feature importance dicts from each fold
        task : str, optional
            Task name for multi-task mode
        """
        # Single-task mode
        if not self.tasks and self._single_reporter:
            return self._single_reporter.save_feature_importance_summary(
                all_importances
            )

        # Multi-task mode
        if task is not None and task in self.reporters:
            return self.reporters[task].save_feature_importance_summary(
                all_importances
            )

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


def parse_args():
    """Parse command line arguments."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Test ClassificationReporter with sample data"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./.dev/classification_reporter_test_out",
        help="Output directory for test results (default: %(default)s)"
    )
    parser.add_argument(
        "--n-samples",
        type=int,
        default=100,
        help="Number of samples to generate (default: %(default)s)"
    )
    parser.add_argument(
        "--n-folds",
        type=int,
        default=3,
        help="Number of CV folds (default: %(default)s)"
    )
    parser.add_argument(
        "--task-type",
        type=str,
        choices=["binary", "multiclass", "multitask"],
        default="binary",
        help="Type of classification task (default: %(default)s)"
    )

    return parser.parse_args()


def main(args):
    """Test ClassificationReporter functionality."""
    from sklearn.datasets import make_classification
    from sklearn.model_selection import StratifiedKFold
    from sklearn.linear_model import LogisticRegression
    from sklearn.ensemble import RandomForestClassifier

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("ClassificationReporter Test")
    print("=" * 60)
    print(f"Task type: {args.task_type}")
    print(f"Output dir: {output_dir}")
    print(f"Samples: {args.n_samples}, Folds: {args.n_folds}")
    print()

    if args.task_type == "binary":
        # Binary classification
        print("Testing Binary Classification...")
        X, y = make_classification(
            n_samples=args.n_samples,
            n_features=20,
            n_classes=2,
            n_informative=15,
            n_redundant=5,
            random_state=42
        )
        labels = ["Negative", "Positive"]

        reporter = ClassificationReporter(output_dir / "binary", track=True)

        # Cross-validation
        cv = StratifiedKFold(n_splits=args.n_folds, shuffle=True, random_state=42)
        model = LogisticRegression(random_state=42, max_iter=1000)

        for fold, (train_idx, test_idx) in enumerate(cv.split(X, y)):
            X_train, X_test = X[train_idx], X[test_idx]
            y_train, y_test = y[train_idx], y[test_idx]

            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            y_proba = model.predict_proba(X_test)

            reporter.calculate_metrics(
                y_true=y_test,
                y_pred=y_pred,
                y_proba=y_proba,
                labels=labels,
                fold=fold
            )

        # Generate reports
        reporter.save_summary()
        print(f"✓ Binary classification results saved to: {output_dir / 'binary'}")

    elif args.task_type == "multiclass":
        # Multiclass classification
        print("Testing Multiclass Classification...")
        X, y = make_classification(
            n_samples=args.n_samples,
            n_features=20,
            n_classes=4,
            n_informative=15,
            n_redundant=5,
            n_clusters_per_class=1,
            random_state=42
        )
        labels = ["Class_A", "Class_B", "Class_C", "Class_D"]

        reporter = ClassificationReporter(output_dir / "multiclass", track=True)

        cv = StratifiedKFold(n_splits=args.n_folds, shuffle=True, random_state=42)
        model = RandomForestClassifier(n_estimators=50, random_state=42)

        for fold, (train_idx, test_idx) in enumerate(cv.split(X, y)):
            X_train, X_test = X[train_idx], X[test_idx]
            y_train, y_test = y[train_idx], y[test_idx]

            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            y_proba = model.predict_proba(X_test)

            reporter.calculate_metrics(
                y_true=y_test,
                y_pred=y_pred,
                y_proba=y_proba,
                labels=labels,
                fold=fold
            )

        reporter.save_summary()
        print(f"✓ Multiclass classification results saved to: {output_dir / 'multiclass'}")

    elif args.task_type == "multitask":
        # Multi-task classification
        print("Testing Multi-task Classification...")

        # Task 1: Binary
        X1, y1 = make_classification(
            n_samples=args.n_samples, n_features=20, n_classes=2, random_state=42
        )

        # Task 2: Multiclass
        X2, y2 = make_classification(
            n_samples=args.n_samples, n_features=20, n_classes=3, random_state=43
        )

        reporter = ClassificationReporter(
            output_dir / "multitask",
            tasks=["binary_task", "multiclass_task"],
            track=True
        )

        cv = StratifiedKFold(n_splits=args.n_folds, shuffle=True, random_state=42)

        # Task 1
        model1 = LogisticRegression(random_state=42, max_iter=1000)
        for fold, (train_idx, test_idx) in enumerate(cv.split(X1, y1)):
            X_train, X_test = X1[train_idx], X1[test_idx]
            y_train, y_test = y1[train_idx], y1[test_idx]

            model1.fit(X_train, y_train)
            y_pred = model1.predict(X_test)
            y_proba = model1.predict_proba(X_test)

            reporter.calculate_metrics(
                y_true=y_test,
                y_pred=y_pred,
                y_proba=y_proba,
                labels=["Neg", "Pos"],
                fold=fold,
                task="binary_task"
            )

        # Task 2
        model2 = RandomForestClassifier(n_estimators=50, random_state=42)
        for fold, (train_idx, test_idx) in enumerate(cv.split(X2, y2)):
            X_train, X_test = X2[train_idx], X2[test_idx]
            y_train, y_test = y2[train_idx], y2[test_idx]

            model2.fit(X_train, y_train)
            y_pred = model2.predict(X_test)
            y_proba = model2.predict_proba(X_test)

            reporter.calculate_metrics(
                y_true=y_test,
                y_pred=y_pred,
                y_proba=y_proba,
                labels=["A", "B", "C"],
                fold=fold,
                task="multiclass_task"
            )

        reporter.save_summary()
        print(f"✓ Multi-task classification results saved to: {output_dir / 'multitask'}")

    print()
    print("=" * 60)
    print("Test Complete!")
    print("=" * 60)
    print(f"\nCreated files in: {output_dir}")

    # List all created files
    import subprocess
    result = subprocess.run(
        ["find", str(output_dir), "-type", "f"],
        capture_output=True,
        text=True
    )
    if result.stdout:
        files = sorted(result.stdout.strip().split('\n'))
        print(f"\nTotal files created: {len(files)}")
        print("\nFile tree:")
        subprocess.run(["tree", str(output_dir)])

    return 0


def run_main():
    """Initialize scitex framework, run main function, and cleanup."""
    global CONFIG, CC, sys, plt, rng

    import sys
    import matplotlib.pyplot as plt
    import scitex as stx

    args = parse_args()

    CONFIG, sys.stdout, sys.stderr, plt, CC, rng = stx.session.start(
        sys,
        plt,
        args=args,
        file=__FILE__,
        sdir_suffix=None,
        verbose=False,
        agg=True,
    )

    exit_status = main(args)

    stx.session.close(
        CONFIG,
        verbose=False,
        notify=False,
        message="",
        exit_status=exit_status,
    )


if __name__ == "__main__":
    run_main()

# EOF
