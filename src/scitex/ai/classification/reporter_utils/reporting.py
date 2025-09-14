#!/usr/bin/env python3
"""
Report generation utilities for classification results.

Provides functions to create publication-ready reports in various formats.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import json


def generate_markdown_report(
    results: Dict[str, Any],
    output_path: Union[str, Path],
    include_plots: bool = True
) -> None:
    """
    Generate a comprehensive markdown report.
    
    Parameters
    ----------
    results : Dict[str, Any]
        Complete results dictionary with metrics and metadata
    output_path : Union[str, Path]
        Path to save the markdown report
    include_plots : bool
        Whether to include links to plot files
        
    Examples
    --------
    >>> generate_markdown_report(
    ...     results,
    ...     "./results/report.md",
    ...     include_plots=True
    ... )
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    lines = []
    
    # Header
    lines.append("# Classification Results Report")
    lines.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Configuration section
    if 'config' in results:
        lines.append("## Experiment Configuration")
        lines.append("")
        config = results['config']
        lines.append(f"- **Name**: {config.get('name', 'Unknown')}")
        lines.append(f"- **Classifier**: {config.get('classifier', 'Unknown')}")
        lines.append(f"- **Dataset**: {config.get('dataset', 'Unknown')}")
        lines.append(f"- **N Folds**: {config.get('n_folds', 'Unknown')}")
        lines.append(f"- **Random Seed**: {config.get('random_seed', 'Unknown')}")
        lines.append("")
    
    # Summary statistics
    if 'summary' in results:
        lines.append("## Summary Statistics")
        lines.append("")
        lines.append("| Metric | Mean ± Std | Min | Max |")
        lines.append("|--------|------------|-----|-----|")
        
        for metric, stats in results['summary'].items():
            if isinstance(stats, dict) and 'mean' in stats:
                mean = stats['mean']
                std = stats['std']
                min_val = stats['min']
                max_val = stats['max']
                lines.append(
                    f"| {metric} | {mean:.3f} ± {std:.3f} | {min_val:.3f} | {max_val:.3f} |"
                )
        lines.append("")
    
    # Per-fold results
    if 'folds' in results:
        lines.append("## Per-Fold Results")
        lines.append("")
        
        # Create DataFrame for better formatting
        fold_data = []
        for fold_result in results['folds']:
            fold_row = {'Fold': fold_result.get('fold_id', 'Unknown')}
            for metric in ['balanced_accuracy', 'mcc', 'roc_auc', 'pr_auc']:
                if metric in fold_result:
                    value = fold_result[metric]
                    if isinstance(value, dict):
                        value = value.get('value', 'N/A')
                    fold_row[metric.replace('_', ' ').title()] = f"{float(value):.3f}" if value != 'N/A' else 'N/A'
            fold_data.append(fold_row)
        
        if fold_data:
            df = pd.DataFrame(fold_data)
            # Try to use to_markdown, fallback to to_string if not available
            try:
                lines.append(df.to_markdown(index=False))
            except:
                lines.append(df.to_string(index=False))
            lines.append("")
    
    # Plots section
    if include_plots and 'plots' in results:
        lines.append("## Figures")
        lines.append("")
        
        for plot_name, plot_path in results['plots'].items():
            lines.append(f"### {plot_name.replace('_', ' ').title()}")
            lines.append(f"![{plot_name}]({plot_path})")
            lines.append("")
    
    # Validation section
    if 'validation' in results:
        lines.append("## Validation Report")
        lines.append("")
        validation = results['validation']
        status = "✓ Complete" if validation.get('complete', False) else "✗ Incomplete"
        lines.append(f"**Status**: {status}")
        
        if 'missing_by_fold' in validation and validation['missing_by_fold']:
            lines.append("\n**Missing Metrics**:")
            for fold_id, missing in validation['missing_by_fold'].items():
                lines.append(f"- Fold {fold_id}: {', '.join(missing)}")
        lines.append("")
    
    # Notes section
    if 'notes' in results:
        lines.append("## Notes")
        lines.append("")
        lines.append(results['notes'])
        lines.append("")
    
    # Write report
    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))


def generate_latex_report(
    results: Dict[str, Any],
    output_path: Union[str, Path],
    document_class: str = "article"
) -> None:
    """
    Generate a LaTeX report suitable for publication.
    
    Parameters
    ----------
    results : Dict[str, Any]
        Complete results dictionary
    output_path : Union[str, Path]
        Path to save the LaTeX report
    document_class : str
        LaTeX document class to use
        
    Examples
    --------
    >>> generate_latex_report(
    ...     results,
    ...     "./results/report.tex"
    ... )
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    lines = []
    
    # LaTeX preamble
    lines.append(f"\\documentclass{{{document_class}}}")
    lines.append("\\usepackage{booktabs}")
    lines.append("\\usepackage{graphicx}")
    lines.append("\\usepackage{amsmath}")
    lines.append("\\begin{document}")
    lines.append("")
    
    # Title
    lines.append("\\section{Classification Results}")
    lines.append("")
    
    # Summary table
    if 'summary' in results:
        lines.append("\\subsection{Summary Statistics}")
        lines.append("")
        lines.append("\\begin{table}[h]")
        lines.append("\\centering")
        lines.append("\\begin{tabular}{lccc}")
        lines.append("\\toprule")
        lines.append("Metric & Mean $\\pm$ Std & Min & Max \\\\")
        lines.append("\\midrule")
        
        for metric, stats in results['summary'].items():
            if isinstance(stats, dict) and 'mean' in stats:
                metric_name = metric.replace('_', ' ').title()
                mean = stats['mean']
                std = stats['std']
                min_val = stats['min']
                max_val = stats['max']
                lines.append(
                    f"{metric_name} & ${mean:.3f} \\pm {std:.3f}$ & "
                    f"{min_val:.3f} & {max_val:.3f} \\\\"
                )
        
        lines.append("\\bottomrule")
        lines.append("\\end{tabular}")
        lines.append("\\caption{Classification performance metrics across all folds}")
        lines.append("\\end{table}")
        lines.append("")
    
    lines.append("\\end{document}")
    
    # Write LaTeX file
    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))


def create_summary_statistics(
    fold_metrics: List[Dict[str, float]],
    metrics_to_summarize: Optional[List[str]] = None
) -> Dict[str, Dict[str, float]]:
    """
    Calculate summary statistics across folds.
    
    Parameters
    ----------
    fold_metrics : List[Dict[str, float]]
        List of metric dictionaries for each fold
    metrics_to_summarize : List[str], optional
        Specific metrics to summarize. If None, summarize all.
        
    Returns
    -------
    Dict[str, Dict[str, float]]
        Summary statistics for each metric
        
    Examples
    --------
    >>> fold_metrics = [
    ...     {'balanced_accuracy': 0.85, 'mcc': 0.70},
    ...     {'balanced_accuracy': 0.87, 'mcc': 0.73},
    ...     {'balanced_accuracy': 0.83, 'mcc': 0.68}
    ... ]
    >>> summary = create_summary_statistics(fold_metrics)
    >>> print(f"BA: {summary['balanced_accuracy']['mean']:.3f}")
    """
    summary = {}
    
    # Determine which metrics to summarize
    if metrics_to_summarize is None:
        all_metrics = set()
        for fold in fold_metrics:
            all_metrics.update(fold.keys())
        metrics_to_summarize = list(all_metrics)
    
    # Calculate statistics for each metric
    for metric in metrics_to_summarize:
        values = []
        for fold in fold_metrics:
            if metric in fold:
                value = fold[metric]
                # Extract value if it's a dict
                if isinstance(value, dict) and 'value' in value:
                    value = value['value']
                if isinstance(value, (int, float)):
                    values.append(float(value))
        
        if values:
            summary[metric] = {
                'mean': float(np.mean(values)),
                'std': float(np.std(values, ddof=1)) if len(values) > 1 else 0.0,
                'min': float(np.min(values)),
                'max': float(np.max(values)),
                'median': float(np.median(values)),
                'values': values,
                'n_folds': len(values)
            }
    
    return summary


def export_for_paper(
    results: Dict[str, Any],
    output_dir: Union[str, Path],
    format_digits: int = 3
) -> Dict[str, Path]:
    """
    Export results in formats suitable for academic papers.
    
    Creates:
    - CSV table with mean ± std format
    - LaTeX table ready for inclusion
    - JSON with all raw data
    
    Parameters
    ----------
    results : Dict[str, Any]
        Complete results dictionary
    output_dir : Union[str, Path]
        Directory to save exports
    format_digits : int
        Number of decimal places for formatting
        
    Returns
    -------
    Dict[str, Path]
        Paths to created files
        
    Examples
    --------
    >>> paths = export_for_paper(
    ...     results,
    ...     "./paper_exports",
    ...     format_digits=3
    ... )
    >>> print(f"LaTeX table: {paths['latex_table']}")
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    created_files = {}
    
    # Format for mean ± std
    def format_mean_std(mean, std, digits=format_digits):
        return f"{mean:.{digits}f} ± {std:.{digits}f}"
    
    # Create summary DataFrame
    if 'summary' in results:
        summary_data = []
        for metric, stats in results['summary'].items():
            if isinstance(stats, dict) and 'mean' in stats:
                summary_data.append({
                    'Metric': metric.replace('_', ' ').title(),
                    'Mean ± Std': format_mean_std(stats['mean'], stats['std']),
                    'Min': f"{stats['min']:.{format_digits}f}",
                    'Max': f"{stats['max']:.{format_digits}f}"
                })
        
        if summary_data:
            df = pd.DataFrame(summary_data)
            
            # Save as CSV
            csv_path = output_dir / 'summary_table.csv'
            df.to_csv(csv_path, index=False)
            created_files['csv_table'] = csv_path
            
            # Save as LaTeX table
            latex_path = output_dir / 'summary_table.tex'
            with open(latex_path, 'w') as f:
                f.write("% Classification Results Summary Table\n")
                f.write("% Include in your LaTeX document with \\input{summary_table.tex}\n\n")
                f.write("\\begin{table}[htbp]\n")
                f.write("\\centering\n")
                f.write("\\caption{Classification Performance Metrics}\n")
                f.write("\\label{tab:classification_results}\n")
                f.write(df.to_latex(index=False, escape=False))
                f.write("\\end{table}\n")
            created_files['latex_table'] = latex_path
    
    # Save raw JSON data
    json_path = output_dir / 'raw_results.json'
    with open(json_path, 'w') as f:
        # Convert numpy types for JSON serialization
        def convert(obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, (np.integer, np.int64)):
                return int(obj)
            elif isinstance(obj, (np.floating, np.float64)):
                return float(obj)
            elif isinstance(obj, pd.DataFrame):
                return obj.to_dict()
            return obj
        
        json.dump(results, f, indent=2, default=convert)
    created_files['raw_json'] = json_path
    
    # Create a README
    readme_path = output_dir / 'README.md'
    with open(readme_path, 'w') as f:
        f.write("# Classification Results Export\n\n")
        f.write("## Files\n\n")
        f.write("- `summary_table.csv`: Results table in CSV format\n")
        f.write("- `summary_table.tex`: LaTeX table for direct inclusion\n")
        f.write("- `raw_results.json`: Complete raw data in JSON format\n\n")
        f.write("## Usage\n\n")
        f.write("### LaTeX\n")
        f.write("```latex\n")
        f.write("\\input{summary_table.tex}\n")
        f.write("```\n\n")
        f.write("### Python\n")
        f.write("```python\n")
        f.write("import pandas as pd\n")
        f.write("df = pd.read_csv('summary_table.csv')\n")
        f.write("```\n")
    created_files['readme'] = readme_path
    
    return created_files


def format_classification_report(
    report_df: pd.DataFrame,
    format_type: str = "markdown"
) -> str:
    """
    Format sklearn classification report DataFrame.
    
    Parameters
    ----------
    report_df : pd.DataFrame
        Classification report as DataFrame
    format_type : str
        Output format ('markdown', 'latex', 'html')
        
    Returns
    -------
    str
        Formatted report string
    """
    if format_type == "markdown":
        return report_df.to_markdown()
    elif format_type == "latex":
        return report_df.to_latex()
    elif format_type == "html":
        return report_df.to_html()
    else:
        return str(report_df)
