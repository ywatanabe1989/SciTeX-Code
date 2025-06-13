#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-01 15:30:00 (ywatanabe)"
# File: ./tests/scitex/ai/utils/test__verify_n_gpus.py

"""Tests for scitex.ai.utils._verify_n_gpus module."""

import pytest
import warnings
import torch
from unittest.mock import patch, MagicMock
from scitex.ai.utils import verify_n_gpus


class TestVerifyNGpus:
    """Test suite for verify_n_gpus function."""

    def test_verify_n_gpus_sufficient_gpus(self):
        """Test when requested GPUs are available."""
        with patch('torch.cuda.device_count', return_value=4):
            # Request less than available
            result = verify_n_gpus(2)
            assert result == 2
            
            # Request exactly available
            result = verify_n_gpus(4)
            assert result == 4

    def test_verify_n_gpus_insufficient_gpus_warns(self):
        """Test warning when requested GPUs exceed available."""
        with patch('torch.cuda.device_count', return_value=2):
            with pytest.warns(UserWarning, match="N_GPUS .* is larger"):
                result = verify_n_gpus(4)
                assert result == 2  # Returns available count

    def test_verify_n_gpus_zero_gpus(self):
        """Test behavior when no GPUs are available."""
        with patch('torch.cuda.device_count', return_value=0):
            # Request 0 GPUs
            result = verify_n_gpus(0)
            assert result == 0
            
            # Request GPUs when none available
            with pytest.warns(UserWarning):
                result = verify_n_gpus(1)
                assert result == 0

    def test_verify_n_gpus_negative_input(self):
        """Test behavior with negative input."""
        with patch('torch.cuda.device_count', return_value=2):
            # Should handle negative numbers gracefully
            result = verify_n_gpus(-1)
            assert result == -1  # Returns as-is when sufficient

    def test_verify_n_gpus_warning_message(self):
        """Test the specific warning message format."""
        with patch('torch.cuda.device_count', return_value=1):
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                result = verify_n_gpus(3)
                
                assert len(w) == 1
                assert issubclass(w[0].category, UserWarning)
                warning_message = str(w[0].message)
                assert "N_GPUS (3)" in warning_message
                assert "torch can acesses (= 1)" in warning_message
                assert "$CUDA_VISIBLE_DEVICES" in warning_message

    def test_verify_n_gpus_large_number(self):
        """Test with unrealistically large GPU request."""
        with patch('torch.cuda.device_count', return_value=8):
            with pytest.warns(UserWarning):
                result = verify_n_gpus(1000)
                assert result == 8

    def test_verify_n_gpus_float_input(self):
        """Test behavior with float input."""
        with patch('torch.cuda.device_count', return_value=2):
            # Float input should work in comparison
            result = verify_n_gpus(1.5)
            assert result == 1.5

    @pytest.mark.parametrize("n_gpus,available,expected", [
        (1, 1, 1),
        (2, 4, 2),
        (4, 2, 2),
        (0, 8, 0),
        (8, 8, 8),
    ])
    def test_verify_n_gpus_various_combinations(self, n_gpus, available, expected):
        """Test various combinations of requested and available GPUs."""
        with patch('torch.cuda.device_count', return_value=available):
            if n_gpus > available:
                with pytest.warns(UserWarning):
                    result = verify_n_gpus(n_gpus)
            else:
                result = verify_n_gpus(n_gpus)
            assert result == expected

    def test_verify_n_gpus_string_input_error(self):
        """Test that string input causes appropriate error."""
        with patch('torch.cuda.device_count', return_value=2):
            # String comparison with int should raise TypeError
            with pytest.raises(TypeError):
                verify_n_gpus("2")

    def test_verify_n_gpus_none_input_error(self):
        """Test that None input causes appropriate error."""
        with patch('torch.cuda.device_count', return_value=2):
            with pytest.raises(TypeError):
                verify_n_gpus(None)

    def test_verify_n_gpus_actual_cuda_check(self):
        """Test with actual CUDA availability check."""
        # This test uses real torch.cuda.device_count
        actual_gpu_count = torch.cuda.device_count()
        
        if actual_gpu_count > 0:
            # Test with available GPUs
            result = verify_n_gpus(1)
            assert result == 1
        else:
            # Test with no GPUs
            with pytest.warns(UserWarning):
                result = verify_n_gpus(1)
                assert result == 0

    def test_verify_n_gpus_multiple_calls(self):
        """Test multiple consecutive calls."""
        with patch('torch.cuda.device_count', return_value=2):
            # Multiple calls should behave consistently
            result1 = verify_n_gpus(1)
            result2 = verify_n_gpus(1)
            assert result1 == result2 == 1
            
            # Each excessive request should warn
            with pytest.warns(UserWarning):
                result3 = verify_n_gpus(3)
            with pytest.warns(UserWarning):
                result4 = verify_n_gpus(3)
            assert result3 == result4 == 2

    def test_verify_n_gpus_environment_variable_mention(self):
        """Test that warning mentions CUDA_VISIBLE_DEVICES."""
        with patch('torch.cuda.device_count', return_value=0):
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                verify_n_gpus(1)
                
                # Check that the warning mentions the environment variable
                assert any("CUDA_VISIBLE_DEVICES" in str(warning.message) for warning in w)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
