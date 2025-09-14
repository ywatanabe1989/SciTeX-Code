#!/usr/bin/env python3
"""
Classification reporter utilities for modular metric calculation and reporting.

This module provides separated, focused utilities for:
- Metric calculations
- File organization
- Validation
- Report generation
"""

from .metrics import (
    calc_balanced_accuracy,
    calc_mcc,
    calc_confusion_matrix,
    calc_classification_report,
    calc_roc_auc,
    calc_pr_auc
)

from .storage import (
    MetricStorage,
    save_metric,
    save_figure,
    save_dataframe,
    organize_outputs
)

from .validation import (
    MetricValidator,
    validate_completeness,
    check_required_metrics
)

from .reporting import (
    generate_markdown_report,
    generate_latex_report,
    create_summary_statistics,
    export_for_paper
)

from .aggregation import (
    aggregate_fold_metrics,
    calculate_mean_std,
    create_summary_table,
    aggregate_confusion_matrices
)

__all__ = [
    # Metrics
    'calc_balanced_accuracy',
    'calc_mcc', 
    'calc_confusion_matrix',
    'calc_classification_report',
    'calc_roc_auc',
    'calc_pr_auc',
    
    # Storage
    'MetricStorage',
    'save_metric',
    'save_figure',
    'save_dataframe',
    'organize_outputs',
    
    # Validation
    'MetricValidator',
    'validate_completeness',
    'check_required_metrics',
    
    # Reporting
    'generate_markdown_report',
    'generate_latex_report',
    'create_summary_statistics',
    'export_for_paper',
    
    # Aggregation
    'aggregate_fold_metrics',
    'calculate_mean_std',
    'create_summary_table',
    'aggregate_confusion_matrices'
]