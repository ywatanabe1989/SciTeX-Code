#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 15:00:00 (ywatanabe)"
# File: ./tests/scitex/decorators/test__combined.py

import pytest
import numpy as np
import pandas as pd
import unittest.mock as mock


def test_combined_torch_batch_fn_exists():
    """Test that torch_batch_fn decorator exists and is callable."""
    from scitex.decorators import torch_batch_fn
    
    assert torch_batch_fn is not None
    assert callable(torch_batch_fn)


def test_combined_numpy_batch_fn_exists():
    """Test that numpy_batch_fn decorator exists and is callable."""
    from scitex.decorators import numpy_batch_fn
    
    assert numpy_batch_fn is not None
    assert callable(numpy_batch_fn)


def test_combined_pandas_batch_fn_exists():
    """Test that pandas_batch_fn decorator exists and is callable."""
    from scitex.decorators import pandas_batch_fn
    
    assert pandas_batch_fn is not None
    assert callable(pandas_batch_fn)


@mock.patch('scitex.decorators._combined.torch_fn')
@mock.patch('scitex.decorators._combined.batch_fn')
def test_combined_torch_batch_fn_decorator_application(mock_batch_fn, mock_torch_fn):
    """Test that torch_batch_fn applies decorators in correct order."""
    from scitex.decorators import torch_batch_fn
    
    # Mock the decorators to return identity functions
    mock_torch_fn.return_value = lambda x: x
    mock_batch_fn.return_value = lambda x: x
    
    @torch_batch_fn
    def dummy_func(x):
        return x
    
    # Verify both decorators were called
    mock_torch_fn.assert_called_once()
    mock_batch_fn.assert_called_once()


@mock.patch('scitex.decorators._combined.numpy_fn')
@mock.patch('scitex.decorators._combined.batch_fn')
def test_combined_numpy_batch_fn_decorator_application(mock_batch_fn, mock_numpy_fn):
    """Test that numpy_batch_fn applies decorators in correct order."""
    from scitex.decorators import numpy_batch_fn
    
    # Mock the decorators to return identity functions
    mock_numpy_fn.return_value = lambda x: x
    mock_batch_fn.return_value = lambda x: x
    
    @numpy_batch_fn
    def dummy_func(x):
        return x
    
    # Verify both decorators were called
    mock_numpy_fn.assert_called_once()
    mock_batch_fn.assert_called_once()


@mock.patch('scitex.decorators._combined.pandas_fn')
@mock.patch('scitex.decorators._combined.batch_fn')
def test_combined_pandas_batch_fn_decorator_application(mock_batch_fn, mock_pandas_fn):
    """Test that pandas_batch_fn applies decorators in correct order."""
    from scitex.decorators import pandas_batch_fn
    
    # Mock the decorators to return identity functions
    mock_pandas_fn.return_value = lambda x: x
    mock_batch_fn.return_value = lambda x: x
    
    @pandas_batch_fn
    def dummy_func(x):
        return x
    
    # Verify both decorators were called
    mock_pandas_fn.assert_called_once()
    mock_batch_fn.assert_called_once()


def test_combined_aliases_exist():
    """Test that decorator aliases exist and reference correct functions."""
    from scitex.decorators import (
        torch_batch_fn, numpy_batch_fn, pandas_batch_fn,
        batch_torch_fn, batch_numpy_fn, batch_pandas_fn
    )
    
    # Test aliases reference the same functions
    assert batch_torch_fn is torch_batch_fn
    assert batch_numpy_fn is numpy_batch_fn
    assert batch_pandas_fn is pandas_batch_fn


def test_combined_function_metadata_preservation():
    """Test that decorators preserve function metadata."""
    from scitex.decorators import torch_batch_fn
    
    @torch_batch_fn
    def test_function(x, y=1):
        """Test function docstring."""
        return x + y
    
    # Test that function name and docstring are preserved
    assert test_function.__name__ == "test_function"
    assert "Test function docstring" in test_function.__doc__


def test_combined_all_exports():
    """Test that __all__ contains expected exports."""
    from scitex.decorators import __all__
    
    expected_exports = [
        'torch_batch_fn',
        'numpy_batch_fn', 
        'pandas_batch_fn',
        'batch_torch_fn',
        'batch_numpy_fn',
        'batch_pandas_fn',
    ]
    
    assert __all__ == expected_exports
    assert len(__all__) == 6


def test_combined_imports_work():
    """Test that all imports from the module work correctly."""
    # Test individual imports
    from scitex.decorators import torch_batch_fn
    from scitex.decorators import numpy_batch_fn
    from scitex.decorators import pandas_batch_fn
    from scitex.decorators import batch_torch_fn
    from scitex.decorators import batch_numpy_fn
    from scitex.decorators import batch_pandas_fn
    
    # Test that they are all callable
    decorators = [
        torch_batch_fn, numpy_batch_fn, pandas_batch_fn,
        batch_torch_fn, batch_numpy_fn, batch_pandas_fn
    ]
    
    for decorator in decorators:
        assert callable(decorator)


@mock.patch('scitex.decorators._combined.torch_fn', side_effect=lambda x: x)
@mock.patch('scitex.decorators._combined.batch_fn', side_effect=lambda x: x)
def test_combined_torch_batch_fn_functionality(mock_batch_fn, mock_torch_fn):
    """Test basic functionality of torch_batch_fn decorated function."""
    from scitex.decorators import torch_batch_fn
    
    @torch_batch_fn
    def simple_function(x):
        return x * 2
    
    # Test that function can be called
    result = simple_function(5)
    assert result == 10


@mock.patch('scitex.decorators._combined.numpy_fn', side_effect=lambda x: x)
@mock.patch('scitex.decorators._combined.batch_fn', side_effect=lambda x: x)
def test_combined_numpy_batch_fn_functionality(mock_batch_fn, mock_numpy_fn):
    """Test basic functionality of numpy_batch_fn decorated function."""
    from scitex.decorators import numpy_batch_fn
    
    @numpy_batch_fn
    def simple_function(x):
        return x * 2
    
    # Test that function can be called
    result = simple_function(5)
    assert result == 10


@mock.patch('scitex.decorators._combined.pandas_fn', side_effect=lambda x: x)
@mock.patch('scitex.decorators._combined.batch_fn', side_effect=lambda x: x)
def test_combined_pandas_batch_fn_functionality(mock_batch_fn, mock_pandas_fn):
    """Test basic functionality of pandas_batch_fn decorated function."""
    from scitex.decorators import pandas_batch_fn
    
    @pandas_batch_fn
    def simple_function(x):
        return x * 2
    
    # Test that function can be called
    result = simple_function(5)
    assert result == 10


def test_combined_decorator_dependencies():
    """Test that required decorator dependencies can be imported."""
    # Test that individual decorators can be imported
    from scitex.decorators import batch_fn
from scitex.decorators import torch_fn
from scitex.decorators import numpy_fn
from scitex.decorators import pandas_fn
    
    # Test that they are callable
    assert callable(batch_fn)
    assert callable(torch_fn)
    assert callable(numpy_fn)
    assert callable(pandas_fn)


def test_combined_wraps_import():
    """Test that functools.wraps is properly imported and used."""
    from functools import wraps
    from typing import Callable
    
    # Test that required imports work
    assert wraps is not None
    assert Callable is not None


if __name__ == "__main__":
    import os
    pytest.main([os.path.abspath(__file__)])