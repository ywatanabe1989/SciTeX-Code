#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-07 12:57:06 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/ai/classification/_MultiClassificationReporter.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/ai/classification/_MultiClassificationReporter.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Enhanced Multi-task Classification Reporter using modular reporter utilities.

This module provides the MultipleTasksClassificationReporter class for managing
classification reports across multiple targets or conditions using the new
reporter_utils system.
"""

from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import numpy as np
import pandas as pd

# Import SingleTaskReporter that uses reporter_utils
from ._SingleClassificationReporter import SingleTaskClassificationReporter
# Import reporter utilities for direct operations
from .reporter_utils import (MetricStorage, MetricValidator,
                             aggregate_fold_metrics, create_summary_statistics,
                             create_summary_table, export_for_paper,
                             generate_markdown_report)


class MultipleTasksClassificationReporter:
    """
    Enhanced reporter for handling classification metrics across multiple targets.

    This class manages multiple SingleTaskClassificationReporter instances, one for each
    target class or condition, enabling parallel reporting and comparison. Uses the
    modular reporter_utils system for improved organization and validation.

    Parameters
    ----------
    name : str
        Base experiment name
    output_dir : Union[str, Path]
        Base directory path for saving results
    target_classes : List[str], optional
        List of target class names or identifiers, default is ["default"]
    required_metrics : List[str], optional
        List of required metrics for validation
    auto_validate : bool
        Whether to validate after each fold

    Attributes
    ----------
    name : str
        Experiment name
    output_dir : Path
        Base output directory
    target_to_id : Dict[str, int]
        Mapping from target names to their indices
    reporters : List[SingleTaskClassificationReporter]
        List of individual classification reporters for each target
    storage : MetricStorage
        Central storage manager for multi-task metadata
    validator : MetricValidator
        Validator for multi-task completeness
    """

    def __init__(
        self,
        name: str,
        output_dir: Union[str, Path] = None,
        target_classes: Optional[List[str]] = None,
        required_metrics: Optional[List[str]] = None,
        auto_validate: bool = True,
    ):
        self.name = name

        # Set default output directory if not provided
        if output_dir is None:
            from datetime import datetime

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = Path(f"./results/multi_{name}_{timestamp}")

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize targets
        if target_classes is None:
            target_classes = ["default"]
        self.target_classes = target_classes

        # Create target mapping
        self.target_to_id = {
            target: i_target for i_target, target in enumerate(target_classes)
        }

        # Print initialization info
        print(f"\n{'='*70}")
        print(f"Multi-Task Classification Reporter Initialized")
        print(f"{'='*70}")
        print(f"Experiment: {name}")
        print(f"Output Directory: {self.output_dir.absolute()}")
        print(f"Target Classes: {target_classes}")
        print(f"{'='*70}\n")

        # Initialize storage for multi-task metadata
        self.storage = MetricStorage(self.output_dir)

        # Initialize validator for multi-task validation
        self.validator = MetricValidator(required_metrics or [])
        self.auto_validate = auto_validate

        # Create individual reporters for each target
        self.reporters = []
        for target_class in target_classes:
            target_dir = self.output_dir / target_class
            reporter = SingleTaskClassificationReporter(
                name=f"{name}_{target_class}",
                output_dir=target_dir,
                required_metrics=required_metrics,
                auto_validate=auto_validate,
            )
            self.reporters.append(reporter)

        # Track multi-task metadata
        self.multi_task_results = defaultdict(list)
        self.config = {
            "name": name,
            "output_dir": str(self.output_dir),
            "target_classes": target_classes,
            "required_metrics": required_metrics,
        }

        # Save initial configuration
        self.storage.save(self.config, "config.json")

    def get_reporter(
        self, target: Optional[str] = None
    ) -> SingleTaskClassificationReporter:
        """
        Get the reporter for a specific target.

        Parameters
        ----------
        target : str, optional
            Target identifier. Uses first target if None.

        Returns
        -------
        SingleTaskClassificationReporter
            Reporter for the specified target
        """
        if target is None:
            target = self.target_classes[0]

        if target not in self.target_to_id:
            raise ValueError(
                f"Unknown target: {target}. Available: {list(self.target_to_id.keys())}"
            )

        target_idx = self.target_to_id[target]
        return self.reporters[target_idx]

    def start_fold(self, fold_idx: int, target: Optional[str] = None) -> None:
        """
        Start a new fold for the specified target(s).

        Parameters
        ----------
        fold_idx : int
            Fold index
        target : str, optional
            Target identifier. If None, starts fold for all targets.
        """
        if target is None:
            # Start fold for all targets
            for reporter in self.reporters:
                reporter.start_fold(fold_idx)
        else:
            reporter = self.get_reporter(target)
            reporter.start_fold(fold_idx)

    def calc_metrics(
        self,
        true_class: np.ndarray,
        pred_class: np.ndarray,
        pred_proba: Optional[np.ndarray] = None,
        labels: Optional[List[str]] = None,
        fold_idx: Optional[int] = None,
        show: bool = False,
        target: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Calculate all classification metrics for the specified target.

        Parameters
        ----------
        true_class : array-like
            True class labels
        pred_class : array-like
            Predicted class labels
        pred_proba : array-like, optional
            Predicted class probabilities
        labels : List[str], optional
            Class labels for display
        fold_idx : int, optional
            Fold index for cross-validation reporting
        show : bool, default False
            Whether to display results
        target : str, optional
            Target identifier

        Returns
        -------
        Dict[str, Any]
            Calculated metrics
        """
        reporter = self.get_reporter(target)

        # Calculate all metrics using the reporter's method
        metrics = reporter.calculate_all_metrics(
            y_true=true_class,
            y_pred=pred_class,
            y_proba=pred_proba,
            labels=labels,
            fold_idx=fold_idx,
            save=True,
            plot=not show,
        )

        # Track results for multi-task summary
        self.multi_task_results[target].append(
            {"fold": fold_idx, "metrics": metrics}
        )

        return metrics

    def add(self, obj: Any, path: str, target: Optional[str] = None) -> None:
        """
        Add an object to the specified target reporter.

        Parameters
        ----------
        obj : Any
            Object to add (figure, DataFrame, scalar, etc.)
        path : str
            Relative path for saving
        target : str, optional
            Target identifier to add the object to
        """
        reporter = self.get_reporter(target)
        reporter.add(obj, path)

    def end_fold(
        self, fold_idx: Optional[int] = None, target: Optional[str] = None
    ) -> None:
        """
        End fold for the specified target(s).

        Parameters
        ----------
        fold_idx : int, optional
            Fold index
        target : str, optional
            Target identifier. If None, ends fold for all targets.
        """
        if target is None:
            # End fold for all targets
            for reporter in self.reporters:
                reporter.end_fold(fold_idx)
        else:
            reporter = self.get_reporter(target)
            reporter.end_fold(fold_idx)

    def create_multi_task_summary(self) -> pd.DataFrame:
        """
        Create a summary table comparing metrics across all tasks.

        Returns
        -------
        pd.DataFrame
            Multi-task comparison summary
        """
        summaries = []

        for target_class, reporter in zip(self.target_classes, self.reporters):
            # Get summary for this target
            target_summary = reporter.create_summary()

            if not target_summary.empty:
                # Add target column
                target_summary["target"] = target_class
                summaries.append(target_summary)

        if summaries:
            # Combine all summaries
            multi_summary = pd.concat(summaries, ignore_index=True)

            # Save multi-task summary
            self.storage.save(multi_summary, "multi_task_summary.csv")

            return multi_summary
        else:
            return pd.DataFrame()

    def validate_all_targets(self) -> Dict[str, Any]:
        """
        Validate completeness for all targets.

        Returns
        -------
        Dict[str, Any]
            Validation report for all targets
        """
        validation_report = {"targets": {}, "complete": True, "summary": {}}

        for target_class, reporter in zip(self.target_classes, self.reporters):
            target_validation = reporter.validate_completeness()
            validation_report["targets"][target_class] = target_validation

            # Update overall completeness
            if not target_validation.get("complete", False):
                validation_report["complete"] = False

        # Add summary statistics
        validation_report["summary"] = {
            "total_targets": len(self.target_classes),
            "complete_targets": sum(
                1
                for v in validation_report["targets"].values()
                if v.get("complete", False)
            ),
        }

        # Save validation report
        self.storage.save(validation_report, "multi_task_validation.json")

        return validation_report

    def generate_comparison_report(self) -> Dict[str, Path]:
        """
        Generate a comparison report across all targets.

        Returns
        -------
        Dict[str, Path]
            Paths to generated comparison files
        """
        generated_files = {}

        # Create multi-task summary
        summary = self.create_multi_task_summary()

        # Prepare comparison data
        comparison_data = {
            "config": self.config,
            "targets": self.target_classes,
            "summary": summary.to_dict() if not summary.empty else {},
            "validation": self.validate_all_targets(),
            "individual_reports": {},
        }

        # Add individual target summaries
        for target_class, reporter in zip(self.target_classes, self.reporters):
            if reporter.fold_results:
                comparison_data["individual_reports"][target_class] = {
                    "summary": create_summary_statistics(
                        reporter.fold_results
                    ),
                    "n_folds": reporter.n_folds,
                }

        # Generate markdown comparison report
        comparison_path = self.output_dir / "multi_task_comparison.md"
        generate_markdown_report(
            comparison_data, comparison_path, include_plots=False
        )
        generated_files["comparison_report"] = comparison_path

        # Export for paper
        paper_dir = self.output_dir / "paper_export"
        paper_paths = export_for_paper(comparison_data, paper_dir)
        generated_files.update(paper_paths)

        return generated_files

    def summarize(
        self, n_round: int = 3, show: bool = True, target: Optional[str] = None
    ) -> Union[pd.DataFrame, Dict[str, pd.DataFrame]]:
        """
        Summarize results for the specified target or all targets.

        Parameters
        ----------
        n_round : int, default 3
            Number of decimal places for rounding
        show : bool, default True
            Whether to display summary
        target : str, optional
            Target identifier. If None, summarizes all targets.

        Returns
        -------
        Union[pd.DataFrame, Dict[str, pd.DataFrame]]
            Summary for specified target or all targets
        """
        if target is not None:
            # Summarize single target
            reporter = self.get_reporter(target)
            summary = reporter.create_summary()

            if show and not summary.empty:
                print(f"\nSummary for target '{target}':")
                print(summary.round(n_round).to_string())

            return summary
        else:
            # Summarize all targets
            summaries = {}

            for target_class, reporter in zip(
                self.target_classes, self.reporters
            ):
                summary = reporter.create_summary()
                summaries[target_class] = summary

                if show and not summary.empty:
                    print(f"\nSummary for target '{target_class}':")
                    print(summary.round(n_round).to_string())

            # Also show multi-task comparison
            if show:
                multi_summary = self.create_multi_task_summary()
                if not multi_summary.empty:
                    print("\nMulti-Task Comparison:")
                    print(multi_summary.round(n_round).to_string())

            return summaries

    def save(
        self,
        files_to_repro: Optional[List[str]] = None,
        meta_dict: Optional[Dict] = None,
        target: Optional[str] = None,
    ) -> Dict[str, Path]:
        """
        Save results for the specified target or all targets.

        Parameters
        ----------
        files_to_repro : List[str], optional
            Files to include in reproducibility package
        meta_dict : Dict, optional
            Metadata dictionary to include
        target : str, optional
            Target identifier. If None, saves all targets.

        Returns
        -------
        Dict[str, Path]
            Paths to saved files
        """
        saved_paths = {}

        if target is not None:
            # Save single target
            reporter = self.get_reporter(target)
            target_paths = reporter.save()
            saved_paths[target] = target_paths
        else:
            # Save all targets
            for target_class, reporter in zip(
                self.target_classes, self.reporters
            ):
                target_paths = reporter.save()
                saved_paths[target_class] = target_paths

            # Generate multi-task comparison report
            print("\n" + "=" * 70)
            print("GENERATING MULTI-TASK COMPARISON")
            print("=" * 70)
            comparison_paths = self.generate_comparison_report()
            saved_paths["comparison"] = comparison_paths

            # Save multi-task metadata
            if meta_dict:
                self.storage.save(meta_dict, "multi_task_metadata.json")

            # Save file list for reproducibility
            if files_to_repro:
                self.storage.save(
                    {"files": files_to_repro}, "reproducibility_files.json"
                )

            # Create final multi-task summary
            validation = self.validate_all_targets()

            # Print final summary
            print("\n" + "=" * 70)
            print("📊 MULTI-TASK CLASSIFICATION RESULTS")
            print("=" * 70)
            print(f"📁 Main Directory: {self.output_dir.absolute()}")
            print(f"\nTargets Processed: {len(self.target_classes)}")
            for i, target_class in enumerate(self.target_classes):
                status = (
                    "✅"
                    if validation["targets"]
                    .get(target_class, {})
                    .get("complete", False)
                    else "⚠️"
                )
                print(
                    f"  {status} {target_class}: {self.output_dir / target_class}/"
                )

            print(f"\nKey Files:")
            print(
                f"  📄 Comparison Report:    {self.output_dir / 'multi_task_comparison.md'}"
            )
            print(
                f"  📊 Multi-Task Summary:   {self.output_dir / 'multi_task_summary.csv'}"
            )
            print(
                f"  ✅ Validation Report:    {self.output_dir / 'multi_task_validation.json'}"
            )

            if validation["complete"]:
                print(f"\n✅ All targets complete with required metrics!")
            else:
                complete = validation["summary"]["complete_targets"]
                total = validation["summary"]["total_targets"]
                print(
                    f"\n⚠️  {complete}/{total} targets complete - check validation report"
                )

            print("=" * 70)

        return saved_paths

    def plot_and_save_conf_mats(
        self,
        plt_module,
        extend_ratio: float = 1.0,
        colorbar: bool = True,
        confmat_plt_config: Optional[Dict] = None,
        sci_notation_kwargs: Optional[Dict] = None,
        target: Optional[str] = None,
    ) -> None:
        """
        Plot and save confusion matrices for the specified target.

        This method is provided for backward compatibility.
        The new system handles plotting automatically in calc_confusion_matrix.

        Parameters
        ----------
        plt_module : module
            Matplotlib pyplot module (ignored - uses internal plotting)
        extend_ratio : float, default 1.0
            Ratio for extending plot dimensions
        colorbar : bool, default True
            Whether to include colorbar
        confmat_plt_config : Dict, optional
            Configuration for confusion matrix plotting
        sci_notation_kwargs : Dict, optional
            Scientific notation formatting arguments
        target : str, optional
            Target identifier
        """
        # This is handled automatically by the reporter's calc_confusion_matrix
        # Just log that it was called for compatibility
        if target:
            print(f"Confusion matrices already saved for target '{target}'")
        else:
            print("Confusion matrices already saved for all targets")


def main():
    """
    Demonstrate usage of enhanced MultipleTasksClassificationReporter.

    This example shows the new features:
    - Modular reporter_utils integration
    - Path-based storage
    - Automatic validation
    - Multi-task comparison reports
    - Publication-ready exports
    """
    import numpy as np
    from sklearn.datasets import make_classification
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split

    print("=== Enhanced Multi-Task Classification Reporter Demo ===\n")

    # Create multi-target reporter
    target_classes = ["binary_balanced", "binary_imbalanced", "multiclass"]
    multi_reporter = MultipleTasksClassificationReporter(
        name="classification_comparison",
        output_dir="./.dev/multi_classification_v2_demo",
        target_classes=target_classes,
        required_metrics=["balanced_accuracy", "mcc", "confusion_matrix"],
        auto_validate=True,
    )

    # Task 1: Balanced binary classification
    print("\n--- Task 1: Balanced Binary Classification ---")
    X1, y1 = make_classification(
        n_samples=500,
        n_features=20,
        n_informative=15,
        n_redundant=5,
        n_classes=2,
        weights=[0.5, 0.5],
        random_state=42,
    )
    X1_train, X1_test, y1_train, y1_test = train_test_split(
        X1, y1, test_size=0.3, random_state=42
    )

    clf1 = RandomForestClassifier(n_estimators=100, random_state=42)
    clf1.fit(X1_train, y1_train)

    metrics1 = multi_reporter.calc_metrics(
        true_class=y1_test,
        pred_class=clf1.predict(X1_test),
        pred_proba=clf1.predict_proba(X1_test),
        labels=["Class 0", "Class 1"],
        fold_idx=0,
        target="binary_balanced",
    )
    print(f"Balanced Accuracy: {metrics1['balanced_accuracy']:.3f}")
    print(f"MCC: {metrics1['mcc']:.3f}")

    # Task 2: Imbalanced binary classification
    print("\n--- Task 2: Imbalanced Binary Classification ---")
    X2, y2 = make_classification(
        n_samples=500,
        n_features=20,
        n_informative=15,
        n_redundant=5,
        n_classes=2,
        weights=[0.9, 0.1],
        random_state=43,
    )
    X2_train, X2_test, y2_train, y2_test = train_test_split(
        X2, y2, test_size=0.3, random_state=42
    )

    clf2 = RandomForestClassifier(n_estimators=100, random_state=42)
    clf2.fit(X2_train, y2_train)

    metrics2 = multi_reporter.calc_metrics(
        true_class=y2_test,
        pred_class=clf2.predict(X2_test),
        pred_proba=clf2.predict_proba(X2_test),
        labels=["Majority", "Minority"],
        fold_idx=0,
        target="binary_imbalanced",
    )
    print(f"Balanced Accuracy: {metrics2['balanced_accuracy']:.3f}")
    print(f"MCC: {metrics2['mcc']:.3f}")

    # Task 3: Multiclass classification
    print("\n--- Task 3: Multiclass Classification ---")
    X3, y3 = make_classification(
        n_samples=500,
        n_features=20,
        n_informative=15,
        n_redundant=5,
        n_classes=3,
        n_clusters_per_class=2,
        random_state=44,
    )
    X3_train, X3_test, y3_train, y3_test = train_test_split(
        X3, y3, test_size=0.3, random_state=42
    )

    clf3 = RandomForestClassifier(n_estimators=100, random_state=42)
    clf3.fit(X3_train, y3_train)

    # For multiclass, we need to handle probabilities differently
    y3_proba = clf3.predict_proba(X3_test)

    metrics3 = multi_reporter.calc_metrics(
        true_class=y3_test,
        pred_class=clf3.predict(X3_test),
        pred_proba=y3_proba,
        labels=["Class A", "Class B", "Class C"],
        fold_idx=0,
        target="multiclass",
    )
    print(f"Balanced Accuracy: {metrics3['balanced_accuracy']:.3f}")
    print(f"MCC: {metrics3['mcc']:.3f}")

    # Add custom metadata for each task
    multi_reporter.add(
        {"model": "RandomForest", "balance": "50/50"},
        "metadata.json",
        target="binary_balanced",
    )
    multi_reporter.add(
        {"model": "RandomForest", "balance": "90/10"},
        "metadata.json",
        target="binary_imbalanced",
    )
    multi_reporter.add(
        {"model": "RandomForest", "n_classes": 3},
        "metadata.json",
        target="multiclass",
    )

    # Save all results and generate reports
    print("\n--- Saving Results and Generating Reports ---")
    saved_paths = multi_reporter.save(
        meta_dict={
            "experiment": "classification_comparison",
            "models": "RandomForest",
            "cv_folds": 1,
        }
    )

    print("\n=== Demo Complete! ===")
    print("\nFeatures Demonstrated:")
    print("✓ Multi-task classification with different scenarios")
    print("✓ Automatic metric calculation and validation")
    print("✓ Path-based file organization")
    print("✓ Multi-task comparison reports")
    print("✓ Publication-ready exports")
    print("✓ Modular reporter_utils integration")

    return multi_reporter


if __name__ == "__main__":
    reporter = main()

# EOF
