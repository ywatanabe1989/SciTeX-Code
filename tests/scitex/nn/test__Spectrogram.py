#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-01-06 (ywatanabe)"
# File: tests/scitex/nn/test__Spectrogram.py

"""Comprehensive test suite for Spectrogram module.

This module tests the spectrogram computation functionality for neural networks,
including STFT parameters, window functions, multi-channel support, and edge cases.
"""

import pytest
import torch
import torch.nn as nn
import numpy as np
from unittest.mock import patch, MagicMock
import tempfile
import os

# Mock scitex.dsp.ensure_3d since it's used in the module
scitex_mock = MagicMock()
scitex_mock.dsp = MagicMock()
scitex_mock.dsp.ensure_3d = lambda x: x.view(-1, x.shape[-2], x.shape[-1]) if x.dim() == 2 else x

with patch.dict('sys.modules', {'scitex': scitex_mock, 'scitex.dsp': scitex_mock.dsp}):
    from scitex.nn import Spectrogram


class TestSpectrogram:
    """Test suite for Spectrogram layer."""
    
    @pytest.fixture
    def sampling_rate(self):
        """Standard sampling rate for testing."""
        return 1000
    
    @pytest.fixture
    def n_fft(self):
        """Default FFT size for testing."""
        return 256
    
    @pytest.fixture
    def sample_input(self):
        """Create sample input tensor."""
        batch_size, n_channels, seq_len = 2, 3, 1000
        return torch.randn(batch_size, n_channels, seq_len)
    
    def test_initialization_default_params(self, sampling_rate):
        """Test initialization with default parameters."""
        layer = Spectrogram(sampling_rate=sampling_rate)
        assert layer.sampling_rate == sampling_rate
        assert layer.n_fft == 256
        assert layer.hop_length == 256 // 4  # Default is n_fft // 4
        assert layer.win_length == 256
        assert isinstance(layer.window, torch.Tensor)
        assert layer.window.shape == (256,)
    
    def test_initialization_custom_params(self, sampling_rate):
        """Test initialization with custom parameters."""
        n_fft = 512
        hop_length = 128
        win_length = 400
        
        layer = Spectrogram(
            sampling_rate=sampling_rate,
            n_fft=n_fft,
            hop_length=hop_length,
            win_length=win_length,
            window="hann"
        )
        
        assert layer.n_fft == n_fft
        assert layer.hop_length == hop_length
        assert layer.win_length == win_length
        assert layer.window.shape == (win_length,)
    
    def test_initialization_invalid_window(self, sampling_rate):
        """Test initialization with invalid window type."""
        with pytest.raises(ValueError, match="Unsupported window type"):
            Spectrogram(sampling_rate=sampling_rate, window="invalid")
    
    def test_forward_basic(self, sampling_rate, sample_input):
        """Test basic forward pass."""
        layer = Spectrogram(sampling_rate=sampling_rate)
        spectrograms, freqs, times = layer(sample_input)
        
        # Check output shapes
        batch_size, n_channels, seq_len = sample_input.shape
        expected_freq_bins = layer.n_fft // 2 + 1
        
        # Number of time frames depends on STFT parameters
        assert spectrograms.shape[0] == batch_size
        assert spectrograms.shape[1] == n_channels
        assert spectrograms.shape[2] == expected_freq_bins
        
        # Check frequency and time arrays
        assert freqs.shape == (expected_freq_bins,)
        assert times.shape[0] == spectrograms.shape[3]
    
    def test_forward_single_channel(self, sampling_rate):
        """Test forward pass with single channel input."""
        x = torch.randn(2, 1, 1000)
        layer = Spectrogram(sampling_rate=sampling_rate)
        
        spectrograms, freqs, times = layer(x)
        
        assert spectrograms.shape[1] == 1  # Single channel maintained
    
    def test_forward_multi_channel(self, sampling_rate):
        """Test forward pass with multi-channel input."""
        n_channels = 8
        x = torch.randn(2, n_channels, 1000)
        layer = Spectrogram(sampling_rate=sampling_rate)
        
        spectrograms, freqs, times = layer(x)
        
        assert spectrograms.shape[1] == n_channels
    
    def test_frequency_range(self, sampling_rate):
        """Test that frequency range is correct (0 to Nyquist)."""
        layer = Spectrogram(sampling_rate=sampling_rate)
        x = torch.randn(1, 1, 1000)
        
        _, freqs, _ = layer(x)
        
        # Check frequency range
        assert freqs[0] == 0
        assert freqs[-1] == sampling_rate / 2  # Nyquist frequency
        
        # Check monotonic increase
        assert torch.all(torch.diff(freqs) > 0)
    
    def test_time_values(self, sampling_rate):
        """Test that time values are correctly computed."""
        hop_length = 100
        layer = Spectrogram(sampling_rate=sampling_rate, hop_length=hop_length)
        x = torch.randn(1, 1, 1000)
        
        _, _, times = layer(x)
        
        # Time between frames should be hop_length / sampling_rate
        expected_time_step = hop_length / sampling_rate
        time_diffs = torch.diff(times)
        assert torch.allclose(time_diffs, torch.tensor(expected_time_step))
    
    def test_different_fft_sizes(self, sampling_rate):
        """Test with various FFT sizes."""
        fft_sizes = [128, 256, 512, 1024]
        x = torch.randn(2, 3, 2000)
        
        for n_fft in fft_sizes:
            layer = Spectrogram(sampling_rate=sampling_rate, n_fft=n_fft)
            spectrograms, freqs, times = layer(x)
            
            expected_freq_bins = n_fft // 2 + 1
            assert spectrograms.shape[2] == expected_freq_bins
            assert freqs.shape[0] == expected_freq_bins
    
    def test_different_hop_lengths(self, sampling_rate):
        """Test with various hop lengths."""
        n_fft = 256
        hop_lengths = [32, 64, 128, 256]
        x = torch.randn(2, 3, 2000)
        
        prev_n_frames = None
        for hop_length in hop_lengths:
            layer = Spectrogram(
                sampling_rate=sampling_rate, 
                n_fft=n_fft, 
                hop_length=hop_length
            )
            spectrograms, _, times = layer(x)
            
            n_frames = spectrograms.shape[3]
            
            # Smaller hop length should give more frames
            if prev_n_frames is not None:
                assert n_frames < prev_n_frames
            prev_n_frames = n_frames
    
    def test_gradient_flow(self, sampling_rate, sample_input):
        """Test that gradients flow properly through the layer."""
        layer = Spectrogram(sampling_rate=sampling_rate)
        sample_input.requires_grad = True
        
        spectrograms, _, _ = layer(sample_input)
        loss = spectrograms.sum()
        loss.backward()
        
        assert sample_input.grad is not None
        assert not torch.allclose(sample_input.grad, torch.zeros_like(sample_input.grad))
    
    def test_device_compatibility_cpu(self, sampling_rate):
        """Test layer works on CPU."""
        layer = Spectrogram(sampling_rate=sampling_rate)
        x = torch.randn(2, 3, 1000)
        
        spectrograms, freqs, times = layer(x)
        
        assert spectrograms.device == x.device
        assert not spectrograms.is_cuda
    
    @pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
    def test_device_compatibility_cuda(self, sampling_rate):
        """Test layer works on CUDA."""
        layer = Spectrogram(sampling_rate=sampling_rate)
        x = torch.randn(2, 3, 1000).cuda()
        
        spectrograms, freqs, times = layer(x)
        
        assert spectrograms.device == x.device
        assert spectrograms.is_cuda
        # Window should be moved to CUDA automatically
        assert layer.window.is_cuda
    
    def test_window_length_variations(self, sampling_rate):
        """Test with different window lengths."""
        n_fft = 512
        win_lengths = [128, 256, 384, 512]
        x = torch.randn(2, 3, 2000)
        
        for win_length in win_lengths:
            layer = Spectrogram(
                sampling_rate=sampling_rate,
                n_fft=n_fft,
                win_length=win_length
            )
            spectrograms, _, _ = layer(x)
            
            # Should produce valid output
            assert not torch.isnan(spectrograms).any()
            assert not torch.isinf(spectrograms).any()
    
    def test_short_signal_handling(self, sampling_rate):
        """Test with signals shorter than window length."""
        n_fft = 256
        layer = Spectrogram(sampling_rate=sampling_rate, n_fft=n_fft)
        
        # Signal shorter than n_fft
        x_short = torch.randn(2, 3, 100)
        spectrograms, _, _ = layer(x_short)
        
        # Should still produce output due to padding
        assert spectrograms.shape[0] == 2
        assert spectrograms.shape[1] == 3
    
    def test_zero_input_handling(self, sampling_rate):
        """Test behavior with zero input."""
        layer = Spectrogram(sampling_rate=sampling_rate)
        x = torch.zeros(2, 3, 1000)
        
        spectrograms, _, _ = layer(x)
        
        # Spectrogram of zeros should be zeros (or very close)
        assert torch.allclose(spectrograms, torch.zeros_like(spectrograms), atol=1e-10)
    
    def test_single_tone_input(self, sampling_rate):
        """Test with single frequency tone."""
        layer = Spectrogram(sampling_rate=sampling_rate, n_fft=512)
        
        # Create single tone at 100 Hz
        t = torch.arange(0, 2, 1/sampling_rate)
        freq = 100
        x = torch.sin(2 * np.pi * freq * t).unsqueeze(0).unsqueeze(0)
        
        spectrograms, freqs, _ = layer(x)
        
        # Find peak frequency
        avg_spectrum = spectrograms[0, 0].mean(dim=1)
        peak_idx = torch.argmax(avg_spectrum)
        peak_freq = freqs[peak_idx]
        
        # Peak should be close to 100 Hz
        assert abs(peak_freq - freq) < 10  # Within 10 Hz tolerance
    
    def test_magnitude_only_output(self, sampling_rate, sample_input):
        """Test that output is magnitude (not complex)."""
        layer = Spectrogram(sampling_rate=sampling_rate)
        spectrograms, _, _ = layer(sample_input)
        
        # Output should be real and non-negative (magnitude)
        assert spectrograms.dtype in [torch.float32, torch.float64]
        assert (spectrograms >= 0).all()
    
    def test_numerical_stability(self, sampling_rate):
        """Test numerical stability with extreme values."""
        layer = Spectrogram(sampling_rate=sampling_rate)
        
        # Test with very large values
        x_large = torch.randn(2, 3, 1000) * 1e6
        spectrograms_large, _, _ = layer(x_large)
        assert not torch.isnan(spectrograms_large).any()
        assert not torch.isinf(spectrograms_large).any()
        
        # Test with very small values
        x_small = torch.randn(2, 3, 1000) * 1e-6
        spectrograms_small, _, _ = layer(x_small)
        assert not torch.isnan(spectrograms_small).any()
    
    def test_batch_consistency(self, sampling_rate):
        """Test that batched processing gives consistent results."""
        layer = Spectrogram(sampling_rate=sampling_rate)
        
        # Single sample
        x_single = torch.randn(1, 3, 1000)
        spec_single, _, _ = layer(x_single)
        
        # Batched with same data
        x_batch = x_single.repeat(4, 1, 1)
        spec_batch, _, _ = layer(x_batch)
        
        # All batch elements should be identical
        for i in range(4):
            assert torch.allclose(spec_batch[i], spec_single[0])
    
    def test_integration_with_sequential(self, sampling_rate):
        """Test integration in nn.Sequential."""
        class SpectrogramWrapper(nn.Module):
            def __init__(self, sampling_rate):
                super().__init__()
                self.spec = Spectrogram(sampling_rate)
            
            def forward(self, x):
                spec, _, _ = self.spec(x)
                return spec
        
        model = nn.Sequential(
            SpectrogramWrapper(sampling_rate),
            nn.Conv2d(3, 16, 3, padding=1),  # Assuming 3 input channels
            nn.ReLU(),
            nn.AdaptiveAvgPool2d((8, 8))
        )
        
        x = torch.randn(4, 3, 1000)
        output = model(x)
        
        assert output.shape == (4, 16, 8, 8)
    
    def test_memory_efficiency(self, sampling_rate):
        """Test memory usage with large inputs."""
        layer = Spectrogram(sampling_rate=sampling_rate)
        
        # Large input
        x = torch.randn(8, 16, 4000)
        
        # Should not raise memory errors
        spectrograms, _, _ = layer(x)
        assert spectrograms.shape[0] == 8
        assert spectrograms.shape[1] == 16
    
    def test_padding_mode_effect(self, sampling_rate):
        """Test that reflect padding is working."""
        layer = Spectrogram(sampling_rate=sampling_rate)
        
        # Signal with sharp edges
        x = torch.ones(1, 1, 1000)
        x[:, :, :100] = -1  # Sharp transition
        
        spectrograms, _, _ = layer(x)
        
        # Should produce valid output without edge artifacts
        assert not torch.isnan(spectrograms).any()
        assert not torch.isinf(spectrograms).any()
    
    def test_energy_preservation(self, sampling_rate):
        """Test approximate energy preservation (Parseval's theorem)."""
        layer = Spectrogram(sampling_rate=sampling_rate, n_fft=512)
        
        # Create signal with known energy
        x = torch.randn(1, 1, 2000)
        time_energy = (x ** 2).sum()
        
        spectrograms, _, _ = layer(x)
        
        # Energy in frequency domain should be related to time domain
        # (Not exact due to windowing and overlap)
        freq_energy = (spectrograms ** 2).sum()
        
        # Check they are in the same order of magnitude
        ratio = freq_energy / time_energy
        assert 0.1 < ratio < 10  # Reasonable range considering windowing

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/nn/_Spectrogram.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-04-02 09:21:12 (ywatanabe)"
# 
# import torch
# import torch.nn as nn
# import torch.nn.functional as F
# import numpy as np
# import matplotlib.pyplot as plt
# import scitex
# from ..decorators import numpy_fn, torch_fn
# 
# 
# class Spectrogram(nn.Module):
#     def __init__(
#         self,
#         sampling_rate,
#         n_fft=256,
#         hop_length=None,
#         win_length=None,
#         window="hann",
#     ):
#         super().__init__()
#         self.sampling_rate = sampling_rate
#         self.n_fft = n_fft
#         self.hop_length = hop_length if hop_length is not None else n_fft // 4
#         self.win_length = win_length if win_length is not None else n_fft
#         if window == "hann":
#             self.window = torch.hann_window(window_length=self.win_length)
#         else:
#             raise ValueError(
#                 "Unsupported window type. Extend this to support more window types."
#             )
# 
#     def forward(self, x):
#         """
#         Computes the spectrogram for each channel in the input signal.
# 
#         Parameters:
#         - signal (torch.Tensor): Input signal of shape (batch_size, n_chs, seq_len).
# 
#         Returns:
#         - spectrograms (torch.Tensor): The computed spectrograms for each channel.
#         """
# 
#         x = scitex.dsp.ensure_3d(x)
# 
#         batch_size, n_chs, seq_len = x.shape
#         spectrograms = []
# 
#         for ch in range(n_chs):
#             x_ch = x[:, ch, :].unsqueeze(1)  # Maintain expected input shape for stft
#             spec = torch.stft(
#                 x_ch.squeeze(1),
#                 n_fft=self.n_fft,
#                 hop_length=self.hop_length,
#                 win_length=self.win_length,
#                 window=self.window.to(x.device),
#                 center=True,
#                 pad_mode="reflect",
#                 normalized=False,
#                 return_complex=True,
#             )
#             magnitude = torch.abs(spec).unsqueeze(1)  # Keep channel dimension
#             spectrograms.append(magnitude)
# 
#         # Concatenate spectrograms along channel dimension
#         spectrograms = torch.cat(spectrograms, dim=1)
# 
#         # Calculate frequencies (y-axis)
#         freqs = torch.linspace(0, self.sampling_rate / 2, steps=self.n_fft // 2 + 1)
# 
#         # Calculate times (x-axis)
#         # The number of frames can be computed from the size of the last dimension of the spectrogram
#         n_frames = spectrograms.shape[-1]
#         # Time of each frame in seconds, considering the hop length and sampling rate
#         times_sec = torch.arange(0, n_frames) * (self.hop_length / self.sampling_rate)
# 
#         return spectrograms, freqs, times_sec
# 
# 
# @torch_fn
# def spectrograms(x, fs, cuda=False):
#     return Spectrogram(fs)(x)
# 
# 
# @torch_fn
# def my_softmax(x, dim=-1):
#     return F.softmax(x, dim=dim)
# 
# 
# @torch_fn
# def unbias(x, func="min", dim=-1, cuda=False):
#     if func == "min":
#         return x - x.min(dim=dim, keepdims=True)[0]
#     if func == "mean":
#         return x - x.mean(dim=dim, keepdims=True)[0]
# 
# 
# @torch_fn
# def normalize(x, axis=-1, amp=1.0, cuda=False):
#     high = torch.abs(x.max(axis=axis, keepdims=True)[0])
#     low = torch.abs(x.min(axis=axis, keepdims=True)[0])
#     return amp * x / torch.maximum(high, low)
# 
# 
# @torch_fn
# def spectrograms(x, fs, dj=0.125, cuda=False):
#     from wavelets_pytorch.transform import (
#         WaveletTransformTorch,
#     )  # PyTorch version
# 
#     dt = 1 / fs
#     # dj = 0.125
#     batch_size, n_chs, seq_len = x.shape
# 
#     x = x.cpu().numpy()
# 
#     # # Batch of signals to process
#     # batch = np.array([batch_size * seq_len])
# 
#     # Initialize wavelet filter banks (scipy and torch implementation)
#     # wa_scipy = WaveletTransform(dt, dj)
#     wa_torch = WaveletTransformTorch(dt, dj, cuda=True)
# 
#     # Performing wavelet transform (and compute scalogram)
#     # cwt_scipy = wa_scipy.cwt(batch)
#     x = x[:, 0][:, np.newaxis]
#     cwt_torch = wa_torch.cwt(x)
# 
#     return cwt_torch
# 
# 
# if __name__ == "__main__":
#     import scitex
#     import seaborn as sns
#     import torchaudio
# 
#     fs = 1024  # 128
#     t_sec = 10
#     x = scitex.dsp.np.demo_sig(t_sec=t_sec, fs=fs, type="ripple")
# 
#     normalize(unbias(x, cuda=True), cuda=True)
# 
#     # My implementtion
#     ss = spectrograms(x, fs, cuda=True)
#     fig, axes = plt.subplots(nrows=2)
#     axes[0].plot(np.arange(x[0, 0]) / fs, x[0, 0])
#     sns.heatmap(ss[0], ax=axes[1])
#     plt.show()
# 
#     ss, ff, tt = spectrograms(x, fs, cuda=True)
#     fig, axes = plt.subplots(nrows=2)
#     axes[0].plot(np.arange(x[0, 0]) / fs, x[0, 0])
#     sns.heatmap(ss[0], ax=axes[1])
#     plt.show()
# 
#     # Torch Audio
#     transform = torchaudio.transforms.Spectrogram(n_fft=16, normalized=True).cuda()
#     xx = torch.tensor(x).float().cuda()[0, 0]
#     ss = transform(xx)
#     sns.heatmap(ss.detach().cpu().numpy())
# 
#     plt.show()

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/nn/_Spectrogram.py
# --------------------------------------------------------------------------------
