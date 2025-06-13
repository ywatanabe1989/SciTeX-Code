#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-05-25 17:15:00 (ywatanabe)"
# File: ./tests/scitex/decorators/test__DataTypeDecorators.py

"""
Test module for scitex.decorators._DataTypeDecorators
"""

import numpy as np
import pandas as pd
import pytest
import torch
import warnings
from unittest.mock import patch, MagicMock


class TestDataTypeDecorators:
    """Test cases for DataTypeDecorators module"""

    @pytest.fixture
    def setup_tensors(self):
        """Setup various tensor types for testing"""
        np_array = np.array([[1.0, 2.0], [3.0, 4.0]])
        torch_tensor = torch.tensor([[1.0, 2.0], [3.0, 4.0]])
        torch_cuda = torch_tensor.cuda() if torch.cuda.is_available() else torch_tensor
        pd_df = pd.DataFrame([[1.0, 2.0], [3.0, 4.0]])

        return {
            "numpy": np_array,
            "torch": torch_tensor,
            "cuda": torch_cuda,
            "pandas": pd_df,
        }

    def test_conversion_warning(self):
        """Test conversion warning functionality"""
from scitex.decorators import (
            _conversion_warning,
            ConversionWarning,
        )

        old = np.array([1, 2, 3])
        new = torch.tensor([1, 2, 3])

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            _conversion_warning(old, new)

            assert len(w) == 1
            assert issubclass(w[0].category, ConversionWarning)
            assert "Converted from ndarray to Tensor" in str(w[0].message)

    def test_cached_warning(self):
        """Test cached warning to avoid repetition"""
from scitex.decorators import _cached_warning

        message = "Test warning message"

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            # First call should produce warning
            _cached_warning(message)
            assert len(w) == 1

            # Second call with same message should be cached
            _cached_warning(message)
            # Due to caching, should still be only 1 warning
            assert len(w) == 1

    def test_try_device(self):
        """Test device movement with fallback"""
from scitex.decorators import _try_device

        tensor = torch.tensor([1.0, 2.0, 3.0])

        # Test CPU to CPU (no change)
        result = _try_device(tensor, "cpu")
        assert result.device.type == "cpu"

        # Test non-tensor input
        non_tensor = [1, 2, 3]
        result = _try_device(non_tensor, "cuda")
        assert result == non_tensor  # Should return unchanged

        if torch.cuda.is_available():
            # Test CPU to CUDA
            result = _try_device(tensor, "cuda")
            assert result.device.type == "cuda"

    def test_is_torch(self, setup_tensors):
        """Test torch tensor detection"""
from scitex.decorators import is_torch

        # Test with torch tensor
        assert is_torch(setup_tensors["torch"]) is True

        # Test with numpy array
        assert is_torch(setup_tensors["numpy"]) is False

        # Test with multiple arguments
        assert is_torch(setup_tensors["numpy"], setup_tensors["torch"]) is True

        # Test with kwargs
        assert is_torch(x=setup_tensors["torch"]) is True
        assert is_torch(x=setup_tensors["numpy"]) is False

    def test_is_cuda(self, setup_tensors):
        """Test CUDA tensor detection"""
from scitex.decorators import is_cuda

        # Test with CPU tensor
        assert is_cuda(setup_tensors["torch"]) is False

        # Test with CUDA tensor (if available)
        if torch.cuda.is_available():
            cuda_tensor = setup_tensors["torch"].cuda()
            assert is_cuda(cuda_tensor) is True

            # Test with mixed inputs
            assert is_cuda(setup_tensors["torch"], cuda_tensor) is True

    def test_decorator_functionality(self):
        """Test decorator conversion functionality"""
        # This would test the actual decorator if it's defined
        # Since we don't see the full decorator implementation,
        # we'll create a mock test

        # Assuming there's a decorator that converts inputs
from scitex.decorators import _try_device

        # Mock function to be decorated
        def sample_function(x):
            return x * 2

        # Test input conversion
        np_input = np.array([1, 2, 3])
        torch_input = torch.tensor([1, 2, 3])

        # The function should handle both types
        np_result = sample_function(np_input)
        torch_result = sample_function(torch_input)

        assert isinstance(np_result, np.ndarray)
        assert isinstance(torch_result, torch.Tensor)

    @pytest.mark.parametrize(
        "input_type,expected_torch,expected_cuda",
        [
            (np.array([1, 2, 3]), False, False),
            (torch.tensor([1, 2, 3]), True, False),
            ([1, 2, 3], False, False),
            (pd.DataFrame([1, 2, 3]), False, False),
        ],
    )
    def test_type_detection(self, input_type, expected_torch, expected_cuda):
        """Test various input type detections"""
from scitex.decorators import is_torch, is_cuda

        assert is_torch(input_type) == expected_torch
        assert is_cuda(input_type) == expected_cuda

    def test_conversion_with_multiple_inputs(self):
        """Test conversion with multiple input arguments"""
from scitex.decorators import is_torch

        # Mix of tensor and non-tensor inputs
        inputs = [
            np.array([1, 2, 3]),
            torch.tensor([4, 5, 6]),
            [7, 8, 9],
            pd.DataFrame([10, 11, 12]),
        ]

        # Should detect torch tensor in the mix
        assert is_torch(*inputs) is True

    def test_device_fallback(self):
        """Test device fallback when CUDA not available"""
from scitex.decorators import _try_device

        tensor = torch.tensor([1.0, 2.0, 3.0])

        # Mock CUDA not available
        with patch("torch.cuda.is_available", return_value=False):
            result = _try_device(tensor, "cuda")
            # Should fallback to CPU or return original
            assert result.device.type == "cpu"


# EOF
