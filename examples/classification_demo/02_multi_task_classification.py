#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-21 23:35:52 (ywatanabe)"
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
Multi-Task Classification Example with SciTeX Reporter

Functionalities:
  1. Load synthetic multi-task classification dataset
  2. Train separate Random Forest models for multiple classification tasks
  3. Evaluate each task independently with MultipleTasksClassificationReporter
  4. Save organized outputs for each task

Dependencies:
  - Core libraries: numpy, pandas, scikit-learn
  - SciTeX modules: scitex.ml.classification, scitex.io, scitex.logging, scitex.session

IO:
  - Input: ./data/multitask_classification.csv
  - Output: ./outputs/multi_task_classification/
      - {task_name}/metrics/fold_*/classification_metrics.csv
      - {task_name}/reports/fold_*/classification_report.txt
      - {task_name}/figures/*.png
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import scitex as stx
from scitex.logging import getLogger
from scitex.ml.classification import MultipleTasksClassificationReporter
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

logger = getLogger(__name__)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Multi-task classification example with SciTeX"
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("./data"),
        help="Directory containing input data (default: ./data)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,  # Will use CONFIG['SDIR'] if not specified
        help="Output directory for results (default: uses SciTeX session directory)",
    )
    parser.add_argument(
        "--n-estimators",
        type=int,
        default=100,
        help="Number of trees in Random Forest (default: 100)",
    )
    parser.add_argument(
        "--test-size",
        type=float,
        default=0.3,
        help="Proportion of dataset for testing (default: 0.3)",
    )
    parser.add_argument(
        "--random-state",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42)",
    )
    return parser.parse_args()


def main(args):
    """Run multi-task classification example.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments
    """
    logger.info("=" * 60)
    logger.info("Multi-Task Classification Example")
    logger.info("=" * 60)

    # Load data
    data_path = (
        __DIR__ + "/00_generate_data_out/datasets/multitask_classification.csv"
    )
    df = stx.io.load(data_path)

    logger.info(f"Loaded dataset from: {data_path}")
    logger.info(f"Shape: {df.shape}")

    # Prepare features
    feature_cols = [col for col in df.columns if col.startswith("feature")]
    X = df[feature_cols].values

    # Prepare targets for multiple tasks
    tasks = {
        "task1_binary": df["task1_binary"].values,
        "task2_count": df["task2_count"].values,
        "task3_dominant": df["task3_dominant"].values,
    }

    logger.info(f"Features: {X.shape}")
    for task_name, y in tasks.items():
        logger.info(f"{task_name} distribution: {np.bincount(y)}")

    # Split data (same split for all tasks)
    X_train, X_test, indices_train, indices_test = train_test_split(
        X,
        np.arange(len(X)),
        test_size=args.test_size,
        random_state=args.random_state,
    )

    # Scale features
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    # Use SciTeX output directory if not specified
    if args.output_dir is None:
        args.output_dir = Path(CONFIG["SDIR"]) / "classification_results"

    # Initialize multi-task reporter
    task_names = list(tasks.keys())
    reporter = MultipleTasksClassificationReporter(
        name="multi_task_classification",
        output_dir=str(args.output_dir),
        target_classes=task_names,
    )

    logger.info(f"Initialized multi-task reporter")
    logger.info(f"Output directory: {args.output_dir}")
    logger.info(f"Tasks: {task_names}")

    # Dictionary to store results
    results = {}

    # Train and evaluate each task
    for task_idx, (task_name, y) in enumerate(tasks.items()):
        logger.info(f"\n{'='*40}")
        logger.info(f"Task {task_idx + 1}/{len(tasks)}: {task_name}")
        logger.info(f"{'='*40}")

        # Get task-specific targets
        y_train = y[indices_train]
        y_test = y[indices_test]

        # Train model for this task
        logger.info(f"Training RandomForest for {task_name}...")
        model = RandomForestClassifier(
            n_estimators=args.n_estimators, random_state=args.random_state
        )
        model.fit(X_train, y_train)

        # Get predictions
        y_pred = model.predict(X_test)
        y_pred_proba = model.predict_proba(X_test)

        # Determine class labels based on task
        n_classes = len(np.unique(y))
        if task_name == "task1_binary":
            class_labels = ["Negative", "Positive"]
        elif task_name == "task2_count":
            class_labels = [f"Count_{i}" for i in range(n_classes)]
        else:  # task3_dominant
            class_labels = [f"Class_{i}" for i in range(n_classes)]

        # Report metrics for this task using unified API
        logger.info(f"Reporting metrics for {task_name}...")
        metrics = reporter.calculate_metrics(
            y_true=y_test,
            y_pred=y_pred,
            y_proba=y_pred_proba,
            labels=class_labels,
            fold_idx=0,
            target=task_name,
        )

        # Store results
        accuracy = np.mean(y_pred == y_test)
        results[task_name] = {"accuracy": accuracy, "metrics": metrics}
        logger.success(f"Accuracy for {task_name}: {accuracy:.3f}")

    # Display summary
    logger.info("\n" + "=" * 60)
    logger.info("Results Summary:")
    logger.info("=" * 60)

    # Save summary results
    summary_df = pd.DataFrame(
        [
            {"task": task, "accuracy": res["accuracy"]}
            for task, res in results.items()
        ]
    )
    summary_path = args.output_dir / "summary.csv"
    stx.io.save(summary_df, summary_path, symlink_from_cwd=True)
    logger.success(f"Saved summary to: {summary_path}")

    # Check output structure
    for task_name in task_names:
        task_dir = args.output_dir / task_name
        if task_dir.exists():
            logger.info(f"\n{task_name} outputs:")
            task_files = list(task_dir.glob("**/*"))
            for file in sorted(task_files):
                if file.is_file():
                    rel_path = file.relative_to(task_dir)
                    size = file.stat().st_size
                    logger.info(f"  - {rel_path} ({size:,} bytes)")

            # Load and display metrics for this task
            metrics_file = (
                task_dir / "metrics" / "fold_00" / "classification_metrics.csv"
            )
            if metrics_file.exists():
                metrics_df = pd.read_csv(metrics_file)
                logger.info(f"\n  Metrics for {task_name}:")
                for _, row in metrics_df.iterrows():
                    logger.info(f"    {row['metric']}: {row['value']:.3f}")

    logger.success("\n" + "=" * 60)
    logger.success("Multi-task classification example completed!")
    logger.success("=" * 60)

    return 0  # Exit status


def run_main() -> None:
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
