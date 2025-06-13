#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-05 12:00:00 (ywatanabe)"
# File: ./src/scitex/str/_latex.py

"""
LaTeX formatting functions with fallback mechanisms.

Functionality:
    - LaTeX text formatting with automatic fallback
    - Safe handling of LaTeX rendering failures
Input:
    Strings or numbers to format
Output:
    LaTeX-formatted strings with fallback support
Prerequisites:
    matplotlib, _latex_fallback module
"""

from ._latex_fallback import safe_latex_render, latex_fallback_decorator


@latex_fallback_decorator(fallback_strategy="auto", preserve_math=True)
def to_latex_style(str_or_num):
    """
    Convert string or number to LaTeX math mode format with fallback.
    
    Parameters
    ----------
    str_or_num : str or numeric
        Input to format in LaTeX style
        
    Returns
    -------
    str
        LaTeX-formatted string with automatic fallback
        
    Examples
    --------
    >>> to_latex_style('aaa')
    '$aaa$'
    
    >>> to_latex_style('alpha')  # Falls back to unicode if LaTeX fails
    'α'
    
    Notes
    -----
    If LaTeX rendering fails (e.g., due to missing fonts or Node.js conflicts),
    this function automatically falls back to mathtext or unicode alternatives.
    """
    if not str_or_num and str_or_num != 0:  # Handle empty string case
        return ""
    
    string = str(str_or_num)
    
    # Avoid double-wrapping
    if len(string) >= 2 and string[0] == "$" and string[-1] == "$":
        return safe_latex_render(string)
    else:
        latex_string = "${}$".format(string)
        return safe_latex_render(latex_string)


@latex_fallback_decorator(fallback_strategy="auto", preserve_math=True)
def add_hat_in_latex_style(str_or_num):
    """
    Add LaTeX hat notation to string with fallback.
    
    Parameters
    ----------
    str_or_num : str or numeric
        Input to format with hat notation
        
    Returns
    -------
    str
        LaTeX-formatted string with hat notation and automatic fallback
        
    Examples
    --------
    >>> add_hat_in_latex_style('aaa')
    '$\\hat{aaa}$'
    
    >>> add_hat_in_latex_style('x')  # Falls back to unicode if LaTeX fails
    'x̂'
    
    Notes
    -----
    If LaTeX rendering fails, this function falls back to unicode hat
    notation or plain text alternatives.
    """
    if not str_or_num and str_or_num != 0:  # Handle empty string case
        return ""
    
    hat_latex = r"\hat{%s}" % str_or_num
    latex_string = to_latex_style(hat_latex)
    return safe_latex_render(latex_string)


def safe_to_latex_style(str_or_num, fallback_strategy="auto"):
    """
    Safe version of to_latex_style with explicit fallback control.
    
    Parameters
    ----------
    str_or_num : str or numeric
        Input to format in LaTeX style
    fallback_strategy : str, optional
        Explicit fallback strategy: "auto", "mathtext", "unicode", "plain"
        
    Returns
    -------
    str
        Formatted string with specified fallback behavior
    """
    if not str_or_num and str_or_num != 0:
        return ""
    
    string = str(str_or_num)
    if len(string) >= 2 and string[0] == "$" and string[-1] == "$":
        return safe_latex_render(string, fallback_strategy)
    else:
        latex_string = "${}$".format(string)
        return safe_latex_render(latex_string, fallback_strategy)


def safe_add_hat_in_latex_style(str_or_num, fallback_strategy="auto"):
    """
    Safe version of add_hat_in_latex_style with explicit fallback control.
    
    Parameters
    ----------
    str_or_num : str or numeric
        Input to format with hat notation
    fallback_strategy : str, optional
        Explicit fallback strategy: "auto", "mathtext", "unicode", "plain"
        
    Returns
    -------
    str
        Formatted string with hat notation and specified fallback behavior
    """
    if not str_or_num and str_or_num != 0:
        return ""
    
    hat_latex = r"\hat{%s}" % str_or_num
    latex_string = safe_to_latex_style(hat_latex, fallback_strategy)
    return latex_string


# Backward compatibility aliases
latex_style = to_latex_style
hat_latex_style = add_hat_in_latex_style

# EOF
