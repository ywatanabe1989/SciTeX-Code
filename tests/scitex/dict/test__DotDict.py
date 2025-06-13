#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 15:15:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/dict/test__DotDict.py

"""Tests for DotDict class."""

import json
import pytest
from scitex.dict import DotDict


def test_dotdict_basic_initialization():
    """Test basic DotDict initialization."""
    # Empty initialization
    dd = DotDict()
    assert len(dd) == 0
    assert list(dd.keys()) == []
    
    # Initialize with dict
    data = {"key1": "value1", "key2": 2}
    dd = DotDict(data)
    assert dd.key1 == "value1"
    assert dd["key2"] == 2
    assert len(dd) == 2


def test_dotdict_invalid_initialization():
    """Test DotDict with invalid initialization."""
    with pytest.raises(TypeError, match="Input must be a dictionary"):
        DotDict("not a dict")
    
    with pytest.raises(TypeError, match="Input must be a dictionary"):
        DotDict([1, 2, 3])


def test_dotdict_attribute_access():
    """Test attribute-style access."""
    dd = DotDict({"name": "test", "value": 42})
    
    # Get
    assert dd.name == "test"
    assert dd.value == 42
    
    # Set
    dd.name = "updated"
    dd.new_attr = "new_value"
    assert dd.name == "updated"
    assert dd.new_attr == "new_value"
    
    # Delete
    del dd.value
    assert "value" not in dd
    with pytest.raises(AttributeError):
        _ = dd.value


def test_dotdict_item_access():
    """Test dictionary-style item access."""
    dd = DotDict()
    
    # Set
    dd["key1"] = "value1"
    dd[100] = "integer key"
    dd["invalid-key"] = "hyphenated"
    
    # Get
    assert dd["key1"] == "value1"
    assert dd[100] == "integer key"
    assert dd["invalid-key"] == "hyphenated"
    
    # Delete
    del dd[100]
    assert 100 not in dd
    with pytest.raises(KeyError):
        _ = dd[100]


def test_dotdict_nested_conversion():
    """Test nested dictionary conversion."""
    data = {
        "level1": {
            "level2": {
                "level3": "deep_value"
            }
        }
    }
    dd = DotDict(data)
    
    # Check nested access
    assert dd.level1.level2.level3 == "deep_value"
    assert isinstance(dd.level1, DotDict)
    assert isinstance(dd.level1.level2, DotDict)
    
    # Update nested
    dd.level1.level2.new_key = "new_value"
    assert dd.level1.level2.new_key == "new_value"


def test_dotdict_integer_keys():
    """Test handling of integer and non-identifier keys."""
    dd = DotDict({
        100: "int_key",
        "valid_key": "string_key",
        "invalid-key": "hyphen",
        "123start": "digit_start"
    })
    
    # Integer keys can only be accessed via item syntax
    assert dd[100] == "int_key"
    assert dd["invalid-key"] == "hyphen"
    assert dd["123start"] == "digit_start"
    
    # Valid identifiers can use both
    assert dd.valid_key == "string_key"
    assert dd["valid_key"] == "string_key"


def test_dotdict_standard_methods():
    """Test standard dictionary methods."""
    dd = DotDict({"a": 1, "b": 2, "c": 3})
    
    # keys, values, items
    assert set(dd.keys()) == {"a", "b", "c"}
    assert set(dd.values()) == {1, 2, 3}
    assert set(dd.items()) == {("a", 1), ("b", 2), ("c", 3)}
    
    # get
    assert dd.get("a") == 1
    assert dd.get("z", "default") == "default"
    
    # pop
    assert dd.pop("b") == 2
    assert "b" not in dd
    assert dd.pop("z", "default") == "default"
    with pytest.raises(KeyError):
        dd.pop("nonexistent")


def test_dotdict_update():
    """Test update method."""
    dd = DotDict({"a": 1})
    
    # Update with dict
    dd.update({"b": 2, "c": 3})
    assert dd.b == 2
    assert dd.c == 3
    
    # Update with iterable
    dd.update([("d", 4), ("e", 5)])
    assert dd.d == 4
    assert dd.e == 5
    
    # Update with nested dict
    dd.update({"nested": {"key": "value"}})
    assert isinstance(dd.nested, DotDict)
    assert dd.nested.key == "value"


def test_dotdict_setdefault():
    """Test setdefault method."""
    dd = DotDict({"a": 1})
    
    # Existing key
    assert dd.setdefault("a", 10) == 1
    assert dd.a == 1
    
    # New key
    assert dd.setdefault("b", 2) == 2
    assert dd.b == 2
    
    # New key with dict value
    dd.setdefault("nested", {"key": "value"})
    assert isinstance(dd.nested, DotDict)


def test_dotdict_contains():
    """Test contains operator."""
    dd = DotDict({"a": 1, 100: "int_key"})
    
    assert "a" in dd
    assert 100 in dd
    assert "nonexistent" not in dd


def test_dotdict_iteration():
    """Test iteration over keys."""
    data = {"a": 1, "b": 2, "c": 3}
    dd = DotDict(data)
    
    keys = list(dd)
    assert set(keys) == set(data.keys())
    
    # Iteration in for loop
    collected = []
    for key in dd:
        collected.append((key, dd[key]))
    assert set(collected) == set(data.items())


def test_dotdict_copy():
    """Test shallow copy."""
    dd = DotDict({"a": 1, "nested": {"b": 2}})
    dd_copy = dd.copy()
    
    # Modify copy
    dd_copy.a = 10
    dd_copy.c = 3
    
    # Original unchanged
    assert dd.a == 1
    assert "c" not in dd
    
    # Shallow copy - nested objects are shared
    dd_copy.nested.b = 20
    assert dd.nested.b == 20  # Changed in original too


def test_dotdict_to_dict():
    """Test conversion back to regular dict."""
    dd = DotDict({
        "a": 1,
        "nested": {"b": 2, "deep": {"c": 3}},
        100: "int_key"
    })
    
    result = dd.to_dict()
    assert isinstance(result, dict)
    assert not isinstance(result, DotDict)
    assert result["a"] == 1
    assert result[100] == "int_key"
    
    # Check nested conversion
    assert isinstance(result["nested"], dict)
    assert not isinstance(result["nested"], DotDict)
    assert result["nested"]["deep"]["c"] == 3


def test_dotdict_string_representation():
    """Test string and repr methods."""
    dd = DotDict({"name": "test", "value": 42})
    
    # repr should show DotDict class
    repr_str = repr(dd)
    assert "DotDict" in repr_str
    assert "'name': 'test'" in repr_str
    
    # str should be JSON format
    str_str = str(dd)
    parsed = json.loads(str_str)
    assert parsed["name"] == "test"
    assert parsed["value"] == 42


def test_dotdict_non_json_serializable():
    """Test handling of non-JSON-serializable values."""
    class CustomObj:
        def __str__(self):
            return "CustomObject"
    
    dd = DotDict({"obj": CustomObj()})
    str_repr = str(dd)
    assert "CustomObject" in str_repr


def test_dotdict_dir():
    """Test dir() for tab completion."""
    dd = DotDict({
        "valid_key": 1,
        "another_key": 2,
        100: "int_key",
        "invalid-key": 3
    })
    
    dir_result = dir(dd)
    
    # Should include valid identifiers
    assert "valid_key" in dir_result
    assert "another_key" in dir_result
    
    # Should include standard methods
    assert "keys" in dir_result
    assert "items" in dir_result
    
    # Should not include non-identifier keys
    assert 100 not in dir_result
    assert "invalid-key" not in dir_result


def test_dotdict_protected_attributes():
    """Test handling of protected attributes."""
    dd = DotDict()
    
    # Should not be able to access _data directly via dot notation
    with pytest.raises(AttributeError):
        _ = dd._nonexistent
    
    # But can set internal attributes
    dd._custom = "value"
    assert dd._custom == "value"


def test_dotdict_edge_cases():
    """Test edge cases and special scenarios."""
    dd = DotDict()
    
    # Empty string key
    dd[""] = "empty"
    assert dd[""] == "empty"
    
    # Keys that conflict with methods
    dd["keys"] = "not_a_method"
    assert dd["keys"] == "not_a_method"
    assert callable(dd.keys)  # Method still accessible
    
    # None as key
    dd[None] = "none_value"
    assert dd[None] == "none_value"
    
    # Complex nested update
    dd.update({
        "level1": {
            "level2": {
                "data": [1, 2, {"nested": "value"}]
            }
        }
    })
    assert dd.level1.level2.data[2]["nested"] == "value"


if __name__ == "__main__":
    import os
    pytest.main([os.path.abspath(__file__), "-v"])


# EOF
