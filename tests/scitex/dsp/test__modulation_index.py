#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-07 13:02:18 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/dsp/test__modulation_index.py

import pytest
import numpy as np
import torch
from scitex.dsp import modulation_index, _reshape


class TestModulationIndex:
    """Test cases for modulation index calculation."""

    def test_import(self):
        """Test that functions can be imported."""
        assert callable(modulation_index)
        assert callable(_reshape)

    def test_modulation_index_basic(self):
        """Test basic modulation index calculation."""
        # Create simple phase and amplitude data
        batch_size, n_chs, n_freqs, n_segments, seq_len = 2, 3, 4, 5, 100
        pha = np.random.uniform(
            -np.pi, np.pi, (batch_size, n_chs, n_freqs, n_segments, seq_len)
        )
        amp = np.random.uniform(0, 1, (batch_size, n_chs, n_freqs, n_segments, seq_len))

        result = modulation_index(pha, amp)

        assert isinstance(result, np.ndarray)
        assert result.shape == (batch_size, n_chs, n_freqs, n_freqs)
        assert np.all(result >= 0)  # MI should be non-negative

    def test_modulation_index_torch(self):
        """Test modulation index with torch tensors."""
        batch_size, n_chs, n_freqs, n_segments, seq_len = 2, 3, 4, 5, 100
        pha = (
            torch.rand(batch_size, n_chs, n_freqs, n_segments, seq_len) * 2 * np.pi
            - np.pi
        )
        amp = torch.rand(batch_size, n_chs, n_freqs, n_segments, seq_len)

        result = modulation_index(pha, amp)

        assert isinstance(result, torch.Tensor)
        assert result.shape == (batch_size, n_chs, n_freqs, n_freqs)
        assert torch.all(result >= 0)

    def test_modulation_index_n_bins(self):
        """Test modulation index with different number of bins."""
        batch_size, n_chs, n_freqs, n_segments, seq_len = 1, 2, 3, 4, 100
        pha = np.random.uniform(
            -np.pi, np.pi, (batch_size, n_chs, n_freqs, n_segments, seq_len)
        )
        amp = np.random.uniform(0, 1, (batch_size, n_chs, n_freqs, n_segments, seq_len))

        # Test different bin numbers
        for n_bins in [6, 12, 18, 36]:
            result = modulation_index(pha, amp, n_bins=n_bins)
            assert result.shape == (batch_size, n_chs, n_freqs, n_freqs)

    def test_modulation_index_amp_prob(self):
        """Test modulation index with amplitude probability option."""
        batch_size, n_chs, n_freqs, n_segments, seq_len = 1, 2, 3, 4, 100
        pha = np.random.uniform(
            -np.pi, np.pi, (batch_size, n_chs, n_freqs, n_segments, seq_len)
        )
        amp = np.random.uniform(0, 1, (batch_size, n_chs, n_freqs, n_segments, seq_len))

        result_false = modulation_index(pha, amp, amp_prob=False)
        result_true = modulation_index(pha, amp, amp_prob=True)

        assert result_false.shape == result_true.shape
        # Results should be different with different amp_prob settings
        assert not np.allclose(result_false, result_true)

    def test_reshape_basic(self):
        """Test _reshape function basic functionality."""
        x = np.random.randn(4, 5, 100)
        batch_size, n_chs = 2, 3

        result = _reshape(x, batch_size=batch_size, n_chs=n_chs)

        assert isinstance(result, torch.Tensor)
        assert result.shape == (batch_size, n_chs, 4, 5, 100)
        assert result.dtype == torch.float32

    def test_reshape_broadcasting(self):
        """Test _reshape broadcasting behavior."""
        x = np.array([[[1, 2], [3, 4]]])
        batch_size, n_chs = 3, 2

        result = _reshape(x, batch_size=batch_size, n_chs=n_chs)

        # Check that values are repeated correctly
        for b in range(batch_size):
            for c in range(n_chs):
                assert torch.equal(result[b, c], torch.tensor(x).float())

    def test_modulation_index_zero_amplitude(self):
        """Test modulation index with zero amplitude."""
        batch_size, n_chs, n_freqs, n_segments, seq_len = 1, 1, 2, 3, 100
        pha = np.random.uniform(
            -np.pi, np.pi, (batch_size, n_chs, n_freqs, n_segments, seq_len)
        )
        amp = np.zeros((batch_size, n_chs, n_freqs, n_segments, seq_len))

        result = modulation_index(pha, amp)

        # With zero amplitude, MI should be zero or very small
        assert np.all(result < 0.01)

    def test_modulation_index_constant_phase(self):
        """Test modulation index with constant phase."""
        batch_size, n_chs, n_freqs, n_segments, seq_len = 1, 1, 2, 3, 100
        pha = np.ones((batch_size, n_chs, n_freqs, n_segments, seq_len)) * np.pi / 4
        amp = np.random.uniform(0, 1, (batch_size, n_chs, n_freqs, n_segments, seq_len))

        result = modulation_index(pha, amp)

        # With constant phase, MI should be high (all amplitude in one bin)
        assert result.shape == (batch_size, n_chs, n_freqs, n_freqs)

    def test_modulation_index_phase_range(self):
        """Test that modulation index handles phase in [-pi, pi] correctly."""
        batch_size, n_chs, n_freqs, n_segments, seq_len = 1, 1, 2, 2, 50
        # Test edge cases of phase values
        pha = np.array([-np.pi, -np.pi / 2, 0, np.pi / 2, np.pi]).reshape(1, 1, 1, 1, 5)
        pha = np.tile(pha, (batch_size, n_chs, n_freqs, n_segments, seq_len // 5))
        amp = np.ones_like(pha)

        result = modulation_index(pha, amp)
        assert np.all(np.isfinite(result))

    def test_modulation_index_single_segment(self):
        """Test modulation index with single segment."""
        batch_size, n_chs, n_freqs, n_segments, seq_len = 1, 1, 3, 1, 200
        pha = np.random.uniform(
            -np.pi, np.pi, (batch_size, n_chs, n_freqs, n_segments, seq_len)
        )
        amp = np.random.uniform(0, 1, (batch_size, n_chs, n_freqs, n_segments, seq_len))

        result = modulation_index(pha, amp)
        assert result.shape == (batch_size, n_chs, n_freqs, n_freqs)

    def test_modulation_index_dtype_handling(self):
        """Test modulation index handles different data types."""
        batch_size, n_chs, n_freqs, n_segments, seq_len = 1, 1, 2, 2, 100

        # Test with float64
        pha = np.random.uniform(
            -np.pi, np.pi, (batch_size, n_chs, n_freqs, n_segments, seq_len)
        ).astype(np.float64)
        amp = np.random.uniform(
            0, 1, (batch_size, n_chs, n_freqs, n_segments, seq_len)
        ).astype(np.float64)

        result = modulation_index(pha, amp)
        assert np.all(np.isfinite(result))

    def test_reshape_preserves_values(self):
        """Test that _reshape preserves original values."""
        x = np.random.randn(2, 3, 10)
        result = _reshape(x, batch_size=1, n_chs=1)

        assert torch.allclose(result[0, 0], torch.tensor(x).float())

    def test_reshape_empty_input(self):
        """Test _reshape with empty input."""
        x = np.array([])
        result = _reshape(x.reshape(0, 0, 0), batch_size=2, n_chs=3)

        assert result.shape == (2, 3, 0, 0, 0)

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/dsp/_modulation_index.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-04 02:09:55 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/dsp/_modulation_index.py
# 
# import torch
# 
# from ..decorators import signal_fn
# from ..nn._ModulationIndex import ModulationIndex
# 
# 
# @signal_fn
# def modulation_index(pha, amp, n_bins=18, amp_prob=False):
#     """
#     pha: (batch_size, n_chs, n_freqs_pha, n_segments, seq_len)
#     amp: (batch_size, n_chs, n_freqs_amp, n_segments, seq_len)
#     """
#     return ModulationIndex(n_bins=n_bins, amp_prob=amp_prob)(pha, amp)
# 
# 
# def _reshape(x, batch_size=2, n_chs=4):
#     return (
#         torch.tensor(x)
#         .float()
#         .unsqueeze(0)
#         .unsqueeze(0)
#         .repeat(batch_size, n_chs, 1, 1, 1)
#     )
# 
# 
# if __name__ == "__main__":
#     import sys
# 
#     import matplotlib.pyplot as plt
#     import scitex
# 
#     # Start
#     CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.gen.start(sys, plt, fig_scale=3)
# 
#     # Parameters
#     FS = 512
#     T_SEC = 5
# 
#     # Demo signal
#     xx, tt, fs = scitex.dsp.demo_sig(fs=FS, t_sec=T_SEC, sig_type="tensorpac")
#     # xx.shape: (8, 19, 20, 512)
# 
#     # Tensorpac
#     (
#         pha,
#         amp,
#         freqs_pha,
#         freqs_amp,
#         pac_tp,
#     ) = scitex.dsp.utils.pac.calc_pac_with_tensorpac(xx, fs, t_sec=T_SEC)
# 
#     # GPU calculation with scitex.dsp.nn.ModulationIndex
#     pha, amp = _reshape(pha), _reshape(amp)
#     pac_scitex = scitex.dsp.modulation_index(pha, amp).cpu().numpy()
#     i_batch, i_ch = 0, 0
#     pac_scitex = pac_scitex[i_batch, i_ch]
# 
#     # Plots
#     fig = scitex.dsp.utils.pac.plot_PAC_scitex_vs_tensorpac(
#         pac_scitex, pac_tp, freqs_pha, freqs_amp
#     )
#     fig.suptitle("MI (modulation index) calculation")
#     scitex.io.save(fig, "modulation_index.png")
# 
#     # Close
#     scitex.gen.close(CONFIG)
# 
# # EOF
# 
# """
# /home/ywatanabe/proj/entrance/scitex/dsp/_modulation_index.py
# """
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/dsp/_modulation_index.py
# --------------------------------------------------------------------------------
