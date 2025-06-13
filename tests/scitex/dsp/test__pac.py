#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-07 13:15:42 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/dsp/test__pac.py

import pytest
import numpy as np
import torch
import unittest.mock as mock
from scitex.dsp import pac


class TestPac:
    """Test cases for phase-amplitude coupling (PAC) calculation."""

    def test_import(self):
        """Test that pac can be imported."""
        assert callable(pac)

    def test_pac_basic_numpy(self):
        """Test basic PAC calculation with numpy array."""
        # Create test signal
        fs = 512
        t_sec = 2
        n_samples = int(fs * t_sec)
        x = np.random.randn(1, 2, n_samples).astype(np.float32)

        pac_values, pha_mids, amp_mids = pac(x, fs)

        assert isinstance(pac_values, np.ndarray)
        assert isinstance(pha_mids, np.ndarray)
        assert isinstance(amp_mids, np.ndarray)
        assert pac_values.shape == (1, 2, 100, 100)  # Default band counts
        assert len(pha_mids) == 100
        assert len(amp_mids) == 100
        assert np.all(pac_values >= 0)  # PAC values should be non-negative

    def test_pac_basic_torch(self):
        """Test basic PAC calculation with torch tensor."""
        fs = 512
        t_sec = 2
        n_samples = int(fs * t_sec)
        x = torch.randn(1, 2, n_samples)

        pac_values, pha_mids, amp_mids = pac(x, fs)

        assert isinstance(pac_values, torch.Tensor)
        assert pac_values.shape == (1, 2, 100, 100)
        assert torch.all(pac_values >= 0)

    def test_pac_custom_frequency_bands(self):
        """Test PAC with custom frequency band parameters."""
        fs = 512
        n_samples = 1024
        x = np.random.randn(1, 1, n_samples).astype(np.float32)

        pac_values, pha_mids, amp_mids = pac(
            x,
            fs,
            pha_start_hz=1,
            pha_end_hz=30,
            pha_n_bands=50,
            amp_start_hz=30,
            amp_end_hz=200,
            amp_n_bands=80,
        )

        assert pac_values.shape == (1, 1, 50, 80)
        assert len(pha_mids) == 50
        assert len(amp_mids) == 80
        assert pha_mids[0] >= 1
        assert pha_mids[-1] <= 30
        assert amp_mids[0] >= 30
        assert amp_mids[-1] <= 200

    def test_pac_batch_processing(self):
        """Test PAC with multiple batch samples."""
        fs = 256
        n_samples = 512
        batch_size = 4
        x = np.random.randn(batch_size, 3, n_samples).astype(np.float32)

        pac_values, _, _ = pac(x, fs, batch_size=batch_size)

        assert pac_values.shape[0] == batch_size
        assert pac_values.shape == (batch_size, 3, 100, 100)

    @pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
    def test_pac_cuda_device(self):
        """Test PAC calculation on CUDA device."""
        fs = 256
        n_samples = 512
        x = torch.randn(1, 2, n_samples)

        pac_values, _, _ = pac(x, fs, device="cuda")

        assert pac_values.is_cuda

    def test_pac_channel_batching(self):
        """Test PAC with channel batching."""
        fs = 256
        n_samples = 512
        n_chs = 16
        x = np.random.randn(1, n_chs, n_samples).astype(np.float32)

        # Process with channel batching
        pac_values, _, _ = pac(x, fs, batch_size_ch=4)

        assert pac_values.shape == (1, n_chs, 100, 100)

    def test_pac_fp16_processing(self):
        """Test PAC with fp16 (half precision) processing."""
        fs = 256
        n_samples = 512
        x = np.random.randn(1, 2, n_samples).astype(np.float32)

        pac_values, _, _ = pac(x, fs, fp16=True)

        assert pac_values.shape == (1, 2, 100, 100)
        assert np.all(np.isfinite(pac_values))

    def test_pac_trainable_mode(self):
        """Test PAC with trainable filter parameters."""
        fs = 256
        n_samples = 512
        x = np.random.randn(1, 2, n_samples).astype(np.float32)

        pac_values, _, _ = pac(x, fs, trainable=True)

        assert pac_values.shape == (1, 2, 100, 100)

    def test_pac_permutation_testing(self):
        """Test PAC with permutation testing."""
        fs = 256
        n_samples = 512
        x = np.random.randn(1, 1, n_samples).astype(np.float32)

        pac_values, _, _ = pac(x, fs, n_perm=10)

        assert pac_values.shape == (1, 1, 100, 100)

    def test_pac_amp_prob_mode(self):
        """Test PAC with amplitude probability mode."""
        fs = 256
        n_samples = 512
        x = np.random.randn(1, 2, n_samples).astype(np.float32)

        pac_values1, _, _ = pac(x, fs, amp_prob=False)
        pac_values2, _, _ = pac(x, fs, amp_prob=True)

        assert pac_values1.shape == pac_values2.shape
        # Results should be different with different amp_prob settings
        assert not np.allclose(pac_values1, pac_values2)

    def test_pac_single_channel(self):
        """Test PAC with single channel signal."""
        fs = 256
        n_samples = 512
        x = np.random.randn(1, 1, n_samples).astype(np.float32)

        pac_values, pha_mids, amp_mids = pac(x, fs)

        assert pac_values.shape == (1, 1, 100, 100)
        assert np.all(pac_values >= 0)

    def test_pac_frequency_ordering(self):
        """Test that frequency bands are properly ordered."""
        fs = 512
        n_samples = 1024
        x = np.random.randn(1, 1, n_samples).astype(np.float32)

        _, pha_mids, amp_mids = pac(x, fs)

        # Check frequencies are monotonically increasing
        assert np.all(np.diff(pha_mids) > 0)
        assert np.all(np.diff(amp_mids) > 0)

    def test_pac_empty_signal_raises(self):
        """Test that empty signal raises appropriate error."""
        fs = 256
        x = np.array([]).reshape(1, 1, 0)

        with pytest.raises(Exception):
            pac(x, fs)

    def test_pac_invalid_sampling_rate(self):
        """Test PAC with edge case sampling rates."""
        n_samples = 512
        x = np.random.randn(1, 1, n_samples).astype(np.float32)

        # Very low sampling rate should work but limit frequency bands
        pac_values, pha_mids, amp_mids = pac(
            x,
            fs=100,  # Low fs
            pha_end_hz=10,  # Must be less than Nyquist
            amp_end_hz=40,  # Must be less than Nyquist
        )

        assert np.all(pha_mids <= 10)
        assert np.all(amp_mids <= 40)

    def test_pac_multi_batch_multi_channel(self):
        """Test PAC with multiple batches and channels."""
        fs = 256
        n_samples = 512
        batch_size = 3
        n_chs = 5
        x = np.random.randn(batch_size, n_chs, n_samples).astype(np.float32)

        pac_values, _, _ = pac(x, fs)

        assert pac_values.shape == (batch_size, n_chs, 100, 100)

        # Each batch and channel should have unique PAC patterns
        for b in range(batch_size):
            for c in range(n_chs):
                assert np.any(pac_values[b, c] > 0)

    def test_pac_dtype_preservation(self):
        """Test that PAC preserves appropriate data types."""
        fs = 256
        n_samples = 512

        # Test with float32
        x_f32 = np.random.randn(1, 1, n_samples).astype(np.float32)
        pac_f32, _, _ = pac(x_f32, fs)
        assert pac_f32.dtype == np.float32

        # Test with float64
        x_f64 = np.random.randn(1, 1, n_samples).astype(np.float64)
        pac_f64, _, _ = pac(x_f64, fs)
        # Should be converted to float32 internally
        assert pac_f64.dtype in [np.float32, np.float64]

    def test_pac_deterministic_with_seed(self):
        """Test that PAC gives reproducible results with fixed random seed."""
        fs = 256
        n_samples = 512

        # Generate same signal twice
        np.random.seed(42)
        x1 = np.random.randn(1, 1, n_samples).astype(np.float32)
        np.random.seed(42)
        x2 = np.random.randn(1, 1, n_samples).astype(np.float32)

        pac1, _, _ = pac(x1, fs)
        pac2, _, _ = pac(x2, fs)

        np.testing.assert_allclose(pac1, pac2, rtol=1e-5)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
