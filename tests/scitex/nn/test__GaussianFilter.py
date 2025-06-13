#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-01 00:00:00 (ywatanabe)"
# Tests for GaussianFilter layer

import math
import pytest
import torch
import torch.nn as nn
import numpy as np
from scitex.nn import GaussianFilter


class TestGaussianFilter:
    """Comprehensive test suite for GaussianFilter layer."""

    def test_initialization_default_sigma(self):
        """Test GaussianFilter initialization with default sigma."""
        radius = 5
        gf = GaussianFilter(radius)
        assert gf.radius == radius
        assert hasattr(gf, "kernel")
        assert gf.kernel.shape == (1, 1, 2 * radius + 1)

    def test_initialization_custom_sigma(self):
        """Test GaussianFilter initialization with custom sigma."""
        radius = 5
        sigma = 2.0
        gf = GaussianFilter(radius, sigma=sigma)
        assert gf.radius == radius
        assert hasattr(gf, "kernel")
        assert gf.kernel.shape == (1, 1, 2 * radius + 1)

    def test_kernel_generation_properties(self):
        """Test properties of generated Gaussian kernel."""
        radius = 5
        sigma = 2.0
        kernel = GaussianFilter.gen_kernel_1d(radius, sigma)
        
        # Check shape
        assert kernel.shape == (1, 1, 2 * radius + 1)
        
        # Check normalization (sum should be 1)
        assert torch.allclose(kernel.sum(), torch.tensor(1.0), atol=1e-6)
        
        # Check symmetry
        kernel_1d = kernel.squeeze()
        assert torch.allclose(kernel_1d, kernel_1d.flip(0), atol=1e-6)
        
        # Check peak at center
        assert kernel_1d[radius] == kernel_1d.max()

    def test_forward_1d_input(self):
        """Test forward pass with 1D input tensor."""
        radius = 3
        gf = GaussianFilter(radius)
        x = torch.randn(20)
        y = gf(x)
        
        # Output should be 3D: (1, 1, seq_len)
        assert y.shape == (1, 1, 20)

    def test_forward_2d_input(self):
        """Test forward pass with 2D input tensor."""
        radius = 3
        gf = GaussianFilter(radius)
        x = torch.randn(5, 20)  # (batch_size, seq_len)
        y = gf(x)
        
        # Output should be 3D: (batch_size, 1, seq_len)
        assert y.shape == (5, 1, 20)

    def test_forward_3d_input(self):
        """Test forward pass with 3D input tensor."""
        radius = 3
        gf = GaussianFilter(radius)
        x = torch.randn(4, 3, 100)  # (batch_size, n_channels, seq_len)
        y = gf(x)
        
        # Output should maintain shape
        assert y.shape == x.shape

    def test_multi_channel_processing(self):
        """Test that filter processes multiple channels independently."""
        radius = 5
        gf = GaussianFilter(radius)
        
        # Create input with distinct channels
        x = torch.zeros(2, 3, 50)
        x[:, 0, 25] = 1.0  # Spike in channel 0
        x[:, 1, 30] = 1.0  # Spike in channel 1
        x[:, 2, 35] = 1.0  # Spike in channel 2
        
        y = gf(x)
        
        # Each channel should be smoothed independently
        assert y.shape == x.shape
        # Peak locations should be preserved
        assert y[0, 0].argmax() == 25
        assert y[0, 1].argmax() == 30
        assert y[0, 2].argmax() == 35

    def test_edge_handling(self):
        """Test edge handling with padding."""
        radius = 3
        gf = GaussianFilter(radius)
        x = torch.ones(1, 1, 20)
        y = gf(x)
        
        # Output length should be preserved due to padding
        assert y.shape[-1] == x.shape[-1]
        
        # Center values should be close to 1 (due to smoothing of constant signal)
        assert torch.allclose(y[:, :, radius:-radius], torch.ones_like(y[:, :, radius:-radius]), atol=0.01)

    def test_different_kernel_sizes(self):
        """Test with various kernel sizes."""
        for radius in [1, 3, 5, 10, 20]:
            gf = GaussianFilter(radius)
            x = torch.randn(2, 3, 100)
            y = gf(x)
            assert y.shape == x.shape

    def test_different_sigma_values(self):
        """Test with various sigma values."""
        radius = 5
        x = torch.randn(2, 3, 100)
        
        for sigma in [0.5, 1.0, 2.0, 5.0, 10.0]:
            gf = GaussianFilter(radius, sigma=sigma)
            y = gf(x)
            assert y.shape == x.shape

    def test_smoothing_effect(self):
        """Test that filter actually smooths the signal."""
        radius = 5
        gf = GaussianFilter(radius)
        
        # Create noisy signal
        x = torch.randn(1, 1, 100)
        y = gf(x)
        
        # Smoothed signal should have lower variance
        x_var = x.var().item()
        y_var = y.var().item()
        assert y_var < x_var

    def test_impulse_response(self):
        """Test impulse response of the filter."""
        radius = 5
        gf = GaussianFilter(radius)
        
        # Create impulse
        x = torch.zeros(1, 1, 50)
        x[0, 0, 25] = 1.0
        
        y = gf(x)
        
        # Response should be the Gaussian kernel centered at impulse
        kernel = gf.kernel.squeeze()
        expected = torch.zeros_like(y.squeeze())
        expected[25-radius:25+radius+1] = kernel
        
        assert torch.allclose(y.squeeze(), expected, atol=1e-5)

    def test_frequency_response(self):
        """Test frequency response characteristics."""
        radius = 10
        gf = GaussianFilter(radius)
        
        # Generate signals of different frequencies
        t = torch.linspace(0, 1, 1000).unsqueeze(0).unsqueeze(0)
        
        # Low frequency - should pass through
        low_freq = torch.sin(2 * math.pi * 5 * t)
        low_filtered = gf(low_freq)
        assert torch.allclose(low_filtered, low_freq, atol=0.1)
        
        # High frequency - should be attenuated
        high_freq = torch.sin(2 * math.pi * 100 * t)
        high_filtered = gf(high_freq)
        assert high_filtered.abs().max() < high_freq.abs().max() * 0.5

    def test_gradient_flow(self):
        """Test that gradients flow through the layer."""
        radius = 5
        gf = GaussianFilter(radius)
        x = torch.randn(2, 3, 50, requires_grad=True)
        
        y = gf(x)
        loss = y.sum()
        loss.backward()
        
        assert x.grad is not None
        assert not torch.allclose(x.grad, torch.zeros_like(x.grad))

    def test_device_compatibility(self):
        """Test operation on different devices."""
        if not torch.cuda.is_available():
            pytest.skip("CUDA not available")
        
        radius = 5
        gf = GaussianFilter(radius).cuda()
        x = torch.randn(2, 3, 50).cuda()
        
        y = gf(x)
        assert y.device == x.device
        assert y.shape == x.shape

    def test_dtype_compatibility(self):
        """Test operation with different data types."""
        radius = 5
        gf = GaussianFilter(radius)
        
        for dtype in [torch.float32, torch.float64]:
            x = torch.randn(2, 3, 50, dtype=dtype)
            y = gf(x)
            assert y.dtype == x.dtype

    def test_batch_consistency(self):
        """Test that batch processing is consistent."""
        radius = 5
        gf = GaussianFilter(radius)
        
        # Single sample
        x_single = torch.randn(1, 3, 50)
        y_single = gf(x_single)
        
        # Batch of same samples
        x_batch = x_single.repeat(4, 1, 1)
        y_batch = gf(x_batch)
        
        # All batch elements should be identical
        for i in range(4):
            assert torch.allclose(y_batch[i], y_single[0])

    def test_zero_radius(self):
        """Test with zero radius (should act as identity)."""
        gf = GaussianFilter(0)
        x = torch.randn(2, 3, 50)
        y = gf(x)
        
        # With radius 0, kernel should be [1], acting as identity
        assert torch.allclose(y, x, atol=1e-5)

    def test_large_radius(self):
        """Test with large radius relative to signal length."""
        radius = 40
        gf = GaussianFilter(radius)
        x = torch.randn(1, 1, 50)
        
        # Should still work without errors
        y = gf(x)
        assert y.shape == x.shape

    def test_integration_with_nn_sequential(self):
        """Test integration with PyTorch Sequential model."""
        model = nn.Sequential(
            nn.Conv1d(3, 16, 3, padding=1),
            nn.ReLU(),
            GaussianFilter(radius=5),
            nn.Conv1d(16, 8, 3, padding=1),
        )
        
        x = torch.randn(4, 3, 100)
        y = model(x)
        assert y.shape == (4, 8, 100)

    def test_state_dict_save_load(self):
        """Test saving and loading model state."""
        radius = 5
        sigma = 3.0
        gf1 = GaussianFilter(radius, sigma)
        
        # Save state
        state = gf1.state_dict()
        
        # Create new instance and load state
        gf2 = GaussianFilter(radius, sigma)
        gf2.load_state_dict(state)
        
        # Kernels should be identical
        assert torch.allclose(gf1.kernel, gf2.kernel)

    def test_numerical_stability(self):
        """Test numerical stability with extreme values."""
        radius = 5
        gf = GaussianFilter(radius)
        
        # Very large values
        x_large = torch.ones(1, 1, 50) * 1e6
        y_large = gf(x_large)
        assert torch.isfinite(y_large).all()
        
        # Very small values
        x_small = torch.ones(1, 1, 50) * 1e-6
        y_small = gf(x_small)
        assert torch.isfinite(y_small).all()

    def test_signal_energy_preservation(self):
        """Test approximate energy preservation for smooth signals."""
        radius = 5
        gf = GaussianFilter(radius)
        
        # Smooth signal (low frequency)
        t = torch.linspace(0, 2*math.pi, 100).unsqueeze(0).unsqueeze(0)
        x = torch.sin(t)
        y = gf(x)
        
        # Energy should be approximately preserved for smooth signals
        x_energy = (x ** 2).sum()
        y_energy = (y ** 2).sum()
        assert torch.allclose(x_energy, y_energy, rtol=0.1)

    def test_causality_check(self):
        """Test that filter maintains causality in padding."""
        radius = 5
        gf = GaussianFilter(radius)
        
        # Step function
        x = torch.zeros(1, 1, 50)
        x[:, :, 25:] = 1.0
        
        y = gf(x)
        
        # Transition should be smooth around step location
        diff = torch.diff(y.squeeze())
        max_diff_idx = diff.argmax()
        assert abs(max_diff_idx.item() - 24) <= radius


if __name__ == "__main__":
    import os
    pytest.main([os.path.abspath(__file__)])
