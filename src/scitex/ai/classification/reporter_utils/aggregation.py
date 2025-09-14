#!/usr/bin/env python3
"""
Metric aggregation utilities for cross-fold analysis.

Provides functions to aggregate metrics across folds and create summary tables.
"""

import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple
import json
from collections import defaultdict


def aggregate_fold_metrics(
    fold_results: List[Dict[str, Any]],
    metrics_to_aggregate: Optional[List[str]] = None
) -> Dict[str, np.ndarray]:
    """
    Aggregate metrics across folds into arrays.
    
    Parameters
    ----------
    fold_results : List[Dict[str, Any]]
        List of metric dictionaries for each fold
    metrics_to_aggregate : List[str], optional
        Specific metrics to aggregate. If None, aggregate all numeric metrics.
        
    Returns
    -------
    Dict[str, np.ndarray]
        Arrays of metric values across folds
        
    Examples
    --------
    >>> fold_results = [
    ...     {'balanced_accuracy': 0.85, 'mcc': 0.70},
    ...     {'balanced_accuracy': 0.87, 'mcc': 0.73},
    ...     {'balanced_accuracy': 0.83, 'mcc': 0.68}
    ... ]
    >>> aggregated = aggregate_fold_metrics(fold_results)
    >>> print(f"BA values: {aggregated['balanced_accuracy']}")
    """
    aggregated = defaultdict(list)
    
    # Determine metrics to aggregate
    if metrics_to_aggregate is None:
        # Find all numeric metrics
        all_metrics = set()
        for fold in fold_results:
            for key, value in fold.items():
                # Check if value is numeric or contains numeric 'value' field
                if isinstance(value, (int, float)):
                    all_metrics.add(key)
                elif isinstance(value, dict) and 'value' in value:
                    if isinstance(value['value'], (int, float)):
                        all_metrics.add(key)
        metrics_to_aggregate = list(all_metrics)
    
    # Aggregate each metric
    for fold in fold_results:
        for metric in metrics_to_aggregate:
            if metric in fold:
                value = fold[metric]
                
                # Extract numeric value
                if isinstance(value, dict):
                    if 'value' in value:
                        value = value['value']
                    else:
                        continue
                
                if isinstance(value, (int, float)):
                    aggregated[metric].append(float(value))
    
    # Convert lists to numpy arrays
    result = {}
    for metric, values in aggregated.items():
        if values:  # Only include metrics with data
            result[metric] = np.array(values)
    
    return result


def calculate_mean_std(
    values: Union[List[float], np.ndarray],
    ddof: int = 1
) -> Tuple[float, float]:
    """
    Calculate mean and standard deviation.
    
    Parameters
    ----------
    values : Union[List[float], np.ndarray]
        Values to calculate statistics for
    ddof : int
        Degrees of freedom for std calculation
        
    Returns
    -------
    Tuple[float, float]
        (mean, std)
        
    Examples
    --------
    >>> mean, std = calculate_mean_std([0.85, 0.87, 0.83])
    >>> print(f"Mean: {mean:.3f}, Std: {std:.3f}")
    """
    values = np.asarray(values)
    mean = float(np.mean(values))
    std = float(np.std(values, ddof=ddof)) if len(values) > 1 else 0.0
    return mean, std


def create_summary_table(
    fold_results: List[Dict[str, Any]],
    metrics: Optional[List[str]] = None,
    include_stats: bool = True,
    format_digits: int = 3
) -> pd.DataFrame:
    """
    Create a summary table with fold results and statistics.
    
    Parameters
    ----------
    fold_results : List[Dict[str, Any]]
        List of metric dictionaries for each fold
    metrics : List[str], optional
        Metrics to include in table. If None, include all.
    include_stats : bool
        Whether to include mean/std rows
    format_digits : int
        Number of decimal places
        
    Returns
    -------
    pd.DataFrame
        Summary table with folds as rows and metrics as columns
        
    Examples
    --------
    >>> fold_results = [
    ...     {'fold': 0, 'balanced_accuracy': 0.85, 'mcc': 0.70},
    ...     {'fold': 1, 'balanced_accuracy': 0.87, 'mcc': 0.73},
    ...     {'fold': 2, 'balanced_accuracy': 0.83, 'mcc': 0.68}
    ... ]
    >>> df = create_summary_table(fold_results, include_stats=True)
    >>> print(df.to_string())
    """
    # Prepare data for DataFrame
    data = []
    
    # Determine metrics to include
    if metrics is None:
        metrics = set()
        for fold in fold_results:
            for key, value in fold.items():
                if key not in ['fold', 'fold_id', 'fold_idx']:
                    # Check if it's a numeric metric
                    if isinstance(value, (int, float)):
                        metrics.add(key)
                    elif isinstance(value, dict) and 'value' in value:
                        if isinstance(value['value'], (int, float)):
                            metrics.add(key)
        metrics = sorted(list(metrics))
    
    # Add fold results
    for i, fold in enumerate(fold_results):
        row = {'Fold': fold.get('fold_id', fold.get('fold', i))}
        
        for metric in metrics:
            if metric in fold:
                value = fold[metric]
                
                # Extract numeric value
                if isinstance(value, dict) and 'value' in value:
                    value = value['value']
                
                if isinstance(value, (int, float)):
                    row[metric.replace('_', ' ').title()] = value
                else:
                    row[metric.replace('_', ' ').title()] = None
            else:
                row[metric.replace('_', ' ').title()] = None
        
        data.append(row)
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Add statistics rows if requested
    if include_stats and len(data) > 0:
        # Calculate statistics for each metric
        mean_row = {'Fold': 'Mean'}
        std_row = {'Fold': 'Std'}
        
        for col in df.columns:
            if col != 'Fold':
                values = df[col].dropna().values
                if len(values) > 0:
                    mean, std = calculate_mean_std(values)
                    mean_row[col] = mean
                    std_row[col] = std
        
        # Append statistics rows
        df = pd.concat([
            df,
            pd.DataFrame([mean_row]),
            pd.DataFrame([std_row])
        ], ignore_index=True)
    
    # Format numeric columns
    for col in df.columns:
        if col != 'Fold':
            df[col] = df[col].apply(
                lambda x: f"{x:.{format_digits}f}" if pd.notna(x) else 'N/A'
            )
    
    return df


def aggregate_confusion_matrices(
    confusion_matrices: List[np.ndarray]
) -> np.ndarray:
    """
    Aggregate confusion matrices across folds.
    
    Parameters
    ----------
    confusion_matrices : List[np.ndarray]
        List of confusion matrices from each fold
        
    Returns
    -------
    np.ndarray
        Summed confusion matrix
        
    Examples
    --------
    >>> cms = [np.array([[8, 2], [1, 9]]) for _ in range(3)]
    >>> total_cm = aggregate_confusion_matrices(cms)
    >>> print(total_cm)
    """
    if not confusion_matrices:
        raise ValueError("No confusion matrices provided")
    
    # Check all matrices have same shape
    shape = confusion_matrices[0].shape
    for cm in confusion_matrices[1:]:
        if cm.shape != shape:
            raise ValueError(f"Inconsistent confusion matrix shapes: {shape} vs {cm.shape}")
    
    # Sum all matrices
    total = np.sum(confusion_matrices, axis=0)
    return total


def aggregate_classification_reports(
    reports: List[pd.DataFrame],
    weighted_average: bool = True
) -> pd.DataFrame:
    """
    Aggregate classification reports across folds.
    
    Parameters
    ----------
    reports : List[pd.DataFrame]
        List of classification report DataFrames
    weighted_average : bool
        Whether to use weighted average based on support
        
    Returns
    -------
    pd.DataFrame
        Aggregated classification report
        
    Examples
    --------
    >>> reports = [report_fold1_df, report_fold2_df, report_fold3_df]
    >>> agg_report = aggregate_classification_reports(reports)
    >>> print(agg_report)
    """
    if not reports:
        raise ValueError("No classification reports provided")
    
    # Get all class labels (rows)
    all_labels = set()
    for report in reports:
        all_labels.update(report.index.tolist())
    all_labels = sorted(list(all_labels))
    
    # Initialize aggregated data
    aggregated = {}
    
    for label in all_labels:
        label_data = {'precision': [], 'recall': [], 'f1-score': [], 'support': []}
        
        for report in reports:
            if label in report.index:
                row = report.loc[label]
                for metric in ['precision', 'recall', 'f1-score']:
                    if metric in row:
                        label_data[metric].append(row[metric])
                if 'support' in row:
                    label_data['support'].append(row['support'])
        
        # Calculate aggregated metrics
        if label_data['support'] and weighted_average:
            # Weighted average based on support
            total_support = sum(label_data['support'])
            weights = np.array(label_data['support']) / total_support
            
            aggregated[label] = {}
            for metric in ['precision', 'recall', 'f1-score']:
                if label_data[metric]:
                    aggregated[label][metric] = np.average(
                        label_data[metric], 
                        weights=weights[:len(label_data[metric])]
                    )
            aggregated[label]['support'] = sum(label_data['support'])
        else:
            # Simple average
            aggregated[label] = {}
            for metric in ['precision', 'recall', 'f1-score']:
                if label_data[metric]:
                    aggregated[label][metric] = np.mean(label_data[metric])
            if label_data['support']:
                aggregated[label]['support'] = sum(label_data['support'])
    
    # Convert to DataFrame
    agg_df = pd.DataFrame.from_dict(aggregated, orient='index')
    return agg_df


def calculate_metric_confidence_interval(
    values: Union[List[float], np.ndarray],
    confidence: float = 0.95
) -> Tuple[float, float, float]:
    """
    Calculate confidence interval for a metric.
    
    Parameters
    ----------
    values : Union[List[float], np.ndarray]
        Metric values across folds
    confidence : float
        Confidence level (e.g., 0.95 for 95%)
        
    Returns
    -------
    Tuple[float, float, float]
        (mean, lower_bound, upper_bound)
        
    Examples
    --------
    >>> values = [0.85, 0.87, 0.83, 0.86, 0.84]
    >>> mean, lower, upper = calculate_metric_confidence_interval(values)
    >>> print(f"Mean: {mean:.3f} [{lower:.3f}, {upper:.3f}]")
    """
    from scipy import stats
    
    values = np.asarray(values)
    n = len(values)
    
    if n < 2:
        # Not enough data for confidence interval
        mean = float(values[0]) if n == 1 else 0.0
        return mean, mean, mean
    
    mean = np.mean(values)
    sem = stats.sem(values)  # Standard error of the mean
    
    # Calculate confidence interval
    interval = stats.t.interval(
        confidence,
        n - 1,
        loc=mean,
        scale=sem
    )
    
    return float(mean), float(interval[0]), float(interval[1])


def merge_fold_results(
    results_dir: Union[str, Path],
    n_folds: int
) -> Dict[str, Any]:
    """
    Merge results from multiple fold directories.
    
    Parameters
    ----------
    results_dir : Union[str, Path]
        Base directory containing fold subdirectories
    n_folds : int
        Number of folds to merge
        
    Returns
    -------
    Dict[str, Any]
        Merged results dictionary
        
    Examples
    --------
    >>> merged = merge_fold_results("./results", n_folds=5)
    >>> print(f"Found {len(merged['folds'])} folds")
    """
    results_dir = Path(results_dir)
    merged = {
        'folds': [],
        'metrics': defaultdict(list)
    }
    
    # Load each fold
    for fold_idx in range(n_folds):
        fold_dir = results_dir / f"fold_{fold_idx:02d}"
        if not fold_dir.exists():
            fold_dir = results_dir / f"fold_{fold_idx}"  # Try without padding
        
        if fold_dir.exists():
            fold_data = {'fold_id': fold_idx}
            
            # Load metrics
            metrics_dir = fold_dir / 'metrics'
            if metrics_dir.exists():
                for metric_file in metrics_dir.glob('*.json'):
                    with open(metric_file, 'r') as f:
                        metric_data = json.load(f)
                        metric_name = metric_file.stem
                        fold_data[metric_name] = metric_data
                        
                        # Add to aggregated metrics
                        if 'value' in metric_data:
                            merged['metrics'][metric_name].append(metric_data['value'])
            
            # Load confusion matrix if exists
            cm_path = fold_dir / 'confusion_matrix.npy'
            if cm_path.exists():
                fold_data['confusion_matrix'] = np.load(cm_path)
            
            merged['folds'].append(fold_data)
    
    # Calculate summary statistics
    merged['summary'] = {}
    for metric_name, values in merged['metrics'].items():
        if values:
            mean, std = calculate_mean_std(values)
            merged['summary'][metric_name] = {
                'mean': mean,
                'std': std,
                'min': float(np.min(values)),
                'max': float(np.max(values)),
                'values': values
            }
    
    return merged
