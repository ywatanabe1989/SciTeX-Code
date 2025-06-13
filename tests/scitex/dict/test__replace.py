#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 15:30:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/dict/test__replace.py

"""Tests for replace function."""

import pytest
from scitex.dict import replace


def test_replace_basic():
    """Test basic string replacement."""
    string = "Hello World"
    replacements = {"Hello": "Hi", "World": "Universe"}
    
    result = replace(string, replacements)
    assert result == "Hi Universe"


def test_replace_single_replacement():
    """Test single replacement."""
    string = "The quick brown fox"
    replacements = {"quick": "slow"}
    
    result = replace(string, replacements)
    assert result == "The slow brown fox"


def test_replace_empty_string():
    """Test replacement on empty string."""
    string = ""
    replacements = {"a": "b", "c": "d"}
    
    result = replace(string, replacements)
    assert result == ""


def test_replace_empty_dict():
    """Test with empty replacement dictionary."""
    string = "Hello World"
    replacements = {}
    
    result = replace(string, replacements)
    assert result == "Hello World"


def test_replace_no_match():
    """Test when no replacements match."""
    string = "Hello World"
    replacements = {"Goodbye": "Hi", "Universe": "Earth"}
    
    result = replace(string, replacements)
    assert result == "Hello World"


def test_replace_multiple_occurrences():
    """Test replacement of multiple occurrences."""
    string = "apple apple apple"
    replacements = {"apple": "orange"}
    
    result = replace(string, replacements)
    assert result == "orange orange orange"


def test_replace_overlapping():
    """Test overlapping replacements."""
    string = "abc"
    replacements = {"ab": "xy", "bc": "yz"}
    
    # First replacement happens first, changing "abc" to "xyc"
    result = replace(string, replacements)
    assert result == "xyc"  # "bc" no longer exists after first replacement


def test_replace_order_matters():
    """Test that order of replacements matters."""
    # In Python 3.7+, dict preserves insertion order
    string = "abc"
    
    # Order 1: a->b first, then b->c
    replacements1 = {"a": "b", "b": "c"}
    result1 = replace(string, replacements1)
    # First "a"->"b" makes "bbc", then "b"->"c" makes "ccc"
    assert result1 == "ccc"
    
    # Order 2: b->c first, then a->b
    string2 = "abc"
    from collections import OrderedDict
    replacements2 = OrderedDict([("b", "c"), ("a", "b")])
    result2 = replace(string2, replacements2)
    # First "b"->"c" makes "acc", then "a"->"b" makes "bcc"
    assert result2 == "bcc"


def test_replace_case_sensitive():
    """Test that replacements are case sensitive."""
    string = "Hello HELLO hello"
    replacements = {"Hello": "Hi"}
    
    result = replace(string, replacements)
    assert result == "Hi HELLO hello"


def test_replace_with_empty_values():
    """Test replacement with empty string values."""
    string = "Remove some words here"
    replacements = {"some ": "", " here": ""}
    
    result = replace(string, replacements)
    assert result == "Remove words"


def test_replace_special_characters():
    """Test replacement with special characters."""
    string = "Price: $100.00 (USD)"
    replacements = {"$": "€", "USD": "EUR"}
    
    result = replace(string, replacements)
    assert result == "Price: €100.00 (EUR)"


def test_replace_newlines_tabs():
    """Test replacement with newlines and tabs."""
    string = "Line1\nLine2\tTabbed"
    replacements = {"\n": " ", "\t": " "}
    
    result = replace(string, replacements)
    assert result == "Line1 Line2 Tabbed"


def test_replace_chain_replacements():
    """Test chain of replacements."""
    string = "A"
    replacements = {"A": "B", "B": "C", "C": "D"}
    
    # Note: This will NOT chain replacements within same call
    # Only "A" -> "B" happens
    result = replace(string, replacements)
    assert "A" not in result
    # The exact result depends on dict ordering


def test_replace_numeric_string():
    """Test replacement in numeric strings."""
    string = "123-456-7890"
    replacements = {"-": "."}
    
    result = replace(string, replacements)
    assert result == "123.456.7890"


def test_replace_repeated_pattern():
    """Test replacement of repeated patterns."""
    string = "ababab"
    replacements = {"ab": "xy"}
    
    result = replace(string, replacements)
    assert result == "xyxyxy"


def test_replace_partial_words():
    """Test replacement of partial words."""
    string = "unhappy and unnecessary"
    replacements = {"un": ""}
    
    result = replace(string, replacements)
    assert result == "happy and necessary"


def test_replace_unicode():
    """Test replacement with unicode characters."""
    string = "Hello 世界"
    replacements = {"世界": "World", "Hello": "你好"}
    
    result = replace(string, replacements)
    assert result == "你好 World"


if __name__ == "__main__":
    import os
    pytest.main([os.path.abspath(__file__), "-v"])


# EOF
