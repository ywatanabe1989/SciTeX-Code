#!/usr/bin/env python3
"""
Validation utilities for classification metrics.

Provides validation for completeness, consistency, and scientific requirements.
"""

import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple
import json


class MetricValidator:
    """
    Validates classification metrics for completeness and consistency.
    
    This class checks that all required metrics are present across folds
    and validates metric values are within expected ranges.
    """
    
    # Standard metric ranges
    METRIC_RANGES = {
        'balanced_accuracy': (0.0, 1.0),
        'mcc': (-1.0, 1.0),
        'roc_auc': (0.0, 1.0),
        'pr_auc': (0.0, 1.0),
        'accuracy': (0.0, 1.0),
        'precision': (0.0, 1.0),
        'recall': (0.0, 1.0),
        'f1': (0.0, 1.0)
    }
    
    def __init__(self, required_metrics: List[str]):
        """
        Initialize validator with required metrics.
        
        Parameters
        ----------
        required_metrics : List[str]
            List of metric names that must be present
        """
        self.required_metrics = required_metrics
        self.validation_results = {}
    
    def validate_metric_value(
        self,
        metric_name: str,
        value: Union[float, np.ndarray]
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate a single metric value is within expected range.
        
        Parameters
        ----------
        metric_name : str
            Name of the metric
        value : Union[float, np.ndarray]
            Metric value to validate
            
        Returns
        -------
        Tuple[bool, Optional[str]]
            (is_valid, error_message)
        """
        if metric_name not in self.METRIC_RANGES:
            # Unknown metric, skip range validation
            return True, None
        
        min_val, max_val = self.METRIC_RANGES[metric_name]
        
        if isinstance(value, np.ndarray):
            value = float(value.mean())  # Use mean for array metrics
        
        if not (min_val <= value <= max_val):
            return False, f"{metric_name} value {value:.4f} outside valid range [{min_val}, {max_val}]"
        
        return True, None
    
    def validate_fold(
        self,
        fold_data: Dict[str, Any],
        fold: int
    ) -> Dict[str, Any]:
        """
        Validate metrics for a single fold.
        
        Parameters
        ----------
        fold_data : Dict[str, Any]
            Dictionary of metrics for the fold
        fold : int
            Fold index
            
        Returns
        -------
        Dict[str, Any]
            Validation results for the fold
        """
        result = {
            'fold': fold,
            'complete': True,
            'missing_metrics': [],
            'invalid_metrics': [],
            'warnings': []
        }
        
        # Check required metrics
        available_metrics = set(fold_data.keys())
        missing = set(self.required_metrics) - available_metrics
        
        if missing:
            result['complete'] = False
            result['missing_metrics'] = list(missing)
        
        # Validate metric values
        for metric_name, metric_value in fold_data.items():
            if isinstance(metric_value, dict) and 'value' in metric_value:
                value = metric_value['value']
            else:
                value = metric_value
            
            is_valid, error_msg = self.validate_metric_value(metric_name, value)
            if not is_valid:
                result['invalid_metrics'].append({
                    'metric': metric_name,
                    'error': error_msg
                })
        
        return result
    
    def validate_all_folds(
        self,
        folds_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Validate metrics across all folds.
        
        Parameters
        ----------
        folds_data : List[Dict[str, Any]]
            List of metric dictionaries for each fold
            
        Returns
        -------
        Dict[str, Any]
            Complete validation report
        """
        validation_report = {
            'complete': True,
            'n_folds': len(folds_data),
            'required_metrics': self.required_metrics,
            'fold_results': [],
            'summary': {
                'missing_by_metric': {},
                'invalid_count': 0,
                'warnings': []
            }
        }
        
        # Validate each fold
        for i, fold_data in enumerate(folds_data):
            fold_result = self.validate_fold(fold_data, i)
            validation_report['fold_results'].append(fold_result)
            
            if not fold_result['complete']:
                validation_report['complete'] = False
            
            if fold_result['invalid_metrics']:
                validation_report['summary']['invalid_count'] += len(fold_result['invalid_metrics'])
        
        # Summarize missing metrics
        for metric in self.required_metrics:
            missing_folds = [
                i for i, fold_data in enumerate(folds_data)
                if metric not in fold_data
            ]
            if missing_folds:
                validation_report['summary']['missing_by_metric'][metric] = missing_folds
        
        # Check consistency across folds
        validation_report['summary']['consistency'] = self._check_consistency(folds_data)
        
        self.validation_results = validation_report
        return validation_report
    
    def _check_consistency(self, folds_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Check metric consistency across folds.
        
        Parameters
        ----------
        folds_data : List[Dict[str, Any]]
            List of metric dictionaries for each fold
            
        Returns
        -------
        Dict[str, Any]
            Consistency analysis
        """
        consistency = {
            'metrics_per_fold': {},
            'consistent': True,
            'issues': []
        }
        
        # Get metrics for each fold
        for i, fold_data in enumerate(folds_data):
            consistency['metrics_per_fold'][f'fold_{i}'] = list(fold_data.keys())
        
        # Check if all folds have same metrics
        all_metrics = [set(fold_data.keys()) for fold_data in folds_data]
        if len(all_metrics) > 1:
            common_metrics = set.intersection(*all_metrics)
            union_metrics = set.union(*all_metrics)
            diff_metrics = union_metrics - common_metrics
            
            if diff_metrics:
                consistency['consistent'] = False
                consistency['issues'].append(
                    f"Inconsistent metrics across folds: {list(diff_metrics)}"
                )
        
        return consistency
    
    def save_report(self, path: Union[str, Path]) -> None:
        """
        Save validation report to file.
        
        Parameters
        ----------
        path : Union[str, Path]
            Path to save report
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w') as f:
            json.dump(self.validation_results, f, indent=2)
    
    def print_summary(self) -> None:
        """
        Print validation summary to console.
        """
        if not self.validation_results:
            print("No validation results available. Run validate_all_folds first.")
            return
        
        report = self.validation_results
        
        print("\n" + "="*60)
        print("VALIDATION REPORT")
        print("="*60)
        
        status = "✓ COMPLETE" if report['complete'] else "✗ INCOMPLETE"
        print(f"Status: {status}")
        print(f"Folds: {report['n_folds']}")
        print(f"Required Metrics: {', '.join(report['required_metrics'])}")
        
        if report['summary']['missing_by_metric']:
            print("\nMissing Metrics:")
            for metric, folds in report['summary']['missing_by_metric'].items():
                print(f"  - {metric}: missing in folds {folds}")
        
        if report['summary']['invalid_count'] > 0:
            print(f"\nInvalid Metrics: {report['summary']['invalid_count']} issues found")
        
        if not report['summary']['consistency']['consistent']:
            print("\nConsistency Issues:")
            for issue in report['summary']['consistency']['issues']:
                print(f"  - {issue}")
        
        print("="*60 + "\n")


# Standalone validation functions
def validate_completeness(
    output_dir: Union[str, Path],
    required_metrics: List[str],
    n_folds: int
) -> Dict[str, Any]:
    """
    Validate completeness of saved metrics.
    
    Parameters
    ----------
    output_dir : Union[str, Path]
        Directory containing saved metrics
    required_metrics : List[str]
        List of required metric names
    n_folds : int
        Expected number of folds
        
    Returns
    -------
    Dict[str, Any]
        Validation report
        
    Examples
    --------
    >>> report = validate_completeness(
    ...     "./results",
    ...     ['balanced_accuracy', 'mcc', 'confusion_matrix'],
    ...     n_folds=5
    ... )
    >>> if report['complete']:
    ...     print("All metrics present!")
    """
    output_dir = Path(output_dir)
    
    validation = {
        'complete': True,
        'expected_folds': n_folds,
        'found_folds': 0,
        'missing_files': [],
        'summary': {}
    }
    
    # Check metrics directory
    metrics_dir = output_dir / 'metrics'
    if not metrics_dir.exists():
        validation['complete'] = False
        validation['missing_files'].append('metrics directory')
        return validation
    
    # Check for each required metric in each fold
    for fold in range(n_folds):
        fold_metrics = []
        for metric in required_metrics:
            # Try different file patterns
            patterns = [
                f"{metric}_fold_{fold:02d}.json",
                f"{metric}_fold_{fold}.json",
                f"fold_{fold:02d}_{metric}.json"
            ]
            
            found = False
            for pattern in patterns:
                if (metrics_dir / pattern).exists():
                    found = True
                    fold_metrics.append(metric)
                    break
            
            if not found:
                validation['complete'] = False
                validation['missing_files'].append(
                    f"fold_{fold:02d}/{metric}"
                )
        
        if fold_metrics:
            validation['found_folds'] += 1
    
    # Summary
    validation['summary'] = {
        'completeness_ratio': validation['found_folds'] / n_folds,
        'missing_count': len(validation['missing_files'])
    }
    
    return validation


def check_required_metrics(
    metrics_dict: Dict[str, Any],
    required: List[str]
) -> Tuple[bool, List[str]]:
    """
    Check if all required metrics are present.
    
    Parameters
    ----------
    metrics_dict : Dict[str, Any]
        Dictionary of available metrics
    required : List[str]
        List of required metric names
        
    Returns
    -------
    Tuple[bool, List[str]]
        (all_present, missing_metrics)
        
    Examples
    --------
    >>> metrics = {'balanced_accuracy': 0.85, 'mcc': 0.7}
    >>> complete, missing = check_required_metrics(
    ...     metrics,
    ...     ['balanced_accuracy', 'mcc', 'roc_auc']
    ... )
    >>> print(f"Missing: {missing}")  # ['roc_auc']
    """
    available = set(metrics_dict.keys())
    required_set = set(required)
    missing = list(required_set - available)
    
    return len(missing) == 0, missing
