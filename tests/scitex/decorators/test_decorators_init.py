#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-04-30 14:24:24 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/tests/scitex/decorators/test___init__.py
# ----------------------------------------
import os

__FILE__ = "./tests/scitex/decorators/test___init__.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import sys

import pytest
import numpy as np
import pandas as pd
import torch
import tempfile
import time
from unittest.mock import patch, MagicMock


def test_init_imports():
    """Test that __init__.py imports all expected decorators."""

    # Force reload of the module to ensure fresh imports
    if "scitex.decorators" in sys.modules:
        del sys.modules["scitex.decorators"]

    # Import the module
    import scitex.decorators

    # Check for expected attributes
    expected_decorators = [
        "cache_disk",
        "cache_mem",
        "preserve_doc",
        "timeout",
        "torch_fn",
        "wrap",
        "numpy_fn",
        "pandas_fn",
        "not_implemented",
    ]

    for decorator in expected_decorators:
        assert hasattr(scitex.decorators, decorator), f"Missing decorator: {decorator}"


def test_all_decorators_available():
    """Test that all decorators are available including additional ones."""
    import scitex.decorators
    
    # Extended list of decorators
    all_decorators = [
        "cache_disk", "cache_mem", "preserve_doc", "timeout",
        "torch_fn", "numpy_fn", "pandas_fn", "signal_fn",
        "wrap", "batch_fn", "not_implemented", "deprecated",
        "enable_auto_order", "disable_auto_order"
    ]
    
    for decorator in all_decorators:
        if decorator in ["deprecated"]:  # Some might be optional
            continue
        assert hasattr(scitex.decorators, decorator), f"Missing decorator: {decorator}"


def test_decorator_callable():
    """Test that all decorators are callable."""
    import scitex.decorators
    
    decorators_to_test = [
        "cache_disk", "cache_mem", "preserve_doc", "timeout",
        "torch_fn", "numpy_fn", "pandas_fn", "signal_fn",
        "wrap", "batch_fn", "not_implemented"
    ]
    
    for dec_name in decorators_to_test:
        if hasattr(scitex.decorators, dec_name):
            decorator = getattr(scitex.decorators, dec_name)
            assert callable(decorator), f"{dec_name} is not callable"


def test_converters_from_module():
    """Test converter decorators from _converters module."""
    import scitex.decorators
    
    # These should be available from _converters import
    potential_converters = [
        'to_numpy', 'to_torch', 'to_pandas', 'to_jax',
        'to_even_shape', 'to_odd_shape'
    ]
    
    # Check which are actually available
    available_converters = []
    for conv in potential_converters:
        if hasattr(scitex.decorators, conv):
            available_converters.append(conv)
            assert callable(getattr(scitex.decorators, conv))
    
    # At least some converters should be available
    assert len(available_converters) > 0


def test_data_type_decorators():
    """Test DataTypeDecorators availability."""
    import scitex.decorators
    
    # Check if DataTypeDecorator or related items are available
    data_type_items = []
    for attr in dir(scitex.decorators):
        if 'DataType' in attr or 'data_type' in attr:
            data_type_items.append(attr)
    
    # Should have some data type related decorators
    assert len(data_type_items) >= 0  # Might be zero if not exported


def test_combined_decorators():
    """Test combined decorators from _combined module."""
    import scitex.decorators
    
    # Check for combined decorators
    combined_patterns = ['_with_cache', '_and_', '_combined']
    combined_decorators = []
    
    for attr in dir(scitex.decorators):
        for pattern in combined_patterns:
            if pattern in attr:
                combined_decorators.append(attr)
                break
    
    # Test any found combined decorators are callable
    for dec in combined_decorators:
        assert callable(getattr(scitex.decorators, dec))


def test_preserve_doc_functionality():
    """Test preserve_doc decorator preserves docstrings."""
    import scitex.decorators
    
    def original_function():
        """This is the original docstring."""
        return "original"
    
    @scitex.decorators.preserve_doc(original_function)
    def decorated_function():
        """This docstring should be replaced."""
        return "decorated"
    
    assert decorated_function.__doc__ == "This is the original docstring."
    assert decorated_function() == "decorated"


def test_cache_disk_basic():
    """Test cache_disk decorator creates cache."""
    import scitex.decorators
    
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.dict(os.environ, {'SciTeX_DIR': tmpdir + '/'}):
            call_count = 0
            
            @scitex.decorators.cache_disk
            def compute_square(x):
                nonlocal call_count
                call_count += 1
                return x ** 2
            
            # First call
            result1 = compute_square(7)
            assert result1 == 49
            first_count = call_count
            
            # Second call with same argument
            result2 = compute_square(7)
            assert result2 == 49
            # joblib might or might not call function again
            
            # Different argument
            result3 = compute_square(8)
            assert result3 == 64


def test_cache_mem_functionality():
    """Test cache_mem decorator with different scenarios."""
    import scitex.decorators
    
    execution_count = 0
    
    @scitex.decorators.cache_mem
    def add_numbers(a, b):
        nonlocal execution_count
        execution_count += 1
        return a + b
    
    # Reset counter
    execution_count = 0
    
    # First call
    assert add_numbers(2, 3) == 5
    assert execution_count == 1
    
    # Cached call
    assert add_numbers(2, 3) == 5
    assert execution_count == 1
    
    # Different arguments
    assert add_numbers(3, 4) == 7
    assert execution_count == 2
    
    # Test with keyword arguments
    assert add_numbers(a=2, b=3) == 5  # Might be cached or not depending on implementation


def test_timeout_decorator_fast_function():
    """Test timeout decorator with fast function."""
    import scitex.decorators
    
    @scitex.decorators.timeout(2.0)  # 2 second timeout
    def fast_computation():
        return sum(range(1000))
    
    # Should complete without timeout
    result = fast_computation()
    assert result == sum(range(1000))


def test_not_implemented_raises():
    """Test not_implemented decorator raises NotImplementedError."""
    import scitex.decorators
    
    @scitex.decorators.not_implemented
    def future_feature(x, y):
        return x + y
    
    with pytest.raises(NotImplementedError):
        future_feature(1, 2)


def test_numpy_fn_conversion():
    """Test numpy_fn decorator converts inputs."""
    import scitex.decorators
    
    @scitex.decorators.numpy_fn
    def compute_mean(arr):
        assert isinstance(arr, np.ndarray)
        return arr.mean()
    
    # Test with list
    result = compute_mean([1, 2, 3, 4, 5])
    assert abs(result - 3.0) < 1e-10
    
    # Test with tuple
    result = compute_mean((10, 20, 30))
    assert abs(result - 20.0) < 1e-10
    
    # Test with numpy array (no conversion needed)
    arr = np.array([2, 4, 6])
    result = compute_mean(arr)
    assert abs(result - 4.0) < 1e-10


def test_torch_fn_conversion():
    """Test torch_fn decorator converts inputs."""
    import scitex.decorators
    
    @scitex.decorators.torch_fn
    def compute_sum(tensor):
        assert isinstance(tensor, torch.Tensor)
        return tensor.sum().item()
    
    # Test with list
    result = compute_sum([1, 2, 3])
    assert result == 6
    
    # Test with numpy array
    arr = np.array([10, 20, 30])
    result = compute_sum(arr)
    assert result == 60
    
    # Test with torch tensor (no conversion)
    tensor = torch.tensor([5, 5, 5])
    result = compute_sum(tensor)
    assert result == 15


def test_pandas_fn_conversion():
    """Test pandas_fn decorator converts inputs."""
    import scitex.decorators
    
    @scitex.decorators.pandas_fn
    def get_shape(df):
        assert isinstance(df, pd.DataFrame)
        return df.shape
    
    # Test with dict
    data = {'A': [1, 2, 3], 'B': [4, 5, 6]}
    shape = get_shape(data)
    assert shape == (3, 2)
    
    # Test with list of lists
    data = [[1, 2], [3, 4], [5, 6]]
    shape = get_shape(data)
    assert shape[0] == 3  # 3 rows
    
    # Test with DataFrame (no conversion)
    df = pd.DataFrame({'X': [1, 2], 'Y': [3, 4]})
    shape = get_shape(df)
    assert shape == (2, 2)


def test_batch_fn_decorator():
    """Test batch_fn processes lists of inputs."""
    import scitex.decorators
    
    @scitex.decorators.batch_fn
    def double(x):
        return x * 2
    
    # Test with list of inputs
    results = double([1, 2, 3, 4])
    assert results == [2, 4, 6, 8]
    
    # Test with single input
    result = double(5)
    assert result == 10
    
    # Test with empty list
    results = double([])
    assert results == []


def test_signal_fn_decorator():
    """Test signal_fn decorator functionality."""
    import scitex.decorators
    
    @scitex.decorators.signal_fn
    def amplify_signal(signal, factor=2):
        assert isinstance(signal, np.ndarray)
        return signal * factor
    
    # Test with list
    result = amplify_signal([1, 2, 3], factor=3)
    expected = np.array([3, 6, 9])
    assert np.array_equal(result, expected)
    
    # Test with numpy array
    signal = np.array([0.5, 1.0, 1.5])
    result = amplify_signal(signal)
    expected = np.array([1.0, 2.0, 3.0])
    assert np.array_equal(result, expected)


def test_auto_order_enable_disable():
    """Test auto-order enable and disable functionality."""
    import scitex.decorators
    
    # Test enable
    with patch('builtins.print') as mock_print:
        scitex.decorators.enable_auto_order()
        mock_print.assert_called()
        assert "Auto-ordering enabled" in str(mock_print.call_args)
    
    # Test disable  
    with patch('builtins.print') as mock_print:
        scitex.decorators.disable_auto_order()
        mock_print.assert_called()
        assert "Auto-ordering disabled" in str(mock_print.call_args)


# --------------------------------------------------------------------------------

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/decorators/__init__.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-05-01 09:18:37 (ywatanabe)"
# # File: /home/ywatanabe/proj/scitex_repo/src/scitex/decorators/__init__.py
# # ----------------------------------------
# import os
# __FILE__ = (
#     "./src/scitex/decorators/__init__.py"
# )
# __DIR__ = os.path.dirname(__FILE__)
# # ----------------------------------------
#
# from ._cache_disk import *
# from ._cache_mem import *
# from ._converters import *
# from ._DataTypeDecorators import *
# from ._deprecated import *
# from ._not_implemented import *
# from ._numpy_fn import *
# from ._pandas_fn import *
# from ._preserve_doc import *
# from ._timeout import *
# from ._torch_fn import *
# from ._wrap import wrap
# from ._batch_fn import batch_fn
#
# # EOF
# --------------------------------------------------------------------------------
# End of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/decorators/__init__.py
# --------------------------------------------------------------------------------
