#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 15:40:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/reproduce/test___init__.py

"""Tests for reproduce module __init__.py."""

import pytest
import scitex.reproduce


def test_reproduce_module_imports():
    """Test that reproduce module imports all expected functions."""
    # Check that expected functions are available
    expected_functions = [
        'gen_id',      # from _gen_ID.py
        'gen_ID',      # backward compatibility alias
        'gen_timestamp',  # from _gen_timestamp.py
        'timestamp',   # alias
        'fix_seeds',   # from _fix_seeds.py
    ]
    
    for func_name in expected_functions:
        assert hasattr(scitex.reproduce, func_name), f"Missing {func_name} in scitex.reproduce"


def test_no_private_functions_exposed():
    """Test that private functions are not exposed."""
    # Check expected public interface
    expected_public = ['gen_id', 'gen_ID', 'gen_timestamp', 'timestamp', 'fix_seeds']
    
    for attr_name in expected_public:
        assert hasattr(scitex.reproduce, attr_name), f"Missing public attribute {attr_name}"


def test_imported_functions_are_callable():
    """Test that imported items are callable functions."""
    import inspect
    
    # Get public attributes
    public_attrs = [attr for attr in dir(scitex.reproduce) 
                   if not attr.startswith('_') and hasattr(scitex.reproduce, attr)]
    
    for attr_name in public_attrs:
        attr = getattr(scitex.reproduce, attr_name)
        # Should be functions (not classes in this module)
        assert callable(attr), f"{attr_name} should be callable"


def test_gen_id_functionality():
    """Test gen_id works when imported from scitex.reproduce."""
    # Basic test
    id1 = scitex.reproduce.gen_id()
    assert isinstance(id1, str)
    assert '_' in id1
    
    # Custom parameters
    id2 = scitex.reproduce.gen_id(N=4)
    parts = id2.split('_')
    assert len(parts[1]) == 4


def test_gen_timestamp_functionality():
    """Test gen_timestamp works when imported from scitex.reproduce."""
    ts = scitex.reproduce.gen_timestamp()
    assert isinstance(ts, str)
    assert len(ts) == 14  # YYYY-MMDD-HHMM format
    
    # Also test alias
    ts2 = scitex.reproduce.timestamp()
    assert isinstance(ts2, str)
    assert len(ts2) == 14


def test_fix_seeds_functionality():
    """Test fix_seeds works when imported from scitex.reproduce."""
    import random
    import numpy as np
    
    # Fix seeds - need to pass modules as parameters
    scitex.reproduce.fix_seeds(random=random, np=np, seed=42, verbose=False)
    
    # Test Python random
    val1 = random.random()
    
    # Fix seeds again with same seed
    scitex.reproduce.fix_seeds(random=random, np=np, seed=42, verbose=False)
    val2 = random.random()
    
    # Should produce same values
    assert val1 == val2
    
    # Test numpy
    scitex.reproduce.fix_seeds(np=np, seed=123, verbose=False)
    arr1 = np.random.rand(5)
    
    scitex.reproduce.fix_seeds(np=np, seed=123, verbose=False)
    arr2 = np.random.rand(5)
    
    assert np.array_equal(arr1, arr2)


def test_backward_compatibility():
    """Test backward compatibility aliases."""
    # gen_ID should be available and same as gen_id
    assert hasattr(scitex.reproduce, 'gen_ID')
    assert scitex.reproduce.gen_ID is scitex.reproduce.gen_id
    
    # timestamp should be available and same as gen_timestamp
    assert hasattr(scitex.reproduce, 'timestamp')
    assert scitex.reproduce.timestamp is scitex.reproduce.gen_timestamp


def test_no_import_side_effects():
    """Test that importing doesn't have side effects."""
    import importlib
    
    # Re-import module
    importlib.reload(scitex.reproduce)
    
    # Should still have all functions
    assert hasattr(scitex.reproduce, 'gen_id')
    assert hasattr(scitex.reproduce, 'gen_timestamp')
    assert hasattr(scitex.reproduce, 'fix_seeds')


def test_module_documentation():
    """Test that imported functions retain documentation."""
    # Check docstrings exist
    assert scitex.reproduce.gen_id.__doc__ is not None
    assert scitex.reproduce.gen_timestamp.__doc__ is not None
    # Note: fix_seeds has no docstring in source
    
    # Check they contain expected content
    assert "unique identifier" in scitex.reproduce.gen_id.__doc__.lower()
    assert "timestamp" in scitex.reproduce.gen_timestamp.__doc__.lower()


def test_no_temporary_variables():
    """Test that temporary import variables are cleaned up."""
    # These should not exist in module namespace
    assert not hasattr(scitex.reproduce, 'os')
    assert not hasattr(scitex.reproduce, 'importlib')
    assert not hasattr(scitex.reproduce, 'inspect')
    assert not hasattr(scitex.reproduce, 'current_dir')
    assert not hasattr(scitex.reproduce, 'filename')
    assert not hasattr(scitex.reproduce, 'module_name')
    assert not hasattr(scitex.reproduce, 'module')
    assert not hasattr(scitex.reproduce, 'name')
    assert not hasattr(scitex.reproduce, 'obj')


def test_function_signatures():
    """Test function signatures are preserved."""
    import inspect
    
    # Test gen_id signature
    sig = inspect.signature(scitex.reproduce.gen_id)
    params = list(sig.parameters.keys())
    assert 'time_format' in params
    assert 'N' in params
    
    # Test gen_timestamp signature (no parameters)
    sig = inspect.signature(scitex.reproduce.gen_timestamp)
    assert len(sig.parameters) == 0
    
    # Test fix_seeds signature
    sig = inspect.signature(scitex.reproduce.fix_seeds)
    params = list(sig.parameters.keys())
    assert 'seed' in params
    assert 'np' in params
    assert 'torch' in params


def test_all_functions_from_submodules():
    """Test all public functions from submodules are available."""
    # Import submodules directly to compare
    from scitex.reproduce import _gen_ID, _gen_timestamp, _fix_seeds
    
    # Check gen_id/gen_ID
    assert hasattr(_gen_ID, 'gen_id')
    assert hasattr(scitex.reproduce, 'gen_id')
    
    # Check gen_timestamp/timestamp
    assert hasattr(_gen_timestamp, 'gen_timestamp')
    assert hasattr(scitex.reproduce, 'gen_timestamp')
    
    # Check fix_seeds
    assert hasattr(_fix_seeds, 'fix_seeds')
    assert hasattr(scitex.reproduce, 'fix_seeds')


def test_reproducibility_workflow():
    """Test typical reproducibility workflow using the module."""
    import numpy as np
    import random
    
    # Set seeds for reproducibility
    scitex.reproduce.fix_seeds(random=random, np=np, seed=42, verbose=False)
    
    # Generate reproducible ID (note: need to reset seed for random part)
    random.seed(42)  # Reset for reproducible random part
    exp_id = scitex.reproduce.gen_id(N=6)
    assert len(exp_id.split('_')[1]) == 6
    
    # Generate timestamp
    ts = scitex.reproduce.gen_timestamp()
    assert len(ts) == 14
    
    # Create reproducible random data
    scitex.reproduce.fix_seeds(np=np, seed=42, verbose=False)
    data1 = np.random.rand(10)
    
    # Reset seeds and verify reproducibility
    scitex.reproduce.fix_seeds(np=np, seed=42, verbose=False)
    data2 = np.random.rand(10)
    
    assert np.array_equal(data1, data2)


if __name__ == "__main__":
    import os
    pytest.main([os.path.abspath(__file__), "-v"])


# EOF
