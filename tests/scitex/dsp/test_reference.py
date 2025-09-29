import pytest
import numpy as np
import torch
import scitex


class TestCommonAverage:
    """Test common average referencing function."""

    def test_import(self):
        """Test function can be imported."""
        assert hasattr(scitex.dsp.reference, "common_average")

    def test_basic_2d(self):
        """Test common average on 2D signal."""
        # Create multichannel signal
        signal = np.random.randn(10, 100)  # 10 channels, 100 samples
        result = scitex.dsp.reference.common_average(signal, dim=0)
        
        # Check mean across channels is zero
        assert np.abs(np.mean(result, axis=0)).max() < 1e-10
        # Check std across channels is 1
        assert np.abs(np.std(result, axis=0, ddof=0) - 1.0).max() < 1e-10

    def test_basic_3d(self):
        """Test common average on 3D signal (trials, channels, time)."""
        signal = np.random.randn(5, 10, 100)  # 5 trials, 10 channels, 100 samples
        result = scitex.dsp.reference.common_average(signal, dim=-2)
        
        # Check shape preserved
        assert result.shape == signal.shape
        
        # Check each trial is properly referenced
        for trial in range(5):
            trial_result = result[trial]
            assert np.abs(np.mean(trial_result, axis=0)).max() < 1e-10
            assert np.abs(np.std(trial_result, axis=0, ddof=0) - 1.0).max() < 1e-10

    def test_different_dimensions(self):
        """Test referencing along different dimensions."""
        signal = np.random.randn(4, 5, 6, 100)
        
        # Test along different dims
        for dim in [0, 1, 2, -2]:
            result = scitex.dsp.reference.common_average(signal, dim=dim)
            assert result.shape == signal.shape
            
            # Check normalization along specified dimension
            mean_vals = np.mean(result, axis=dim)
            std_vals = np.std(result, axis=dim, ddof=0)
            assert np.abs(mean_vals).max() < 1e-10
            assert np.abs(std_vals - 1.0).max() < 1e-10

    def test_preserves_shape(self):
        """Test that function preserves input shape."""
        shapes = [(10, 100), (5, 10, 100), (2, 5, 10, 100)]
        for shape in shapes:
            signal = np.random.randn(*shape)
            result = scitex.dsp.reference.common_average(signal)
            assert result.shape == signal.shape

    def test_torch_input(self):
        """Test with PyTorch tensor input."""
        signal = torch.randn(8, 64, 1000)
        result = scitex.dsp.reference.common_average(signal, dim=1)
        
        assert isinstance(result, torch.Tensor)
        assert result.shape == signal.shape
        
        # Check normalization
        mean_vals = torch.mean(result, dim=1)
        std_vals = torch.std(result, dim=1, unbiased=False)
        assert torch.abs(mean_vals).max() < 1e-6
        assert torch.abs(std_vals - 1.0).max() < 1e-6

    def test_constant_channels(self):
        """Test with constant values across channels."""
        signal = np.ones((5, 100))
        with pytest.warns(RuntimeWarning):
            result = scitex.dsp.reference.common_average(signal, dim=0)
            # Should handle division by zero
            assert np.all(np.isnan(result)) or np.all(np.isinf(result))


class TestRandom:
    """Test random channel referencing function."""

    def test_import(self):
        """Test function can be imported."""
        assert hasattr(scitex.dsp.reference, "random")

    def test_basic_2d(self):
        """Test random reference on 2D signal."""
        np.random.seed(42)
        signal = np.random.randn(10, 100)
        result = scitex.dsp.reference.random(signal, dim=0)
        
        # Check shape preserved
        assert result.shape == signal.shape
        
        # Check that at least one channel is zero (self-referenced)
        zero_channels = np.all(np.abs(result) < 1e-10, axis=1)
        assert np.any(zero_channels)

    def test_basic_3d(self):
        """Test random reference on 3D signal."""
        signal = np.random.randn(5, 10, 100)
        result = scitex.dsp.reference.random(signal, dim=1)
        
        assert result.shape == signal.shape
        
        # Each trial should have one zero channel
        for trial in range(5):
            trial_result = result[trial]
            zero_channels = np.all(np.abs(trial_result) < 1e-10, axis=1)
            assert np.any(zero_channels)

    def test_different_dimensions(self):
        """Test referencing along different dimensions."""
        signal = np.random.randn(4, 5, 6)
        
        for dim in [0, 1, 2]:
            result = scitex.dsp.reference.random(signal, dim=dim)
            assert result.shape == signal.shape
            
            # Check structure along dimension
            # Should have one zero slice along the dimension
            axes = list(range(signal.ndim))
            axes.remove(dim)
            zero_slices = np.all(np.abs(result) < 1e-10, axis=tuple(axes))
            assert np.any(zero_slices)

    def test_torch_input(self):
        """Test with PyTorch tensor input."""
        torch.manual_seed(42)
        signal = torch.randn(8, 64, 1000)
        result = scitex.dsp.reference.random(signal, dim=1)
        
        assert isinstance(result, torch.Tensor)
        assert result.shape == signal.shape

    def test_randomness(self):
        """Test that function produces different results on different calls."""
        signal = np.random.randn(10, 100)
        
        # Get multiple results
        results = []
        for _ in range(5):
            results.append(scitex.dsp.reference.random(signal, dim=0))
        
        # Check that results are different
        all_different = True
        for i in range(len(results)):
            for j in range(i + 1, len(results)):
                if np.allclose(results[i], results[j]):
                    all_different = False
                    break
        
        assert all_different, "Random reference should produce different results"

    def test_preserves_shape(self):
        """Test that function preserves input shape."""
        shapes = [(10, 100), (5, 10, 100), (2, 5, 10, 100)]
        for shape in shapes:
            signal = np.random.randn(*shape)
            result = scitex.dsp.reference.random(signal)
            assert result.shape == signal.shape


class TestTakeReference:
    """Test specific channel referencing function."""

    def test_import(self):
        """Test function can be imported."""
        assert hasattr(scitex.dsp.reference, "take_reference")

    def test_basic_2d(self):
        """Test reference to specific channel on 2D signal."""
        signal = np.random.randn(10, 100)
        ref_channel = 3
        
        result = scitex.dsp.reference.take_reference(signal, ref_channel, dim=0)
        
        # Check shape preserved
        assert result.shape == signal.shape
        
        # Check reference channel is zero
        assert np.allclose(result[ref_channel], 0)
        
        # Check other channels are correctly referenced
        for ch in range(10):
            if ch != ref_channel:
                expected = signal[ch] - signal[ref_channel]
                assert np.allclose(result[ch], expected)

    def test_basic_3d(self):
        """Test reference to specific channel on 3D signal."""
        signal = np.random.randn(5, 10, 100)
        ref_channel = 7
        
        result = scitex.dsp.reference.take_reference(signal, ref_channel, dim=1)
        
        assert result.shape == signal.shape
        
        # Check each trial
        for trial in range(5):
            # Reference channel should be zero
            assert np.allclose(result[trial, ref_channel], 0)
            
            # Other channels correctly referenced
            for ch in range(10):
                if ch != ref_channel:
                    expected = signal[trial, ch] - signal[trial, ref_channel]
                    assert np.allclose(result[trial, ch], expected)

    def test_different_dimensions(self):
        """Test referencing along different dimensions."""
        signal = np.random.randn(4, 5, 6, 7)
        
        # Test along each dimension
        for dim in range(4):
            ref_idx = 2
            result = scitex.dsp.reference.take_reference(signal, ref_idx, dim=dim)
            
            assert result.shape == signal.shape
            
            # Create index to check reference slice is zero
            idx = [slice(None)] * 4
            idx[dim] = ref_idx
            assert np.allclose(result[tuple(idx)], 0)

    def test_negative_dimension(self):
        """Test with negative dimension indices."""
        signal = np.random.randn(3, 4, 5, 6)
        
        # Test dim=-2 (equivalent to dim=2)
        ref_idx = 1
        result = scitex.dsp.reference.take_reference(signal, ref_idx, dim=-2)
        
        assert result.shape == signal.shape
        assert np.allclose(result[:, :, ref_idx, :], 0)

    def test_edge_indices(self):
        """Test with edge case reference indices."""
        signal = np.random.randn(10, 100)
        
        # First channel
        result = scitex.dsp.reference.take_reference(signal, 0, dim=0)
        assert np.allclose(result[0], 0)
        
        # Last channel
        result = scitex.dsp.reference.take_reference(signal, 9, dim=0)
        assert np.allclose(result[9], 0)

    def test_torch_input(self):
        """Test with PyTorch tensor input."""
        signal = torch.randn(8, 64, 1000)
        ref_channel = 32
        
        result = scitex.dsp.reference.take_reference(signal, ref_channel, dim=1)
        
        assert isinstance(result, torch.Tensor)
        assert result.shape == signal.shape
        assert torch.allclose(result[:, ref_channel, :], torch.zeros_like(result[:, ref_channel, :]))

    def test_preserves_shape(self):
        """Test that function preserves input shape."""
        shapes = [(10, 100), (5, 10, 100), (2, 5, 10, 100)]
        for shape in shapes:
            signal = np.random.randn(*shape)
            result = scitex.dsp.reference.take_reference(signal, 0)
            assert result.shape == signal.shape

    def test_invalid_index(self):
        """Test with invalid reference index."""
        signal = np.random.randn(10, 100)
        
        # This should raise an error
        with pytest.raises((IndexError, RuntimeError, AssertionError)):
            scitex.dsp.reference.take_reference(signal, 10, dim=0)  # Out of bounds

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/dsp/reference.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "ywatanabe (2024-11-02 22:48:44)"
# # File: ./scitex_repo/src/scitex/dsp/reference.py
# 
# import torch as _torch
# from ..decorators import torch_fn as _torch_fn
# 
# 
# @_torch_fn
# def common_average(x, dim=-2):
#     re_referenced = (x - x.mean(dim=dim, keepdims=True)) / x.std(dim=dim, keepdims=True)
#     assert x.shape == re_referenced.shape
#     return re_referenced
# 
# 
# @_torch_fn
# def random(x, dim=-2):
#     idx_all = [slice(None)] * x.ndim
#     idx_rand_dim = _torch.randperm(x.shape[dim])
#     idx_all[dim] = idx_rand_dim
#     y = x[idx_all]
#     re_referenced = x - y
#     assert x.shape == re_referenced.shape
#     return re_referenced
# 
# 
# @_torch_fn
# def take_reference(x, tgt_indi, dim=-2):
#     idx_all = [slice(None)] * x.ndim
#     idx_all[dim] = tgt_indi
#     re_referenced = x - x[tgt_indi]
#     assert x.shape == re_referenced.shape
#     return re_referenced
# 
# 
# if __name__ == "__main__":
#     import scitex
# 
#     x, f, t = scitex.dsp.demo_sig()
#     y = common_average(x)
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/dsp/reference.py
# --------------------------------------------------------------------------------
