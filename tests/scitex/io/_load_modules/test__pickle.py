#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 14:35:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/io/_load_modules/test__pickle.py

"""Tests for pickle file loading functionality.

This module tests the _load_pickle function from scitex.io._load_modules._pickle,
which handles loading pickle files including gzip-compressed pickles.
"""

import os
import tempfile
import pickle
import gzip
import pytest


def test_load_pickle_basic():
    """Test loading a basic pickle file."""
    from scitex.io._load_modules import _load_pickle
    
    # Test various data types
    test_data = {
        'string': 'Hello World',
        'integer': 42,
        'float': 3.14159,
        'list': [1, 2, 3, 4, 5],
        'dict': {'nested': {'key': 'value'}},
        'tuple': (1, 'two', 3.0),
        'set': {1, 2, 3},
        'none': None,
        'bool': True
    }
    
    with tempfile.NamedTemporaryFile(suffix='.pkl', delete=False) as f:
        pickle.dump(test_data, f)
        temp_path = f.name
    
    try:
        loaded_data = _load_pickle(temp_path)
        assert loaded_data == test_data
        assert isinstance(loaded_data, dict)
        assert loaded_data['string'] == 'Hello World'
        assert loaded_data['list'] == [1, 2, 3, 4, 5]
    finally:
        os.unlink(temp_path)


def test_load_pickle_with_pickle_extension():
    """Test loading a file with .pickle extension."""
    from scitex.io._load_modules import _load_pickle
    
    test_data = ['item1', 'item2', 'item3']
    
    with tempfile.NamedTemporaryFile(suffix='.pickle', delete=False) as f:
        pickle.dump(test_data, f)
        temp_path = f.name
    
    try:
        loaded_data = _load_pickle(temp_path)
        assert loaded_data == test_data
    finally:
        os.unlink(temp_path)


def test_load_pickle_compressed():
    """Test loading gzip-compressed pickle files."""
    from scitex.io._load_modules import _load_pickle
    
    # Create a large data structure to benefit from compression
    large_data = {
        f'key_{i}': list(range(100)) for i in range(100)
    }
    
    with tempfile.NamedTemporaryFile(suffix='.pkl.gz', delete=False) as f:
        with gzip.open(f.name, 'wb') as gz:
            pickle.dump(large_data, gz)
        temp_path = f.name
    
    try:
        loaded_data = _load_pickle(temp_path)
        assert loaded_data == large_data
        assert len(loaded_data) == 100
        assert loaded_data['key_50'] == list(range(100))
    finally:
        os.unlink(temp_path)


def test_load_pickle_complex_objects():
    """Test loading pickle with complex Python objects."""
    from scitex.io._load_modules import _load_pickle
    
    # Define a custom class
    class CustomClass:
        def __init__(self, name, value):
            self.name = name
            self.value = value
        
        def __eq__(self, other):
            return self.name == other.name and self.value == other.value
    
    # Create complex data with custom objects
    obj1 = CustomClass("test", 123)
    obj2 = CustomClass("another", 456)
    
    complex_data = {
        'objects': [obj1, obj2],
        'lambda': lambda x: x * 2,  # Note: lambdas may not pickle well
        'nested': {
            'obj': obj1,
            'data': [1, 2, 3]
        }
    }
    
    with tempfile.NamedTemporaryFile(suffix='.pkl', delete=False) as f:
        # Remove lambda for pickling (lambdas don't pickle well)
        data_to_save = {k: v for k, v in complex_data.items() if k != 'lambda'}
        pickle.dump(data_to_save, f)
        temp_path = f.name
    
    try:
        loaded_data = _load_pickle(temp_path)
        assert len(loaded_data['objects']) == 2
        assert loaded_data['objects'][0].name == "test"
        assert loaded_data['objects'][0].value == 123
        assert loaded_data['nested']['obj'] == obj1
    finally:
        os.unlink(temp_path)


def test_load_pickle_invalid_extension():
    """Test that loading non-pickle file raises ValueError."""
    from scitex.io._load_modules import _load_pickle
    
    with pytest.raises(ValueError, match="File must have .pkl, .pickle, or .pkl.gz extension"):
        _load_pickle("test.txt")
    
    with pytest.raises(ValueError, match="File must have .pkl, .pickle, or .pkl.gz extension"):
        _load_pickle("/path/to/file.json")


def test_load_pickle_corrupted_file():
    """Test handling of corrupted pickle files."""
    from scitex.io._load_modules import _load_pickle
    
    # Create a file with invalid pickle data
    with tempfile.NamedTemporaryFile(suffix='.pkl', delete=False) as f:
        f.write(b"This is not valid pickle data")
        temp_path = f.name
    
    try:
        with pytest.raises(pickle.UnpicklingError):
            _load_pickle(temp_path)
    finally:
        os.unlink(temp_path)


def test_load_pickle_nonexistent_file():
    """Test loading a nonexistent file."""
    from scitex.io._load_modules import _load_pickle
    
    with pytest.raises(FileNotFoundError):
        _load_pickle("/nonexistent/path/file.pkl")


def test_load_pickle_numpy_arrays():
    """Test loading pickle containing numpy arrays."""
    from scitex.io._load_modules import _load_pickle
    import numpy as np
    
    # Create data with numpy arrays
    numpy_data = {
        'array_1d': np.array([1, 2, 3, 4, 5]),
        'array_2d': np.random.rand(10, 20),
        'array_3d': np.ones((5, 5, 5)),
        'structured': np.array([(1, 'a'), (2, 'b')], 
                              dtype=[('num', 'i4'), ('char', 'U1')])
    }
    
    with tempfile.NamedTemporaryFile(suffix='.pkl', delete=False) as f:
        pickle.dump(numpy_data, f)
        temp_path = f.name
    
    try:
        loaded_data = _load_pickle(temp_path)
        np.testing.assert_array_equal(loaded_data['array_1d'], numpy_data['array_1d'])
        np.testing.assert_array_almost_equal(loaded_data['array_2d'], numpy_data['array_2d'])
        assert loaded_data['array_3d'].shape == (5, 5, 5)
    finally:
        os.unlink(temp_path)


def test_load_pickle_protocol_versions():
    """Test loading pickles saved with different protocol versions."""
    from scitex.io._load_modules import _load_pickle
    
    test_data = {'protocol_test': True, 'data': [1, 2, 3]}
    
    # Test different pickle protocols (0-5, where 5 is the highest in Python 3.8+)
    for protocol in range(pickle.HIGHEST_PROTOCOL + 1):
        with tempfile.NamedTemporaryFile(suffix='.pkl', delete=False) as f:
            pickle.dump(test_data, f, protocol=protocol)
            temp_path = f.name
        
        try:
            loaded_data = _load_pickle(temp_path)
            assert loaded_data == test_data
        finally:
            os.unlink(temp_path)


if __name__ == "__main__":
    pytest.main([os.path.abspath(__file__), "-v"])
