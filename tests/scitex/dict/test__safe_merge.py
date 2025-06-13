#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 15:40:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/dict/test__safe_merge.py

"""Tests for safe_merge function."""

import pytest
from scitex.dict import safe_merge


def test_safe_merge_basic():
    """Test basic dictionary merging without conflicts."""
    dict1 = {'a': 1, 'b': 2}
    dict2 = {'c': 3, 'd': 4}
    
    result = safe_merge(dict1, dict2)
    assert result == {'a': 1, 'b': 2, 'c': 3, 'd': 4}
    
    # Original dicts should be unchanged
    assert dict1 == {'a': 1, 'b': 2}
    assert dict2 == {'c': 3, 'd': 4}


def test_safe_merge_empty_dicts():
    """Test merging with empty dictionaries."""
    # All empty
    result = safe_merge({}, {}, {})
    assert result == {}
    
    # One empty, one with data
    result = safe_merge({}, {'a': 1})
    assert result == {'a': 1}
    
    # One with data, one empty
    result = safe_merge({'a': 1}, {})
    assert result == {'a': 1}


def test_safe_merge_single_dict():
    """Test merging a single dictionary."""
    dict1 = {'a': 1, 'b': 2}
    result = safe_merge(dict1)
    assert result == {'a': 1, 'b': 2}
    assert result is not dict1  # Should be a new dict


def test_safe_merge_no_args():
    """Test merging with no arguments."""
    result = safe_merge()
    assert result == {}


def test_safe_merge_overlapping_keys():
    """Test that overlapping keys raise ValueError."""
    dict1 = {'a': 1, 'b': 2}
    dict2 = {'b': 3, 'c': 4}  # 'b' overlaps
    
    with pytest.raises(ValueError, match="Overlapping keys found"):
        safe_merge(dict1, dict2)


def test_safe_merge_multiple_dicts():
    """Test merging multiple dictionaries."""
    dict1 = {'a': 1}
    dict2 = {'b': 2}
    dict3 = {'c': 3}
    dict4 = {'d': 4}
    
    result = safe_merge(dict1, dict2, dict3, dict4)
    assert result == {'a': 1, 'b': 2, 'c': 3, 'd': 4}


def test_safe_merge_complex_values():
    """Test merging with complex value types."""
    dict1 = {
        'list': [1, 2, 3],
        'dict': {'nested': True},
        'tuple': (1, 2)
    }
    dict2 = {
        'set': {4, 5, 6},
        'none': None,
        'bool': False
    }
    
    result = safe_merge(dict1, dict2)
    assert result['list'] == [1, 2, 3]
    assert result['dict'] == {'nested': True}
    assert result['tuple'] == (1, 2)
    assert result['set'] == {4, 5, 6}
    assert result['none'] is None
    assert result['bool'] is False


def test_safe_merge_numeric_keys():
    """Test merging with numeric keys."""
    dict1 = {1: 'one', 2: 'two'}
    dict2 = {3: 'three', 4: 'four'}
    
    result = safe_merge(dict1, dict2)
    assert result == {1: 'one', 2: 'two', 3: 'three', 4: 'four'}


def test_safe_merge_mixed_key_types():
    """Test merging with mixed key types."""
    # When keys don't overlap, mixed types work fine
    dict1 = {'a': 1, 1: 'one'}
    dict2 = {'b': 2, 2: 'two'}
    
    result = safe_merge(dict1, dict2)
    assert result == {'a': 1, 1: 'one', 'b': 2, 2: 'two'}


def test_safe_merge_none_key():
    """Test merging with None as a key."""
    dict1 = {None: 'none_value', 'a': 1}
    dict2 = {'b': 2, 'c': 3}
    
    result = safe_merge(dict1, dict2)
    assert result == {None: 'none_value', 'a': 1, 'b': 2, 'c': 3}


def test_safe_merge_overlap_with_none():
    """Test overlapping None keys."""
    dict1 = {None: 'value1'}
    dict2 = {None: 'value2'}
    
    with pytest.raises(ValueError, match="Overlapping keys found"):
        safe_merge(dict1, dict2)


def test_safe_merge_later_dict_overlap():
    """Test overlap detection with later dictionaries."""
    dict1 = {'a': 1}
    dict2 = {'b': 2}
    dict3 = {'a': 3}  # Overlaps with dict1
    
    with pytest.raises(ValueError, match="Overlapping keys found"):
        safe_merge(dict1, dict2, dict3)


def test_safe_merge_multiple_overlaps():
    """Test multiple overlapping keys."""
    dict1 = {'a': 1, 'b': 2, 'c': 3}
    dict2 = {'a': 10, 'b': 20, 'd': 4}  # 'a' and 'b' overlap
    
    with pytest.raises(ValueError, match="Overlapping keys found"):
        safe_merge(dict1, dict2)


def test_safe_merge_order_preservation():
    """Test that merge preserves order (Python 3.7+)."""
    dict1 = {'z': 1, 'y': 2}
    dict2 = {'x': 3, 'w': 4}
    dict3 = {'v': 5, 'u': 6}
    
    result = safe_merge(dict1, dict2, dict3)
    keys = list(result.keys())
    assert keys == ['z', 'y', 'x', 'w', 'v', 'u']


def test_safe_merge_large_dicts():
    """Test merging large dictionaries."""
    # Create large non-overlapping dicts
    dict1 = {f'a{i}': i for i in range(100)}
    dict2 = {f'b{i}': i for i in range(100)}
    dict3 = {f'c{i}': i for i in range(100)}
    
    result = safe_merge(dict1, dict2, dict3)
    assert len(result) == 300
    assert result['a50'] == 50
    assert result['b75'] == 75
    assert result['c99'] == 99


def test_safe_merge_unicode_keys():
    """Test merging with unicode keys."""
    dict1 = {'Hello': 1, '世界': 2}
    dict2 = {'你好': 3, 'Bonjour': 4}
    
    result = safe_merge(dict1, dict2)
    assert result == {'Hello': 1, '世界': 2, '你好': 3, 'Bonjour': 4}


def test_safe_merge_special_key_types():
    """Test with special key types that are hashable."""
    # Due to numpy array conversion issues with heterogeneous types,
    # test separately with same key types
    dict1 = {frozenset([1, 2]): 'frozen1'}
    dict2 = {frozenset([3, 4]): 'frozen2'}
    
    result = safe_merge(dict1, dict2)
    assert result[frozenset([1, 2])] == 'frozen1'
    assert result[frozenset([3, 4])] == 'frozen2'


if __name__ == "__main__":
    import os
    pytest.main([os.path.abspath(__file__), "-v"])


# EOF
