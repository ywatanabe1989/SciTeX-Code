#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-01 21:30:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/io/_save_modules/_tex.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/io/_save_modules/_tex.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Save objects as LaTeX/TeX format.

Supports multiple input types:
- pandas DataFrames → LaTeX tables via df.to_latex()
- dicts/lists → LaTeX tables via convert_results()
- str → Direct write (pre-formatted TeX)
- matplotlib figures → TikZ/PGFPlots (future enhancement)
"""

from typing import Union, Optional, Any
import warnings


def save_tex(
    obj: Any,
    spath: str,
    caption: Optional[str] = None,
    label: Optional[str] = None,
    document: bool = False,
    longtable: bool = False,
    escape: bool = True,
    **kwargs
) -> None:
    """
    Save object as LaTeX/TeX format.

    Parameters
    ----------
    obj : Any
        Object to save. Supported types:
        - pandas.DataFrame: Converted to LaTeX table
        - dict/list[dict]: Converted via convert_results() if available
        - str: Written directly as pre-formatted TeX
        - Other: Attempted conversion to string
    spath : str
        Path where the .tex file will be saved.
    caption : str, optional
        Table caption (wrapped in \\caption{})
    label : str, optional
        Table label for referencing (wrapped in \\label{})
    document : bool, default False
        If True, wrap content in full LaTeX document structure
    longtable : bool, default False
        Use longtable environment for multi-page tables (DataFrames only)
    escape : bool, default True
        Escape special LaTeX characters (DataFrames only)
    **kwargs
        Additional arguments passed to df.to_latex() or convert_results()

    Returns
    -------
    None

    Examples
    --------
    >>> import pandas as pd
    >>> import scitex as stx
    >>>
    >>> # Save DataFrame as LaTeX table
    >>> df = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
    >>> stx.io.save(df, 'table.tex')
    >>>
    >>> # With caption and label
    >>> stx.io.save(df, 'table.tex', caption='My Results', label='tab:results')
    >>>
    >>> # Save raw LaTeX string
    >>> latex = r'\\begin{equation} E = mc^2 \\end{equation}'
    >>> stx.io.save(latex, 'equation.tex')
    >>>
    >>> # Full document
    >>> stx.io.save(df, 'doc.tex', document=True)

    Notes
    -----
    - For DataFrames, uses pandas.DataFrame.to_latex()
    - For dicts/lists, attempts to use scitex.stats.utils.convert_results()
    - For strings, writes content directly
    - The document=True option creates a complete compilable LaTeX document
    """
    import pandas as pd

    # Determine content based on object type
    tex_content = None

    if isinstance(obj, str):
        # Direct string writing
        tex_content = obj

    elif isinstance(obj, pd.DataFrame):
        # DataFrame to LaTeX table
        tex_content = _dataframe_to_latex(
            obj,
            caption=caption,
            label=label,
            longtable=longtable,
            escape=escape,
            **kwargs
        )

    elif isinstance(obj, (dict, list)):
        # Try to convert using stats module's convert_results
        try:
            from ...stats.utils._normalizers import convert_results
            tex_content = convert_results(obj, return_as='latex', **kwargs)

            # Add caption and label if provided
            if caption or label:
                tex_content = _wrap_with_table_env(tex_content, caption, label)

        except ImportError:
            warnings.warn(
                "Cannot convert dict/list to LaTeX: "
                "scitex.stats.utils.convert_results not available. "
                "Converting to string instead."
            )
            tex_content = str(obj)
        except Exception as e:
            warnings.warn(
                f"Failed to convert object to LaTeX: {e}. "
                f"Converting to string instead."
            )
            tex_content = str(obj)

    else:
        # Fallback: convert to string
        warnings.warn(
            f"Unsupported type {type(obj)} for LaTeX export. "
            f"Converting to string."
        )
        tex_content = str(obj)

    # Wrap in document structure if requested
    if document:
        tex_content = _wrap_in_document(tex_content)

    # Write to file
    with open(spath, 'w') as f:
        f.write(tex_content)


def _dataframe_to_latex(
    df: 'pd.DataFrame',
    caption: Optional[str] = None,
    label: Optional[str] = None,
    longtable: bool = False,
    escape: bool = True,
    **kwargs
) -> str:
    """
    Convert pandas DataFrame to LaTeX table.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to convert
    caption : str, optional
        Table caption
    label : str, optional
        Table label for referencing
    longtable : bool
        Use longtable environment for multi-page tables
    escape : bool
        Escape special LaTeX characters
    **kwargs
        Additional arguments for df.to_latex()

    Returns
    -------
    str
        LaTeX table string
    """
    import pandas as pd

    # Build to_latex arguments
    latex_kwargs = {
        'index': False,
        'escape': escape,
    }

    if longtable:
        latex_kwargs['longtable'] = True

    if caption:
        latex_kwargs['caption'] = caption

    if label:
        latex_kwargs['label'] = label

    # Merge with user kwargs
    latex_kwargs.update(kwargs)

    # Convert to LaTeX
    return df.to_latex(**latex_kwargs)


def _wrap_with_table_env(
    content: str,
    caption: Optional[str] = None,
    label: Optional[str] = None
) -> str:
    """
    Wrap LaTeX content in table environment with caption and label.

    Parameters
    ----------
    content : str
        LaTeX content to wrap
    caption : str, optional
        Table caption
    label : str, optional
        Table label

    Returns
    -------
    str
        Wrapped LaTeX content
    """
    lines = ['\\begin{table}[htbp]', '\\centering']

    if caption:
        lines.append(f'\\caption{{{caption}}}')

    if label:
        lines.append(f'\\label{{{label}}}')

    lines.append(content)
    lines.append('\\end{table}')

    return '\n'.join(lines)


def _wrap_in_document(content: str) -> str:
    """
    Wrap LaTeX content in complete document structure.

    Parameters
    ----------
    content : str
        LaTeX content to wrap

    Returns
    -------
    str
        Complete LaTeX document
    """
    document_template = r'''\documentclass{article}
\usepackage{booktabs}
\usepackage{longtable}
\usepackage{array}
\usepackage{multirow}
\usepackage{geometry}
\geometry{margin=1in}

\begin{document}

%s

\end{document}
'''
    return document_template % content


# Alias for consistency with other save modules
_save_tex = save_tex

# EOF
