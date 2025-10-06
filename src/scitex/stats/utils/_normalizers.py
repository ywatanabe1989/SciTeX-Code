#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-01 20:28:19 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/stats/utils/_normalizers.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Output format normalization utilities for scitex.stats.

Provides functions to convert between dict and DataFrame formats,
ensuring consistent output structure across all statistical tests.
"""

from typing import Any, Dict, List, Literal, Optional, Union

import numpy as np
import pandas as pd

# Standard columns for statistical test outputs
STANDARD_COLUMNS = [
    "test_method",
    "statistic_name",
    "statistic",
    "alternative",
    "n_samples",
    "n_x",
    "n_y",
    "n_pairs",
    "var_x",
    "var_y",
    "pvalue",
    "pvalue_adjusted",
    "pstars",
    "alpha",
    "alpha_adjusted",
    "rejected",
    "effect_size",
    "effect_size_metric",
    "effect_size_interpretation",
    "effect_size_secondary",
    "effect_size_secondary_metric",
    "effect_size_secondary_interpretation",
    "power",
    "H0",
]

# Default values for standard columns
STANDARD_DEFAULTS = {
    "alternative": "two-sided",
    "pstars": "ns",
    "rejected": False,
    "alpha": 0.05,
    "alpha_adjusted": np.nan,
    "pvalue_adjusted": np.nan,
    "power": np.nan,
    "n_samples": np.nan,
    "n_x": np.nan,
    "n_y": np.nan,
    "n_pairs": np.nan,
    "var_x": "",
    "var_y": "",
}

# Column types
COLUMN_TYPES = {
    "test_method": str,
    "statistic_name": str,
    "statistic": float,
    "alternative": str,
    "n_samples": "Int64",  # Nullable integer
    "n_x": "Int64",
    "n_y": "Int64",
    "n_pairs": "Int64",
    "var_x": str,
    "var_y": str,
    "pvalue": float,
    "pvalue_adjusted": float,
    "pstars": str,
    "alpha": float,
    "alpha_adjusted": float,
    "rejected": bool,
    "effect_size": float,
    "effect_size_metric": str,
    "effect_size_interpretation": str,
    "effect_size_secondary": float,
    "effect_size_secondary_metric": str,
    "effect_size_secondary_interpretation": str,
    "power": float,
    "H0": str,
}


def normalize_result(
    result: Dict[str, Any], fill_missing: bool = True
) -> Dict[str, Any]:
    """
    Normalize a test result dictionary to standard format.

    Parameters
    ----------
    result : dict
        Result dictionary from a statistical test
    fill_missing : bool, default True
        Whether to fill missing standard columns with defaults

    Returns
    -------
    dict
        Normalized result dictionary

    Examples
    --------
    >>> result = {'pvalue': 0.023, 'statistic': 2.45}
    >>> normalized = normalize_result(result)
    >>> 'pstars' in normalized
    True
    """
    normalized = result.copy()

    if fill_missing:
        for col, default in STANDARD_DEFAULTS.items():
            if col not in normalized:
                normalized[col] = default

    # Use adjusted pvalue if available, otherwise use raw pvalue
    pvalue_for_decision = normalized.get(
        "pvalue_adjusted", normalized.get("pvalue")
    )
    alpha_for_decision = normalized.get(
        "alpha_adjusted", normalized.get("alpha", 0.05)
    )

    # Compute pstars based on adjusted pvalue if available
    if "pstars" not in normalized and pvalue_for_decision is not None:
        from ._formatters import p2stars

        normalized["pstars"] = p2stars(pvalue_for_decision)

    # Compute rejected based on adjusted criteria if available
    if "rejected" not in normalized and pvalue_for_decision is not None:
        normalized["rejected"] = pvalue_for_decision < alpha_for_decision

    return normalized


def to_dataframe(
    results: Union[Dict[str, Any], List[Dict[str, Any]]],
    normalize: bool = True,
) -> pd.DataFrame:
    """
    Convert test result(s) to DataFrame.

    Parameters
    ----------
    results : dict or list of dict
        Single result dict or list of result dicts
    normalize : bool, default True
        Whether to normalize results before conversion

    Returns
    -------
    pd.DataFrame
        DataFrame with one row per result

    Examples
    --------
    >>> result = {'var_x': 'A', 'var_y': 'B', 'pvalue': 0.01}
    >>> df = to_dataframe(result)
    >>> df.shape
    (1, ...)

    >>> results = [result1, result2, result3]
    >>> df = to_dataframe(results)
    >>> len(df)
    3
    """
    # Handle single dict
    if isinstance(results, dict):
        results = [results]

    # Normalize if requested
    if normalize:
        results = [normalize_result(r) for r in results]

    # Convert to DataFrame
    df = pd.DataFrame(results)

    return df


def force_dataframe(
    results: Union[Dict[str, Any], List[Dict[str, Any]], pd.DataFrame],
    columns: Optional[List[str]] = None,
    fill_na: bool = True,
    defaults: Optional[Dict[str, Any]] = None,
    enforce_types: bool = True,
) -> pd.DataFrame:
    """
    Ensure DataFrame output with consistent columns and types.

    This is the main function for normalizing statistical test outputs
    to a standard DataFrame format.

    Parameters
    ----------
    results : dict, list of dict, or DataFrame
        Test result(s) to normalize
    columns : list of str, optional
        Columns to include. If None, uses all columns in results.
        If specified, ensures these columns exist (adds with NaN if missing).
    fill_na : bool, default True
        Whether to fill NaN values with defaults
    defaults : dict, optional
        Custom default values. Merged with STANDARD_DEFAULTS.
    enforce_types : bool, default True
        Whether to enforce correct dtypes for standard columns

    Returns
    -------
    pd.DataFrame
        Normalized DataFrame with consistent format

    Examples
    --------
    >>> # Basic usage
    >>> results = [
    ...     {'var_x': 'A', 'pvalue': 0.01},
    ...     {'var_x': 'B', 'pvalue': 0.05, 'effect_size': 0.5},
    ... ]
    >>> df = force_dataframe(results)
    >>> 'effect_size' in df.columns
    True
    >>> df['effect_size'].isna().sum()
    1

    >>> # Specify required columns
    >>> df = force_dataframe(
    ...     results,
    ...     columns=['var_x', 'pvalue', 'pstars', 'rejected']
    ... )
    >>> set(df.columns) >= {'var_x', 'pvalue', 'pstars', 'rejected'}
    True

    >>> # Custom defaults
    >>> df = force_dataframe(
    ...     results,
    ...     defaults={'effect_size': 0.0, 'pstars': 'ns'}
    ... )
    """
    # Convert to DataFrame if needed
    if not isinstance(results, pd.DataFrame):
        df = to_dataframe(results, normalize=True)
    else:
        df = results.copy()

    # Merge custom defaults with standard defaults
    all_defaults = STANDARD_DEFAULTS.copy()
    if defaults:
        all_defaults.update(defaults)

    # Ensure specified columns exist
    if columns:
        for col in columns:
            if col not in df.columns:
                default_val = all_defaults.get(col, np.nan)
                df[col] = default_val

    # Fill NaN values with defaults
    if fill_na:
        for col, default_val in all_defaults.items():
            if col in df.columns:
                df[col] = df[col].fillna(default_val)

    # Enforce types for standard columns
    if enforce_types:
        for col, dtype in COLUMN_TYPES.items():
            if col in df.columns:
                try:
                    df[col] = df[col].astype(dtype)
                except (ValueError, TypeError):
                    # Skip if conversion fails
                    pass

    return df


def to_dict(df: pd.DataFrame, row: int = 0) -> Dict[str, Any]:
    """
    Convert DataFrame row to dictionary.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing test results
    row : int, default 0
        Row index to convert

    Returns
    -------
    dict
        Dictionary representation of the row

    Examples
    --------
    >>> df = pd.DataFrame({'pvalue': [0.01, 0.05], 'var_x': ['A', 'B']})
    >>> result = to_dict(df, row=1)
    >>> result['var_x']
    'B'
    """
    return df.iloc[row].to_dict()


def combine_results(
    results_list: List[Union[Dict, pd.DataFrame]], **kwargs
) -> pd.DataFrame:
    """
    Combine multiple test results into a single DataFrame.

    Parameters
    ----------
    results_list : list
        List of result dicts or DataFrames
    **kwargs : dict
        Additional arguments passed to force_dataframe

    Returns
    -------
    pd.DataFrame
        Combined DataFrame with all results

    Examples
    --------
    >>> r1 = test_ttest_ind(x1, y1, var_x='Control', var_y='Treatment')
    >>> r2 = test_ttest_ind(x2, y2, var_x='Placebo', var_y='Drug')
    >>> df = combine_results([r1, r2])
    >>> len(df)
    2
    """
    # Convert all to DataFrames
    dfs = []
    for result in results_list:
        if isinstance(result, dict):
            df = to_dataframe(result)
        elif isinstance(result, pd.DataFrame):
            df = result
        else:
            raise TypeError(f"Expected dict or DataFrame, got {type(result)}")
        dfs.append(df)

    # Concatenate
    combined = pd.concat(dfs, ignore_index=True)

    # Normalize
    return force_dataframe(combined, **kwargs)


def export_results(
    results: Union[Dict[str, Any], List[Dict[str, Any]], pd.DataFrame],
    path: str,
    format: Optional[str] = None,
    **kwargs,
) -> str:
    """
    Export test results to various formats.

    Parameters
    ----------
    results : dict, list of dict, or DataFrame
        Test results to export
    path : str
        Output file path
    format : str, optional
        Output format: 'csv', 'txt', 'json', 'xlsx', 'latex'
        If None, inferred from path extension
    **kwargs : dict
        Additional arguments passed to export function

    Returns
    -------
    str
        Path to exported file

    Examples
    --------
    >>> result = test_ttest_ind(x, y)
    >>> export_results(result, 'results.csv')
    'results.csv'

    >>> # Multiple results
    >>> results = [result1, result2, result3]
    >>> export_results(results, 'results.xlsx')
    'results.xlsx'

    >>> # LaTeX table
    >>> export_results(results, 'results.tex', format='latex')
    'results.tex'
    """
    import os

    # Infer format from extension if not provided
    if format is None:
        _, ext = os.path.splitext(path)
        format = ext.lstrip(".").lower()

    # Convert to DataFrame
    if not isinstance(results, pd.DataFrame):
        df = force_dataframe(results)
    else:
        df = results

    # Export based on format
    if format == "csv":
        df.to_csv(path, index=False, **kwargs)
        # Add signature as comment
        with open(path, "a") as f:
            f.write(f"\n# {_get_scitex_signature('excel')}\n")
    elif format in ["txt", "tsv"]:
        df.to_csv(path, index=False, sep="\t", **kwargs)
        # Add signature
        with open(path, "a") as f:
            f.write(f"\n{_get_scitex_signature('text')}")
    elif format == "json":
        # Export JSON with metadata
        import json

        data = {
            "data": df.to_dict("records"),
            "metadata": {
                "generated_by": "SciTeX Stats",
                "timestamp": _get_scitex_signature("excel").split(" | ")[1],
                "description": "Professional Statistical Analysis Framework for Scientific Computing",
            },
        }
        with open(path, "w") as f:
            json.dump(data, f, indent=2, **kwargs)
    elif format == "xlsx":
        df.to_excel(path, index=False, **kwargs)
    elif format in ["latex", "tex"]:
        latex_str = df.to_latex(index=False, **kwargs)
        # Add signature as LaTeX comment
        latex_str += f"\n% {_get_scitex_signature('excel')}\n"
        with open(path, "w") as f:
            f.write(latex_str)
    else:
        raise ValueError(
            f"Unsupported format: {format}. "
            f"Use 'csv', 'txt', 'json', 'xlsx', or 'latex'"
        )

    return path


def export_excel_styled(
    results: Union[Dict[str, Any], List[Dict[str, Any]], pd.DataFrame],
    path: str,
    **kwargs,
) -> str:
    """ """
    pass


def export_report(
    results: Union[Dict[str, Any], List[Dict[str, Any]], pd.DataFrame],
    path: str,
    title: str = "Statistical Analysis Report",
    include_summary: bool = True,
    **kwargs,
) -> str:
    """
    Export formatted report with colored highlights.

    Parameters
    ----------
    results : dict, list of dict, or DataFrame
        Test results to export
    path : str
        Output file path (supports .html, .md, .txt)
    title : str, default "Statistical Analysis Report"
        Report title
    include_summary : bool, default True
        Whether to include summary statistics
    **kwargs : dict
        Additional arguments

    Returns
    -------
    str
        Path to exported file

    Notes
    -----
    Report includes:
    - Summary statistics (counts of significant results)
    - Full results table with color-coded significance
    - Automatic detection of output format from extension

    Examples
    --------
    >>> results = [result1, result2, result3]
    >>> export_report(results, 'report.html', title='My Analysis')
    'report.html'

    >>> export_report(results, 'report.md')  # Markdown format
    'report.md'
    """
    import os

    # Convert to DataFrame
    if not isinstance(results, pd.DataFrame):
        df = force_dataframe(results)
    else:
        df = results

    # Detect format
    _, ext = os.path.splitext(path)
    format_type = ext.lstrip(".").lower()

    # Generate report based on format
    if format_type == "html":
        return _export_report_html(df, path, title, include_summary)
    elif format_type == "md":
        return _export_report_markdown(df, path, title, include_summary)
    else:  # txt or other
        return _export_report_text(df, path, title, include_summary)


def _get_scitex_signature(format_type="html"):
    """Generate SciTeX Stats signature for branding."""
    import datetime

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if format_type == "html":
        return f"""
        <div style="margin-top: 30px; padding-top: 20px; border-top: 2px solid #ddd; text-align: center; color: #666; font-size: 12px;">
            <p>Generated by <strong style="color: #4CAF50;">SciTeX Stats</strong> | {timestamp}</p>
            <p style="font-size: 10px;">Professional Statistical Analysis Framework for Scientific Computing</p>
        </div>
        """
    elif format_type == "markdown":
        return f"\n\n---\n\n*Generated by **SciTeX Stats** | {timestamp}*\n\n*Professional Statistical Analysis Framework for Scientific Computing*\n"
    elif format_type == "text":
        return f"\n\n{'='*80}\nGenerated by SciTeX Stats | {timestamp}\nProfessional Statistical Analysis Framework for Scientific Computing\n{'='*80}\n"
    else:
        return f"Generated by SciTeX Stats | {timestamp}"


def _export_report_html(df, path, title, include_summary):
    """Generate HTML report with styling."""
    # Generate summary
    summary_html = ""
    if include_summary and "pvalue" in df.columns:
        n_total = len(df)
        n_sig_001 = (df["pvalue"] < 0.001).sum()
        n_sig_01 = ((df["pvalue"] >= 0.001) & (df["pvalue"] < 0.01)).sum()
        n_sig_05 = ((df["pvalue"] >= 0.01) & (df["pvalue"] < 0.05)).sum()
        n_ns = (df["pvalue"] >= 0.05).sum()

        summary_html = f"""
        <div class="summary">
            <h2>Summary</h2>
            <ul>
                <li>Total tests: {n_total}</li>
                <li style="color: #FF6B6B; font-weight: bold;">p < 0.001 (***): {n_sig_001}</li>
                <li style="color: #FFA500; font-weight: bold;">p < 0.01 (**): {n_sig_01}</li>
                <li style="color: #FFE66D; font-weight: bold;">p < 0.05 (*): {n_sig_05}</li>
                <li style="color: #999;">p >= 0.05 (ns): {n_ns}</li>
            </ul>
        </div>
        """

    # Style function for DataFrame
    def style_pvalue(val):
        if pd.isna(val):
            return ""
        if val < 0.001:
            return (
                "background-color: #FF6B6B; font-weight: bold; color: white;"
            )
        elif val < 0.01:
            return (
                "background-color: #FFA500; font-weight: bold; color: white;"
            )
        elif val < 0.05:
            return "background-color: #FFE66D; font-weight: bold;"
        else:
            return "background-color: #E8E8E8;"

    # Apply styling
    if "pvalue" in df.columns:
        styled = df.style.applymap(style_pvalue, subset=["pvalue"])
    else:
        styled = df.style

    # Generate HTML
    table_html = styled.to_html()

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{title}</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 20px;
                background-color: #f5f5f5;
            }}
            h1 {{
                color: #333;
                border-bottom: 3px solid #4CAF50;
                padding-bottom: 10px;
            }}
            .summary {{
                background-color: white;
                padding: 15px;
                border-radius: 5px;
                margin-bottom: 20px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            table {{
                border-collapse: collapse;
                width: 100%;
                background-color: white;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            th {{
                background-color: #4CAF50;
                color: white;
                padding: 12px;
                text-align: left;
            }}
            td {{
                padding: 10px;
                border-bottom: 1px solid #ddd;
            }}
            tr:hover {{
                background-color: #f5f5f5;
            }}
        </style>
    </head>
    <body>
        <h1>{title}</h1>
        {summary_html}
        <h2>Results</h2>
        {table_html}
        {_get_scitex_signature('html')}
    </body>
    </html>
    """

    with open(path, "w") as f:
        f.write(html_content)

    return path


def _export_report_markdown(df, path, title, include_summary):
    """Generate Markdown report."""
    lines = [f"# {title}\n"]

    # Summary
    if include_summary and "pvalue" in df.columns:
        n_total = len(df)
        n_sig = (df["pvalue"] < 0.05).sum()
        n_ns = (df["pvalue"] >= 0.05).sum()

        lines.append("## Summary\n")
        lines.append(f"- Total tests: {n_total}")
        lines.append(f"- Significant (p < 0.05): {n_sig}")
        lines.append(f"- Non-significant (p >= 0.05): {n_ns}\n")

    # Table
    lines.append("## Results\n")
    lines.append(df.to_markdown(index=False))

    # Add signature
    lines.append(_get_scitex_signature("markdown"))

    with open(path, "w") as f:
        f.write("\n".join(lines))

    return path


def _export_report_text(df, path, title, include_summary):
    """Generate plain text report."""
    lines = [title, "=" * len(title), ""]

    # Summary
    if include_summary and "pvalue" in df.columns:
        n_total = len(df)
        n_sig = (df["pvalue"] < 0.05).sum()

        lines.append("SUMMARY")
        lines.append(f"Total tests: {n_total}")
        lines.append(f"Significant: {n_sig}")
        lines.append("")

    # Table
    lines.append("RESULTS")
    lines.append(df.to_string(index=False))

    # Add signature
    lines.append(_get_scitex_signature("text"))

    with open(path, "w") as f:
        f.write("\n".join(lines))

    return path


def export_summary(
    results: Union[Dict[str, Any], List[Dict[str, Any]], pd.DataFrame],
    path: str,
    columns: Optional[List[str]] = None,
    format: Optional[str] = None,
    **kwargs,
) -> str:
    """
    Export summary of test results (selected columns only).

    Parameters
    ----------
    results : dict, list of dict, or DataFrame
        Test results to export
    path : str
        Output file path
    columns : list of str, optional
        Columns to include. Default: key columns for reporting
    format : str, optional
        Output format (inferred from extension if None)
    **kwargs : dict
        Additional arguments passed to export function

    Returns
    -------
    str
        Path to exported file

    Examples
    --------
    >>> # Export only key columns
    >>> export_summary(results, 'summary.csv')
    'summary.csv'

    >>> # Custom columns
    >>> export_summary(
    ...     results,
    ...     'summary.xlsx',
    ...     columns=['var_x', 'var_y', 'pvalue', 'effect_size']
    ... )
    'summary.xlsx'
    """
    # Default summary columns
    if columns is None:
        columns = [
            "test_method",
            "var_x",
            "var_y",
            "n_x",
            "n_y",
            "statistic",
            "pvalue",
            "pstars",
            "rejected",
            "effect_size",
            "effect_size_metric",
            "effect_size_interpretation",
        ]

    # Convert to DataFrame
    if not isinstance(results, pd.DataFrame):
        df = force_dataframe(results)
    else:
        df = results

    # Select columns (only those that exist)
    available_cols = [col for col in columns if col in df.columns]
    df_summary = df[available_cols]

    # Export
    return export_results(df_summary, path, format=format, **kwargs)


def convert_results(
    results: Union[Dict[str, Any], List[Dict[str, Any]], pd.DataFrame],
    return_as: Literal[
        "dict",
        "dataframe",
        "markdown",
        "json",
        "latex",
        "html",
        "text",
    ] = "dict",
    **kwargs,
) -> Union[dict, List[dict], pd.DataFrame, str]:
    """
    Convert statistical test results to specified format.

    This is a pure format converter - does NOT save files.
    For saving, use scitex.io.save() after conversion.

    Parameters
    ----------
    results : dict, list of dict, or DataFrame
        Test results to convert
    return_as : str, default 'dict'
        Output format:
        - 'dict': Python dictionary (single result) or list of dicts (multiple)
        - 'dataframe': pandas DataFrame
        - 'markdown': Markdown table string
        - 'json': JSON string
        - 'latex': LaTeX table string
        - 'html': HTML table string
        - 'text': Plain text table string
    **kwargs : dict
        Additional arguments passed to format functions

    Returns
    -------
    output : dict, list, DataFrame, or str
        Converted results in requested format

    Notes
    -----
    This function only handles format conversion. To save results to files,
    convert to DataFrame first, then use scitex.io.save():

    >>> df = convert_results(results, return_as='dataframe')
    >>> stx.io.save(df, 'results.xlsx')

    Examples
    --------
    >>> result = {'pvalue': 0.01, 'var_x': 'A', 'var_y': 'B'}

    # Convert to different formats
    >>> convert_results(result, return_as='dict')
    {'pvalue': 0.01, 'var_x': 'A', 'var_y': 'B'}

    >>> df = convert_results(result, return_as='dataframe')
    # Returns DataFrame

    >>> convert_results(result, return_as='markdown')
    '| var_x | var_y | pvalue |\\n|-------|-------|--------|...'

    >>> latex_str = convert_results(result, return_as='latex')

    # To save to file, use stx.io.save
    >>> import scitex as stx
    >>> df = convert_results(result, return_as='dataframe')
    >>> stx.io.save(df, 'results.xlsx')  # Uses stx.io.save for file operations
    """
    # Handle each format - pure conversion, no file I/O
    if return_as == "dict":
        if isinstance(results, dict):
            return results
        elif isinstance(results, list):
            return results
        elif isinstance(results, pd.DataFrame):
            return (
                results.to_dict("records")
                if len(results) > 1
                else to_dict(results, row=0)
            )

    elif return_as == "dataframe":
        return force_dataframe(results)

    elif return_as == "markdown":
        df_out = force_dataframe(results)
        return df_out.to_markdown(index=False, **kwargs)

    elif return_as == "json":
        df_out = force_dataframe(results)
        return df_out.to_json(orient="records", indent=2, **kwargs)

    elif return_as == "latex":
        df_out = force_dataframe(results)
        return df_out.to_latex(index=False, **kwargs)

    elif return_as == "html":
        df_out = force_dataframe(results)
        return df_out.to_html(index=False, **kwargs)

    elif return_as == "text":
        df_out = force_dataframe(results)
        return df_out.to_string(index=False, **kwargs)

    elif return_as == "csv":
        df_out = force_dataframe(results)
        return df_out.to_csv(index=False, **kwargs)

    else:
        raise ValueError(
            f"Unknown return_as format: {return_as}. "
            f"Use 'dict', 'dataframe', 'markdown', 'json', 'latex', 'html', or 'text'"
        )


# Convenience alias
as_dataframe = force_dataframe

__all__ = [
    "normalize_result",
    "to_dataframe",
    "force_dataframe",
    "to_dict",
    "combine_results",
    "convert_results",
    "export_results",
    "export_summary",
    "export_excel_styled",
    "export_report",
    "as_dataframe",
    "STANDARD_COLUMNS",
    "STANDARD_DEFAULTS",
    "COLUMN_TYPES",
]

# EOF
