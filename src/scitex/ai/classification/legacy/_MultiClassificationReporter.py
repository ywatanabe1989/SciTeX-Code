#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-07 11:00:00 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/SciTeX-Code/src/scitex/ai/classification/_MultiClassificationReporter.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/ai/classification/_MultiClassificationReporter.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Multi-target classification reporter for handling multiple classification targets.

This module provides the MultiClassificationReporter class for managing
classification reports across multiple targets or conditions.
Now updated to use the modular reporter_utils system.
"""

import os as _os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import numpy as np
import pandas as pd
from collections import defaultdict


# Import reporter utilities for enhanced functionality
from .reporter_utils import (
    MetricStorage,
    MetricValidator,
    create_summary_table,
    generate_markdown_report,
    create_summary_statistics
)


class MultipleTasksClassificationReporter:
    """
    Reporter for handling classification metrics across multiple targets.

    This class manages multiple SingleTaskClassificationReporter instances, one for each
    target class or condition, enabling parallel reporting and comparison.
    Now enhanced with modular reporter_utils for better organization.

    Parameters
    ----------
    save_dir : str
        Base directory path for saving results
    target_classes : List[str], optional
        List of target class names or identifiers, default is [""]

    Attributes
    ----------
    target_to_id : Dict[str, int]
        Mapping from target names to their indices
    reporters : List[SingleTaskClassificationReporter]
        List of individual classification reporters for each target
    storage : MetricStorage
        Central storage manager for multi-task metadata
    """

    def __init__(self, save_dir: str, target_classes: List[str] = None):
        # Convert to Path for better path handling
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)
        
        if target_classes is None:
            target_classes = [""]
            save_dirs = [self.save_dir]
        else:
            save_dirs = [
                self.save_dir / target_class
                for target_class in target_classes
            ]
        
        self.target_classes = target_classes
        self.target_to_id = {
            target: i_target for i_target, target in enumerate(target_classes)
        }
        
        # Initialize central storage for multi-task metadata
        self.storage = MetricStorage(self.save_dir)
        
        # Initialize validator with default required metrics
        self.validator = MetricValidator(
            required_metrics=['balanced_accuracy', 'mcc', 'confusion_matrix']
        )
        
        # Import the enhanced version if available, fallback to original
        try:
            from ._SingleClassificationReporter_v2 import \
                SingleTaskClassificationReporter
        except ImportError:
            from ._SingleClassificationReporter import \
                SingleTaskClassificationReporter
        
        # Create reporters with enhanced configuration
        self.reporters = []
        for i, (save_dir, target_class) in enumerate(zip(save_dirs, target_classes)):
            # Create reporter with proper configuration
            if hasattr(SingleTaskClassificationReporter, '__init__') and \
               'name' in SingleTaskClassificationReporter.__init__.__code__.co_varnames:
                # New interface with name parameter
                reporter = SingleTaskClassificationReporter(
                    name=target_class if target_class else "default",
                    output_dir=save_dir
                )
            else:
                # Legacy interface
                reporter = SingleTaskClassificationReporter(str(save_dir))
            self.reporters.append(reporter)
        
        # Track multi-task results
        self.multi_task_results = defaultdict(list)

    def add(self, obj_name: str, obj: Any, target: Optional[str] = None):
        """
        Add an object to the specified target reporter.

        Parameters
        ----------
        obj_name : str
            Name identifier for the object
        obj : Any
            Object to add (figure, DataFrame, scalar, etc.)
        target : str, optional
            Target identifier to add the object to
        """
        target_idx = self.target_to_id[target]
        self.reporters[target_idx].add(obj_name, obj)

    def calc_metrics(
        self,
        true_class,
        pred_class,
        pred_proba,
        labels: Optional[List[str]] = None,
        fold_idx: Optional[int] = None,
        show: bool = True,
        auc_plot_config: Optional[Dict] = None,
        target: Optional[str] = None,
    ):
        """
        Calculate classification metrics for the specified target.

        Parameters
        ----------
        true_class : array-like
            True class labels
        pred_class : array-like
            Predicted class labels
        pred_proba : array-like
            Predicted class probabilities
        labels : List[str], optional
            Class labels for display
        fold_idx : int, optional
            Fold index for cross-validation reporting
        show : bool, default True
            Whether to display results
        auc_plot_config : Dict, optional
            Configuration for AUC plotting
        target : str, optional
            Target identifier
        """
        if auc_plot_config is None:
            auc_plot_config = {
                "figsize": (7, 7),
                "labelsize": 8,
                "fontsize": 7,
                "legendfontsize": 6,
                "tick_size": 0.8,
                "tick_width": 0.2,
            }

        target_idx = self.target_to_id[target]
        reporter = self.reporters[target_idx]
        
        # Check if reporter has new interface
        if hasattr(reporter, 'calculate_all_metrics'):
            # Use new comprehensive method
            metrics = reporter.calculate_all_metrics(
                y_true=true_class,
                y_pred=pred_class,
                y_proba=pred_proba,
                labels=labels,
                fold_idx=fold_idx,
                save=True,
                plot=not show
            )
            # Track results
            self.multi_task_results[target].append({
                'fold': fold_idx,
                'metrics': metrics
            })
        else:
            # Use legacy interface
            reporter.calc_metrics(
                true_class,
                pred_class,
                pred_proba,
                labels=labels,
                fold_idx=fold_idx,
                show=show,
                auc_plot_config=auc_plot_config,
            )

    def summarize(
        self,
        n_round: int = 3,
        show: bool = False,
        target: Optional[str] = None,
    ):
        """
        Summarize results for the specified target.

        Parameters
        ----------
        n_round : int, default 3
            Number of decimal places for rounding
        show : bool, default False
            Whether to display summary
        target : str, optional
            Target identifier
        """
        target_idx = self.target_to_id[target]
        self.reporters[target_idx].summarize(
            n_round=n_round,
            show=show,
        )

    def save(
        self,
        files_to_repro: Optional[List[str]] = None,
        meta_dict: Optional[Dict] = None,
        target: Optional[str] = None,
    ):
        """
        Save results for the specified target.

        Parameters
        ----------
        files_to_repro : List[str], optional
            Files to include in reproducibility package
        meta_dict : Dict, optional
            Metadata dictionary to include
        target : str, optional
            Target identifier
        """
        if target is not None:
            # Save specific target
            target_idx = self.target_to_id[target]
            reporter = self.reporters[target_idx]
            
            # Use new save interface if available
            if hasattr(reporter, 'save') and reporter.save.__code__.co_argcount == 1:
                # New interface - save() takes no arguments
                reporter.save()
                # Save metadata separately if provided
                if meta_dict:
                    self.storage.save(meta_dict, f"{target}_metadata.json")
            else:
                # Legacy interface
                reporter.save(
                    files_to_repro=files_to_repro,
                    meta_dict=meta_dict,
                )
        else:
            # Save all targets
            for target_name, reporter in zip(self.target_classes, self.reporters):
                if hasattr(reporter, 'save'):
                    if reporter.save.__code__.co_argcount == 1:
                        reporter.save()
                    else:
                        reporter.save(
                            files_to_repro=files_to_repro,
                            meta_dict=meta_dict,
                        )
            
            # Create multi-task summary if we have results
            if self.multi_task_results:
                self._create_multi_task_summary()
            
            # Save global metadata
            if meta_dict:
                self.storage.save(meta_dict, "global_metadata.json")
            if files_to_repro:
                self.storage.save(
                    {'files': files_to_repro},
                    'reproducibility_files.json'
                )
    
    def _create_multi_task_summary(self):
        """
        Create a summary comparing all tasks.
        """
        summaries = []
        for target_class in self.target_classes:
            if target_class in self.multi_task_results:
                results = self.multi_task_results[target_class]
                if results:
                    summary = pd.DataFrame(results)
                    summary['target'] = target_class
                    summaries.append(summary)
        
        if summaries:
            multi_summary = pd.concat(summaries, ignore_index=True)
            self.storage.save(multi_summary, 'multi_task_summary.csv')

    def plot_and_save_conf_mats(
        self,
        plt_module,
        extend_ratio: float = 1.0,
        colorbar: bool = True,
        confmat_plt_config: Optional[Dict] = None,
        sci_notation_kwargs: Optional[Dict] = None,
        target: Optional[str] = None,
    ):
        """
        Plot and save confusion matrices for the specified target.

        Parameters
        ----------
        plt_module : module
            Matplotlib pyplot module
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
        target_idx = self.target_to_id[target]
        self.reporters[target_idx].plot_and_save_conf_mats(
            plt_module,
            extend_ratio=extend_ratio,
            colorbar=colorbar,
            confmat_plt_config=confmat_plt_config,
            sci_notation_kwargs=sci_notation_kwargs,
        )


def main():
    """
    Demonstrate usage of MultipleTasksClassificationReporter.

    This function shows how to use MultipleTasksClassificationReporter for
    managing multiple classification tasks simultaneously.

    Example Output:
    ---------------
    === MultipleTasksClassificationReporter Usage Example ===

    Created MultipleTasksClassificationReporter with targets: ['binary_task', 'weighted_task']
    Available reporters: 2
    Target mapping: {'binary_task': 0, 'weighted_task': 1}

    Dataset: 350 training, 150 test samples

    --- Task 1: Binary Classification ---
    Balanced Accuracy in fold#1: 0.906
    MCC in fold#1: 0.813

    Confusion Matrix in fold#1:
             Class 0  Class 1
    Class 0       63        8
    Class 1        6       73

    ROC AUC in fold#1: 0.961

    --- Task 2: Weighted Classification (Same data, different evaluation) ---
    Balanced Accuracy in fold#1: 0.906
    MCC in fold#1: 0.813

    --- Saving Results ---
    Results saved to: ./.dev/multi_classification_example
    Task 1 (Binary): Balanced Acc = 0.906, MCC = 0.813, ROC AUC = 0.961
    Task 2 (Weighted): Balanced Acc = 0.906, MCC = 0.813
    Each task has its own subdirectory with separate results.

    Directory Structure Created:
    ----------------------------
    .dev/multi_classification_example/
    ├── binary_task/
    │   ├── ROC_fig.pkl
    │   ├── PRE_REC_fig.pkl
    │   ├── task_metadata.pkl
    │   └── binary_task_summary.yaml
    └── weighted_task/
        ├── task_metadata.pkl
        └── weighted_task_summary.yaml

    Features Demonstrated:
    ----------------------
    1. Multiple task management with separate save directories
    2. Target-specific result tracking and organization
    3. Independent metric calculation per task
    4. Separate metadata and result saving per task
    5. Task-specific configuration and evaluation
    6. Parallel processing of different classification scenarios

    Use Cases:
    ----------
    - Cross-validation with different folds
    - Multiple classification targets (multi-label)
    - Different evaluation criteria on same data
    - A/B testing of classification approaches
    - Ensemble method comparison
    """
    import matplotlib

    matplotlib.use(
        "Agg"
    )  # Use non-interactive backend for headless environments
    import matplotlib.pyplot as plt
    import numpy as np
    from sklearn.datasets import make_classification
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split

    print("=== MultipleTasksClassificationReporter Usage Example ===\n")

    # Create multi-target reporter for two different tasks
    save_dir = "./.dev/multi_classification_example"
    target_classes = ["binary_task", "weighted_task"]
    multi_reporter = MultipleTasksClassificationReporter(
        save_dir, target_classes
    )

    print(
        f"Created MultipleTasksClassificationReporter with targets: {target_classes}"
    )
    print(f"Available reporters: {len(multi_reporter.reporters)}")
    print(f"Target mapping: {multi_reporter.target_to_id}")

    # Generate sample data for both tasks
    X, y = make_classification(
        n_samples=500,
        n_features=15,
        n_informative=8,
        n_redundant=7,
        n_classes=2,
        random_state=42,
    )

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )

    # Train classifier
    clf = RandomForestClassifier(n_estimators=50, random_state=42)
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    y_pred_proba = clf.predict_proba(X_test)[:, 1]

    labels = ["Class 0", "Class 1"]
    fold_idx = 1

    print(f"\nDataset: {len(X_train)} training, {len(X_test)} test samples")

    # Test Task 1: Binary classification task
    print("\n--- Task 1: Binary Classification ---")
    target = "binary_task"

    # Calculate metrics for first target
    balanced_acc_1 = multi_reporter.reporters[0].calc_balanced_accuracy(
        y_test, y_pred, fold_idx, show=True
    )
    mcc_1 = multi_reporter.reporters[0].calc_mcc(
        y_test, y_pred, fold_idx, show=True
    )
    conf_mat_1 = multi_reporter.reporters[0].calc_conf_mat(
        y_test, y_pred, labels, fold_idx, show=True
    )
    auc_1 = multi_reporter.reporters[0].calc_aucs(
        y_test, y_pred_proba, labels, fold_idx, show=True
    )

    # Add custom data for first target
    multi_reporter.add(
        "task_metadata",
        {"task_type": "standard_binary", "model": "RandomForest"},
        target,
    )

    # Test Task 2: Weighted classification task (simulate different evaluation)
    print(
        "\n--- Task 2: Weighted Classification (Same data, different evaluation) ---"
    )
    target = "weighted_task"

    # Use same predictions but evaluate differently
    balanced_acc_2 = multi_reporter.reporters[1].calc_balanced_accuracy(
        y_test, y_pred, fold_idx, show=True
    )
    mcc_2 = multi_reporter.reporters[1].calc_mcc(
        y_test, y_pred, fold_idx, show=True
    )

    # Add custom data for second target
    multi_reporter.add(
        "task_metadata",
        {"task_type": "weighted_binary", "model": "RandomForest"},
        target,
    )

    # Save results for both tasks
    print("\n--- Saving Results ---")

    # Save for binary task
    meta_dict_1 = {
        "binary_task_summary.yaml": {
            "balanced_accuracy": float(balanced_acc_1),
            "mcc": float(mcc_1),
            "roc_auc": float(auc_1),
        }
    }
    multi_reporter.save(meta_dict=meta_dict_1, target="binary_task")

    # Save for weighted task
    meta_dict_2 = {
        "weighted_task_summary.yaml": {
            "balanced_accuracy": float(balanced_acc_2),
            "mcc": float(mcc_2),
        }
    }
    multi_reporter.save(meta_dict=meta_dict_2, target="weighted_task")

    print(f"\n=== Multi-task Classification Example Completed! ===")
    print(f"Results saved to: {save_dir}")
    print(
        f"Task 1 (Binary): Balanced Acc = {balanced_acc_1:.3f}, MCC = {mcc_1:.3f}, ROC AUC = {auc_1:.3f}"
    )
    print(
        f"Task 2 (Weighted): Balanced Acc = {balanced_acc_2:.3f}, MCC = {mcc_2:.3f}"
    )
    print(f"Each task has its own subdirectory with separate results.")


if __name__ == "__main__":
    main()

# EOF
