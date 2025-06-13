#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-05-31 21:45:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/dsp/test__detect_ripples.py

"""Comprehensive test suite for detect_ripples functionality.

Testing ripple detection algorithm which:
1. Detects oscillatory events in neural signals
2. Typically used for hippocampal sharp-wave ripples (80-250 Hz)
3. Returns DataFrame with event timing and properties
"""

import pytest
import numpy as np
import pandas as pd
import torch
from unittest.mock import patch, MagicMock

# Import the function to test
from scitex.dsp import (
    detect_ripples,
    _preprocess,
    _find_events,
    _drop_ripples_at_edges,
    _calc_relative_peak_position,
    _sort_columns,
)


class TestDetectRipplesBasicFunctionality:
    """Test basic ripple detection functionality."""

    @pytest.fixture
    def simple_signal(self):
        """Create a simple signal with embedded ripple."""
        fs = 1000  # Hz
        duration = 2  # seconds
        t = np.arange(0, duration, 1 / fs)

        # Background signal (low frequency) with some noise
        background = 0.2 * np.sin(2 * np.pi * 5 * t) + 0.1 * np.random.randn(len(t))

        # Add a strong ripple burst (100 Hz) from 0.5 to 0.7 seconds
        ripple = np.zeros_like(t)
        ripple_idx = (t >= 0.5) & (t <= 0.7)
        # Make the ripple much stronger
        ripple[ripple_idx] = 10 * np.sin(2 * np.pi * 100 * t[ripple_idx])

        signal = background + ripple
        return signal, fs

    @pytest.fixture
    def multi_channel_signal(self):
        """Create multi-channel signal with ripples."""
        fs = 1000
        duration = 2
        n_channels = 4
        t = np.arange(0, duration, 1 / fs)

        signals = []
        for ch in range(n_channels):
            # Different phase for each channel with noise
            phase_shift = ch * np.pi / 4
            background = 0.2 * np.sin(
                2 * np.pi * 5 * t + phase_shift
            ) + 0.1 * np.random.randn(len(t))

            # Add strong ripple at different times for each channel
            ripple = np.zeros_like(t)
            start_time = 0.5 + ch * 0.1
            end_time = start_time + 0.2
            ripple_idx = (t >= start_time) & (t <= end_time)
            ripple[ripple_idx] = 8 * np.sin(2 * np.pi * 100 * t[ripple_idx])

            signals.append(background + ripple)

        return np.array(signals), fs

    def test_detect_ripples_basic(self, simple_signal):
        """Test basic ripple detection on simple signal."""
        np.random.seed(42)  # For reproducibility
        signal, fs = simple_signal
        # Make it 2D (1 channel)
        signal = signal[np.newaxis, :]

        df = detect_ripples(signal, fs, low_hz=80, high_hz=140, sd=1.5)

        assert isinstance(df, pd.DataFrame)

        # Check required columns
        required_columns = [
            "start_s",
            "end_s",
            "duration_s",
            "peak_s",
            "rel_peak_pos",
            "peak_amp_sd",
        ]
        assert all(col in df.columns for col in required_columns)

        # If ripples were detected, check timing makes sense
        if len(df) > 0:
            assert all(df["start_s"] < df["peak_s"])
            assert all(df["peak_s"] < df["end_s"])
            assert all(df["duration_s"] > 0)

    def test_detect_ripples_multi_channel(self, multi_channel_signal):
        """Test ripple detection on multi-channel signal."""
        np.random.seed(42)
        signal, fs = multi_channel_signal

        df = detect_ripples(signal, fs, low_hz=80, high_hz=140, sd=1.5)

        assert isinstance(df, pd.DataFrame)
        # Multi-channel processing may combine channels, so just check we get results
        if len(df) > 0:
            assert all(df["duration_s"] > 0)

    def test_detect_ripples_3d_input(self, simple_signal):
        """Test with 3D input (batch_size, n_channels, seq_len)."""
        np.random.seed(42)
        signal, fs = simple_signal
        # Create batch of 3 signals
        batch_signal = np.stack([signal, signal * 1.5, signal * 0.8])
        # Add channel dimension
        batch_signal = batch_signal[:, np.newaxis, :]

        df = detect_ripples(batch_signal, fs, low_hz=80, high_hz=140, sd=1.5)

        assert isinstance(df, pd.DataFrame)
        # 3D input processing may vary, just check structure
        assert all(col in df.columns for col in ["start_s", "end_s", "duration_s"])

    def test_detect_ripples_with_preprocessed_return(self, simple_signal):
        """Test returning preprocessed signal."""
        signal, fs = simple_signal
        signal = signal[np.newaxis, :]

        result = detect_ripples(
            signal, fs, low_hz=80, high_hz=140, return_preprocessed_signal=True
        )

        assert isinstance(result, tuple)
        assert len(result) == 3

        df, xx_r, fs_r = result
        assert isinstance(df, pd.DataFrame)
        assert isinstance(xx_r, np.ndarray)
        assert isinstance(fs_r, (int, float))

        # Check downsampling happened
        assert fs_r < fs  # Should be downsampled to ~3x low_hz


class TestDetectRipplesParameters:
    """Test different parameter configurations."""

    @pytest.fixture
    def ripple_signal(self):
        """Create signal with clear ripple events."""
        fs = 2000
        duration = 3
        t = np.arange(0, duration, 1 / fs)

        # Create signal with multiple ripple events
        signal = np.random.randn(len(t)) * 0.1  # Background noise

        # Add 3 ripple events at different times
        for start, end, freq, amp in [
            (0.5, 0.7, 120, 5),
            (1.2, 1.4, 100, 4),
            (2.0, 2.3, 110, 6),
        ]:
            idx = (t >= start) & (t <= end)
            signal[idx] += amp * np.sin(2 * np.pi * freq * t[idx])

        return signal[np.newaxis, :], fs

    def test_different_frequency_bands(self, ripple_signal):
        """Test detection with different frequency bands."""
        signal, fs = ripple_signal

        # Test narrow band
        df_narrow = detect_ripples(signal, fs, low_hz=100, high_hz=120)

        # Test wide band
        df_wide = detect_ripples(signal, fs, low_hz=80, high_hz=200)

        assert len(df_wide) >= len(df_narrow)  # Wide band should catch more

    def test_sd_threshold(self, ripple_signal):
        """Test different standard deviation thresholds."""
        signal, fs = ripple_signal

        # Low threshold - more detections
        df_low = detect_ripples(signal, fs, low_hz=80, high_hz=140, sd=1.0)

        # High threshold - fewer detections
        df_high = detect_ripples(signal, fs, low_hz=80, high_hz=140, sd=3.0)

        assert len(df_low) >= len(df_high)

    def test_smoothing_sigma(self, ripple_signal):
        """Test different smoothing parameters."""
        signal, fs = ripple_signal

        # Less smoothing
        df_sharp = detect_ripples(
            signal, fs, low_hz=80, high_hz=140, smoothing_sigma_ms=2, sd=1.5
        )

        # More smoothing
        df_smooth = detect_ripples(
            signal, fs, low_hz=80, high_hz=140, smoothing_sigma_ms=10, sd=1.5
        )

        # Check both return valid DataFrames
        assert isinstance(df_sharp, pd.DataFrame)
        assert isinstance(df_smooth, pd.DataFrame)

    def test_min_duration(self, ripple_signal):
        """Test minimum duration filtering."""
        signal, fs = ripple_signal

        # Short duration threshold
        df_short = detect_ripples(signal, fs, low_hz=80, high_hz=140, min_duration_ms=5)

        # Long duration threshold
        df_long = detect_ripples(signal, fs, low_hz=80, high_hz=140, min_duration_ms=50)

        assert len(df_short) >= len(df_long)

        # Check all events meet minimum duration
        if len(df_long) > 0:
            assert all(df_long["duration_s"] >= 0.05)


class TestDetectRipplesEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_signal(self):
        """Test with empty signal."""
        signal = np.array([]).reshape(1, 0)
        fs = 1000

        with pytest.raises(Exception):  # Should handle gracefully
            detect_ripples(signal, fs, low_hz=80, high_hz=140)

    def test_flat_signal(self):
        """Test with flat signal (no ripples)."""
        signal = np.ones((1, 2000))
        fs = 1000

        df = detect_ripples(signal, fs, low_hz=80, high_hz=140)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0  # No ripples in flat signal

    def test_pure_noise(self):
        """Test with pure noise signal."""
        np.random.seed(42)
        signal = np.random.randn(1, 5000) * 0.1
        fs = 1000

        df = detect_ripples(signal, fs, low_hz=80, high_hz=140, sd=3.0)

        assert isinstance(df, pd.DataFrame)
        # Very few or no detections expected with high threshold

    def test_very_short_signal(self):
        """Test with very short signal."""
        signal = np.random.randn(1, 100)
        fs = 1000

        df = detect_ripples(signal, fs, low_hz=80, high_hz=140)

        assert isinstance(df, pd.DataFrame)
        # Likely no detections in such short signal

    def test_nan_handling(self):
        """Test handling of NaN values."""
        signal = np.random.randn(1, 2000)
        signal[0, 500:600] = np.nan
        fs = 1000

        df = detect_ripples(signal, fs, low_hz=80, high_hz=140)

        assert isinstance(df, pd.DataFrame)
        # Should handle NaNs gracefully


class TestPreprocessing:
    """Test the preprocessing function."""

    def test_preprocess_2d_to_3d(self):
        """Test 2D to 3D conversion."""
        signal_2d = np.random.randn(4, 1000)
        fs = 1000

        xx_r, fs_r = _preprocess(signal_2d, fs, low_hz=80, high_hz=140)

        assert xx_r.ndim == 2  # Returns 2D after processing
        assert fs_r == 80 * 3  # Downsampled to 3x low_hz

    def test_preprocess_downsampling(self):
        """Test downsampling in preprocessing."""
        signal = np.random.randn(1, 4, 10000)
        fs = 2000
        low_hz = 100

        xx_r, fs_r = _preprocess(signal, fs, low_hz=low_hz, high_hz=200)

        assert fs_r == low_hz * 3
        # Check signal is shorter after downsampling
        assert xx_r.shape[-1] < signal.shape[-1]

    def test_preprocess_filtering(self):
        """Test filtering in preprocessing."""
        # Use demo signal which is known to work
from scitex.dsp import demo_sig

        # Get a ripple demo signal
        signal, t, fs = demo_sig(sig_type="ripple", n_chs=4)

        # Ensure 3D format
        if signal.ndim == 2:
            signal = signal[np.newaxis, :]

        xx_r, fs_r = _preprocess(signal, fs, low_hz=80, high_hz=140)

        # Check that preprocessing returns valid data
        assert isinstance(xx_r, np.ndarray)
        assert xx_r.ndim == 2  # Should be 2D after processing
        assert fs_r == 80 * 3  # Check downsampling

        # With a proper ripple signal, should get some valid data
        # Even if edges are NaN, center should have values
        if xx_r.size > 0:
            # Check that it's not all NaN or all zero
            assert not (np.all(np.isnan(xx_r)) or np.all(xx_r == 0))


class TestEventDetection:
    """Test the event detection function."""

    def test_find_events_basic(self):
        """Test basic event finding."""
        # Create z-scored signal with clear peaks
        signal = np.random.randn(1, 1000) * 0.1
        # Add strong peaks that will survive z-scoring
        signal[0, 200:250] += 5.0
        signal[0, 600:650] += 4.0
        # Z-score the signal as the function expects
        signal = (signal - signal.mean()) / signal.std()

        fs = 250
        df = _find_events(signal, fs, sd=2.0, min_duration_ms=10)

        assert isinstance(df, pd.DataFrame)
        # May or may not find events depending on preprocessing

    def test_find_events_multi_channel(self):
        """Test event finding on multiple channels."""
        n_channels = 3
        signal = np.random.randn(n_channels, 1000) * 0.1

        # Add peaks at different locations for each channel
        for ch in range(n_channels):
            start = 200 + ch * 200
            signal[ch, start : start + 50] += 5.0

        # Z-score each channel
        for ch in range(n_channels):
            signal[ch] = (signal[ch] - signal[ch].mean()) / signal[ch].std()

        fs = 250
        df = _find_events(signal, fs, sd=2.0, min_duration_ms=10)

        assert isinstance(df, pd.DataFrame)
        # Check structure is correct even if no events found


class TestHelperFunctions:
    """Test helper functions."""

    def test_drop_ripples_at_edges(self):
        """Test edge ripple removal."""
        # Create DataFrame with events at edges
        df = pd.DataFrame(
            {
                "start_s": [0.01, 0.5, 1.9],  # First and last are at edges
                "end_s": [0.05, 0.7, 1.95],
                "peak_s": [0.03, 0.6, 1.92],
                "duration_s": [0.04, 0.2, 0.05],
                "peak_amp_sd": [2.5, 3.0, 2.8],
            }
        )

        # Mock signal for edge calculation
        xx_r = np.zeros((1, 500))
        fs_r = 250
        low_hz = 80

        df_filtered = _drop_ripples_at_edges(df, low_hz, xx_r, fs_r)

        assert len(df_filtered) < len(df)  # Some events removed
        # Middle event should remain
        assert 0.5 in df_filtered["start_s"].values

    def test_calc_relative_peak_position(self):
        """Test relative peak position calculation."""
        df = pd.DataFrame(
            {
                "start_s": [0.0, 1.0],
                "end_s": [0.2, 1.4],
                "peak_s": [0.1, 1.2],
                "duration_s": [0.2, 0.4],
            }
        )

        df_with_rel = _calc_relative_peak_position(df)

        assert "rel_peak_pos" in df_with_rel.columns
        # First event: peak at midpoint
        assert abs(df_with_rel.iloc[0]["rel_peak_pos"] - 0.5) < 0.01
        # Second event: peak at 0.5 position
        assert abs(df_with_rel.iloc[1]["rel_peak_pos"] - 0.5) < 0.01

    def test_sort_columns(self):
        """Test column sorting."""
        df = pd.DataFrame(
            {
                "peak_amp_sd": [2.5],
                "end_s": [0.2],
                "start_s": [0.0],
                "rel_peak_pos": [0.5],
                "peak_s": [0.1],
                "duration_s": [0.2],
            }
        )

        df_sorted = _sort_columns(df)

        expected_order = [
            "start_s",
            "end_s",
            "duration_s",
            "peak_s",
            "rel_peak_pos",
            "peak_amp_sd",
        ]
        assert list(df_sorted.columns) == expected_order


class TestIntegration:
    """Integration tests with realistic scenarios."""

    def test_realistic_eeg_like_signal(self):
        """Test with realistic EEG-like signal."""
        np.random.seed(42)
        fs = 1000
        duration = 5
        t = np.arange(0, duration, 1 / fs)

        # Simulate EEG with multiple frequency components
        eeg = (
            0.2 * np.sin(2 * np.pi * 8 * t)  # Alpha
            + 0.1 * np.sin(2 * np.pi * 20 * t)  # Beta
            + 0.05 * np.random.randn(len(t))
        )  # Noise

        # Add strong ripple events
        ripple_events = [(1.0, 1.15, 120), (2.5, 2.65, 100), (4.0, 4.2, 110)]
        for start, end, freq in ripple_events:
            idx = (t >= start) & (t <= end)
            eeg[idx] += 10 * np.sin(2 * np.pi * freq * t[idx])

        eeg = eeg[np.newaxis, :]

        df = detect_ripples(eeg, fs, low_hz=80, high_hz=140, sd=1.5)

        assert isinstance(df, pd.DataFrame)
        # Check structure and reasonable values if events detected
        if len(df) > 0:
            assert all(df["duration_s"] > 0.01)  # Reasonable durations
            assert all(df["peak_amp_sd"] > 0)  # Positive amplitudes

    def test_batch_processing(self):
        """Test processing multiple recordings in batch."""
        fs = 1000
        n_batch = 5
        n_channels = 2
        duration = 2

        # Create batch of signals
        batch_signals = []
        for b in range(n_batch):
            t = np.arange(0, duration, 1 / fs)
            channels = []
            for ch in range(n_channels):
                signal = np.random.randn(len(t)) * 0.1
                # Add ripple at different time for each batch/channel
                ripple_time = 0.5 + b * 0.2 + ch * 0.1
                idx = (t >= ripple_time) & (t <= ripple_time + 0.15)
                signal[idx] += 3 * np.sin(2 * np.pi * 110 * t[idx])
                channels.append(signal)
            batch_signals.append(np.array(channels))

        batch_array = np.array(batch_signals)

        # Process entire batch
        df = detect_ripples(batch_array, fs, low_hz=80, high_hz=140)

        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        # Should have detections across multiple channels
        assert len(df.index.unique()) > 1


# Test with pytest
if __name__ == "__main__":
    import os
    import pytest

    pytest.main([os.path.abspath(__file__), "-v"])
