#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: ./tests/scitex/stats/desc/test__real.py

import pytest
import numpy as np
import torch
import scitex


class TestImports:
    def test_import_main(self):
        import scitex

    def test_import_submodule(self):
        import scitex.stats

    def test_import_target(self):
        import scitex.stats.desc._real


class TestMean:
    """Test mean function."""
    
    def test_basic_functionality(self):
        """Test basic mean computation."""
        x = torch.tensor([1.0, 2.0, 3.0, 4.0, 5.0])
        result = scitex.stats.desc._real.mean(x)
        assert result == 3.0
    
    def test_numpy_input(self):
        """Test with numpy array input."""
        x = np.array([2.0, 4.0, 6.0, 8.0])
        result = scitex.stats.desc._real.mean(x)
        assert isinstance(result, torch.Tensor)
        assert result == 5.0
    
    def test_multidimensional(self):
        """Test mean with multiple dimensions."""
        x = torch.tensor([[1.0, 2.0, 3.0],
                          [4.0, 5.0, 6.0]])
        
        # Mean along last dimension
        result1 = scitex.stats.desc._real.mean(x, dim=-1)
        assert torch.allclose(result1, torch.tensor([2.0, 5.0]))
        
        # Mean along first dimension
        result2 = scitex.stats.desc._real.mean(x, dim=0)
        assert torch.allclose(result2, torch.tensor([2.5, 3.5, 4.5]))
    
    def test_keepdims(self):
        """Test keepdims parameter."""
        x = torch.randn(3, 4, 5)
        
        result1 = scitex.stats.desc._real.mean(x, dim=1, keepdims=True)
        assert result1.shape == (3, 1, 5)
        
        result2 = scitex.stats.desc._real.mean(x, dim=1, keepdims=False)
        assert result2.shape == (3, 5)


class TestStd:
    """Test std function."""
    
    def test_basic_functionality(self):
        """Test basic standard deviation computation."""
        x = torch.tensor([1.0, 1.0, 1.0, 1.0])
        result = scitex.stats.desc._real.std(x)
        assert result == 0.0  # No variation
        
        x2 = torch.tensor([1.0, 2.0, 3.0, 4.0, 5.0])
        result2 = scitex.stats.desc._real.std(x2)
        expected = torch.std(x2)
        assert torch.isclose(result2, expected)
    
    def test_unbiased_estimator(self):
        """Test that std uses unbiased estimator by default."""
        x = torch.tensor([1.0, 2.0, 3.0])
        result = scitex.stats.desc._real.std(x)
        # PyTorch std uses unbiased estimator (Bessel's correction) by default
        expected = torch.std(x, unbiased=True)
        assert torch.isclose(result, expected)
    
    def test_multidimensional(self):
        """Test std with multiple dimensions."""
        torch.manual_seed(42)
        x = torch.randn(10, 20, 30)
        
        result = scitex.stats.desc._real.std(x, dim=-1)
        assert result.shape == (10, 20)
        assert torch.all(result >= 0)  # std is always non-negative


class TestVar:
    """Test var function."""
    
    def test_basic_functionality(self):
        """Test basic variance computation."""
        x = torch.tensor([1.0, 2.0, 3.0, 4.0, 5.0])
        result = scitex.stats.desc._real.var(x)
        expected = torch.var(x)
        assert torch.isclose(result, expected)
    
    def test_relationship_with_std(self):
        """Test that var = std^2."""
        x = torch.randn(20, 30)
        
        var_result = scitex.stats.desc._real.var(x, dim=-1)
        std_result = scitex.stats.desc._real.std(x, dim=-1)
        
        assert torch.allclose(var_result, std_result ** 2, rtol=1e-5)
    
    def test_keepdims(self):
        """Test keepdims parameter."""
        x = torch.randn(3, 4, 5)
        
        result1 = scitex.stats.desc._real.var(x, dim=-1, keepdims=True)
        assert result1.shape == (3, 4, 1)
        
        result2 = scitex.stats.desc._real.var(x, dim=-1, keepdims=False)
        assert result2.shape == (3, 4)


class TestZscore:
    """Test zscore function."""
    
    def test_basic_functionality(self):
        """Test basic z-score normalization."""
        x = torch.tensor([1.0, 2.0, 3.0, 4.0, 5.0])
        result = scitex.stats.desc._real.zscore(x)
        
        # Check mean is approximately 0
        assert torch.abs(result.mean()) < 1e-5
        # Check std is approximately 1
        assert torch.abs(result.std() - 1.0) < 1e-5
    
    def test_keepdims_default_true(self):
        """Test that keepdims defaults to True for zscore."""
        x = torch.randn(3, 4, 5)
        
        # Default keepdims=True
        result1 = scitex.stats.desc._real.zscore(x, dim=1)
        assert result1.shape == x.shape
        
        # Explicit keepdims=False
        result2 = scitex.stats.desc._real.zscore(x, dim=1, keepdims=False)
        assert result2.shape == (3, 4, 5)
    
    def test_multidimensional(self):
        """Test z-score with multiple dimensions."""
        torch.manual_seed(42)
        x = torch.randn(10, 20, 30)
        
        # Normalize along last dimension
        result = scitex.stats.desc._real.zscore(x, dim=-1)
        
        # Check normalization per slice
        for i in range(10):
            for j in range(20):
                slice_data = result[i, j, :]
                assert torch.abs(slice_data.mean()) < 1e-5
                assert torch.abs(slice_data.std() - 1.0) < 1e-5
    
    def test_constant_values(self):
        """Test z-score with constant values."""
        x = torch.ones(5, 10)
        result = scitex.stats.desc._real.zscore(x, dim=-1)
        
        # When std is 0, result should be NaN or 0
        assert torch.all(torch.isnan(result)) or torch.all(result == 0)


class TestSkewness:
    """Test skewness function."""
    
    def test_symmetric_distribution(self):
        """Test skewness of symmetric distribution."""
        x = torch.tensor([-2.0, -1.0, 0.0, 1.0, 2.0])
        result = scitex.stats.desc._real.skewness(x)
        assert torch.abs(result) < 1e-5  # Should be ~0 for symmetric
    
    def test_right_skewed(self):
        """Test positive skewness for right-skewed distribution."""
        # Right-skewed: more values on left, tail on right
        x = torch.tensor([1.0, 1.0, 1.0, 2.0, 3.0, 10.0])
        result = scitex.stats.desc._real.skewness(x)
        assert result > 0
    
    def test_left_skewed(self):
        """Test negative skewness for left-skewed distribution."""
        # Left-skewed: more values on right, tail on left
        x = torch.tensor([-10.0, 1.0, 2.0, 2.0, 2.0, 2.0])
        result = scitex.stats.desc._real.skewness(x)
        assert result < 0
    
    def test_normal_distribution(self):
        """Test skewness of normal distribution."""
        torch.manual_seed(42)
        x = torch.randn(10000)
        result = scitex.stats.desc._real.skewness(x)
        # Normal distribution has skewness ~0
        assert torch.abs(result) < 0.1


class TestKurtosis:
    """Test kurtosis function."""
    
    def test_normal_distribution(self):
        """Test kurtosis of normal distribution."""
        torch.manual_seed(42)
        x = torch.randn(10000)
        result = scitex.stats.desc._real.kurtosis(x)
        # Excess kurtosis of normal distribution is 0
        assert torch.abs(result) < 0.1
    
    def test_uniform_distribution(self):
        """Test kurtosis of uniform distribution."""
        x = torch.linspace(-1, 1, 1000)
        result = scitex.stats.desc._real.kurtosis(x)
        # Uniform distribution has negative excess kurtosis (~-1.2)
        assert result < -1.0
    
    def test_peaked_distribution(self):
        """Test kurtosis of peaked distribution."""
        # Create a distribution with heavy tails
        x = torch.cat([torch.randn(100) * 0.1,  # Narrow center
                       torch.randn(10) * 10])    # Heavy tails
        result = scitex.stats.desc._real.kurtosis(x)
        # Should have positive excess kurtosis
        assert result > 0
    
    def test_keepdims(self):
        """Test keepdims parameter."""
        x = torch.randn(3, 4, 5)
        
        result1 = scitex.stats.desc._real.kurtosis(x, dim=-1, keepdims=True)
        assert result1.shape == (3, 4, 1)
        
        result2 = scitex.stats.desc._real.kurtosis(x, dim=-1, keepdims=False)
        assert result2.shape == (3, 4)


class TestQuantile:
    """Test quantile function."""
    
    def test_basic_functionality(self):
        """Test basic quantile computation."""
        x = torch.tensor([0.0, 1.0, 2.0, 3.0, 4.0])
        
        # 50th percentile (median)
        result = scitex.stats.desc._real.quantile(x, 50)
        assert result == 2.0
        
        # 0th percentile (min)
        result_min = scitex.stats.desc._real.quantile(x, 0)
        assert result_min == 0.0
        
        # 100th percentile (max)
        result_max = scitex.stats.desc._real.quantile(x, 100)
        assert result_max == 4.0
    
    def test_multidimensional(self):
        """Test quantile with multiple dimensions."""
        x = torch.tensor([[1.0, 2.0, 3.0, 4.0, 5.0],
                          [2.0, 4.0, 6.0, 8.0, 10.0]])
        
        # 50th percentile along last dimension
        result = scitex.stats.desc._real.quantile(x, 50, dim=-1)
        assert torch.allclose(result, torch.tensor([3.0, 6.0]))
    
    def test_multiple_dimensions_reduction(self):
        """Test quantile with multiple dimension reduction."""
        x = torch.randn(2, 3, 4, 5)
        
        result = scitex.stats.desc._real.quantile(x, 50, dim=(1, 2))
        assert result.shape == (2, 5)
    
    def test_keepdims(self):
        """Test keepdims parameter."""
        x = torch.randn(3, 4, 5)
        
        result1 = scitex.stats.desc._real.quantile(x, 25, dim=1, keepdims=True)
        assert result1.shape == (3, 1, 5)
        
        result2 = scitex.stats.desc._real.quantile(x, 25, dim=1, keepdims=False)
        assert result2.shape == (3, 5)


class TestQ25Q50Q75:
    """Test q25, q50, q75 convenience functions."""
    
    def test_q25(self):
        """Test 25th percentile function."""
        x = torch.tensor([0.0, 1.0, 2.0, 3.0, 4.0])
        result = scitex.stats.desc._real.q25(x)
        
        # Should match quantile(x, 25)
        expected = scitex.stats.desc._real.quantile(x, 25)
        assert torch.isclose(result, expected)
        
        # 25th percentile should be between 0 and 2
        assert 0.0 <= result <= 2.0
    
    def test_q50(self):
        """Test 50th percentile (median) function."""
        x = torch.tensor([1.0, 2.0, 3.0, 4.0, 5.0])
        result = scitex.stats.desc._real.q50(x)
        
        # Should match quantile(x, 50)
        expected = scitex.stats.desc._real.quantile(x, 50)
        assert torch.isclose(result, expected)
        assert result == 3.0
    
    def test_q75(self):
        """Test 75th percentile function."""
        x = torch.tensor([0.0, 1.0, 2.0, 3.0, 4.0])
        result = scitex.stats.desc._real.q75(x)
        
        # Should match quantile(x, 75)
        expected = scitex.stats.desc._real.quantile(x, 75)
        assert torch.isclose(result, expected)
        
        # 75th percentile should be between 2 and 4
        assert 2.0 <= result <= 4.0
    
    def test_quantile_ordering(self):
        """Test that q25 < q50 < q75."""
        x = torch.randn(100)
        
        q25_val = scitex.stats.desc._real.q25(x)
        q50_val = scitex.stats.desc._real.q50(x)
        q75_val = scitex.stats.desc._real.q75(x)
        
        assert q25_val < q50_val < q75_val


class TestIntegration:
    """Integration tests for real statistics functions."""
    
    def test_real_world_scenario(self):
        """Test with realistic data."""
        # Simulate sensor data
        torch.manual_seed(42)
        time_points = 1000
        channels = 64
        
        # Generate data with trend and noise
        t = torch.linspace(0, 10, time_points)
        signal = torch.sin(2 * np.pi * 0.5 * t)  # 0.5 Hz sine wave
        noise = torch.randn(channels, time_points) * 0.1
        data = signal.unsqueeze(0) + noise
        
        # Compute statistics
        mean_val = scitex.stats.desc._real.mean(data, dim=-1)
        std_val = scitex.stats.desc._real.std(data, dim=-1)
        skew_val = scitex.stats.desc._real.skewness(data, dim=-1)
        kurt_val = scitex.stats.desc._real.kurtosis(data, dim=-1)
        
        # Verify shapes
        assert mean_val.shape == (channels,)
        assert std_val.shape == (channels,)
        assert skew_val.shape == (channels,)
        assert kurt_val.shape == (channels,)
        
        # Verify reasonable values
        assert torch.all(torch.abs(mean_val) < 0.5)  # Mean near 0
        assert torch.all(std_val > 0)  # Positive std
        assert torch.all(torch.abs(skew_val) < 1)  # Reasonable skewness
    
    def test_statistical_consistency(self):
        """Test consistency between different statistics."""
        x = torch.randn(50, 100)
        
        # Test mean and median relationship
        mean_val = scitex.stats.desc._real.mean(x, dim=-1)
        median_val = scitex.stats.desc._real.q50(x, dim=-1)
        
        # For normal distribution, mean ≈ median
        assert torch.allclose(mean_val, median_val, rtol=0.1)
        
        # Test IQR relationship
        q25_val = scitex.stats.desc._real.q25(x, dim=-1)
        q75_val = scitex.stats.desc._real.q75(x, dim=-1)
        iqr = q75_val - q25_val
        
        # IQR should be positive
        assert torch.all(iqr > 0)
        
        # For normal distribution, IQR ≈ 1.35 * std
        std_val = scitex.stats.desc._real.std(x, dim=-1)
        expected_iqr = 1.35 * std_val
        assert torch.allclose(iqr, expected_iqr, rtol=0.2)
    
    def test_edge_cases(self):
        """Test edge cases."""
        # Single value
        x1 = torch.tensor([5.0])
        assert scitex.stats.desc._real.mean(x1) == 5.0
        assert scitex.stats.desc._real.std(x1) == 0.0
        assert scitex.stats.desc._real.q50(x1) == 5.0
        
        # Constant values
        x2 = torch.ones(10)
        assert scitex.stats.desc._real.mean(x2) == 1.0
        assert scitex.stats.desc._real.std(x2) == 0.0
        assert scitex.stats.desc._real.var(x2) == 0.0
        
        # Two values
        x3 = torch.tensor([1.0, 3.0])
        assert scitex.stats.desc._real.mean(x3) == 2.0
        assert scitex.stats.desc._real.q50(x3) == 2.0


# --------------------------------------------------------------------------------

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/stats/desc/_real.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-17 21:17:13 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/stats/desc/_real.py
#
# THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/stats/desc/_real.py"
#
# """
# Functionality:
#     - Computes descriptive statistics on PyTorch tensors
# Input:
#     - PyTorch tensor or numpy array
# Output:
#     - Descriptive statistics (mean, std, quantiles, etc.)
# Prerequisites:
#     - PyTorch, NumPy
# """
#
#
# import numpy as np
# import torch
#
# from ...decorators import torch_fn
#
#
# @torch_fn
# def mean(x, axis=-1, dim=None, keepdims=False):
#     return x.mean(dim, keepdims=keepdims)
#
#
# @torch_fn
# def std(x, axis=-1, dim=None, keepdims=False):
#     return x.std(dim, keepdims=keepdims)
#
#
# @torch_fn
# def var(x, axis=-1, dim=None, keepdims=False):
#     return x.var(dim, keepdims=keepdims)
#
#
# @torch_fn
# def zscore(x, axis=-1, dim=None, keepdims=True):
#     _mean = mean(x, dim=dim, keepdims=True)
#     _std = std(x, dim=dim, keepdims=True)
#     zscores = (x - _mean) / _std
#     return zscores if keepdims else zscores.squeeze(dim)
#
#
# @torch_fn
# def skewness(x, axis=-1, dim=None, keepdims=False):
#     zscores = zscore(x, axis=axis, keepdims=True)
#     return torch.mean(torch.pow(zscores, 3.0), dim=dim, keepdims=keepdims)
#
#
# @torch_fn
# def kurtosis(x, axis=-1, dim=None, keepdims=False):
#     zscores = zscore(x, axis=axis, keepdims=True)
#     return torch.mean(torch.pow(zscores, 4.0), dim=dim, keepdims=keepdims) - 3.0
#
#
# @torch_fn
# def quantile(x, q, axis=-1, dim=None, keepdims=False):
#     dim = axis if dim is None else dim
#     if isinstance(dim, (tuple, list)):
#         for d in sorted(dim, reverse=True):
#             x = torch.quantile(x, q / 100, dim=d, keepdims=keepdims)
#     else:
#         x = torch.quantile(x, q / 100, dim=dim, keepdims=keepdims)
#     return x
#
#
# @torch_fn
# def q25(x, axis=-1, dim=None, keepdims=False):
#     return quantile(x, 25, axis=axis, dim=dim, keepdims=keepdims)
#
#
# @torch_fn
# def q50(x, axis=-1, dim=None, keepdims=False):
#     return quantile(x, 50, axis=axis, dim=dim, keepdims=keepdims)
#
#
# @torch_fn
# def q75(x, axis=-1, dim=None, keepdims=False):
#     return quantile(x, 75, axis=axis, dim=dim, keepdims=keepdims)
#
#
# if __name__ == "__main__":
#     # from scitex.stats.desc import *
#
#     x = np.random.rand(4, 3, 2)
#     print(describe(x, dim=(1, 2), keepdims=False)[0].shape)
#     print(describe(x, funcs="all", dim=(1, 2), keepdims=False)[0].shape)
#
# # EOF
