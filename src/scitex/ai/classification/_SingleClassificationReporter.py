#!/usr/bin/env python3
"""
Enhanced Single Classification Reporter using modular reporter utilities.

This version integrates with the new reporter_utils module for better
modularity, validation, and standardization.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import numpy as np
import pandas as pd
from collections import defaultdict

# Import from reporter_utils
from .reporter_utils import (
    # Metrics
    calc_balanced_accuracy,
    calc_mcc,
    calc_confusion_matrix,
    calc_classification_report,
    calc_roc_auc,
    calc_pr_auc,
    # Storage
    MetricStorage,
    # Validation
    MetricValidator,
    # Aggregation
    aggregate_fold_metrics,
    create_summary_table,
    aggregate_confusion_matrices,
    # Reporting
    generate_markdown_report,
    export_for_paper,
    create_summary_statistics
)


class SingleTaskClassificationReporter:
    """
    Enhanced classification reporter using modular utilities.
    
    Features:
    - Automatic metric calculation with validation
    - Path-based file organization
    - Built-in validation and completeness checking
    - Publication-ready exports
    - Automatic aggregation across folds
    
    Parameters
    ----------
    name : str
        Experiment name
    output_dir : Union[str, Path]
        Base directory for outputs
    required_metrics : List[str], optional
        List of required metrics for validation
    auto_validate : bool
        Whether to validate after each fold
    """
    
    def __init__(
        self,
        name: str,
        output_dir: Union[str, Path] = None,
        required_metrics: Optional[List[str]] = None,
        auto_validate: bool = True
    ):
        self.name = name
        
        # Set default output directory if not provided
        if output_dir is None:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = Path(f"./results/{name}_{timestamp}")
        
        self.output_dir = Path(output_dir)
        self.storage = MetricStorage(self.output_dir)
        
        # Create directory structure
        self._create_directory_structure()
        
        # Print where results will be saved
        print(f"\n{'='*60}")
        print(f"Classification Reporter Initialized")
        print(f"{'='*60}")
        print(f"Experiment: {name}")
        print(f"Output Directory: {self.output_dir.absolute()}")
        print(f"{'='*60}\n")
        
        # Default required metrics
        if required_metrics is None:
            required_metrics = [
                'balanced_accuracy',
                'mcc',
                'confusion_matrix',
                'classification_report'
            ]
        
        self.required_metrics = required_metrics
        self.validator = MetricValidator(required_metrics)
        self.auto_validate = auto_validate
        
        # Track fold results
        self.fold_results = []
        self.current_fold = None
        self.n_folds = 0
        
        # Track custom additions
        self.custom_objects = defaultdict(list)
        
        # Metadata
        self.config = {
            'name': name,
            'output_dir': str(self.output_dir),
            'required_metrics': required_metrics
        }
    
    def _create_directory_structure(self) -> None:
        """Create standard directory structure for outputs."""
        directories = [
            self.output_dir / 'metrics',
            self.output_dir / 'plots',
            self.output_dir / 'tables',
            self.output_dir / 'reports',
            self.output_dir / 'models',
            self.output_dir / 'paper_export'
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def get_output_paths(self) -> Dict[str, Path]:
        """
        Get all output paths.
        
        Returns
        -------
        Dict[str, Path]
            Dictionary of output paths
        """
        return {
            'base': self.output_dir,
            'metrics': self.output_dir / 'metrics',
            'plots': self.output_dir / 'plots',
            'tables': self.output_dir / 'tables',
            'reports': self.output_dir / 'reports',
            'models': self.output_dir / 'models',
            'paper_export': self.output_dir / 'paper_export',
            'final_report': self.output_dir / 'report.md',
            'summary_table': self.output_dir / 'summary_table.csv',
            'validation_report': self.output_dir / 'validation_report.json'
        }
    
    def start_fold(self, fold_idx: int) -> None:
        """
        Start a new fold.
        
        Parameters
        ----------
        fold_idx : int
            Fold index
        """
        self.current_fold = {
            'fold_id': fold_idx,
            'metrics': {}
        }
        self.n_folds = max(self.n_folds, fold_idx + 1)
    
    def calc_balanced_accuracy(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        fold_idx: Optional[int] = None,
        save: bool = True
    ) -> float:
        """
        Calculate and save balanced accuracy.
        
        Parameters
        ----------
        y_true : np.ndarray
            True labels
        y_pred : np.ndarray
            Predicted labels
        fold_idx : int, optional
            Fold index (uses current_fold if None)
        save : bool
            Whether to save to disk
            
        Returns
        -------
        float
            Balanced accuracy score
        """
        if fold_idx is None:
            fold_idx = self.current_fold['fold_id'] if self.current_fold else 0
        
        # Calculate metric
        result = calc_balanced_accuracy(y_true, y_pred, fold=fold_idx)
        
        # Store in current fold
        if self.current_fold and self.current_fold['fold_id'] == fold_idx:
            self.current_fold['metrics']['balanced_accuracy'] = result['value']
        
        # Save to disk
        if save:
            self.storage.save(
                result,
                f"metrics/fold_{fold_idx:02d}/balanced_accuracy.json"
            )
        
        return result['value']
    
    def calc_mcc(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        fold_idx: Optional[int] = None,
        save: bool = True
    ) -> float:
        """
        Calculate and save Matthews Correlation Coefficient.
        
        Parameters
        ----------
        y_true : np.ndarray
            True labels
        y_pred : np.ndarray
            Predicted labels
        fold_idx : int, optional
            Fold index
        save : bool
            Whether to save to disk
            
        Returns
        -------
        float
            MCC score
        """
        if fold_idx is None:
            fold_idx = self.current_fold['fold_id'] if self.current_fold else 0
        
        # Calculate metric
        result = calc_mcc(y_true, y_pred, fold=fold_idx)
        
        # Store in current fold
        if self.current_fold and self.current_fold['fold_id'] == fold_idx:
            self.current_fold['metrics']['mcc'] = result['value']
        
        # Save to disk
        if save:
            self.storage.save(
                result,
                f"metrics/fold_{fold_idx:02d}/mcc.json"
            )
        
        return result['value']
    
    def calc_confusion_matrix(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        labels: Optional[List[str]] = None,
        fold_idx: Optional[int] = None,
        save: bool = True,
        plot: bool = True
    ) -> np.ndarray:
        """
        Calculate and save confusion matrix.
        
        Parameters
        ----------
        y_true : np.ndarray
            True labels
        y_pred : np.ndarray
            Predicted labels
        labels : List[str], optional
            Class labels
        fold_idx : int, optional
            Fold index
        save : bool
            Whether to save to disk
        plot : bool
            Whether to create and save plot
            
        Returns
        -------
        np.ndarray
            Confusion matrix
        """
        if fold_idx is None:
            fold_idx = self.current_fold['fold_id'] if self.current_fold else 0
        
        # Calculate metric
        result = calc_confusion_matrix(y_true, y_pred, labels=labels, fold=fold_idx)
        
        # Store in current fold
        if self.current_fold and self.current_fold['fold_id'] == fold_idx:
            self.current_fold['metrics']['confusion_matrix'] = result['value']
        
        # Save to disk
        if save:
            # Save as CSV (more readable than numpy)
            self.storage.save(
                result,  # Pass the full result dict for CSV formatting
                f"metrics/fold_{fold_idx:02d}/confusion_matrix.csv"
            )
            
            # Also save labels separately for compatibility
            self.storage.save(
                {'labels': result['labels']},
                f"metrics/fold_{fold_idx:02d}/confusion_matrix_labels.json"
            )
        
        # Create plot if requested
        if plot:
            try:
                import matplotlib.pyplot as plt
                from scitex.ai.plt._conf_mat import conf_mat as plot_conf_mat
                
                # Use the scitex confusion matrix plotting function
                fig, cm_df = plot_conf_mat(
                    plt,
                    cm=result['value'],
                    labels=result['labels'],
                    title=f"Confusion Matrix - Fold {fold_idx}"
                )
                
                if save and fig is not None:
                    self.storage.save(
                        fig,
                        f"plots/fold_{fold_idx:02d}/confusion_matrix.jpg"
                    )
                    
            except Exception as e:
                print(f"Warning: Could not create confusion matrix plot: {e}")
                fig = None
        
        return result['value']
    
    def calc_classification_report(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        labels: Optional[List[str]] = None,
        additional_metrics: Optional[Dict[str, float]] = None,
        fold_idx: Optional[int] = None,
        save: bool = True
    ) -> pd.DataFrame:
        """
        Calculate and save classification report.
        
        Parameters
        ----------
        y_true : np.ndarray
            True labels
        y_pred : np.ndarray
            Predicted labels
        labels : List[str], optional
            Class labels
        additional_metrics : Dict[str, float], optional
            Additional metrics to include
        fold_idx : int, optional
            Fold index
        save : bool
            Whether to save to disk
            
        Returns
        -------
        pd.DataFrame
            Classification report
        """
        if fold_idx is None:
            fold_idx = self.current_fold['fold_id'] if self.current_fold else 0
        
        # Calculate metric
        result = calc_classification_report(
            y_true, y_pred,
            labels=labels,
            additional_metrics=additional_metrics,
            fold=fold_idx
        )
        
        # Store in current fold
        if self.current_fold and self.current_fold['fold_id'] == fold_idx:
            self.current_fold['metrics']['classification_report'] = result['value']
        
        # Save to disk
        if save:
            self.storage.save(
                result['value'],
                f"metrics/fold_{fold_idx:02d}/classification_report.csv"
            )
        
        return result['value']
    
    def calc_roc_auc(
        self,
        y_true: np.ndarray,
        y_proba: np.ndarray,
        fold_idx: Optional[int] = None,
        save: bool = True,
        plot: bool = True
    ) -> float:
        """
        Calculate and save ROC AUC.
        
        Parameters
        ----------
        y_true : np.ndarray
            True labels
        y_proba : np.ndarray
            Predicted probabilities (can be 1D for binary or 2D for multiclass)
        fold_idx : int, optional
            Fold index
        save : bool
            Whether to save to disk
        plot : bool
            Whether to create and save plot
            
        Returns
        -------
        float
            ROC AUC score
        """
        if fold_idx is None:
            fold_idx = self.current_fold['fold_id'] if self.current_fold else 0
        
        # Handle probability array format
        # If 2D array for binary classification, use positive class probabilities
        if y_proba.ndim == 2 and y_proba.shape[1] == 2:
            y_proba_binary = y_proba[:, 1]
        else:
            y_proba_binary = y_proba
        
        # Calculate metric with curve
        result = calc_roc_auc(y_true, y_proba_binary, fold=fold_idx, return_curve=True)
        
        # Store in current fold
        if self.current_fold and self.current_fold['fold_id'] == fold_idx:
            self.current_fold['metrics']['roc_auc'] = result['value']
        
        # Save to disk
        if save:
            self.storage.save(
                {'value': result['value'], 'fold': fold_idx},
                f"metrics/fold_{fold_idx:02d}/roc_auc.json"
            )
        
        # Create plot if requested
        if plot:
            try:
                import matplotlib.pyplot as plt
                from scitex.ai.plt.aucs import roc_auc as plot_roc_auc
                # Get class labels
                n_classes = y_proba.shape[1] if y_proba.ndim > 1 else 2
                labels = [str(i) for i in range(n_classes)]
                fig = plot_roc_auc(plt, y_true, y_proba, labels)
            except Exception as e:
                print(f"Warning: Could not create ROC plot: {e}")
                fig = None
            if save and fig is not None:
                self.storage.save(
                    fig,
                    f"plots/fold_{fold_idx:02d}/roc_curve.jpg"
                )
        
        return result['value']
    
    def calc_pr_auc(
        self,
        y_true: np.ndarray,
        y_proba: np.ndarray,
        fold_idx: Optional[int] = None,
        save: bool = True,
        plot: bool = True
    ) -> float:
        """
        Calculate and save Precision-Recall AUC.
        
        Parameters
        ----------
        y_true : np.ndarray
            True labels
        y_proba : np.ndarray
            Predicted probabilities (can be 1D for binary or 2D for multiclass)
        fold_idx : int, optional
            Fold index
        save : bool
            Whether to save to disk
        plot : bool
            Whether to create and save plot
            
        Returns
        -------
        float
            PR AUC score
        """
        if fold_idx is None:
            fold_idx = self.current_fold['fold_id'] if self.current_fold else 0
        
        # Handle probability array format
        # If 2D array for binary classification, use positive class probabilities
        if y_proba.ndim == 2 and y_proba.shape[1] == 2:
            y_proba_binary = y_proba[:, 1]
        else:
            y_proba_binary = y_proba
        
        # Calculate metric with curve
        result = calc_pr_auc(y_true, y_proba_binary, fold=fold_idx, return_curve=True)
        
        # Store in current fold
        if self.current_fold and self.current_fold['fold_id'] == fold_idx:
            self.current_fold['metrics']['pr_auc'] = result['value']
        
        # Save to disk
        if save:
            self.storage.save(
                {'value': result['value'], 'fold': fold_idx},
                f"metrics/fold_{fold_idx:02d}/pr_auc.json"
            )
        
        # Create plot if requested
        if plot:
            try:
                import matplotlib.pyplot as plt
                from scitex.ai.plt.aucs import pre_rec_auc as plot_pr_auc
                # Get class labels
                n_classes = y_proba.shape[1] if y_proba.ndim > 1 else 2
                labels = [str(i) for i in range(n_classes)]
                fig = plot_pr_auc(plt, y_true, y_proba, labels)
            except Exception as e:
                print(f"Warning: Could not create PR plot: {e}")
                fig = None
            if save and fig is not None:
                self.storage.save(
                    fig,
                    f"plots/fold_{fold_idx:02d}/pr_curve.jpg"
                )
        
        return result['value']
    
    def end_fold(self, fold_idx: Optional[int] = None) -> None:
        """
        End current fold and optionally validate.
        
        Parameters
        ----------
        fold_idx : int, optional
            Fold index to end (uses current if None)
        """
        if fold_idx is None and self.current_fold:
            fold_idx = self.current_fold['fold_id']
        
        # Add to fold results
        if self.current_fold:
            self.fold_results.append(self.current_fold)
        
        # Validate if enabled
        if self.auto_validate and self.current_fold:
            validation = self.validator.validate_fold(
                self.current_fold['metrics'],
                fold_idx
            )
            
            if not validation['complete']:
                print(f"Warning: Fold {fold_idx} missing metrics: {validation['missing_metrics']}")
        
        # Reset current fold
        self.current_fold = None
    
    def add(self, obj: Any, path: str) -> None:
        """
        Add custom object with specified path.
        
        Parameters
        ----------
        obj : Any
            Object to save (figure, dataframe, dict, etc.)
        path : str
            Relative path for saving
        """
        # Save immediately
        full_path = self.storage.save(obj, path)
        
        # Track for later reference
        self.custom_objects[path].append(obj)
    
    def calculate_all_metrics(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_proba: Optional[np.ndarray] = None,
        labels: Optional[List[str]] = None,
        fold_idx: Optional[int] = None,
        save: bool = True,
        plot: bool = True
    ) -> Dict[str, Any]:
        """
        Calculate all standard metrics at once.
        
        Parameters
        ----------
        y_true : np.ndarray
            True labels
        y_pred : np.ndarray
            Predicted labels
        y_proba : np.ndarray, optional
            Predicted probabilities (for AUC metrics)
        labels : List[str], optional
            Class labels
        fold_idx : int, optional
            Fold index
        save : bool
            Whether to save to disk
        plot : bool
            Whether to create plots
            
        Returns
        -------
        Dict[str, Any]
            All calculated metrics
        """
        if fold_idx is not None:
            self.start_fold(fold_idx)
        
        metrics = {}
        
        # Basic metrics
        metrics['balanced_accuracy'] = self.calc_balanced_accuracy(
            y_true, y_pred, fold_idx, save
        )
        metrics['mcc'] = self.calc_mcc(
            y_true, y_pred, fold_idx, save
        )
        
        # Confusion matrix
        metrics['confusion_matrix'] = self.calc_confusion_matrix(
            y_true, y_pred, labels, fold_idx, save, plot
        )
        
        # Classification report with additional metrics
        additional = {
            'balanced_accuracy': metrics['balanced_accuracy'],
            'mcc': metrics['mcc']
        }
        metrics['classification_report'] = self.calc_classification_report(
            y_true, y_pred, labels, additional, fold_idx, save
        )
        
        # AUC metrics if probabilities provided
        if y_proba is not None:
            metrics['roc_auc'] = self.calc_roc_auc(
                y_true, y_proba, fold_idx, save, plot
            )
            metrics['pr_auc'] = self.calc_pr_auc(
                y_true, y_proba, fold_idx, save, plot
            )
        
        # End fold
        if fold_idx is not None:
            self.end_fold(fold_idx)
        
        return metrics
    
    def create_summary(self) -> pd.DataFrame:
        """
        Create summary table across all folds.
        
        Returns
        -------
        pd.DataFrame
            Summary statistics table
        """
        if not self.fold_results:
            print("No fold results to summarize")
            return pd.DataFrame()
        
        # Create summary table
        summary_df = create_summary_table(
            self.fold_results,
            include_stats=True,
            format_digits=3
        )
        
        # Save summary
        self.storage.save(summary_df, "summary_table.csv")
        
        return summary_df
    
    def validate_completeness(self) -> Dict[str, Any]:
        """
        Validate completeness across all folds.
        
        Returns
        -------
        Dict[str, Any]
            Validation report
        """
        if not self.fold_results:
            return {'complete': False, 'message': 'No fold results'}
        
        # Flatten the fold results structure for validation
        # Convert from [{fold_id: 0, metrics: {metric1: val1, ...}}]
        # To [{metric1: val1, metric2: val2, fold_id: 0, ...}]
        flattened_fold_results = []
        for fold_result in self.fold_results:
            flattened_fold = {}
            
            # Add non-metric fields first
            for key, value in fold_result.items():
                if key != 'metrics':
                    flattened_fold[key] = value
            
            # Add metrics at the top level
            if 'metrics' in fold_result:
                flattened_fold.update(fold_result['metrics'])
            
            flattened_fold_results.append(flattened_fold)
        
        # Validate all folds with flattened structure
        report = self.validator.validate_all_folds(flattened_fold_results)
        
        # Save validation report
        self.validator.save_report(self.output_dir / "validation_report.json")
        
        # Print summary
        self.validator.print_summary()
        
        return report
    
    def generate_report(
        self,
        include_plots: bool = True,
        do_paper_export: bool = True
    ) -> Dict[str, Path]:
        """
        Generate comprehensive report.
        
        Parameters
        ----------
        include_plots : bool
            Whether to include plots in report
        export_for_paper : bool
            Whether to create paper-ready exports
            
        Returns
        -------
        Dict[str, Path]
            Paths to generated files
        """
        generated_files = {}
        
        # Prepare results dictionary
        results = {
            'config': self.config,
            'folds': self.fold_results,
            'summary': create_summary_statistics(self.fold_results),
            'validation': self.validate_completeness()
        }
        
        # Add plot references if available
        if include_plots:
            plots_dir = self.output_dir / 'plots'
            if plots_dir.exists():
                results['plots'] = {
                    p.stem: str(p) for p in plots_dir.rglob('*.jpg')
                }
        
        # Generate markdown report
        report_path = self.output_dir / 'report.md'
        generate_markdown_report(results, report_path, include_plots)
        generated_files['report'] = report_path
        
        # Export for paper if requested
        if do_paper_export:
            paper_dir = self.output_dir / 'paper_export'
            paper_export_paths = export_for_paper(results, paper_dir)
            generated_files.update(paper_export_paths)
        
        print(f"\n✓ Reports generated in {self.output_dir}")
        for name, path in generated_files.items():
            print(f"  - {name}: {path}")
        
        return generated_files
    
    def save(self) -> Dict[str, Path]:
        """
        Save all results and generate final outputs.
        
        This method:
        1. Creates summary statistics
        2. Validates completeness
        3. Generates reports
        4. Exports for publication
        
        Returns
        -------
        Dict[str, Path]
            Paths to all generated files
        """
        # Create summary
        summary = self.create_summary()
        print("\n" + "="*60)
        print("SUMMARY STATISTICS")
        print("="*60)
        print(summary.to_string())
        
        # Validate
        print("\n" + "="*60)
        print("VALIDATION")
        print("="*60)
        validation = self.validate_completeness()
        
        # Generate reports
        print("\n" + "="*60)
        print("GENERATING REPORTS")
        print("="*60)
        report_files = self.generate_report()
        
        # Save metadata
        self.storage.save(
            {
                'name': self.name,
                'n_folds': self.n_folds,
                'required_metrics': self.required_metrics,
                'validation': validation
            },
            'metadata.json'
        )
        
        # Get all output paths
        paths = self.get_output_paths()
        
        # Print final report locations
        print("\n" + "="*70)
        print("📊 FINAL REPORT LOCATIONS")
        print("="*70)
        print(f"📁 Main Directory: {self.output_dir.absolute()}")
        print(f"\nKey Files:")
        print(f"  📄 Final Report:      {paths['final_report']}")
        print(f"  📊 Summary Table:     {paths['summary_table']}")
        print(f"  ✅ Validation Report: {paths['validation_report']}")
        print(f"\nDirectories:")
        print(f"  📈 Metrics:       {paths['metrics']}/")
        print(f"  📊 Plots:         {paths['plots']}/")
        print(f"  📑 Tables:        {paths['tables']}/")
        print(f"  📄 Reports:       {paths['reports']}/")
        print(f"  📚 Paper Export:  {paths['paper_export']}/")
        
        if validation.get('complete', False):
            print(f"\n✅ All required metrics present - experiment complete!")
        else:
            print(f"\n⚠️  Some required metrics missing - check validation report")
        
        print("="*70)
        
        return paths