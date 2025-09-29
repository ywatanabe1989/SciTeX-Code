#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 15:20:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/dict/test__listed_dict.py

"""Tests for listed_dict function."""

import pytest
from collections import defaultdict
from scitex.dict import listed_dict


def test_listed_dict_no_keys():
    """Test listed_dict without initial keys."""
    d = listed_dict()
    
    # Should be a defaultdict(list)
    assert isinstance(d, defaultdict)
    assert d.default_factory == list
    
    # Should start empty
    assert len(d) == 0
    
    # New keys should create empty lists
    d['new_key'].append(1)
    assert d['new_key'] == [1]
    
    # Multiple appends
    d['key2'].append('a')
    d['key2'].append('b')
    assert d['key2'] == ['a', 'b']


def test_listed_dict_with_keys():
    """Test listed_dict with initial keys."""
    keys = ['a', 'b', 'c']
    d = listed_dict(keys)
    
    # Should have all keys initialized
    assert len(d) == 3
    assert 'a' in d
    assert 'b' in d
    assert 'c' in d
    
    # Each key should have empty list
    assert d['a'] == []
    assert d['b'] == []
    assert d['c'] == []


def test_listed_dict_append_operations():
    """Test append operations on listed_dict."""
    d = listed_dict(['x', 'y'])
    
    # Append to existing keys
    d['x'].append(10)
    d['x'].append(20)
    d['y'].append('hello')
    
    assert d['x'] == [10, 20]
    assert d['y'] == ['hello']
    
    # Append to new key
    d['z'].append(3.14)
    assert d['z'] == [3.14]


def test_listed_dict_mixed_types():
    """Test listed_dict with mixed data types."""
    d = listed_dict()
    
    # Different types in same list
    d['mixed'].append(1)
    d['mixed'].append('string')
    d['mixed'].append([1, 2, 3])
    d['mixed'].append({'nested': 'dict'})
    d['mixed'].append(None)
    
    assert d['mixed'] == [1, 'string', [1, 2, 3], {'nested': 'dict'}, None]


def test_listed_dict_list_operations():
    """Test various list operations on listed_dict values."""
    d = listed_dict(['nums'])
    
    # extend
    d['nums'].extend([1, 2, 3])
    assert d['nums'] == [1, 2, 3]
    
    # insert
    d['nums'].insert(1, 'inserted')
    assert d['nums'] == [1, 'inserted', 2, 3]
    
    # remove
    d['nums'].remove('inserted')
    assert d['nums'] == [1, 2, 3]
    
    # pop
    assert d['nums'].pop() == 3
    assert d['nums'] == [1, 2]


def test_listed_dict_empty_keys_list():
    """Test listed_dict with empty keys list."""
    d = listed_dict([])
    
    # Should create empty defaultdict
    assert isinstance(d, defaultdict)
    assert len(d) == 0
    
    # Should still work as defaultdict
    d['new'].append(42)
    assert d['new'] == [42]


def test_listed_dict_duplicate_keys():
    """Test listed_dict with duplicate keys."""
    keys = ['a', 'b', 'a', 'c', 'b']
    d = listed_dict(keys)
    
    # Should only have unique keys
    assert len(d) == 3
    assert sorted(d.keys()) == ['a', 'b', 'c']
    
    # All should be empty lists
    for key in ['a', 'b', 'c']:
        assert d[key] == []


def test_listed_dict_none_key():
    """Test listed_dict with None in keys."""
    keys = ['a', None, 'b']
    d = listed_dict(keys)
    
    # Should handle None as a key
    assert len(d) == 3
    assert None in d
    assert d[None] == []
    
    # Can append to None key
    d[None].append('none_value')
    assert d[None] == ['none_value']


def test_listed_dict_numeric_keys():
    """Test listed_dict with numeric keys."""
    keys = [1, 2.5, 3]
    d = listed_dict(keys)
    
    assert len(d) == 3
    assert d[1] == []
    assert d[2.5] == []
    assert d[3] == []
    
    # Numeric keys work normally
    d[1].append('one')
    d[2.5].append('two-point-five')
    assert d[1] == ['one']
    assert d[2.5] == ['two-point-five']


def test_listed_dict_iteration():
    """Test iteration over listed_dict."""
    keys = ['first', 'second', 'third']
    d = listed_dict(keys)
    
    # Add some data
    d['first'].extend([1, 2])
    d['second'].append('data')
    
    # Iterate over keys
    collected_keys = list(d.keys())
    assert set(collected_keys) == set(keys)
    
    # Iterate over items
    for key, value in d.items():
        assert isinstance(value, list)


def test_listed_dict_del_operations():
    """Test deletion operations on listed_dict."""
    d = listed_dict(['a', 'b', 'c'])
    
    # Add data
    d['a'].append(1)
    d['b'].extend([2, 3])
    
    # Delete a key
    del d['a']
    assert 'a' not in d
    assert len(d) == 2
    
    # New 'a' key should create new list
    d['a'].append(99)
    assert d['a'] == [99]


def test_listed_dict_copy_behavior():
    """Test copy behavior of listed_dict."""
    d1 = listed_dict(['x'])
    d1['x'].append(1)
    
    # Direct assignment shares reference
    d2 = d1
    d2['x'].append(2)
    assert d1['x'] == [1, 2]  # d1 also changed
    
    # Copy creates new dict but shares list references
    d3 = d1.copy()
    d3['x'].append(3)
    assert d1['x'] == [1, 2, 3]  # d1 also changed
    
    # Deep copy would be needed for full independence
    import copy
    d4 = copy.deepcopy(d1)
    d4['x'].append(4)
    assert d1['x'] == [1, 2, 3]  # d1 unchanged
    assert d4['x'] == [1, 2, 3, 4]


def test_listed_dict_real_world_example():
    """Test real-world usage pattern of listed_dict."""
    # Collecting items by category
    items_by_category = listed_dict(['fruits', 'vegetables', 'dairy'])
    
    # Simulate processing items
    items = [
        ('apple', 'fruits'),
        ('carrot', 'vegetables'),
        ('banana', 'fruits'),
        ('milk', 'dairy'),
        ('lettuce', 'vegetables'),
        ('cheese', 'dairy'),
        ('orange', 'fruits')
    ]
    
    for item, category in items:
        items_by_category[category].append(item)
    
    assert items_by_category['fruits'] == ['apple', 'banana', 'orange']
    assert items_by_category['vegetables'] == ['carrot', 'lettuce']
    assert items_by_category['dairy'] == ['milk', 'cheese']
    
    # Can still add new categories dynamically
    items_by_category['grains'].append('bread')
    assert items_by_category['grains'] == ['bread']

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/dict/_listed_dict.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-02 12:40:01 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/dict/_listed_dict.py
# 
# from collections import defaultdict
# 
# 
# def listed_dict(keys=None):
#     """
#     Example 1:
#         import random
#         random.seed(42)
#         d = listed_dict()
#         for _ in range(10):
#             d['a'].append(random.randint(0, 10))
#         print(d)
#         # defaultdict(<class 'list'>, {'a': [10, 1, 0, 4, 3, 3, 2, 1, 10, 8]})
# 
#     Example 2:
#         import random
#         random.seed(42)
#         keys = ['a', 'b', 'c']
#         d = listed_dict(keys)
#         for _ in range(10):
#             d['a'].append(random.randint(0, 10))
#             d['b'].append(random.randint(0, 10))
#             d['c'].append(random.randint(0, 10))
#         print(d)
#         # defaultdict(<class 'list'>, {'a': [10, 4, 2, 8, 6, 1, 8, 8, 8, 7],
#         #                              'b': [1, 3, 1, 1, 0, 3, 9, 3, 6, 9],
#         #                              'c': [0, 3, 10, 9, 0, 3, 0, 10, 3, 4]})
#     """
#     dict_list = defaultdict(list)
#     # initialize with keys if possible
#     if keys is not None:
#         for k in keys:
#             dict_list[k] = []
#     return dict_list
# 
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/dict/_listed_dict.py
# --------------------------------------------------------------------------------
