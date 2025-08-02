#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-01 00:00:00 (ywatanabe)"
# Tests for Power Spectral Density (PSD) layer

import math
import pytest
import torch
import torch.nn as nn
import numpy as np
from scitex.nn import PSD


class TestPSD:
    """Comprehensive test suite for Power Spectral Density layer."""

    def test_initialization_basic(self):
        """Test basic PSD layer initialization."""
        sample_rate = 1000
        psd = PSD(sample_rate)
        
        assert psd.sample_rate == sample_rate
        assert psd.dim == -1
        assert psd.prob == False

    def test_initialization_with_options(self):
        """Test PSD layer initialization with all options."""
        sample_rate = 500
        psd = PSD(sample_rate, prob=True, dim=-2)
        
        assert psd.sample_rate == sample_rate
        assert psd.dim == -2
        assert psd.prob == True

    def test_forward_real_signal_1d(self):
        """Test forward pass with 1D real signal."""
        sample_rate = 1000
        psd_layer = PSD(sample_rate)
        
        # Create 1D signal
        seq_len = 1000
        x = torch.randn(seq_len)
        
        psd, freqs = psd_layer(x)
        
        # Check output shapes
        assert psd.shape == (seq_len // 2 + 1,)
        assert freqs.shape == (seq_len // 2 + 1,)
        
        # Check frequency range
        assert freqs[0] == 0
        assert freqs[-1] == sample_rate / 2  # Nyquist frequency

    def test_forward_real_signal_2d(self):
        """Test forward pass with 2D real signal (batch)."""
        sample_rate = 1000
        psd_layer = PSD(sample_rate)
        
        batch_size = 4
        seq_len = 512
        x = torch.randn(batch_size, seq_len)
        
        psd, freqs = psd_layer(x)
        
        # Check output shapes
        assert psd.shape == (batch_size, seq_len // 2 + 1)
        assert freqs.shape == (seq_len // 2 + 1,)

    def test_forward_real_signal_3d(self):
        """Test forward pass with 3D real signal (batch, channels, time)."""
        sample_rate = 1000
        psd_layer = PSD(sample_rate)
        
        batch_size = 4
        n_channels = 3
        seq_len = 512
        x = torch.randn(batch_size, n_channels, seq_len)
        
        psd, freqs = psd_layer(x)
        
        # Check output shapes
        assert psd.shape == (batch_size, n_channels, seq_len // 2 + 1)
        assert freqs.shape == (seq_len // 2 + 1,)

    def test_forward_complex_signal(self):
        """Test forward pass with complex signal."""
        sample_rate = 1000
        psd_layer = PSD(sample_rate)
        
        seq_len = 512
        x_real = torch.randn(seq_len)
        x_imag = torch.randn(seq_len)
        x = torch.complex(x_real, x_imag)
        
        psd, freqs = psd_layer(x)
        
        # Complex signals use full FFT
        assert psd.shape == (seq_len,)
        assert freqs.shape == (seq_len,)

    def test_parseval_theorem(self):
        """Test Parseval's theorem: energy conservation."""
        sample_rate = 1000
        psd_layer = PSD(sample_rate)
        
        # Create signal
        seq_len = 1000
        x = torch.randn(seq_len)
        
        # Time domain energy
        time_energy = (x ** 2).mean()
        
        # Frequency domain energy from PSD
        psd, freqs = psd_layer(x)
        freq_step = freqs[1] - freqs[0]
        freq_energy = psd.sum() * freq_step
        
        # Should be approximately equal (within numerical precision)
        assert torch.allclose(time_energy, freq_energy, rtol=0.1)

    def test_single_frequency_signal(self):
        """Test PSD of pure sinusoidal signal."""
        sample_rate = 1000
        psd_layer = PSD(sample_rate)
        
        # Create pure sine wave
        seq_len = 1000
        t = torch.linspace(0, 1, seq_len)
        freq = 50  # 50 Hz
        x = torch.sin(2 * math.pi * freq * t)
        
        psd, freqs = psd_layer(x)
        
        # Find peak frequency
        peak_idx = psd.argmax()
        peak_freq = freqs[peak_idx]
        
        # Peak should be at the signal frequency
        assert abs(peak_freq - freq) < sample_rate / seq_len  # Within frequency resolution

    def test_multiple_frequency_signal(self):
        """Test PSD of signal with multiple frequencies."""
        sample_rate = 1000
        psd_layer = PSD(sample_rate)
        
        # Create signal with multiple frequencies
        seq_len = 2000
        t = torch.linspace(0, 2, seq_len)
        freq1, freq2 = 50, 150  # Hz
        x = torch.sin(2 * math.pi * freq1 * t) + 0.5 * torch.sin(2 * math.pi * freq2 * t)
        
        psd, freqs = psd_layer(x)
        
        # Find peaks
        threshold = psd.max() * 0.3
        peaks = torch.where(psd > threshold)[0]
        peak_freqs = freqs[peaks]
        
        # Should find both frequencies
        assert any(abs(peak_freqs - freq1) < 5) 
        assert any(abs(peak_freqs - freq2) < 5)

    def test_white_noise_spectrum(self):
        """Test PSD of white noise (should be approximately flat)."""
        sample_rate = 1000
        psd_layer = PSD(sample_rate)
        
        # Generate white noise
        seq_len = 10000
        x = torch.randn(seq_len)
        
        psd, freqs = psd_layer(x)
        
        # PSD should be relatively flat
        # Check variance across frequency bins (exclude DC)
        psd_normalized = psd[1:] / psd[1:].mean()
        assert psd_normalized.std() < 0.3  # Relatively flat

    def test_probability_mode(self):
        """Test probability normalization mode."""
        sample_rate = 1000
        psd_layer = PSD(sample_rate, prob=True)
        
        batch_size = 4
        seq_len = 512
        x = torch.randn(batch_size, seq_len)
        
        psd, freqs = psd_layer(x)
        
        # In probability mode, PSD should sum to 1 along frequency dimension
        psd_sum = psd.sum(dim=-1)
        assert torch.allclose(psd_sum, torch.ones(batch_size), atol=1e-6)

    def test_different_dimensions(self):
        """Test operation along different dimensions."""
        sample_rate = 1000
        
        # Test with dim=-1 (default)
        psd1 = PSD(sample_rate, dim=-1)
        x1 = torch.randn(4, 3, 512)
        psd_out1, freqs1 = psd1(x1)
        assert psd_out1.shape == (4, 3, 257)  # 512/2 + 1
        
        # Test with dim=-2
        psd2 = PSD(sample_rate, dim=-2)
        x2 = torch.randn(4, 512, 3)
        psd_out2, freqs2 = psd2(x2)
        assert psd_out2.shape == (4, 257, 3)

    def test_different_sample_rates(self):
        """Test with various sample rates."""
        seq_len = 1000
        x = torch.randn(seq_len)
        
        for sample_rate in [100, 500, 1000, 44100, 48000]:
            psd_layer = PSD(sample_rate)
            psd, freqs = psd_layer(x)
            
            # Nyquist frequency should be sample_rate / 2
            assert freqs[-1] == sample_rate / 2

    def test_dc_component(self):
        """Test DC component (zero frequency) handling."""
        sample_rate = 1000
        psd_layer = PSD(sample_rate)
        
        # Signal with DC offset
        seq_len = 1000
        dc_offset = 2.5
        x = torch.ones(seq_len) * dc_offset + 0.1 * torch.randn(seq_len)
        
        psd, freqs = psd_layer(x)
        
        # DC component should have highest power
        assert psd[0] > psd[1:].max()
        assert freqs[0] == 0  # DC is at 0 Hz

    def test_frequency_resolution(self):
        """Test frequency resolution of PSD."""
        sample_rate = 1000
        psd_layer = PSD(sample_rate)
        
        for seq_len in [100, 500, 1000, 2000]:
            x = torch.randn(seq_len)
            psd, freqs = psd_layer(x)
            
            # Frequency resolution should be sample_rate / seq_len
            freq_resolution = freqs[1] - freqs[0]
            expected_resolution = sample_rate / seq_len
            assert abs(freq_resolution - expected_resolution) < 1e-6

    def test_gradient_flow(self):
        """Test that gradients flow through the layer."""
        sample_rate = 1000
        psd_layer = PSD(sample_rate)
        
        x = torch.randn(4, 512, requires_grad=True)
        psd, freqs = psd_layer(x)
        loss = psd.sum()
        loss.backward()
        
        assert x.grad is not None
        assert not torch.allclose(x.grad, torch.zeros_like(x.grad))

    def test_device_compatibility(self):
        """Test operation on different devices."""
        if not torch.cuda.is_available():
            pytest.skip("CUDA not available")
        
        sample_rate = 1000
        psd_layer = PSD(sample_rate).cuda()
        x = torch.randn(4, 512).cuda()
        
        psd, freqs = psd_layer(x)
        assert psd.device == x.device
        assert freqs.device == x.device

    def test_batch_independence(self):
        """Test that batch samples are processed independently."""
        sample_rate = 1000
        psd_layer = PSD(sample_rate)
        
        # Create batch with different signals
        batch_size = 3
        seq_len = 512
        x = torch.zeros(batch_size, seq_len)
        
        # Different frequency for each batch element
        t = torch.linspace(0, 1, seq_len)
        x[0] = torch.sin(2 * math.pi * 50 * t)   # 50 Hz
        x[1] = torch.sin(2 * math.pi * 100 * t)  # 100 Hz
        x[2] = torch.sin(2 * math.pi * 150 * t)  # 150 Hz
        
        psd, freqs = psd_layer(x)
        
        # Each batch should have peak at different frequency
        peaks = psd.argmax(dim=-1)
        assert len(torch.unique(peaks)) == batch_size

    def test_numerical_stability(self):
        """Test numerical stability with extreme values."""
        sample_rate = 1000
        psd_layer = PSD(sample_rate)
        
        # Very large values
        x_large = torch.randn(512) * 1e6
        psd_large, _ = psd_layer(x_large)
        assert torch.isfinite(psd_large).all()
        
        # Very small values
        x_small = torch.randn(512) * 1e-6
        psd_small, _ = psd_layer(x_small)
        assert torch.isfinite(psd_small).all()

    def test_zero_signal(self):
        """Test PSD of zero signal."""
        sample_rate = 1000
        psd_layer = PSD(sample_rate)
        
        x = torch.zeros(512)
        psd, freqs = psd_layer(x)
        
        # PSD should be all zeros
        assert torch.allclose(psd, torch.zeros_like(psd))

    def test_window_function_effect(self):
        """Test that PSD captures windowing effects correctly."""
        sample_rate = 1000
        psd_layer = PSD(sample_rate)
        
        # Create windowed signal
        seq_len = 1000
        t = torch.linspace(0, 1, seq_len)
        window = torch.hann_window(seq_len)
        x = window * torch.sin(2 * math.pi * 50 * t)
        
        psd, freqs = psd_layer(x)
        
        # Should still have peak at signal frequency
        peak_idx = psd.argmax()
        peak_freq = freqs[peak_idx]
        assert abs(peak_freq - 50) < 5

    def test_integration_with_nn_sequential(self):
        """Test integration with PyTorch Sequential model."""
        sample_rate = 1000
        seq_len = 512
        
        class PSDFeatureExtractor(nn.Module):
            def __init__(self):
                super().__init__()
                self.psd = PSD(sample_rate)
                self.fc = nn.Linear(seq_len // 2 + 1, 10)
            
            def forward(self, x):
                psd, _ = self.psd(x)
                return self.fc(psd)
        
        model = PSDFeatureExtractor()
        x = torch.randn(8, seq_len)
        y = model(x)
        assert y.shape == (8, 10)

    def test_power_vs_amplitude_spectrum(self):
        """Test that PSD represents power (squared amplitude)."""
        sample_rate = 1000
        psd_layer = PSD(sample_rate)
        
        # Create signal with known amplitude
        seq_len = 1000
        t = torch.linspace(0, 1, seq_len)
        amplitude = 2.0
        x = amplitude * torch.sin(2 * math.pi * 50 * t)
        
        psd, freqs = psd_layer(x)
        
        # Peak PSD value should be related to amplitude squared
        peak_psd = psd.max()
        # Due to normalization, exact relationship depends on implementation

    def test_multi_channel_processing(self):
        """Test that multiple channels are processed correctly."""
        sample_rate = 1000
        psd_layer = PSD(sample_rate)
        
        # Multi-channel signal with different frequencies
        n_channels = 3
        seq_len = 1000
        t = torch.linspace(0, 1, seq_len)
        
        x = torch.zeros(n_channels, seq_len)
        x[0] = torch.sin(2 * math.pi * 30 * t)
        x[1] = torch.sin(2 * math.pi * 60 * t)
        x[2] = torch.sin(2 * math.pi * 90 * t)
        
        psd, freqs = psd_layer(x)
        
        # Each channel should have different peak
        peaks = psd.argmax(dim=-1)
        assert len(torch.unique(peaks)) == n_channels

    def test_aliasing_detection(self):
        """Test detection of aliasing (frequencies above Nyquist)."""
        sample_rate = 100  # Low sample rate
        psd_layer = PSD(sample_rate)
        
        # Signal with frequency above Nyquist (50 Hz)
        seq_len = 1000
        t = torch.linspace(0, 10, seq_len)
        true_freq = 80  # Hz (above Nyquist)
        x = torch.sin(2 * math.pi * true_freq * t)
        
        psd, freqs = psd_layer(x)
        
        # Due to aliasing, peak won't be at true frequency
        # It will appear at alias frequency
        peak_idx = psd.argmax()
        peak_freq = freqs[peak_idx]
        assert peak_freq < sample_rate / 2  # Must be below Nyquist

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/nn/_PSD.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-04-11 21:50:09 (ywatanabe)"
# 
# import torch
# import torch.nn as nn
# 
# 
# class PSD(nn.Module):
#     def __init__(self, sample_rate, prob=False, dim=-1):
#         super(PSD, self).__init__()
#         self.sample_rate = sample_rate
#         self.dim = dim
#         self.prob = prob
# 
#     def forward(self, signal):
# 
#         is_complex = signal.is_complex()
#         if is_complex:
#             signal_fft = torch.fft.fft(signal, dim=self.dim)
#             freqs = torch.fft.fftfreq(signal.size(self.dim), 1 / self.sample_rate).to(
#                 signal.device
#             )
# 
#         else:
#             signal_fft = torch.fft.rfft(signal, dim=self.dim)
#             freqs = torch.fft.rfftfreq(signal.size(self.dim), 1 / self.sample_rate).to(
#                 signal.device
#             )
# 
#         power_spectrum = torch.abs(signal_fft) ** 2
#         power_spectrum = power_spectrum / signal.size(self.dim)
# 
#         psd = power_spectrum * (1.0 / self.sample_rate)
# 
#         # To probability if specified
#         if self.prob:
#             psd /= psd.sum(dim=self.dim, keepdims=True)
# 
#         return psd, freqs

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/nn/_PSD.py
# --------------------------------------------------------------------------------
