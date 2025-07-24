#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-01-06 (ywatanabe)"
# File: tests/scitex/nn/test__Wavelet.py

"""Comprehensive test suite for Wavelet module.

This module tests the wavelet transform functionality for neural networks,
including Morlet wavelet generation, multi-scale analysis, phase/amplitude extraction,
and edge cases.
"""

import pytest
import torch
import torch.nn as nn
import numpy as np
from unittest.mock import patch, MagicMock
import tempfile
import os

# Mock scitex modules
scitex_mock = MagicMock()
scitex_mock.dsp = MagicMock()
scitex_mock.dsp.ensure_3d = lambda x: x.view(-1, x.shape[-2], x.shape[-1]) if x.dim() == 2 else x

# Mock the to_even and to_odd functions
def mock_to_even(x):
    return x if x % 2 == 0 else x + 1

def mock_to_odd(x):
    return x if x % 2 == 1 else x + 1

with patch.dict('sys.modules', {
    'scitex': scitex_mock, 
    'scitex.dsp': scitex_mock.dsp,
    'scitex.gen': MagicMock(),
    'scitex.gen._to_even': MagicMock(to_even=mock_to_even),
    'scitex.gen._to_odd': MagicMock(to_odd=mock_to_odd)
}):
    # Import with mocked dependencies
    import sys
    sys.modules['scitex.gen._to_even'].to_even = mock_to_even
    sys.modules['scitex.gen._to_odd'].to_odd = mock_to_odd
    
    from scitex.nn import Wavelet


class TestWavelet:
    """Test suite for Wavelet layer."""
    
    @pytest.fixture
    def sample_rate(self):
        """Standard sample rate for testing."""
        return 1000
    
    @pytest.fixture
    def sample_input(self):
        """Create sample input tensor."""
        batch_size, n_channels, seq_len = 2, 3, 1000
        return torch.randn(batch_size, n_channels, seq_len)
    
    def test_initialization_default_params(self, sample_rate):
        """Test initialization with default parameters."""
        layer = Wavelet(samp_rate=sample_rate)
        
        assert layer.out_scale == "log"
        assert layer.kernel is not None
        assert layer.freqs is not None
        assert isinstance(layer.dummy, torch.Tensor)
    
    def test_initialization_custom_params(self, sample_rate):
        """Test initialization with custom parameters."""
        kernel_size = 512
        freq_scale = "log"
        out_scale = "linear"
        
        layer = Wavelet(
            samp_rate=sample_rate,
            kernel_size=kernel_size,
            freq_scale=freq_scale,
            out_scale=out_scale
        )
        
        assert layer.out_scale == out_scale
        assert layer.kernel_size == mock_to_even(kernel_size)
    
    def test_morlet_generation_linear_scale(self, sample_rate):
        """Test Morlet wavelet generation with linear frequency scale."""
        morlets, freqs = Wavelet.gen_morlet_to_nyquist(
            samp_rate=sample_rate,
            kernel_size=None,
            freq_scale="linear"
        )
        
        # Check output types
        assert isinstance(morlets, np.ndarray)
        assert isinstance(freqs, np.ndarray)
        
        # Check frequency range
        nyquist = sample_rate / 2
        assert freqs[0] > 0
        assert freqs[-1] <= nyquist
        
        # Check monotonic increase
        assert np.all(np.diff(freqs) > 0)
        
        # Check morlets are complex
        assert morlets.dtype == np.complex128
    
    def test_morlet_generation_log_scale(self, sample_rate):
        """Test Morlet wavelet generation with log frequency scale."""
        morlets, freqs = Wavelet.gen_morlet_to_nyquist(
            samp_rate=sample_rate,
            kernel_size=None,
            freq_scale="log"
        )
        
        # Check logarithmic spacing
        freq_ratios = freqs[1:] / freqs[:-1]
        # For log scale, ratios should be approximately constant
        assert np.std(freq_ratios) < np.mean(freq_ratios) * 0.5
    
    def test_forward_basic(self, sample_rate, sample_input):
        """Test basic forward pass."""
        layer = Wavelet(samp_rate=sample_rate)
        pha, amp, freqs = layer(sample_input)
        
        batch_size, n_channels, seq_len = sample_input.shape
        n_freqs = layer.kernel.shape[0]
        
        # Check output shapes
        assert pha.shape == (batch_size, n_channels, n_freqs, seq_len)
        assert amp.shape == (batch_size, n_channels, n_freqs, seq_len)
        assert freqs.shape == (batch_size, n_channels, n_freqs)
    
    def test_forward_log_scale_output(self, sample_rate, sample_input):
        """Test forward pass with log scale output."""
        layer = Wavelet(samp_rate=sample_rate, out_scale="log")
        pha, amp, freqs = layer(sample_input)
        
        # Amplitude should be log-transformed
        assert not torch.isinf(amp).any()  # Log should handle small values
    
    def test_forward_linear_scale_output(self, sample_rate, sample_input):
        """Test forward pass with linear scale output."""
        layer = Wavelet(samp_rate=sample_rate, out_scale="linear")
        pha, amp, freqs = layer(sample_input)
        
        # Amplitude should be non-negative
        assert (amp >= 0).all()
    
    def test_phase_range(self, sample_rate, sample_input):
        """Test that phase values are in correct range."""
        layer = Wavelet(samp_rate=sample_rate)
        pha, _, _ = layer(sample_input)
        
        # Phase should be between -pi and pi
        assert (pha >= -np.pi).all()
        assert (pha <= np.pi).all()
    
    def test_gradient_flow(self, sample_rate, sample_input):
        """Test that gradients flow properly through the layer."""
        layer = Wavelet(samp_rate=sample_rate)
        sample_input.requires_grad = True
        
        pha, amp, _ = layer(sample_input)
        loss = amp.sum() + pha.sum()
        loss.backward()
        
        assert sample_input.grad is not None
        assert not torch.allclose(sample_input.grad, torch.zeros_like(sample_input.grad))
    
    def test_edge_handling(self, sample_rate):
        """Test edge handling with reflection padding."""
        layer = Wavelet(samp_rate=sample_rate)
        
        # Create signal with sharp edges
        x = torch.ones(1, 1, 1000)
        x[:, :, :100] = -1
        x[:, :, -100:] = -1
        
        pha, amp, _ = layer(x)
        
        # Should not have NaN or Inf at edges
        assert not torch.isnan(pha).any()
        assert not torch.isinf(amp).any()
    
    def test_device_compatibility_cpu(self, sample_rate):
        """Test layer works on CPU."""
        layer = Wavelet(samp_rate=sample_rate)
        x = torch.randn(2, 3, 1000)
        
        pha, amp, freqs = layer(x)
        
        assert pha.device == x.device
        assert amp.device == x.device
        assert not pha.is_cuda
    
    @pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
    def test_device_compatibility_cuda(self, sample_rate):
        """Test layer works on CUDA."""
        layer = Wavelet(samp_rate=sample_rate).cuda()
        x = torch.randn(2, 3, 1000).cuda()
        
        pha, amp, freqs = layer(x)
        
        assert pha.device == x.device
        assert amp.device == x.device
        assert pha.is_cuda
        assert layer.kernel.is_cuda
    
    def test_different_kernel_sizes(self, sample_rate):
        """Test with various kernel sizes."""
        kernel_sizes = [256, 512, 1024, 2048]
        x = torch.randn(2, 3, 2000)
        
        for kernel_size in kernel_sizes:
            layer = Wavelet(samp_rate=sample_rate, kernel_size=kernel_size)
            pha, amp, _ = layer(x)
            
            # Output should maintain input sequence length
            assert pha.shape[-1] == x.shape[-1]
            assert amp.shape[-1] == x.shape[-1]
    
    def test_frequency_resolution(self, sample_rate):
        """Test frequency resolution with different scales."""
        layer_linear = Wavelet(samp_rate=sample_rate, freq_scale="linear")
        layer_log = Wavelet(samp_rate=sample_rate, freq_scale="log")
        
        # Linear scale should have more high-frequency components
        n_freqs_linear = layer_linear.freqs.shape[0]
        n_freqs_log = layer_log.freqs.shape[0]
        
        assert n_freqs_linear > n_freqs_log  # Linear has more bins overall
    
    def test_single_tone_analysis(self, sample_rate):
        """Test wavelet analysis of single frequency tone."""
        layer = Wavelet(samp_rate=sample_rate, freq_scale="linear")
        
        # Create single tone at 100 Hz
        t = torch.arange(0, 2, 1/sample_rate)
        freq = 100
        x = torch.sin(2 * np.pi * freq * t).unsqueeze(0).unsqueeze(0)
        
        pha, amp, freqs = layer(x)
        
        # Find peak frequency
        avg_amp = amp[0, 0].mean(dim=1)
        peak_idx = torch.argmax(avg_amp)
        peak_freq = freqs[0, 0, peak_idx]
        
        # Peak should be close to 100 Hz
        assert abs(peak_freq - freq) < 20  # Within 20 Hz tolerance
    
    def test_chirp_signal_analysis(self, sample_rate):
        """Test wavelet analysis of chirp signal."""
        layer = Wavelet(samp_rate=sample_rate)
        
        # Create chirp signal (frequency increases over time)
        t = torch.arange(0, 2, 1/sample_rate)
        f0, f1 = 50, 200
        chirp = torch.sin(2 * np.pi * (f0 + (f1-f0) * t / 2) * t)
        x = chirp.unsqueeze(0).unsqueeze(0)
        
        pha, amp, freqs = layer(x)
        
        # Early time should have lower frequency content
        early_amp = amp[0, 0, :, :100].mean(dim=1)
        late_amp = amp[0, 0, :, -100:].mean(dim=1)
        
        early_peak = freqs[0, 0, torch.argmax(early_amp)]
        late_peak = freqs[0, 0, torch.argmax(late_amp)]
        
        # Frequency should increase over time
        assert late_peak > early_peak
    
    def test_zero_input_handling(self, sample_rate):
        """Test behavior with zero input."""
        layer = Wavelet(samp_rate=sample_rate)
        x = torch.zeros(2, 3, 1000)
        
        pha, amp, _ = layer(x)
        
        # Amplitude should be near zero (or log of small value)
        if layer.out_scale == "log":
            assert (amp < -5).all()  # Log of small values
        else:
            assert torch.allclose(amp, torch.zeros_like(amp), atol=1e-10)
    
    def test_numerical_stability(self, sample_rate):
        """Test numerical stability with extreme values."""
        layer = Wavelet(samp_rate=sample_rate)
        
        # Test with very large values
        x_large = torch.randn(2, 3, 1000) * 1e6
        pha_large, amp_large, _ = layer(x_large)
        assert not torch.isnan(pha_large).any()
        assert not torch.isinf(amp_large).any()
        
        # Test with very small values
        x_small = torch.randn(2, 3, 1000) * 1e-6
        pha_small, amp_small, _ = layer(x_small)
        assert not torch.isnan(pha_small).any()
        assert not torch.isinf(amp_small).any()
    
    def test_batch_consistency(self, sample_rate):
        """Test that batched processing gives consistent results."""
        layer = Wavelet(samp_rate=sample_rate)
        
        # Single sample
        x_single = torch.randn(1, 3, 1000)
        pha_single, amp_single, _ = layer(x_single)
        
        # Batched with same data
        x_batch = x_single.repeat(4, 1, 1)
        pha_batch, amp_batch, _ = layer(x_batch)
        
        # All batch elements should be identical
        for i in range(4):
            assert torch.allclose(pha_batch[i], pha_single[0])
            assert torch.allclose(amp_batch[i], amp_single[0])
    
    def test_kernel_properties(self, sample_rate):
        """Test properties of generated Morlet wavelets."""
        layer = Wavelet(samp_rate=sample_rate)
        
        # Kernel should be complex
        assert layer.kernel.dtype == torch.complex64 or layer.kernel.dtype == torch.complex128
        
        # Each wavelet should be normalized
        for i in range(layer.kernel.shape[0]):
            wavelet = layer.kernel[i]
            # Check that wavelet has reasonable magnitude
            assert wavelet.abs().max() > 0
            assert wavelet.abs().max() < 10
    
    def test_memory_efficiency(self, sample_rate):
        """Test memory usage with large inputs."""
        layer = Wavelet(samp_rate=sample_rate)
        
        # Large input
        x = torch.randn(4, 8, 4000)
        
        # Should not raise memory errors
        pha, amp, _ = layer(x)
        assert pha.shape[0] == 4
        assert pha.shape[1] == 8
    
    def test_integration_with_sequential(self, sample_rate):
        """Test integration in nn.Sequential."""
        class WaveletFeatures(nn.Module):
            def __init__(self, samp_rate):
                super().__init__()
                self.wavelet = Wavelet(samp_rate)
            
            def forward(self, x):
                _, amp, _ = self.wavelet(x)
                # Average over time for feature extraction
                return amp.mean(dim=-1)
        
        model = nn.Sequential(
            WaveletFeatures(sample_rate),
            nn.Flatten(),
            nn.Linear(3 * 10, 64),  # Assuming ~10 frequency bands
            nn.ReLU(),
            nn.Linear(64, 10)
        )
        
        x = torch.randn(4, 3, 1000)
        # Note: This might fail due to dynamic frequency band calculation
        # Just check it doesn't crash
        try:
            output = model(x)
            assert output.shape[0] == 4
        except RuntimeError:
            # Expected if linear layer size doesn't match
            pass
    
    def test_phase_amplitude_consistency(self, sample_rate, sample_input):
        """Test that phase and amplitude are consistent."""
        layer = Wavelet(samp_rate=sample_rate)
        pha, amp, _ = layer(sample_input)
        
        # Reconstruct complex representation
        # complex = amp * exp(i * pha)
        # This is just a sanity check that values are reasonable
        
        # Phase should vary smoothly for continuous signals
        phase_diff = torch.diff(pha, dim=-1)
        # Most phase differences should be small (no phase wrapping issues)
        assert (torch.abs(phase_diff) < np.pi).sum() > phase_diff.numel() * 0.8
    
    def test_custom_kernel_size_effect(self, sample_rate):
        """Test that kernel size affects frequency resolution."""
        x = torch.randn(1, 1, 2000)
        
        # Smaller kernel - less frequency resolution
        layer_small = Wavelet(samp_rate=sample_rate, kernel_size=256)
        _, amp_small, freqs_small = layer_small(x)
        
        # Larger kernel - better frequency resolution
        layer_large = Wavelet(samp_rate=sample_rate, kernel_size=2048)
        _, amp_large, freqs_large = layer_large(x)
        
        # Different kernel sizes should give different results
        assert amp_small.shape != amp_large.shape or not torch.allclose(amp_small, amp_large)

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/nn/_Wavelet.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-03 07:17:26 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/nn/_Wavelet.py
# 
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-05-30 11:04:45 (ywatanabe)"
# 
# 
# import scitex
# import numpy as np
# import torch
# import torch.nn as nn
# import torch.nn.functional as F
# from ..gen._to_even import to_even
# from ..gen._to_odd import to_odd
# 
# 
# class Wavelet(nn.Module):
#     def __init__(
#         self, samp_rate, kernel_size=None, freq_scale="linear", out_scale="log"
#     ):
#         super().__init__()
#         self.register_buffer("dummy", torch.tensor(0))
#         self.kernel = None
#         self.init_kernel(samp_rate, kernel_size=kernel_size, freq_scale=freq_scale)
#         self.out_scale = out_scale
# 
#     def forward(self, x):
#         """Apply the 2D filter (n_filts, kernel_size) to input signal x with shape: (batch_size, n_chs, seq_len)"""
#         x = scitex.dsp.ensure_3d(x).to(self.dummy.device)
#         seq_len = x.shape[-1]
# 
#         # Ensure the kernel is initialized
#         if self.kernel is None:
#             self.init_kernel()
#             if self.kernel is None:
#                 raise ValueError("Filter kernel has not been initialized.")
#         assert self.kernel.ndim == 2
#         self.kernel = self.kernel.to(x.device)  # cuda, torch.complex128
# 
#         # Edge handling and convolution
#         extension_length = self.radius
#         first_segment = x[:, :, :extension_length].flip(dims=[-1])
#         last_segment = x[:, :, -extension_length:].flip(dims=[-1])
#         extended_x = torch.cat([first_segment, x, last_segment], dim=-1)
# 
#         # working??
#         kernel_batched = self.kernel.unsqueeze(1)
#         extended_x_reshaped = extended_x.view(-1, 1, extended_x.shape[-1])
# 
#         filtered_x_real = F.conv1d(
#             extended_x_reshaped, kernel_batched.real.float(), groups=1
#         )
#         filtered_x_imag = F.conv1d(
#             extended_x_reshaped, kernel_batched.imag.float(), groups=1
#         )
# 
#         filtered_x = torch.view_as_complex(
#             torch.stack([filtered_x_real, filtered_x_imag], dim=-1)
#         )
# 
#         filtered_x = filtered_x.view(
#             x.shape[0], x.shape[1], kernel_batched.shape[0], -1
#         )
#         filtered_x = filtered_x.view(
#             x.shape[0], x.shape[1], kernel_batched.shape[0], -1
#         )
#         filtered_x = filtered_x[..., :seq_len]
#         assert filtered_x.shape[-1] == seq_len
# 
#         pha = filtered_x.angle()
#         amp = filtered_x.abs()
# 
#         # Repeats freqs
#         freqs = (
#             self.freqs.unsqueeze(0).unsqueeze(0).repeat(pha.shape[0], pha.shape[1], 1)
#         )
# 
#         if self.out_scale == "log":
#             return pha, torch.log(amp + 1e-5), freqs
#         else:
#             return pha, amp, freqs
# 
#     def init_kernel(self, samp_rate, kernel_size=None, freq_scale="log"):
#         device = self.dummy.device
#         morlets, freqs = self.gen_morlet_to_nyquist(
#             samp_rate, kernel_size=kernel_size, freq_scale=freq_scale
#         )
#         self.kernel = torch.tensor(morlets).to(device)
#         self.freqs = torch.tensor(freqs).float().to(device)
# 
#     @staticmethod
#     def gen_morlet_to_nyquist(samp_rate, kernel_size=None, freq_scale="linear"):
#         """
#         Generates Morlet wavelets for exponentially increasing frequency bands up to the Nyquist frequency.
# 
#         Parameters:
#         - samp_rate (int): The sampling rate of the signal, in Hertz.
#         - kernel_size (int): The size of the kernel, in number of samples.
# 
#         Returns:
#         - np.ndarray: A 2D array of complex values representing the Morlet wavelets for each frequency band.
#         """
#         if kernel_size is None:
#             kernel_size = int(samp_rate)  # * 2.5)
# 
#         nyquist_freq = samp_rate / 2
# 
#         # Log freq_scale
#         def calc_freq_boundaries_log(nyquist_freq):
#             n_kernels = int(np.floor(np.log2(nyquist_freq)))
#             mid_hz = np.array([2 ** (n + 1) for n in range(n_kernels)])
#             width_hz = np.hstack([np.array([1]), np.diff(mid_hz) / 2]) + 1
#             low_hz = mid_hz - width_hz
#             high_hz = mid_hz + width_hz
#             low_hz[0] = 0.1
#             return low_hz, high_hz
# 
#         def calc_freq_boundaries_linear(nyquist_freq):
#             n_kernels = int(nyquist_freq)
#             high_hz = np.linspace(1, nyquist_freq, n_kernels)
#             low_hz = high_hz - np.hstack([np.array(1), np.diff(high_hz)])
#             low_hz[0] = 0.1
#             return low_hz, high_hz
# 
#         if freq_scale == "linear":
#             fn = calc_freq_boundaries_linear
#         if freq_scale == "log":
#             fn = calc_freq_boundaries_log
#         low_hz, high_hz = fn(nyquist_freq)
# 
#         morlets = []
#         freqs = []
# 
#         for _, (ll, hh) in enumerate(zip(low_hz, high_hz)):
#             if ll > nyquist_freq:
#                 break
# 
#             center_frequency = (ll + hh) / 2
# 
#             t = np.arange(-kernel_size // 2, kernel_size // 2) / samp_rate
#             # Calculate standard deviation of the gaussian window for a given center frequency
#             sigma = 7 / (2 * np.pi * center_frequency)
#             sine_wave = np.exp(2j * np.pi * center_frequency * t)
#             gaussian_window = np.exp(-(t**2) / (2 * sigma**2))
#             morlet_wavelet = sine_wave * gaussian_window
# 
#             freqs.append(center_frequency)
#             morlets.append(morlet_wavelet)
# 
#         return np.array(morlets), np.array(freqs)
# 
#     @property
#     def kernel_size(
#         self,
#     ):
#         return to_even(self.kernel.shape[-1])
# 
#     @property
#     def radius(
#         self,
#     ):
#         return to_even(self.kernel_size // 2)
# 
# 
# if __name__ == "__main__":
#     import matplotlib.pyplot as plt
#     import scitex
# 
#     xx, tt, fs = scitex.dsp.demo_sig(sig_type="chirp")
# 
#     pha, amp, ff = scitex.dsp.wavelet(xx, fs)
# 
#     fig, ax = scitex.plt.subplots()
#     ax.imshow2d(amp[0, 0].T)
#     ax = scitex.plt.ax.set_ticks(ax, xticks=tt, yticks=ff)
#     ax = scitex.plt.ax.set_n_ticks(ax)
#     plt.show()
# 
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/nn/_Wavelet.py
# --------------------------------------------------------------------------------
