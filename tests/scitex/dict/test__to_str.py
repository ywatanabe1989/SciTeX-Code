#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 15:40:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/dict/test__to_str.py

"""Tests for to_str function."""

import pytest
from collections import OrderedDict
from scitex.dict import to_str


def test_to_str_basic():
    """Test basic dictionary to string conversion."""
    # Using OrderedDict to ensure consistent ordering
    d = OrderedDict([('a', 1), ('b', 2), ('c', 3)])
    result = to_str(d)
    assert result == "a-1_b-2_c-3"


def test_to_str_empty_dict():
    """Test conversion of empty dictionary."""
    d = {}
    result = to_str(d)
    assert result == ""


def test_to_str_single_item():
    """Test conversion of single-item dictionary."""
    d = {'key': 'value'}
    result = to_str(d)
    assert result == "key-value"


def test_to_str_custom_delimiter():
    """Test conversion with custom delimiter."""
    d = OrderedDict([('x', 10), ('y', 20)])
    result = to_str(d, delimiter="|")
    assert result == "x-10|y-20"
    
    # Test with longer delimiter
    result = to_str(d, delimiter=" AND ")
    assert result == "x-10 AND y-20"


def test_to_str_numeric_values():
    """Test conversion with various numeric values."""
    d = OrderedDict([
        ('int', 42),
        ('float', 3.14),
        ('negative', -10),
        ('zero', 0)
    ])
    result = to_str(d)
    assert result == "int-42_float-3.14_negative--10_zero-0"


def test_to_str_string_values():
    """Test conversion with string values."""
    d = OrderedDict([
        ('name', 'John'),
        ('city', 'New York'),
        ('empty', '')
    ])
    result = to_str(d)
    assert result == "name-John_city-New York_empty-"


def test_to_str_special_characters():
    """Test conversion with special characters in keys/values."""
    d = OrderedDict([
        ('key-with-dash', 'value'),
        ('key_with_underscore', 'value'),
        ('key', 'value-with-dash')
    ])
    result = to_str(d)
    assert result == "key-with-dash-value_key_with_underscore-value_key-value-with-dash"


def test_to_str_unicode():
    """Test conversion with unicode characters."""
    d = OrderedDict([
        ('Hello', 'World'),
        ('你好', '世界'),
        ('こんにちは', '世界')
    ])
    result = to_str(d)
    assert result == "Hello-World_你好-世界_こんにちは-世界"


def test_to_str_boolean_values():
    """Test conversion with boolean values."""
    d = OrderedDict([('true', True), ('false', False)])
    result = to_str(d)
    assert result == "true-True_false-False"


def test_to_str_none_value():
    """Test conversion with None value."""
    d = {'key': None}
    result = to_str(d)
    assert result == "key-None"


def test_to_str_mixed_types():
    """Test conversion with mixed value types."""
    d = OrderedDict([
        ('str', 'hello'),
        ('int', 123),
        ('float', 45.6),
        ('bool', True),
        ('none', None)
    ])
    result = to_str(d)
    assert result == "str-hello_int-123_float-45.6_bool-True_none-None"


def test_to_str_numeric_keys():
    """Test conversion with numeric keys."""
    d = OrderedDict([(1, 'one'), (2, 'two'), (3, 'three')])
    result = to_str(d)
    assert result == "1-one_2-two_3-three"


def test_to_str_empty_delimiter():
    """Test conversion with empty delimiter."""
    d = OrderedDict([('a', 1), ('b', 2)])
    result = to_str(d, delimiter="")
    assert result == "a-1b-2"


def test_to_str_special_delimiter():
    """Test conversion with special delimiters."""
    d = OrderedDict([('x', 1), ('y', 2)])
    
    # Newline delimiter
    result = to_str(d, delimiter="\n")
    assert result == "x-1\ny-2"
    
    # Tab delimiter
    result = to_str(d, delimiter="\t")
    assert result == "x-1\ty-2"


def test_to_str_complex_values():
    """Test conversion with complex value types (should use string representation)."""
    d = OrderedDict([
        ('list', [1, 2, 3]),
        ('tuple', (4, 5, 6)),
        ('dict', {'nested': 'value'})
    ])
    result = to_str(d)
    assert result == "list-[1, 2, 3]_tuple-(4, 5, 6)_dict-{'nested': 'value'}"


def test_to_str_order_preservation():
    """Test that order is preserved in modern Python (3.7+)."""
    # In Python 3.7+, regular dicts maintain insertion order
    d = {'z': 1, 'y': 2, 'x': 3}
    result = to_str(d)
    # Order should be preserved as z-y-x
    assert result == "z-1_y-2_x-3"


def test_to_str_large_dict():
    """Test conversion of large dictionary."""
    d = OrderedDict((f'key{i}', f'value{i}') for i in range(100))
    result = to_str(d)
    
    # Check length and format
    parts = result.split('_')
    assert len(parts) == 100
    assert parts[0] == 'key0-value0'
    assert parts[99] == 'key99-value99'


def test_to_str_delimiter_in_values():
    """Test when delimiter appears in values."""
    d = OrderedDict([
        ('key1', 'value_with_underscore'),
        ('key2', 'normal_value')
    ])
    result = to_str(d)
    # Delimiter in values should not affect parsing
    assert result == "key1-value_with_underscore_key2-normal_value"


def test_to_str_whitespace_keys_values():
    """Test with whitespace in keys and values."""
    d = OrderedDict([
        (' key ', ' value '),
        ('key\n', 'value\t')
    ])
    result = to_str(d)
    assert result == " key - value _key\n-value\t"


if __name__ == "__main__":
    import os
    pytest.main([os.path.abspath(__file__), "-v"])


# EOF
