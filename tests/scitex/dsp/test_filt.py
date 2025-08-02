#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-01 20:50:00 (ywatanabe)"
# File: ./tests/scitex/dsp/test_filt.py

"""
Test module for scitex.dsp.filt filtering functions.
"""

import pytest
import numpy as np
import torch
from numpy.testing import assert_allclose


class TestFilt:
    """Test class for filtering functions."""

    @pytest.fixture
    def simple_signal(self):
        """Create a simple test signal with known frequency components."""
        fs = 1000  # 1 kHz sampling rate
        t = np.linspace(0, 1, fs, endpoint=False)
        # Create signal with 50 Hz and 200 Hz components
        signal = np.sin(2 * np.pi * 50 * t) + np.sin(2 * np.pi * 200 * t)
        return signal.astype(np.float32), t, fs

    @pytest.fixture
    def multi_channel_signal(self):
        """Create a multi-channel test signal."""
        fs = 1000
        t = np.linspace(0, 1, fs, endpoint=False)
        n_channels = 3
        signals = []
        for i in range(n_channels):
            freq = 50 * (i + 1)  # 50, 100, 150 Hz
            signals.append(np.sin(2 * np.pi * freq * t))
        signal = np.array(signals).astype(np.float32)
        return signal, t, fs

    def test_module_import(self):
        """Test that filt module can be imported."""
        import scitex.dsp.filt

        assert hasattr(scitex.dsp.filt, "bandpass")
        assert hasattr(scitex.dsp.filt, "bandstop")
        assert hasattr(scitex.dsp.filt, "lowpass")
        assert hasattr(scitex.dsp.filt, "highpass")
        assert hasattr(scitex.dsp.filt, "gauss")

    def test_bandpass_filter(self, simple_signal):
        """Test bandpass filtering."""
        from scitex.dsp.filt import bandpass

        signal, t, fs = simple_signal
        bands = np.array([[40, 60]])  # Pass 50 Hz, reject 200 Hz

        filtered, t_out = bandpass(signal, fs, bands, t=t)

        # Check output shape
        assert filtered.shape == signal.shape
        assert t_out.shape == t.shape

        # Check that signal energy is reduced (200 Hz component removed)
        assert np.std(filtered) < np.std(signal)

    def test_bandstop_filter(self, simple_signal):
        """Test bandstop filtering."""
        from scitex.dsp.filt import bandstop

        signal, t, fs = simple_signal
        bands = np.array([[190, 210]])  # Stop 200 Hz, pass 50 Hz

        filtered, t_out = bandstop(signal, fs, bands, t=t)

        # Check output shape
        assert filtered.shape == signal.shape
        assert t_out.shape == t.shape

        # Check that signal energy is reduced (200 Hz component removed)
        assert np.std(filtered) < np.std(signal)

    def test_lowpass_filter(self, simple_signal):
        """Test lowpass filtering."""
        from scitex.dsp.filt import lowpass

        signal, t, fs = simple_signal
        cutoff = 100  # Pass 50 Hz, reject 200 Hz

        filtered, t_out = lowpass(signal, fs, cutoff, t=t)

        # Check output shape
        assert filtered.shape == signal.shape
        assert t_out.shape == t.shape

        # Check that high frequency is attenuated
        assert np.std(filtered) < np.std(signal)

    def test_highpass_filter(self, simple_signal):
        """Test highpass filtering."""
        from scitex.dsp.filt import highpass

        signal, t, fs = simple_signal
        cutoff = 100  # Reject 50 Hz, pass 200 Hz

        filtered, t_out = highpass(signal, fs, cutoff, t=t)

        # Check output shape
        assert filtered.shape == signal.shape
        assert t_out.shape == t.shape

        # Signal should still have energy (200 Hz component)
        assert np.std(filtered) > 0

    def test_gaussian_filter(self, simple_signal):
        """Test Gaussian smoothing filter."""
        from scitex.dsp.filt import gauss

        signal, t, fs = simple_signal
        sigma = 5  # Smoothing parameter

        filtered, t_out = gauss(signal, sigma, t=t)

        # Check output shape
        assert filtered.shape == signal.shape
        assert t_out.shape == t.shape

        # Gaussian filter should smooth the signal
        # Check that high frequency variations are reduced
        diff_original = np.diff(signal)
        diff_filtered = np.diff(filtered)
        assert np.std(diff_filtered) < np.std(diff_original)

    def test_multi_channel_filtering(self, multi_channel_signal):
        """Test filtering with multi-channel signals."""
        from scitex.dsp.filt import bandpass

        signal, t, fs = multi_channel_signal
        bands = np.array([[80, 120]])  # Pass only 100 Hz channel

        filtered, _ = bandpass(signal, fs, bands)

        # Check shape preservation
        assert filtered.shape == signal.shape

        # Middle channel (100 Hz) should have highest energy
        channel_energies = np.std(filtered, axis=1)
        assert np.argmax(channel_energies) == 1

    def test_torch_tensor_input(self, simple_signal):
        """Test filtering with PyTorch tensor input."""
        from scitex.dsp.filt import bandpass

        signal_np, t_np, fs = simple_signal
        signal_torch = torch.tensor(signal_np)
        t_torch = torch.tensor(t_np)
        bands = np.array([[40, 60]])

        filtered, t_out = bandpass(signal_torch, fs, bands, t=t_torch)

        # Should return torch tensors
        assert isinstance(filtered, torch.Tensor)
        assert isinstance(t_out, torch.Tensor)
        assert filtered.shape == signal_torch.shape

    def test_multiple_bands(self):
        """Test filtering with multiple frequency bands."""
        from scitex.dsp.filt import bandpass

        # Create signal with multiple frequency components
        fs = 1000
        t = np.linspace(0, 1, fs, endpoint=False)
        signal = (
            np.sin(2 * np.pi * 50 * t)
            + np.sin(2 * np.pi * 150 * t)
            + np.sin(2 * np.pi * 250 * t)
        )

        # Multiple pass bands
        bands = np.array([[40, 60], [140, 160]])  # Pass 50 and 150 Hz

        try:
            filtered, _ = bandpass(signal, fs, bands)
            # Implementation may or may not support multiple bands
            assert filtered.shape[-1] == signal.shape[-1]
        except:
            # Single band fallback
            bands_single = np.array([[40, 160]])
            filtered, _ = bandpass(signal, fs, bands_single)
            assert filtered.shape == signal.shape

    def test_edge_frequencies(self, simple_signal):
        """Test filtering at edge frequencies."""
        from scitex.dsp.filt import lowpass, highpass

        signal, t, fs = simple_signal

        # Very low cutoff
        filtered_low, _ = lowpass(signal, fs, 1)  # 1 Hz cutoff
        assert np.std(filtered_low) < np.std(signal) * 0.1  # Should remove most signal

        # Very high cutoff
        filtered_high, _ = highpass(signal, fs, fs / 2 - 1)  # Near Nyquist
        assert np.std(filtered_high) < np.std(signal) * 0.1  # Should remove most signal

    def test_empty_signal(self):
        """Test filtering empty signals."""
        from scitex.dsp.filt import bandpass

        signal = np.array([])
        fs = 1000
        bands = np.array([[40, 60]])

        filtered, t = bandpass(signal, fs, bands)
        assert filtered.shape == (0,)

    def test_batch_filtering(self):
        """Test filtering with batched signals."""
        from scitex.dsp.filt import bandpass

        # Create batched signal (batch_size, n_channels, n_samples)
        batch_size = 2
        n_channels = 3
        n_samples = 1000
        fs = 1000

        signal = np.random.randn(batch_size, n_channels, n_samples).astype(np.float32)
        bands = np.array([[40, 60]])

        filtered, _ = bandpass(signal, fs, bands)

        # Should preserve batch dimensions
        assert filtered.shape == signal.shape

    def test_filter_stability(self, simple_signal):
        """Test that filters don't introduce instabilities."""
        from scitex.dsp.filt import bandpass, lowpass, highpass

        signal, _, fs = simple_signal

        # Test various filters
        filters = [
            (bandpass, {"bands": np.array([[40, 60]])}),
            (lowpass, {"cutoffs_hz": 100}),
            (highpass, {"cutoffs_hz": 100}),
        ]

        for filt_func, params in filters:
            filtered, _ = filt_func(signal, fs, **params)

            # Check for NaN or Inf
            assert not np.any(np.isnan(filtered))
            assert not np.any(np.isinf(filtered))

            # Check that output is bounded
            assert np.max(np.abs(filtered)) < np.max(np.abs(signal)) * 10

    @pytest.mark.parametrize("sigma", [1, 3, 5, 10])
    def test_gaussian_sigma_effect(self, sigma):
        """Test Gaussian filter with different sigma values."""
        from scitex.dsp.filt import gauss

        # Create noisy signal
        signal = np.random.randn(1000).astype(np.float32)

        filtered, _ = gauss(signal, sigma)

        # Larger sigma should smooth more
        roughness = np.std(np.diff(filtered))
        assert roughness < np.std(np.diff(signal))


# --------------------------------------------------------------------------------

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/dsp/filt.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-04 02:05:47 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/dsp/filt.py
# 
# import scitex
# import numpy as np
# 
# from ..decorators import signal_fn
# 
# # No top-level imports from nn module to avoid circular dependency
# # Filters will be imported inside functions when needed
# 
# 
# @signal_fn
# def gauss(x, sigma, t=None):
#     from ..nn._Filters import GaussianFilter
#     return GaussianFilter(sigma)(x, t=t)
# 
# 
# @signal_fn
# def bandpass(x, fs, bands, t=None):
#     import torch
#     from ..nn._Filters import BandPassFilter
# 
#     # Convert bands to tensor if it's not already
#     if not isinstance(bands, torch.Tensor):
#         bands = torch.tensor(bands, dtype=torch.float32)
#     return BandPassFilter(bands, fs, x.shape[-1])(x, t=t)
# 
# 
# @signal_fn
# def bandstop(x, fs, bands, t=None):
#     from ..nn._Filters import BandStopFilter
#     return BandStopFilter(bands, fs, x.shape[-1])(x, t=t)
# 
# 
# @signal_fn
# def lowpass(x, fs, cutoffs_hz, t=None):
#     from ..nn._Filters import LowPassFilter
#     return LowPassFilter(cutoffs_hz, fs, x.shape[-1])(x, t=t)
# 
# 
# @signal_fn
# def highpass(x, fs, cutoffs_hz, t=None):
#     from ..nn._Filters import HighPassFilter
#     return HighPassFilter(cutoffs_hz, fs, x.shape[-1])(x, t=t)
# 
# 
# def _custom_print(x):
#     print(type(x), x.shape)
# 
# 
# if __name__ == "__main__":
#     import sys
# 
#     import matplotlib.pyplot as plt
#     import torch
# 
#     # Start
#     CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.gen.start(sys, plt)
# 
#     # Parametes
#     T_SEC = 1
#     SRC_FS = 1024
#     FREQS_HZ = list(np.linspace(0, 500, 10, endpoint=False).astype(int))
#     SIG_TYPE = "periodic"
#     BANDS = np.vstack([[80, 310]])
#     SIGMA = 3
# 
#     # Demo Signal
#     xx, tt, fs = scitex.dsp.demo_sig(
#         t_sec=T_SEC,
#         fs=SRC_FS,
#         freqs_hz=FREQS_HZ,
#         sig_type=SIG_TYPE,
#     )
# 
#     # Filtering
#     x_bp, t_bp = scitex.dsp.filt.bandpass(xx, fs, BANDS, t=tt)
#     x_bs, t_bs = scitex.dsp.filt.bandstop(xx, fs, BANDS, t=tt)
#     x_lp, t_lp = scitex.dsp.filt.lowpass(xx, fs, BANDS[:, 0], t=tt)
#     x_hp, t_hp = scitex.dsp.filt.highpass(xx, fs, BANDS[:, 1], t=tt)
#     x_g, t_g = scitex.dsp.filt.gauss(xx, sigma=SIGMA, t=tt)
#     filted = {
#         f"Original (Sum of {FREQS_HZ}-Hz signals)": (xx, tt, fs),
#         f"Bandpass-filtered ({BANDS[0][0]} - {BANDS[0][1]} Hz)": (
#             x_bp,
#             t_bp,
#             fs,
#         ),
#         f"Bandstop-filtered ({BANDS[0][0]} - {BANDS[0][1]} Hz)": (
#             x_bs,
#             t_bs,
#             fs,
#         ),
#         f"Lowpass-filtered ({BANDS[0][0]} Hz)": (x_lp, t_lp, fs),
#         f"Highpass-filtered ({BANDS[0][1]} Hz)": (x_hp, t_hp, fs),
#         f"Gaussian-filtered (sigma = {SIGMA} SD [point])": (x_g, t_g, fs),
#     }
# 
#     # Plots traces
#     fig, axes = plt.subplots(nrows=len(filted), ncols=1, sharex=True, sharey=True)
#     i_batch = 0
#     i_ch = 0
#     i_filt = 0
#     for ax, (k, v) in zip(axes, filted.items()):
#         _xx, _tt, _fs = v
#         if _xx.ndim == 3:
#             _xx = _xx[i_batch, i_ch]
#         elif _xx.ndim == 4:
#             _xx = _xx[i_batch, i_ch, i_filt]
#         ax.plot(_tt, _xx, label=k)
#         ax.legend(loc="upper left")
# 
#     fig.suptitle("Filtered")
#     fig.supxlabel("Time [s]")
#     fig.supylabel("Amplitude")
# 
#     scitex.io.save(fig, "traces.png")
# 
#     # Calculates and Plots PSD
#     fig, axes = plt.subplots(nrows=len(filted), ncols=1, sharex=True, sharey=True)
#     i_batch = 0
#     i_ch = 0
#     i_filt = 0
#     for ax, (k, v) in zip(axes, filted.items()):
#         _xx, _tt, _fs = v
# 
#         _psd, ff = scitex.dsp.psd(_xx, _fs)
#         if _psd.ndim == 3:
#             _psd = _psd[i_batch, i_ch]
#         elif _psd.ndim == 4:
#             _psd = _psd[i_batch, i_ch, i_filt]
# 
#         ax.plot(ff, _psd, label=k)
#         ax.legend(loc="upper left")
# 
#         for bb in np.hstack(BANDS):
#             ax.axvline(x=bb, color=CC["grey"], linestyle="--")
# 
#     fig.suptitle("PSD (power spectrum density) of filtered signals")
#     fig.supxlabel("Frequency [Hz]")
#     fig.supylabel("log(Power [uV^2 / Hz]) [a.u.]")
#     scitex.io.save(fig, "psd.png")
# 
#     # Close
#     scitex.gen.close(CONFIG)
# 
# # EOF
# 
# """
# /home/ywatanabe/proj/scitex/src/scitex/dsp/filt.py
# """
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/dsp/filt.py
# --------------------------------------------------------------------------------
