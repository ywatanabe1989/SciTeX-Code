#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 16:00:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/tex/test__to_vec.py

"""Tests for to_vec function that converts strings to LaTeX vector notation."""

import pytest
from scitex.tex import to_vec


def test_to_vec_basic():
    """Test basic vector conversion."""
    result = to_vec("AB")
    assert result == r"\overrightarrow{\mathrm{AB}}"


def test_to_vec_single_character():
    """Test with single character vector."""
    result = to_vec("v")
    assert result == r"\overrightarrow{\mathrm{v}}"
    
    result = to_vec("x")
    assert result == r"\overrightarrow{\mathrm{x}}"


def test_to_vec_numeric_string():
    """Test with numeric strings."""
    result = to_vec("12")
    assert result == r"\overrightarrow{\mathrm{12}}"
    
    result = to_vec("0")
    assert result == r"\overrightarrow{\mathrm{0}}"


def test_to_vec_empty_string():
    """Test with empty string."""
    result = to_vec("")
    assert result == r"\overrightarrow{\mathrm{}}"


def test_to_vec_special_characters():
    """Test with special characters that are valid in LaTeX."""
    # Underscores and numbers
    result = to_vec("v_1")
    assert result == r"\overrightarrow{\mathrm{v_1}}"
    
    # Mixed case
    result = to_vec("PQ")
    assert result == r"\overrightarrow{\mathrm{PQ}}"
    
    # With prime
    result = to_vec("A'")
    assert result == r"\overrightarrow{\mathrm{A'}}"


def test_to_vec_long_string():
    """Test with longer vector names."""
    result = to_vec("velocity")
    assert result == r"\overrightarrow{\mathrm{velocity}}"
    
    result = to_vec("F_net")
    assert result == r"\overrightarrow{\mathrm{F_net}}"


def test_to_vec_unicode():
    """Test with unicode characters."""
    # Greek letters as unicode
    result = to_vec("αβ")
    assert result == r"\overrightarrow{\mathrm{αβ}}"
    
    # Math symbols
    result = to_vec("∇φ")
    assert result == r"\overrightarrow{\mathrm{∇φ}}"


def test_to_vec_spaces():
    """Test with strings containing spaces."""
    result = to_vec("A B")
    assert result == r"\overrightarrow{\mathrm{A B}}"
    
    # Leading/trailing spaces
    result = to_vec(" CD ")
    assert result == r"\overrightarrow{\mathrm{ CD }}"


def test_to_vec_latex_special_chars():
    """Test with characters that have special meaning in LaTeX."""
    # These might need escaping in real LaTeX, but function doesn't escape
    result = to_vec("$x$")
    assert result == r"\overrightarrow{\mathrm{$x$}}"
    
    result = to_vec("a&b")
    assert result == r"\overrightarrow{\mathrm{a&b}}"
    
    result = to_vec("x^2")
    assert result == r"\overrightarrow{\mathrm{x^2}}"


def test_to_vec_braces():
    """Test with braces in input."""
    result = to_vec("{AB}")
    assert result == r"\overrightarrow{\mathrm{{AB}}}"
    
    result = to_vec("a{b}c")
    assert result == r"\overrightarrow{\mathrm{a{b}c}}"


def test_to_vec_escape_sequences():
    """Test with escape sequences."""
    # Backslash in input
    result = to_vec(r"\vec")
    assert result == r"\overrightarrow{\mathrm{\vec}}"
    
    # Newline character (literal newline in output)
    result = to_vec("A\nB")
    assert result == "\\overrightarrow{\\mathrm{A\nB}}"


def test_to_vec_repeated_calls():
    """Test that repeated calls produce consistent results."""
    input_str = "XY"
    result1 = to_vec(input_str)
    result2 = to_vec(input_str)
    assert result1 == result2 == r"\overrightarrow{\mathrm{XY}}"


def test_to_vec_type_preservation():
    """Test that function returns string type."""
    result = to_vec("AB")
    assert isinstance(result, str)
    
    # Even with empty input
    result = to_vec("")
    assert isinstance(result, str)


def test_to_vec_examples_from_docstring():
    """Test the example given in the docstring."""
    vector = to_vec("AB")
    assert vector == r"\overrightarrow{\mathrm{AB}}"


def test_to_vec_mathematical_notation():
    """Test with common mathematical vector notations."""
    # Position vectors
    result = to_vec("r")
    assert result == r"\overrightarrow{\mathrm{r}}"
    
    # Force vectors
    result = to_vec("F")
    assert result == r"\overrightarrow{\mathrm{F}}"
    
    # Electric field
    result = to_vec("E")
    assert result == r"\overrightarrow{\mathrm{E}}"
    
    # With subscripts
    result = to_vec("r_0")
    assert result == r"\overrightarrow{\mathrm{r_0}}"


def test_to_vec_raw_string_output():
    """Test that output is valid raw string for LaTeX."""
    result = to_vec("PQ")
    # Check that it contains the expected LaTeX commands
    assert r"\overrightarrow" in result
    assert r"\mathrm" in result
    assert "{PQ}" in result


def test_to_vec_edge_cases():
    """Test edge cases and boundary conditions."""
    # Very long string
    long_str = "A" * 100
    result = to_vec(long_str)
    assert result == rf"\overrightarrow{{\mathrm{{{long_str}}}}}"
    
    # String with only special characters
    result = to_vec("_-_-_")
    assert result == r"\overrightarrow{\mathrm{_-_-_}}"
    
    # Numeric only
    result = to_vec("123456")
    assert result == r"\overrightarrow{\mathrm{123456}}"


def test_to_vec_practical_usage():
    """Test practical usage in LaTeX documents."""
    # Common vector operations
    vec_ab = to_vec("AB")
    vec_bc = to_vec("BC")
    
    # These should be valid LaTeX when used in equations
    assert vec_ab.startswith(r"\overrightarrow")
    assert vec_bc.startswith(r"\overrightarrow")
    
    # Can be concatenated in LaTeX expressions
    latex_expr = f"{vec_ab} + {vec_bc}"
    assert r"\overrightarrow{\mathrm{AB}}" in latex_expr
    assert r"\overrightarrow{\mathrm{BC}}" in latex_expr


if __name__ == "__main__":
    import os
    pytest.main([os.path.abspath(__file__), "-v"])


# EOF
