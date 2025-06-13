#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-07 13:42:15 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/dsp/test__resample.py

import pytest
import numpy as np
import torch
from scitex.dsp import resample


class TestResample:
    """Test cases for signal resampling functionality."""

    def test_import(self):
        """Test that resample can be imported."""
        assert callable(resample)

    def test_resample_upsample_numpy(self):
        """Test upsampling with numpy array."""
        # Create test signal
        src_fs = 100
        tgt_fs = 200
        t = np.linspace(0, 1, src_fs)
        x = np.sin(2 * np.pi * 5 * t).reshape(1, 1, -1).astype(np.float32)

        xr = resample(x, src_fs, tgt_fs)

        assert isinstance(xr, np.ndarray)
        assert xr.shape[-1] == x.shape[-1] * 2  # Double the samples
        assert xr.shape[:-1] == x.shape[:-1]  # Other dimensions unchanged

    def test_resample_downsample_numpy(self):
        """Test downsampling with numpy array."""
        src_fs = 200
        tgt_fs = 100
        t = np.linspace(0, 1, src_fs)
        x = np.sin(2 * np.pi * 5 * t).reshape(1, 1, -1).astype(np.float32)

        xr = resample(x, src_fs, tgt_fs)

        assert xr.shape[-1] == x.shape[-1] // 2  # Half the samples
        assert xr.shape[:-1] == x.shape[:-1]

    def test_resample_upsample_torch(self):
        """Test upsampling with torch tensor."""
        src_fs = 100
        tgt_fs = 300
        t = torch.linspace(0, 1, src_fs)
        x = torch.sin(2 * torch.pi * 5 * t).reshape(1, 1, -1)

        xr = resample(x, src_fs, tgt_fs)

        assert isinstance(xr, torch.Tensor)
        assert xr.shape[-1] == x.shape[-1] * 3

    def test_resample_with_time_vector(self):
        """Test resampling with time vector output."""
        src_fs = 128
        tgt_fs = 256
        t = np.linspace(0, 2, 2 * src_fs)
        x = np.random.randn(1, 1, len(t)).astype(np.float32)

        xr, tr = resample(x, src_fs, tgt_fs, t=t)

        assert len(tr) == xr.shape[-1]
        assert abs(tr[0] - t[0]) < 1e-6  # Same start time
        assert abs(tr[-1] - t[-1]) < 1e-6  # Same end time

    def test_resample_multi_channel(self):
        """Test resampling with multiple channels."""
        src_fs = 100
        tgt_fs = 150
        n_channels = 4
        n_samples = 200
        x = np.random.randn(1, n_channels, n_samples).astype(np.float32)

        xr = resample(x, src_fs, tgt_fs)

        assert xr.shape[0] == 1
        assert xr.shape[1] == n_channels
        assert xr.shape[2] == int(n_samples * tgt_fs / src_fs)

    def test_resample_batch_processing(self):
        """Test resampling with batch processing."""
        src_fs = 100
        tgt_fs = 200
        batch_size = 3
        n_samples = 100
        x = np.random.randn(batch_size, 2, n_samples).astype(np.float32)

        xr = resample(x, src_fs, tgt_fs)

        assert xr.shape[0] == batch_size
        assert xr.shape[1] == 2
        assert xr.shape[2] == n_samples * 2

    def test_resample_preserves_frequency_content(self):
        """Test that resampling preserves frequency content."""
        src_fs = 256
        tgt_fs = 512
        freq = 10  # Hz - well below Nyquist for both rates
        t = np.linspace(0, 2, 2 * src_fs)
        x = np.sin(2 * np.pi * freq * t).reshape(1, 1, -1).astype(np.float32)

        xr = resample(x, src_fs, tgt_fs)

        # Check that signal still oscillates at same frequency
        # Count zero crossings
        orig_crossings = np.sum(np.diff(np.sign(x[0, 0])) != 0)
        resamp_crossings = np.sum(np.diff(np.sign(xr[0, 0])) != 0)

        # Should have approximately same number of cycles
        assert abs(orig_crossings - resamp_crossings) < 5

    def test_resample_no_change_same_fs(self):
        """Test resampling with same source and target fs."""
        fs = 100
        n_samples = 200
        x = np.random.randn(1, 1, n_samples).astype(np.float32)

        xr = resample(x, fs, fs)

        assert xr.shape == x.shape
        np.testing.assert_allclose(xr, x, rtol=1e-5)

    def test_resample_dtype_preservation(self):
        """Test that resampling preserves data types."""
        src_fs = 100
        tgt_fs = 200

        # Test float32
        x_f32 = torch.randn(1, 1, 100, dtype=torch.float32)
        xr_f32 = resample(x_f32, src_fs, tgt_fs)
        assert xr_f32.dtype == torch.float32

        # Test float64
        x_f64 = torch.randn(1, 1, 100, dtype=torch.float64)
        xr_f64 = resample(x_f64, src_fs, tgt_fs)
        assert xr_f64.dtype == torch.float64

    def test_resample_device_preservation(self):
        """Test that resampling preserves device placement."""
        if not torch.cuda.is_available():
            pytest.skip("CUDA not available")

        src_fs = 100
        tgt_fs = 200
        x = torch.randn(1, 1, 100).cuda()

        xr = resample(x, src_fs, tgt_fs)

        assert xr.is_cuda
        assert xr.device == x.device

    def test_resample_extreme_ratios(self):
        """Test resampling with extreme ratios."""
        # Large upsampling ratio
        x = np.random.randn(1, 1, 10).astype(np.float32)
        xr = resample(x, 10, 100)  # 10x upsampling
        assert xr.shape[-1] == 100

        # Large downsampling ratio
        x = np.random.randn(1, 1, 1000).astype(np.float32)
        xr = resample(x, 1000, 100)  # 10x downsampling
        assert xr.shape[-1] == 100

    def test_resample_empty_signal_raises(self):
        """Test that empty signal raises error."""
        x = np.array([]).reshape(1, 1, 0)

        with pytest.raises(Exception):
            resample(x, 100, 200)

    def test_resample_non_integer_ratio(self):
        """Test resampling with non-integer ratio."""
        src_fs = 100
        tgt_fs = 150  # 1.5x ratio
        n_samples = 100
        x = np.random.randn(1, 1, n_samples).astype(np.float32)

        xr = resample(x, src_fs, tgt_fs)

        expected_samples = int(n_samples * tgt_fs / src_fs)
        assert xr.shape[-1] == expected_samples

    def test_resample_time_vector_torch(self):
        """Test resampling with time vector for torch tensors."""
        src_fs = 100
        tgt_fs = 200
        t = torch.linspace(0, 1, src_fs)
        x = torch.randn(1, 1, src_fs)

        xr, tr = resample(x, src_fs, tgt_fs, t=t)

        assert isinstance(tr, torch.Tensor)
        assert len(tr) == xr.shape[-1]
        assert torch.allclose(tr[0], t[0])
        assert torch.allclose(tr[-1], t[-1])

    def test_resample_aliasing_prevention(self):
        """Test that downsampling includes anti-aliasing."""
        src_fs = 1000
        tgt_fs = 100

        # Create signal with high frequency content that would alias
        t = np.linspace(0, 1, src_fs)
        high_freq = 400  # Hz - above Nyquist for target rate
        low_freq = 10  # Hz - below Nyquist for target rate

        x_high = np.sin(2 * np.pi * high_freq * t).reshape(1, 1, -1).astype(np.float32)
        x_low = np.sin(2 * np.pi * low_freq * t).reshape(1, 1, -1).astype(np.float32)

        xr_high = resample(x_high, src_fs, tgt_fs)
        xr_low = resample(x_low, src_fs, tgt_fs)

        # High frequency content should be attenuated more than low frequency
        high_energy = np.sum(xr_high**2)
        low_energy = np.sum(xr_low**2)

        # Low frequency should retain more energy
        assert low_energy > high_energy * 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
