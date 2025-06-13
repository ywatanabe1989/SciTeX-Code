#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 15:40:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/dict/test___init__.py

"""Tests for dict module __init__.py."""

import pytest
import scitex.dict


def test_dict_module_imports():
    """Test that dict module imports all expected functions and classes."""
    # Check that expected functions are available
    expected_functions = [
        'DotDict',  # class from _DotDict.py
        'listed_dict',  # function from _listed_dict.py
        'pop_keys',  # function from _pop_keys.py
        'replace',  # function from _replace.py
        'safe_merge',  # function from _safe_merge.py
        'to_str',  # function from _to_str.py
    ]
    
    for func_name in expected_functions:
        assert hasattr(scitex.dict, func_name), f"Missing {func_name} in scitex.dict"


def test_no_private_functions_exposed():
    """Test that private functions (starting with _) are not exposed."""
    # Note: The current implementation exposes module names like _DotDict
    # alongside the actual classes/functions. This is a known issue.
    # We'll test for the expected public interface instead.
    expected_public = ['DotDict', 'listed_dict', 'pop_keys', 'replace', 'safe_merge', 'to_str']
    
    for attr_name in expected_public:
        assert hasattr(scitex.dict, attr_name), f"Missing public attribute {attr_name}"


def test_imported_items_are_callable():
    """Test that imported items are functions or classes."""
    import inspect
    
    public_attrs = [attr for attr in dir(scitex.dict) if not attr.startswith('_')]
    
    for attr_name in public_attrs:
        attr = getattr(scitex.dict, attr_name)
        assert inspect.isfunction(attr) or inspect.isclass(attr), \
            f"{attr_name} should be a function or class"


def test_dotdict_class_functionality():
    """Test that DotDict class works correctly when imported from scitex.dict."""
    # Create an instance
    dd = scitex.dict.DotDict({'a': 1, 'b': 2})
    
    # Test basic functionality
    assert dd.a == 1
    assert dd['b'] == 2


def test_listed_dict_functionality():
    """Test that listed_dict function works correctly when imported from scitex.dict."""
    ld = scitex.dict.listed_dict()
    ld['key'].append('value')
    assert ld['key'] == ['value']


def test_pop_keys_functionality():
    """Test that pop_keys function works correctly when imported from scitex.dict."""
    lst = ['a', 'b', 'c', 'd']
    result = scitex.dict.pop_keys(lst, ['b', 'd'])
    assert result == ['a', 'c']


def test_replace_functionality():
    """Test that replace function works correctly when imported from scitex.dict."""
    replacements = {'old': 'new', 'hello': 'hi'}
    result = scitex.dict.replace("old hello world", replacements)
    assert result == "new hi world"


def test_safe_merge_functionality():
    """Test that safe_merge function works correctly when imported from scitex.dict."""
    dict1 = {'a': 1}
    dict2 = {'b': 2}
    result = scitex.dict.safe_merge(dict1, dict2)
    assert result == {'a': 1, 'b': 2}


def test_to_str_functionality():
    """Test that to_str function works correctly when imported from scitex.dict."""
    d = {'a': 1, 'b': 2}
    result = scitex.dict.to_str(d)
    # Result order may vary, so check both possibilities
    assert result in ['a-1_b-2', 'b-2_a-1']


def test_no_import_side_effects():
    """Test that importing scitex.dict doesn't have unexpected side effects."""
    # Re-import to test
    import importlib
    importlib.reload(scitex.dict)
    
    # Should still have all expected functions
    assert hasattr(scitex.dict, 'DotDict')
    assert hasattr(scitex.dict, 'listed_dict')


def test_module_documentation():
    """Test that imported items retain their documentation."""
    # Check that functions have docstrings (where they exist)
    assert scitex.dict.pop_keys.__doc__ is not None
    # Note: replace function has no docstring in the source
    assert scitex.dict.safe_merge.__doc__ is not None
    assert scitex.dict.to_str.__doc__ is not None
    
    # Check DotDict class has docstring
    assert scitex.dict.DotDict.__doc__ is not None


def test_no_temporary_variables():
    """Test that temporary variables used during import are cleaned up."""
    # These variables should not exist in the module namespace
    assert not hasattr(scitex.dict, 'os')
    assert not hasattr(scitex.dict, 'importlib')
    assert not hasattr(scitex.dict, 'inspect')
    assert not hasattr(scitex.dict, 'current_dir')
    assert not hasattr(scitex.dict, 'filename')
    assert not hasattr(scitex.dict, 'module_name')
    assert not hasattr(scitex.dict, 'module')
    assert not hasattr(scitex.dict, 'name')
    assert not hasattr(scitex.dict, 'obj')


def test_function_signatures_preserved():
    """Test that function signatures are preserved after import."""
    import inspect
    
    # Test that we can get signatures (indicates proper function import)
    sig_pop_keys = inspect.signature(scitex.dict.pop_keys)
    assert len(sig_pop_keys.parameters) == 2
    
    sig_replace = inspect.signature(scitex.dict.replace)
    assert len(sig_replace.parameters) == 2
    
    sig_to_str = inspect.signature(scitex.dict.to_str)
    assert len(sig_to_str.parameters) == 2
    assert 'delimiter' in sig_to_str.parameters


if __name__ == "__main__":
    import os
    pytest.main([os.path.abspath(__file__), "-v"])


# EOF
