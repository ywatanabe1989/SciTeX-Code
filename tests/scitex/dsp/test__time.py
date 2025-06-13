#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-07 13:52:48 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/dsp/test__time.py

import pytest
import numpy as np
from scitex.dsp import time


class TestTime:
    """Test cases for time array generation."""

    def test_import(self):
        """Test that time can be imported."""
        assert callable(time)

    def test_time_basic(self):
        """Test basic time array generation."""
        start_sec = 0
        end_sec = 1
        fs = 100

        t = time(start_sec, end_sec, fs)

        assert isinstance(t, np.ndarray)
        assert len(t) == (end_sec - start_sec) * fs
        assert t[0] == start_sec
        assert t[-1] == end_sec

    def test_time_non_zero_start(self):
        """Test time array with non-zero start."""
        start_sec = 5
        end_sec = 8
        fs = 100

        t = time(start_sec, end_sec, fs)

        assert len(t) == (end_sec - start_sec) * fs
        assert t[0] == start_sec
        assert t[-1] == end_sec

    def test_time_high_sampling_rate(self):
        """Test time array with high sampling rate."""
        start_sec = 0
        end_sec = 0.1  # 100ms
        fs = 10000  # 10 kHz

        t = time(start_sec, end_sec, fs)

        assert len(t) == int((end_sec - start_sec) * fs)
        assert abs(t[0] - start_sec) < 1e-9
        assert abs(t[-1] - end_sec) < 1e-9

    def test_time_fractional_duration(self):
        """Test time array with fractional duration."""
        start_sec = 0
        end_sec = 2.5
        fs = 100

        t = time(start_sec, end_sec, fs)

        expected_len = int((end_sec - start_sec) * fs)
        assert len(t) == expected_len

    def test_time_uniform_spacing(self):
        """Test that time points are uniformly spaced."""
        start_sec = 0
        end_sec = 1
        fs = 100

        t = time(start_sec, end_sec, fs)

        # Check uniform spacing
        dt = np.diff(t)
        expected_dt = 1.0 / fs
        np.testing.assert_allclose(dt, expected_dt, rtol=1e-9)

    def test_time_negative_start(self):
        """Test time array with negative start time."""
        start_sec = -2
        end_sec = 3
        fs = 100

        t = time(start_sec, end_sec, fs)

        assert len(t) == (end_sec - start_sec) * fs
        assert t[0] == start_sec
        assert t[-1] == end_sec

    def test_time_low_sampling_rate(self):
        """Test time array with low sampling rate."""
        start_sec = 0
        end_sec = 10
        fs = 1  # 1 Hz

        t = time(start_sec, end_sec, fs)

        assert len(t) == (end_sec - start_sec) * fs
        assert len(t) == 10

    def test_time_single_sample(self):
        """Test time array with single sample."""
        start_sec = 0
        end_sec = 1
        fs = 1

        t = time(start_sec, end_sec, fs)

        assert len(t) == 1
        # For single sample, could be either start or end
        assert t[0] >= start_sec and t[0] <= end_sec

    def test_time_precision(self):
        """Test precision of time array values."""
        start_sec = 0.0
        end_sec = 1.0
        fs = 1000

        t = time(start_sec, end_sec, fs)

        # Check that values are precise
        # Second sample should be exactly 1ms after first
        assert abs(t[1] - t[0] - 0.001) < 1e-12

    def test_time_zero_duration(self):
        """Test time array with zero duration."""
        start_sec = 5
        end_sec = 5
        fs = 100

        t = time(start_sec, end_sec, fs)

        # Should return empty array or single point
        assert len(t) <= 1
        if len(t) == 1:
            assert t[0] == start_sec

    def test_time_very_long_duration(self):
        """Test time array with very long duration."""
        start_sec = 0
        end_sec = 3600  # 1 hour
        fs = 1  # 1 Hz to keep array manageable

        t = time(start_sec, end_sec, fs)

        assert len(t) == 3600
        assert t[0] == start_sec
        assert t[-1] == end_sec

    def test_time_floating_point_consistency(self):
        """Test that floating point calculations are consistent."""
        start_sec = 0.0
        end_sec = 0.1
        fs = 44100  # Audio sampling rate

        t = time(start_sec, end_sec, fs)

        # Should have exactly the expected number of samples
        expected_samples = int((end_sec - start_sec) * fs)
        assert len(t) == expected_samples

        # Check endpoints
        assert abs(t[0] - start_sec) < 1e-9
        assert abs(t[-1] - end_sec) < 1e-9


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
