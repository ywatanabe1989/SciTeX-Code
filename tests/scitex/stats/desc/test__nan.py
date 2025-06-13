#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: ./tests/scitex/stats/desc/test__nan.py

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
        import scitex.stats.desc._nan


class TestNanMax:
    """Test nanmax function."""
    
    def test_basic_functionality(self):
        """Test basic nanmax with NaN values."""
        x = torch.tensor([1.0, 2.0, float('nan'), 4.0, 3.0])
        result = scitex.stats.desc._nan.nanmax(x)
        assert result == 4.0
    
    def test_multidimensional(self):
        """Test nanmax with multiple dimensions."""
        x = torch.tensor([[1.0, float('nan'), 3.0],
                          [float('nan'), 5.0, 2.0]])
        
        # Max along last dimension
        result1 = scitex.stats.desc._nan.nanmax(x, dim=-1)
        assert torch.allclose(result1, torch.tensor([3.0, 5.0]))
        
        # Max along first dimension
        result2 = scitex.stats.desc._nan.nanmax(x, dim=0)
        assert torch.allclose(result2, torch.tensor([1.0, 5.0, 3.0]))
    
    def test_keepdims(self):
        """Test keepdims parameter."""
        x = torch.randn(3, 4, 5)
        x[0, 0, 0] = float('nan')
        
        result1 = scitex.stats.desc._nan.nanmax(x, dim=1, keepdims=True)
        assert result1.shape == (3, 1, 5)
        
        result2 = scitex.stats.desc._nan.nanmax(x, dim=1, keepdims=False)
        assert result2.shape == (3, 5)
    
    def test_all_nan(self):
        """Test with all NaN values."""
        x = torch.full((3, 4), float('nan'))
        result = scitex.stats.desc._nan.nanmax(x, dim=-1)
        # Result should be min value of dtype when all are NaN
        assert torch.all(result == torch.finfo(x.dtype).min)


class TestNanMin:
    """Test nanmin function."""
    
    def test_basic_functionality(self):
        """Test basic nanmin with NaN values."""
        x = torch.tensor([1.0, 2.0, float('nan'), 4.0, 3.0])
        result = scitex.stats.desc._nan.nanmin(x)
        assert result == 1.0
    
    def test_multidimensional(self):
        """Test nanmin with multiple dimensions."""
        x = torch.tensor([[1.0, float('nan'), 3.0],
                          [float('nan'), 5.0, 2.0]])
        
        result1 = scitex.stats.desc._nan.nanmin(x, dim=-1)
        assert torch.allclose(result1, torch.tensor([1.0, 2.0]))
        
        result2 = scitex.stats.desc._nan.nanmin(x, dim=0)
        assert torch.allclose(result2, torch.tensor([1.0, 5.0, 2.0]))


class TestNanMean:
    """Test nanmean function."""
    
    def test_basic_functionality(self):
        """Test basic nanmean with NaN values."""
        x = torch.tensor([1.0, 2.0, float('nan'), 4.0])
        result = scitex.stats.desc._nan.nanmean(x)
        expected = (1.0 + 2.0 + 4.0) / 3
        assert torch.isclose(result, torch.tensor(expected))
    
    def test_numpy_input(self):
        """Test with numpy array input."""
        x = np.array([1.0, 2.0, np.nan, 4.0])
        result = scitex.stats.desc._nan.nanmean(x)
        expected = (1.0 + 2.0 + 4.0) / 3
        assert torch.isclose(result, torch.tensor(expected))
    
    def test_multiple_dimensions(self):
        """Test with multiple dimension reduction."""
        x = torch.randn(2, 3, 4, 5)
        x[0, 0, 0, 0] = float('nan')
        x[1, 2, 3, 4] = float('nan')
        
        result = scitex.stats.desc._nan.nanmean(x, dim=(1, 2))
        assert result.shape == (2, 5)


class TestNanStd:
    """Test nanstd function."""
    
    def test_basic_functionality(self):
        """Test basic nanstd with NaN values."""
        x = torch.tensor([1.0, 2.0, float('nan'), 3.0, 4.0, 5.0])
        result = scitex.stats.desc._nan.nanstd(x)
        
        # Calculate expected std ignoring NaN
        valid_values = torch.tensor([1.0, 2.0, 3.0, 4.0, 5.0])
        expected = torch.std(valid_values, unbiased=False)
        assert torch.isclose(result, expected, rtol=1e-5)
    
    def test_keepdims(self):
        """Test keepdims parameter."""
        x = torch.randn(3, 4, 5)
        x[0, 0, :] = float('nan')
        
        result1 = scitex.stats.desc._nan.nanstd(x, dim=-1, keepdims=True)
        assert result1.shape == (3, 4, 1)
        
        result2 = scitex.stats.desc._nan.nanstd(x, dim=-1, keepdims=False)
        assert result2.shape == (3, 4)


class TestNanVar:
    """Test nanvar function."""
    
    def test_basic_functionality(self):
        """Test basic nanvar with NaN values."""
        x = torch.tensor([1.0, 2.0, float('nan'), 3.0])
        result = scitex.stats.desc._nan.nanvar(x)
        
        # Calculate expected variance
        valid_values = torch.tensor([1.0, 2.0, 3.0])
        expected = torch.var(valid_values, unbiased=False)
        assert torch.isclose(result, expected, rtol=1e-5)
    
    def test_relationship_with_std(self):
        """Test that var = std^2."""
        x = torch.randn(10, 20)
        x[0, :5] = float('nan')
        
        var_result = scitex.stats.desc._nan.nanvar(x, dim=-1)
        std_result = scitex.stats.desc._nan.nanstd(x, dim=-1)
        
        assert torch.allclose(var_result, std_result ** 2, rtol=1e-5)


class TestNanZscore:
    """Test nanzscore function."""
    
    def test_basic_functionality(self):
        """Test basic z-score normalization."""
        x = torch.tensor([1.0, 2.0, float('nan'), 3.0, 4.0, 5.0])
        result = scitex.stats.desc._nan.nanzscore(x)
        
        # Check that non-NaN values have mean ~0 and std ~1
        valid_mask = ~torch.isnan(result)
        assert torch.abs(result[valid_mask].mean()) < 1e-5
        assert torch.abs(result[valid_mask].std() - 1.0) < 1e-5
    
    def test_keepdims(self):
        """Test keepdims parameter."""
        x = torch.randn(3, 4, 5)
        
        result1 = scitex.stats.desc._nan.nanzscore(x, dim=1, keepdims=True)
        assert result1.shape == x.shape
        
        result2 = scitex.stats.desc._nan.nanzscore(x, dim=1, keepdims=False)
        assert result2.shape == (3, 4, 5)  # Should squeeze dim 1


class TestNanKurtosis:
    """Test nankurtosis function."""
    
    def test_normal_distribution(self):
        """Test kurtosis of normal distribution (should be ~0)."""
        torch.manual_seed(42)
        x = torch.randn(10000)
        result = scitex.stats.desc._nan.nankurtosis(x)
        # Excess kurtosis of normal distribution is 0
        assert torch.abs(result) < 0.1
    
    def test_with_nan(self):
        """Test kurtosis with NaN values."""
        x = torch.tensor([1.0, 2.0, float('nan'), 3.0, 4.0, 5.0])
        result = scitex.stats.desc._nan.nankurtosis(x)
        assert not torch.isnan(result)


class TestNanSkewness:
    """Test nanskewness function."""
    
    def test_symmetric_distribution(self):
        """Test skewness of symmetric distribution (should be ~0)."""
        x = torch.tensor([-2.0, -1.0, 0.0, 1.0, 2.0])
        result = scitex.stats.desc._nan.nanskewness(x)
        assert torch.abs(result) < 1e-5
    
    def test_skewed_distribution(self):
        """Test skewness of skewed distribution."""
        # Right-skewed distribution
        x = torch.tensor([1.0, 1.0, 1.0, 2.0, 3.0, 10.0])
        result = scitex.stats.desc._nan.nanskewness(x)
        assert result > 0  # Should be positive for right-skewed
    
    def test_with_nan(self):
        """Test skewness with NaN values."""
        x = torch.tensor([1.0, 2.0, float('nan'), 3.0, 4.0, float('nan'), 5.0])
        result = scitex.stats.desc._nan.nanskewness(x)
        assert not torch.isnan(result)


class TestNanQuantiles:
    """Test nanquantile and related functions."""
    
    def test_nanq25(self):
        """Test 25th percentile."""
        x = torch.tensor([1.0, 2.0, float('nan'), 3.0, 4.0])
        result = scitex.stats.desc._nan.nanq25(x)
        # 25th percentile of [1, 2, 3, 4] should be between 1 and 2
        assert 1.0 <= result <= 2.0
    
    def test_nanq50(self):
        """Test 50th percentile (median)."""
        x = torch.tensor([1.0, 2.0, float('nan'), 3.0, 4.0, 5.0])
        result = scitex.stats.desc._nan.nanq50(x)
        # Median of [1, 2, 3, 4, 5] is 3
        assert torch.isclose(result, torch.tensor(3.0))
    
    def test_nanq75(self):
        """Test 75th percentile."""
        x = torch.tensor([1.0, 2.0, float('nan'), 3.0, 4.0])
        result = scitex.stats.desc._nan.nanq75(x)
        # 75th percentile of [1, 2, 3, 4] should be between 3 and 4
        assert 3.0 <= result <= 4.0
    
    def test_nanquantile(self):
        """Test general quantile function."""
        x = torch.tensor([0.0, 1.0, 2.0, float('nan'), 3.0, 4.0])
        
        # Test multiple quantiles
        q = torch.tensor([0.0, 0.25, 0.5, 0.75, 1.0])
        result = scitex.stats.desc._nan.nanquantile(x, q)
        
        assert result[0] == 0.0  # min
        assert result[-1] == 4.0  # max
        assert result[2] == 2.0  # median


class TestNanCount:
    """Test nancount function."""
    
    def test_basic_functionality(self):
        """Test counting non-NaN values."""
        x = torch.tensor([1.0, 2.0, float('nan'), 3.0, float('nan')])
        result = scitex.stats.desc._nan.nancount(x)
        assert result == 3
    
    def test_multidimensional(self):
        """Test counting along dimensions."""
        x = torch.tensor([[1.0, float('nan'), 3.0],
                          [float('nan'), 5.0, float('nan')]])
        
        # Count along last dimension
        result1 = scitex.stats.desc._nan.nancount(x, dim=-1)
        assert torch.allclose(result1, torch.tensor([2, 1]))
        
        # Count along first dimension
        result2 = scitex.stats.desc._nan.nancount(x, dim=0)
        assert torch.allclose(result2, torch.tensor([1, 1, 1]))
    
    def test_keepdims(self):
        """Test keepdims parameter."""
        x = torch.randn(3, 4, 5)
        x[0, 0, :] = float('nan')
        
        result1 = scitex.stats.desc._nan.nancount(x, dim=-1, keepdims=True)
        assert result1.shape == (3, 4, 1)
        
        result2 = scitex.stats.desc._nan.nancount(x, dim=-1, keepdims=False)
        assert result2.shape == (3, 4)


class TestNanSum:
    """Test nansum function."""
    
    def test_basic_functionality(self):
        """Test basic nansum."""
        x = torch.tensor([1.0, 2.0, float('nan'), 3.0])
        result = scitex.stats.desc._nan.nansum(x)
        assert result == 6.0
    
    def test_all_nan(self):
        """Test sum of all NaN values."""
        x = torch.full((3,), float('nan'))
        result = scitex.stats.desc._nan.nansum(x)
        assert result == 0.0  # Sum of all NaN should be 0


class TestNanProd:
    """Test nanprod function."""
    
    def test_basic_functionality(self):
        """Test basic nanprod."""
        x = torch.tensor([2.0, 3.0, float('nan'), 4.0])
        result = scitex.stats.desc._nan.nanprod(x)
        assert result == 24.0  # 2 * 3 * 4
    
    def test_with_zeros(self):
        """Test product with zeros."""
        x = torch.tensor([2.0, 0.0, float('nan'), 4.0])
        result = scitex.stats.desc._nan.nanprod(x)
        assert result == 0.0


class TestNanArgMinMax:
    """Test nanargmin and nanargmax functions."""
    
    def test_nanargmax(self):
        """Test finding index of maximum ignoring NaN."""
        x = torch.tensor([1.0, float('nan'), 5.0, 3.0, float('nan')])
        result = scitex.stats.desc._nan.nanargmax(x)
        assert result == 2  # Index of 5.0
    
    def test_nanargmin(self):
        """Test finding index of minimum ignoring NaN."""
        x = torch.tensor([5.0, float('nan'), 1.0, 3.0, float('nan')])
        result = scitex.stats.desc._nan.nanargmin(x)
        assert result == 2  # Index of 1.0
    
    def test_multidimensional_argmax(self):
        """Test argmax with multiple dimensions."""
        x = torch.tensor([[1.0, float('nan'), 3.0],
                          [float('nan'), 5.0, 2.0]])
        
        result = scitex.stats.desc._nan.nanargmax(x, dim=-1)
        assert torch.allclose(result, torch.tensor([2, 1]))


class TestIntegration:
    """Integration tests for nan functions."""
    
    def test_real_world_scenario(self):
        """Test with realistic data containing NaN values."""
        # Simulate sensor data with missing values
        torch.manual_seed(42)
        data = torch.randn(100, 50)
        
        # Add random NaN values (10% missing)
        mask = torch.rand_like(data) < 0.1
        data[mask] = float('nan')
        
        # Compute various statistics
        mean = scitex.stats.desc._nan.nanmean(data, dim=0)
        std = scitex.stats.desc._nan.nanstd(data, dim=0)
        min_val = scitex.stats.desc._nan.nanmin(data, dim=0)
        max_val = scitex.stats.desc._nan.nanmax(data, dim=0)
        count = scitex.stats.desc._nan.nancount(data, dim=0)
        
        # Verify results
        assert mean.shape == (50,)
        assert std.shape == (50,)
        assert torch.all(std >= 0)  # std should be non-negative
        assert torch.all(min_val <= max_val)  # min <= max
        assert torch.all(count <= 100)  # count <= total samples
        assert torch.all(count > 0)  # Should have some valid values
    
    def test_batch_processing(self):
        """Test batch processing with NaN handling."""
        # Large tensor with NaN values
        x = torch.randn(1000, 100)
        x[torch.rand_like(x) < 0.05] = float('nan')
        
        # Process with batch_size
        result = scitex.stats.desc._nan.nanmean(x, dim=-1, batch_size=100)
        assert result.shape == (1000,)
        assert not torch.any(torch.isnan(result))  # No NaN in results
    
    def test_consistency_across_functions(self):
        """Test consistency between related functions."""
        x = torch.randn(50, 30)
        x[torch.rand_like(x) < 0.2] = float('nan')
        
        # Test that zscore has mean 0 and std 1
        z = scitex.stats.desc._nan.nanzscore(x, dim=0)
        z_mean = scitex.stats.desc._nan.nanmean(z, dim=0)
        z_std = scitex.stats.desc._nan.nanstd(z, dim=0)
        
        assert torch.allclose(z_mean, torch.zeros_like(z_mean), atol=1e-5)
        assert torch.allclose(z_std, torch.ones_like(z_std), atol=1e-5)


# --------------------------------------------------------------------------------

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/stats/desc/_nan.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-25 20:51:05 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/stats/desc/_nan.py
#
# THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/stats/desc/_nan.py"
#
# from scitex.decorators import torch_fn, batch_fn
# import torch
#
#
# @torch_fn
# @batch_fn
# def nanmax(x, axis=-1, dim=None, batch_size=None, keepdims=False):
#     min_value = torch.finfo(x.dtype).min
#     dim = axis if dim is None else dim
#     if isinstance(dim, (tuple, list)):
#         for d in sorted(dim, reverse=True):
#             x = x.nan_to_num(min_value).max(dim=d, keepdims=keepdims)[0]
#     else:
#         x = x.nan_to_num(min_value).max(dim=dim, keepdims=keepdims)[0]
#     return x
#
#
# @torch_fn
# @batch_fn
# def nanmin(x, axis=-1, dim=None, batch_size=None, keepdims=False):
#     max_value = torch.finfo(x.dtype).max
#     dim = axis if dim is None else dim
#     if isinstance(dim, (tuple, list)):
#         for d in sorted(dim, reverse=True):
#             x = x.nan_to_num(max_value).min(dim=d, keepdims=keepdims)[0]
#     else:
#         x = x.nan_to_num(max_value).min(dim=dim, keepdims=keepdims)[0]
#     return x
#
#
# @torch_fn
# @batch_fn
# def nansum(x, axis=-1, dim=None, batch_size=None, keepdims=False):
#     return torch.nansum(x, dim=dim, keepdims=keepdims)
#
#
# @torch_fn
# @batch_fn
# def nanmean(x, axis=-1, dim=None, batch_size=None, keepdims=False):
#     return torch.nanmean(x, dim=dim, keepdims=keepdims)
#
#
# @torch_fn
# @batch_fn
# def nanvar(x, axis=-1, dim=None, batch_size=None, keepdims=False):
#     tensor_mean = nanmean(x, dim=dim, keepdims=True)
#     return (x - tensor_mean).square().nanmean(dim=dim, keepdims=keepdims)
#
#
# @torch_fn
# @batch_fn
# def nanstd(x, axis=-1, dim=None, batch_size=None, keepdims=False):
#     return torch.sqrt(nanvar(x, dim=dim, keepdims=keepdims))
#
#
# # @torch_fn
# # def nanzscore(x, axis=-1, dim=None, batch_size=None, keepdims=True):
# #     _mean = nanmean(x, dim=dim, keepdims=True)
# #     _std = nanstd(x, dim=dim, keepdims=True)
# #     zscores = (x - _mean) / _std
# #     return zscores if keepdims else zscores.squeeze(dim)
# @torch_fn
# @batch_fn
# def nanzscore(x, axis=-1, dim=None, batch_size=None, keepdims=True):
#     dim = axis if dim is None else dim
#     if isinstance(dim, (tuple, list)):
#         _mean = nanmean(x, dim=dim, keepdims=True)
#         _std = nanstd(x, dim=dim, keepdims=True)
#     else:
#         _mean = nanmean(x, dim=dim, keepdims=True)
#         _std = nanstd(x, dim=dim, keepdims=True)
#     zscores = (x - _mean) / _std
#     return zscores if keepdims else zscores.squeeze(dim)
#
#
# # @torch_fn
# # def nankurtosis(x, axis=-1, dim=None, batch_size=None, keepdims=False):
# #     zscores = nanzscore(x, axis=axis, keepdims=True)
# #     n = (~torch.isnan(x)).sum(dim=dim, keepdim=True).to(x.dtype)  # Changed this line
# #     k = torch.nanmean(torch.pow(zscores, 4.0), dim=dim, keepdims=keepdims)
# #     correction = (n * (n + 1)) / ((n - 1) * (n - 2) * (n - 3))
# #     return correction * k - 3 * (n - 1)**2 / ((n - 2) * (n - 3))
#
#
# # @torch_fn
# # def nankurtosis(x, axis=-1, dim=None, batch_size=None, keepdims=False):
# #     dim = axis if dim is None else dim
# #     if isinstance(dim, (tuple, list)):
# #         zscores = nanzscore(x, dim=dim, keepdims=True)
# #         n = (~torch.isnan(x)).sum(dim=dim, keepdim=True).to(x.dtype)
# #         k = torch.nanmean(torch.pow(zscores, 4.0), dim=dim, keepdims=keepdims)
# #         correction = (n * (n + 1)) / ((n - 1) * (n - 2) * (n - 3))
# #         result = correction * k - 3 * (n - 1)**2 / ((n - 2) * (n - 3))
# #         return result.squeeze() if not keepdims else result
# #     else:
# #         # Original code for single dimension
# #         zscores = nanzscore(x, dim=dim, keepdims=True)
# #         n = (~torch.isnan(x)).sum(dim=dim, keepdim=True).to(x.dtype)
# #         k = torch.nanmean(torch.pow(zscores, 4.0), dim=dim, keepdims=keepdims)
# #         correction = (n * (n + 1)) / ((n - 1) * (n - 2) * (n - 3))
# #         result = correction * k - 3 * (n - 1)**2 / ((n - 2) * (n - 3))
# #         return result.squeeze() if not keepdims else result
#
# # @torch_fn
# # def nanskewness(x, axis=-1, dim=None, batch_size=None, keepdims=False):
# #     zscores = nanzscore(x, axis=axis, keepdims=True)
# #     n = (~torch.isnan(x)).sum(dim=dim, keepdim=True).to(x.dtype)  # Changed this line
# #     s = torch.nanmean(torch.pow(zscores, 3.0), dim=dim, keepdims=keepdims)
# #     correction = n**2 / ((n - 1) * (n - 2))
# #     return correction * s
#
#
# @torch_fn
# @batch_fn
# def nankurtosis(x, axis=-1, dim=None, batch_size=None, keepdims=False):
#     zscores = nanzscore(x, axis=axis, keepdims=True)
#     return torch.nanmean(torch.pow(zscores, 4.0), dim=dim, keepdims=keepdims) - 3.0
#
#
# @torch_fn
# @batch_fn
# def nanskewness(x, axis=-1, dim=None, batch_size=None, keepdims=False):
#     zscores = nanzscore(x, axis=axis, keepdims=True)
#     return torch.nanmean(torch.pow(zscores, 3.0), dim=dim, keepdims=keepdims)
#
#
# @torch_fn
# @batch_fn
# def nanprod(x, axis=-1, dim=None, batch_size=None, keepdims=False):
#     dim = axis if dim is None else dim
#     if isinstance(dim, (tuple, list)):
#         for d in sorted(dim, reverse=True):
#             x = x.nan_to_num(1).prod(dim=d, keepdims=keepdims)
#     else:
#         x = x.nan_to_num(1).prod(dim=dim, keepdims=keepdims)
#     return x
#
#
# @torch_fn
# @batch_fn
# def nancumprod(x, axis=-1, dim=None, batch_size=None, keepdims=False):
#     dim = axis if dim is None else dim
#     return x.nan_to_num(1).cumprod(dim=dim)
#
#
# @torch_fn
# @batch_fn
# def nancumsum(x, axis=-1, dim=None, batch_size=None, keepdims=False):
#     dim = axis if dim is None else dim
#     return x.nan_to_num(0).cumsum(dim=dim)
#
#
# @torch_fn
# @batch_fn
# def nanargmin(x, axis=-1, dim=None, batch_size=None, keepdims=False):
#     max_value = torch.finfo(x.dtype).max
#     dim = axis if dim is None else dim
#     return x.nan_to_num(max_value).argmin(dim=dim, keepdims=keepdims)
#
#
# @torch_fn
# @batch_fn
# def nanargmax(x, axis=-1, dim=None, batch_size=None, keepdims=False):
#     min_value = torch.finfo(x.dtype).min
#     dim = axis if dim is None else dim
#     return x.nan_to_num(min_value).argmax(dim=dim, keepdims=keepdims)
#
#
# @torch_fn
# @batch_fn
# def nanquantile(x, q, axis=-1, dim=None, batch_size=None, keepdims=False):
#     return torch.nanquantile(x, q, dim=dim, keepdims=keepdims)
#
#
# @torch_fn
# @batch_fn
# def nanq25(x, axis=-1, dim=None, batch_size=None, keepdims=False):
#     return nanquantile(x, 0.25, dim=dim, keepdims=keepdims)
#
#
# @torch_fn
# @batch_fn
# def nanq50(x, axis=-1, dim=None, batch_size=None, keepdims=False):
#     return nanquantile(x, 0.50, dim=dim, keepdims=keepdims)
#
#
# @torch_fn
# @batch_fn
# def nanq75(x, axis=-1, dim=None, batch_size=None, keepdims=False):
#     return nanquantile(x, 0.75, dim=dim, keepdims=keepdims)
#
#
# @torch_fn
# @batch_fn
# def nancount(x, axis=-1, dim=None, batch_size=None, keepdims=False):
#     dim = axis if dim is None else dim
#     return (~torch.isnan(x)).sum(dim=dim, keepdims=keepdims).to(x.dtype)
#
#
# # EOF
