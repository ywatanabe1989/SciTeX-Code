#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-03 07:47:00 (ywatanabe)"
# File: ./tests/scitex/decorators/test__signal_fn.py

import pytest
import numpy as np
import pandas as pd
import torch
import xarray as xr
from unittest.mock import patch, Mock


def test_signal_fn_decorator_basic_functionality():
    """Test basic functionality of signal_fn decorator."""
    from scitex.decorators import signal_fn
    
    @signal_fn
    def dummy_signal_function(signal, param=1.0):
        """Dummy function that adds param to signal."""
        return signal + param
    
    # Test with numpy array
    input_signal = np.array([1.0, 2.0, 3.0])
    result = dummy_signal_function(input_signal, param=0.5)
    
    assert isinstance(result, np.ndarray)
    np.testing.assert_array_almost_equal(result, np.array([1.5, 2.5, 3.5]))


def test_signal_fn_with_different_input_types():
    """Test signal_fn decorator with different input types."""
    from scitex.decorators import signal_fn
    
    @signal_fn
    def identity_function(signal):
        """Return signal as-is."""
        return signal
    
    # Test with list
    input_list = [1.0, 2.0, 3.0]
    result = identity_function(input_list)
    assert isinstance(result, list)
    assert result == input_list
    
    # Test with numpy array
    input_array = np.array([1.0, 2.0, 3.0])
    result = identity_function(input_array)
    assert isinstance(result, np.ndarray)
    np.testing.assert_array_equal(result, input_array)
    
    # Test with pandas DataFrame
    input_df = pd.DataFrame({'col1': [1.0, 2.0], 'col2': [3.0, 4.0]})
    result = identity_function(input_df)
    assert isinstance(result, pd.DataFrame)
    # Note: DataFrame conversion may change column structure, just check values
    np.testing.assert_array_equal(result.values, input_df.values)
    
    # Test with pandas Series
    input_series = pd.Series([1.0, 2.0, 3.0])
    result = identity_function(input_series)
    assert isinstance(result, pd.Series)
    # Note: Series conversion may change dtype, just check values
    np.testing.assert_array_equal(result.values, input_series.values)


def test_signal_fn_with_xarray():
    """Test signal_fn decorator with xarray DataArray."""
    from scitex.decorators import signal_fn
    
    @signal_fn
    def identity_function(signal):
        """Return signal as-is."""
        return signal
    
    # Test with xarray DataArray
    input_xr = xr.DataArray([1.0, 2.0, 3.0], dims=['x'])
    result = identity_function(input_xr)
    assert isinstance(result, xr.DataArray)
    # Note: xarray conversion may change dimension names, just check values
    np.testing.assert_array_equal(result.values, input_xr.values)


def test_signal_fn_preserves_additional_arguments():
    """Test that signal_fn only converts first argument, preserves others."""
    from scitex.decorators import signal_fn
    
    @signal_fn
    def signal_with_params(signal, fs, window_size):
        """Function with signal and non-signal parameters."""
        # Verify that fs and window_size are preserved as original types
        assert isinstance(fs, (int, float))
        assert isinstance(window_size, int)
        return signal * fs / window_size
    
    input_signal = np.array([1.0, 2.0, 3.0])
    fs = 256.0  # sampling frequency
    window_size = 128  # window size
    
    result = signal_with_params(input_signal, fs, window_size)
    
    assert isinstance(result, np.ndarray)
    expected = input_signal * fs / window_size
    np.testing.assert_array_almost_equal(result, expected)


def test_signal_fn_tuple_return():
    """Test signal_fn decorator with tuple return values."""
    from scitex.decorators import signal_fn
    
    @signal_fn
    def function_returning_tuple(signal):
        """Function that returns tuple (signal, metadata)."""
        # Return processed signal and some metadata
        processed_signal = signal * 2
        metadata = {"factor": 2.0}
        return processed_signal, metadata
    
    input_signal = np.array([1.0, 2.0, 3.0])
    result_signal, result_metadata = function_returning_tuple(input_signal)
    
    # Signal should be converted back to numpy
    assert isinstance(result_signal, np.ndarray)
    np.testing.assert_array_almost_equal(result_signal, np.array([2.0, 4.0, 6.0]))
    
    # Metadata should remain unchanged
    assert result_metadata == {"factor": 2.0}


def test_signal_fn_with_empty_args():
    """Test signal_fn decorator with empty arguments."""
    from scitex.decorators import signal_fn
    
    @signal_fn
    def function_no_args():
        """Function with no arguments."""
        return torch.tensor([1.0, 2.0, 3.0])
    
    result = function_no_args()
    # Should return torch tensor since no original object to convert back to
    assert isinstance(result, torch.Tensor)


def test_signal_fn_nested_decorator_detection():
    """Test signal_fn decorator nested decorator detection."""
    from scitex.decorators import signal_fn
    
    # Mock nested decorator context
    with patch('scitex.decorators._signal_fn.is_nested_decorator', return_value=True):
        @signal_fn
        def nested_function(signal):
            return signal
        
        input_signal = np.array([1.0, 2.0, 3.0])
        result = nested_function(input_signal)
        
        # Should bypass conversion when nested
        assert result is input_signal


def test_signal_fn_decorator_attributes():
    """Test that signal_fn decorator sets proper attributes."""
    from scitex.decorators import signal_fn
    
    @signal_fn
    def test_function(signal):
        return signal
    
    # Check decorator attributes
    assert hasattr(test_function, '_is_wrapper')
    assert test_function._is_wrapper is True
    assert hasattr(test_function, '_decorator_type')
    assert test_function._decorator_type == "signal_fn"


def test_signal_fn_with_kwargs():
    """Test signal_fn decorator with keyword arguments."""
    from scitex.decorators import signal_fn
    
    @signal_fn
    def signal_with_kwargs(signal, scale=1.0, offset=0.0):
        """Function with keyword arguments."""
        return signal * scale + offset
    
    input_signal = np.array([1.0, 2.0, 3.0])
    result = signal_with_kwargs(input_signal, scale=2.0, offset=1.0)
    
    assert isinstance(result, np.ndarray)
    expected = input_signal * 2.0 + 1.0
    np.testing.assert_array_almost_equal(result, expected)


def test_signal_fn_torch_tensor_input():
    """Test signal_fn decorator with torch tensor input."""
    from scitex.decorators import signal_fn
    
    @signal_fn
    def torch_identity(signal):
        """Return signal as-is."""
        return signal
    
    input_tensor = torch.tensor([1.0, 2.0, 3.0])
    result = torch_identity(input_tensor)
    
    # Should remain as torch tensor since input was torch tensor
    assert isinstance(result, torch.Tensor)
    torch.testing.assert_close(result, input_tensor)


def test_signal_fn_complex_processing():
    """Test signal_fn decorator with more complex signal processing."""
    from scitex.decorators import signal_fn
    
    @signal_fn
    def complex_processing(signal, multiplier, add_noise=False):
        """Complex processing function."""
        processed = signal * multiplier
        if add_noise:
            noise = torch.randn_like(processed) * 0.01
            processed = processed + noise
        return processed
    
    input_signal = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    result = complex_processing(input_signal, multiplier=2.0, add_noise=False)
    
    assert isinstance(result, np.ndarray)
    expected = input_signal * 2.0
    np.testing.assert_array_almost_equal(result, expected)


def test_signal_fn_error_handling():
    """Test signal_fn decorator error handling."""
    from scitex.decorators import signal_fn
    
    @signal_fn
    def function_with_error(signal):
        """Function that raises an error."""
        raise ValueError("Test error")
    
    input_signal = np.array([1.0, 2.0, 3.0])
    
    # Error should propagate through decorator
    with pytest.raises(ValueError, match="Test error"):
        function_with_error(input_signal)


@patch('scitex.decorators._signal_fn.to_torch')
def test_signal_fn_conversion_mocking(mock_to_torch):
    """Test signal_fn decorator with mocked conversion functions."""
    from scitex.decorators import signal_fn
    
    # Mock the to_torch conversion
    mock_tensor = torch.tensor([1.0, 2.0, 3.0])
    mock_to_torch.return_value = [[mock_tensor]]
    
    @signal_fn
    def mock_function(signal):
        return signal + 1
    
    input_signal = np.array([1.0, 2.0, 3.0])
    result = mock_function(input_signal)
    
    # Verify to_torch was called
    mock_to_torch.assert_called_once()
    
    # Result should be converted back to numpy
    assert isinstance(result, np.ndarray)

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/decorators/_signal_fn.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-05-31 (ywatanabe)"
# # File: /home/ywatanabe/proj/scitex_repo/src/scitex/decorators/_signal_fn.py
# # ----------------------------------------
# import os
# 
# __FILE__ = "./src/scitex/decorators/_signal_fn.py"
# __DIR__ = os.path.dirname(__FILE__)
# # ----------------------------------------
# 
# from functools import wraps
# from typing import Any as _Any
# from typing import Callable
# 
# import numpy as np
# import pandas as pd
# import torch
# import xarray as xr
# 
# from ._converters import _return_always, is_nested_decorator, to_torch
# 
# 
# def signal_fn(func: Callable) -> Callable:
#     """Decorator for signal processing functions that converts only the first argument (signal) to torch tensor.
# 
#     This decorator is designed for DSP functions where:
#     - The first argument is the signal data that should be converted to torch tensor
#     - Other arguments (like sampling frequency, bands, etc.) should remain as-is
#     """
# 
#     @wraps(func)
#     def wrapper(*args: _Any, **kwargs: _Any) -> _Any:
#         # Skip conversion if already in a nested decorator context
#         if is_nested_decorator():
#             results = func(*args, **kwargs)
#             return results
# 
#         # Set the current decorator context
#         wrapper._current_decorator = "signal_fn"
# 
#         # Store original object for type preservation
#         original_object = args[0] if args else None
# 
#         # Convert only the first argument (signal) to torch tensor
#         if args:
#             # Convert first argument to torch
#             converted_first_arg = to_torch(args[0], return_fn=_return_always)[0][0]
# 
#             # Keep other arguments as-is
#             converted_args = (converted_first_arg,) + args[1:]
#         else:
#             converted_args = args
# 
#         results = func(*converted_args, **kwargs)
# 
#         # Convert results back to original input types
#         if isinstance(results, torch.Tensor):
#             if original_object is not None:
#                 if isinstance(original_object, list):
#                     return results.detach().cpu().numpy().tolist()
#                 elif isinstance(original_object, np.ndarray):
#                     return results.detach().cpu().numpy()
#                 elif isinstance(original_object, pd.DataFrame):
#                     return pd.DataFrame(results.detach().cpu().numpy())
#                 elif isinstance(original_object, pd.Series):
#                     return pd.Series(results.detach().cpu().numpy().flatten())
#                 elif isinstance(original_object, xr.DataArray):
#                     return xr.DataArray(results.detach().cpu().numpy())
#             return results
# 
#         # Handle tuple returns (e.g., (signal, frequencies))
#         elif isinstance(results, tuple):
#             converted_results = []
#             for r in results:
#                 if isinstance(r, torch.Tensor):
#                     if original_object is not None and isinstance(
#                         original_object, np.ndarray
#                     ):
#                         converted_results.append(r.detach().cpu().numpy())
#                     else:
#                         converted_results.append(r)
#                 else:
#                     converted_results.append(r)
#             return tuple(converted_results)
# 
#         return results
# 
#     # Mark as a wrapper for detection
#     wrapper._is_wrapper = True
#     wrapper._decorator_type = "signal_fn"
#     return wrapper
# 
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/decorators/_signal_fn.py
# --------------------------------------------------------------------------------
