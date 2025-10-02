#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-07 09:45:36 (ywatanabe)"
# File: /ssh:sp:/data/gpfs/projects/punim2354/ywatanabe/SciTeX-Code/src/scitex/ai/classification/_SingleClassificationReporter.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

# Time-stamp: "2025-09-05 06:55:00 (ywatanabe)"

"""
Single classification reporter for handling individual classification tasks.

This module provides the ClassificationReporter class for comprehensive
classification performance evaluation and reporting.
"""


import os as _os
import random as _random
from collections import defaultdict as _defaultdict
from pprint import pprint as _pprint
from typing import Any, Dict, List, Optional

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as _plt
import numpy as _np
import pandas as _pd
import torch as _torch
from scitex.repro import fix_seeds as _fix_seeds
from sklearn.metrics import balanced_accuracy_score as _balanced_accuracy_score
from sklearn.metrics import classification_report as _classification_report
from sklearn.metrics import confusion_matrix as _confusion_matrix
from sklearn.metrics import matthews_corrcoef as _matthews_corrcoef


class SingleTaskClassificationReporter:
    """
    Comprehensive classification reporter for single target classification.

    Saves the following metrics under save_dir:
    - Balanced Accuracy
    - MCC (Matthews Correlation Coefficient)
    - Confusion Matrix
    - Classification Report
    - ROC AUC score / curve
    - PRE-REC AUC score / curve

    Parameters
    ----------
    save_dir : str
        Directory path for saving results and metrics

    Attributes
    ----------
    save_dir : str
        Directory path for saving results
    folds_dict : defaultdict
        Dictionary storing results from different folds

    Usage Examples
    --------------
    Basic usage with automatic saving:
    >>> reporter = SingleTaskClassificationReporter("./results")
    >>> 
    >>> # Calculate metrics (these are automatically added internally)
    >>> balanced_acc = reporter.calc_balanced_accuracy(y_true, y_pred, fold_idx=1)
    >>> mcc = reporter.calc_mcc(y_true, y_pred, fold_idx=1)
    >>> conf_mat = reporter.calc_conf_mat(y_true, y_pred, labels, fold_idx=1)
    >>> clf_report = reporter.calc_clf_report(
    ...     y_true, y_pred, labels, balanced_acc, mcc, fold_idx=1
    ... )
    >>> roc_auc = reporter.calc_aucs(y_true, y_proba, labels, fold_idx=1)
    >>> 
    >>> # Save everything (auto-saves all calculated metrics)
    >>> reporter.save()

    Manual addition of custom objects:
    >>> # Add custom figures
    >>> fig, ax = plt.subplots()
    >>> ax.plot(performance_over_time)
    >>> reporter.add("learning_curves", fig)
    >>> 
    >>> # Add custom DataFrames
    >>> summary_df = pd.DataFrame({
    ...     "patient": patient_ids,
    ...     "accuracy": accuracies,
    ...     "mcc": mccs
    ... })
    >>> reporter.add("patient_summary", summary_df)
    >>> 
    >>> # Add custom dictionaries/metadata
    >>> metadata = {
    ...     "experiment_date": "2025-09-07",
    ...     "model": "RandomForest",
    ...     "n_features": 100
    ... }
    >>> reporter.add("experiment_metadata", metadata)
    >>> 
    >>> # Save with metadata
    >>> reporter.save(meta_dict={"metadata.yaml": metadata})

    Manual saving of specific objects outside reporter:
    >>> import scitex as stx
    >>> 
    >>> # Save DataFrames directly
    >>> stx.io.save(summary_df, "./results/summary.csv")
    >>> 
    >>> # Save figures directly
    >>> stx.io.save(fig, "./results/performance.jpg")
    >>> 
    >>> # Save dictionaries as JSON/YAML
    >>> stx.io.save(metadata, "./results/metadata.yaml")
    """

    def __init__(self, save_dir: str, required_metrics: Optional[List[str]] = None):
        self.save_dir = save_dir
        self.folds_dict = _defaultdict(list)
        _fix_seeds(os=_os, random=_random, np=_np, torch=_torch, verbose=False)
        
        # Track required metrics for validation
        self.required_metrics = required_metrics or [
            'balanced_accuracy',
            'mcc', 
            'confusion_matrix',
            'classification_report',
            'roc_auc'  # for binary classification
        ]
        self.collected_metrics = _defaultdict(set)  # Track what's been collected per fold

    def add(self, obj: Any, path: str):
        """
        Add an object to the reporter with a specified relative path.
        
        The object will be saved to: {self.save_dir}/{path}
        File type is automatically determined from the extension in the path.
        
        Parameters
        ----------
        obj : Any
            Object to save (figure, DataFrame, dict, array, scalar, etc.)
        path : str
            Relative path where the object should be saved, including filename 
            and extension. Can include subdirectories.
            
        Examples
        --------
        Basic usage with different object types:
        
        >>> reporter = SingleTaskClassificationReporter("./results")
        >>> 
        >>> # Save figure to specific location with format
        >>> fig, ax = plt.subplots()
        >>> ax.plot([1, 2, 3])
        >>> reporter.add(fig, "figures/roc_curve_fold_01.jpg")
        >>> reporter.add(fig, "figures/roc_curve_fold_01.png")  # Different format
        >>> reporter.add(fig, "figures/roc_curve_fold_01.pdf")  # Vector format
        >>> 
        >>> # Save DataFrame as CSV or Excel
        >>> df = pd.DataFrame({'accuracy': [0.95, 0.93], 'fold': [1, 2]})
        >>> reporter.add(df, "metrics/results.csv")
        >>> reporter.add(df, "metrics/results.xlsx")  # Excel format
        >>> 
        >>> # Save dictionary as JSON or YAML
        >>> config = {'model': 'RF', 'n_estimators': 100}
        >>> reporter.add(config, "configs/experiment.json")
        >>> reporter.add(config, "configs/experiment.yaml")
        >>> 
        >>> # Save numpy array
        >>> embeddings = np.random.rand(100, 50)
        >>> reporter.add(embeddings, "embeddings/features.npy")
        >>> 
        >>> # Save scalar metrics
        >>> reporter.add(0.95, "metrics/accuracy.pkl")
        >>> reporter.add({'acc': 0.95, 'mcc': 0.82}, "metrics/fold_01_metrics.json")
        >>> 
        >>> # Organize by folds in subdirectories
        >>> for fold_idx in range(1, 6):
        ...     fig = create_confusion_matrix(y_true, y_pred)
        ...     reporter.add(fig, f"confusion_matrices/fold_{fold_idx:02d}.jpg")
        ...     
        ...     metrics = calculate_metrics(y_true, y_pred)
        ...     reporter.add(metrics, f"metrics/fold_{fold_idx:02d}.json")
        >>> 
        >>> # Custom nested organization
        >>> reporter.add(fig, "visualizations/training/loss_curve.png")
        >>> reporter.add(df, "tables/patient_wise/summary.csv")
        >>> reporter.add(model_weights, "models/checkpoints/best_model.pth")
        >>> 
        >>> # When ready, save all added objects
        >>> reporter.save()
        
        Notes
        -----
        - Paths are relative to self.save_dir
        - Directories are created automatically if they don't exist
        - File format is determined by extension (e.g., .jpg, .csv, .json)
        - The extension must be compatible with the object type
        - Objects are accumulated and saved when save() is called
        
        Supported formats by object type:
        - Figures: .jpg, .png, .pdf, .svg, .eps
        - DataFrames: .csv, .xlsx, .json, .pkl
        - Dicts/Lists: .json, .yaml, .pkl
        - NumPy arrays: .npy, .npz, .csv
        - Torch tensors: .pt, .pth
        - Any object: .pkl (pickle)
        """
        assert isinstance(path, str), "Path must be a string"
        
        # Store both object and its intended path
        if path not in self.folds_dict:
            self.folds_dict[path] = []
        self.folds_dict[path].append(obj)

    def calc_balanced_accuracy(
        self, true_class, pred_class, fold_idx: int, show: bool = False
    ) -> float:
        """
        Calculate balanced accuracy score and automatically save it.

        Parameters
        ----------
        true_class : array-like
            True class labels
        pred_class : array-like
            Predicted class labels
        fold_idx : int
            Fold index for reporting
        show : bool, default False
            Whether to print the result

        Returns
        -------
        float
            Balanced accuracy score
        """
        balanced_acc = _balanced_accuracy_score(true_class, pred_class)
        if show:
            print(
                f"\nBalanced Accuracy in fold#{fold_idx}: {balanced_acc:.3f}\n"
            )
        
        # Automatically save to standard location as JSON for readability
        metric_data = {
            'metric': 'balanced_accuracy',
            'value': float(balanced_acc),
            'fold': fold_idx
        }
        self.add(metric_data, f"metrics/balanced_accuracy_fold_{fold_idx:02d}.json")
        
        # Track that this metric was collected for this fold
        self.collected_metrics[fold_idx].add('balanced_accuracy')
        
        return balanced_acc

    def calc_bACC(
        self, true_class, pred_class, fold_idx: int, show: bool = False
    ) -> float:
        """Balanced ACC (legacy alias for calc_balanced_accuracy)"""
        return self.calc_balanced_accuracy(
            true_class, pred_class, fold_idx, show
        )

    def calc_mcc(
        self, true_class, pred_class, fold_idx: int, show: bool = False
    ) -> float:
        """
        Calculate Matthews Correlation Coefficient.

        Parameters
        ----------
        true_class : array-like
            True class labels
        pred_class : array-like
            Predicted class labels
        fold_idx : int
            Fold index for reporting
        show : bool, default False
            Whether to print the result

        Returns
        -------
        float
            Matthews Correlation Coefficient
        """
        mcc = float(_matthews_corrcoef(true_class, pred_class))
        if show:
            print(f"\nMCC in fold#{fold_idx}: {mcc:.3f}\n")
        
        # Automatically save to standard location as JSON for readability
        metric_data = {
            'metric': 'mcc',
            'value': float(mcc),
            'fold': fold_idx
        }
        self.add(metric_data, f"metrics/mcc_fold_{fold_idx:02d}.json")
        
        # Track that this metric was collected for this fold
        self.collected_metrics[fold_idx].add('mcc')
        
        return mcc

    def calc_conf_mat(
        self,
        true_class,
        pred_class,
        labels: List[str],
        fold_idx: int,
        show: bool = False,
    ) -> _pd.DataFrame:
        """
        Calculate confusion matrix.

        This method assumes unique classes of true_class and pred_class are the same.

        Parameters
        ----------
        true_class : array-like
            True class labels
        pred_class : array-like
            Predicted class labels
        labels : List[str]
            Class labels for display
        fold_idx : int
            Fold index for reporting
        show : bool, default False
            Whether to print the confusion matrix

        Returns
        -------
        pd.DataFrame
            Confusion matrix as DataFrame
        """
        conf_mat = _pd.DataFrame(
            data=_confusion_matrix(
                true_class, pred_class, labels=_np.arange(len(labels))
            ),
            columns=labels,
        ).set_index(_pd.Series(list(labels)))

        if show:
            print(f"\nConfusion Matrix in fold#{fold_idx}:\n")
            _pprint(conf_mat)
            print()

        # Automatically save confusion matrix
        self.add(conf_mat, f"confusion_matrices/conf_mat_fold_{fold_idx:02d}.csv")
        
        # Also keep for plotting (backward compatibility)
        if "conf_mat_data" not in self.folds_dict:
            self.folds_dict["conf_mat_data"] = []
        self.folds_dict["conf_mat_data"].append(conf_mat)
        
        # Track that this metric was collected for this fold
        self.collected_metrics[fold_idx].add('confusion_matrix')

        return conf_mat

    def calc_clf_report(
        self,
        true_class,
        pred_class,
        labels: List[str],
        balanced_acc: float,
        mcc: float,
        fold_idx: int,
        show: bool = False,
    ) -> _pd.DataFrame:
        """
        Generate classification report.

        Parameters
        ----------
        true_class : array-like
            True class labels
        pred_class : array-like
            Predicted class labels
        labels : List[str]
            Class labels for display
        balanced_acc : float
            Balanced accuracy score
        mcc : float
            Matthews Correlation Coefficient score
        fold_idx : int
            Fold index for reporting
        show : bool, default False
            Whether to print the report

        Returns
        -------
        pd.DataFrame
            Classification report as DataFrame
        """
        clf_report = _pd.DataFrame(
            _classification_report(
                true_class,
                pred_class,
                labels=_np.arange(len(labels)),
                target_names=labels,
                output_dict=True,
            )
        )

        clf_report["balanced accuracy"] = balanced_acc
        clf_report["mcc"] = mcc
        clf_report = _pd.concat(
            [
                clf_report[labels],
                clf_report[
                    ["balanced accuracy", "mcc", "macro avg", "weighted avg"]
                ],
            ],
            axis=1,
        )
        clf_report = clf_report.round(3)
        clf_report["index"] = clf_report.index
        clf_report.loc["support", "index"] = "sample size"
        clf_report.set_index("index", drop=True, inplace=True)
        clf_report.index.name = None
        if show:
            print(f"\nClassification Report for fold#{fold_idx}:\n")
            _pprint(clf_report)
            print()

        # Automatically save classification report
        self.add(clf_report, f"reports/classification_report_fold_{fold_idx:02d}.csv")
        
        # Track that this metric was collected for this fold
        self.collected_metrics[fold_idx].add('classification_report')

        return clf_report
    
    def summarize_metrics(self):
        """
        Calculate and save summary statistics across all folds.
        
        This method collects all metrics that have been saved and computes
        mean and std across folds, saving them as summary files.
        
        Examples
        --------
        >>> reporter = SingleTaskClassificationReporter("./results")
        >>> 
        >>> # Run multiple folds
        >>> for fold_idx in range(1, 6):
        ...     balanced_acc = reporter.calc_balanced_accuracy(y_true, y_pred, fold_idx)
        ...     mcc = reporter.calc_mcc(y_true, y_pred, fold_idx)
        ... 
        >>> # Calculate and save summaries
        >>> reporter.summarize_metrics()
        
        Notes
        -----
        Creates the following summary files:
        - metrics/summary_balanced_accuracy.json (mean, std, all values)
        - metrics/summary_mcc.json
        - reports/summary_classification_report.csv (averaged across folds)
        """
        import json
        import glob
        
        # Summarize scalar metrics
        metrics_dir = _os.path.join(self.save_dir, "metrics")
        if _os.path.exists(metrics_dir):
            # Balanced accuracy
            ba_files = sorted(glob.glob(_os.path.join(metrics_dir, "balanced_accuracy_fold_*.json")))
            if ba_files:
                ba_values = []
                for f in ba_files:
                    with open(f, 'r') as fp:
                        data = json.load(fp)
                        ba_values.append(data['value'])
                
                ba_summary = {
                    'mean': float(_np.mean(ba_values)),
                    'std': float(_np.std(ba_values, ddof=1)),
                    'values': ba_values,
                    'n_folds': len(ba_values)
                }
                self.add(ba_summary, "metrics/summary_balanced_accuracy.json")
            
            # MCC
            mcc_files = sorted(glob.glob(_os.path.join(metrics_dir, "mcc_fold_*.json")))
            if mcc_files:
                mcc_values = []
                for f in mcc_files:
                    with open(f, 'r') as fp:
                        data = json.load(fp)
                        mcc_values.append(data['value'])
                
                mcc_summary = {
                    'mean': float(_np.mean(mcc_values)),
                    'std': float(_np.std(mcc_values, ddof=1)),
                    'values': mcc_values,
                    'n_folds': len(mcc_values)
                }
                self.add(mcc_summary, "metrics/summary_mcc.json")
        
        # Summarize classification reports
        reports_dir = _os.path.join(self.save_dir, "reports")
        if _os.path.exists(reports_dir):
            report_files = sorted(glob.glob(_os.path.join(reports_dir, "classification_report_fold_*.csv")))
            if report_files:
                reports = []
                for f in report_files:
                    reports.append(_pd.read_csv(f, index_col=0))
                
                if reports:
                    # Calculate mean report
                    mean_report = _pd.concat(reports).groupby(level=0).mean()
                    self.add(mean_report, "reports/summary_classification_report.csv")
        
        # Create consolidated metrics DataFrame
        self._create_consolidated_metrics()
    
    def _create_consolidated_metrics(self):
        """Create a single CSV file with all metrics across folds."""
        metrics_data = []
        metrics_dir = _os.path.join(self.save_dir, "metrics")
        
        if _os.path.exists(metrics_dir):
            # Collect all metric JSON files
            import json
            import glob
            
            for json_file in sorted(glob.glob(_os.path.join(metrics_dir, "*_fold_*.json"))):
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    # Extract fold number from filename
                    filename = _os.path.basename(json_file)
                    if 'fold' in data:
                        fold = data['fold']
                    else:
                        # Try to extract from filename
                        import re
                        match = re.search(r'fold_(\d+)', filename)
                        fold = int(match.group(1)) if match else 0
                    
                    metric_name = data.get('metric', filename.split('_fold')[0])
                    metrics_data.append({
                        'fold': fold,
                        'metric': metric_name,
                        'value': data.get('value', data)
                    })
            
            if metrics_data:
                # Convert to DataFrame and pivot
                df = _pd.DataFrame(metrics_data)
                if not df.empty:
                    # Pivot to have metrics as columns, folds as rows
                    pivot_df = df.pivot(index='fold', columns='metric', values='value')
                    
                    # Add summary statistics
                    pivot_df.loc['mean'] = pivot_df.mean()
                    pivot_df.loc['std'] = pivot_df.std()
                    
                    # Save consolidated metrics
                    self.add(pivot_df, "metrics/all_metrics_summary.csv")
    
    def validate_completeness(self) -> Dict[str, Any]:
        """
        Validate that all required metrics have been collected for all folds.
        
        Returns
        -------
        Dict[str, Any]
            Validation report with 'complete', 'missing', and 'summary' keys
            
        Examples
        --------
        >>> validation = reporter.validate_completeness()
        >>> if not validation['complete']:
        ...     print("Missing metrics:", validation['missing'])
        """
        validation_report = {
            'complete': True,
            'missing': [],
            'summary': {}
        }
        
        # Get all folds that have been processed
        all_folds = set(self.collected_metrics.keys())
        
        if not all_folds:
            validation_report['complete'] = False
            validation_report['missing'].append("No folds have been processed")
            return validation_report
        
        # Check each fold for required metrics
        for fold in all_folds:
            collected = self.collected_metrics[fold]
            missing = set(self.required_metrics) - collected
            
            if missing:
                validation_report['complete'] = False
                validation_report['missing'].append({
                    'fold': fold,
                    'missing_metrics': list(missing)
                })
        
        # Add summary
        validation_report['summary'] = {
            'n_folds': len(all_folds),
            'folds': sorted(list(all_folds)),
            'required_metrics': self.required_metrics,
            'all_collected': validation_report['complete']
        }
        
        return validation_report
    
    def generate_standard_report(self, output_format: str = 'markdown') -> str:
        """
        Generate a standardized report suitable for papers/requirements.
        
        Parameters
        ----------
        output_format : str
            Format for report ('markdown', 'latex', 'html')
            
        Returns
        -------
        str
            Formatted report text
            
        Examples
        --------
        >>> report = reporter.generate_standard_report('markdown')
        >>> with open('results/report.md', 'w') as f:
        ...     f.write(report)
        """
        import json
        import glob
        
        # Validate first
        validation = self.validate_completeness()
        if not validation['complete']:
            import warnings
            warnings.warn(f"Report incomplete. Missing: {validation['missing']}")
        
        # Collect metrics
        metrics_dir = _os.path.join(self.save_dir, "metrics")
        all_metrics = {}
        
        if _os.path.exists(metrics_dir):
            for json_file in sorted(glob.glob(_os.path.join(metrics_dir, "*.json"))):
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    metric_name = data.get('metric', 'unknown')
                    if metric_name not in all_metrics:
                        all_metrics[metric_name] = []
                    all_metrics[metric_name].append(data.get('value', data))
        
        # Generate report based on format
        if output_format == 'markdown':
            report = "# Classification Results Report\n\n"
            report += "## Summary Statistics\n\n"
            
            for metric, values in all_metrics.items():
                if values:
                    mean_val = _np.mean(values)
                    std_val = _np.std(values, ddof=1) if len(values) > 1 else 0
                    report += f"- **{metric}**: {mean_val:.3f} ± {std_val:.3f}\n"
            
            report += f"\n## Configuration\n\n"
            report += f"- Number of folds: {len(self.collected_metrics)}\n"
            report += f"- Output directory: `{self.save_dir}`\n"
            
            # Add validation status
            report += f"\n## Validation Status\n\n"
            report += f"- Complete: {'✓' if validation['complete'] else '✗'}\n"
            if not validation['complete']:
                report += f"- Missing: {validation['missing']}\n"
            
            # Save report
            self.add(report, "report.md")
            
        elif output_format == 'latex':
            # LaTeX format for papers
            report = "\\begin{table}[h]\n\\centering\n"
            report += "\\begin{tabular}{lr}\n"
            report += "\\toprule\n"
            report += "Metric & Value \\\\\n"
            report += "\\midrule\n"
            
            for metric, values in all_metrics.items():
                if values:
                    mean_val = _np.mean(values)
                    std_val = _np.std(values, ddof=1) if len(values) > 1 else 0
                    report += f"{metric.replace('_', ' ').title()} & ${mean_val:.3f} \\pm {std_val:.3f}$ \\\\\n"
            
            report += "\\bottomrule\n"
            report += "\\end{tabular}\n"
            report += "\\caption{Classification Results}\n"
            report += "\\end{table}\n"
            
            self.add(report, "report.tex")
            
        else:
            report = str(all_metrics)
        
        return report

    def calc_aucs(
        self,
        true_class,
        pred_proba,
        labels: List[str],
        fold_idx: int,
        show: bool = True,
        auc_plot_config: Optional[Dict] = None,
    ) -> float:
        """
        Calculate AUC scores and generate plots.

        Parameters
        ----------
        true_class : array-like
            True class labels
        pred_proba : array-like
            Predicted class probabilities
        labels : List[str]
            Class labels
        fold_idx : int
            Fold index for reporting
        show : bool, default True
            Whether to display results
        auc_plot_config : Dict, optional
            Configuration for AUC plotting

        Returns
        -------
        float
            ROC AUC score
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

        n_classes = len(labels)
        assert len(_np.unique(true_class)) == n_classes

        if n_classes == 2:
            roc_auc = self._calc_aucs_binary(
                true_class,
                pred_proba,
                fold_idx,
                show=show,
                auc_plot_config=auc_plot_config,
            )
        else:
            # TODO: Implement multi-class AUC calculation
            raise NotImplementedError(
                "Multi-class AUC calculation not yet implemented"
            )

        return roc_auc

    def _calc_aucs_binary(
        self,
        true_class,
        pred_proba,
        fold_idx: int,
        show: bool = False,
        auc_plot_config: Optional[Dict] = None,
    ) -> float:
        """
        Calculate metrics for binary classification.

        Parameters
        ----------
        true_class : array-like
            True class labels
        pred_proba : array-like
            Predicted class probabilities
        fold_idx : int
            Fold index for reporting
        show : bool, default False
            Whether to display results
        auc_plot_config : Dict, optional
            Configuration for AUC plotting

        Returns
        -------
        float
            ROC AUC score
        """
        # Use scitex.ai.plt utilities for consistent plotting
        from scitex.ml.plt._plot_pre_rec_curve import pre_rec_auc
        from scitex.ml.plt._plot_roc_curve import roc_auc

        unique_classes = sorted(list(_np.unique(true_class)))
        n_classes = len(unique_classes)
        assert n_classes == 2, "This method is only for binary classification"

        # For binary classification, prepare data for scitex.ai.plt functions
        labels = ["Class_0", "Class_1"]

        # Convert single probability to two-class probability matrix
        pred_proba_2class = _np.column_stack([1 - pred_proba, pred_proba])

        # Determine save paths for AUC figures (use absolute paths)
        fold_suffix = f"_fold_{fold_idx:02d}" if fold_idx is not None else ""
        roc_spath = _os.path.abspath(
            _os.path.join(
                self.save_dir,
                f"receiver_operating_characteristic{fold_suffix}.jpg",
            )
        )
        prerec_spath = _os.path.abspath(
            _os.path.join(
                self.save_dir, f"precision_recall_curve{fold_suffix}.jpg"
            )
        )

        # Use scitex.ml.plt._plot_roc_curve for ROC curve with automatic saving
        fig_roc, roc_metrics = roc_auc(
            _plt, true_class, pred_proba_2class, labels, spath=roc_spath
        )
        roc_auc_score = roc_metrics["roc_auc"][1]  # Get AUC for positive class

        # Use scitex.ml.plt._plot_pre_rec_curve for Precision-Recall curve with automatic saving
        fig_prerec, prerec_metrics = pre_rec_auc(
            _plt, true_class, pred_proba_2class, labels, spath=prerec_spath
        )

        if show:
            print(f"\nROC AUC in fold#{fold_idx}: {roc_auc_score:.3f}\n")

        return roc_auc_score

    def plot_and_save_conf_mats(
        self,
        extend_ratio: float = 1.0,
        colorbar: bool = True,
        confmat_plt_config: Optional[Dict] = None,
        sci_notation_kwargs: Optional[Dict] = None,
    ):
        """
        Plot and save confusion matrices using scitex.ai.plt.conf_mat.

        Parameters
        ----------
        extend_ratio : float, default 1.0
            Ratio for extending plot dimensions
        colorbar : bool, default True
            Whether to include colorbar
        confmat_plt_config : Dict, optional
            Configuration for confusion matrix plotting
        sci_notation_kwargs : Dict, optional
            Scientific notation formatting arguments
        """
        from scitex.ai.plt import conf_mat

        if (
            "conf_mat_data" in self.folds_dict
            and self.folds_dict["conf_mat_data"]
        ):
            for i, conf_mat_data in enumerate(
                self.folds_dict["conf_mat_data"]
            ):
                # Extract confusion matrix data
                cm = (
                    conf_mat_data.values
                    if hasattr(conf_mat_data, "values")
                    else conf_mat_data
                )
                labels = (
                    conf_mat_data.columns.tolist()
                    if hasattr(conf_mat_data, "columns")
                    else None
                )

                # Determine save path with subdirectory (use absolute path)
                fold_suffix = (
                    f"_fold_{i+1:02d}"
                    if len(self.folds_dict["conf_mat_data"]) > 1
                    else ""
                )
                # Create confusion_matrices subdirectory
                conf_mat_dir = _os.path.join(self.save_dir, "confusion_matrices")
                _os.makedirs(conf_mat_dir, exist_ok=True)
                spath = _os.path.abspath(
                    _os.path.join(conf_mat_dir, f"conf_mat{fold_suffix}.jpg")
                )

                # Create and save confusion matrix plot using scitex.ai.plt with spath
                fig = conf_mat(
                    plt=_plt,
                    cm=cm,
                    labels=labels,
                    title=f"Confusion Matrix (Fold {i+1})",
                    colorbar=colorbar,
                    x_extend_ratio=extend_ratio,
                    y_extend_ratio=extend_ratio,
                    spath=spath,
                )

    def save(
        self,
        files_to_repro: Optional[List[str]] = None,
        meta_dict: Optional[Dict] = None,
    ):
        """
        Save all objects that were added via add() method.
        
        Objects are saved to their specified paths relative to self.save_dir.
        The file format is determined by the extension provided in add().

        Parameters
        ----------
        files_to_repro : List[str], optional
            Files to include in reproducibility package
        meta_dict : Dict, optional
            Additional metadata dictionary to save. Keys should be relative paths.

        Examples
        --------
        >>> reporter = SingleTaskClassificationReporter("./results")
        >>> 
        >>> # Add objects with specific paths
        >>> fig = create_plot()
        >>> reporter.add(fig, "plots/accuracy.jpg")
        >>> 
        >>> df = pd.DataFrame({'metric': ['acc', 'mcc'], 'value': [0.95, 0.82]})
        >>> reporter.add(df, "tables/metrics.csv")
        >>> 
        >>> # Save all added objects
        >>> reporter.save()
        >>> 
        >>> # Save with additional metadata
        >>> meta_dict = {
        ...     "config.yaml": {'model': 'RF', 'n_trees': 100},
        ...     "info/date.txt": "2025-09-07"
        ... }
        >>> reporter.save(meta_dict=meta_dict)
        
        Notes
        -----
        - All paths are relative to self.save_dir
        - Directories are created automatically
        - Files are saved using scitex.io.save with format auto-detection
        """
        import scitex as stx

        # Create save directory if it doesn't exist
        _os.makedirs(self.save_dir, exist_ok=True)

        # Save all objects that were added via add()
        for path, obj_list in self.folds_dict.items():
            if obj_list:
                if len(obj_list) == 1:
                    # Single object - save to the specified path
                    obj = obj_list[0]
                    full_path = _os.path.abspath(
                        _os.path.join(self.save_dir, path)
                    )
                    # Create directory if needed
                    save_dir = _os.path.dirname(full_path)
                    _os.makedirs(save_dir, exist_ok=True)
                    # Save using scitex.io.save (handles format based on extension)
                    stx.io.save(obj, full_path)
                else:
                    # Multiple objects with same path - need to differentiate
                    # This happens when add() is called multiple times with same path
                    # Add index suffix before extension
                    base_path, ext = _os.path.splitext(path)
                    for i, obj in enumerate(obj_list):
                        indexed_path = f"{base_path}_{i+1:02d}{ext}"
                        full_path = _os.path.abspath(
                            _os.path.join(self.save_dir, indexed_path)
                        )
                        # Create directory if needed
                        save_dir = _os.path.dirname(full_path)
                        _os.makedirs(save_dir, exist_ok=True)
                        # Save using scitex.io.save
                        stx.io.save(obj, full_path)

        # Add metadata if provided
        if meta_dict is not None:
            for path, value in meta_dict.items():
                full_path = _os.path.abspath(
                    _os.path.join(self.save_dir, path)
                )
                # Create directory if needed
                save_dir = _os.path.dirname(full_path)
                _os.makedirs(save_dir, exist_ok=True)
                stx.io.save(value, full_path)

        # Save files for reproducibility if provided
        if files_to_repro is not None:
            repro_dir = _os.path.join(self.save_dir, "reproducibility")
            _os.makedirs(repro_dir, exist_ok=True)
            import shutil

            for file_path in files_to_repro:
                if _os.path.exists(file_path):
                    filename = _os.path.basename(file_path)
                    dest_path = _os.path.join(repro_dir, filename)
                    shutil.copy2(file_path, dest_path)

        print(f"Results saved to: {self.save_dir}")


def main():
    """
    Demonstrate usage of SingleTaskClassificationReporter.

    This function provides a complete example of using SingleTaskClassificationReporter
    for binary classification, including all major functionality:

    Example Output:
    ---------------
    === SingleTaskClassificationReporter Usage Example ===

    Balanced Accuracy in fold#1: 0.914

    MCC in fold#1: 0.828

    Confusion Matrix in fold#1:
             Class 0  Class 1
    Class 0      140       17
    Class 1        9      134

    Classification Report for fold#1:
                 Class 0  Class 1  balanced accuracy  macro avg  weighted avg
    precision      0.940    0.887              0.914      0.914         0.915
    recall         0.892    0.937              0.914      0.914         0.913
    f1-score       0.915    0.912              0.914      0.913         0.913
    sample size  157.000  143.000              0.914    300.000       300.000

    ROC AUC in fold#1: 0.958

    Results saved to: ./.dev/classification_reporter_example

    === Example completed! Results saved to: ./.dev/classification_reporter_example ===

    Files Created:
    --------------
    - ROC_fig.pkl: ROC curve plot
    - PRE_REC_fig.pkl: Precision-Recall curve plot
    - custom_histogram.pkl: Custom probability histogram
    - experiment_config.yaml: Experiment configuration
    - results_summary.csv: Summary metrics table

    Features Demonstrated:
    ----------------------
    1. Balanced accuracy calculation
    2. Matthews Correlation Coefficient (MCC)
    3. Confusion matrix generation and display
    4. Classification report with per-class metrics
    5. ROC AUC calculation and curve plotting
    6. Precision-Recall AUC and curve plotting
    7. Custom object tracking (figures, data)
    8. Metadata saving (YAML, CSV formats)
    9. Complete result persistence
    """
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    from sklearn.datasets import make_classification
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split

    print("=== SingleTaskClassificationReporter Usage Example ===\n")

    # Generate sample data
    X, y = make_classification(
        n_samples=1000,
        n_features=20,
        n_informative=10,
        n_redundant=10,
        n_classes=2,
        random_state=42,
    )

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )

    # Train a simple classifier
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)

    # Make predictions
    y_pred = clf.predict(X_test)
    y_pred_proba = clf.predict_proba(X_test)[:, 1]

    # Create reporter
    save_dir = "./.dev/classification_reporter_example"
    reporter = SingleTaskClassificationReporter(save_dir)

    # Calculate metrics
    labels = ["Class 0", "Class 1"]
    fold_idx = 1

    balanced_acc = reporter.calc_balanced_accuracy(
        y_test, y_pred, fold_idx, show=True
    )
    mcc = reporter.calc_mcc(y_test, y_pred, fold_idx, show=True)
    conf_mat = reporter.calc_conf_mat(
        y_test, y_pred, labels, fold_idx, show=True
    )
    clf_report = reporter.calc_clf_report(
        y_test, y_pred, labels, balanced_acc, mcc, fold_idx, show=True
    )

    # Calculate AUCs and generate plots
    auc_score = reporter.calc_aucs(
        y_test, y_pred_proba, labels, fold_idx, show=True
    )

    # Add custom objects
    custom_fig, custom_ax = plt.subplots()
    custom_ax.hist(y_pred_proba, bins=20, alpha=0.7)
    custom_ax.set_title("Predicted Probability Distribution")
    reporter.add("custom_histogram", custom_fig)

    # Create metadata
    metadata = {
        "experiment_config.yaml": {
            "n_estimators": 100,
            "random_state": 42,
            "test_size": 0.3,
        },
        "results_summary.csv": _pd.DataFrame(
            {
                "metric": ["balanced_accuracy", "mcc", "roc_auc"],
                "value": [balanced_acc, mcc, auc_score],
            }
        ),
    }

    # Save everything
    reporter.save(meta_dict=metadata)

    print(f"\n=== Example completed! Results saved to: {save_dir} ===")


if __name__ == "__main__":
    main()

# EOF
