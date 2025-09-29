#!/usr/bin/env python3
"""
Data models for classification reporting using dataclasses.

Provides type-safe, validated data structures for metrics and reports.
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import numpy as np
import pandas as pd
from datetime import datetime
import json


@dataclass
class MetricResult:
    """Single metric result with metadata."""
    
    metric_name: str
    value: Union[float, np.ndarray, pd.DataFrame]
    fold: Optional[int] = None
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            'metric': self.metric_name,
            'fold': self.fold,
            'timestamp': self.timestamp.isoformat()
        }
        
        # Handle different value types
        if isinstance(self.value, (int, float)):
            result['value'] = float(self.value)
        elif isinstance(self.value, np.ndarray):
            result['value'] = self.value.tolist()
        elif isinstance(self.value, pd.DataFrame):
            result['value'] = self.value.to_dict()
        else:
            result['value'] = str(self.value)
            
        result.update(self.metadata)
        return result
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    def save(self, path: Union[str, Path]) -> None:
        """Save metric to file based on type."""
        path = Path(path)
        
        if isinstance(self.value, pd.DataFrame):
            # Save DataFrames as CSV
            self.value.to_csv(path.with_suffix('.csv'))
        elif isinstance(self.value, np.ndarray):
            # Save arrays as NPY
            np.save(path.with_suffix('.npy'), self.value)
        else:
            # Save scalars as JSON
            with open(path.with_suffix('.json'), 'w') as f:
                json.dump(self.to_dict(), f, indent=2)


@dataclass
class FoldResults:
    """Results for a single fold."""
    
    fold_id: int
    balanced_accuracy: Optional[MetricResult] = None
    mcc: Optional[MetricResult] = None
    confusion_matrix: Optional[MetricResult] = None
    classification_report: Optional[MetricResult] = None
    roc_auc: Optional[MetricResult] = None
    pr_auc: Optional[MetricResult] = None
    custom_metrics: Dict[str, MetricResult] = field(default_factory=dict)
    
    def is_complete(self, required_metrics: List[str]) -> bool:
        """Check if all required metrics are present."""
        available = self.get_available_metrics()
        return all(metric in available for metric in required_metrics)
    
    def get_available_metrics(self) -> List[str]:
        """Get list of available metrics."""
        metrics = []
        if self.balanced_accuracy is not None:
            metrics.append('balanced_accuracy')
        if self.mcc is not None:
            metrics.append('mcc')
        if self.confusion_matrix is not None:
            metrics.append('confusion_matrix')
        if self.classification_report is not None:
            metrics.append('classification_report')
        if self.roc_auc is not None:
            metrics.append('roc_auc')
        if self.pr_auc is not None:
            metrics.append('pr_auc')
        metrics.extend(self.custom_metrics.keys())
        return metrics
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {'fold_id': self.fold_id}
        
        for metric_name in ['balanced_accuracy', 'mcc', 'roc_auc', 'pr_auc']:
            metric = getattr(self, metric_name)
            if metric is not None:
                result[metric_name] = metric.to_dict()
                
        # Add custom metrics
        for name, metric in self.custom_metrics.items():
            result[name] = metric.to_dict()
            
        return result


@dataclass
class ExperimentConfig:
    """Configuration for an experiment."""
    
    name: str
    output_dir: Path
    n_folds: int = 5
    required_metrics: List[str] = field(default_factory=lambda: [
        'balanced_accuracy', 'mcc', 'confusion_matrix', 'classification_report'
    ])
    classifier: str = 'unknown'
    dataset: str = 'unknown'
    features: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    random_seed: int = 42
    timestamp: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Ensure output_dir is a Path object."""
        if isinstance(self.output_dir, str):
            self.output_dir = Path(self.output_dir)
            
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'name': self.name,
            'output_dir': str(self.output_dir),
            'n_folds': self.n_folds,
            'required_metrics': self.required_metrics,
            'classifier': self.classifier,
            'dataset': self.dataset,
            'features': self.features,
            'parameters': self.parameters,
            'random_seed': self.random_seed,
            'timestamp': self.timestamp.isoformat()
        }
    
    def save(self) -> None:
        """Save configuration to output directory."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        config_path = self.output_dir / 'experiment_config.json'
        with open(config_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)


@dataclass
class ExperimentResults:
    """Complete results for an experiment."""
    
    config: ExperimentConfig
    fold_results: List[FoldResults] = field(default_factory=list)
    summary_statistics: Optional[Dict[str, Any]] = None
    
    def add_fold(self, fold_result: FoldResults) -> None:
        """Add results for a fold."""
        self.fold_results.append(fold_result)
        
    def validate_completeness(self) -> Dict[str, Any]:
        """Validate that all required metrics are present for all folds."""
        validation = {
            'complete': True,
            'missing_by_fold': {},
            'summary': {
                'n_folds_expected': self.config.n_folds,
                'n_folds_actual': len(self.fold_results),
                'required_metrics': self.config.required_metrics
            }
        }
        
        # Check number of folds
        if len(self.fold_results) != self.config.n_folds:
            validation['complete'] = False
            validation['summary']['error'] = f"Expected {self.config.n_folds} folds, got {len(self.fold_results)}"
        
        # Check each fold
        for fold_result in self.fold_results:
            if not fold_result.is_complete(self.config.required_metrics):
                validation['complete'] = False
                missing = set(self.config.required_metrics) - set(fold_result.get_available_metrics())
                validation['missing_by_fold'][fold_result.fold_id] = list(missing)
                
        return validation
    
    def calculate_summary_statistics(self) -> Dict[str, Any]:
        """Calculate summary statistics across folds."""
        summary = {}
        
        # Collect metrics across folds
        metrics_data = {
            'balanced_accuracy': [],
            'mcc': [],
            'roc_auc': [],
            'pr_auc': []
        }
        
        for fold_result in self.fold_results:
            for metric_name in metrics_data.keys():
                metric = getattr(fold_result, metric_name)
                if metric is not None and isinstance(metric.value, (int, float)):
                    metrics_data[metric_name].append(metric.value)
        
        # Calculate statistics
        for metric_name, values in metrics_data.items():
            if values:
                summary[metric_name] = {
                    'mean': float(np.mean(values)),
                    'std': float(np.std(values, ddof=1)) if len(values) > 1 else 0.0,
                    'min': float(np.min(values)),
                    'max': float(np.max(values)),
                    'values': values
                }
        
        self.summary_statistics = summary
        return summary
    
    def to_dataframe(self) -> pd.DataFrame:
        """Convert results to a DataFrame for easy analysis."""
        data = []
        for fold_result in self.fold_results:
            row = {'fold': fold_result.fold_id}
            
            # Add standard metrics
            for metric_name in ['balanced_accuracy', 'mcc', 'roc_auc', 'pr_auc']:
                metric = getattr(fold_result, metric_name)
                if metric is not None and isinstance(metric.value, (int, float)):
                    row[metric_name] = metric.value
            
            # Add custom metrics
            for name, metric in fold_result.custom_metrics.items():
                if isinstance(metric.value, (int, float)):
                    row[name] = metric.value
                    
            data.append(row)
        
        df = pd.DataFrame(data)
        
        # Add summary statistics as final rows
        if self.summary_statistics:
            for metric_name, stats in self.summary_statistics.items():
                if metric_name in df.columns:
                    # Add mean and std rows
                    mean_row = {'fold': 'mean'}
                    std_row = {'fold': 'std'}
                    for col in df.columns:
                        if col != 'fold' and col in self.summary_statistics:
                            mean_row[col] = self.summary_statistics[col]['mean']
                            std_row[col] = self.summary_statistics[col]['std']
                    
            # Append summary rows if we have data
            if len(data) > 0 and self.summary_statistics:
                df = pd.concat([df, pd.DataFrame([mean_row, std_row])], ignore_index=True)
        
        return df
    
    def save(self) -> None:
        """Save all results to the output directory."""
        output_dir = self.config.output_dir
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save configuration
        self.config.save()
        
        # Save fold results
        for fold_result in self.fold_results:
            fold_dir = output_dir / f'fold_{fold_result.fold_id:02d}'
            fold_dir.mkdir(exist_ok=True)
            
            # Save each metric
            for metric_name in ['balanced_accuracy', 'mcc', 'roc_auc', 'pr_auc']:
                metric = getattr(fold_result, metric_name)
                if metric is not None:
                    metric.save(fold_dir / metric_name)
            
            # Save confusion matrix
            if fold_result.confusion_matrix is not None:
                fold_result.confusion_matrix.save(fold_dir / 'confusion_matrix')
            
            # Save classification report
            if fold_result.classification_report is not None:
                fold_result.classification_report.save(fold_dir / 'classification_report')
        
        # Save summary
        if self.summary_statistics:
            with open(output_dir / 'summary_statistics.json', 'w') as f:
                json.dump(self.summary_statistics, f, indent=2)
        
        # Save results DataFrame
        df = self.to_dataframe()
        df.to_csv(output_dir / 'all_results.csv', index=False)
        
        # Save validation report
        validation = self.validate_completeness()
        with open(output_dir / 'validation_report.json', 'w') as f:
            json.dump(validation, f, indent=2)