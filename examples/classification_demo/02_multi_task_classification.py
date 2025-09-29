#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-22 15:06:29 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/examples/classification_demo/02_multi_task_classification.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./examples/classification_demo/02_multi_task_classification.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Multi-Task Classification Example with Cross-Validation

Demonstrates:
  1. Multi-task classification with cross-validation
  2. Automatic fold organization for each task
  3. Custom data saving per task and fold
  4. CV summary generation
"""


import numpy as np
import pandas as pd
import scitex as stx
from scitex.ml.classification import ClassificationReporter
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler


def main():
    """Run multi-task classification with cross-validation."""
    # Load data
    df = stx.io.load("./data/datasets/multitask_classification.csv")

    # Prepare features
    feature_cols = [col for col in df.columns if col.startswith("feature")]
    X = df[feature_cols].values

    # Prepare targets for multiple tasks
    tasks = {
        "task1_binary": df["task1_binary"].values,
        "task2_count": df["task2_count"].values,
        "task3_dominant": df["task3_dominant"].values,
    }

    # Initialize unified reporter (multi-task mode)
    reporter = ClassificationReporter(
        CONFIG["SDIR"] + "classification_results",
        tasks=list(tasks.keys()),
        verbose=False,
    )

    # Setup cross-validation
    n_folds = 5

    # Store results for summary
    all_task_results = {task_name: [] for task_name in tasks.keys()}

    # Perform cross-validation for each task
    for task_name, y in tasks.items():
        # Create stratified folds based on this task's labels
        cv = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=42)

        for fold_idx, (train_idx, test_idx) in enumerate(cv.split(X, y)):
            # Split data for this fold
            X_train, X_test = X[train_idx], X[test_idx]
            y_train, y_test = y[train_idx], y[test_idx]

            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)

            # Train model
            model = RandomForestClassifier(
                n_estimators=100, random_state=42 + fold_idx
            )
            model.fit(X_train_scaled, y_train)

            # Get predictions
            y_pred = model.predict(X_test_scaled)
            y_pred_proba = model.predict_proba(X_test_scaled)

            # Determine class labels
            n_classes = len(np.unique(y))
            if task_name == "task1_binary":
                class_labels = ["Negative", "Positive"]
            elif task_name == "task2_count":
                class_labels = [f"Count_{i}" for i in range(n_classes)]
            else:  # task3_dominant
                class_labels = [f"Class_{i}" for i in range(n_classes)]

            # Calculate and save metrics
            metrics = reporter.calculate_metrics(
                y_true=y_test,
                y_pred=y_pred,
                y_proba=y_pred_proba,
                labels=class_labels,
                fold=fold_idx,
                task=task_name,
                verbose=False,
            )

            # Store accuracy for summary
            accuracy = np.mean(y_pred == y_test)
            all_task_results[task_name].append(accuracy)

            # Save custom data for this fold
            reporter.save(
                {
                    "feature_{i}": imp
                    for i, imp in enumerate(model.feature_importances_)
                },
                "feature_importance.json",
                task=task_name,
                fold=fold_idx,
            )

            # Save predictions
            predictions_df = pd.DataFrame(
                {
                    "sample_idx": test_idx,
                    "y_true": y_test,
                    "y_pred": y_pred,
                    **{
                        f"proba_class_{i}": y_pred_proba[:, i]
                        for i in range(y_pred_proba.shape[1])
                    },
                }
            )
            reporter.save(
                predictions_df,
                "predictions.csv",
                task=task_name,
                fold=fold_idx,
            )

        # Save task-level CV summary
        task_accuracies = all_task_results[task_name]
        task_cv_summary = {
            "task": task_name,
            "n_folds": n_folds,
            "accuracies": task_accuracies,
            "mean_accuracy": np.mean(task_accuracies),
            "std_accuracy": np.std(task_accuracies),
            "min_accuracy": np.min(task_accuracies),
            "max_accuracy": np.max(task_accuracies),
        }
        # Save to task's cv_summary directory
        reporter.save(
            task_cv_summary, "cv_summary/task_summary.json", task=task_name
        )

    # Save global cross-validation summary
    overall_summary = {}
    for task_name in tasks.keys():
        accs = all_task_results[task_name]
        overall_summary[task_name] = {
            "mean": np.mean(accs),
            "std": np.std(accs),
            "min": np.min(accs),
            "max": np.max(accs),
        }

    global_analysis = {
        "experiment_type": "multi_task_classification_cv",
        "n_tasks": len(tasks),
        "task_names": list(tasks.keys()),
        "n_samples": X.shape[0],
        "n_features": X.shape[1],
        "n_folds": n_folds,
        "task_summaries": overall_summary,
        "mean_accuracy_across_tasks": np.mean(
            [s["mean"] for s in overall_summary.values()]
        ),
        "std_accuracy_across_tasks": np.std(
            [s["mean"] for s in overall_summary.values()]
        ),
    }
    reporter.save(global_analysis, "global_cv_summary.json")

    # Save comparison report
    comparison_report = (
        f"""# Multi-Task Classification CV Report

## Experiment Overview
- Tasks: {', '.join(tasks.keys())}
- Samples: {X.shape[0]}
- Features: {X.shape[1]}
- Cross-validation: {n_folds}-fold

## Results Summary
| Task | Mean ± Std | Min | Max |
|------|------------|-----|-----|
"""
        + "\n".join(
            [
                f"| {task} | {overall_summary[task]['mean']:.3f} ± {overall_summary[task]['std']:.3f} | "
                f"{overall_summary[task]['min']:.3f} | {overall_summary[task]['max']:.3f} |"
                for task in tasks.keys()
            ]
        )
        + f"""

## Overall Performance
- Mean Accuracy: {global_analysis['mean_accuracy_across_tasks']:.3f} ± {global_analysis['std_accuracy_across_tasks']:.3f}
"""
    )
    reporter.save(comparison_report, "cv_comparison_report.md")

    return 0


def run_main() -> None:
    """Initialize scitex framework, run main function, and cleanup."""
    global CONFIG, CC, sys, plt, rng

    import argparse
    import sys

    import matplotlib.pyplot as plt
    import scitex as stx

    args = argparse.Namespace()  # Empty namespace instead of None
    CONFIG, sys.stdout, sys.stderr, plt, CC, rng = stx.session.start(
        sys,
        plt,
        args=args,
        file=__FILE__,
        sdir_suffix=None,
        verbose=False,
        agg=True,
    )

    exit_status = main()

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
