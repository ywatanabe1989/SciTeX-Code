#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-30 18:45:00 (Claude)"
# File: /tests/scitex/dsp/test__dsp_comprehensive.py

"""
Comprehensive tests for scitex.dsp module core functions.
Tests digital signal processing functionality.
"""

import os
import sys
import pytest
import numpy as np
import pandas as pd
from scipy import signal

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../src"))

import scitex.dsp


class TestDemoSig:
    """Test demo signal generation."""

    def test_demo_sig_basic(self):
        """Test basic demo signal generation."""
        # Generate a demo signal
        sig, time, fs = scitex.dsp.demo_sig()

        # Check types
        assert isinstance(sig, np.ndarray)
        assert isinstance(time, np.ndarray)
        assert isinstance(fs, (int, float))

        # Check signal is 3D (batch, channels, time)
        assert sig.ndim == 3

        # Check time matches last dimension of signal
        assert len(time) == sig.shape[-1]

        # Check values are finite
        assert np.all(np.isfinite(sig))
        assert np.all(np.isfinite(time))

    def test_demo_sig_parameters(self):
        """Test demo signal with parameters."""
        # Test with specific duration and sampling rate
        t_sec = 2.0  # seconds
        fs = 1000  # Hz

        sig, time, fs_out = scitex.dsp.demo_sig(t_sec=t_sec, fs=fs)

        # Check sampling rate matches
        assert fs_out == fs

        # Check length matches expected
        expected_length = int(t_sec * fs)
        assert sig.shape[-1] == expected_length
        assert len(time) == expected_length


class TestFiltering:
    """Test filtering functions."""

    @pytest.fixture
    def sample_signal(self):
        """Create a sample signal with known frequency components."""
        sfreq = 1000  # Hz
        duration = 2  # seconds
        t = np.linspace(0, duration, sfreq * duration)

        # Create signal with 10Hz, 50Hz, and 200Hz components
        sig = (
            np.sin(2 * np.pi * 10 * t)
            + 0.5 * np.sin(2 * np.pi * 50 * t)
            + 0.3 * np.sin(2 * np.pi * 200 * t)
        )

        return sig, sfreq

    def test_filt_bandpass(self, sample_signal):
        """Test bandpass filtering."""
        sig, sfreq = sample_signal

        # Apply bandpass filter (30-70 Hz)
        filtered = scitex.dsp.filt.bandpass(sig, sfreq, (30, 70))

        # Check output shape
        assert filtered.shape == sig.shape

        # Check values are finite
        assert np.all(np.isfinite(filtered))

        # The 50Hz component should be preserved
        # Check power spectrum
        freqs, psd = signal.periodogram(filtered, sfreq)
        peak_freq = freqs[np.argmax(psd)]
        assert 45 < peak_freq < 55  # Should be around 50Hz

    def test_filt_lowpass(self, sample_signal):
        """Test lowpass filtering."""
        sig, sfreq = sample_signal

        # Apply lowpass filter (30 Hz)
        filtered = scitex.dsp.filt.lowpass(sig, sfreq, 30)

        # Check output shape
        assert filtered.shape == sig.shape

        # High frequency components should be attenuated
        freqs, psd_orig = signal.periodogram(sig, sfreq)
        freqs, psd_filt = signal.periodogram(filtered, sfreq)

        # Power at 200Hz should be significantly reduced
        idx_200 = np.argmin(np.abs(freqs - 200))
        assert psd_filt[idx_200] < 0.1 * psd_orig[idx_200]

    def test_filt_highpass(self, sample_signal):
        """Test highpass filtering."""
        sig, sfreq = sample_signal

        # Apply highpass filter (100 Hz)
        filtered = scitex.dsp.filt.highpass(sig, sfreq, 100)

        # Check output shape
        assert filtered.shape == sig.shape

        # Low frequency components should be attenuated
        freqs, psd_orig = signal.periodogram(sig, sfreq)
        freqs, psd_filt = signal.periodogram(filtered, sfreq)

        # Power at 10Hz should be significantly reduced
        idx_10 = np.argmin(np.abs(freqs - 10))
        assert psd_filt[idx_10] < 0.1 * psd_orig[idx_10]


class TestSpectralAnalysis:
    """Test spectral analysis functions."""

    @pytest.fixture
    def test_signal(self):
        """Create test signal with known spectral content."""
        sfreq = 512
        duration = 4
        t = np.linspace(0, duration, sfreq * duration)

        # Create signal with specific frequency components
        sig = (
            np.sin(2 * np.pi * 10 * t)  # Alpha (10 Hz)
            + np.sin(2 * np.pi * 20 * t)  # Beta (20 Hz)
            + 0.5 * np.sin(2 * np.pi * 40 * t)
        )  # Gamma (40 Hz)

        return sig, sfreq

    def test_psd_basic(self, test_signal):
        """Test basic PSD computation."""
        sig, sfreq = test_signal

        # Compute PSD
        psd, freqs = scitex.dsp.psd(sig, sfreq)

        # Check outputs
        assert isinstance(freqs, np.ndarray)
        assert isinstance(psd, np.ndarray)
        assert len(freqs) == len(psd)

        # Check frequency range
        assert freqs[0] >= 0
        assert freqs[-1] <= sfreq / 2  # Nyquist

        # Check PSD values are non-negative
        assert np.all(psd >= 0)

        # Check peaks at expected frequencies
        idx_10 = np.argmin(np.abs(freqs - 10))
        idx_20 = np.argmin(np.abs(freqs - 20))
        idx_40 = np.argmin(np.abs(freqs - 40))

        # These should be local maxima
        assert psd[idx_10] > psd[idx_10 - 2 : idx_10 + 3].mean() * 2
        assert psd[idx_20] > psd[idx_20 - 2 : idx_20 + 3].mean() * 2
        assert psd[idx_40] > psd[idx_40 - 2 : idx_40 + 3].mean() * 2

    def test_psd_multidimensional(self):
        """Test PSD with multidimensional input."""
        sfreq = 256
        n_channels = 5
        n_samples = 1024

        # Create multichannel signal
        sig = np.random.randn(n_channels, n_samples)

        # Add different frequency to each channel
        t = np.linspace(0, n_samples / sfreq, n_samples)
        for ch in range(n_channels):
            sig[ch] += np.sin(2 * np.pi * (10 + ch * 5) * t)

        # Compute PSD
        psd, freqs = scitex.dsp.psd(sig, sfreq)

        # Check shape
        assert psd.shape[0] == n_channels
        assert len(freqs) == psd.shape[1]


class TestHilbertTransform:
    """Test Hilbert transform and related functions."""

    def test_hilbert_basic(self):
        """Test basic Hilbert transform."""
        # Create a simple sinusoidal signal
        sfreq = 1000
        duration = 1
        t = np.linspace(0, duration, sfreq * duration)
        freq = 50  # Hz
        sig = np.sin(2 * np.pi * freq * t)

        # Apply Hilbert transform
        analytic = scitex.dsp.hilbert(sig)

        # Check output is complex
        assert np.iscomplexobj(analytic)

        # Check length preserved
        assert len(analytic) == len(sig)

        # Check instantaneous amplitude is approximately constant
        amplitude = np.abs(analytic)
        assert np.std(amplitude[100:-100]) < 0.1  # Ignore edge effects

        # Check instantaneous phase increases linearly
        phase = np.angle(analytic)
        phase_diff = np.diff(np.unwrap(phase))
        expected_phase_diff = 2 * np.pi * freq / sfreq
        assert np.abs(np.mean(phase_diff) - expected_phase_diff) < 0.01

    def test_hilbert_envelope(self):
        """Test envelope extraction using Hilbert transform."""
        # Create amplitude modulated signal
        sfreq = 1000
        duration = 1
        t = np.linspace(0, duration, sfreq * duration)

        carrier_freq = 100  # Hz
        mod_freq = 5  # Hz

        # AM signal: (1 + 0.5*cos(2*pi*5*t)) * sin(2*pi*100*t)
        modulation = 1 + 0.5 * np.cos(2 * np.pi * mod_freq * t)
        sig = modulation * np.sin(2 * np.pi * carrier_freq * t)

        # Get envelope using Hilbert
        analytic = scitex.dsp.hilbert(sig)
        envelope = np.abs(analytic)

        # Envelope should match modulation
        # (allowing for edge effects)
        assert np.corrcoef(envelope[100:-100], modulation[100:-100])[0, 1] > 0.99


class TestTimeFrequencyAnalysis:
    """Test time-frequency analysis functions."""

    def test_wavelet_basic(self):
        """Test basic wavelet transform."""
        # Create signal with time-varying frequency
        sfreq = 1000
        duration = 2
        t = np.linspace(0, duration, sfreq * duration)

        # Chirp signal (frequency increases from 10 to 50 Hz)
        sig = signal.chirp(t, 10, duration, 50)

        # Apply wavelet transform
        freqs_wavelet = np.logspace(np.log10(5), np.log10(100), 50)
        tfr = scitex.dsp.wavelet(sig, sfreq, freqs_wavelet)

        # Check output shape
        assert tfr.shape == (len(freqs_wavelet), len(sig))

        # Check it's complex
        assert np.iscomplexobj(tfr)

        # Power should be concentrated along the chirp trajectory
        power = np.abs(tfr) ** 2

        # At beginning, power should be concentrated at low frequencies
        t_start = int(0.1 * sfreq)
        power_start = power[:, t_start]
        peak_freq_idx_start = np.argmax(power_start)
        assert freqs_wavelet[peak_freq_idx_start] < 20  # Should be around 10Hz

        # At end, power should be concentrated at high frequencies
        t_end = int(1.9 * sfreq)
        power_end = power[:, t_end]
        peak_freq_idx_end = np.argmax(power_end)
        assert freqs_wavelet[peak_freq_idx_end] > 40  # Should be around 50Hz


class TestPAC:
    """Test Phase-Amplitude Coupling functions."""

    def test_pac_basic(self):
        """Test basic PAC computation."""
        # Create synthetic signal with PAC
        sfreq = 1000
        duration = 5
        t = np.linspace(0, duration, sfreq * duration)

        # Low frequency phase signal (10 Hz)
        phase_freq = 10
        phase_sig = np.sin(2 * np.pi * phase_freq * t)

        # High frequency amplitude signal (50 Hz)
        amp_freq = 50
        # Modulate amplitude with phase
        amplitude = 1 + 0.5 * np.sin(2 * np.pi * phase_freq * t)
        amp_sig = amplitude * np.sin(2 * np.pi * amp_freq * t)

        # Combine signals
        sig = phase_sig + amp_sig

        # Compute PAC - pac function has different signature
        pac_value = scitex.dsp.pac(
            sig,
            sfreq,
            pha_start_hz=8,
            pha_end_hz=12,
            amp_start_hz=45,
            amp_end_hz=55,
            pha_n_bands=10,
            amp_n_bands=10,
        )

        # PAC should be significant
        assert pac_value > 0
        assert pac_value < 1  # Normalized PAC

        # Test with no coupling
        sig_no_pac = phase_sig + np.sin(2 * np.pi * amp_freq * t)
        pac_no_coupling = scitex.dsp.pac(
            sig_no_pac,
            sfreq,
            pha_start_hz=8,
            pha_end_hz=12,
            amp_start_hz=45,
            amp_end_hz=55,
            pha_n_bands=10,
            amp_n_bands=10,
        )

        # PAC should be lower without coupling
        assert pac_no_coupling < pac_value


class TestSignalProcessingUtils:
    """Test signal processing utility functions."""

    def test_resample(self):
        """Test signal resampling."""
        # Create signal
        sfreq_orig = 1000
        duration = 1
        t_orig = np.linspace(0, duration, sfreq_orig * duration)
        sig_orig = np.sin(2 * np.pi * 10 * t_orig)

        # Resample to 500 Hz
        sfreq_new = 500
        sig_resampled = scitex.dsp.resample(sig_orig, sfreq_orig, sfreq_new)

        # Check length
        expected_length = int(len(sig_orig) * sfreq_new / sfreq_orig)
        assert len(sig_resampled) == expected_length

        # Check signal preserved (roughly)
        t_new = np.linspace(0, duration, len(sig_resampled))
        sig_expected = np.sin(2 * np.pi * 10 * t_new)

        # Allow for some resampling error
        assert np.corrcoef(sig_resampled, sig_expected)[0, 1] > 0.99

    def test_crop(self):
        """Test signal cropping."""
        # Create signal
        sfreq = 1000
        duration = 5
        sig = np.random.randn(sfreq * duration)

        # Crop from 1 to 3 seconds
        cropped = scitex.dsp.crop(sig, sfreq, 1.0, 3.0)

        # Check length
        expected_length = int(2.0 * sfreq)
        assert len(cropped) == expected_length

        # Check content matches
        start_idx = int(1.0 * sfreq)
        end_idx = int(3.0 * sfreq)
        np.testing.assert_array_equal(cropped, sig[start_idx:end_idx])

    def test_ensure_3d(self):
        """Test ensure_3d function."""
        # Test 1D -> 3D
        sig_1d = np.random.randn(100)
        sig_3d = scitex.dsp.ensure_3d(sig_1d)
        assert sig_3d.shape == (1, 1, 100)

        # Test 2D -> 3D
        sig_2d = np.random.randn(5, 100)
        sig_3d = scitex.dsp.ensure_3d(sig_2d)
        assert sig_3d.shape == (1, 5, 100)

        # Test 3D unchanged
        sig_3d_orig = np.random.randn(2, 5, 100)
        sig_3d = scitex.dsp.ensure_3d(sig_3d_orig)
        assert sig_3d.shape == sig_3d_orig.shape
        np.testing.assert_array_equal(sig_3d, sig_3d_orig)


class TestNormalization:
    """Test normalization functions."""

    def test_norm_zscore(self):
        """Test z-score normalization."""
        # Create signal with known mean and std
        sig = np.random.randn(1000) * 5 + 10

        # Apply z-score normalization
        normed = scitex.dsp.norm.z(sig)

        # Check mean is ~0 and std is ~1
        assert np.abs(np.mean(normed)) < 0.01
        assert np.abs(np.std(normed) - 1) < 0.01

    def test_norm_minmax(self):
        """Test min-max normalization."""
        # Create signal
        sig = np.random.randn(1000) * 5 + 10

        # Apply min-max normalization
        normed = scitex.dsp.norm.minmax(sig)

        # Check range is [0, 1]
        assert np.min(normed) >= 0
        assert np.max(normed) <= 1
        assert np.abs(np.min(normed) - 0) < 1e-10
        assert np.abs(np.max(normed) - 1) < 1e-10


class TestNoiseAddition:
    """Test noise addition functions."""

    def test_add_white_noise(self):
        """Test adding white noise."""
        # Create clean signal
        sig = np.sin(2 * np.pi * 10 * np.linspace(0, 1, 1000))

        # Add white noise with amplitude
        amp = 0.1
        noisy = scitex.dsp.add_noise.white(sig, amp=amp)

        # Check shape preserved
        assert noisy.shape == sig.shape

        # Check signal is modified
        assert not np.array_equal(sig, noisy)

        # Check SNR is approximately correct
        signal_power = np.mean(sig**2)
        noise_power = np.mean((noisy - sig) ** 2)
        actual_snr_db = 10 * np.log10(signal_power / noise_power)

        # Allow some tolerance
        assert np.abs(actual_snr_db - snr_db) < 1.0


class TestRippleDetection:
    """Test ripple detection functionality."""

    def test_detect_ripples(self):
        """Test ripple detection on synthetic data."""
        # Create signal with synthetic ripple
        sfreq = 1000
        duration = 10
        t = np.linspace(0, duration, sfreq * duration)

        # Background signal
        sig = np.random.randn(len(t)) * 0.5

        # Add ripple (150 Hz burst from 5 to 5.1 seconds)
        ripple_start = 5.0
        ripple_end = 5.1
        ripple_mask = (t >= ripple_start) & (t <= ripple_end)
        sig[ripple_mask] += 3 * np.sin(2 * np.pi * 150 * t[ripple_mask])

        # Detect ripples - requires low_hz and high_hz parameters
        ripples = scitex.dsp.detect_ripples(sig, sfreq, low_hz=100, high_hz=200)

        # Should detect at least one ripple
        assert len(ripples) >= 1

        # Check if detected ripple overlaps with true ripple
        detected = False
        for ripple in ripples:
            if (
                ripple["start"] <= ripple_start <= ripple["end"]
                or ripple["start"] <= ripple_end <= ripple["end"]
            ):
                detected = True
                break

        assert detected


class TestModulationIndex:
    """Test modulation index computation."""

    def test_modulation_index(self):
        """Test modulation index calculation."""
        # Create signal with known modulation
        sfreq = 1000
        duration = 5
        t = np.linspace(0, duration, sfreq * duration)

        # Carrier (40 Hz) with amplitude modulation (5 Hz)
        carrier_freq = 40
        mod_freq = 5
        mod_depth = 0.5  # 50% modulation

        amplitude = 1 + mod_depth * np.sin(2 * np.pi * mod_freq * t)
        sig = amplitude * np.sin(2 * np.pi * carrier_freq * t)

        # Compute modulation index - check actual signature
        mi = scitex.dsp.modulation_index(sig, sfreq, f_phase=(3, 7), f_amp=(35, 45))

        # MI should be significant
        assert mi > 0

        # Test with unmodulated signal
        sig_unmod = np.sin(2 * np.pi * carrier_freq * t)
        mi_unmod = scitex.dsp.modulation_index(
            sig_unmod, sfreq, f_phase=(3, 7), f_amp=(35, 45)
        )

        # MI should be much lower
        assert mi_unmod < mi / 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
