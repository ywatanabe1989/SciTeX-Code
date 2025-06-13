#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-10 19:10:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/decorators/test__converters_comprehensive.py

"""Comprehensive tests for data type converter functions."""

import os
import warnings
from unittest.mock import MagicMock, Mock, patch

import numpy as np
import pandas as pd
import pytest
import torch
import xarray as xr


class TestConversionWarning:
    """Test cases for ConversionWarning class."""
    
    def test_import(self):
        """Test that ConversionWarning can be imported."""
from scitex.decorators import ConversionWarning
        assert issubclass(ConversionWarning, UserWarning)
    
    def test_warning_raised(self):
        """Test that ConversionWarning can be raised."""
from scitex.decorators import ConversionWarning
        
        with pytest.warns(ConversionWarning):
            warnings.warn("Test warning", ConversionWarning)


class TestCachedWarning:
    """Test cases for _cached_warning function."""
    
    def test_cached_warning_basic(self):
        """Test basic cached warning functionality."""
from scitex.decorators import _cached_warning
        
        with pytest.warns(UserWarning):
            _cached_warning("Test message")
    
    def test_cached_warning_caching(self):
        """Test that warnings are cached."""
from scitex.decorators import _cached_warning
        
        # Clear cache
        _cached_warning.cache_clear()
        
        # First call should warn
        with pytest.warns(UserWarning):
            _cached_warning("Cached message")
        
        # Subsequent calls with same message should use cache
        # (warning still raised due to warning configuration)
        with pytest.warns(UserWarning):
            _cached_warning("Cached message")


class TestConversionWarningFunction:
    """Test cases for _conversion_warning function."""
    
    def test_conversion_warning_numpy_to_torch(self):
        """Test conversion warning from numpy to torch."""
from scitex.decorators import _conversion_warning
        
        old = np.array([1, 2, 3])
        new = torch.tensor([1, 2, 3])
        
        with pytest.warns(UserWarning) as record:
            _conversion_warning(old, new)
        
        assert "ndarray to Tensor" in str(record[0].message)
        assert "cpu" in str(record[0].message)
    
    @pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
    def test_conversion_warning_cuda(self):
        """Test conversion warning with CUDA tensor."""
from scitex.decorators import _conversion_warning
        
        old = np.array([1, 2, 3])
        new = torch.tensor([1, 2, 3]).cuda()
        
        with pytest.warns(UserWarning) as record:
            _conversion_warning(old, new)
        
        assert "cuda" in str(record[0].message)


class TestTryDevice:
    """Test cases for _try_device function."""
    
    def test_try_device_cpu_to_cpu(self):
        """Test moving CPU tensor to CPU (no-op)."""
from scitex.decorators import _try_device
        
        tensor = torch.tensor([1, 2, 3])
        result = _try_device(tensor, "cpu")
        
        assert result.device.type == "cpu"
        assert torch.equal(result, tensor)
    
    @pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
    def test_try_device_cpu_to_cuda(self):
        """Test moving CPU tensor to CUDA."""
from scitex.decorators import _try_device
        
        tensor = torch.tensor([1, 2, 3])
        result = _try_device(tensor, "cuda")
        
        assert result.device.type == "cuda"
        assert torch.equal(result.cpu(), tensor)
    
    @pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
    def test_try_device_cuda_to_cuda(self):
        """Test moving CUDA tensor to CUDA (no-op)."""
from scitex.decorators import _try_device
        
        tensor = torch.tensor([1, 2, 3]).cuda()
        result = _try_device(tensor, "cuda")
        
        assert result.device.type == "cuda"
        assert result is tensor  # Should be same object
    
    def test_try_device_non_tensor(self):
        """Test _try_device with non-tensor input."""
from scitex.decorators import _try_device
        
        data = [1, 2, 3]
        result = _try_device(data, "cuda")
        
        assert result is data  # Should return unchanged
    
    @patch('torch.Tensor.to')
    def test_try_device_cuda_oom(self, mock_to):
        """Test handling of CUDA out of memory error."""
from scitex.decorators import _try_device
        
        # Mock CUDA OOM error
        mock_to.side_effect = RuntimeError("CUDA out of memory")
        
        tensor = torch.tensor([1, 2, 3])
        
        with pytest.warns(UserWarning, match="CUDA memory insufficient"):
            result = _try_device(tensor, "cuda")
        
        assert result.device.type == "cpu"


class TestIsTorch:
    """Test cases for is_torch function."""
    
    def test_is_torch_with_tensor(self):
        """Test is_torch with torch tensor."""
from scitex.decorators import is_torch
        
        tensor = torch.tensor([1, 2, 3])
        assert is_torch(tensor) is True
    
    def test_is_torch_with_numpy(self):
        """Test is_torch with numpy array."""
from scitex.decorators import is_torch
        
        array = np.array([1, 2, 3])
        assert is_torch(array) is False
    
    def test_is_torch_with_mixed_args(self):
        """Test is_torch with mixed arguments."""
from scitex.decorators import is_torch
        
        tensor = torch.tensor([1, 2, 3])
        array = np.array([4, 5, 6])
        
        assert is_torch(array, tensor) is True
        assert is_torch(array, array) is False
    
    def test_is_torch_with_kwargs(self):
        """Test is_torch with keyword arguments."""
from scitex.decorators import is_torch
        
        tensor = torch.tensor([1, 2, 3])
        array = np.array([4, 5, 6])
        
        assert is_torch(data=tensor) is True
        assert is_torch(x=array, y=tensor) is True
        assert is_torch(x=array, y=array) is False
    
    def test_is_torch_empty(self):
        """Test is_torch with no arguments."""
from scitex.decorators import is_torch
        
        assert is_torch() is False


class TestIsCuda:
    """Test cases for is_cuda function."""
    
    @pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
    def test_is_cuda_with_cuda_tensor(self):
        """Test is_cuda with CUDA tensor."""
from scitex.decorators import is_cuda
        
        tensor = torch.tensor([1, 2, 3]).cuda()
        assert is_cuda(tensor) is True
    
    def test_is_cuda_with_cpu_tensor(self):
        """Test is_cuda with CPU tensor."""
from scitex.decorators import is_cuda
        
        tensor = torch.tensor([1, 2, 3])
        assert is_cuda(tensor) is False
    
    def test_is_cuda_with_non_tensor(self):
        """Test is_cuda with non-tensor."""
from scitex.decorators import is_cuda
        
        array = np.array([1, 2, 3])
        assert is_cuda(array) is False
    
    @pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
    def test_is_cuda_with_kwargs(self):
        """Test is_cuda with keyword arguments."""
from scitex.decorators import is_cuda
        
        cuda_tensor = torch.tensor([1, 2, 3]).cuda()
        cpu_tensor = torch.tensor([4, 5, 6])
        
        assert is_cuda(x=cuda_tensor) is True
        assert is_cuda(x=cpu_tensor, y=cuda_tensor) is True
        assert is_cuda(x=cpu_tensor, y=cpu_tensor) is False


class TestReturnFunctions:
    """Test cases for _return_always and _return_if functions."""
    
    def test_return_always(self):
        """Test _return_always function."""
from scitex.decorators import _return_always
        
        args = (1, 2, 3)
        kwargs = {"a": 4, "b": 5}
        
        result = _return_always(*args, **kwargs)
        assert result == (args, kwargs)
        
        # Test with empty inputs
        result = _return_always()
        assert result == ((), {})
    
    def test_return_if_both(self):
        """Test _return_if with both args and kwargs."""
from scitex.decorators import _return_if
        
        args = (1, 2, 3)
        kwargs = {"a": 4, "b": 5}
        
        result = _return_if(*args, **kwargs)
        assert result == (args, kwargs)
    
    def test_return_if_args_only(self):
        """Test _return_if with args only."""
from scitex.decorators import _return_if
        
        args = (1, 2, 3)
        
        result = _return_if(*args)
        assert result == args
    
    def test_return_if_kwargs_only(self):
        """Test _return_if with kwargs only."""
from scitex.decorators import _return_if
        
        kwargs = {"a": 4, "b": 5}
        
        result = _return_if(**kwargs)
        assert result == kwargs
    
    def test_return_if_empty(self):
        """Test _return_if with no inputs."""
from scitex.decorators import _return_if
        
        result = _return_if()
        assert result is None


class TestToTorch:
    """Test cases for to_torch function."""
    
    def test_to_torch_numpy_array(self):
        """Test converting numpy array to torch tensor."""
from scitex.decorators import to_torch
        
        array = np.array([1, 2, 3])
        result = to_torch(array)
        
        assert isinstance(result[0], torch.Tensor)
        assert torch.equal(result[0], torch.tensor([1.0, 2.0, 3.0]))
    
    def test_to_torch_list(self):
        """Test converting list to torch tensor."""
from scitex.decorators import to_torch
        
        data = [1, 2, 3]
        result = to_torch(data)
        
        assert isinstance(result[0], torch.Tensor)
        assert result[0].dtype == torch.float32
    
    def test_to_torch_pandas_series(self):
        """Test converting pandas Series to torch tensor."""
from scitex.decorators import to_torch
        
        series = pd.Series([1, 2, 3])
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = to_torch(series)
        
        assert isinstance(result[0], torch.Tensor)
        assert result[0].shape == (3,)
    
    def test_to_torch_pandas_dataframe(self):
        """Test converting pandas DataFrame to torch tensor."""
from scitex.decorators import to_torch
        
        df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = to_torch(df)
        
        assert isinstance(result[0], torch.Tensor)
        assert result[0].shape == (3, 2)
    
    def test_to_torch_xarray(self):
        """Test converting xarray DataArray to torch tensor."""
from scitex.decorators import to_torch
        
        data = xr.DataArray(np.array([1, 2, 3]))
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = to_torch(data)
        
        assert isinstance(result[0], torch.Tensor)
    
    def test_to_torch_nested_list(self):
        """Test converting nested structures."""
from scitex.decorators import to_torch
        
        data = ([1, 2], [3, 4])
        result = to_torch(data)
        
        assert isinstance(result[0], list)
        assert all(isinstance(t, torch.Tensor) for t in result[0])
    
    def test_to_torch_none_handling(self):
        """Test handling of None values."""
from scitex.decorators import to_torch
        
        result = to_torch(None, [1, 2, 3], None)
        
        # None values should be filtered out
        assert len(result) == 1
        assert isinstance(result[0], torch.Tensor)
    
    @pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
    def test_to_torch_cuda_device(self):
        """Test conversion with CUDA device."""
from scitex.decorators import to_torch
        
        array = np.array([1, 2, 3])
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = to_torch(array, device="cuda")
        
        assert result[0].device.type == "cuda"
    
    def test_to_torch_axis_to_dim(self):
        """Test axis parameter conversion to dim."""
from scitex.decorators import to_torch
        
        array = np.array([[1, 2], [3, 4]])
        _, kwargs = to_torch(array, axis=1)
        
        assert "dim" in kwargs
        assert "axis" not in kwargs
        assert kwargs["dim"] == 1
    
    def test_to_torch_with_return_always(self):
        """Test to_torch with _return_always function."""
from scitex.decorators import to_torch, _return_always
        
        array = np.array([1, 2, 3])
        args, kwargs = to_torch(array, return_fn=_return_always, test_kwarg=123)
        
        assert len(args) == 1
        assert isinstance(args[0], torch.Tensor)
        assert kwargs["test_kwarg"] == 123


class TestToNumpy:
    """Test cases for to_numpy function."""
    
    def test_to_numpy_torch_tensor(self):
        """Test converting torch tensor to numpy array."""
from scitex.decorators import to_numpy
        
        tensor = torch.tensor([1, 2, 3])
        result = to_numpy(tensor)
        
        assert isinstance(result[0], np.ndarray)
        np.testing.assert_array_equal(result[0], np.array([1, 2, 3]))
    
    def test_to_numpy_pandas_series(self):
        """Test converting pandas Series to numpy array."""
from scitex.decorators import to_numpy
        
        series = pd.Series([1, 2, 3])
        result = to_numpy(series)
        
        assert isinstance(result[0], np.ndarray)
        assert result[0].shape == (3,)
    
    def test_to_numpy_pandas_dataframe(self):
        """Test converting pandas DataFrame to numpy array."""
from scitex.decorators import to_numpy
        
        df = pd.DataFrame({"a": [1, 2, 3]})
        result = to_numpy(df)
        
        assert isinstance(result[0], np.ndarray)
        assert result[0].shape == (3,)
    
    def test_to_numpy_list(self):
        """Test converting list to numpy array."""
from scitex.decorators import to_numpy
        
        data = [1, 2, 3]
        result = to_numpy(data)
        
        assert isinstance(result[0], np.ndarray)
    
    def test_to_numpy_tuple_recursive(self):
        """Test recursive conversion of tuples."""
from scitex.decorators import to_numpy
        
        data = (torch.tensor([1, 2]), torch.tensor([3, 4]))
        result = to_numpy(data)
        
        assert isinstance(result[0], list)
        assert all(isinstance(arr, np.ndarray) for arr in result[0])
    
    @pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
    def test_to_numpy_cuda_tensor(self):
        """Test converting CUDA tensor to numpy."""
from scitex.decorators import to_numpy
        
        tensor = torch.tensor([1, 2, 3]).cuda()
        result = to_numpy(tensor)
        
        assert isinstance(result[0], np.ndarray)
        assert result[0].shape == (3,)
    
    def test_to_numpy_dim_to_axis(self):
        """Test dim parameter conversion to axis."""
from scitex.decorators import to_numpy
        
        tensor = torch.tensor([[1, 2], [3, 4]])
        _, kwargs = to_numpy(tensor, dim=1)
        
        assert "axis" in kwargs
        assert "dim" not in kwargs
        assert kwargs["axis"] == 1
    
    def test_to_numpy_none_filtering(self):
        """Test filtering of None values."""
from scitex.decorators import to_numpy
        
        result = to_numpy(None, [1, 2, 3], None)
        
        assert len(result) == 1
        assert isinstance(result[0], np.ndarray)


class TestIsNestedDecorator:
    """Test cases for is_nested_decorator function."""
    
    def test_is_nested_decorator_basic(self):
        """Test basic is_nested_decorator functionality."""
from scitex.decorators import is_nested_decorator
        
        # Outside decorator context
        assert is_nested_decorator() is False
    
    @patch('inspect.currentframe')
    def test_is_nested_decorator_mocked(self, mock_frame):
        """Test is_nested_decorator with mocked frames."""
from scitex.decorators import is_nested_decorator
        
        # Create mock frame chain
        frame1 = MagicMock()
        frame1.f_code.co_name = "wrapper"
        frame1.f_locals = {"_current_decorator": "torch_fn"}
        frame1.f_back = None
        
        frame2 = MagicMock()
        frame2.f_code.co_name = "wrapper"
        frame2.f_locals = {"_current_decorator": "numpy_fn"}
        frame2.f_back = frame1
        
        mock_frame.return_value = frame2
        
        # Should detect nested decorators
        assert is_nested_decorator() is True


class TestEdgeCasesAndIntegration:
    """Test edge cases and integration scenarios."""
    
    def test_to_torch_to_numpy_roundtrip(self):
        """Test roundtrip conversion."""
from scitex.decorators import to_torch, to_numpy
        
        original = np.array([1.5, 2.5, 3.5])
        
        # Convert to torch and back
        torch_result = to_torch(original)
        numpy_result = to_numpy(torch_result[0])
        
        np.testing.assert_array_almost_equal(numpy_result[0], original)
    
    def test_mixed_type_conversion(self):
        """Test conversion with mixed types."""
from scitex.decorators import to_torch
        
        # Mix of convertible and non-convertible types
        result = to_torch([1, 2, 3], "string", {"key": "value"})
        
        assert len(result) == 3
        assert isinstance(result[0], torch.Tensor)
        assert result[1] == "string"
        assert result[2] == {"key": "value"}
    
    def test_empty_container_conversion(self):
        """Test conversion of empty containers."""
from scitex.decorators import to_torch, to_numpy
        
        # Empty list
        torch_result = to_torch([])
        assert isinstance(torch_result[0], torch.Tensor)
        assert torch_result[0].shape == (0,)
        
        # Empty numpy array
        numpy_result = to_numpy(np.array([]))
        assert isinstance(numpy_result[0], np.ndarray)
        assert numpy_result[0].shape == (0,)
    
    def test_large_data_conversion(self):
        """Test conversion with large data."""
from scitex.decorators import to_torch, to_numpy
        
        # Large array
        large_array = np.random.randn(1000, 1000)
        
        torch_result = to_torch(large_array)
        assert torch_result[0].shape == (1000, 1000)
        
        numpy_result = to_numpy(torch_result[0])
        assert numpy_result[0].shape == (1000, 1000)
    
    def test_dtype_preservation(self):
        """Test data type preservation during conversion."""
from scitex.decorators import to_torch
        
        # Integer array
        int_array = np.array([1, 2, 3], dtype=np.int32)
        result = to_torch(int_array)
        
        # to_torch converts to float by default
        assert result[0].dtype == torch.float32
    
    def test_warning_suppression(self):
        """Test warning behavior."""
from scitex.decorators import to_torch, ConversionWarning
        
        array = np.array([1, 2, 3])
        
        # Should warn by default
        with pytest.warns(ConversionWarning):
            to_torch(array, device="cuda" if torch.cuda.is_available() else "cpu")


class TestPerformance:
    """Test performance aspects."""
    
    def test_conversion_caching(self):
        """Test that conversion doesn't create unnecessary copies."""
from scitex.decorators import to_torch
        
        # Already a tensor
        tensor = torch.tensor([1, 2, 3])
        result = to_torch(tensor)
        
        # Should return the same tensor when device matches
        if not torch.cuda.is_available():
            assert result[0] is tensor


if __name__ == "__main__":
    pytest.main([os.path.abspath(__file__), "-v"])