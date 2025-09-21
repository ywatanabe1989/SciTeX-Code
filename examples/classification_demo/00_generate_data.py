#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-22 01:27:03 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/examples/classification_demo/00_generate_data.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./examples/classification_demo/00_generate_data.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
  - Generates synthetic datasets for classification examples
  - Creates binary classification dataset with 2 classes
  - Creates multi-class classification dataset with 5 classes
  - Creates time series classification dataset with subject-based structure
  - Creates multi-task classification dataset with 3 different targets
  - Saves all datasets as CSV files with proper structure

Dependencies:
  - scripts:
    - None
  - packages:
    - numpy
    - pandas
    - sklearn.datasets
    - scitex

IO:
  - input-files:
    - None

  - output-files:
    - ./data/binary_classification.csv
    - ./data/multiclass_classification.csv
    - ./data/time_series_classification.csv
    - ./data/multitask_classification.csv
"""

"""Imports"""
import argparse

import numpy as np
import pandas as pd
import scitex as stx
from scitex.logging import getLogger
from sklearn.datasets import make_classification

logger = getLogger(__name__)

"""Parameters"""
# CONFIG = stx.io.load_configs()

"""Functions & Classes"""
def generate_binary_classification_data(
    n_samples: int = 1000, n_features: int = 20
) -> pd.DataFrame:
    """Generate binary classification dataset.

    Args:
        n_samples: Number of samples to generate
        n_features: Number of features

    Returns:
        DataFrame with features and binary target
    """
    X, y = make_classification(
        n_samples=n_samples,
        n_features=n_features,
        n_informative=15,
        n_redundant=5,
        n_classes=2,
        random_state=42,
        flip_y=0.05,
    )

    # Create DataFrame
    feature_names = [f"feature_{i}" for i in range(n_features)]
    df = pd.DataFrame(X, columns=feature_names)
    df["target"] = y

    return df


def generate_multiclass_classification_data(
    n_samples: int = 1500, n_features: int = 30, n_classes: int = 5
) -> pd.DataFrame:
    """Generate multi-class classification dataset.

    Args:
        n_samples: Number of samples to generate
        n_features: Number of features
        n_classes: Number of classes

    Returns:
        DataFrame with features and multi-class target
    """
    X, y = make_classification(
        n_samples=n_samples,
        n_features=n_features,
        n_informative=20,
        n_redundant=10,
        n_classes=n_classes,
        n_clusters_per_class=2,
        random_state=42,
        flip_y=0.03,
    )

    # Create DataFrame
    feature_names = [f"feature_{i}" for i in range(n_features)]
    df = pd.DataFrame(X, columns=feature_names)
    df["target"] = y

    return df


def generate_time_series_classification_data(
    n_subjects: int = 10, n_timepoints: int = 200, n_features: int = 15
) -> pd.DataFrame:
    """Generate time series classification dataset with subject-based structure.

    Args:
        n_subjects: Number of subjects
        n_timepoints: Number of time points per subject
        n_features: Number of features

    Returns:
        DataFrame with subject_id, timestamp, features, and target
    """
    data = []

    for subject_id in range(n_subjects):
        # Assign class to subject (binary)
        subject_class = subject_id % 2

        # Generate time series for this subject
        base_signal = np.sin(np.linspace(0, 10, n_timepoints))

        for t in range(n_timepoints):
            # Generate features with temporal correlation
            features = []
            for f in range(n_features):
                value = base_signal[t] * (f + 1) * 0.1
                value += np.random.randn() * 0.5
                if subject_class == 1:
                    value += np.sin(t * 0.1) * 0.3
                features.append(value)

            # Add row
            row = {
                "subject_id": subject_id,
                "timestamp": t / (n_timepoints - 1) * 10,  # Normalize to 0-10
                **{f"feature_{i}": features[i] for i in range(n_features)},
                "target": subject_class,
            }
            data.append(row)

    df = pd.DataFrame(data)

    # Count unique subjects per class
    class_counts = df.groupby("target")["subject_id"].nunique().to_dict()

    return df


def generate_multitask_classification_data(
    n_samples: int = 1200, n_features: int = 25
) -> pd.DataFrame:
    """Generate multi-task classification dataset with 3 different targets.

    Args:
        n_samples: Number of samples
        n_features: Number of features

    Returns:
        DataFrame with features and 3 different classification targets
    """
    # Generate base features
    X, _ = make_classification(
        n_samples=n_samples,
        n_features=n_features,
        n_informative=20,
        n_redundant=5,
        n_classes=4,
        random_state=42,
    )

    # Create DataFrame
    feature_names = [f"feature_{i}" for i in range(n_features)]
    df = pd.DataFrame(X, columns=feature_names)

    # Generate 3 different targets with different characteristics
    # Task 1: Binary classification
    df["task1_binary"] = (df["feature_0"] + df["feature_1"] > 0).astype(int)

    # Task 2: Count classification (0, 1, 2, 3)
    quartiles = pd.qcut(df["feature_2"] + df["feature_3"], q=4, labels=False)
    df["task2_count"] = quartiles

    # Task 3: Dominant feature classification (3 classes)
    dominant = np.argmax(
        np.abs(df[["feature_4", "feature_5", "feature_6"]].values), axis=1
    )
    df["task3_dominant"] = dominant

    return df


def main(args: argparse.Namespace) -> int:
    """Generate all synthetic datasets for classification examples.

    Args:
        args: Command line arguments

    Returns:
        Exit status (0 for success)
    """
    # Generate binary classification dataset
    df_binary = generate_binary_classification_data(
        n_samples=args.binary_samples, n_features=args.binary_features
    )
    stx.io.save(
        df_binary,
        "./data/datasets/binary_classification.csv",
        symlink_from_cwd=True,
    )

    # Generate multi-class classification dataset
    df_multiclass = generate_multiclass_classification_data(
        n_samples=args.multiclass_samples,
        n_features=args.multiclass_features,
        n_classes=args.multiclass_classes,
    )
    stx.io.save(
        df_multiclass,
        "./data/datasets/multiclass_classification.csv",
        symlink_from_cwd=True,
    )

    # Generate time series classification dataset
    df_timeseries = generate_time_series_classification_data(
        n_subjects=args.timeseries_subjects,
        n_timepoints=args.timeseries_points,
        n_features=args.timeseries_features,
    )
    stx.io.save(
        df_timeseries,
        "./data/datasets/time_series_classification.csv",
        symlink_from_cwd=True,
    )

    # Generate multi-task classification dataset
    df_multitask = generate_multitask_classification_data(
        n_samples=args.multitask_samples, n_features=args.multitask_features
    )
    stx.io.save(
        df_multitask,
        "./data/datasets/multitask_classification.csv",
        symlink_from_cwd=True,
    )

    return 0


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate synthetic datasets for classification examples"
    )

    # Binary classification parameters
    parser.add_argument(
        "--binary-samples",
        type=int,
        default=1000,
        help="Number of samples for binary classification (default: %(default)s)",
    )
    parser.add_argument(
        "--binary-features",
        type=int,
        default=20,
        help="Number of features for binary classification (default: %(default)s)",
    )

    # Multi-class classification parameters
    parser.add_argument(
        "--multiclass-samples",
        type=int,
        default=1500,
        help="Number of samples for multi-class classification (default: %(default)s)",
    )
    parser.add_argument(
        "--multiclass-features",
        type=int,
        default=30,
        help="Number of features for multi-class classification (default: %(default)s)",
    )
    parser.add_argument(
        "--multiclass-classes",
        type=int,
        default=5,
        help="Number of classes for multi-class classification (default: %(default)s)",
    )

    # Time series parameters
    parser.add_argument(
        "--timeseries-subjects",
        type=int,
        default=10,
        help="Number of subjects for time series data (default: %(default)s)",
    )
    parser.add_argument(
        "--timeseries-points",
        type=int,
        default=200,
        help="Number of time points per subject (default: %(default)s)",
    )
    parser.add_argument(
        "--timeseries-features",
        type=int,
        default=15,
        help="Number of features for time series data (default: %(default)s)",
    )

    # Multi-task parameters
    parser.add_argument(
        "--multitask-samples",
        type=int,
        default=1200,
        help="Number of samples for multi-task classification (default: %(default)s)",
    )
    parser.add_argument(
        "--multitask-features",
        type=int,
        default=25,
        help="Number of features for multi-task classification (default: %(default)s)",
    )

    args = parser.parse_args()
    return args


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
