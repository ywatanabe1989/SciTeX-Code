#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-31 19:50:00 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/.claude-worktree/scitex_repo/tests/scitex/gen/test__norm.py

import pytest
import torch
import numpy as np
from scitex.gen import to_z, to_nanz, to_01, to_nan01, unbias, clip_perc


class TestNormalizationFunctions:
    """Test cases for normalization functions in scitex.gen._norm."""

    @pytest.fixture
    def sample_tensor(self):
        """Create a sample tensor for testing."""
        return torch.tensor([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])

    @pytest.fixture
    def tensor_with_nan(self):
        """Create a tensor with NaN values."""
        return torch.tensor([[1.0, float("nan"), 3.0], [4.0, 5.0, float("nan")]])

    def test_to_z_basic(self, sample_tensor):
        """Test basic z-score normalization."""
        result = to_z(sample_tensor, dim=-1, device="cpu")

        # Check shape is preserved
        assert result.shape == sample_tensor.shape

        # Check mean is approximately 0 and std is approximately 1
        assert torch.allclose(result.mean(dim=-1), torch.zeros(2), atol=1e-6)
        assert torch.allclose(result.std(dim=-1), torch.ones(2), atol=1e-6)

    def test_to_z_different_dims(self, sample_tensor):
        """Test z-score normalization along different dimensions."""
        # Along dim 0
        result_dim0 = to_z(sample_tensor, dim=0, device="cpu")
        assert torch.allclose(result_dim0.mean(dim=0), torch.zeros(3), atol=1e-6)
        assert torch.allclose(result_dim0.std(dim=0), torch.ones(3), atol=1e-6)

        # Along dim 1
        result_dim1 = to_z(sample_tensor, dim=1, device="cpu")
        assert torch.allclose(result_dim1.mean(dim=1), torch.zeros(2), atol=1e-6)
        assert torch.allclose(result_dim1.std(dim=1), torch.ones(2), atol=1e-6)

    def test_to_nanz_with_nan(self, tensor_with_nan):
        """Test z-score normalization with NaN handling."""
        result = to_nanz(tensor_with_nan, dim=-1, device="cpu")

        # Check shape is preserved
        assert result.shape == tensor_with_nan.shape

        # Check non-NaN values are normalized
        # For first row: [1.0, nan, 3.0] -> mean=2, std=1
        assert torch.allclose(result[0, 0], torch.tensor(-1.0), atol=1e-6)
        assert torch.allclose(result[0, 2], torch.tensor(1.0), atol=1e-6)
        assert torch.isnan(result[0, 1])

    def test_to_01_basic(self, sample_tensor):
        """Test min-max scaling to [0, 1] range."""
        result = to_01(sample_tensor, dim=-1, device="cpu")

        # Check shape is preserved
        assert result.shape == sample_tensor.shape

        # Check min is 0 and max is 1 along dimension
        assert torch.allclose(result.min(dim=-1)[0], torch.zeros(2))
        assert torch.allclose(result.max(dim=-1)[0], torch.ones(2))

    def test_to_01_edge_case(self):
        """Test min-max scaling with constant values."""
        # All values are the same
        constant_tensor = torch.ones(2, 3) * 5.0
        result = to_01(constant_tensor, dim=-1, device="cpu")
        # Result should handle division by zero gracefully
        assert result.shape == constant_tensor.shape

    def test_to_nan01_with_nan(self, tensor_with_nan):
        """Test min-max scaling with NaN handling."""
        result = to_nan01(tensor_with_nan, dim=-1, device="cpu")

        # Check shape is preserved
        assert result.shape == tensor_with_nan.shape

        # Check non-NaN values are scaled properly
        # For first row: [1.0, nan, 3.0] -> min=1, max=3
        assert torch.allclose(result[0, 0], torch.tensor(0.0), atol=1e-6)
        assert torch.allclose(result[0, 2], torch.tensor(1.0), atol=1e-6)
        assert torch.isnan(result[0, 1])

    def test_unbias_mean(self, sample_tensor):
        """Test unbiasing using mean method."""
        result = unbias(sample_tensor, dim=-1, fn="mean", device="cpu")

        # Check shape is preserved
        assert result.shape == sample_tensor.shape

        # Check mean is approximately 0
        assert torch.allclose(result.mean(dim=-1), torch.zeros(2), atol=1e-6)

    def test_unbias_min(self, sample_tensor):
        """Test unbiasing using min method."""
        result = unbias(sample_tensor, dim=-1, fn="min", device="cpu")

        # Check shape is preserved
        assert result.shape == sample_tensor.shape

        # Check min is 0
        assert torch.allclose(result.min(dim=-1)[0], torch.zeros(2))

    def test_unbias_invalid_method(self, sample_tensor):
        """Test unbias with invalid method raises error."""
        with pytest.raises(ValueError, match="Unsupported unbiasing method"):
            unbias(sample_tensor, dim=-1, fn="invalid", device="cpu")

    def test_clip_perc_basic(self, sample_tensor):
        """Test percentile clipping."""
        # Create tensor with outliers
        tensor_with_outliers = torch.tensor(
            [[1.0, 2.0, 3.0, 100.0], [-100.0, 4.0, 5.0, 6.0]]
        )

        result = clip_perc(
            tensor_with_outliers, lower_perc=25, upper_perc=75, dim=-1, device="cpu"
        )

        # Check shape is preserved
        assert result.shape == tensor_with_outliers.shape

        # Check values are clipped
        # Outliers should be clipped to the 25th and 75th percentiles
        assert result[0, 3] < 100.0  # Upper outlier clipped
        assert result[1, 0] > -100.0  # Lower outlier clipped

    def test_numpy_array_input(self):
        """Test functions work with numpy array inputs."""
        np_array = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])

        # to_z should handle numpy arrays via torch_fn decorator
        result = to_z(np_array, dim=-1, device="cpu")
        assert isinstance(result, torch.Tensor)
        assert torch.allclose(result.mean(dim=-1), torch.zeros(2), atol=1e-6)

    def test_axis_parameter(self, sample_tensor):
        """Test using 'axis' parameter instead of 'dim' for numpy compatibility."""
        # The functions should handle axis parameter
        result = to_z(sample_tensor, axis=0, device="cpu")
        assert result.shape == sample_tensor.shape
        assert torch.allclose(result.mean(dim=0), torch.zeros(3), atol=1e-6)

    @pytest.mark.parametrize("func", [to_z, to_01, unbias])
    def test_functions_preserve_gradient(self, func):
        """Test that functions preserve gradient information."""
        tensor = torch.tensor([[1.0, 2.0, 3.0]], requires_grad=True)
        result = func(tensor, dim=-1, device="cpu")

        # Should be able to compute gradients
        loss = result.sum()
        loss.backward()
        assert tensor.grad is not None

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/gen/_norm.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-19 01:09:55 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/gen/_norm.py
# 
# THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/gen/_norm.py"
# 
# import torch
# 
# from ..decorators import torch_fn
# from ..torch import nanstd
# 
# 
# @torch_fn
# def to_z(x, axis=-1, dim=None, device="cuda"):
#     """Standardizes tensor to zero mean and unit variance along specified dimension.
# 
#     Parameters
#     ----------
#     xx : torch.Tensor
#         Input tensor
#     dim : int, optional
#         Dimension along which to standardize (preferred)
#     axis : int, optional
#         Alternative to dim for numpy compatibility
#     device : str
#         Device to use for computation
# 
#     Returns
#     -------
#     torch.Tensor
#         Z-scored tensor
#     """
#     return (x - x.mean(dim=dim, keepdim=True)) / x.std(dim=dim, keepdim=True)
# 
# 
# @torch_fn
# def to_nanz(x, axis=-1, dim=None, device="cuda"):
#     """Standardizes tensor handling NaN values along specified dimension.
# 
#     Parameters
#     ----------
#     xx : torch.Tensor
#         Input tensor
#     dim : int, optional
#         Dimension along which to standardize (preferred)
#     axis : int, optional
#         Alternative to dim for numpy compatibility
#     device : str
#         Device to use for computation
# 
#     Returns
#     -------
#     torch.Tensor
#         Z-scored tensor with NaN handling
#     """
#     nan_mean = torch.nanmean(x, dim=dim, keepdim=True)
#     nan_std = nanstd(x, dim=dim, keepdim=True)
#     return (x - nan_mean) / nan_std
# 
# 
# @torch_fn
# def to_01(x, axis=-1, dim=None, device="cuda"):
#     """Min-max scales tensor to [0, 1] range along specified dimension.
# 
#     Parameters
#     ----------
#     xx : torch.Tensor
#         Input tensor
#     dim : int, optional
#         Dimension along which to scale (preferred)
#     axis : int, optional
#         Alternative to dim for numpy compatibility
#     device : str
#         Device to use for computation
# 
#     Returns
#     -------
#     torch.Tensor
#         Min-max scaled tensor
#     """
#     # Use dim if provided, otherwise use axis
#     dimension = dim if dim is not None else axis
#     
#     if dimension is None:
#         # Scale entire tensor
#         x_min = x.min()
#         x_max = x.max()
#     else:
#         # Scale along specified dimension
#         x_min = x.min(dim=dimension, keepdim=True)[0]
#         x_max = x.max(dim=dimension, keepdim=True)[0]
#     
#     # Avoid division by zero
#     return (x - x_min) / (x_max - x_min + 1e-8)
# 
# 
# @torch_fn
# def to_nan01(x, axis=-1, dim=None, device="cuda"):
#     """Min-max scales tensor handling NaN values along specified dimension.
# 
#     Parameters
#     ----------
#     xx : torch.Tensor
#         Input tensor
#     dim : int, optional
#         Dimension along which to scale (preferred)
#     axis : int, optional
#         Alternative to dim for numpy compatibility
#     device : str
#         Device to use for computation
# 
#     Returns
#     -------
#     torch.Tensor
#         Min-max scaled tensor with NaN handling
#     """
#     # Use dim if provided, otherwise use axis
#     dimension = dim if dim is not None else axis
#     
#     if dimension is None:
#         # Scale entire tensor
#         x_min = torch.nanmin(x)
#         x_max = torch.nanmax(x)
#     else:
#         # Scale along specified dimension
#         x_min = torch.nanmin(x, dim=dimension, keepdim=True)[0]
#         x_max = torch.nanmax(x, dim=dimension, keepdim=True)[0]
#     
#     # Avoid division by zero
#     return (x - x_min) / (x_max - x_min + 1e-8)
# 
# 
# @torch_fn
# def unbias(x, axis=-1, dim=None, fn="mean", device="cuda"):
#     """Removes bias from tensor using specified method along dimension.
# 
#     Parameters
#     ----------
#     xx : torch.Tensor
#         Input tensor
#     dim : int, optional
#         Dimension along which to unbias (preferred)
#     axis : int, optional
#         Alternative to dim for numpy compatibility
#     fn : str
#         Method to use for unbiasing ('mean' or 'min')
#     device : str
#         Device to use for computation
# 
#     Returns
#     -------
#     torch.Tensor
#         Unbiased tensor
#     """
#     if fn == "mean":
#         return x - x.mean(dim=dim, keepdims=True)
#     if fn == "min":
#         return x - x.min(dim=dim, keepdims=True)[0]
#     raise ValueError(f"Unsupported unbiasing method: {fn}")
# 
# 
# @torch_fn
# def clip_perc(x, lower_perc=2.5, upper_perc=97.5, low=None, high=None, axis=-1, dim=None, device="cuda"):
#     """Clips tensor values between specified percentiles along dimension.
# 
#     Parameters
#     ----------
#     x : torch.Tensor
#         Input tensor
#     lower_perc : float
#         Lower percentile (0-100)
#     upper_perc : float
#         Upper percentile (0-100)
#     low : float, optional
#         Alternative name for lower_perc
#     high : float, optional
#         Alternative name for upper_perc
#     dim : int
#         Dimension along which to compute percentiles (preferred)
#     axis : int
#         Alternative to dim for numpy compatibility
#     device : str
#         Device to use for computation
# 
#     Returns
#     -------
#     torch.Tensor
#         Clipped tensor
#     """
#     # Handle alternative parameter names
#     if low is not None:
#         lower_perc = low
#     if high is not None:
#         upper_perc = high
#         
#     # Use dim if provided, otherwise use axis
#     dimension = dim if dim is not None else axis
#     
#     lower = torch.quantile(x, lower_perc / 100, dim=dimension, keepdim=True)
#     upper = torch.quantile(x, upper_perc / 100, dim=dimension, keepdim=True)
#     return torch.clamp(x, min=lower, max=upper)
# 
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/gen/_norm.py
# --------------------------------------------------------------------------------
