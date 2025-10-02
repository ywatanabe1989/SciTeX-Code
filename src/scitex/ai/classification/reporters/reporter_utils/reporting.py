#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-22 03:00:00 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/ai/classification/reporter_utils/reporting.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Report generation utilities for classification reporters.

Supports multiple output formats:
- Org-mode with inline images
- Markdown with embedded plots
- LaTeX for academic papers
- Paper export functionality
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import numpy as np
import pandas as pd
from datetime import datetime
import yaml


def generate_org_report(
    results: Dict[str, Any],
    output_path: Union[str, Path],
    include_plots: bool = True,
    verbose: bool = True,
    convert_formats: bool = True,
) -> Path:
    """
    Generate org-mode report with inline images and optional pandoc conversions.
    
    Parameters
    ----------
    results : Dict[str, Any]
        Classification results dictionary
    output_path : Union[str, Path]
        Output file path
    include_plots : bool, default True
        Whether to include plot images
    verbose : bool, default True
        Whether to print progress messages
    convert_formats : bool, default True
        Whether to use pandoc to generate other formats
    
    Returns
    -------
    Path
        Path to generated report
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Try to get CONFIG from results first (passed from memory)
    config_data = None
    # Debug logging
    from scitex.logging import getLogger
    logger = getLogger(__name__)
    
    # First check if session_config was passed in results
    if 'session_config' in results and results['session_config'] is not None:
        # Convert CONFIG object to dict, only keeping useful fields
        session_config = results['session_config']
        config_data = {}
        
        # List of keys to include (uppercase attributes that are not methods)
        useful_keys = ['ID', 'PID', 'START_TIME', 'END_TIME', 'RUN_TIME', 
                       'FILE', 'FILE_PATH', 'SDIR', 'SDIR_PATH', 
                       'REL_SDIR', 'REL_SDIR_PATH', 'ARGS', 'EXIT_STATUS']
        
        for key in useful_keys:
            if hasattr(session_config, key):
                value = getattr(session_config, key)
                # Convert to string for display, avoiding repr() formatting
                if value is not None:
                    if isinstance(value, (str, int, float, bool)):
                        config_data[key] = value
                    else:
                        # Use str() for cleaner output
                        config_data[key] = str(value)
        
        logger.info(f"Using session CONFIG from memory with {len(config_data)} keys")
    
    # Fallback to loading from file if not provided
    if config_data is None:
        try:
            # Try different possible locations for CONFIG.yaml
            # The report is generated in classification_results/reports/
            # CONFIG.yaml is in the session directory under CONFIGS/
            
            # Get the session directory from the output path
            # output_path is like: /path/to/RUNNING/ID/classification_results/reports/report.org
            # We need: /path/to/RUNNING/ID/CONFIGS/CONFIG.yaml
            
            # output_path.parent = /path/to/RUNNING/ID/classification_results/reports/
            # output_path.parent.parent = /path/to/RUNNING/ID/classification_results/
            # output_path.parent.parent.parent = /path/to/RUNNING/ID/  <- Session root!
            
            session_dir = output_path.parent.parent.parent
            possible_paths = [
                session_dir / "CONFIGS" / "CONFIG.yaml",  # This should be the correct path
            ]
            
            logger.info(f"Looking for CONFIG.yaml from: {output_path}")
            logger.info(f"Output path parent dirs: {output_path.parent}, {output_path.parent.parent}, {output_path.parent.parent.parent}")
            config_path = None
            for path in possible_paths:
                logger.info(f"Checking path: {path}, exists: {path.exists()}")
                if path.exists():
                    config_path = path
                    logger.info(f"Found CONFIG at path: {config_path}")
                    break
            
            # Try to get from session output directory if not found
            if not config_path and 'config' in results and 'output_dir' in results['config']:
                # The output_dir is like /path/to/RUNNING/ID/classification_results
                # We need to go to /path/to/RUNNING/ID/CONFIGS/CONFIG.yaml
                output_dir = Path(results['config']['output_dir'])
                # Go up to session dir (from classification_results to session root)
                session_dir = output_dir.parent  
                config_path = session_dir / "CONFIGS" / "CONFIG.yaml"
                logger.info(f"Trying session path: {config_path}, exists: {config_path.exists()}")
                if not config_path.exists():
                    config_path = None
            
            if config_path and config_path.exists():
                logger.info(f"Found CONFIG at: {config_path}")
                with open(config_path, 'r') as config_file:
                    config_data = yaml.safe_load(config_file)
                logger.info(f"Successfully loaded CONFIG with {len(config_data)} keys")
            else:
                logger.warning(f"No CONFIG.yaml found in any expected location")
        except Exception as e:
            # Always log the error for debugging
            logger.warning(f"Could not load CONFIG.yaml: {e}")
            import traceback
            logger.warning(f"Traceback: {traceback.format_exc()}")
    
    with open(output_path, 'w') as f:
        # Header
        f.write("#+TITLE: Classification Results Report\n")
        f.write(f"#+AUTHOR: SciTeX Classification Reporter\n")
        f.write(f"#+DATE: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("#+OPTIONS: toc:2 num:t\n")
        f.write("#+STARTUP: overview inlineimages\n")
        f.write("#+HTML_HEAD: <style>img { cursor: zoom-in; } img:active { transform: scale(2.5); z-index: 999; position: relative; }</style>\n")
        f.write("#+ATTR_ORG: :width 400\n\n")  # Default width for all images
        
        # Get configuration and fold info
        config = results.get('config', {})
        n_folds = config.get('n_folds', len(results.get('folds', [])))
        
        # Dataset information (sample sizes) - extract from folds
        f.write("* Dataset Information\n\n")
        if 'folds' in results and results['folds']:
            # Create table header
            sample_header = "| Fold | Train Total | Train Seizure | Train Interictal | Test Total | Test Seizure | Test Interictal |"
            sample_separator = "|------|-------------|---------------|------------------|------------|--------------|-----------------|"

            f.write(sample_header + "\n")
            f.write(sample_separator + "\n")

            # Add sample size info for each fold if available
            for fold_data in results['folds']:
                fold_id = fold_data.get('fold_id', '?')
                # Sample sizes might be in fold_data directly or we need to compute
                n_train = fold_data.get('n_train', '-')
                n_test = fold_data.get('n_test', '-')
                n_train_seizure = fold_data.get('n_train_seizure', '-')
                n_train_interictal = fold_data.get('n_train_interictal', '-')
                n_test_seizure = fold_data.get('n_test_seizure', '-')
                n_test_interictal = fold_data.get('n_test_interictal', '-')

                row = f"| {fold_id:02d} | {n_train} | {n_train_seizure} | {n_train_interictal} | {n_test} | {n_test_seizure} | {n_test_interictal} |"
                f.write(row + "\n")
            f.write("\n")

        f.write("* Summary Performance\n\n")

        # Create comprehensive metrics table including per-fold values
        if 'summary' in results and results['summary']:
            # Build header with fold columns
            header = "| Metric |"
            separator = "|--------|"
            for i in range(n_folds):
                header += f" Fold {i:02d} |"
                separator += "---------|"
            header += " Mean ± Std |"
            separator += "------------|"

            f.write(header + "\n")
            f.write(separator + "\n")

            # Display metrics in specific order
            metric_order = ['balanced_accuracy', 'mcc', 'roc_auc', 'pr_auc']
            metric_display_names = {
                'balanced_accuracy': 'Balanced Accuracy',
                'mcc': 'MCC',
                'roc_auc': 'ROC AUC',
                'pr_auc': 'PR AUC'
            }

            # Collect fold values
            for metric_name in metric_order:
                if metric_name in results['summary']:
                    stats = results['summary'][metric_name]
                    if isinstance(stats, dict) and 'mean' in stats:
                        row = f"| {metric_display_names.get(metric_name, metric_name)} |"

                        # Add individual fold values (rounded to 3 digits)
                        fold_values = stats.get('values', [])
                        for i in range(n_folds):
                            if i < len(fold_values):
                                row += f" {fold_values[i]:.3f} |"
                            else:
                                row += " - |"

                        # Add mean ± std (rounded to 3 digits)
                        mean = stats.get('mean', 0)
                        std = stats.get('std', 0)
                        row += f" {mean:.3f} ± {std:.3f} |"
                        f.write(row + "\n")
            f.write("\n")
        
        # Visualizations section
        if include_plots and 'plots' in results:
            f.write("* Visualizations\n\n")
            
            # Confusion Matrices - all in one section
            f.write("** Confusion Matrices\n\n")
            f.write("#+BEGIN_EXPORT html\n")
            f.write("<div style='display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; max-width: 100%;'>\n")
            f.write("#+END_EXPORT\n\n")
            
            # CV Summary confusion matrix first
            cv_summary_plots = {k: v for k, v in results['plots'].items() if 'cv_summary' in k}
            cm_plots = [v for k, v in cv_summary_plots.items() if 'confusion_matrix' in k]
            
            if cm_plots:
                for plot_path in cm_plots:
                    rel_path = _make_relative_path(output_path.parent, 
                                                  Path(results.get('config', {}).get('output_dir', '.')) / plot_path)
                    f.write("#+BEGIN_EXPORT html\n")
                    f.write("<div style='text-align: center;'>\n")
                    f.write("#+END_EXPORT\n")
                    f.write("#+ATTR_ORG: :width 250\n")
                    f.write("#+ATTR_HTML: :width 100% :style max-width:250px\n")
                    f.write("#+CAPTION: Overall\n")
                    f.write(f"[[file:{rel_path}]]\n")
                    f.write("#+BEGIN_EXPORT html\n")
                    f.write("</div>\n")
                    f.write("#+END_EXPORT\n\n")
            
            # Individual fold confusion matrices
            for fold in range(n_folds):
                # Look for plots with exact fold matching
                fold_key = f'fold_{fold:02d}'
                fold_plots = {k: v for k, v in results['plots'].items() if fold_key in k}
                fold_cm = [v for k, v in fold_plots.items() if 'confusion_matrix' in k]
                
                if fold_cm and len(fold_cm) > 0:
                    # Take only the first matching confusion matrix for this fold
                    plot_path = fold_cm[0]
                    rel_path = _make_relative_path(output_path.parent,
                                                  Path(results.get('config', {}).get('output_dir', '.')) / plot_path)
                    f.write("#+BEGIN_EXPORT html\n")
                    f.write("<div style='text-align: center;'>\n")
                    f.write("#+END_EXPORT\n")
                    f.write("#+ATTR_ORG: :width 250\n")
                    f.write("#+ATTR_HTML: :width 100% :style max-width:250px\n") 
                    f.write(f"#+CAPTION: Fold {fold:02d}\n")
                    f.write(f"[[file:{rel_path}]]\n")
                    f.write("#+BEGIN_EXPORT html\n")
                    f.write("</div>\n")
                    f.write("#+END_EXPORT\n\n")
            
            f.write("#+BEGIN_EXPORT html\n")
            f.write("</div>\n")
            f.write("#+END_EXPORT\n\n")
            
            # ROC Curves - all in one section
            f.write("** ROC Curves\n\n")
            f.write("#+BEGIN_EXPORT html\n")
            f.write("<div style='display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; max-width: 100%;'>\n")
            f.write("#+END_EXPORT\n\n")
            
            # CV Summary ROC curve
            roc_plots = [v for k, v in cv_summary_plots.items() if 'roc_curve' in k]
            if roc_plots:
                for plot_path in roc_plots:
                    rel_path = _make_relative_path(output_path.parent,
                                                  Path(results.get('config', {}).get('output_dir', '.')) / plot_path)
                    f.write("#+BEGIN_EXPORT html\n")
                    f.write("<div style='text-align: center;'>\n")
                    f.write("#+END_EXPORT\n")
                    f.write("#+ATTR_ORG: :width 250\n")
                    f.write("#+ATTR_HTML: :width 100% :style max-width:250px\n")
                    f.write("#+CAPTION: Overall\n")
                    f.write(f"[[file:{rel_path}]]\n")
                    f.write("#+BEGIN_EXPORT html\n")
                    f.write("</div>\n")
                    f.write("#+END_EXPORT\n\n")
            
            # Individual fold ROC curves
            for fold in range(n_folds):
                # Look for plots with exact fold matching
                fold_key = f'fold_{fold:02d}'
                fold_plots = {k: v for k, v in results['plots'].items() if fold_key in k}
                fold_roc = [v for k, v in fold_plots.items() if 'roc_curve' in k]
                
                if fold_roc and len(fold_roc) > 0:
                    # Take only the first matching ROC curve for this fold
                    plot_path = fold_roc[0]
                    rel_path = _make_relative_path(output_path.parent,
                                                  Path(results.get('config', {}).get('output_dir', '.')) / plot_path)
                    f.write("#+BEGIN_EXPORT html\n")
                    f.write("<div style='text-align: center;'>\n")
                    f.write("#+END_EXPORT\n")
                    f.write("#+ATTR_ORG: :width 250\n")
                    f.write("#+ATTR_HTML: :width 100% :style max-width:250px\n")
                    f.write(f"#+CAPTION: Fold {fold:02d}\n")
                    f.write(f"[[file:{rel_path}]]\n")
                    f.write("#+BEGIN_EXPORT html\n")
                    f.write("</div>\n")
                    f.write("#+END_EXPORT\n\n")
                        
            f.write("#+BEGIN_EXPORT html\n")
            f.write("</div>\n")
            f.write("#+END_EXPORT\n\n")
            
            # PR Curves - all in one section  
            f.write("** Precision-Recall Curves\n\n")
            f.write("#+BEGIN_EXPORT html\n")
            f.write("<div style='display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; max-width: 100%;'>\n")
            f.write("#+END_EXPORT\n\n")
            
            # CV Summary PR curve
            pr_plots = [v for k, v in cv_summary_plots.items() if 'pr_curve' in k]
            if pr_plots:
                for plot_path in pr_plots:
                    rel_path = _make_relative_path(output_path.parent,
                                                  Path(results.get('config', {}).get('output_dir', '.')) / plot_path)
                    f.write("#+BEGIN_EXPORT html\n")
                    f.write("<div style='text-align: center;'>\n")
                    f.write("#+END_EXPORT\n")
                    f.write("#+ATTR_ORG: :width 250\n")
                    f.write("#+ATTR_HTML: :width 100% :style max-width:250px\n")
                    f.write("#+CAPTION: Overall\n")
                    f.write(f"[[file:{rel_path}]]\n")
                    f.write("#+BEGIN_EXPORT html\n")
                    f.write("</div>\n")
                    f.write("#+END_EXPORT\n\n")
            
            # Individual fold PR curves
            for fold in range(n_folds):
                # Look for plots with exact fold matching
                fold_key = f'fold_{fold:02d}'
                fold_plots = {k: v for k, v in results['plots'].items() if fold_key in k}
                fold_pr = [v for k, v in fold_plots.items() if 'pr_curve' in k]
                
                if fold_pr and len(fold_pr) > 0:
                    # Take only the first matching PR curve for this fold
                    plot_path = fold_pr[0]
                    rel_path = _make_relative_path(output_path.parent,
                                                  Path(results.get('config', {}).get('output_dir', '.')) / plot_path)
                    f.write("#+BEGIN_EXPORT html\n")
                    f.write("<div style='text-align: center;'>\n")
                    f.write("#+END_EXPORT\n")
                    f.write("#+ATTR_ORG: :width 250\n")
                    f.write("#+ATTR_HTML: :width 100% :style max-width:250px\n")
                    f.write(f"#+CAPTION: Fold {fold:02d}\n")
                    f.write(f"[[file:{rel_path}]]\n")
                    f.write("#+BEGIN_EXPORT html\n")
                    f.write("</div>\n")
                    f.write("#+END_EXPORT\n\n")
                        
            f.write("#+BEGIN_EXPORT html\n")
            f.write("</div>\n")
            f.write("#+END_EXPORT\n\n")
        
        # Experiment Configuration section at the end (less prominent)
        logger.info(f"config_data is: {config_data is not None}, type: {type(config_data)}")
        if config_data:
            logger.info(f"Writing CONFIG section with {len(config_data)} keys")
            f.write("* Experiment Configuration\n\n")
            f.write("| Parameter | Value |\n")
            f.write("|-----------|-------|\n")
            
            # Display configuration in a clean format
            for key, value in sorted(config_data.items()):
                # Format the key nicely
                display_key = key.replace('_', ' ').title()
                # Format value for org-mode table
                display_value = str(value)
                # Escape pipe characters in values for org table
                display_value = display_value.replace('|', '\\vert{}')
                # For paths, show just the relative part if too long
                if 'SDIR' in key.upper() and len(display_value) > 80:
                    # Try to show the end part which is more informative
                    if '/' in display_value:
                        parts = display_value.split('/')
                        # Keep last few parts
                        if len(parts) > 4:
                            display_value = '.../'+'/'.join(parts[-4:])
                # Wrap in verbatim for paths to avoid formatting issues
                if '/' in display_value or '_' in display_value:
                    display_value = f"~{display_value}~"
                f.write(f"| {display_key} | {display_value} |\n")
            f.write("\n")
        
        # Footer
        f.write("\n* Report Generation\n\n")
        f.write(f"- Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("- Generated by: SciTeX Classification Reporter\n")
        f.write("- Format: Org-mode\n")
    
    if verbose:
        from scitex.logging import getLogger
        logger = getLogger(__name__)
        logger.info(f"Generated org-mode report: {output_path}")
    
    # Optional pandoc conversions
    if convert_formats:
        import subprocess
        import shutil
        import os
        
        # Check for pandoc in regular PATH or module system
        pandoc_cmd = shutil.which('pandoc')
        if not pandoc_cmd:
            # Try module system path
            module_pandoc = '/apps/easybuild-2022/easybuild/software/Core/Pandoc/3.1.2/bin/pandoc'
            if os.path.exists(module_pandoc):
                pandoc_cmd = module_pandoc
        
        if pandoc_cmd:
            conversions = [
                # (output_filename, extra_args, description)
                (output_path.with_suffix('.md'), [], "markdown"),
                (output_path.with_suffix('.html'), ['--standalone', '--embed-resources'], "HTML"),
                (output_path.with_suffix('.tex'), [], "LaTeX"),
                (output_path.with_suffix('.docx'), ['--resource-path=' + str(output_path.parent.parent)], "DOCX"),
            ]
            
            for output_file, extra_args, format_name in conversions:
                try:
                    cmd = [pandoc_cmd, str(output_path), '-o', str(output_file)] + extra_args
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    if result.returncode == 0 and verbose:
                        logger.info(f"Generated {format_name} report: {output_file}")
                    elif verbose and result.returncode != 0:
                        logger.warning(f"{format_name} generation failed: {result.stderr}")
                except subprocess.TimeoutExpired:
                    if verbose:
                        logger.warning(f"{format_name} conversion timed out")
                except Exception as e:
                    if verbose:
                        logger.warning(f"{format_name} conversion failed: {e}")
            
            # Convert to PDF (requires LaTeX)
            if shutil.which('xelatex') or shutil.which('pdflatex'):
                try:
                    pdf_path = output_path.with_suffix('.pdf')
                    pdf_engine = 'xelatex' if shutil.which('xelatex') else 'pdflatex'
                    result = subprocess.run(
                        [pandoc_cmd, str(output_path), f'--pdf-engine={pdf_engine}', '-o', str(pdf_path)],
                        capture_output=True,
                        text=True,
                        timeout=60
                    )
                    if result.returncode == 0 and verbose:
                        logger.info(f"Generated PDF report: {pdf_path}")
                    elif verbose:
                        logger.warning(f"PDF generation failed: {result.stderr}")
                except subprocess.TimeoutExpired:
                    if verbose:
                        logger.warning("PDF conversion timed out")
                except Exception as e:
                    if verbose:
                        logger.warning(f"PDF conversion failed: {e}")
        elif verbose:
            logger.info("Pandoc not found. Skipping format conversions. Try 'module load Pandoc/3.1.2'")
    
    return output_path


def generate_markdown_report(
    results: Dict[str, Any],
    output_path: Union[str, Path],
    include_plots: bool = True,
    verbose: bool = True,
) -> Path:
    """
    Generate comprehensive markdown report.
    
    Parameters
    ----------
    results : Dict[str, Any]
        Classification results dictionary
    output_path : Union[str, Path]
        Output file path
    include_plots : bool, default True
        Whether to include plot images
    verbose : bool, default True
        Whether to print progress messages
    
    Returns
    -------
    Path
        Path to generated report
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        # Header
        f.write("# Classification Report\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Experiment Info
        config = results.get('config', {})
        f.write("## Experiment Information\n\n")
        f.write(f"- **Experiment Name:** {config.get('name', 'Unknown')}\n")
        f.write(f"- **Number of Folds:** {config.get('n_folds', 'N/A')}\n")
        f.write(f"- **Output Directory:** `{config.get('output_dir', 'N/A')}`\n\n")
        
        # Summary Statistics
        if 'summary' in results and results['summary']:
            f.write("## Summary Statistics\n\n")
            f.write("| Metric | Mean ± Std | Min | Max |\n")
            f.write("|--------|------------|-----|-----|\n")
            
            for metric_name, stats in results['summary'].items():
                if isinstance(stats, dict) and 'mean' in stats:
                    mean = stats.get('mean', 0)
                    std = stats.get('std', 0)
                    min_val = stats.get('min', 0)
                    max_val = stats.get('max', 0)
                    metric_display = metric_name.replace('_', ' ').title()
                    f.write(f"| {metric_display} | {mean:.3f} ± {std:.3f} | "
                           f"{min_val:.3f} | {max_val:.3f} |\n")
            f.write("\n")
        
        # CV Summary Results with Plots
        if include_plots and 'plots' in results:
            f.write("## CV Summary Results\n\n")
            
            # Find cv_summary plots
            cv_summary_plots = {k: v for k, v in results['plots'].items() 
                            if 'cv_summary' in k}
            
            if cv_summary_plots:
                # Confusion Matrix
                cm_plots = [v for k, v in cv_summary_plots.items() 
                           if 'confusion_matrix' in k]
                if cm_plots:
                    f.write("### CV Summary Confusion Matrix\n\n")
                    for plot_path in cm_plots:
                        rel_path = _make_relative_path(output_path.parent,
                                                      Path(results.get('config', {}).get('output_dir', '.')) / plot_path)
                        f.write(f"![Confusion Matrix]({rel_path})\n\n")
                
                # ROC Curve
                roc_plots = [v for k, v in cv_summary_plots.items() 
                            if 'roc_curve' in k]
                if roc_plots:
                    f.write("### CV Summary ROC Curve\n\n")
                    for plot_path in roc_plots:
                        rel_path = _make_relative_path(output_path.parent,
                                                      Path(results.get('config', {}).get('output_dir', '.')) / plot_path)
                        f.write(f"![ROC Curve]({rel_path})\n\n")
                
                # PR Curve
                pr_plots = [v for k, v in cv_summary_plots.items() 
                           if 'pr_curve' in k]
                if pr_plots:
                    f.write("### CV Summary Precision-Recall Curve\n\n")
                    for plot_path in pr_plots:
                        rel_path = _make_relative_path(output_path.parent,
                                                      Path(results.get('config', {}).get('output_dir', '.')) / plot_path)
                        f.write(f"![PR Curve]({rel_path})\n\n")
        
        # Per-Fold Results (abbreviated for brevity)
        if 'folds' in results and results['folds']:
            f.write("## Per-Fold Results\n\n")
            
            # Create summary table
            f.write("| Fold | Balanced Accuracy | ROC AUC | PR AUC | MCC |\n")
            f.write("|------|-------------------|---------|--------|-----|\n")
            
            for fold_data in results['folds']:
                fold_id = fold_data.get('fold_id', 0)
                
                # Extract metrics
                bacc = _extract_metric_value(fold_data.get('balanced_accuracy'))
                roc = _extract_metric_value(fold_data.get('roc_auc'))
                pr = _extract_metric_value(fold_data.get('pr_auc'))
                mcc = _extract_metric_value(fold_data.get('mcc'))
                
                f.write(f"| {fold_id:02d} | ")
                f.write(f"{bacc:.3f} | " if bacc is not None else "N/A | ")
                f.write(f"{roc:.3f} | " if roc is not None else "N/A | ")
                f.write(f"{pr:.3f} | " if pr is not None else "N/A | ")
                f.write(f"{mcc:.3f} |\n" if mcc is not None else "N/A |\n")
            
            f.write("\n")
    
    if verbose:
        from scitex.logging import getLogger
        logger = getLogger(__name__)
        logger.info(f"Generated markdown report: {output_path}")
    
    return output_path


def generate_latex_report(
    results: Dict[str, Any],
    output_path: Union[str, Path],
    verbose: bool = True,
) -> Path:
    """
    Generate LaTeX report for academic papers.
    
    Parameters
    ----------
    results : Dict[str, Any]
        Classification results dictionary
    output_path : Union[str, Path]
        Output file path
    verbose : bool, default True
        Whether to print progress messages
    
    Returns
    -------
    Path
        Path to generated report
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        # Document setup
        f.write("\\documentclass[11pt]{article}\n")
        f.write("\\usepackage{booktabs}\n")
        f.write("\\usepackage{graphicx}\n")
        f.write("\\usepackage{float}\n")
        f.write("\\usepackage{amsmath}\n")
        f.write("\\usepackage{hyperref}\n\n")
        
        f.write("\\title{Classification Report}\n")
        f.write(f"\\date{{\\today}}\n\n")
        
        f.write("\\begin{document}\n")
        f.write("\\maketitle\n\n")
        
        # Experiment Information
        config = results.get('config', {})
        f.write("\\section{Experiment Information}\n\n")
        f.write("\\begin{itemize}\n")
        f.write(f"\\item \\textbf{{Experiment Name:}} {_latex_escape(config.get('name', 'Unknown'))}\n")
        f.write(f"\\item \\textbf{{Number of Folds:}} {config.get('n_folds', 'N/A')}\n")
        f.write(f"\\item \\textbf{{Output Directory:}} \\texttt{{{_latex_escape(str(config.get('output_dir', 'N/A')))}}}\n")
        f.write("\\end{itemize}\n\n")
        
        # Summary Statistics
        if 'summary' in results and results['summary']:
            f.write("\\section{Summary Statistics}\n\n")
            f.write("\\begin{table}[H]\n")
            f.write("\\centering\n")
            f.write("\\begin{tabular}{lccc}\n")
            f.write("\\toprule\n")
            f.write("Metric & Mean $\\pm$ Std & Min & Max \\\\\n")
            f.write("\\midrule\n")
            
            for metric_name, stats in results['summary'].items():
                if isinstance(stats, dict) and 'mean' in stats:
                    mean = stats.get('mean', 0)
                    std = stats.get('std', 0)
                    min_val = stats.get('min', 0)
                    max_val = stats.get('max', 0)
                    metric_display = metric_name.replace('_', ' ').title()
                    f.write(f"{_latex_escape(metric_display)} & "
                           f"${mean:.3f} \\pm {std:.3f}$ & "
                           f"{min_val:.3f} & {max_val:.3f} \\\\\n")
            
            f.write("\\bottomrule\n")
            f.write("\\end{tabular}\n")
            f.write("\\caption{Cross-validation performance metrics}\n")
            f.write("\\label{tab:cv_metrics}\n")
            f.write("\\end{table}\n\n")
        
        # Plots (if available)
        if 'plots' in results:
            f.write("\\section{Visualizations}\n\n")
            
            # CV Summary plots
            cv_summary_plots = {k: v for k, v in results['plots'].items() 
                            if 'cv_summary' in k}
            
            if cv_summary_plots:
                # Find specific plot types
                for plot_type, title in [
                    ('confusion_matrix', 'CV Summary Confusion Matrix'),
                    ('roc_curve', 'CV Summary ROC Curve'),
                    ('pr_curve', 'CV Summary Precision-Recall Curve')
                ]:
                    type_plots = [v for k, v in cv_summary_plots.items() 
                                 if plot_type in k]
                    if type_plots:
                        f.write(f"\\subsection{{{title}}}\n\n")
                        for plot_path in type_plots:
                            rel_path = _make_relative_path(output_path.parent,
                                                          Path(results.get('config', {}).get('output_dir', '.')) / plot_path)
                            f.write("\\begin{figure}[H]\n")
                            f.write("\\centering\n")
                            f.write(f"\\includegraphics[width=0.8\\textwidth]{{{rel_path}}}\n")
                            f.write(f"\\caption{{{title}}}\n")
                            f.write(f"\\label{{fig:{plot_type}_cv_summary}}\n")
                            f.write("\\end{figure}\n\n")
        
        f.write("\\end{document}\n")
    
    if verbose:
        from scitex.logging import getLogger
        logger = getLogger(__name__)
        logger.info(f"Generated LaTeX report: {output_path}")
    
    return output_path


def create_summary_statistics(results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create comprehensive summary statistics from results.
    
    Parameters
    ----------
    results : Dict[str, Any]
        Classification results
    
    Returns
    -------
    Dict[str, Any]
        Summary statistics
    """
    summary = {}
    
    if 'folds' in results:
        # Aggregate metrics across folds
        metrics_to_aggregate = [
            'balanced_accuracy', 'roc_auc', 'pr_auc', 'mcc',
            'precision', 'recall', 'f1_score'
        ]
        
        for metric_name in metrics_to_aggregate:
            values = []
            for fold_data in results['folds']:
                if metric_name in fold_data:
                    value = _extract_metric_value(fold_data[metric_name])
                    if value is not None:
                        values.append(value)
            
            if values:
                values = np.array(values)
                summary[metric_name] = {
                    'mean': float(np.mean(values)),
                    'std': float(np.std(values)),
                    'min': float(np.min(values)),
                    'max': float(np.max(values)),
                    'median': float(np.median(values)),
                    'values': values.tolist()
                }
    
    return summary


def export_for_paper(
    results: Dict[str, Any],
    output_dir: Union[str, Path],
    verbose: bool = True,
) -> Dict[str, Path]:
    """
    Export results in formats suitable for academic papers.
    
    Parameters
    ----------
    results : Dict[str, Any]
        Classification results
    output_dir : Union[str, Path]
        Output directory for exports
    verbose : bool, default True
        Whether to print progress messages
    
    Returns
    -------
    Dict[str, Path]
        Paths to exported files
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    exported_files = {}
    
    # Export summary metrics as LaTeX table
    if 'summary' in results:
        latex_table_path = output_dir / "metrics_table.tex"
        _export_metrics_table_latex(results['summary'], latex_table_path)
        exported_files['metrics_table'] = latex_table_path
        
        # Also export as CSV for easier processing
        csv_table_path = output_dir / "summary_table.csv"
        _export_summary_table_csv(results['summary'], csv_table_path)
        exported_files['summary_table'] = csv_table_path
        
    # Export raw results as JSON
    import json
    raw_results_path = output_dir / "raw_results.json"
    with open(raw_results_path, 'w') as f:
        # Create serializable version of results
        serializable_results = _make_serializable(results)
        json.dump(serializable_results, f, indent=2)
    exported_files['raw_results'] = raw_results_path
    
    # Export confusion matrix as CSV
    if 'overall_confusion_matrix' in results:
        cm_path = output_dir / "confusion_matrix.csv"
        cm_data = np.array(results['overall_confusion_matrix'])
        cm_df = pd.DataFrame(cm_data)
        cm_df.to_csv(cm_path, index=True)
        exported_files['confusion_matrix'] = cm_path
    
    # Copy key plots
    config = results.get('config', {})
    base_dir = Path(results.get('config', {}).get('output_dir', '.'))
    
    if 'plots' in results:
        plots_dir = output_dir / "figures"
        plots_dir.mkdir(exist_ok=True)
        
        # Copy cv_summary plots with standardized names
        cv_summary_plots = {k: v for k, v in results['plots'].items() 
                        if 'cv_summary' in k}
        
        for plot_key, plot_path in cv_summary_plots.items():
            src_path = base_dir / plot_path
            if src_path.exists():
                # Standardize filename
                if 'confusion_matrix' in plot_key:
                    dest_name = "confusion_matrix_cv_summary.jpg"
                elif 'roc_curve' in plot_key:
                    dest_name = "roc_curve_cv_summary.jpg"
                elif 'pr_curve' in plot_key:
                    dest_name = "pr_curve_cv_summary.jpg"
                else:
                    dest_name = src_path.name
                
                dest_path = plots_dir / dest_name
                import shutil
                shutil.copy2(src_path, dest_path)
                exported_files[f"figure_{dest_name.split('.')[0]}"] = dest_path
    
    if verbose:
        from scitex.logging import getLogger
        logger = getLogger(__name__)
        logger.info(f"Exported {len(exported_files)} files for paper to {output_dir}")
    
    return exported_files


# Helper functions

def _extract_metric_value(metric_data: Any) -> Optional[float]:
    """Extract numeric value from metric data."""
    if metric_data is None:
        return None
    if isinstance(metric_data, dict) and 'value' in metric_data:
        return float(metric_data['value'])
    if isinstance(metric_data, (int, float, np.number)):
        return float(metric_data)
    return None


def _make_relative_path(from_dir: Path, to_path: Path) -> str:
    """Create relative path from one directory to another."""
    try:
        # Try to make relative path
        rel_path = Path(to_path).relative_to(from_dir)
        return str(rel_path)
    except ValueError:
        # If not possible, try going up directories
        try:
            # Count how many directories to go up
            common_parts = 0
            from_parts = from_dir.parts
            to_parts = Path(to_path).parts
            
            for fp, tp in zip(from_parts, to_parts):
                if fp == tp:
                    common_parts += 1
                else:
                    break
            
            # Build relative path
            ups = len(from_parts) - common_parts
            rel_parts = ['..'] * ups + list(to_parts[common_parts:])
            return '/'.join(rel_parts)
        except:
            # Fallback to absolute path
            return str(to_path)


def _latex_escape(text: str) -> str:
    """Escape special LaTeX characters."""
    if not isinstance(text, str):
        text = str(text)
    
    replacements = {
        '\\': '\\textbackslash{}',
        '{': '\\{',
        '}': '\\}',
        '$': '\\$',
        '&': '\\&',
        '%': '\\%',
        '#': '\\#',
        '_': '\\_',
        '~': '\\textasciitilde{}',
        '^': '\\textasciicircum{}'
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    return text


def _export_metrics_table_latex(
    summary: Dict[str, Any],
    output_path: Path
) -> None:
    """Export summary metrics as a LaTeX table."""
    with open(output_path, 'w') as f:
        f.write("% Classification metrics summary table\n")
        f.write("\\begin{table}[htbp]\n")
        f.write("\\centering\n")
        f.write("\\begin{tabular}{lccc}\n")
        f.write("\\toprule\n")
        f.write("Metric & Mean $\\pm$ Std & Min & Max \\\\\n")
        f.write("\\midrule\n")
        
        for metric_name, stats in summary.items():
            if isinstance(stats, dict) and 'mean' in stats:
                mean = stats.get('mean', 0)
                std = stats.get('std', 0)
                min_val = stats.get('min', 0)
                max_val = stats.get('max', 0)
                metric_display = metric_name.replace('_', ' ').title()
                f.write(f"{_latex_escape(metric_display)} & "
                       f"${mean:.3f} \\pm {std:.3f}$ & "
                       f"{min_val:.3f} & {max_val:.3f} \\\\\n")
        
        f.write("\\bottomrule\n")
        f.write("\\end{tabular}\n")
        f.write("\\caption{Classification performance metrics}\n")
        f.write("\\label{tab:metrics}\n")
        f.write("\\end{table}\n")


def _export_summary_table_csv(
    summary: Dict[str, Any],
    output_path: Path
) -> None:
    """Export summary metrics as CSV table."""
    # Create DataFrame from summary
    data = []
    for metric_name, stats in summary.items():
        if isinstance(stats, dict) and 'mean' in stats:
            row = {
                'Metric': metric_name.replace('_', ' ').title(),
                'Mean': stats.get('mean', 0),
                'Std': stats.get('std', 0),
                'Min': stats.get('min', 0),
                'Max': stats.get('max', 0)
            }
            data.append(row)
    
    if data:
        df = pd.DataFrame(data)
        df.to_csv(output_path, index=False)


def _make_serializable(obj: Any) -> Any:
    """Convert numpy arrays and other non-serializable objects to serializable format."""
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (np.integer, np.floating)):
        return float(obj)
    elif isinstance(obj, pd.DataFrame):
        # Convert DataFrame to dict with orient='list' for JSON serialization
        return obj.to_dict(orient='list')
    elif isinstance(obj, pd.Series):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {k: _make_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_make_serializable(item) for item in obj]
    elif isinstance(obj, Path):
        return str(obj)
    else:
        return obj

# EOF