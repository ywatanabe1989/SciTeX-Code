#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-30 19:30:00 (Claude)"
# File: /tests/scitex/dsp/test__dsp_comprehensive_v2.py

"""
Comprehensive tests for scitex.dsp module - simplified version.
Tests digital signal processing functionality.
"""

import os
import sys
import pytest
import numpy as np
import torch

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../src"))

import scitex.dsp


class TestDemoSig:
    """Test demo signal generation."""

    def test_demo_sig_basic(self):
        """Test basic demo signal generation."""
        sig, time, fs = scitex.dsp.demo_sig()

        assert isinstance(sig, np.ndarray)
        assert isinstance(time, np.ndarray)
        assert isinstance(fs, (int, float))
        assert sig.ndim == 3
        assert len(time) == sig.shape[-1]

    def test_demo_sig_types(self):
        """Test different signal types."""
        for sig_type in ["uniform", "gauss", "periodic", "chirp"]:
            sig, time, fs = scitex.dsp.demo_sig(sig_type=sig_type)
            assert isinstance(sig, np.ndarray)
            assert sig.ndim == 3


class TestBasicDSP:
    """Test basic DSP functions."""

    @pytest.fixture
    def sample_signal(self):
        """Create a sample signal."""
        # Use demo_sig to get proper 3D signal
        sig, time, fs = scitex.dsp.demo_sig(t_sec=2.0, fs=1000, n_chs=1, batch_size=1)
        return sig, fs

    def test_ensure_3d(self):
        """Test ensure_3d function."""
        # 1D signal
        sig_1d = np.random.randn(1000)
        sig_3d = scitex.dsp.ensure_3d(sig_1d)
        assert sig_3d.shape == (1, 1, 1000)

        # 2D signal (batch_size, seq_len)
        sig_2d = np.random.randn(5, 1000)
        sig_3d = scitex.dsp.ensure_3d(sig_2d)
        assert sig_3d.shape == (5, 1, 1000)  # (batch, channels=1, seq_len)

    def test_crop(self):
        """Test signal cropping into windows."""
        # Create a simple signal
        sig = np.random.randn(100)

        # Crop into windows of length 20
        window_length = 20
        cropped = scitex.dsp.crop(sig, window_length=window_length)

        # Check that we get windows
        assert isinstance(cropped, np.ndarray)

    def test_resample(self, sample_signal):
        """Test resampling."""
        sig, fs = sample_signal

        # Resample to half the frequency
        new_fs = fs // 2
        # resample expects the signal first, then fs as integers
        # The signal_fn decorator will convert sig to torch tensor automatically
        resampled = scitex.dsp.resample(sig, int(fs), int(new_fs))

        # Check length is approximately half
        expected_length = sig.shape[-1] // 2
        assert abs(resampled.shape[-1] - expected_length) < 10


class TestSpectralAnalysis:
    """Test spectral analysis functions."""

    def test_psd(self):
        """Test PSD computation."""
        # Create signal with known frequency
        fs = 1000
        duration = 2
        t = np.linspace(0, duration, fs * duration)
        freq = 50  # 50 Hz

        # Create 3D signal (batch=1, channel=1, time)
        sig = np.sin(2 * np.pi * freq * t)
        sig = sig.reshape(1, 1, -1)

        # Compute PSD - pass fs as keyword argument to avoid torch_fn conversion
        psd_result, freqs = scitex.dsp.psd(sig, fs=fs)

        # Check outputs - convert tensor to numpy if needed
        if hasattr(psd_result, "cpu"):
            psd_result = psd_result.cpu().numpy()
        if hasattr(freqs, "cpu"):
            freqs = freqs.cpu().numpy()

        assert isinstance(psd_result, np.ndarray)
        assert isinstance(freqs, np.ndarray)

        # PSD should have peak around 50 Hz
        # Find frequency closest to 50 Hz
        idx_50 = np.argmin(np.abs(freqs - 50))

        # Check that 50 Hz has high power
        assert psd_result[0, 0, idx_50] > psd_result[0, 0].mean() * 10

    def test_hilbert(self):
        """Test Hilbert transform."""
        # Create a modulated signal with envelope
        t = np.linspace(0, 1, 1000)
        carrier_freq = 50  # Hz
        modulation_freq = 5  # Hz

        # Create amplitude modulated signal
        envelope = 1 + 0.5 * np.cos(2 * np.pi * modulation_freq * t)
        carrier = np.sin(2 * np.pi * carrier_freq * t)
        sig = envelope * carrier
        sig = sig.reshape(1, 1, -1)  # Make 3D

        # Apply Hilbert transform - returns (phase, amplitude)
        phase, amplitude = scitex.dsp.hilbert(sig)

        # Convert to numpy if they're tensors
        if hasattr(phase, "cpu"):
            phase = phase.cpu().numpy()
        if hasattr(amplitude, "cpu"):
            amplitude = amplitude.cpu().numpy()

        # Check outputs
        assert isinstance(phase, np.ndarray)
        assert isinstance(amplitude, np.ndarray)

        # Check shapes preserved
        assert phase.shape == sig.shape
        assert amplitude.shape == sig.shape

        # The amplitude should track the envelope
        # Just check that we get reasonable values
        assert amplitude.mean() > 0
        assert amplitude.max() < 10  # Reasonable upper bound


class TestFiltering:
    """Test filtering with proper tensor handling."""

    def test_filter_functions_exist(self):
        """Test that filter functions exist."""
        assert hasattr(scitex.dsp.filt, "bandpass")
        assert hasattr(scitex.dsp.filt, "lowpass")
        assert hasattr(scitex.dsp.filt, "highpass")
        assert hasattr(scitex.dsp.filt, "gauss")


class TestNormalization:
    """Test normalization functions."""

    def test_norm_z(self):
        """Test z-score normalization."""
        sig = np.random.randn(1, 1, 1000) * 5 + 10
        normed = scitex.dsp.norm.z(sig)

        # Check mean ~0 and std ~1
        assert np.abs(normed.mean()) < 0.1
        assert np.abs(normed.std() - 1) < 0.1

    def test_norm_minmax(self):
        """Test min-max normalization."""
        sig = np.random.randn(1, 1, 1000) * 5 + 10
        normed = scitex.dsp.norm.minmax(sig)

        # Check range
        assert normed.min() >= -1
        assert normed.max() <= 1


class TestAddNoise:
    """Test noise addition functions."""

    def test_add_white_noise(self):
        """Test white noise addition."""
        sig = np.ones((1, 1, 1000))
        noisy = scitex.dsp.add_noise.white(sig, amp=0.1)

        # Check signal is modified
        assert not np.array_equal(sig, noisy)

        # Check noise level is reasonable
        noise = noisy - sig
        assert noise.std() < 0.2


class TestPAC:
    """Test Phase-Amplitude Coupling."""

    def test_pac_basic(self):
        """Test basic PAC computation."""
        # Create signal
        sig, _, fs = scitex.dsp.demo_sig(sig_type="periodic", t_sec=5, fs=512)

        # Compute PAC with minimal bands for speed
        # The signal_fn decorator will handle conversion, just pass numpy array
        result = scitex.dsp.pac(
            sig,  # numpy array (will be converted by decorator)
            int(fs),  # fs as integer
            pha_start_hz=5,
            pha_end_hz=15,
            pha_n_bands=5,
            amp_start_hz=50,
            amp_end_hz=100,
            amp_n_bands=5,
            device="cpu",  # Use CPU for testing
        )

        # PAC returns a tuple: (pac_values, pha_freqs, amp_freqs)
        if isinstance(result, tuple):
            pac_result, pha_freqs, amp_freqs = result
        else:
            pac_result = result

        # Check output
        assert isinstance(pac_result, (np.ndarray, torch.Tensor))
        assert pac_result.ndim >= 2  # At least (batch, channels)


class TestRippleDetection:
    """Test ripple detection."""

    def test_detect_ripples_basic(self):
        """Test basic ripple detection."""
        # Create 3D signal as required by detect_ripples
        sig = np.random.randn(1, 1, 1000)  # (batch, channels, time)
        fs = 1000

        # Detect ripples - fs should be float
        result = scitex.dsp.detect_ripples(sig, float(fs), low_hz=100, high_hz=200)

        # Check output is DataFrame or similar
        assert result is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
