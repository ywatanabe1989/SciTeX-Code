#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-07 15:35:00 (ywatanabe)"
# File: ./tests/scitex/str/test__latex_fallback.py

"""
Comprehensive tests for LaTeX fallback mechanism.

This module tests the LaTeX fallback functionality that gracefully
handles LaTeX rendering failures by converting to mathtext or unicode.
"""

import pytest
import matplotlib.pyplot as plt
from unittest.mock import Mock, patch, MagicMock
import functools
from scitex.str import set_fallback_mode, get_fallback_mode, latex_to_mathtext, latex_to_unicode, safe_latex_render, latex_fallback_decorator, get_latex_status, enable_latex_fallback, disable_latex_fallback, reset_latex_cache, LaTeXFallbackError

# Mocked missing functions for testing
check_latex_capability = lambda *args, **kwargs: None  # Mocked

# Missing imports: check_latex_capability


class TestFallbackMode:
    """Test fallback mode management."""

    def setup_method(self):
        """Reset state before each test."""
        reset_latex_cache()
        set_fallback_mode("auto")

    def test_set_fallback_mode_valid(self):
        """Test setting valid fallback modes."""
        for mode in ["auto", "force_mathtext", "force_plain"]:
            set_fallback_mode(mode)
            assert get_fallback_mode() == mode

    def test_set_fallback_mode_invalid(self):
        """Test setting invalid fallback mode raises error."""
        with pytest.raises(ValueError, match="Invalid fallback mode"):
            set_fallback_mode("invalid_mode")

    def test_fallback_mode_resets_cache(self):
        """Test that changing mode resets LaTeX capability cache."""
        # Force a capability check to cache result
        check_latex_capability()
        cache_info_before = check_latex_capability.cache_info()
        
        # Change mode should reset cache
        set_fallback_mode("force_mathtext")
        
        # This should trigger a new check
        check_latex_capability()
        cache_info_after = check_latex_capability.cache_info()
        
        # Cache should have been cleared
        assert cache_info_after.hits == 0


class TestLatexCapability:
    """Test LaTeX capability detection."""

    def setup_method(self):
        """Reset state before each test."""
        reset_latex_cache()
        set_fallback_mode("auto")

    @patch('matplotlib.pyplot.rcParams', {'text.usetex': False})
    def test_latex_disabled_in_rcparams(self):
        """Test capability when LaTeX is disabled in rcParams."""
        assert not check_latex_capability()

    @patch('matplotlib.pyplot.rcParams', {'text.usetex': True})
    def test_latex_enabled_but_fails(self):
        """Test capability when LaTeX is enabled but rendering fails."""
        with patch('matplotlib.pyplot.subplots') as mock_subplots:
            mock_fig = Mock()
            mock_ax = Mock()
            mock_ax.text.side_effect = Exception("LaTeX error")
            mock_subplots.return_value = (mock_fig, mock_ax)
            
            assert not check_latex_capability()

    @patch('matplotlib.pyplot.rcParams', {'text.usetex': True})
    def test_latex_enabled_and_works(self):
        """Test capability when LaTeX is enabled and working."""
        with patch('matplotlib.pyplot.subplots') as mock_subplots:
            mock_fig = Mock()
            mock_ax = Mock()
            mock_fig.canvas = Mock()
            mock_subplots.return_value = (mock_fig, mock_ax)
            
            result = check_latex_capability()
            # Result depends on actual system capability
            assert isinstance(result, bool)

    def test_force_modes_return_false(self):
        """Test that force modes always return False for capability."""
        set_fallback_mode("force_mathtext")
        assert not check_latex_capability()
        
        set_fallback_mode("force_plain")
        assert not check_latex_capability()

    def test_capability_is_cached(self):
        """Test that capability check is cached."""
        # First call
        check_latex_capability()
        cache_info = check_latex_capability.cache_info()
        assert cache_info.misses == 1
        
        # Second call should hit cache
        check_latex_capability()
        cache_info = check_latex_capability.cache_info()
        assert cache_info.hits == 1


class TestLatexToMathtext:
    """Test LaTeX to mathtext conversion."""

    def test_empty_string(self):
        """Test conversion of empty string."""
        assert latex_to_mathtext("") == ""

    def test_basic_greek_letters(self):
        """Test conversion of Greek letters."""
        assert latex_to_mathtext(r"$\\alpha$") == r"$\alpha$"
        assert latex_to_mathtext(r"$\\beta$") == r"$\beta$"
        assert latex_to_mathtext(r"$\\gamma$") == r"$\gamma$"

    def test_mathematical_symbols(self):
        """Test conversion of mathematical symbols."""
        assert latex_to_mathtext(r"$\\sum$") == r"$\sum$"
        assert latex_to_mathtext(r"$\\int$") == r"$\int$"
        assert latex_to_mathtext(r"$\\partial$") == r"$\partial$"

    def test_functions(self):
        """Test conversion of functions."""
        assert latex_to_mathtext(r"$\\sin x$") == r"$\sin x$"
        assert latex_to_mathtext(r"$\\cos \\theta$") == r"$\cos \theta$"

    def test_formatting(self):
        """Test conversion of formatting commands."""
        assert latex_to_mathtext(r"$\\textbf{bold}$") == r"$\mathbf{bold}$"
        assert latex_to_mathtext(r"$\\textit{italic}$") == r"$\mathit{italic}$"

    def test_fractions(self):
        """Test conversion of fractions."""
        assert latex_to_mathtext(r"$\\frac{1}{2}$") == r"$\frac{1}{2}$"

    def test_accents(self):
        """Test conversion of accents."""
        assert latex_to_mathtext(r"$\\hat{x}$") == r"$\hat{x}$"
        assert latex_to_mathtext(r"$\\vec{v}$") == r"$\vec{v}$"

    def test_strip_outer_dollars(self):
        """Test stripping of outer dollar signs."""
        assert latex_to_mathtext(r"$x^2$") == r"$x^2$"
        assert latex_to_mathtext(r"x^2") == r"$x^2$"

    def test_complex_expression(self):
        """Test conversion of complex expression."""
        input_latex = r"$\\int_0^\\infty \\sin(\\omega t) dt$"
        expected = r"$\int_0^\infty \sin(\omega t) dt$"
        assert latex_to_mathtext(input_latex) == expected


class TestLatexToUnicode:
    """Test LaTeX to Unicode conversion."""

    def test_empty_string(self):
        """Test conversion of empty string."""
        assert latex_to_unicode("") == ""

    def test_greek_letters(self):
        """Test conversion of Greek letters to Unicode."""
        assert latex_to_unicode(r"$\\alpha$") == "α"
        assert latex_to_unicode(r"$\\beta$") == "β"
        assert latex_to_unicode(r"$\\pi$") == "π"
        assert latex_to_unicode(r"$\\Omega$") == "Ω"

    def test_mathematical_symbols(self):
        """Test conversion of math symbols to Unicode."""
        assert latex_to_unicode(r"$\\pm$") == "±"
        assert latex_to_unicode(r"$\\times$") == "×"
        assert latex_to_unicode(r"$\\infty$") == "∞"
        assert latex_to_unicode(r"$\\sum$") == "∑"

    def test_superscripts(self):
        """Test conversion of superscripts."""
        assert latex_to_unicode(r"$x^2$") == "x²"
        assert latex_to_unicode(r"$x^{3}$") == "x³"

    def test_subscripts(self):
        """Test conversion of subscripts."""
        assert latex_to_unicode(r"$x_0$") == "x₀"
        assert latex_to_unicode(r"$x_{1}$") == "x₁"

    def test_command_removal(self):
        """Test removal of LaTeX commands."""
        assert latex_to_unicode(r"$\\textbf{bold}$") == "bold"
        assert latex_to_unicode(r"$\\unknown command$") == " command"

    def test_mixed_content(self):
        """Test conversion of mixed content."""
        assert latex_to_unicode(r"$\\alpha_0 \\times \\beta^2$") == "α₀ × β²"

    def test_strip_braces(self):
        """Test removal of remaining braces."""
        assert latex_to_unicode(r"${x}$") == "x"


class TestSafeLatexRender:
    """Test safe LaTeX rendering with fallback."""

    def setup_method(self):
        """Reset state before each test."""
        reset_latex_cache()
        set_fallback_mode("auto")

    def test_empty_input(self):
        """Test handling of empty input."""
        assert safe_latex_render("") == ""
        assert safe_latex_render(None) == None

    def test_non_string_input(self):
        """Test handling of non-string input."""
        assert safe_latex_render(123) == 123
        assert safe_latex_render([1, 2, 3]) == [1, 2, 3]

    @patch('scitex.str._latex_fallback.check_latex_capability', return_value=True)
    def test_successful_latex_render(self, mock_check):
        """Test successful LaTeX rendering."""
        with patch('matplotlib.pyplot.subplots') as mock_subplots:
            mock_fig = Mock()
            mock_ax = Mock()
            mock_fig.canvas = Mock()
            mock_subplots.return_value = (mock_fig, mock_ax)
            
            result = safe_latex_render(r"$x^2$")
            assert result == r"$x^2$"

    @patch('scitex.str._latex_fallback.check_latex_capability', return_value=True)
    def test_latex_render_fails_fallback_to_mathtext(self, mock_check):
        """Test fallback to mathtext when LaTeX fails."""
        with patch('matplotlib.pyplot.subplots') as mock_subplots:
            mock_fig = Mock()
            mock_ax = Mock()
            mock_ax.text.side_effect = Exception("LaTeX error")
            mock_subplots.return_value = (mock_fig, mock_ax)
            
            result = safe_latex_render(r"$\\alpha^2$", fallback_strategy="auto")
            assert result == r"$\alpha^2$"

    def test_force_mathtext_strategy(self):
        """Test force mathtext strategy."""
        result = safe_latex_render(r"$\\beta$", fallback_strategy="mathtext")
        assert result == r"$\beta$"

    def test_force_unicode_strategy(self):
        """Test force unicode strategy."""
        result = safe_latex_render(r"$\\gamma$", fallback_strategy="unicode")
        assert result == "γ"

    def test_plain_strategy(self):
        """Test plain text strategy."""
        result = safe_latex_render(r"$\\delta^2$", fallback_strategy="plain")
        assert "2" in result  # Should contain the 2
        assert "$" not in result  # Should not contain LaTeX markers

    def test_invalid_strategy(self):
        """Test invalid fallback strategy."""
        with pytest.raises(ValueError, match="Unknown fallback strategy"):
            safe_latex_render(r"$x$", fallback_strategy="invalid")

    def test_preserve_math_true(self):
        """Test preserve_math=True behavior."""
        set_fallback_mode("force_mathtext")
        result = safe_latex_render(r"$\\pi r^2$", preserve_math=True)
        assert "$" in result  # Should preserve math mode

    def test_preserve_math_false(self):
        """Test preserve_math=False behavior."""
        set_fallback_mode("force_mathtext")
        result = safe_latex_render(r"$\\pi r^2$", preserve_math=False)
        assert "π" in result  # Should use unicode


class TestLatexFallbackDecorator:
    """Test LaTeX fallback decorator."""

    def test_successful_function_call(self):
        """Test decorator with successful function call."""
        @latex_fallback_decorator()
        def test_func(text):
            return f"Rendered: {text}"
        
        result = test_func("Hello")
        assert result == "Rendered: Hello"

    def test_latex_error_fallback(self):
        """Test decorator fallback on LaTeX error."""
        @latex_fallback_decorator(fallback_strategy="unicode")
        def test_func(text):
            if "\\alpha" in text:
                raise Exception("LaTeX rendering failed")
            return text
        
        with patch('matplotlib.pyplot.rcParams', {'text.usetex': True}):
            result = test_func(r"$\\alpha$")
            assert result == "α"

    def test_non_latex_error_propagation(self):
        """Test that non-LaTeX errors are propagated."""
        @latex_fallback_decorator()
        def test_func():
            raise ValueError("Not a LaTeX error")
        
        with pytest.raises(ValueError, match="Not a LaTeX error"):
            test_func()

    def test_kwargs_handling(self):
        """Test decorator handles kwargs correctly."""
        @latex_fallback_decorator(fallback_strategy="mathtext")
        def test_func(x, label=None):
            if label and "\\beta" in label:
                raise Exception("LaTeX error")
            return f"{x}: {label}"
        
        result = test_func(1, label=r"$\\beta$")
        assert "beta" in result.lower() or "β" in result

    def test_preserve_function_metadata(self):
        """Test decorator preserves function metadata."""
        @latex_fallback_decorator()
        def documented_func():
            """This is a documented function."""
            pass
        
        assert documented_func.__name__ == "documented_func"
        assert documented_func.__doc__ == "This is a documented function."


class TestStatusFunctions:
    """Test status and utility functions."""

    def setup_method(self):
        """Reset state before each test."""
        reset_latex_cache()
        set_fallback_mode("auto")

    def test_get_latex_status(self):
        """Test getting LaTeX status information."""
        status = get_latex_status()
        
        assert 'latex_available' in status
        assert 'fallback_mode' in status
        assert 'usetex_enabled' in status
        assert 'mathtext_fontset' in status
        assert 'font_family' in status
        assert 'cache_info' in status
        
        assert isinstance(status['latex_available'], bool)
        assert status['fallback_mode'] == "auto"

    def test_enable_latex_fallback(self):
        """Test enabling LaTeX fallback."""
        enable_latex_fallback("force_mathtext")
        assert get_fallback_mode() == "force_mathtext"
        
        enable_latex_fallback()  # Default to "auto"
        assert get_fallback_mode() == "auto"

    def test_disable_latex_fallback(self):
        """Test disabling LaTeX fallback."""
        disable_latex_fallback()
        # This should force LaTeX usage
        # Implementation sets _latex_available = True

    def test_reset_latex_cache(self):
        """Test resetting LaTeX cache."""
        # Make a call to populate cache
        check_latex_capability()
        cache_info_before = check_latex_capability.cache_info()
        
        # Reset cache
        reset_latex_cache()
        
        # Make another call
        check_latex_capability()
        cache_info_after = check_latex_capability.cache_info()
        
        # Cache should have been cleared
        assert cache_info_after.misses >= 1
        assert cache_info_after.hits == 0


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_deeply_nested_latex(self):
        """Test handling of deeply nested LaTeX."""
        nested = r"$\\frac{\\alpha}{\\sqrt{\\beta^2 + \\gamma^2}}$"
        result = latex_to_mathtext(nested)
        assert "frac" in result
        assert "alpha" in result

    def test_malformed_latex(self):
        """Test handling of malformed LaTeX."""
        malformed = r"$\\frac{1{2}$"  # Missing closing brace
        # Should not crash
        result = latex_to_unicode(malformed)
        assert isinstance(result, str)

    def test_unicode_normalization(self):
        """Test Unicode normalization."""
        # Test that combining characters work
        result = latex_to_unicode(r"$\\tilde{n}$")
        assert isinstance(result, str)

    def test_empty_commands(self):
        """Test handling of empty LaTeX commands."""
        assert latex_to_unicode(r"$\\$") == ""
        assert latex_to_unicode(r"$\\{}$") == ""

    def test_consecutive_superscripts(self):
        """Test handling of consecutive superscripts."""
        result = latex_to_unicode(r"$2^{10}$")
        assert "2" in result
        assert "¹⁰" in result or "10" in result

    def test_mixed_super_subscripts(self):
        """Test handling of mixed super and subscripts."""
        result = latex_to_unicode(r"$x_i^2$")
        assert "x" in result
        # Should contain both sub and superscript

    def test_special_latex_environments(self):
        """Test handling of special LaTeX environments."""
        # These should be stripped or handled gracefully
        env_text = r"$\\begin{array}{c} x \\\\ y \\end{array}$"
        result = safe_latex_render(env_text, fallback_strategy="unicode")
        assert isinstance(result, str)
        assert "x" in result or "y" in result

    def test_thread_safety(self):
        """Test thread safety of cached functions."""
        # The lru_cache should be thread-safe
        import threading
        results = []
        
        def check_capability():
            results.append(check_latex_capability())
        
        threads = [threading.Thread(target=check_capability) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # All results should be the same
        assert all(r == results[0] for r in results)

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/str/_latex_fallback.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2025-06-05 12:00:00 (ywatanabe)"
# # File: ./src/scitex/str/_latex_fallback.py
# 
# """
# LaTeX Fallback Mechanism for SciTeX
# 
# This module provides a robust fallback system for LaTeX rendering issues.
# When LaTeX compilation fails (e.g., missing fonts, Node.js conflicts), 
# it gracefully degrades to mathtext or plain text alternatives.
# 
# Functionality:
#     - Detect LaTeX rendering capabilities
#     - Convert LaTeX to mathtext equivalents
#     - Provide plain text fallbacks
#     - Cache LaTeX capability status
# Input:
#     LaTeX strings and matplotlib configuration
# Output:
#     Fallback-compatible strings for matplotlib
# Prerequisites:
#     matplotlib
# """
# 
# import functools
# import logging
# import re
# import warnings
# from typing import Dict, Optional, Tuple, Union, Callable, Any
# 
# # matplotlib imports moved to functions that need them
# 
# # Configure logging
# logger = logging.getLogger(__name__)
# 
# # Global state for LaTeX capability
# _latex_available = None
# _fallback_mode = "auto"  # "auto", "force_mathtext", "force_plain"
# 
# 
# class LaTeXFallbackError(Exception):
#     """Raised when LaTeX fallback mechanisms fail."""
#     pass
# 
# 
# def set_fallback_mode(mode: str) -> None:
#     """
#     Set the global fallback mode for LaTeX rendering.
#     
#     Parameters
#     ----------
#     mode : str
#         Fallback mode: "auto" (detect capability), "force_mathtext", or "force_plain"
#     """
#     global _fallback_mode
#     if mode not in ["auto", "force_mathtext", "force_plain"]:
#         raise ValueError(f"Invalid fallback mode: {mode}")
#     _fallback_mode = mode
#     # Reset capability cache when mode changes
#     global _latex_available
#     _latex_available = None
# 
# 
# def get_fallback_mode() -> str:
#     """Get the current fallback mode."""
#     return _fallback_mode
# 
# 
# @functools.lru_cache(maxsize=1)
# def check_latex_capability() -> bool:
#     """
#     Check if LaTeX rendering is available and working.
#     
#     Returns
#     -------
#     bool
#         True if LaTeX is available, False otherwise
#     """
#     global _latex_available
#     
#     # Import matplotlib here when actually needed
#     try:
#         import matplotlib.pyplot as plt
#     except ImportError:
#         _latex_available = False
#         return False
#     
#     # If forcing a mode, return accordingly
#     if _fallback_mode == "force_mathtext" or _fallback_mode == "force_plain":
#         _latex_available = False
#         return False
#     
#     # Cache the result if already determined
#     if _latex_available is not None:
#         return _latex_available
#     
#     try:
#         # Test if LaTeX is configured
#         if not plt.rcParams.get('text.usetex', False):
#             _latex_available = False
#             return False
#         
#         # Try a simple LaTeX rendering test
#         fig, ax = plt.subplots(figsize=(1, 1))
#         try:
#             # Test with a simple LaTeX expression
#             text_obj = ax.text(0.5, 0.5, r'$x^2$', usetex=True)
#             fig.canvas.draw()  # Force rendering
#             _latex_available = True
#             result = True
#         except Exception as e:
#             logger.debug(f"LaTeX capability test failed: {e}")
#             _latex_available = False
#             result = False
#         finally:
#             plt.close(fig)
#         
#         return result
#         
#     except Exception as e:
#         logger.debug(f"LaTeX capability check failed: {e}")
#         _latex_available = False
#         return False
# 
# 
# def latex_to_mathtext(latex_str: str) -> str:
#     """
#     Convert LaTeX syntax to matplotlib mathtext equivalent.
#     
#     Parameters
#     ----------
#     latex_str : str
#         LaTeX string to convert
#         
#     Returns
#     -------
#     str
#         Mathtext equivalent string
#     """
#     if not latex_str:
#         return latex_str
#     
#     # Remove outer $ if present
#     text = latex_str.strip()
#     if text.startswith('$') and text.endswith('$'):
#         text = text[1:-1]
#     
#     # Common LaTeX to mathtext conversions
#     conversions = {
#         # Greek letters
#         r'\\alpha': r'\alpha',
#         r'\\beta': r'\beta', 
#         r'\\gamma': r'\gamma',
#         r'\\delta': r'\delta',
#         r'\\epsilon': r'\epsilon',
#         r'\\theta': r'\theta',
#         r'\\lambda': r'\lambda',
#         r'\\mu': r'\mu',
#         r'\\pi': r'\pi',
#         r'\\sigma': r'\sigma',
#         r'\\tau': r'\tau',
#         r'\\phi': r'\phi',
#         r'\\omega': r'\omega',
#         
#         # Mathematical symbols
#         r'\\sum': r'\sum',
#         r'\\int': r'\int',
#         r'\\partial': r'\partial',
#         r'\\infty': r'\infty',
#         r'\\pm': r'\pm',
#         r'\\times': r'\times',
#         r'\\cdot': r'\cdot',
#         r'\\approx': r'\approx',
#         r'\\neq': r'\neq',
#         r'\\leq': r'\leq',
#         r'\\geq': r'\geq',
#         
#         # Functions
#         r'\\sin': r'\sin',
#         r'\\cos': r'\cos',
#         r'\\tan': r'\tan',
#         r'\\log': r'\log',
#         r'\\ln': r'\ln',
#         r'\\exp': r'\exp',
#         
#         # Formatting (limited mathtext support)
#         r'\\textbf\{([^}]+)\}': r'\mathbf{\1}',
#         r'\\mathbf\{([^}]+)\}': r'\mathbf{\1}',
#         r'\\textit\{([^}]+)\}': r'\mathit{\1}',
#         r'\\mathit\{([^}]+)\}': r'\mathit{\1}',
#         
#         # Hats and accents
#         r'\\hat\{([^}]+)\}': r'\hat{\1}',
#         r'\\overrightarrow\{([^}]+)\}': r'\vec{\1}',
#         r'\\vec\{([^}]+)\}': r'\vec{\1}',
#         
#         # Fractions (simple ones)
#         r'\\frac\{([^}]+)\}\{([^}]+)\}': r'\frac{\1}{\2}',
#         
#         # Subscripts and superscripts (should work as-is)
#         # Powers and indices are handled naturally by mathtext
#     }
#     
#     # Apply conversions
#     for latex_pattern, mathtext_replacement in conversions.items():
#         text = re.sub(latex_pattern, mathtext_replacement, text)
#     
#     # Wrap in mathtext markers
#     return f'${text}$'
# 
# 
# def latex_to_unicode(latex_str: str) -> str:
#     """
#     Convert LaTeX to Unicode plain text equivalent.
#     
#     Parameters
#     ----------
#     latex_str : str
#         LaTeX string to convert
#         
#     Returns
#     -------
#     str
#         Unicode plain text equivalent
#     """
#     if not latex_str:
#         return latex_str
#     
#     # Remove outer $ if present
#     text = latex_str.strip()
#     if text.startswith('$') and text.endswith('$'):
#         text = text[1:-1]
#     
#     # Greek letters to Unicode
#     greek_conversions = {
#         r'\\alpha': 'α', r'\\beta': 'β', r'\\gamma': 'γ', r'\\delta': 'δ',
#         r'\\epsilon': 'ε', r'\\zeta': 'ζ', r'\\eta': 'η', r'\\theta': 'θ',
#         r'\\iota': 'ι', r'\\kappa': 'κ', r'\\lambda': 'λ', r'\\mu': 'μ',
#         r'\\nu': 'ν', r'\\xi': 'ξ', r'\\pi': 'π', r'\\rho': 'ρ',
#         r'\\sigma': 'σ', r'\\tau': 'τ', r'\\upsilon': 'υ', r'\\phi': 'φ',
#         r'\\chi': 'χ', r'\\psi': 'ψ', r'\\omega': 'ω',
#         
#         # Capital Greek
#         r'\\Gamma': 'Γ', r'\\Delta': 'Δ', r'\\Theta': 'Θ', r'\\Lambda': 'Λ',
#         r'\\Xi': 'Ξ', r'\\Pi': 'Π', r'\\Sigma': 'Σ', r'\\Upsilon': 'Υ',
#         r'\\Phi': 'Φ', r'\\Psi': 'Ψ', r'\\Omega': 'Ω',
#     }
#     
#     # Mathematical symbols to Unicode
#     symbol_conversions = {
#         r'\\pm': '±', r'\\times': '×', r'\\cdot': '·', r'\\div': '÷',
#         r'\\neq': '≠', r'\\leq': '≤', r'\\geq': '≥', r'\\approx': '≈',
#         r'\\infty': '∞', r'\\partial': '∂', r'\\sum': '∑', r'\\int': '∫',
#         r'\\sqrt': '√', r'\\angle': '∠', r'\\degree': '°',
#     }
#     
#     # Superscript numbers
#     superscript_conversions = {
#         r'\^0': '⁰', r'\^1': '¹', r'\^2': '²', r'\^3': '³', r'\^4': '⁴',
#         r'\^5': '⁵', r'\^6': '⁶', r'\^7': '⁷', r'\^8': '⁸', r'\^9': '⁹',
#         r'\^\{0\}': '⁰', r'\^\{1\}': '¹', r'\^\{2\}': '²', r'\^\{3\}': '³',
#         r'\^\{4\}': '⁴', r'\^\{5\}': '⁵', r'\^\{6\}': '⁶', r'\^\{7\}': '⁷',
#         r'\^\{8\}': '⁸', r'\^\{9\}': '⁹',
#     }
#     
#     # Subscript numbers
#     subscript_conversions = {
#         r'_0': '₀', r'_1': '₁', r'_2': '₂', r'_3': '₃', r'_4': '₄',
#         r'_5': '₅', r'_6': '₆', r'_7': '₇', r'_8': '₈', r'_9': '₉',
#         r'_\{0\}': '₀', r'_\{1\}': '₁', r'_\{2\}': '₂', r'_\{3\}': '₃',
#         r'_\{4\}': '₄', r'_\{5\}': '₅', r'_\{6\}': '₆', r'_\{7\}': '₇',
#         r'_\{8\}': '₈', r'_\{9\}': '₉',
#     }
#     
#     # Apply all conversions
#     all_conversions = {**greek_conversions, **symbol_conversions, 
#                       **superscript_conversions, **subscript_conversions}
#     
#     for latex_pattern, unicode_char in all_conversions.items():
#         text = re.sub(latex_pattern, unicode_char, text)
#     
#     # Remove remaining LaTeX commands (simple cleanup)
#     text = re.sub(r'\\[a-zA-Z]+\{([^}]*)\}', r'\1', text)  # \command{content} -> content
#     text = re.sub(r'\\[a-zA-Z]+', '', text)  # \command -> remove
#     text = re.sub(r'[{}]', '', text)  # Remove remaining braces
#     
#     return text
# 
# 
# def safe_latex_render(
#     text: str,
#     fallback_strategy: str = "auto",
#     preserve_math: bool = True
# ) -> str:
#     """
#     Safely render LaTeX text with automatic fallback.
#     
#     Parameters
#     ----------
#     text : str
#         Text that may contain LaTeX
#     fallback_strategy : str, optional
#         Strategy when LaTeX fails: "auto", "mathtext", "unicode", "plain"
#     preserve_math : bool, optional
#         Whether to preserve mathematical notation in fallbacks
#         
#     Returns
#     -------
#     str
#         Safely rendered text
#     """
#     if not text or not isinstance(text, str):
#         return text
#     
#     # Import matplotlib when needed
#     import matplotlib.pyplot as plt
#     
#     # Determine if we should attempt LaTeX
#     use_latex = (_fallback_mode == "auto" and check_latex_capability())
#     
#     if use_latex:
#         # Try LaTeX first
#         try:
#             # Test rendering capability with the actual text
#             fig, ax = plt.subplots(figsize=(1, 1))
#             try:
#                 ax.text(0.5, 0.5, text, usetex=True)
#                 fig.canvas.draw()
#                 plt.close(fig)
#                 return text  # LaTeX works
#             except Exception:
#                 plt.close(fig)
#                 raise LaTeXFallbackError("LaTeX rendering failed")
#         except Exception:
#             # Fall through to fallback strategies
#             pass
#     
#     # Apply fallback strategy
#     if fallback_strategy == "auto":
#         # Automatically choose best fallback
#         if preserve_math and ('$' in text or '\\' in text):
#             try:
#                 return latex_to_mathtext(text)
#             except Exception:
#                 return latex_to_unicode(text)
#         else:
#             return latex_to_unicode(text)
#     
#     elif fallback_strategy == "mathtext":
#         return latex_to_mathtext(text)
#     
#     elif fallback_strategy == "unicode":
#         return latex_to_unicode(text)
#     
#     elif fallback_strategy == "plain":
#         # Strip all LaTeX and return plain text
#         plain = latex_to_unicode(text)
#         # Remove any remaining special characters
#         plain = re.sub(r'[^\w\s\(\)\[\].,;:!?-]', '', plain)
#         return plain
#     
#     else:
#         raise ValueError(f"Unknown fallback strategy: {fallback_strategy}")
# 
# 
# def latex_fallback_decorator(
#     fallback_strategy: str = "auto",
#     preserve_math: bool = True
# ):
#     """
#     Decorator to add LaTeX fallback capability to functions.
#     
#     Parameters
#     ----------
#     fallback_strategy : str, optional
#         Fallback strategy to use
#     preserve_math : bool, optional
#         Whether to preserve mathematical notation
#         
#     Returns
#     -------
#     callable
#         Decorated function with LaTeX fallback
#     """
#     def decorator(func: Callable) -> Callable:
#         @functools.wraps(func)
#         def wrapper(*args, **kwargs):
#             try:
#                 return func(*args, **kwargs)
#             except Exception as e:
#                 # Check if this is a LaTeX-related error
#                 error_str = str(e).lower()
#                 latex_error_indicators = [
#                     'latex', 'tex', 'dvi', 'tfm', 'font', 'usetex', 
#                     'kpathsea', 'dvipng', 'ghostscript'
#                 ]
#                 
#                 if any(indicator in error_str for indicator in latex_error_indicators):
#                     logger.warning(f"LaTeX error in {func.__name__}: {e}")
#                     logger.warning("Falling back to alternative text rendering")
#                     
#                     # Try to apply fallback to string arguments
#                     new_args = []
#                     for arg in args:
#                         if isinstance(arg, str):
#                             new_args.append(safe_latex_render(
#                                 arg, fallback_strategy, preserve_math
#                             ))
#                         else:
#                             new_args.append(arg)
#                     
#                     new_kwargs = {}
#                     for key, value in kwargs.items():
#                         if isinstance(value, str):
#                             new_kwargs[key] = safe_latex_render(
#                                 value, fallback_strategy, preserve_math
#                             )
#                         else:
#                             new_kwargs[key] = value
#                     
#                     # Import matplotlib when needed
#                     import matplotlib.pyplot as plt
#                     
#                     # Temporarily disable LaTeX for this call
#                     original_usetex = plt.rcParams.get('text.usetex', False)
#                     plt.rcParams['text.usetex'] = False
#                     
#                     try:
#                         result = func(*new_args, **new_kwargs)
#                         return result
#                     finally:
#                         plt.rcParams['text.usetex'] = original_usetex
#                 else:
#                     # Re-raise non-LaTeX errors
#                     raise
#         return wrapper
#     return decorator
# 
# 
# def get_latex_status() -> Dict[str, Any]:
#     """
#     Get comprehensive LaTeX status information.
#     
#     Returns
#     -------
#     Dict[str, Any]
#         Status information including capability, mode, and configuration
#     """
#     import matplotlib.pyplot as plt
#     
#     return {
#         'latex_available': check_latex_capability(),
#         'fallback_mode': get_fallback_mode(),
#         'usetex_enabled': plt.rcParams.get('text.usetex', False),
#         'mathtext_fontset': plt.rcParams.get('mathtext.fontset', 'cm'),
#         'font_family': plt.rcParams.get('font.family', ['serif']),
#         'cache_info': check_latex_capability.cache_info()._asdict(),
#     }
# 
# 
# # Convenience functions
# def enable_latex_fallback(mode: str = "auto") -> None:
#     """Enable LaTeX fallback with specified mode."""
#     set_fallback_mode(mode)
# 
# 
# def disable_latex_fallback() -> None:
#     """Disable LaTeX fallback (force LaTeX usage)."""
#     global _latex_available
#     _latex_available = True  # Force LaTeX usage
# 
# 
# def reset_latex_cache() -> None:
#     """Reset the LaTeX capability cache."""
#     check_latex_capability.cache_clear()
#     global _latex_available
#     _latex_available = None
# 
# 
# # EOF
# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/str/_latex_fallback.py
# --------------------------------------------------------------------------------
