import pytest
import numpy as np
import torch
import scitex


class TestZ:
    """Test z-score normalization function."""

    def test_import(self):
        """Test function can be imported."""
        assert hasattr(scitex.dsp.norm, "z")

    def test_basic_1d(self):
        """Test z-score normalization on 1D signal."""
        # Create signal with known mean and std
        signal = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        result = scitex.dsp.norm.z(signal)

        # Check result has zero mean and unit std
        assert np.abs(np.mean(result)) < 1e-10
        assert np.abs(np.std(result, ddof=0) - 1.0) < 1e-10

    def test_basic_2d(self):
        """Test z-score normalization on 2D signal."""
        signal = np.random.randn(10, 100)
        result = scitex.dsp.norm.z(signal, dim=-1)

        # Check each row has zero mean and unit std
        row_means = np.mean(result, axis=-1)
        row_stds = np.std(result, axis=-1, ddof=0)
        assert np.all(np.abs(row_means) < 1e-10)
        assert np.all(np.abs(row_stds - 1.0) < 1e-10)

    def test_basic_3d(self):
        """Test z-score normalization on 3D signal."""
        signal = np.random.randn(5, 10, 100)
        result = scitex.dsp.norm.z(signal, dim=-1)

        # Check last dimension has zero mean and unit std
        assert result.shape == signal.shape
        flat_result = result.reshape(-1, 100)
        for row in flat_result:
            assert np.abs(np.mean(row)) < 1e-10
            assert np.abs(np.std(row, ddof=0) - 1.0) < 1e-10

    def test_different_dimensions(self):
        """Test z-score normalization along different dimensions."""
        signal = np.random.randn(4, 5, 6)
        
        # Test along dim=0
        result0 = scitex.dsp.norm.z(signal, dim=0)
        assert np.all(np.abs(np.mean(result0, axis=0)) < 1e-10)
        
        # Test along dim=1
        result1 = scitex.dsp.norm.z(signal, dim=1)
        assert np.all(np.abs(np.mean(result1, axis=1)) < 1e-10)
        
        # Test along dim=2 (default)
        result2 = scitex.dsp.norm.z(signal, dim=2)
        assert np.all(np.abs(np.mean(result2, axis=2)) < 1e-10)

    def test_constant_signal(self):
        """Test z-score normalization on constant signal."""
        signal = np.ones((5, 10))
        with pytest.warns(RuntimeWarning):
            result = scitex.dsp.norm.z(signal)
            # Should handle division by zero gracefully
            assert np.all(np.isnan(result)) or np.all(np.isinf(result))

    def test_torch_input(self):
        """Test with PyTorch tensor input."""
        signal = torch.randn(10, 50)
        result = scitex.dsp.norm.z(signal)
        
        assert isinstance(result, torch.Tensor)
        assert torch.abs(torch.mean(result, dim=-1)).max() < 1e-6
        assert torch.abs(torch.std(result, dim=-1, unbiased=False) - 1.0).max() < 1e-6

    def test_preserves_shape(self):
        """Test that function preserves input shape."""
        shapes = [(10,), (5, 20), (3, 4, 50), (2, 3, 4, 100)]
        for shape in shapes:
            signal = np.random.randn(*shape)
            result = scitex.dsp.norm.z(signal)
            assert result.shape == signal.shape


class TestMinmax:
    """Test minmax normalization function."""

    def test_import(self):
        """Test function can be imported."""
        assert hasattr(scitex.dsp.norm, "minmax")

    def test_basic_1d(self):
        """Test minmax normalization on 1D signal."""
        signal = np.array([-2.0, -1.0, 0.0, 1.0, 2.0])
        result = scitex.dsp.norm.minmax(signal)
        
        # Check max absolute value is 1.0
        assert np.abs(result).max() == pytest.approx(1.0)
        # Check proportions are preserved
        assert result[0] == pytest.approx(-1.0)
        assert result[-1] == pytest.approx(1.0)

    def test_basic_2d(self):
        """Test minmax normalization on 2D signal."""
        signal = np.random.randn(5, 50) * 10
        result = scitex.dsp.norm.minmax(signal, dim=-1)
        
        # Check each row's max absolute value is 1.0
        max_abs_per_row = np.abs(result).max(axis=-1)
        assert np.allclose(max_abs_per_row, 1.0)

    def test_basic_3d(self):
        """Test minmax normalization on 3D signal."""
        signal = np.random.randn(3, 4, 50) * 5
        result = scitex.dsp.norm.minmax(signal, dim=-1)
        
        # Check shape preserved
        assert result.shape == signal.shape
        
        # Check normalization along last dimension
        flat_result = result.reshape(-1, 50)
        for row in flat_result:
            assert np.abs(row).max() == pytest.approx(1.0)

    def test_amplitude_scaling(self):
        """Test amplitude parameter."""
        signal = np.array([-4.0, -2.0, 0.0, 2.0, 4.0])
        
        # Test amp=2.0
        result = scitex.dsp.norm.minmax(signal, amp=2.0)
        assert np.abs(result).max() == pytest.approx(2.0)
        
        # Test amp=0.5
        result = scitex.dsp.norm.minmax(signal, amp=0.5)
        assert np.abs(result).max() == pytest.approx(0.5)

    def test_different_dimensions(self):
        """Test normalization along different dimensions."""
        signal = np.random.randn(4, 5, 6) * 3
        
        # Test along each dimension
        for dim in [0, 1, 2, -1]:
            result = scitex.dsp.norm.minmax(signal, dim=dim)
            # Get max absolute values along the specified dimension
            max_vals = np.abs(result).max(axis=dim)
            assert np.allclose(max_vals, 1.0)

    def test_positive_only_signal(self):
        """Test with positive-only signal."""
        signal = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        result = scitex.dsp.norm.minmax(signal)
        
        assert result.max() == pytest.approx(1.0)
        assert result.min() == pytest.approx(0.2)  # 1/5

    def test_negative_only_signal(self):
        """Test with negative-only signal."""
        signal = np.array([-5.0, -4.0, -3.0, -2.0, -1.0])
        result = scitex.dsp.norm.minmax(signal)
        
        assert result.min() == pytest.approx(-1.0)
        assert result.max() == pytest.approx(-0.2)  # -1/5

    def test_symmetric_signal(self):
        """Test with symmetric signal."""
        signal = np.array([-3.0, -1.0, 0.0, 1.0, 3.0])
        result = scitex.dsp.norm.minmax(signal)
        
        assert result.min() == pytest.approx(-1.0)
        assert result.max() == pytest.approx(1.0)
        assert result[2] == pytest.approx(0.0)  # Middle value stays 0

    def test_torch_input(self):
        """Test with PyTorch tensor input."""
        signal = torch.randn(5, 50) * 10
        result = scitex.dsp.norm.minmax(signal)
        
        assert isinstance(result, torch.Tensor)
        max_abs_per_row = torch.abs(result).max(dim=-1)[0]
        assert torch.allclose(max_abs_per_row, torch.ones_like(max_abs_per_row))

    def test_zero_signal(self):
        """Test with zero signal."""
        signal = np.zeros((5, 10))
        with pytest.warns(RuntimeWarning):
            result = scitex.dsp.norm.minmax(signal)
            # Should handle division by zero
            assert np.all(np.isnan(result)) or np.all(np.isinf(result))

    def test_preserves_shape(self):
        """Test that function preserves input shape."""
        shapes = [(10,), (5, 20), (3, 4, 50), (2, 3, 4, 100)]
        for shape in shapes:
            signal = np.random.randn(*shape) * 5
            result = scitex.dsp.norm.minmax(signal)
            assert result.shape == signal.shape

    def test_edge_cases(self):
        """Test edge cases."""
        # Single value
        signal = np.array([5.0])
        result = scitex.dsp.norm.minmax(signal)
        assert result[0] == pytest.approx(1.0)
        
        # Two values with same absolute value
        signal = np.array([-2.0, 2.0])
        result = scitex.dsp.norm.minmax(signal)
        assert result[0] == pytest.approx(-1.0)
        assert result[1] == pytest.approx(1.0)


if __name__ == "__main__":
    import os

    pytest.main([os.path.abspath(__file__), "-v"])

# --------------------------------------------------------------------------------
# Start of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/dsp/norm.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-04-05 12:15:42 (ywatanabe)"
#
# import torch as _torch
# from ..decorators import torch_fn as _torch_fn
#
#
# @_torch_fn
# def z(x, dim=-1):
#     return (x - x.mean(dim=dim, keepdim=True)) / x.std(dim=dim, keepdim=True)
#
#
# @_torch_fn
# def minmax(x, amp=1.0, dim=-1, fn="mean"):
#     MM = x.max(dim=dim, keepdims=True)[0].abs()
#     mm = x.min(dim=dim, keepdims=True)[0].abs()
#     return amp * x / _torch.maximum(MM, mm)

# --------------------------------------------------------------------------------
# End of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/dsp/norm.py
# --------------------------------------------------------------------------------
