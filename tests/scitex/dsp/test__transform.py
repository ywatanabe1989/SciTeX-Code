#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-07 14:08:32 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/dsp/test__transform.py

import pytest
import numpy as np
import pandas as pd
import torch
from scitex.dsp import to_sktime_df, to_segments


class TestTransform:
    """Test cases for signal transformation functions."""

    def test_import(self):
        """Test that functions can be imported."""
        assert callable(to_sktime_df)
        assert callable(to_segments)

    def test_to_sktime_df_basic(self):
        """Test basic conversion to sktime format."""
        # Create 3D array (n_samples, seq_len, n_channels)
        n_samples, seq_len, n_channels = 5, 100, 3
        arr = np.random.randn(n_samples, seq_len, n_channels)

        df = to_sktime_df(arr)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == n_samples
        assert list(df.columns) == ["dim_0"]

        # Check that each cell contains a Series
        for i in range(n_samples):
            cell_data = df.iloc[i, 0]
            assert isinstance(cell_data, pd.Series)
            assert len(cell_data) == n_channels
            assert all(f"channel_{j}" in cell_data.index for j in range(n_channels))

    def test_to_sktime_df_single_channel(self):
        """Test conversion with single channel."""
        n_samples, seq_len, n_channels = 3, 50, 1
        arr = np.random.randn(n_samples, seq_len, n_channels)

        df = to_sktime_df(arr)

        assert len(df) == n_samples
        for i in range(n_samples):
            cell_data = df.iloc[i, 0]
            assert "channel_0" in cell_data.index
            assert len(cell_data["channel_0"]) == seq_len

    def test_to_sktime_df_shape_validation(self):
        """Test that invalid shapes raise errors."""
        # 2D array should raise error
        arr_2d = np.random.randn(10, 20)
        with pytest.raises(ValueError, match="Input data must be a 3D array"):
            to_sktime_df(arr_2d)

        # 4D array should raise error
        arr_4d = np.random.randn(5, 10, 20, 3)
        with pytest.raises(ValueError, match="Input data must be a 3D array"):
            to_sktime_df(arr_4d)

    def test_to_sktime_df_data_preservation(self):
        """Test that data is preserved during conversion."""
        n_samples, seq_len, n_channels = 2, 10, 2
        arr = np.arange(n_samples * seq_len * n_channels).reshape(
            n_samples, seq_len, n_channels
        )

        df = to_sktime_df(arr)

        # Check that data is preserved
        for i in range(n_samples):
            cell_data = df.iloc[i, 0]
            for j in range(n_channels):
                channel_data = cell_data[f"channel_{j}"]
                expected_data = arr[i, :, j]
                np.testing.assert_array_equal(channel_data.values, expected_data)

    def test_to_segments_basic_numpy(self):
        """Test basic segmentation with numpy array."""
        # Create test signal
        signal_len = 1000
        window_size = 100
        x = np.random.randn(1, 2, signal_len).astype(np.float32)

        segments = to_segments(x, window_size)

        assert isinstance(segments, np.ndarray)
        # Check shape: original dims + segments + window_size
        expected_n_segments = (signal_len - window_size) + 1
        assert segments.shape == (1, 2, expected_n_segments, window_size)

    def test_to_segments_basic_torch(self):
        """Test basic segmentation with torch tensor."""
        signal_len = 500
        window_size = 50
        x = torch.randn(1, 3, signal_len)

        segments = to_segments(x, window_size)

        assert isinstance(segments, torch.Tensor)
        expected_n_segments = (signal_len - window_size) + 1
        assert segments.shape == (1, 3, expected_n_segments, window_size)

    def test_to_segments_overlap(self):
        """Test segmentation with overlap."""
        signal_len = 200
        window_size = 40
        overlap_factor = 2  # 50% overlap
        x = np.random.randn(1, 1, signal_len).astype(np.float32)

        segments = to_segments(x, window_size, overlap_factor=overlap_factor)

        stride = window_size // overlap_factor
        expected_n_segments = (signal_len - window_size) // stride + 1
        assert segments.shape[-2] == expected_n_segments
        assert segments.shape[-1] == window_size

    def test_to_segments_no_overlap(self):
        """Test segmentation without overlap."""
        signal_len = 300
        window_size = 50
        overlap_factor = 1  # No overlap
        x = np.random.randn(2, 4, signal_len).astype(np.float32)

        segments = to_segments(x, window_size, overlap_factor=overlap_factor)

        expected_n_segments = (signal_len - window_size) + 1
        assert segments.shape == (2, 4, expected_n_segments, window_size)

    def test_to_segments_different_dimensions(self):
        """Test segmentation along different dimensions."""
        # Test with dim=1
        x = np.random.randn(3, 100, 5).astype(np.float32)
        window_size = 20

        segments = to_segments(x, window_size, dim=1)

        expected_n_segments = (100 - window_size) + 1
        assert segments.shape == (3, expected_n_segments, 5, window_size)

    def test_to_segments_edge_case_exact_fit(self):
        """Test when signal length is exact multiple of window size."""
        signal_len = 100
        window_size = 100
        x = np.random.randn(1, 1, signal_len).astype(np.float32)

        segments = to_segments(x, window_size)

        # Should have exactly 1 segment
        assert segments.shape == (1, 1, 1, window_size)

    def test_to_segments_window_larger_than_signal(self):
        """Test when window size is larger than signal."""
        signal_len = 50
        window_size = 100
        x = np.random.randn(1, 1, signal_len).astype(np.float32)

        segments = to_segments(x, window_size)

        # Should have 0 segments
        assert segments.shape[-2] == 0

    def test_to_segments_dtype_preservation(self):
        """Test that data types are preserved."""
        signal_len = 200
        window_size = 50

        # Test float32
        x_f32 = torch.randn(1, 1, signal_len, dtype=torch.float32)
        segments_f32 = to_segments(x_f32, window_size)
        assert segments_f32.dtype == torch.float32

        # Test float64
        x_f64 = torch.randn(1, 1, signal_len, dtype=torch.float64)
        segments_f64 = to_segments(x_f64, window_size)
        assert segments_f64.dtype == torch.float64

    def test_to_segments_device_preservation(self):
        """Test that device placement is preserved."""
        if not torch.cuda.is_available():
            pytest.skip("CUDA not available")

        signal_len = 200
        window_size = 50
        x = torch.randn(1, 2, signal_len).cuda()

        segments = to_segments(x, window_size)

        assert segments.is_cuda
        assert segments.device == x.device

    def test_to_segments_content_verification(self):
        """Test that segment content is correct."""
        signal_len = 100
        window_size = 10
        # Create a simple pattern for easy verification
        x = np.arange(signal_len).reshape(1, 1, signal_len).astype(np.float32)

        segments = to_segments(x, window_size)

        # Check first few segments
        for i in range(min(5, segments.shape[2])):
            expected = np.arange(i, i + window_size)
            np.testing.assert_array_equal(segments[0, 0, i, :], expected)

    def test_to_segments_high_overlap(self):
        """Test segmentation with high overlap factor."""
        signal_len = 200
        window_size = 50
        overlap_factor = 10  # 90% overlap
        x = np.random.randn(1, 1, signal_len).astype(np.float32)

        segments = to_segments(x, window_size, overlap_factor=overlap_factor)

        stride = window_size // overlap_factor
        expected_n_segments = (signal_len - window_size) // stride + 1
        assert segments.shape[-2] == expected_n_segments

        # With high overlap, should have many segments
        assert segments.shape[-2] > signal_len // window_size

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/dsp/_transform.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-04-08 12:41:59 (ywatanabe)"#!/usr/bin/env python3
# 
# 
# import warnings
# 
# import numpy as np
# import pandas as pd
# import torch
# from ..decorators import torch_fn
# 
# 
# def to_sktime_df(arr):
#     """
#     Convert a 3D numpy array into a DataFrame suitable for sktime.
# 
#     Parameters:
#     arr (numpy.ndarray): A 3D numpy array with shape (n_samples, n_channels, seq_len)
# 
#     Returns:
#     pandas.DataFrame: A DataFrame in sktime format
#     """
#     if len(arr.shape) != 3:
#         raise ValueError("Input data must be a 3D array")
# 
#     n_samples, seq_len, n_channels = arr.shape
# 
#     # Initialize an empty DataFrame for sktime format
#     sktime_df = pd.DataFrame(index=range(n_samples), columns=["dim_0"])
# 
#     # Iterate over each sample
#     for i in range(n_samples):
#         # Combine all channels into a single cell
#         combined_series = pd.Series(
#             {f"channel_{j}": pd.Series(arr[i, :, j]) for j in range(n_channels)}
#         )
#         sktime_df.iloc[i, 0] = combined_series
# 
#     return sktime_df
# 
# 
# @torch_fn
# def to_segments(x, window_size, overlap_factor=1, dim=-1):
#     stride = window_size // overlap_factor
#     num_windows = (x.size(dim) - window_size) // stride + 1
#     windows = x.unfold(dim, window_size, stride)
#     return windows
# 
# 
# if __name__ == "__main__":
#     import scitex
# 
#     x, t, f = scitex.dsp.demo_sig()
# 
#     y = to_segments(x, 256)
# 
#     x = 100 * np.random.rand(16, 160, 1000)
#     print(_normalize_time(x))
# 
#     x = torch.randn(16, 160, 1000)
#     print(_normalize_time(x))
# 
#     x = torch.randn(16, 160, 1000).cuda()
#     print(_normalize_time(x))
# 
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/dsp/_transform.py
# --------------------------------------------------------------------------------
