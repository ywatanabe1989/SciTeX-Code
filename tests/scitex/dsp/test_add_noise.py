#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-01 21:00:00 (ywatanabe)"
# File: ./tests/scitex/dsp/test_add_noise.py

"""
Test module for scitex.dsp.add_noise functions.
"""

import pytest
import numpy as np
import torch
from numpy.testing import assert_allclose


class TestAddNoise:
    """Test class for noise addition functions."""

    @pytest.fixture
    def clean_signal(self):
        """Create a clean test signal."""
        t = np.linspace(0, 1, 1000)
        signal = np.sin(2 * np.pi * 10 * t)  # 10 Hz sine wave
        return signal.astype(np.float32)

    @pytest.fixture
    def multi_channel_signal(self):
        """Create a multi-channel clean signal."""
        t = np.linspace(0, 1, 1000)
        n_channels = 4
        signals = []
        for i in range(n_channels):
            freq = 5 * (i + 1)  # 5, 10, 15, 20 Hz
            signals.append(np.sin(2 * np.pi * freq * t))
        return np.array(signals, dtype=np.float32)

    def test_module_import(self):
        """Test that add_noise module can be imported."""
        import scitex.dsp.add_noise

        assert hasattr(scitex.dsp.add_noise, "gauss")
        assert hasattr(scitex.dsp.add_noise, "white")
        assert hasattr(scitex.dsp.add_noise, "pink")
        assert hasattr(scitex.dsp.add_noise, "brown")

    def test_gauss_noise(self, clean_signal):
        """Test Gaussian noise addition."""
        from scitex.dsp.add_noise import gauss

        noisy = gauss(clean_signal, amp=0.1)

        # Check shape preserved
        assert noisy.shape == clean_signal.shape

        # Check that noise was added (signal changed)
        assert not np.array_equal(noisy, clean_signal)

        # Check noise properties
        noise = noisy - clean_signal
        assert np.abs(np.mean(noise)) < 0.05  # Should be zero mean
        assert 0.05 < np.std(noise) < 0.15  # Should have std ~ amp

    def test_white_noise(self, clean_signal):
        """Test white noise addition."""
        from scitex.dsp.add_noise import white

        amp = 0.2
        noisy = white(clean_signal, amp=amp)

        # Check shape preserved
        assert noisy.shape == clean_signal.shape

        # Check that noise was added
        assert not np.array_equal(noisy, clean_signal)

        # Check noise is bounded by amplitude
        noise = noisy - clean_signal
        assert np.all(np.abs(noise) <= amp * 1.01)  # Small tolerance

    def test_pink_noise(self, clean_signal):
        """Test pink (1/f) noise addition."""
        from scitex.dsp.add_noise import pink

        noisy = pink(clean_signal, amp=0.1)

        # Check shape preserved
        assert noisy.shape == clean_signal.shape

        # Check that noise was added
        assert not np.array_equal(noisy, clean_signal)

        # Pink noise should have more low-frequency content
        noise = noisy - clean_signal
        # Basic check that noise exists
        assert np.std(noise) > 0

    def test_brown_noise(self, clean_signal):
        """Test brown (Brownian) noise addition."""
        from scitex.dsp.add_noise import brown

        noisy = brown(clean_signal, amp=0.1)

        # Check shape preserved
        assert noisy.shape == clean_signal.shape

        # Check that noise was added
        assert not np.array_equal(noisy, clean_signal)

        # Brown noise is integrated white noise
        noise = noisy - clean_signal
        assert np.std(noise) > 0

    def test_amplitude_scaling(self, clean_signal):
        """Test that amplitude parameter scales noise correctly."""
        from scitex.dsp.add_noise import gauss

        # Test different amplitudes
        amp1, amp2 = 0.1, 0.5
        noisy1 = gauss(clean_signal, amp=amp1)
        noisy2 = gauss(clean_signal, amp=amp2)

        noise1 = noisy1 - clean_signal
        noise2 = noisy2 - clean_signal

        # Larger amplitude should produce larger noise
        assert np.std(noise2) > np.std(noise1)

        # Rough proportionality check
        ratio = np.std(noise2) / np.std(noise1)
        assert 3 < ratio < 7  # Approximately amp2/amp1 = 5

    def test_multi_channel_noise(self, multi_channel_signal):
        """Test noise addition to multi-channel signals."""
        from scitex.dsp.add_noise import gauss, white, pink, brown

        noise_funcs = [gauss, white, pink, brown]

        for noise_func in noise_funcs:
            noisy = noise_func(multi_channel_signal, amp=0.1)

            # Check shape preserved
            assert noisy.shape == multi_channel_signal.shape

            # Check each channel has different noise
            noise = noisy - multi_channel_signal
            for i in range(len(noise) - 1):
                assert not np.array_equal(noise[i], noise[i + 1])

    def test_torch_tensor_input(self, clean_signal):
        """Test noise addition with PyTorch tensor input."""
        from scitex.dsp.add_noise import gauss, white, pink, brown

        signal_torch = torch.tensor(clean_signal)
        noise_funcs = [gauss, white, pink, brown]

        for noise_func in noise_funcs:
            noisy = noise_func(signal_torch, amp=0.1)

            # Should return torch tensor
            assert isinstance(noisy, torch.Tensor)
            assert noisy.shape == signal_torch.shape

            # Should add noise
            assert not torch.equal(noisy, signal_torch)

    def test_zero_amplitude(self, clean_signal):
        """Test that zero amplitude returns unchanged signal."""
        from scitex.dsp.add_noise import gauss, white

        # With zero amplitude, signal should be unchanged
        noisy_gauss = gauss(clean_signal, amp=0.0)
        noisy_white = white(clean_signal, amp=0.0)

        assert_allclose(noisy_gauss, clean_signal, rtol=1e-6)
        assert_allclose(noisy_white, clean_signal, rtol=1e-6)

    def test_reproducibility_with_seed(self, clean_signal):
        """Test that noise is reproducible with same random seed."""
        from scitex.dsp.add_noise import gauss

        # Set seed and generate noise
        torch.manual_seed(42)
        noisy1 = gauss(torch.tensor(clean_signal), amp=0.1)

        # Reset seed and generate again
        torch.manual_seed(42)
        noisy2 = gauss(torch.tensor(clean_signal), amp=0.1)

        # Should be identical
        assert torch.equal(noisy1, noisy2)

    def test_different_dimensions(self):
        """Test noise addition with different signal dimensions."""
        from scitex.dsp.add_noise import gauss, pink, brown

        # 1D signal
        signal_1d = torch.randn(1000)
        noisy_1d = gauss(signal_1d, amp=0.1)
        assert noisy_1d.shape == signal_1d.shape

        # 2D signal
        signal_2d = torch.randn(4, 1000)
        noisy_2d = gauss(signal_2d, amp=0.1)
        assert noisy_2d.shape == signal_2d.shape

        # 3D signal
        signal_3d = torch.randn(2, 4, 1000)
        noisy_3d = gauss(signal_3d, amp=0.1)
        assert noisy_3d.shape == signal_3d.shape

    def test_pink_noise_spectrum(self, clean_signal):
        """Test that pink noise has appropriate spectral characteristics."""
        from scitex.dsp.add_noise import pink

        # Generate longer signal for better spectral analysis
        long_signal = np.zeros(10000, dtype=np.float32)
        noisy = pink(long_signal, amp=1.0)

        # Pink noise should have 1/f spectrum
        # Basic test: low frequencies should have more power
        noise = noisy - long_signal
        fft = np.abs(np.fft.rfft(noise))

        # Compare power in low vs high frequency bands
        low_power = np.mean(fft[:100] ** 2)
        high_power = np.mean(fft[-100:] ** 2)

        # Low frequencies should have more power
        assert low_power > high_power

    def test_brown_noise_integration(self, clean_signal):
        """Test that brown noise is integrated white noise."""
        from scitex.dsp.add_noise import brown

        noisy = brown(clean_signal, amp=0.1)
        noise = noisy - clean_signal

        # Brown noise should be smoother than white noise
        # Check that consecutive differences are smaller
        diff_noise = np.diff(noise)
        assert np.std(diff_noise) < np.std(noise)

    def test_device_handling(self):
        """Test proper device handling for GPU tensors."""
        from scitex.dsp.add_noise import gauss, white, pink, brown

        if torch.cuda.is_available():
            signal_gpu = torch.randn(1000).cuda()
            noise_funcs = [gauss, white, pink, brown]

            for noise_func in noise_funcs:
                noisy = noise_func(signal_gpu, amp=0.1)
                assert noisy.is_cuda
                assert noisy.device == signal_gpu.device

    @pytest.mark.parametrize(
        "noise_type,amp",
        [
            ("gauss", 0.1),
            ("gauss", 1.0),
            ("white", 0.5),
            ("pink", 0.2),
            ("brown", 0.1),
        ],
    )
    def test_signal_to_noise_ratio(self, clean_signal, noise_type, amp):
        """Test signal-to-noise ratio for different noise types and amplitudes."""
        import scitex.dsp.add_noise as add_noise

        noise_func = getattr(add_noise, noise_type)
        noisy = noise_func(clean_signal, amp=amp)

        # Calculate SNR
        signal_power = np.mean(clean_signal**2)
        noise = noisy - clean_signal
        noise_power = np.mean(noise**2)

        # SNR should be reasonable
        snr_db = 10 * np.log10(signal_power / noise_power)
        assert -10 < snr_db < 40  # Reasonable SNR range


# --------------------------------------------------------------------------------

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/dsp/add_noise.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "ywatanabe (2024-11-02 23:09:49)"
# # File: ./scitex_repo/src/scitex/dsp/add_noise.py
# 
# import torch
# from ..decorators import signal_fn
# 
# 
# def _uniform(shape, amp=1.0):
#     a, b = -amp, amp
#     return -amp + (2 * amp) * torch.rand(shape)
# 
# 
# @signal_fn
# def gauss(x, amp=1.0):
#     noise = amp * torch.randn(x.shape)
#     return x + noise.to(x.device)
# 
# 
# @signal_fn
# def white(x, amp=1.0):
#     return x + _uniform(x.shape, amp=amp).to(x.device)
# 
# 
# @signal_fn
# def pink(x, amp=1.0, dim=-1):
#     """
#     Adds pink noise to a given tensor along a specified dimension.
# 
#     Parameters:
#     - x (torch.Tensor): The input tensor to which pink noise will be added.
#     - amp (float, optional): The amplitude of the pink noise. Defaults to 1.0.
#     - dim (int, optional): The dimension along which to add pink noise. Defaults to -1.
# 
#     Returns:
#     - torch.Tensor: The input tensor with added pink noise.
#     """
#     cols = x.size(dim)
#     noise = torch.randn(cols, dtype=x.dtype, device=x.device)
#     noise = torch.fft.rfft(noise)
#     indices = torch.arange(1, noise.size(0), dtype=x.dtype, device=x.device)
#     noise[1:] /= torch.sqrt(indices)
#     noise = torch.fft.irfft(noise, n=cols)
#     noise = noise - noise.mean()
#     noise_amp = torch.sqrt(torch.mean(noise**2))
#     noise = noise * (amp / noise_amp)
#     return x + noise.to(x.device)
# 
# 
# @signal_fn
# def brown(x, amp=1.0, dim=-1):
#     noise = _uniform(x.shape, amp=amp)
#     noise = torch.cumsum(noise, dim=dim)
#     noise = scitex.dsp.norm.minmax(noise, amp=amp, dim=dim)
#     return x + noise.to(x.device)
# 
# 
# if __name__ == "__main__":
#     import sys
# 
#     import matplotlib.pyplot as plt
#     import scitex
# 
#     # Start
#     CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.gen.start(sys, plt)
# 
#     # Parameters
#     T_SEC = 1
#     FS = 128
# 
#     # Demo signal
#     xx, tt, fs = scitex.dsp.demo_sig(t_sec=T_SEC, fs=FS)
# 
#     funcs = {
#         "orig": lambda x: x,
#         "gauss": gauss,
#         "white": white,
#         "pink": pink,
#         "brown": brown,
#     }
# 
#     # Plots
#     fig, axes = scitex.plt.subplots(nrows=len(funcs), ncols=2, sharex=True, sharey=True)
#     count = 0
#     for (k, fn), axes_row in zip(funcs.items(), axes):
#         for ax in axes_row:
#             if count % 2 == 0:
#                 ax.plot(tt, fn(xx)[0, 0], label=k, c="blue")
#             else:
#                 ax.plot(tt, (fn(xx) - xx)[0, 0], label=f"{k} - orig", c="red")
#             count += 1
#             ax.legend(loc="upper right")
# 
#     fig.supxlabel("Time [s]")
#     fig.supylabel("Amplitude [?V]")
#     axes[0, 0].set_title("Signal + Noise")
#     axes[0, 1].set_title("Noise")
# 
#     scitex.io.save(fig, "traces.png")
# 
#     # Close
#     scitex.gen.close(CONFIG)
# 
# # EOF
# 
# """
# /home/ywatanabe/proj/entrance/scitex/dsp/add_noise.py
# """
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/dsp/add_noise.py
# --------------------------------------------------------------------------------
