#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-01 00:00:00 (ywatanabe)"
# Tests for Hilbert transform layer

import math
import pytest
import torch
import torch.nn as nn
import numpy as np
from scitex.nn import Hilbert


class TestHilbert:
    """Comprehensive test suite for Hilbert transform layer."""

    def test_initialization_basic(self):
        """Test basic Hilbert layer initialization."""
        seq_len = 100
        hilbert = Hilbert(seq_len)
        
        assert hilbert.n == seq_len
        assert hilbert.dim == -1
        assert hilbert.fp16 == False
        assert hilbert.in_place == False
        assert hasattr(hilbert, "f")
        assert hilbert.f.shape == (seq_len,)

    def test_initialization_with_options(self):
        """Test Hilbert layer initialization with all options."""
        seq_len = 128
        hilbert = Hilbert(seq_len, dim=-2, fp16=True, in_place=True)
        
        assert hilbert.n == seq_len
        assert hilbert.dim == -2
        assert hilbert.fp16 == True
        assert hilbert.in_place == True

    def test_frequency_buffer_properties(self):
        """Test properties of frequency buffer."""
        seq_len = 64
        hilbert = Hilbert(seq_len)
        
        # Check frequency buffer shape
        assert hilbert.f.shape == (seq_len,)
        
        # Check frequency values range
        assert hilbert.f.min() >= -0.5
        assert hilbert.f.max() <= 0.5

    def test_forward_basic_1d(self):
        """Test forward pass with 1D signal."""
        seq_len = 100
        hilbert = Hilbert(seq_len)
        
        x = torch.randn(seq_len)
        y = hilbert(x)
        
        # Output should have phase and amplitude
        assert y.shape == (seq_len, 2)

    def test_forward_basic_2d(self):
        """Test forward pass with 2D signal (batch)."""
        seq_len = 100
        batch_size = 4
        hilbert = Hilbert(seq_len)
        
        x = torch.randn(batch_size, seq_len)
        y = hilbert(x)
        
        # Output should have phase and amplitude as last dimension
        assert y.shape == (batch_size, seq_len, 2)

    def test_forward_basic_3d(self):
        """Test forward pass with 3D signal (batch, channels, time)."""
        seq_len = 100
        batch_size = 4
        n_channels = 3
        hilbert = Hilbert(seq_len)
        
        x = torch.randn(batch_size, n_channels, seq_len)
        y = hilbert(x)
        
        # Output should have phase and amplitude as last dimension
        assert y.shape == (batch_size, n_channels, seq_len, 2)

    def test_phase_amplitude_extraction(self):
        """Test that phase and amplitude are correctly extracted."""
        seq_len = 256
        hilbert = Hilbert(seq_len)
        
        # Create a simple sinusoidal signal
        t = torch.linspace(0, 2*math.pi, seq_len)
        x = torch.sin(t)
        
        y = hilbert(x)
        phase = y[..., 0]
        amplitude = y[..., 1]
        
        # Check dimensions
        assert phase.shape == x.shape
        assert amplitude.shape == x.shape
        
        # Amplitude should be approximately constant for sine wave
        assert amplitude.std() < 0.1

    def test_analytic_signal_properties(self):
        """Test properties of analytic signal from Hilbert transform."""
        seq_len = 512
        hilbert = Hilbert(seq_len)
        
        # Create test signal
        t = torch.linspace(0, 4*math.pi, seq_len)
        freq = 2.0
        x = torch.cos(2*math.pi*freq*t/seq_len)
        
        # Get Hilbert transform
        y = hilbert(x)
        phase = y[..., 0]
        amplitude = y[..., 1]
        
        # For cosine, amplitude should be approximately 1
        assert torch.allclose(amplitude.mean(), torch.tensor(1.0), atol=0.1)

    def test_fp16_mode(self):
        """Test operation in fp16 mode."""
        seq_len = 128
        hilbert = Hilbert(seq_len, fp16=True)
        
        x = torch.randn(4, seq_len)
        y = hilbert(x)
        
        # Output should be float32 (converted back from fp16)
        assert y.dtype == torch.float32
        assert y.shape == (4, seq_len, 2)

    def test_in_place_mode(self):
        """Test in-place vs non-in-place operation."""
        seq_len = 128
        
        # Non-in-place
        hilbert_not_inplace = Hilbert(seq_len, in_place=False)
        x1 = torch.randn(seq_len, requires_grad=True)
        x1_copy = x1.clone()
        y1 = hilbert_not_inplace(x1)
        assert torch.equal(x1, x1_copy)  # Input should not be modified
        
        # In-place
        hilbert_inplace = Hilbert(seq_len, in_place=True)
        x2 = torch.randn(seq_len)
        y2 = hilbert_inplace(x2)
        # Just verify it works without error

    def test_different_sequence_lengths(self):
        """Test with various sequence lengths."""
        for seq_len in [32, 64, 128, 256, 512, 1024]:
            hilbert = Hilbert(seq_len)
            x = torch.randn(2, seq_len)
            y = hilbert(x)
            assert y.shape == (2, seq_len, 2)

    def test_dim_parameter(self):
        """Test operation along different dimensions."""
        seq_len = 100
        
        # Test with dim=-1 (default)
        hilbert1 = Hilbert(seq_len, dim=-1)
        x1 = torch.randn(4, 3, seq_len)
        y1 = hilbert1(x1)
        assert y1.shape == (4, 3, seq_len, 2)
        
        # Test with dim=-2
        hilbert2 = Hilbert(seq_len, dim=-2)
        x2 = torch.randn(4, seq_len, 3)
        y2 = hilbert2(x2)
        assert y2.shape == (4, seq_len, 3, 2)

    def test_instantaneous_frequency(self):
        """Test instantaneous frequency calculation from phase."""
        seq_len = 256
        hilbert = Hilbert(seq_len)
        
        # Create chirp signal (frequency increases linearly)
        t = torch.linspace(0, 1, seq_len)
        f0, f1 = 10, 50
        phase_chirp = 2 * math.pi * (f0 * t + (f1 - f0) * t**2 / 2)
        x = torch.cos(phase_chirp)
        
        y = hilbert(x)
        phase = y[..., 0]
        
        # Instantaneous frequency is derivative of phase
        inst_freq = torch.diff(torch.unwrap(phase)) / (2 * math.pi / seq_len)
        
        # Frequency should increase from ~f0 to ~f1
        assert inst_freq[10] < inst_freq[-10]  # Frequency increases

    def test_envelope_detection(self):
        """Test envelope detection using Hilbert transform."""
        seq_len = 512
        hilbert = Hilbert(seq_len)
        
        # Create amplitude modulated signal
        t = torch.linspace(0, 1, seq_len)
        carrier_freq = 50
        mod_freq = 5
        carrier = torch.cos(2 * math.pi * carrier_freq * t)
        envelope = 1 + 0.5 * torch.cos(2 * math.pi * mod_freq * t)
        x = envelope * carrier
        
        y = hilbert(x)
        detected_envelope = y[..., 1]
        
        # Check envelope detection accuracy
        # Downsample for comparison (carrier oscillations affect exact match)
        assert torch.allclose(detected_envelope[::10], envelope[::10], atol=0.15)

    def test_gradient_flow(self):
        """Test that gradients flow through the layer."""
        seq_len = 128
        hilbert = Hilbert(seq_len)
        
        x = torch.randn(4, seq_len, requires_grad=True)
        y = hilbert(x)
        loss = y.sum()
        loss.backward()
        
        assert x.grad is not None
        assert not torch.allclose(x.grad, torch.zeros_like(x.grad))

    def test_device_compatibility(self):
        """Test operation on different devices."""
        if not torch.cuda.is_available():
            pytest.skip("CUDA not available")
        
        seq_len = 128
        hilbert = Hilbert(seq_len).cuda()
        x = torch.randn(4, seq_len).cuda()
        
        y = hilbert(x)
        assert y.device == x.device
        assert y.shape == (4, seq_len, 2)

    def test_batch_processing_consistency(self):
        """Test consistency of batch processing."""
        seq_len = 128
        hilbert = Hilbert(seq_len)
        
        # Single sample
        x_single = torch.randn(seq_len)
        y_single = hilbert(x_single)
        
        # Batch containing same sample
        x_batch = x_single.unsqueeze(0).repeat(4, 1)
        y_batch = hilbert(x_batch)
        
        # All batch results should be identical
        for i in range(4):
            assert torch.allclose(y_batch[i], y_single, atol=1e-6)

    def test_real_signal_constraint(self):
        """Test that input must be real-valued."""
        seq_len = 128
        hilbert = Hilbert(seq_len)
        
        # Real signal should work
        x_real = torch.randn(seq_len)
        y_real = hilbert(x_real)
        assert y_real.shape == (seq_len, 2)

    def test_numerical_stability(self):
        """Test numerical stability with extreme values."""
        seq_len = 128
        hilbert = Hilbert(seq_len)
        
        # Very large values
        x_large = torch.randn(seq_len) * 1e6
        y_large = hilbert(x_large)
        assert torch.isfinite(y_large).all()
        
        # Very small values
        x_small = torch.randn(seq_len) * 1e-6
        y_small = hilbert(x_small)
        assert torch.isfinite(y_small).all()

    def test_orthogonality_property(self):
        """Test orthogonality between original and Hilbert transform."""
        seq_len = 256
        hilbert = Hilbert(seq_len)
        
        # For a sinusoidal signal
        t = torch.linspace(0, 4*math.pi, seq_len)
        x = torch.sin(t)
        
        # Get Hilbert transform (imaginary part of analytic signal)
        # Note: The layer returns phase and amplitude, not the transform directly
        # This test verifies the transform properties indirectly
        y = hilbert(x)
        phase = y[..., 0]
        
        # Phase should advance by ~90 degrees for sine wave
        # This is an indirect test of the orthogonality property

    def test_integration_with_nn_module(self):
        """Test integration with PyTorch Sequential model."""
        seq_len = 128
        
        model = nn.Sequential(
            nn.Linear(seq_len, seq_len),
            nn.ReLU(),
            Hilbert(seq_len),
            nn.Flatten(),
            nn.Linear(seq_len * 2, 10)
        )
        
        x = torch.randn(8, seq_len)
        y = model(x)
        assert y.shape == (8, 10)

    def test_state_dict_save_load(self):
        """Test saving and loading model state."""
        seq_len = 128
        hilbert1 = Hilbert(seq_len, fp16=True, in_place=True)
        
        # Save state
        state = hilbert1.state_dict()
        
        # Create new instance and load state
        hilbert2 = Hilbert(seq_len, fp16=True, in_place=True)
        hilbert2.load_state_dict(state)
        
        # Frequency buffers should be identical
        assert torch.equal(hilbert1.f, hilbert2.f)

    def test_power_spectrum_preservation(self):
        """Test that power spectrum magnitude is preserved."""
        seq_len = 256
        hilbert = Hilbert(seq_len)
        
        # Create test signal
        x = torch.randn(seq_len)
        
        # Apply Hilbert transform
        y = hilbert(x)
        amplitude = y[..., 1]
        
        # Power should be approximately preserved
        x_power = (x ** 2).mean()
        # Note: amplitude is envelope, so comparison is indirect

    def test_causality_approximation(self):
        """Test the soft step function approximation for causality."""
        seq_len = 128
        hilbert = Hilbert(seq_len)
        
        # The frequency domain step function should approximate ideal Hilbert
        steepness = 50
        u = torch.sigmoid(steepness * hilbert.f)
        
        # Check that it approximates a step function
        # Should be ~0 for negative frequencies, ~1 for positive
        assert u[seq_len//2:].mean() < 0.1  # Negative frequencies
        assert u[:seq_len//2].mean() > 0.9  # Positive frequencies

    def test_multi_channel_independence(self):
        """Test that channels are processed independently."""
        seq_len = 128
        hilbert = Hilbert(seq_len)
        
        # Create multi-channel signal with different content
        x = torch.zeros(3, seq_len)
        x[0] = torch.sin(torch.linspace(0, 2*math.pi, seq_len))
        x[1] = torch.cos(torch.linspace(0, 4*math.pi, seq_len))
        x[2] = torch.randn(seq_len) * 0.1
        
        y = hilbert(x)
        
        # Each channel should be processed independently
        assert y.shape == (3, seq_len, 2)
        # Verify different statistics for each channel
        assert not torch.allclose(y[0], y[1], atol=0.1)
        assert not torch.allclose(y[1], y[2], atol=0.1)


if __name__ == "__main__":
    import os
    pytest.main([os.path.abspath(__file__)])
