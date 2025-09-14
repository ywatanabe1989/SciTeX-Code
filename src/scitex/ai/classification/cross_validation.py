#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-07 12:57:42 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/ai/classification/cross_validation.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/ai/classification/cross_validation.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
"""
Cross-validation helper for streamlined machine learning experiments.

Provides a high-level interface for running cross-validation with
automatic metric tracking, validation, and report generation.
"""

import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

import numpy as np
import pandas as pd
from sklearn.model_selection import BaseCrossValidator, StratifiedKFold

from ._SingleClassificationReporter import SingleTaskClassificationReporter


class CrossValidationExperiment:
    """
    Streamlined cross-validation experiment runner.

    This class handles:
    - Cross-validation splitting
    - Model training and evaluation
    - Automatic metric calculation
    - Hyperparameter tracking
    - Progress monitoring
    - Report generation

    Parameters
    ----------
    name : str
        Experiment name
    model_fn : Callable
        Function that returns a model instance
    cv : BaseCrossValidator, optional
        Cross-validation splitter (default: 5-fold stratified)
    output_dir : Union[str, Path], optional
        Output directory for results
    metrics : List[str], optional
        List of metrics to calculate
    save_models : bool
        Whether to save trained models
    verbose : bool
        Whether to print progress
    """

    def __init__(
        self,
        name: str,
        model_fn: Callable,
        cv: Optional[BaseCrossValidator] = None,
        output_dir: Optional[Union[str, Path]] = None,
        metrics: Optional[List[str]] = None,
        save_models: bool = True,
        verbose: bool = True,
    ):
        self.name = name
        self.model_fn = model_fn
        self.cv = cv or StratifiedKFold(
            n_splits=5, shuffle=True, random_state=42
        )
        self.save_models = save_models
        self.verbose = verbose

        # Initialize reporter
        self.reporter = SingleTaskClassificationReporter(
            name=name, output_dir=output_dir, required_metrics=metrics
        )

        # Track experiment metadata
        self.metadata = {
            "name": name,
            "start_time": None,
            "end_time": None,
            "n_folds": (
                self.cv.get_n_splits()
                if hasattr(self.cv, "get_n_splits")
                else None
            ),
            "hyperparameters": {},
            "dataset_info": {},
        }

        # Results storage
        self.fold_times = []
        self.models = []

    def set_hyperparameters(self, **kwargs) -> None:
        """
        Set hyperparameters for tracking.

        Parameters
        ----------
        **kwargs
            Hyperparameter key-value pairs
        """
        self.metadata["hyperparameters"] = kwargs

        # Save hyperparameters
        self.reporter.add(kwargs, "experiment/hyperparameters.json")

    def describe_dataset(
        self,
        X: np.ndarray,
        y: np.ndarray,
        feature_names: Optional[List[str]] = None,
        class_names: Optional[List[str]] = None,
    ) -> None:
        """
        Record dataset information.

        Parameters
        ----------
        X : np.ndarray
            Features
        y : np.ndarray
            Labels
        feature_names : List[str], optional
            Feature names
        class_names : List[str], optional
            Class names
        """
        self.metadata["dataset_info"] = {
            "n_samples": X.shape[0],
            "n_features": X.shape[1],
            "n_classes": len(np.unique(y)),
            "class_distribution": pd.Series(y).value_counts().to_dict(),
            "feature_names": feature_names,
            "class_names": class_names,
        }

        # Save dataset info
        self.reporter.add(
            self.metadata["dataset_info"], "experiment/dataset_info.json"
        )

    def run(
        self,
        X: np.ndarray,
        y: np.ndarray,
        feature_names: Optional[List[str]] = None,
        class_names: Optional[List[str]] = None,
        calculate_curves: bool = True,
    ) -> Dict[str, Any]:
        """
        Run complete cross-validation experiment.

        Parameters
        ----------
        X : np.ndarray
            Features
        y : np.ndarray
            Labels
        feature_names : List[str], optional
            Feature names
        class_names : List[str], optional
            Class names
        calculate_curves : bool
            Whether to calculate and plot ROC/PR curves

        Returns
        -------
        Dict[str, Any]
            Experiment results and paths
        """
        # Record start time
        self.metadata["start_time"] = datetime.now()
        start_time = time.time()

        # Describe dataset
        self.describe_dataset(X, y, feature_names, class_names)

        if self.verbose:
            print("\n" + "=" * 70)
            print(f"CROSS-VALIDATION EXPERIMENT: {self.name}")
            print("=" * 70)
            print(
                f"Dataset: {X.shape[0]} samples, {X.shape[1]} features, {len(np.unique(y))} classes"
            )
            print(f"CV Strategy: {self.cv}")
            print(f"Model: {self.model_fn().__class__.__name__}")
            print("=" * 70 + "\n")

        # Run cross-validation
        for fold_idx, (train_idx, test_idx) in enumerate(self.cv.split(X, y)):
            fold_start = time.time()

            if self.verbose:
                print(
                    f"\n--- Fold {fold_idx + 1}/{self.cv.get_n_splits()} ---"
                )

            # Split data
            X_train, X_test = X[train_idx], X[test_idx]
            y_train, y_test = y[train_idx], y[test_idx]

            # Train model
            model = self.model_fn()

            if self.verbose:
                print(f"Training {model.__class__.__name__}...")

            model.fit(X_train, y_train)

            # Get predictions
            y_pred = model.predict(X_test)

            # Get probabilities if available
            y_proba = None
            if hasattr(model, "predict_proba"):
                y_proba = model.predict_proba(X_test)
            elif hasattr(model, "decision_function"):
                # For SVM and other models with decision function
                decision = model.decision_function(X_test)
                if len(decision.shape) == 1:
                    # Binary classification
                    y_proba = np.vstack([1 - decision, decision]).T
                else:
                    # Multi-class - use softmax approximation
                    y_proba = self._softmax(decision)

            # Calculate all metrics
            metrics = self.reporter.calculate_all_metrics(
                y_true=y_test,
                y_pred=y_pred,
                y_proba=y_proba,
                labels=class_names,
                fold_idx=fold_idx,
                save=True,
                plot=calculate_curves,
            )

            # Save model if requested
            if self.save_models:
                model_path = f"models/fold_{fold_idx:02d}_model.pkl"
                self.reporter.add(model, model_path)
                self.models.append(model)

            # Track timing
            fold_time = time.time() - fold_start
            self.fold_times.append(fold_time)

            if self.verbose:
                print(f"  Fold {fold_idx} completed in {fold_time:.2f}s")
                print(
                    f"  BA: {metrics.get('balanced_accuracy', 0):.3f}, "
                    f"MCC: {metrics.get('mcc', 0):.3f}"
                )
                if "roc_auc" in metrics:
                    print(
                        f"  ROC: {metrics['roc_auc']:.3f}, "
                        f"PR: {metrics.get('pr_auc', 0):.3f}"
                    )

        # Record end time
        self.metadata["end_time"] = datetime.now()
        total_time = time.time() - start_time

        # Save timing information
        timing_info = {
            "total_time": total_time,
            "mean_fold_time": np.mean(self.fold_times),
            "fold_times": self.fold_times,
        }
        self.reporter.add(timing_info, "experiment/timing.json")

        if self.verbose:
            print(f"\n{'='*70}")
            print(f"Experiment completed in {total_time:.2f}s")
            print(f"Mean fold time: {np.mean(self.fold_times):.2f}s")
            print(f"{'='*70}\n")

        # Generate final reports
        result_paths = self.reporter.save()

        # Return results
        return {
            "paths": result_paths,
            "metadata": self.metadata,
            "timing": timing_info,
            "models": self.models if self.save_models else None,
        }

    def _softmax(self, x: np.ndarray) -> np.ndarray:
        """Apply softmax to decision values."""
        exp_x = np.exp(x - np.max(x, axis=1, keepdims=True))
        return exp_x / np.sum(exp_x, axis=1, keepdims=True)

    def get_summary(self) -> pd.DataFrame:
        """Get summary statistics across folds."""
        return self.reporter.create_summary()

    def get_validation_report(self) -> Dict[str, Any]:
        """Get validation report."""
        return self.reporter.validate_completeness()


def quick_experiment(
    X: np.ndarray,
    y: np.ndarray,
    model,
    name: str = "quick_experiment",
    n_folds: int = 5,
    **kwargs,
) -> Dict[str, Any]:
    """
    Run a quick cross-validation experiment.

    This is a convenience function for rapid experimentation.

    Parameters
    ----------
    X : np.ndarray
        Features
    y : np.ndarray
        Labels
    model : sklearn estimator or callable
        Model instance or function that returns model
    name : str
        Experiment name
    n_folds : int
        Number of CV folds
    **kwargs
        Additional arguments for CrossValidationExperiment

    Returns
    -------
    Dict[str, Any]
        Experiment results

    Examples
    --------
    >>> from sklearn.svm import SVC
    >>> results = quick_experiment(X, y, SVC(), name="svm_test")
    >>> print(f"Report saved to: {results['paths']['final_report']}")
    """
    # Create model function if needed
    if callable(model) and not hasattr(model, "fit"):
        model_fn = model
    else:
        model_fn = lambda: model.__class__(**model.get_params())

    # Set up cross-validation
    cv = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=42)

    # Create experiment
    experiment = CrossValidationExperiment(
        name=name, model_fn=model_fn, cv=cv, **kwargs
    )

    # Track hyperparameters if available
    if hasattr(model, "get_params"):
        experiment.set_hyperparameters(**model.get_params())

    # Run experiment
    results = experiment.run(X, y)

    return results

# EOF
