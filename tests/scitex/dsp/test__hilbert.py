#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-07 10:52:57 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/dsp/test__hilbert.py

import pytest
import numpy as np
import torch
from scitex.dsp import hilbert


class TestHilbert:
    """Test cases for hilbert transform function."""

    @pytest.fixture
    def simple_signal(self):
        """Create a simple sinusoidal signal."""
        t = np.linspace(0, 1, 1000)
        freq = 10  # Hz
        signal = np.sin(2 * np.pi * freq * t)
        return signal.astype(np.float32)

    @pytest.fixture
    def complex_signal(self):
        """Create a multi-frequency signal."""
        t = np.linspace(0, 1, 1000)
        signal = (
            np.sin(2 * np.pi * 5 * t)
            + 0.5 * np.sin(2 * np.pi * 20 * t)
            + 0.3 * np.sin(2 * np.pi * 50 * t)
        )
        return signal.astype(np.float32)

    def test_import(self):
        """Test that hilbert can be imported."""
        assert callable(hilbert)

    def test_numpy_1d_signal(self, simple_signal):
        """Test hilbert transform on 1D numpy array."""
        phase, amplitude = hilbert(simple_signal)

        assert isinstance(phase, np.ndarray)
        assert isinstance(amplitude, np.ndarray)
        assert phase.shape == simple_signal.shape
        assert amplitude.shape == simple_signal.shape
        assert phase.dtype == np.float32
        assert amplitude.dtype == np.float32

    def test_torch_1d_signal(self, simple_signal):
        """Test hilbert transform on 1D torch tensor."""
        tensor_signal = torch.from_numpy(simple_signal)
        phase, amplitude = hilbert(tensor_signal)

        assert isinstance(phase, torch.Tensor)
        assert isinstance(amplitude, torch.Tensor)
        assert phase.shape == tensor_signal.shape
        assert amplitude.shape == tensor_signal.shape
        assert phase.dtype == torch.float32
        assert amplitude.dtype == torch.float32

    def test_2d_signal(self, simple_signal):
        """Test hilbert transform on 2D signal (multi-channel)."""
        # Create 4-channel signal
        signal_2d = np.stack([simple_signal] * 4)
        phase, amplitude = hilbert(signal_2d)

        assert phase.shape == signal_2d.shape
        assert amplitude.shape == signal_2d.shape

        # Check that all channels are processed identically
        for i in range(1, 4):
            np.testing.assert_allclose(phase[0], phase[i], rtol=1e-5)
            np.testing.assert_allclose(amplitude[0], amplitude[i], rtol=1e-5)

    def test_3d_signal(self, simple_signal):
        """Test hilbert transform on 3D signal (batch, channel, time)."""
        # Create batch of 2, 4 channels each
        signal_3d = np.stack([np.stack([simple_signal] * 4)] * 2)
        phase, amplitude = hilbert(signal_3d)

        assert phase.shape == signal_3d.shape
        assert amplitude.shape == signal_3d.shape

    def test_phase_amplitude_relationship(self, simple_signal):
        """Test that phase and amplitude have correct relationship."""
        phase, amplitude = hilbert(simple_signal)

        # Amplitude should be non-negative
        assert np.all(amplitude >= 0)

        # Phase should be in radians
        assert np.all(phase >= -np.pi)
        assert np.all(phase <= np.pi)

        # For a sine wave, amplitude should be relatively constant
        # (except at edges due to boundary effects)
        center_amp = amplitude[100:-100]
        assert np.std(center_amp) / np.mean(center_amp) < 0.1

    def test_constant_signal(self):
        """Test hilbert transform on constant signal."""
        constant = np.ones(1000, dtype=np.float32)
        phase, amplitude = hilbert(constant)

        # Constant signal should have near-constant amplitude
        # Phase is undefined for DC component
        assert np.allclose(amplitude[100:-100], 1.0, rtol=0.1)

    def test_zero_signal(self):
        """Test hilbert transform on zero signal."""
        zeros = np.zeros(1000, dtype=np.float32)
        phase, amplitude = hilbert(zeros)

        # Zero signal should have zero amplitude
        assert np.allclose(amplitude, 0.0, atol=1e-6)

    def test_complex_signal_frequencies(self, complex_signal):
        """Test hilbert transform preserves frequency content."""
        phase, amplitude = hilbert(complex_signal)

        # Check that amplitude modulation captures the signal envelope
        assert amplitude.min() >= 0
        assert amplitude.max() <= 2.0  # Max possible for our complex signal

    def test_dim_parameter(self, simple_signal):
        """Test hilbert transform along different dimensions."""
        # Create 2D signal
        signal_2d = np.stack([simple_signal, simple_signal * 0.5])

        # Transform along last dimension (default)
        phase1, amp1 = hilbert(signal_2d, dim=-1)
        assert phase1.shape == signal_2d.shape

        # Transform along first dimension
        phase2, amp2 = hilbert(signal_2d, dim=0)
        assert phase2.shape == signal_2d.shape

        # Results should be different
        assert not np.allclose(phase1, phase2)
        assert not np.allclose(amp1, amp2)

    def test_instantaneous_frequency(self, simple_signal):
        """Test that instantaneous frequency can be derived from phase."""
        phase, amplitude = hilbert(simple_signal)

        # Compute instantaneous frequency from phase derivative
        fs = 1000  # Sampling frequency
        inst_freq = np.diff(np.unwrap(phase)) * fs / (2 * np.pi)

        # For a 10 Hz sine wave, instantaneous frequency should be ~10 Hz
        # (except at boundaries)
        center_freq = inst_freq[100:-100]
        assert np.abs(np.mean(center_freq) - 10.0) < 0.5

    def test_analytic_signal_property(self, simple_signal):
        """Test that hilbert transform creates proper analytic signal."""
        phase, amplitude = hilbert(simple_signal)

        # Reconstruct analytic signal
        analytic = amplitude * np.exp(1j * phase)

        # Real part should approximate original signal
        reconstructed = np.real(analytic)

        # Allow some error at boundaries
        center_orig = simple_signal[50:-50]
        center_recon = reconstructed[50:-50]
        correlation = np.corrcoef(center_orig, center_recon)[0, 1]
        assert correlation > 0.99

    def test_torch_device_handling(self, simple_signal):
        """Test hilbert transform handles torch devices correctly."""
        if not torch.cuda.is_available():
            pytest.skip("CUDA not available")

        # Create tensor on GPU
        tensor_signal = torch.from_numpy(simple_signal).cuda()
        phase, amplitude = hilbert(tensor_signal)

        assert phase.device == tensor_signal.device
        assert amplitude.device == tensor_signal.device
        assert phase.is_cuda
        assert amplitude.is_cuda

    def test_batch_consistency(self, simple_signal):
        """Test that batched processing gives same results."""
        # Single signal
        phase1, amp1 = hilbert(simple_signal)

        # Batched signal
        batched = np.stack([simple_signal, simple_signal])
        phase2, amp2 = hilbert(batched)

        # Results should be identical for both batch items
        np.testing.assert_allclose(phase1, phase2[0], rtol=1e-5)
        np.testing.assert_allclose(phase1, phase2[1], rtol=1e-5)
        np.testing.assert_allclose(amp1, amp2[0], rtol=1e-5)
        np.testing.assert_allclose(amp1, amp2[1], rtol=1e-5)

    def test_dtype_preservation(self):
        """Test that output dtype matches input dtype."""
        for dtype in [np.float32, np.float64]:
            signal = np.random.randn(1000).astype(dtype)
            phase, amplitude = hilbert(signal)

            assert phase.dtype == dtype
            assert amplitude.dtype == dtype

    def test_empty_signal(self):
        """Test hilbert transform on empty signal."""
        empty = np.array([], dtype=np.float32)
        phase, amplitude = hilbert(empty)

        assert phase.shape == (0,)
        assert amplitude.shape == (0,)

    def test_single_sample(self):
        """Test hilbert transform on single sample."""
        single = np.array([1.0], dtype=np.float32)
        phase, amplitude = hilbert(single)

        assert phase.shape == (1,)
        assert amplitude.shape == (1,)
        assert np.isfinite(phase[0])
        assert np.isfinite(amplitude[0])

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/dsp/_hilbert.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-04 02:07:11 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/dsp/_hilbert.py
# 
# """
# This script does XYZ.
# """
# 
# import sys
# 
# import matplotlib.pyplot as plt
# from ..nn._Hilbert import Hilbert
# 
# from ..decorators import signal_fn
# 
# 
# # Functions
# @signal_fn
# def hilbert(
#     x,
#     dim=-1,
# ):
#     y = Hilbert(x.shape[-1], dim=dim)(x)
#     return y[..., 0], y[..., 1]
# 
# 
# if __name__ == "__main__":
#     import scitex
# 
#     # Start
#     CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.gen.start(sys, plt)
# 
#     # Parameters
#     T_SEC = 1.0
#     FS = 400
#     SIG_TYPE = "chirp"
# 
#     # Demo signal
#     xx, tt, fs = scitex.dsp.demo_sig(t_sec=T_SEC, fs=FS, sig_type=SIG_TYPE)
# 
#     # Main
#     pha, amp = hilbert(
#         xx,
#         dim=-1,
#     )
#     # (32, 19, 1280, 2)
# 
#     # Plots
#     fig, axes = scitex.plt.subplots(nrows=2, sharex=True)
#     fig.suptitle("Hilbert Transformation")
# 
#     axes[0].plot(tt, xx[0, 0], label=SIG_TYPE)
#     axes[0].plot(tt, amp[0, 0], label="Amplidue")
#     axes[0].legend()
#     # axes[0].set_xlabel("Time [s]")
#     axes[0].set_ylabel("Amplitude [?V]")
# 
#     axes[1].plot(tt, pha[0, 0], label="Phase")
#     axes[1].legend()
# 
#     axes[1].set_xlabel("Time [s]")
#     axes[1].set_ylabel("Phase [rad]")
# 
#     # plt.show()
#     scitex.io.save(fig, "traces.png")
# 
#     # Close
#     scitex.gen.close(CONFIG)
# 
# # EOF
# 
# """
# /home/ywatanabe/proj/entrance/scitex/dsp/_hilbert.py
# """
# 
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/dsp/_hilbert.py
# --------------------------------------------------------------------------------
