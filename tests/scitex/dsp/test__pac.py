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
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/dsp/_pac.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-26 22:24:40 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/dsp/_pac.py
# 
# THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/dsp/_pac.py"
# 
# import sys
# 
# import matplotlib.pyplot as plt
# import numpy as np
# import torch
# from ..str import printc
# 
# from ..decorators import signal_fn, batch_fn
# from ..nn._PAC import PAC
# 
# """
# scitex.dsp.pac function
# """
# 
# 
# # @batch_fn
# @signal_fn
# def pac(
#     x,
#     fs,
#     pha_start_hz=2,
#     pha_end_hz=20,
#     pha_n_bands=100,
#     amp_start_hz=60,
#     amp_end_hz=160,
#     amp_n_bands=100,
#     device="cuda",
#     batch_size=1,
#     batch_size_ch=-1,
#     fp16=False,
#     trainable=False,
#     n_perm=None,
#     amp_prob=False,
# ):
#     """
#     Compute the phase-amplitude coupling (PAC) for signals. This function automatically handles inputs as
#     PyTorch tensors, NumPy arrays, or pandas DataFrames.
# 
#     Arguments:
#     - x (torch.Tensor | np.ndarray | pd.DataFrame): Input signal. Shape can be either (batch_size, n_chs, seq_len) or
#     - fs (float): Sampling frequency of the input signal.
#     - pha_start_hz (float, optional): Start frequency for phase bands. Default is 2 Hz.
#     - pha_end_hz (float, optional): End frequency for phase bands. Default is 20 Hz.
#     - pha_n_bands (int, optional): Number of phase bands. Default is 100.
#     - amp_start_hz (float, optional): Start frequency for amplitude bands. Default is 60 Hz.
#     - amp_end_hz (float, optional): End frequency for amplitude bands. Default is 160 Hz.
#     - amp_n_bands (int, optional): Number of amplitude bands. Default is 100.
# 
#     Returns:
#     - torch.Tensor: PAC values. Shape: (batch_size, n_chs, pha_n_bands, amp_n_bands)
#     - numpy.ndarray: Phase bands used for the computation.
#     - numpy.ndarray: Amplitude bands used for the computation.
# 
#     Example:
#         FS = 512
#         T_SEC = 4
#         xx, tt, fs = scitex.dsp.demo_sig(
#             batch_size=1, n_chs=1, fs=FS, t_sec=T_SEC, sig_type="tensorpac"
#         )
#         pac, pha_mids_hz, amp_mids_hz = scitex.dsp.pac(xx, fs)
#     """
# 
#     def process_ch_batching(m, x, batch_size_ch, device):
#         n_chs = x.shape[1]
#         n_batches = (n_chs + batch_size_ch - 1) // batch_size_ch
# 
#         agg = []
#         for ii in range(n_batches):
#             start, end = batch_size_ch * ii, min(batch_size_ch * (ii + 1), n_chs)
#             _pac = m(x[:, start:end, :].to(device)).detach().cpu()
#             agg.append(_pac)
# 
#         # return np.concatenate(agg, axis=1)
#         return torch.cat(agg, dim=1)
# 
#     m = PAC(
#         x.shape[-1],
#         fs,
#         pha_start_hz=pha_start_hz,
#         pha_end_hz=pha_end_hz,
#         pha_n_bands=pha_n_bands,
#         amp_start_hz=amp_start_hz,
#         amp_end_hz=amp_end_hz,
#         amp_n_bands=amp_n_bands,
#         fp16=fp16,
#         trainable=trainable,
#         n_perm=n_perm,
#         amp_prob=amp_prob,
#     ).to(device)
# 
#     if batch_size_ch == -1:
#         return m(x.to(device)), m.PHA_MIDS_HZ, m.AMP_MIDS_HZ
#     else:
#         return (
#             process_ch_batching(m, x, batch_size_ch, device),
#             m.PHA_MIDS_HZ,
#             m.AMP_MIDS_HZ,
#         )
# 
# 
# if __name__ == "__main__":
#     import matplotlib.pyplot as plt
#     import scitex
# 
#     # Start
#     CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.gen.start(sys, plt)
# 
#     pac, freqs_pha, freqs_amp = scitex.dsp.pac(
#         np.random.rand(1, 16, 24000),
#         400,
#         batch_size=1,
#         batch_size_ch=8,
#         fp16=True,
#         n_perm=16,
#     )
# 
# #     # Parameters
# #     FS = 512
# #     T_SEC = 4
# #     # IS_TRAINABLE = False
# #     # FP16 = True
# 
# #     for IS_TRAINABLE in [True, False]:
# #         for FP16 in [True, False]:
# 
# #             # Demo signal
# #             xx, tt, fs = scitex.dsp.demo_sig(
# #                 batch_size=1, n_chs=1, fs=FS, t_sec=T_SEC, sig_type="pac"
# #             )
# 
# 
# #             # scitex.str.print_debug()
# #             # xx = np.random.rand(1,16,24000)
# #             # fs = 400
# 
# #             # scitex calculation
# #             pac_scitex, pha_mids_scitex, amp_mids_scitex = scitex.dsp.pac(
# #                 xx,
# #                 fs,
# #                 pha_n_bands=50,
# #                 amp_n_bands=30,
# #                 trainable=IS_TRAINABLE,
# #                 fp16=FP16,
# #             )
# #             i_batch, i_ch = 0, 0
# #             pac_scitex = pac_scitex[i_batch, i_ch]
# 
# #             printc(type(pac_scitex))
# 
# #             # Tensorpac calculation
# #             (
# #                 _,
# #                 _,
# #                 _pha_mids_tp,
# #                 _amp_mids_tp,
# #                 pac_tp,
# #             ) = scitex.dsp.utils.pac.calc_pac_with_tensorpac(xx, fs, T_SEC)
# 
# #             # Validates the consitency in frequency definitions
# #             assert np.allclose(
# #                 pha_mids_scitex, _pha_mids_tp
# #             )
# #             assert np.allclose(
# #                 amp_mids_scitex, _amp_mids_tp
# #             )
# 
# #             scitex.io.save(
# #                 (pac_scitex, pac_tp, pha_mids_scitex, amp_mids_scitex),
# #                 "./data/cache.npz",
# #             )
# 
# #             # ################################################################################
# #             # # cache
# #             # pac_scitex, pac_tp, pha_mids_scitex, amp_mids_scitex = scitex.io.load(
# #             #     "./data/cache.npz"
# #             # )
# #             # ################################################################################
# 
# #             # Plots
# #             fig = scitex.dsp.utils.pac.plot_PAC_scitex_vs_tensorpac(
# #                 pac_scitex, pac_tp, pha_mids_scitex, amp_mids_scitex
# #             )
# #             fig.suptitle(
# #                 "Phase-Amplitude Coupling calculation\n\n(Bandpass Filtering -> Hilbert Transformation-> Modulation Index)"
# #             )
# #             plt.show()
# 
# #             scitex.gen.reload(scitex.dsp)
# 
# #             # Saves the figure
# #             trainable_str = "trainable" if IS_TRAINABLE else "static"
# #             fp_str = "fp16" if FP16 else "fp32"
# #             scitex.io.save(
# #                 fig, f"pac_with_{trainable_str}_bandpass_{fp_str}.png"
# #             )
# 
# 
# # def run_method_tests():
# #     import scitex
# 
# #     # Test parameters
# #     FS = 512
# #     T_SEC = 4
# 
# #     class PACProcessor:
# #         @batch_torch_fn
# #         def process_pac(self, x, fs, **kwargs):
# #             return pac(x, fs, **kwargs)
# 
# #         @signal_fn
# #         def process_signal(self, x):
# #             return x * 2
# 
# #     def run_method_basic_tests():
# #         processor = PACProcessor()
# 
# #         # Generate test signal
# #         xx, tt, fs = scitex.dsp.demo_sig(
# #             batch_size=1, n_chs=1, fs=FS, t_sec=T_SEC, sig_type="pac"
# #         )
# 
# #         try:
# #             # Test method with batch processing
# #             result_batch, pha_mids, amp_mids = processor.process_pac(
# #                 xx, fs, pha_n_bands=50, amp_n_bands=30, batch_size=1
# #             )
# #             assert torch.is_tensor(result_batch)
# 
# #             # Test basic torch method
# #             result_torch = processor.process_signal(xx)
# #             assert torch.is_tensor(result_torch)
# 
# #             scitex.str.printc("Passed: Basic method tests", "yellow")
# #         except Exception as err:
# #             scitex.str.printc(f"Failed: Basic method tests - {str(err)}", "red")
# 
# #     def run_method_cuda_tests():
# #         if not torch.cuda.is_available():
# #             scitex.str.printc(
# #                 "CUDA method tests skipped: No GPU available", "yellow"
# #             )
# #             return
# 
# #         processor = PACProcessor()
# #         xx, tt, fs = scitex.dsp.demo_sig(
# #             batch_size=1, n_chs=1, fs=FS, t_sec=T_SEC, sig_type="pac"
# #         )
# 
# #         try:
# #             # Test with CUDA
# #             result_cuda, _, _ = processor.process_pac(xx, fs, device="cuda")
# #             assert result_cuda.device.type == "cuda"
# 
# #             result_torch = processor.process_signal(xx, device="cuda")
# #             assert result_torch.device.type == "cuda"
# 
# #             scitex.str.printc("Passed: CUDA method tests", "yellow")
# #         except Exception as err:
# #             scitex.str.printc(f"Failed: CUDA method tests - {str(err)}", "red")
# 
# #     def run_method_batch_size_tests():
# #         processor = PACProcessor()
# #         batch_sizes = [1, 2, 4]
# 
# #         for batch_size in batch_sizes:
# #             try:
# #                 xx, tt, fs = scitex.dsp.demo_sig(
# #                     batch_size=batch_size,
# #                     n_chs=1,
# #                     fs=FS,
# #                     t_sec=T_SEC,
# #                     sig_type="pac",
# #                 )
# 
# #                 result, _, _ = processor.process_pac(
# #                     xx, fs, batch_size=batch_size
# #                 )
# #                 assert result.shape[0] == batch_size
# 
# #                 scitex.str.printc(
# #                     f"Passed: Method batch size test with size={batch_size}",
# #                     "yellow",
# #                 )
# #             except Exception as err:
# #                 scitex.str.printc(
# #                     f"Failed: Method batch size test with size={batch_size} - {str(err)}",
# #                     "red",
# #                 )
# 
# #     # Execute method test suites
# #     test_suites = [
# #         ("Method Basic Tests", run_method_basic_tests),
# #         ("Method CUDA Tests", run_method_cuda_tests),
# #         ("Method Batch Size Tests", run_method_batch_size_tests),
# #     ]
# 
# #     for test_name, test_func in test_suites:
# #         test_func()
# 
# 
# # if __name__ == "__main__":
# #     run_method_tests()
# 
# # # EOF
# 
# # """
# # python -m scitex.dsp._pac
# # """
# 
# #
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/dsp/_pac.py
# --------------------------------------------------------------------------------
