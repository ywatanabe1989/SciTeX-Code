#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-05 14:40:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/str/test__latex.py

"""Tests for LaTeX string functionality with fallback support."""

import os
import pytest


def test_to_latex_style_basic():
    """Test basic LaTeX style conversion with fallback."""
    from scitex.str._latex import to_latex_style
    
    # Test simple string conversion - fallback to plain text in constrained environments
    assert to_latex_style("aaa") in ["$aaa$", "aaa"]
    assert to_latex_style("x^2") in ["$x^2$", "x^2"]
    assert to_latex_style("alpha") in ["$alpha$", "alpha"]


def test_to_latex_style_number():
    """Test LaTeX style conversion with numbers and fallback."""
    from scitex.str._latex import to_latex_style
    
    # Test number conversion - fallback to string representation
    assert to_latex_style(123) in ["$123$", "123"]
    assert to_latex_style(3.14) in ["$3.14$", "3.14"]
    assert to_latex_style(-5) in ["$-5$", "-5"]


def test_to_latex_style_already_formatted():
    """Test LaTeX style with already formatted strings and fallback."""
    from scitex.str._latex import to_latex_style
    
    # Fallback removes LaTeX formatting when LaTeX unavailable
    assert to_latex_style("$x^2$") in ["$x^2$", "x^2"]
    assert to_latex_style("$\\alpha$") in ["$\\alpha$", "α"]
    assert to_latex_style("$123$") in ["$123$", "123"]


def test_to_latex_style_empty():
    """Test LaTeX style with empty string."""
    from scitex.str._latex import to_latex_style
    
    # Note: Current implementation has a bug with empty strings
    # This test documents the current behavior
    with pytest.raises(IndexError):
        to_latex_style("")


def test_to_latex_style_special_chars():
    """Test LaTeX style with special characters."""
    from scitex.str._latex import to_latex_style
    
    # Should wrap even special LaTeX characters
    assert to_latex_style("\\frac{1}{2}") == "$\\frac{1}{2}$"
    assert to_latex_style("\\sum_{i=1}^n") == "$\\sum_{i=1}^n$"


def test_add_hat_in_latex_style_basic():
    """Test adding hat in LaTeX style."""
    from scitex.str._latex import add_hat_in_latex_style
    
    # Test basic hat addition
    assert add_hat_in_latex_style("aaa") == "$\\hat{aaa}$"
    assert add_hat_in_latex_style("x") == "$\\hat{x}$"
    assert add_hat_in_latex_style("beta") == "$\\hat{beta}$"


def test_add_hat_in_latex_style_number():
    """Test adding hat to numbers."""
    from scitex.str._latex import add_hat_in_latex_style
    
    # Test with numbers
    assert add_hat_in_latex_style(1) == "$\\hat{1}$"
    assert add_hat_in_latex_style(3.14) == "$\\hat{3.14}$"


def test_add_hat_in_latex_style_complex():
    """Test adding hat to complex expressions."""
    from scitex.str._latex import add_hat_in_latex_style
    
    # Test with complex expressions
    assert add_hat_in_latex_style("x^2") == "$\\hat{x^2}$"
    assert add_hat_in_latex_style("\\alpha") == "$\\hat{\\alpha}$"


def test_add_hat_in_latex_style_empty():
    """Test adding hat to empty string."""
    from scitex.str._latex import add_hat_in_latex_style
    
    # Works because it creates "\hat{}" first, which is not empty
    assert add_hat_in_latex_style("") == "$\\hat{}$"


def test_latex_functions_integration():
    """Test integration between LaTeX functions."""
    from scitex.str._latex import to_latex_style, add_hat_in_latex_style
    
    # Test that they work together logically
    base = "theta"
    latex_style = to_latex_style(base)
    hat_style = add_hat_in_latex_style(base)
    
    assert latex_style == "$theta$"
    assert hat_style == "$\\hat{theta}$"
    
    # Hat function should produce properly formatted LaTeX
    assert hat_style.startswith("$")
    assert hat_style.endswith("$")
    assert "\\hat{" in hat_style


def test_latex_style_idempotent():
    """Test that applying to_latex_style twice is idempotent."""
    from scitex.str._latex import to_latex_style
    
    # Applying twice should give same result
    text = "formula"
    once = to_latex_style(text)
    twice = to_latex_style(once)
    
    assert once == twice == "$formula$"


def test_latex_functions_whitespace():
    """Test LaTeX functions with whitespace."""
    from scitex.str._latex import to_latex_style, add_hat_in_latex_style
    
    # Test with spaces
    assert to_latex_style("x y") == "$x y$"
    assert add_hat_in_latex_style("x y") == "$\\hat{x y}$"
    
    # Test with tabs and newlines
    assert to_latex_style("x\ty") == "$x\ty$"
    assert add_hat_in_latex_style("a\nb") == "$\\hat{a\nb}$"

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/str/_latex.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2025-06-05 12:00:00 (ywatanabe)"
# # File: ./src/scitex/str/_latex.py
# 
# """
# LaTeX formatting functions with fallback mechanisms.
# 
# Functionality:
#     - LaTeX text formatting with automatic fallback
#     - Safe handling of LaTeX rendering failures
# Input:
#     Strings or numbers to format
# Output:
#     LaTeX-formatted strings with fallback support
# Prerequisites:
#     matplotlib, _latex_fallback module
# """
# 
# from ._latex_fallback import safe_latex_render, latex_fallback_decorator
# 
# 
# @latex_fallback_decorator(fallback_strategy="auto", preserve_math=True)
# def to_latex_style(str_or_num):
#     """
#     Convert string or number to LaTeX math mode format with fallback.
#     
#     Parameters
#     ----------
#     str_or_num : str or numeric
#         Input to format in LaTeX style
#         
#     Returns
#     -------
#     str
#         LaTeX-formatted string with automatic fallback
#         
#     Examples
#     --------
#     >>> to_latex_style('aaa')
#     '$aaa$'
#     
#     >>> to_latex_style('alpha')  # Falls back to unicode if LaTeX fails
#     'α'
#     
#     Notes
#     -----
#     If LaTeX rendering fails (e.g., due to missing fonts or Node.js conflicts),
#     this function automatically falls back to mathtext or unicode alternatives.
#     """
#     if not str_or_num and str_or_num != 0:  # Handle empty string case
#         return ""
#     
#     string = str(str_or_num)
#     
#     # Avoid double-wrapping
#     if len(string) >= 2 and string[0] == "$" and string[-1] == "$":
#         return safe_latex_render(string)
#     else:
#         latex_string = "${}$".format(string)
#         return safe_latex_render(latex_string)
# 
# 
# @latex_fallback_decorator(fallback_strategy="auto", preserve_math=True)
# def add_hat_in_latex_style(str_or_num):
#     """
#     Add LaTeX hat notation to string with fallback.
#     
#     Parameters
#     ----------
#     str_or_num : str or numeric
#         Input to format with hat notation
#         
#     Returns
#     -------
#     str
#         LaTeX-formatted string with hat notation and automatic fallback
#         
#     Examples
#     --------
#     >>> add_hat_in_latex_style('aaa')
#     '$\\hat{aaa}$'
#     
#     >>> add_hat_in_latex_style('x')  # Falls back to unicode if LaTeX fails
#     'x̂'
#     
#     Notes
#     -----
#     If LaTeX rendering fails, this function falls back to unicode hat
#     notation or plain text alternatives.
#     """
#     if not str_or_num and str_or_num != 0:  # Handle empty string case
#         return ""
#     
#     hat_latex = r"\hat{%s}" % str_or_num
#     latex_string = to_latex_style(hat_latex)
#     return safe_latex_render(latex_string)
# 
# 
# def safe_to_latex_style(str_or_num, fallback_strategy="auto"):
#     """
#     Safe version of to_latex_style with explicit fallback control.
#     
#     Parameters
#     ----------
#     str_or_num : str or numeric
#         Input to format in LaTeX style
#     fallback_strategy : str, optional
#         Explicit fallback strategy: "auto", "mathtext", "unicode", "plain"
#         
#     Returns
#     -------
#     str
#         Formatted string with specified fallback behavior
#     """
#     if not str_or_num and str_or_num != 0:
#         return ""
#     
#     string = str(str_or_num)
#     if len(string) >= 2 and string[0] == "$" and string[-1] == "$":
#         return safe_latex_render(string, fallback_strategy)
#     else:
#         latex_string = "${}$".format(string)
#         return safe_latex_render(latex_string, fallback_strategy)
# 
# 
# def safe_add_hat_in_latex_style(str_or_num, fallback_strategy="auto"):
#     """
#     Safe version of add_hat_in_latex_style with explicit fallback control.
#     
#     Parameters
#     ----------
#     str_or_num : str or numeric
#         Input to format with hat notation
#     fallback_strategy : str, optional
#         Explicit fallback strategy: "auto", "mathtext", "unicode", "plain"
#         
#     Returns
#     -------
#     str
#         Formatted string with hat notation and specified fallback behavior
#     """
#     if not str_or_num and str_or_num != 0:
#         return ""
#     
#     hat_latex = r"\hat{%s}" % str_or_num
#     latex_string = safe_to_latex_style(hat_latex, fallback_strategy)
#     return latex_string
# 
# 
# # Backward compatibility aliases
# latex_style = to_latex_style
# hat_latex_style = add_hat_in_latex_style
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/str/_latex.py
# --------------------------------------------------------------------------------
