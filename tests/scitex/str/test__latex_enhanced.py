#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-10 21:00:00 (claude)"
# File: ./tests/scitex/str/test__latex_enhanced.py

"""Enhanced tests for LaTeX string functionality to improve coverage."""

import pytest
import sys
import os

# Mock the _latex_fallback module since it might not be accessible
class MockLatexFallback:
    @staticmethod
    def safe_latex_render(latex_string, fallback_strategy="auto"):
        """Mock implementation that returns the latex string as-is."""
        return latex_string
    
    @staticmethod
    def latex_fallback_decorator(fallback_strategy="auto", preserve_math=True):
        """Mock decorator that does nothing."""
        def decorator(func):
            return func
        return decorator

# Replace the import
sys.modules['scitex.str._latex_fallback'] = MockLatexFallback()

# Now we can safely import
from scitex.str import (
    to_latex_style, 
    add_hat_in_latex_style,
    safe_to_latex_style,
    safe_add_hat_in_latex_style,
    latex_style,  # alias
    hat_latex_style  # alias
)


class TestToLatexStyleEnhanced:
    """Enhanced test suite for to_latex_style function."""
    
    def test_basic_strings(self):
        """Test basic string conversions."""
        assert to_latex_style("x") == "$x$"
        assert to_latex_style("alpha") == "$alpha$"
        assert to_latex_style("theta_1") == "$theta_1$"
        assert to_latex_style("x^2 + y^2") == "$x^2 + y^2$"
    
    def test_numeric_inputs(self):
        """Test various numeric inputs."""
        assert to_latex_style(0) == "$0$"
        assert to_latex_style(1) == "$1$"
        assert to_latex_style(-1) == "$-1$"
        assert to_latex_style(3.14159) == "$3.14159$"
        assert to_latex_style(1e-6) == "$1e-06$"
        assert to_latex_style(float('inf')) == "$inf$"
    
    def test_empty_and_falsy_values(self):
        """Test empty and falsy values."""
        assert to_latex_style("") == ""  # Empty string returns empty
        assert to_latex_style(0) == "$0$"  # Zero is not empty
        assert to_latex_style(None) == ""  # None becomes empty string
        assert to_latex_style(False) == "$False$"  # False is converted to string
    
    def test_already_latex_formatted(self):
        """Test strings already in LaTeX format."""
        assert to_latex_style("$x$") == "$x$"  # Already wrapped
        assert to_latex_style("$x^2$") == "$x^2$"
        assert to_latex_style("$\\alpha + \\beta$") == "$\\alpha + \\beta$"
        assert to_latex_style("$$x$$") == "$$x$$"  # Display math mode
    
    def test_special_latex_commands(self):
        """Test special LaTeX commands."""
        assert to_latex_style("\\frac{1}{2}") == "$\\frac{1}{2}$"
        assert to_latex_style("\\sum_{i=1}^n") == "$\\sum_{i=1}^n$"
        assert to_latex_style("\\int_0^\\infty") == "$\\int_0^\\infty$"
        assert to_latex_style("\\begin{matrix}a&b\\end{matrix}") == "$\\begin{matrix}a&b\\end{matrix}$"
    
    def test_unicode_characters(self):
        """Test with unicode characters."""
        assert to_latex_style("π") == "$π$"
        assert to_latex_style("∑") == "$∑$"
        assert to_latex_style("∫") == "$∫$"
        assert to_latex_style("α β γ") == "$α β γ$"
    
    def test_edge_cases(self):
        """Test edge cases."""
        assert to_latex_style("$") == "$$"  # Single dollar sign
        assert to_latex_style("$$") == "$$$"  # Double dollar sign (not wrapped)
        assert to_latex_style("$x") == "$$x$"  # Incomplete LaTeX
        assert to_latex_style("x$") == "$x$$"  # Incomplete LaTeX
        assert to_latex_style(" ") == "$ $"  # Just space
        assert to_latex_style("\n") == "$\n$"  # Newline
    
    def test_alias_function(self):
        """Test that latex_style alias works."""
        assert latex_style("x") == to_latex_style("x")
        assert latex_style(123) == to_latex_style(123)


class TestAddHatInLatexStyleEnhanced:
    """Enhanced test suite for add_hat_in_latex_style function."""
    
    def test_basic_hat_addition(self):
        """Test basic hat additions."""
        assert add_hat_in_latex_style("x") == "$\\hat{x}$"
        assert add_hat_in_latex_style("y") == "$\\hat{y}$"
        assert add_hat_in_latex_style("theta") == "$\\hat{theta}$"
        assert add_hat_in_latex_style("beta_1") == "$\\hat{beta_1}$"
    
    def test_numeric_hat(self):
        """Test hat on numeric values."""
        assert add_hat_in_latex_style(0) == "$\\hat{0}$"
        assert add_hat_in_latex_style(1) == "$\\hat{1}$"
        assert add_hat_in_latex_style(3.14) == "$\\hat{3.14}$"
        assert add_hat_in_latex_style(-5) == "$\\hat{-5}$"
    
    def test_empty_and_falsy_hat(self):
        """Test hat on empty and falsy values."""
        assert add_hat_in_latex_style("") == ""  # Empty returns empty
        assert add_hat_in_latex_style(0) == "$\\hat{0}$"  # Zero gets hat
        assert add_hat_in_latex_style(None) == ""  # None becomes empty
        assert add_hat_in_latex_style(False) == "$\\hat{False}$"
    
    def test_complex_expressions_hat(self):
        """Test hat on complex expressions."""
        assert add_hat_in_latex_style("x^2") == "$\\hat{x^2}$"
        assert add_hat_in_latex_style("x + y") == "$\\hat{x + y}$"
        assert add_hat_in_latex_style("\\alpha") == "$\\hat{\\alpha}$"
        assert add_hat_in_latex_style("f(x)") == "$\\hat{f(x)}$"
    
    def test_unicode_hat(self):
        """Test hat on unicode characters."""
        assert add_hat_in_latex_style("π") == "$\\hat{π}$"
        assert add_hat_in_latex_style("∑") == "$\\hat{∑}$"
        assert add_hat_in_latex_style("μ") == "$\\hat{μ}$"
    
    def test_alias_function(self):
        """Test that hat_latex_style alias works."""
        assert hat_latex_style("x") == add_hat_in_latex_style("x")
        assert hat_latex_style(123) == add_hat_in_latex_style(123)


class TestSafeLatexFunctions:
    """Test the safe versions with explicit fallback control."""
    
    def test_safe_to_latex_style(self):
        """Test safe_to_latex_style with different strategies."""
        # Test basic functionality
        assert safe_to_latex_style("x") == "$x$"
        assert safe_to_latex_style("alpha", "auto") == "$alpha$"
        assert safe_to_latex_style("beta", "mathtext") == "$beta$"
        assert safe_to_latex_style("gamma", "unicode") == "$gamma$"
        assert safe_to_latex_style("delta", "plain") == "$delta$"
        
        # Test empty handling
        assert safe_to_latex_style("") == ""
        assert safe_to_latex_style(None) == ""
        assert safe_to_latex_style(0) == "$0$"
        
        # Test already formatted
        assert safe_to_latex_style("$x$") == "$x$"
        assert safe_to_latex_style("$x^2$", "auto") == "$x^2$"
    
    def test_safe_add_hat_in_latex_style(self):
        """Test safe_add_hat_in_latex_style with different strategies."""
        # Test basic functionality
        assert safe_add_hat_in_latex_style("x") == "$\\hat{x}$"
        assert safe_add_hat_in_latex_style("alpha", "auto") == "$\\hat{alpha}$"
        assert safe_add_hat_in_latex_style("beta", "mathtext") == "$\\hat{beta}$"
        assert safe_add_hat_in_latex_style("gamma", "unicode") == "$\\hat{gamma}$"
        assert safe_add_hat_in_latex_style("delta", "plain") == "$\\hat{delta}$"
        
        # Test empty handling
        assert safe_add_hat_in_latex_style("") == ""
        assert safe_add_hat_in_latex_style(None) == ""
        assert safe_add_hat_in_latex_style(0) == "$\\hat{0}$"
        
        # Test numeric
        assert safe_add_hat_in_latex_style(42, "auto") == "$\\hat{42}$"


class TestLatexIntegration:
    """Test integration between different LaTeX functions."""
    
    def test_function_consistency(self):
        """Test that functions are consistent with each other."""
        # Regular and safe versions should match with default strategy
        assert to_latex_style("x") == safe_to_latex_style("x")
        assert add_hat_in_latex_style("y") == safe_add_hat_in_latex_style("y")
        
        # Aliases should match originals
        assert latex_style("z") == to_latex_style("z")
        assert hat_latex_style("w") == add_hat_in_latex_style("w")
    
    def test_nested_operations(self):
        """Test nested LaTeX operations."""
        # Apply to_latex_style to already hatted expression
        hatted = add_hat_in_latex_style("x")
        assert to_latex_style(hatted) == hatted  # Should not double-wrap
        
        # Create complex expression
        expr = "x + y"
        latex_expr = to_latex_style(expr)
        assert latex_expr == "$x + y$"
        
        # Hat the whole expression
        hat_expr = add_hat_in_latex_style(expr)
        assert hat_expr == "$\\hat{x + y}$"
    
    @pytest.mark.parametrize("input_val,expected_latex,expected_hat", [
        ("x", "$x$", "$\\hat{x}$"),
        ("alpha", "$alpha$", "$\\hat{alpha}$"),
        (123, "$123$", "$\\hat{123}$"),
        ("", "", ""),
        (0, "$0$", "$\\hat{0}$"),
        ("$y$", "$y$", "$\\hat{$y$}$"),  # Note: This might not be ideal behavior
    ])
    def test_parametrized_operations(self, input_val, expected_latex, expected_hat):
        """Parametrized test for both operations."""
        assert to_latex_style(input_val) == expected_latex
        assert add_hat_in_latex_style(input_val) == expected_hat


class TestLatexEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_very_long_strings(self):
        """Test with very long strings."""
        long_str = "x" * 1000
        assert to_latex_style(long_str) == f"${long_str}$"
        assert add_hat_in_latex_style(long_str) == f"$\\hat{{{long_str}}}$"
    
    def test_special_characters(self):
        """Test with special characters that might break LaTeX."""
        special_chars = r"{}[]()&%#_"
        assert to_latex_style(special_chars) == f"${special_chars}$"
        assert add_hat_in_latex_style(special_chars) == f"$\\hat{{{special_chars}}}$"
    
    def test_multiline_strings(self):
        """Test with multiline strings."""
        multiline = "line1\nline2\nline3"
        assert to_latex_style(multiline) == f"${multiline}$"
        assert add_hat_in_latex_style(multiline) == f"$\\hat{{{multiline}}}$"
    
    def test_mixed_content(self):
        """Test with mixed LaTeX and regular content."""
        mixed = "normal text $latex$ more text"
        assert to_latex_style(mixed) == f"${mixed}$"
        
        # Test partial LaTeX
        partial = "$incomplete"
        assert to_latex_style(partial) == f"${partial}$"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])