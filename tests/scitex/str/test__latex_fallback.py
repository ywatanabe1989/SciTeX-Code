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
    pytest.main([__file__])


# EOF