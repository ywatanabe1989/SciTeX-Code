#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-03 04:10:00 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/ml/plt/plot_feature_importance.py

"""
Plot feature importance from trained models.

This module provides visualization functions for feature importance,
supporting both single-fold and cross-validation summary plots.
"""

from pathlib import Path
from typing import Dict, List, Optional, Union
import numpy as np
import matplotlib.pyplot as plt
import scitex as stx


def plot_feature_importance(
    importance: Union[np.ndarray, Dict[str, float]],
    feature_names: Optional[List[str]] = None,
    top_n: int = 20,
    title: str = "Feature Importance",
    xlabel: str = "Importance",
    figsize: tuple = (10, 8),
    spath: Optional[Union[str, Path]] = None,
) -> plt.Figure:
    """
    Plot feature importance as a horizontal bar chart.

    Parameters
    ----------
    importance : np.ndarray or Dict[str, float]
        Feature importance values. If array, must match feature_names length.
        If dict, keys are feature names and values are importances.
    feature_names : List[str], optional
        Names of features (required if importance is array)
    top_n : int, default 20
        Number of top features to display
    title : str, default "Feature Importance"
        Plot title
    xlabel : str, default "Importance"
        X-axis label
    figsize : tuple, default (10, 8)
        Figure size
    spath : Union[str, Path], optional
        Path to save the figure

    Returns
    -------
    fig : matplotlib.figure.Figure
        The figure object

    Examples
    --------
    >>> from sklearn.ensemble import RandomForestClassifier
    >>> import numpy as np
    >>> X = np.random.rand(100, 5)
    >>> y = np.random.randint(0, 2, 100)
    >>> model = RandomForestClassifier().fit(X, y)
    >>> fig = plot_feature_importance(
    ...     model.feature_importances_,
    ...     feature_names=['f1', 'f2', 'f3', 'f4', 'f5'],
    ...     spath='feature_importance.jpg'
    ... )
    """
    # Convert dict to arrays if needed
    if isinstance(importance, dict):
        feature_names = list(importance.keys())
        importance = np.array(list(importance.values()))

    # Validate inputs
    if feature_names is None:
        raise ValueError("feature_names must be provided when importance is an array")

    if len(feature_names) != len(importance):
        raise ValueError(
            f"Length mismatch: {len(feature_names)} feature names "
            f"but {len(importance)} importance values"
        )

    # Sort by importance
    indices = np.argsort(importance)[::-1][:top_n]
    sorted_importance = importance[indices]
    sorted_names = [feature_names[i] for i in indices]

    # Create figure
    fig, ax = plt.subplots(figsize=figsize)

    # Create horizontal bar plot
    y_pos = np.arange(len(sorted_names))
    ax.barh(
        y_pos,
        sorted_importance,
        align="center",
        alpha=0.8,
        color="steelblue",
        edgecolor="black",
    )

    # Format feature names (replace underscores, title case)
    formatted_names = [
        name.replace("_", " ").title() for name in sorted_names
    ]

    ax.set_yticks(y_pos)
    ax.set_yticklabels(formatted_names, fontsize=9)
    ax.invert_yaxis()  # Top feature at top
    ax.set_xlabel(xlabel, fontsize=11, fontweight="bold")
    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.grid(True, alpha=0.3, axis="x")

    plt.tight_layout()

    # Save if path provided
    if spath:
        spath_abs = Path(spath).resolve() if isinstance(spath, (str, Path)) else spath
        stx.io.save(fig, str(spath_abs), use_caller_path=False)

    return fig


def plot_feature_importance_cv_summary(
    all_importances: List[Dict[str, float]],
    top_n: int = 20,
    title: Optional[str] = None,
    figsize: tuple = (12, 8),
    spath: Optional[Union[str, Path]] = None,
) -> plt.Figure:
    """
    Plot feature importance summary across cross-validation folds with error bars.

    Parameters
    ----------
    all_importances : List[Dict[str, float]]
        List of importance dictionaries from each fold
    top_n : int, default 20
        Number of top features to display
    title : str, optional
        Plot title (auto-generated if None)
    figsize : tuple, default (12, 8)
        Figure size
    spath : Union[str, Path], optional
        Path to save the figure

    Returns
    -------
    fig : matplotlib.figure.Figure
        The figure object

    Examples
    --------
    >>> # After cross-validation
    >>> all_importances = [
    ...     {'feature1': 0.3, 'feature2': 0.7},
    ...     {'feature1': 0.4, 'feature2': 0.6},
    ... ]
    >>> fig = plot_feature_importance_cv_summary(
    ...     all_importances,
    ...     spath='feature_importance_cv_summary.jpg'
    ... )
    """
    if not all_importances:
        raise ValueError("all_importances cannot be empty")

    # Aggregate importances across folds
    all_features = set()
    for imp_dict in all_importances:
        all_features.update(imp_dict.keys())

    # Calculate mean and std for each feature
    feature_stats = {}
    for feature in all_features:
        values = [imp_dict.get(feature, 0) for imp_dict in all_importances]
        feature_stats[feature] = {
            "mean": float(np.mean(values)),
            "std": float(np.std(values)),
        }

    # Sort by mean importance and take top_n
    sorted_features = sorted(
        feature_stats.items(), key=lambda x: x[1]["mean"], reverse=True
    )[:top_n]

    # Extract data for plotting
    names = [item[0] for item in sorted_features]
    means = [item[1]["mean"] for item in sorted_features]
    stds = [item[1]["std"] for item in sorted_features]

    # Create figure
    fig, ax = plt.subplots(figsize=figsize)

    # Create horizontal bar plot with error bars
    y_pos = np.arange(len(names))
    ax.barh(
        y_pos,
        means,
        xerr=stds,
        align="center",
        alpha=0.8,
        color="steelblue",
        edgecolor="black",
        capsize=5,
        error_kw={"linewidth": 2},
    )

    # Format feature names
    formatted_names = [name.replace("_", " ").title() for name in names]

    ax.set_yticks(y_pos)
    ax.set_yticklabels(formatted_names, fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel("Mean Importance ± Std", fontsize=11, fontweight="bold")

    # Auto-generate title if not provided
    if title is None:
        n_folds = len(all_importances)
        title = f"Feature Importance (CV Summary, n={n_folds} folds)"

    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.grid(True, alpha=0.3, axis="x")

    plt.tight_layout()

    # Save if path provided
    if spath:
        spath_abs = Path(spath).resolve() if isinstance(spath, (str, Path)) else spath
        stx.io.save(fig, str(spath_abs), use_caller_path=False)

    return fig


def main(args):
    """Demo feature importance plotting."""
    from sklearn.ensemble import RandomForestClassifier
    from sklearn import datasets

    # Load iris dataset
    iris = datasets.load_iris()
    X = iris.data
    y = iris.target
    feature_names = iris.feature_names

    # Train model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)

    # Plot single fold
    fig = plot_feature_importance(
        model.feature_importances_,
        feature_names=feature_names,
        title="Feature Importance (Iris Dataset)",
        spath="plot_feature_importance_demo_single.jpg",
    )

    # Simulate CV results
    all_importances = []
    for i in range(5):
        model_fold = RandomForestClassifier(n_estimators=100, random_state=i)
        model_fold.fit(X, y)
        importance_dict = {
            name: float(imp)
            for name, imp in zip(feature_names, model_fold.feature_importances_)
        }
        all_importances.append(importance_dict)

    # Plot CV summary
    fig = plot_feature_importance_cv_summary(
        all_importances,
        spath="plot_feature_importance_demo_cv.jpg",
    )

    print("Generated feature importance plots:")
    print("  - plot_feature_importance_demo_single.jpg")
    print("  - plot_feature_importance_demo_cv.jpg")

    return 0


def parse_args():
    """Parse command line arguments."""
    import argparse

    parser = argparse.ArgumentParser(description="Demo feature importance plotting")
    return parser.parse_args()


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
        file=__file__,
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
