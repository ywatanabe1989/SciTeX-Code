#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-01 20:30:00 (ywatanabe)"
# File: ./tests/scitex/dsp/test__crop.py

"""
Test module for scitex.dsp.crop function.
"""

import pytest
import numpy as np
from numpy.testing import assert_array_equal, assert_allclose


class TestCrop:
    """Test class for crop function."""

    @pytest.fixture
    def simple_signal_1d(self):
        """Create a simple 1D signal."""
        return np.arange(100)

    @pytest.fixture
    def simple_signal_2d(self):
        """Create a simple 2D signal (channels x time)."""
        n_channels = 5
        n_samples = 100
        return np.arange(n_channels * n_samples).reshape(n_channels, n_samples)

    @pytest.fixture
    def time_vector(self):
        """Create a time vector."""
        fs = 100  # 100 Hz
        n_samples = 100
        return np.arange(n_samples) / fs

    def test_import(self):
        """Test that crop can be imported."""
        from scitex.dsp import crop

        assert callable(crop)

    def test_basic_crop_no_overlap(self, simple_signal_2d):
        """Test basic cropping without overlap."""
        from scitex.dsp import crop

        window_length = 20
        result = crop(simple_signal_2d, window_length, overlap_factor=0.0)

        # Should have 5 windows (100 / 20 = 5)
        assert result.shape[0] == 5  # 5 windows
        assert result.shape[1] == simple_signal_2d.shape[0]  # same channels
        assert result.shape[2] == window_length

        # Check first window
        assert_array_equal(result[0], simple_signal_2d[:, :window_length])

    def test_crop_with_50_percent_overlap(self, simple_signal_2d):
        """Test cropping with 50% overlap."""
        from scitex.dsp import crop

        window_length = 20
        result = crop(simple_signal_2d, window_length, overlap_factor=0.5)

        # With 50% overlap, step = 10, so (100-20)/10 + 1 = 9 windows
        assert result.shape[0] == 9

        # Check overlap: second window should start at position 10
        assert_array_equal(result[1], simple_signal_2d[:, 10:30])

    def test_crop_with_time_vector(self, simple_signal_2d, time_vector):
        """Test cropping with time vector."""
        from scitex.dsp import crop

        window_length = 20
        windows, times = crop(
            simple_signal_2d, window_length, overlap_factor=0.5, time=time_vector
        )

        # Check shapes
        assert windows.shape[0] == times.shape[0]  # Same number of windows
        assert times.shape[1] == window_length  # Each time window has correct length

        # Check time values
        assert_allclose(times[0], time_vector[:window_length])
        assert_allclose(times[1], time_vector[10:30])  # 50% overlap

    def test_crop_different_axis(self):
        """Test cropping along different axes."""
        from scitex.dsp import crop

        # Create 3D signal (trials x channels x time)
        signal_3d = np.arange(4 * 5 * 100).reshape(4, 5, 100)

        # Crop along last axis (default)
        result = crop(signal_3d, window_length=25, axis=-1)
        assert result.shape == (4, 4, 5, 25)  # 4 windows, original trials and channels

        # Crop along first axis
        result = crop(signal_3d[:50], window_length=10, axis=0)
        # This would move axis 0 to create windows
        assert result.shape[1] == 5  # 5 windows of length 10 from 50 samples

    def test_crop_with_various_overlaps(self, simple_signal_1d):
        """Test cropping with various overlap factors."""
        from scitex.dsp import crop

        window_length = 20

        # No overlap
        result = crop(simple_signal_1d, window_length, overlap_factor=0.0)
        assert result.shape[0] == 5  # 100/20 = 5

        # 25% overlap
        result = crop(simple_signal_1d, window_length, overlap_factor=0.25)
        step = int(20 * 0.75)  # 15
        expected_windows = (100 - 20) // step + 1
        assert result.shape[0] == expected_windows

        # 75% overlap
        result = crop(simple_signal_1d, window_length, overlap_factor=0.75)
        step = int(20 * 0.25)  # 5
        expected_windows = (100 - 20) // step + 1
        assert result.shape[0] == expected_windows

    def test_window_longer_than_signal(self):
        """Test when window length exceeds signal length."""
        from scitex.dsp import crop

        short_signal = np.arange(10)
        result = crop(short_signal, window_length=20)

        # Should return at least 1 window with available data
        assert result.shape[0] >= 1

    def test_invalid_axis(self, simple_signal_2d):
        """Test error handling for invalid axis."""
        from scitex.dsp import crop

        with pytest.raises(ValueError, match="Invalid axis"):
            crop(simple_signal_2d, window_length=20, axis=5)

    def test_time_vector_length_mismatch(self, simple_signal_2d):
        """Test error when time vector length doesn't match signal."""
        from scitex.dsp import crop

        wrong_time = np.arange(50)  # Wrong length

        with pytest.raises(ValueError, match="Length of time vector"):
            crop(simple_signal_2d, window_length=20, time=wrong_time)

    def test_negative_axis_indexing(self):
        """Test negative axis indexing."""
        from scitex.dsp import crop

        signal_3d = np.random.rand(3, 4, 50)

        # -1 should be equivalent to axis=2
        result1 = crop(signal_3d, window_length=10, axis=-1)
        result2 = crop(signal_3d, window_length=10, axis=2)
        assert_array_equal(result1, result2)

    def test_exact_fit_windows(self):
        """Test when signal length is exact multiple of window length."""
        from scitex.dsp import crop

        # Signal of length 100, window of 25 -> exactly 4 windows
        signal = np.arange(100)
        result = crop(signal, window_length=25, overlap_factor=0.0)

        assert result.shape[0] == 4
        assert_array_equal(result[0], signal[:25])
        assert_array_equal(result[-1], signal[75:])

    def test_multichannel_consistency(self):
        """Test that all channels are cropped consistently."""
        from scitex.dsp import crop

        n_channels = 8
        signal = np.random.rand(n_channels, 200)
        window_length = 50

        result = crop(signal, window_length, overlap_factor=0.5)

        # Check that each window maintains channel structure
        for i in range(result.shape[0]):
            for ch in range(n_channels):
                # Calculate expected start position
                start = i * 25  # 50% overlap means step of 25
                expected = signal[ch, start : start + window_length]
                assert_allclose(result[i, ch], expected)

    @pytest.mark.parametrize(
        "window_length,overlap,expected_windows",
        [
            (10, 0.0, 10),  # 100/10 = 10
            (20, 0.5, 9),  # (100-20)/10 + 1 = 9
            (25, 0.0, 4),  # 100/25 = 4
            (50, 0.5, 3),  # (100-50)/25 + 1 = 3
        ],
    )
    def test_window_calculations(self, window_length, overlap, expected_windows):
        """Test window count calculations with various parameters."""
        from scitex.dsp import crop

        signal = np.arange(100)
        result = crop(signal, window_length, overlap_factor=overlap)
        assert result.shape[0] == expected_windows

    def test_preserve_data_integrity(self, simple_signal_2d):
        """Test that cropping preserves data without modification."""
        from scitex.dsp import crop

        window_length = 30
        overlap = 0.5
        result = crop(simple_signal_2d, window_length, overlap_factor=overlap)

        # Verify random windows match original data
        n_windows = result.shape[0]
        for _ in range(5):  # Check 5 random windows
            i = np.random.randint(0, n_windows)
            start = int(i * window_length * (1 - overlap))
            end = start + window_length
            assert_array_equal(result[i], simple_signal_2d[:, start:end])


# --------------------------------------------------------------------------------

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/dsp/_crop.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "ywatanabe (2024-11-02 22:50:46)"
# # File: ./scitex_repo/src/scitex/dsp/_crop.py
# 
# import numpy as np
# 
# 
# def crop(sig_2d, window_length, overlap_factor=0.0, axis=-1, time=None):
#     """
#     Crops the input signal into overlapping windows of a specified length,
#     allowing for an arbitrary axis and considering a time vector.
# 
#     Parameters:
#     - sig_2d (numpy.ndarray): The input sig_2d array to be cropped. Can be multi-dimensional.
#     - window_length (int): The length of each window to crop the sig_2d into.
#     - overlap_factor (float): The fraction of the window that consecutive windows overlap. For example, an overlap_factor of 0.5 means 50% overlap.
#     - axis (int): The time axis along which to crop the sig_2d.
#         - time (numpy.ndarray): The time vector associated with the signal. Its length should match the signal's length along the cropping axis.
# 
#     Returns:
#     - cropped_windows (numpy.ndarray): The cropped signal windows. The shape depends on the input shape and the specified axis.
#     """
#     # Ensure axis is in a valid range
#     if axis < 0:
#         axis += sig_2d.ndim
#     if axis >= sig_2d.ndim or axis < 0:
#         raise ValueError("Invalid axis. Axis out of range for sig_2d dimensions.")
# 
#     if time is not None:
#         # Validate the length of the time vector against the signal's dimension
#         if sig_2d.shape[axis] != len(time):
#             raise ValueError(
#                 "Length of time vector does not match signal's dimension along the specified axis."
#             )
# 
#     # Move the target axis to the last position
#     axes = np.arange(sig_2d.ndim)
#     axes[axis], axes[-1] = axes[-1], axes[axis]
#     sig_2d_permuted = np.transpose(sig_2d, axes)
# 
#     # Compute the number of windows and the step size
#     seq_len = sig_2d_permuted.shape[-1]
#     step = int(window_length * (1 - overlap_factor))
#     n_windows = max(
#         1, ((seq_len - window_length) // step + 1)
#     )  # Ensure at least 1 window
# 
#     # Crop the sig_2d into windows
#     cropped_windows = []
#     cropped_times = []
#     for i in range(n_windows):
#         start = i * step
#         end = start + window_length
#         cropped_windows.append(sig_2d_permuted[..., start:end])
#         if time is not None:
#             cropped_times.append(time[start:end])
# 
#     # Convert list of windows back to numpy array
#     cropped_windows = np.array(cropped_windows)
#     cropped_times = np.array(cropped_times)
# 
#     # Move the last axis back to its original position if necessary
#     if axis != sig_2d.ndim - 1:
#         # Compute the inverse permutation
#         inv_axes = np.argsort(axes)
#         cropped_windows = np.transpose(cropped_windows, axes=inv_axes)
# 
#     if time is None:
#         return cropped_windows
#     else:
#         return cropped_windows, cropped_times
# 
# 
# def main():
#     import random
# 
#     FS = 128
#     N_CHS = 19
#     RECORD_S = 13
#     WINDOW_S = 2
#     FACTOR = 0.5
# 
#     # To pts
#     record_pts = int(RECORD_S * FS)
#     window_pts = int(WINDOW_S * FS)
# 
#     # Demo signal
#     sig2d = np.random.rand(N_CHS, record_pts)
#     time = np.arange(record_pts) / FS
# 
#     # Main
#     xx, tt = crop(sig2d, window_pts, overlap_factor=FACTOR, time=time)
# 
#     print(f"sig2d.shape: {sig2d.shape}")
#     print(f"xx.shape: {xx.shape}")
# 
#     # Validation
#     i_seg = random.randint(0, len(xx) - 1)
#     start = int(i_seg * window_pts * FACTOR)
#     end = start + window_pts
#     assert np.allclose(sig2d[:, start:end], xx[i_seg])
# 
# 
# if __name__ == "__main__":
#     # parser = argparse.ArgumentParser(description='')
#     # import argparse
#     # # Argument Parser
#     import sys
# 
#     import matplotlib.pyplot as plt
#     import scitex
# 
#     # parser.add_argument('--var', '-v', type=int, default=1, help='')
#     # parser.add_argument('--flag', '-f', action='store_true', default=False, help='')
#     # args = parser.parse_args()
#     # Main
#     CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.gen.start(sys, plt, verbose=False)
#     main()
#     scitex.gen.close(CONFIG, verbose=False, notify=False)
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/dsp/_crop.py
# --------------------------------------------------------------------------------
