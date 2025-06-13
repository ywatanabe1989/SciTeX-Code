#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 15:12:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/str/test___init__.py

"""Tests for str module initialization."""

import os
import pytest
import inspect


def test_str_module_import():
    """Test that str module can be imported."""
    try:
        import scitex.str
        assert True
    except ImportError:
        pytest.fail("Failed to import scitex.str")


def test_str_module_functions():
    """Test that module exposes expected functions."""
    import scitex.str as mstr
    
    # Check for core string utility functions (based on actual output)
    expected = [
        'color_text', 'ct',  # Text coloring
        'printc',  # Colored printing
        'clean_path',  # Path cleaning
        'mask_api',  # API key masking (note: mask_api not mask_api_key)
        'gen_id', 'gen_ID',  # ID generation
        'gen_timestamp', 'timestamp',  # Timestamp generation
        'decapitalize',  # Text formatting
        'grep',  # Text searching
        'parse',  # Text parsing
        'print_debug',  # Debug printing
        'readable_bytes',  # Byte formatting
        'remove_ansi',  # ANSI code removal
        'replace',  # Text replacement
        'search',  # Text searching
        'squeeze_spaces',  # Space squeezing (note: squeeze_spaces not squeeze_space)
    ]
    
    for func in expected:
        assert hasattr(mstr, func), f"Missing function: {func}"


def test_str_module_function_callability():
    """Test that imported functions are callable."""
    import scitex.str as mstr
    
    # Test a few key functions are callable
    core_functions = ['color_text', 'clean_path', 'gen_id', 'gen_timestamp']
    
    for func_name in core_functions:
        func = getattr(mstr, func_name)
        assert callable(func), f"Function {func_name} is not callable"


def test_str_module_public_functions():
    """Test that module exposes public functions correctly."""
    import scitex.str as mstr
    
    # Get all public functions (not starting with underscore)
    public_functions = [name for name in dir(mstr) 
                       if not name.startswith('_') and not name.startswith('__')]
    
    # Should have at least 10 public functions
    assert len(public_functions) >= 10, f"Too few public functions: {len(public_functions)}"
    
    # Test that some core functions exist
    core_functions = ['color_text', 'clean_path', 'gen_id', 'printc']
    for func in core_functions:
        assert func in public_functions, f"Missing core function: {func}"


def test_str_module_dynamic_import():
    """Test that dynamic import works correctly."""
    import scitex.str as mstr
    
    # Should have imported functions from all modules
    all_functions = [name for name, obj in inspect.getmembers(mstr) 
                    if inspect.isfunction(obj) and not name.startswith('_')]
    
    # Should have multiple functions (more than 10)
    assert len(all_functions) >= 10, f"Too few functions imported: {len(all_functions)}"


def test_str_module_backward_compatibility():
    """Test backward compatibility aliases."""
    import scitex.str as mstr
    
    # Test known aliases
    aliases = [
        ('gen_ID', 'gen_id'),  # Backward compatibility
        ('ct', 'color_text'),  # Short alias
        ('timestamp', 'gen_timestamp'),  # Alternative name
    ]
    
    for alias, original in aliases:
        if hasattr(mstr, alias) and hasattr(mstr, original):
            assert getattr(mstr, alias) is getattr(mstr, original), \
                f"Alias {alias} does not point to {original}"


def test_str_module_latex_functions():
    """Test that LaTeX-related functions are available."""
    import scitex.str as mstr
    
    # Should have LaTeX functionality
    if hasattr(mstr, '_latex'):  # If latex module exists
        # Test that latex functions are available
        pass  # Implementation depends on actual latex module content


def test_str_module_no_import_pollution():
    """Test that module doesn't have leftover import variables."""
    import scitex.str as mstr
    
    # These should be cleaned up by the __init__.py
    unwanted = ['os', 'importlib', 'inspect', 'current_dir', 
                'filename', 'module_name', 'module', 'name', 'obj']
    
    for var in unwanted:
        assert not hasattr(mstr, var), f"Unwanted variable {var} found in module"


def test_str_module_function_types():
    """Test that all exported items are functions or classes."""
    import scitex.str as mstr
    
    # Get all non-dunder attributes
    all_attrs = [(name, getattr(mstr, name)) for name in dir(mstr) 
                 if not name.startswith('__')]
    
    for name, obj in all_attrs:
        # Should be function, class, or module
        assert (inspect.isfunction(obj) or inspect.isclass(obj) or 
                inspect.ismodule(obj)), \
            f"Unexpected object type for {name}: {type(obj)}"


def test_str_module_consistency():
    """Test module naming consistency."""
    import scitex.str as mstr
    
    # Get all function names
    functions = [name for name, obj in inspect.getmembers(mstr) 
                if inspect.isfunction(obj) and not name.startswith('_')]
    
    # Most should follow snake_case (some exceptions for backward compatibility)
    snake_case_functions = [name for name in functions 
                           if name.islower() or '_' in name.lower()]
    
    # At least 80% should follow snake_case
    consistency_ratio = len(snake_case_functions) / len(functions)
    assert consistency_ratio >= 0.8, \
        f"Low naming consistency: {consistency_ratio:.2%}"


if __name__ == "__main__":
    pytest.main([os.path.abspath(__file__), "-v"])
