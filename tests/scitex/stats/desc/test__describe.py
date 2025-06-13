#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: ./tests/scitex/stats/desc/test__describe.py

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
        import scitex.stats.desc._describe
    
    def test_import_from_stats(self):
        # Test that describe is available from stats module
        assert hasattr(scitex.stats, 'describe')


class TestDescribeWrapper:
    """Test the describe function wrapper from scitex.stats."""
    
    def test_basic_functionality(self):
        """Test basic describe functionality with various inputs."""
        # List input
        data = [1, 2, 3, 4, 5]
        result = scitex.stats.describe(data)
        
        assert isinstance(result, dict)
        assert 'mean' in result
        assert 'std' in result
        assert 'min' in result
        assert 'max' in result
        assert result['mean'] == 3.0
        assert result['min'] == 1.0
        assert result['max'] == 5.0
    
    def test_numpy_array(self):
        """Test with numpy array input."""
        data = np.array([1, 2, 3, 4, 5, 6])
        result = scitex.stats.describe(data)
        
        assert result['mean'] == 3.5
        assert result['min'] == 1.0
        assert result['max'] == 6.0
        assert 'std' in result
    
    def test_torch_tensor(self):
        """Test with PyTorch tensor input."""
        data = torch.tensor([2.0, 4.0, 6.0, 8.0])
        result = scitex.stats.describe(data)
        
        assert result['mean'] == 5.0
        assert result['min'] == 2.0
        assert result['max'] == 8.0
    
    def test_with_nan_values(self):
        """Test handling of NaN values."""
        data = np.array([1, 2, np.nan, 4, 5])
        result = scitex.stats.describe(data)
        
        # Should handle NaN properly
        assert result['mean'] == 3.0  # Mean of [1, 2, 4, 5]
        assert result['min'] == 1.0
        assert result['max'] == 5.0
    
    def test_empty_data(self):
        """Test with empty data."""
        data = []
        result = scitex.stats.describe(data)
        
        assert isinstance(result, dict)
        assert np.isnan(result['mean'])
        assert np.isnan(result['std'])
    
    def test_single_value(self):
        """Test with single value."""
        data = [42]
        result = scitex.stats.describe(data)
        
        assert result['mean'] == 42.0
        assert result['min'] == 42.0
        assert result['max'] == 42.0
        assert result['std'] == 0.0
    
    def test_multidimensional_data(self):
        """Test with multidimensional data."""
        data = np.array([[1, 2, 3], [4, 5, 6]])
        result = scitex.stats.describe(data)
        
        assert result['mean'] == 3.5
        assert result['min'] == 1.0
        assert result['max'] == 6.0


class TestDescribeInternal:
    """Test the internal describe function with tensor operations."""
    
    def test_basic_tensor_operations(self):
        """Test basic describe functionality with tensors."""
        x = torch.randn(10, 20, 30)
        stats, names = scitex.stats.desc._describe.describe(x, dim=-1)
        
        # Check output shape
        assert stats.shape == (10, 20, 7)  # 7 default statistics
        assert len(names) == 7
        assert all(name in ["nanmean", "nanstd", "nankurtosis", "nanskewness", 
                           "nanq25", "nanq50", "nanq75"] for name in names)
    
    def test_different_dimensions(self):
        """Test computation along different dimensions."""
        x = torch.randn(4, 5, 6, 7)
        
        # Single dimension
        stats1, _ = scitex.stats.desc._describe.describe(x, dim=0)
        assert stats1.shape == (5, 6, 7, 7)
        
        stats2, _ = scitex.stats.desc._describe.describe(x, dim=-1)
        assert stats2.shape == (4, 5, 6, 7)
        
        # Multiple dimensions
        stats3, _ = scitex.stats.desc._describe.describe(x, dim=(0, 1))
        assert stats3.shape == (6, 7, 7)
        
        stats4, _ = scitex.stats.desc._describe.describe(x, dim=(-2, -1))
        assert stats4.shape == (4, 5, 7)
    
    def test_keepdims(self):
        """Test keepdims parameter."""
        x = torch.randn(3, 4, 5)
        
        # keepdims=True (default)
        stats1, _ = scitex.stats.desc._describe.describe(x, dim=1, keepdims=True)
        assert stats1.shape == (3, 1, 5, 7)
        
        # keepdims=False
        stats2, _ = scitex.stats.desc._describe.describe(x, dim=1, keepdims=False)
        assert stats2.shape == (3, 5, 7)
    
    def test_custom_functions(self):
        """Test with custom function selection."""
        x = torch.randn(2, 3, 4)
        
        # Single function
        stats1, names1 = scitex.stats.desc._describe.describe(x, dim=-1, funcs=["nanmean"])
        assert stats1.shape == (2, 3, 1)
        assert names1 == ["nanmean"]
        
        # Multiple functions
        funcs = ["nanmean", "nanstd", "nanmax", "nanmin"]
        stats2, names2 = scitex.stats.desc._describe.describe(x, dim=-1, funcs=funcs)
        assert stats2.shape == (2, 3, 4)
        assert names2 == funcs
    
    def test_all_functions(self):
        """Test with all available functions."""
        x = torch.randn(2, 3, 4)
        stats, names = scitex.stats.desc._describe.describe(x, dim=-1, funcs="all")
        
        # Should include all available functions
        assert len(names) > 7  # More than default
        assert stats.shape[-1] == len(names)
        
        # Check some expected functions are included
        expected_funcs = ["mean", "std", "nanmean", "nanstd", "nanmax", "nanmin"]
        for func in expected_funcs:
            assert func in names
    
    def test_batch_processing(self):
        """Test batch processing functionality."""
        x = torch.randn(100, 50, 30)
        
        # Process with batch_size
        stats, _ = scitex.stats.desc._describe.describe(x, dim=-1, batch_size=10)
        assert stats.shape == (100, 50, 7)
    
    def test_statistical_correctness(self):
        """Test that computed statistics are correct."""
        # Create known data
        x = torch.tensor([[[1.0, 2.0, 3.0, 4.0, 5.0]]])
        stats, names = scitex.stats.desc._describe.describe(x, dim=-1, funcs=["nanmean", "nanstd"])
        
        # Expected values
        expected_mean = 3.0
        expected_std = torch.std(x[0, 0], unbiased=True).item()
        
        mean_idx = names.index("nanmean")
        std_idx = names.index("nanstd")
        
        assert torch.isclose(stats[0, 0, mean_idx], torch.tensor(expected_mean))
        assert torch.isclose(stats[0, 0, std_idx], torch.tensor(expected_std), rtol=1e-5)


class TestVerifyNonLeakage:
    """Test verify_non_leakage function."""
    
    def test_basic_verification(self):
        """Test basic non-leakage verification."""
        x = torch.randn(10, 20, 30)
        
        # Should pass without error
        result = scitex.stats.desc._describe.verify_non_leakage(x, dim=(1, 2))
        assert result is True
    
    def test_different_shapes(self):
        """Test with different tensor shapes."""
        shapes = [(5, 10, 15), (2, 3, 4, 5), (100, 50)]
        
        for shape in shapes:
            x = torch.randn(*shape)
            dim = tuple(range(1, len(shape)))  # All dims except first
            result = scitex.stats.desc._describe.verify_non_leakage(x, dim=dim)
            assert result is True
    
    def test_single_sample(self):
        """Test with single sample."""
        x = torch.randn(1, 10, 20)
        result = scitex.stats.desc._describe.verify_non_leakage(x, dim=(1, 2))
        assert result is True
    
    def test_with_nan_values(self):
        """Test non-leakage with NaN values."""
        x = torch.randn(5, 10, 15)
        x[0, 0, 0] = float('nan')
        x[2, 5, 7] = float('nan')
        
        result = scitex.stats.desc._describe.verify_non_leakage(x, dim=(1, 2))
        assert result is True


class TestIntegration:
    """Integration tests for describe functionality."""
    
    def test_wrapper_with_internal(self):
        """Test that wrapper properly calls internal function."""
        # Create test data
        data = np.random.randn(10, 20)
        
        # Use wrapper
        result = scitex.stats.describe(data)
        
        # Use internal function
        stats, names = scitex.stats.desc._describe.describe(data, funcs=["nanmean", "nanstd", "nanmin", "nanmax"])
        
        # Extract values from internal result
        mean_idx = names.index("nanmean")
        std_idx = names.index("nanstd")
        min_idx = names.index("nanmin")
        max_idx = names.index("nanmax")
        
        internal_mean = float(stats.reshape(-1)[mean_idx])
        internal_std = float(stats.reshape(-1)[std_idx])
        internal_min = float(stats.reshape(-1)[min_idx])
        internal_max = float(stats.reshape(-1)[max_idx])
        
        # Compare results (wrapper may have slightly different calculation)
        assert np.isclose(result['mean'], internal_mean, rtol=1e-5)
        assert np.isclose(result['min'], internal_min, rtol=1e-5)
        assert np.isclose(result['max'], internal_max, rtol=1e-5)
    
    def test_real_world_scenario(self):
        """Test with realistic data dimensions."""
        # Simulate batch of time series data
        batch_size, seq_len, features = 32, 100, 64
        x = torch.randn(batch_size, seq_len, features)
        
        # Use wrapper for simple statistics
        flat_result = scitex.stats.describe(x)
        assert isinstance(flat_result, dict)
        assert all(key in flat_result for key in ['mean', 'std', 'min', 'max'])
        
        # Use internal for detailed statistics
        stats, names = scitex.stats.desc._describe.describe(x, dim=1)
        assert stats.shape == (batch_size, features, 7)
        
        # Verify statistics are reasonable
        mean_idx = names.index("nanmean")
        std_idx = names.index("nanstd")
        
        assert torch.all(stats[:, :, std_idx] >= 0)  # std should be non-negative
    
    def test_error_handling(self):
        """Test error handling in wrapper."""
        # Test with problematic input that might cause internal function to fail
        # but wrapper should handle gracefully
        
        # Very large values
        data = np.array([1e308, 1e308, 1e308])
        result = scitex.stats.describe(data)
        assert isinstance(result, dict)
        assert 'mean' in result
        
        # Mixed types (wrapper should convert)
        data = [1, 2.5, 3, np.int64(4), np.float32(5)]
        result = scitex.stats.describe(data)
        assert result['mean'] == 3.1
        assert result['min'] == 1.0
        assert result['max'] == 5.0


# --------------------------------------------------------------------------------

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/stats/desc/_describe.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-12-05 09:20:53 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/stats/desc/_describe.py
#
# THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/stats/desc/_describe.py"
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
# from typing import List, Optional, Tuple, Union
#
# import numpy as np
# import torch
#
# from ...decorators import batch_fn, torch_fn
# from ._nan import (
#     nancount,
#     nankurtosis,
#     nanmax,
#     nanmean,
#     nanmin,
#     nanq25,
#     nanq50,
#     nanq75,
#     nanskewness,
#     nanstd,
#     nanvar,
# )
# from ._real import kurtosis, mean, q25, q50, q75, skewness, std
#
#
# def verify_non_leakage(
#     x: torch.Tensor,
#     dim: Optional[Union[int, Tuple[int, ...]]] = None,
# ):
#     """
#     Verifies that statistics computation doesn't leak information across samples.
#
#     Parameters
#     ----------
#     x : torch.Tensor
#         Input tensor
#     dim : Optional[Union[int, Tuple[int, ...]]]
#         Dimension(s) used for computation
#
#     Returns
#     -------
#     bool
#         True if verification passes
#
#     Raises
#     ------
#     AssertionError
#         If statistics leak information across samples
#     """
#     # Full calculation
#     described, _ = describe(x, dim=(1, 2))
#
#     # Compute statistics on first sample
#     x_first = x[:1]
#     described_first, _ = describe(x_first, dim=dim)
#
#     # Verify shapes match
#     assert (
#         described_first.shape == described[:1].shape
#     ), f"Shape mismatch: {described_first.shape} != {described[:1].shape}"
#
#     # Verify values match
#     torch.testing.assert_close(
#         described_first,
#         described[:1],
#         rtol=1e-5,
#         atol=1e-8,
#         msg="Statistics leak information across samples",
#     )
#
#     return True
#
#
# @torch_fn
# @batch_fn
# def describe(
#     x: torch.Tensor,
#     axis: int = -1,
#     dim: Optional[Union[int, Tuple[int, ...]]] = None,
#     keepdims: bool = False,
#     funcs: Union[List[str], str] = [
#         "nanmean",
#         "nanstd",
#         "nankurtosis",
#         "nanskewness",
#         "nanq25",
#         "nanq50",
#         "nanq75",
#     ],
#     device: Optional[torch.device] = None,
#     batch_size: int = -1,
# ) -> Tuple[torch.Tensor, List[str]]:
#     """
#     Computes various descriptive statistics.
#
#     Parameters
#     ----------
#     x : torch.Tensor
#         Input tensor
#     axis : int, default=-1
#         Deprecated. Use dim instead
#     dim : int or tuple of ints, optional
#         Dimension(s) along which to compute statistics
#     keepdims : bool, default=True
#         Whether to keep reduced dimensions
#     funcs : list of str or "all"
#         Statistical functions to compute
#     device : torch.device, optional
#         Device to use for computation
#
#     Returns
#     -------
#     Tuple[torch.Tensor, List[str]]
#         Computed statistics and their names
#     """
#     dim = axis if dim is None else dim
#     dim = (dim,) if isinstance(dim, int) else tuple(dim)
#
#     func_names = funcs
#     func_candidates = {
#         "mean": mean,
#         "std": std,
#         "kurtosis": kurtosis,
#         "skewness": skewness,
#         "q25": q25,
#         "q50": q50,
#         "q75": q75,
#         "nanmean": nanmean,
#         "nanstd": nanstd,
#         "nanvar": nanvar,
#         "nankurtosis": nankurtosis,
#         "nanskewness": nanskewness,
#         "nanq25": nanq25,
#         "nanq50": nanq50,
#         "nanq75": nanq75,
#         "nanmax": nanmax,
#         "nanmin": nanmin,
#         "nancount": nancount,
#         # "nanprod": nanprod,
#         # "nanargmin": nanargmin,
#         # "nanargmax": nanargmax,
#     }
#
#     if funcs == "all":
#         _funcs = list(func_candidates.values())
#         func_names = list(func_candidates.keys())
#     else:
#         _funcs = [func_candidates[ff] for ff in func_names]
#
#     calculated = [ff(x, dim=dim, keepdims=keepdims) for ff in _funcs]
#     return torch.stack(calculated, dim=-1), func_names
#
#
# if __name__ == "__main__":
#     from scitex.stats.desc._describe import describe, verify_non_leakage
#
#     # x = np.random.rand(4, 3, 2)
#     # x = np.random.rand(390, 250, 16, 100, 100)
#     # print(scitex.stats.desc.nankurtosis(x, dim=(1,2)).shape)
#
#     x = np.random.rand(10, 250, 16, 100, 100)
#
#     described, _ = describe(x[:10], dim=(-2, -1), batch_size=1)
#     # verify_non_leakage(x, dim=(1, 2))
#     # # print(describe(x, dim=(1, 2), keepdims=False)[0].shape)
#     # # print(describe(x, funcs="all", dim=(1, 2), keepdims=False)[0].shape)
#
#
# """
# python ./scitex_repo/src/scitex/stats/desc/_describe.py
# python -m src.scitex.stats.desc._describe
# """
#
# # EOF
