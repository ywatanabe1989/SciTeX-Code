#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-04 09:40:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/dict/test__listed_dict_enhanced.py

"""Comprehensive tests for listed_dict functionality."""

import pytest
from collections import defaultdict
import random


class TestListedDictEnhanced:
    """Enhanced test suite for listed_dict function."""

    def test_basic_creation_no_keys(self):
        """Test creating listed_dict without predefined keys."""
        from scitex.dict import listed_dict
        
        d = listed_dict()
        
        # Should be a defaultdict with list factory
        assert isinstance(d, defaultdict)
        assert d.default_factory == list
        
        # Should be empty initially
        assert len(d) == 0

    def test_basic_creation_with_keys(self):
        """Test creating listed_dict with predefined keys."""
        from scitex.dict import listed_dict
        
        keys = ['a', 'b', 'c']
        d = listed_dict(keys)
        
        # Should have the specified keys initialized
        assert len(d) == 3
        assert 'a' in d
        assert 'b' in d
        assert 'c' in d
        
        # All values should be empty lists
        assert d['a'] == []
        assert d['b'] == []
        assert d['c'] == []

    def test_dynamic_key_addition(self):
        """Test that new keys can be added dynamically."""
        from scitex.dict import listed_dict
        
        d = listed_dict()
        
        # Add to non-existent key
        d['new_key'].append(1)
        
        assert 'new_key' in d
        assert d['new_key'] == [1]

    def test_list_operations(self):
        """Test various list operations on dictionary values."""
        from scitex.dict import listed_dict
        
        d = listed_dict(['data'])
        
        # Test append
        d['data'].append(1)
        d['data'].append(2)
        assert d['data'] == [1, 2]
        
        # Test extend
        d['data'].extend([3, 4])
        assert d['data'] == [1, 2, 3, 4]
        
        # Test insert
        d['data'].insert(0, 0)
        assert d['data'] == [0, 1, 2, 3, 4]
        
        # Test remove
        d['data'].remove(2)
        assert d['data'] == [0, 1, 3, 4]

    def test_empty_keys_list(self):
        """Test behavior with empty keys list."""
        from scitex.dict import listed_dict
        
        d = listed_dict([])
        
        # Should create empty dict
        assert len(d) == 0
        
        # Should still work as defaultdict
        d['test'].append('value')
        assert d['test'] == ['value']

    def test_none_keys_parameter(self):
        """Test explicit None parameter."""
        from scitex.dict import listed_dict
        
        d = listed_dict(keys=None)
        
        # Should behave same as no parameter
        assert isinstance(d, defaultdict)
        assert len(d) == 0

    def test_duplicate_keys(self):
        """Test behavior with duplicate keys."""
        from scitex.dict import listed_dict
        
        keys = ['a', 'b', 'a', 'c']
        d = listed_dict(keys)
        
        # Should only have unique keys
        assert len(d) == 3
        assert set(d.keys()) == {'a', 'b', 'c'}

    def test_different_key_types(self):
        """Test with different types of keys."""
        from scitex.dict import listed_dict
        
        keys = [1, 'string', (1, 2), frozenset([3, 4])]
        d = listed_dict(keys)
        
        assert len(d) == 4
        for key in keys:
            assert key in d
            assert d[key] == []

    def test_example1_reproduction(self):
        """Test reproduction of example 1 from docstring."""
        from scitex.dict import listed_dict
        
        random.seed(42)
        d = listed_dict()
        
        for _ in range(10):
            d['a'].append(random.randint(0, 10))
        
        # Should have generated the same sequence as in docstring
        expected = [10, 1, 0, 4, 3, 3, 2, 1, 10, 8]
        assert d['a'] == expected

    def test_example2_reproduction(self):
        """Test reproduction of example 2 from docstring."""
        from scitex.dict import listed_dict
        
        random.seed(42)
        keys = ['a', 'b', 'c']
        d = listed_dict(keys)
        
        for _ in range(10):
            d['a'].append(random.randint(0, 10))
            d['b'].append(random.randint(0, 10))
            d['c'].append(random.randint(0, 10))
        
        # Should have generated the same sequences as in docstring
        expected_a = [10, 4, 2, 8, 6, 1, 8, 8, 8, 7]
        expected_b = [1, 3, 1, 1, 0, 3, 9, 3, 6, 9]
        expected_c = [0, 3, 10, 9, 0, 3, 0, 10, 3, 4]
        
        assert d['a'] == expected_a
        assert d['b'] == expected_b
        assert d['c'] == expected_c

    def test_multiple_access_same_key(self):
        """Test multiple accesses to the same key."""
        from scitex.dict import listed_dict
        
        d = listed_dict()
        
        # Multiple accesses should return the same list object
        list1 = d['test']
        list2 = d['test']
        
        assert list1 is list2
        
        # Modifications should be shared
        list1.append(1)
        assert list2 == [1]

    def test_key_initialization_overwrites_existing(self):
        """Test that key initialization overwrites existing values."""
        from scitex.dict import listed_dict
        
        d = listed_dict()
        
        # Add some data
        d['a'].append(1)
        d['b'].append(2)
        
        # Now initialize with keys including 'a'
        d2 = listed_dict(['a', 'c'])
        
        # Original dict should be unaffected
        assert d['a'] == [1]
        assert d['b'] == [2]
        
        # New dict should have empty 'a'
        assert d2['a'] == []
        assert d2['c'] == []

    def test_performance_with_many_keys(self):
        """Test performance with many keys."""
        from scitex.dict import listed_dict
        
        many_keys = [f'key_{i}' for i in range(1000)]
        d = listed_dict(many_keys)
        
        # Should initialize all keys
        assert len(d) == 1000
        
        # All should be empty lists
        for key in many_keys:
            assert d[key] == []

    def test_nested_list_behavior(self):
        """Test behavior with nested lists."""
        from scitex.dict import listed_dict
        
        d = listed_dict(['nested'])
        
        # Add nested lists
        d['nested'].append([1, 2])
        d['nested'].append([3, 4])
        
        assert d['nested'] == [[1, 2], [3, 4]]
        
        # Modify nested list
        d['nested'][0].append(5)
        assert d['nested'] == [[1, 2, 5], [3, 4]]

    def test_serialization_compatibility(self):
        """Test that the dictionary can be serialized."""
        from scitex.dict import listed_dict
        import pickle
        
        d = listed_dict(['a', 'b'])
        d['a'].extend([1, 2, 3])
        d['b'].extend(['x', 'y'])
        
        # Should be pickle-able
        serialized = pickle.dumps(d)
        deserialized = pickle.loads(serialized)
        
        assert deserialized['a'] == [1, 2, 3]
        assert deserialized['b'] == ['x', 'y']

    def test_dict_methods_work(self):
        """Test that standard dict methods work."""
        from scitex.dict import listed_dict
        
        d = listed_dict(['a', 'b', 'c'])
        d['a'].append(1)
        d['b'].append(2)
        
        # Test keys()
        assert set(d.keys()) == {'a', 'b', 'c'}
        
        # Test values()
        values = list(d.values())
        assert [1] in values
        assert [2] in values
        assert [] in values
        
        # Test items()
        items = dict(d.items())
        assert items['a'] == [1]
        assert items['b'] == [2]
        assert items['c'] == []

    def test_clear_and_update(self):
        """Test clear and update operations."""
        from scitex.dict import listed_dict
        
        d = listed_dict(['a', 'b'])
        d['a'].extend([1, 2])
        d['b'].extend([3, 4])
        
        # Test update
        d.update({'c': [5, 6]})
        assert d['c'] == [5, 6]
        
        # Test clear
        d.clear()
        assert len(d) == 0
        
        # Should still work as defaultdict after clear
        d['new'].append(7)
        assert d['new'] == [7]

    def test_copy_behavior(self):
        """Test copying behavior."""
        from scitex.dict import listed_dict
        import copy
        
        d = listed_dict(['a'])
        d['a'].extend([1, 2, 3])
        
        # Shallow copy
        d_copy = copy.copy(d)
        assert d_copy['a'] == [1, 2, 3]
        
        # Modifying original should affect copy (shallow)
        d['a'].append(4)
        assert d_copy['a'] == [1, 2, 3, 4]
        
        # Deep copy
        d_deep = copy.deepcopy(d)
        d['a'].append(5)
        assert d_deep['a'] == [1, 2, 3, 4]  # Should not include 5

    def test_special_characters_in_keys(self):
        """Test with special characters in keys."""
        from scitex.dict import listed_dict
        
        special_keys = ['key with spaces', 'key-with-dashes', 'key.with.dots', 'key_with_underscores']
        d = listed_dict(special_keys)
        
        for key in special_keys:
            assert key in d
            d[key].append(f'value_for_{key}')
            assert len(d[key]) == 1

    def test_memory_efficiency(self):
        """Test that empty lists are not unnecessarily duplicated."""
        from scitex.dict import listed_dict
        
        d = listed_dict(['a', 'b', 'c'])
        
        # All lists should be separate objects
        assert d['a'] is not d['b']
        assert d['b'] is not d['c']
        assert d['a'] is not d['c']


if __name__ == "__main__":
    import os
    pytest.main([os.path.abspath(__file__), "-v"])