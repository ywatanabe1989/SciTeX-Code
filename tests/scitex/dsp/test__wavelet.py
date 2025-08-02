#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-07 14:23:18 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/dsp/test__wavelet.py

import pytest
import numpy as np
import torch
from scitex.dsp import wavelet


class TestWavelet:
    """Test cases for wavelet transformation functionality."""

    def test_import(self):
        """Test that wavelet can be imported."""
        assert callable(wavelet)

    def test_wavelet_basic_numpy(self):
        """Test basic wavelet transform with numpy array."""
        # Create test signal
        fs = 256
        t = np.linspace(0, 2, 2 * fs)
        freq = 10  # Hz
        x = np.sin(2 * np.pi * freq * t).reshape(1, 1, -1).astype(np.float32)

        pha, amp, freqs = wavelet(x, fs, device="cpu")

        assert isinstance(pha, np.ndarray)
        assert isinstance(amp, np.ndarray)
        assert isinstance(freqs, np.ndarray)
        assert pha.shape[0] == 1  # batch size
        assert pha.shape[1] == 1  # channels
        assert amp.shape == pha.shape
        assert len(freqs.shape) >= 1
        assert np.all(amp >= 0)  # Amplitude should be non-negative

    def test_wavelet_basic_torch(self):
        """Test basic wavelet transform with torch tensor."""
        fs = 256
        t = torch.linspace(0, 2, 2 * fs)
        freq = 10  # Hz
        x = torch.sin(2 * torch.pi * freq * t).reshape(1, 1, -1)

        pha, amp, freqs = wavelet(x, fs, device="cpu")

        assert isinstance(pha, torch.Tensor)
        assert isinstance(amp, torch.Tensor)
        assert isinstance(freqs, torch.Tensor)
        assert torch.all(amp >= 0)

    def test_wavelet_multi_channel(self):
        """Test wavelet transform with multiple channels."""
        fs = 256
        n_channels = 4
        n_samples = 512
        x = np.random.randn(1, n_channels, n_samples).astype(np.float32)

        pha, amp, freqs = wavelet(x, fs, device="cpu")

        assert pha.shape[0] == 1
        assert pha.shape[1] == n_channels
        assert amp.shape == pha.shape

    def test_wavelet_batch_processing(self):
        """Test wavelet transform with batch processing."""
        fs = 256
        batch_size = 3
        n_samples = 512
        x = np.random.randn(batch_size, 2, n_samples).astype(np.float32)

        pha, amp, freqs = wavelet(x, fs, device="cpu", batch_size=2)

        assert pha.shape[0] == batch_size
        assert amp.shape[0] == batch_size

    def test_wavelet_freq_scale_linear(self):
        """Test wavelet transform with linear frequency scale."""
        fs = 256
        n_samples = 512
        x = np.random.randn(1, 1, n_samples).astype(np.float32)

        pha, amp, freqs = wavelet(x, fs, freq_scale="linear", device="cpu")

        # Check that frequencies are approximately linearly spaced
        freq_diffs = np.diff(freqs.flatten())
        assert np.std(freq_diffs) / np.mean(freq_diffs) < 0.1

    def test_wavelet_out_scale_log(self):
        """Test wavelet transform with log output scale."""
        fs = 256
        n_samples = 512
        x = np.random.randn(1, 1, n_samples).astype(np.float32)

        pha_lin, amp_lin, _ = wavelet(x, fs, out_scale="linear", device="cpu")
        pha_log, amp_log, _ = wavelet(x, fs, out_scale="log", device="cpu")

        # Phase should be the same
        np.testing.assert_allclose(pha_lin, pha_log, rtol=1e-5)

        # Amplitude should be different (log scale)
        assert not np.allclose(amp_lin, amp_log)

        # Log amplitude should not have NaN
        assert not np.any(np.isnan(amp_log))

    @pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
    def test_wavelet_cuda_device(self):
        """Test wavelet transform on CUDA device."""
        fs = 256
        n_samples = 512
        x = torch.randn(1, 2, n_samples)

        pha, amp, freqs = wavelet(x, fs, device="cuda")

        assert pha.is_cuda
        assert amp.is_cuda
        assert freqs.is_cuda

    def test_wavelet_frequency_content(self):
        """Test that wavelet detects correct frequency content."""
        fs = 256
        t = np.linspace(0, 2, 2 * fs)
        freq = 20  # Hz
        x = np.sin(2 * np.pi * freq * t).reshape(1, 1, -1).astype(np.float32)

        pha, amp, freqs = wavelet(x, fs, device="cpu")

        # Find frequency with maximum amplitude
        amp_mean = np.mean(amp[0, 0], axis=0)
        peak_freq_idx = np.argmax(amp_mean)
        peak_freq = freqs.flatten()[peak_freq_idx]

        # Should be close to the input frequency
        assert abs(peak_freq - freq) < 10  # Within 10 Hz tolerance

    def test_wavelet_phase_range(self):
        """Test that phase values are in correct range."""
        fs = 256
        n_samples = 512
        x = np.random.randn(1, 1, n_samples).astype(np.float32)

        pha, amp, freqs = wavelet(x, fs, device="cpu")

        # Phase should be in [-pi, pi] range
        assert np.all(pha >= -np.pi - 0.1)
        assert np.all(pha <= np.pi + 0.1)

    def test_wavelet_empty_signal_raises(self):
        """Test that empty signal raises error."""
        fs = 256
        x = np.array([]).reshape(1, 1, 0)

        with pytest.raises(Exception):
            wavelet(x, fs, device="cpu")

    def test_wavelet_time_frequency_dimensions(self):
        """Test output dimensions match expected time-frequency representation."""
        fs = 256
        n_samples = 512
        x = np.random.randn(1, 1, n_samples).astype(np.float32)

        pha, amp, freqs = wavelet(x, fs, device="cpu")

        # Should have time and frequency dimensions
        assert len(pha.shape) >= 3  # batch, channel, time, freq
        assert pha.shape[-2] > 1  # time dimension
        assert pha.shape[-1] > 1  # frequency dimension

    def test_wavelet_chirp_signal(self):
        """Test wavelet transform on chirp signal."""
        fs = 512
        t = np.linspace(0, 2, 2 * fs)
        # Linear chirp from 10 to 100 Hz
        f0, f1 = 10, 100
        chirp = np.sin(2 * np.pi * (f0 + (f1 - f0) * t / 2) * t)
        x = chirp.reshape(1, 1, -1).astype(np.float32)

        pha, amp, freqs = wavelet(x, fs, device="cpu")

        # Should detect increasing frequency content over time
        amp_data = amp[0, 0]

        # Early time should have more low frequency content
        early_amp = amp_data[: len(amp_data) // 4].mean(axis=0)
        late_amp = amp_data[-len(amp_data) // 4 :].mean(axis=0)

        # Find peak frequencies
        early_peak = freqs.flatten()[np.argmax(early_amp)]
        late_peak = freqs.flatten()[np.argmax(late_amp)]

        # Late peak should be higher frequency than early peak
        assert late_peak > early_peak

    def test_wavelet_dtype_preservation(self):
        """Test that wavelet preserves data types appropriately."""
        fs = 256
        n_samples = 512

        # Test float32
        x_f32 = torch.randn(1, 1, n_samples, dtype=torch.float32)
        pha_f32, amp_f32, _ = wavelet(x_f32, fs, device="cpu")
        assert pha_f32.dtype == torch.float32
        assert amp_f32.dtype == torch.float32

    def test_wavelet_large_batch(self):
        """Test wavelet with large batch size."""
        fs = 256
        batch_size = 10
        n_samples = 256
        x = np.random.randn(batch_size, 2, n_samples).astype(np.float32)

        pha, amp, freqs = wavelet(x, fs, device="cpu", batch_size=4)

        assert pha.shape[0] == batch_size
        assert amp.shape[0] == batch_size

        # All batches should have valid data
        assert not np.any(np.isnan(pha))
        assert not np.any(np.isnan(amp))

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/dsp/_wavelet.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-04 02:12:00 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/dsp/_wavelet.py
# 
# """scitex.dsp.wavelet function"""
# 
# 
# from ..decorators import batch_fn, signal_fn
# from ..nn._Wavelet import Wavelet
# import scitex
# 
# 
# # Functions
# @signal_fn
# @batch_fn
# def wavelet(
#     x,
#     fs,
#     freq_scale="linear",
#     out_scale="linear",
#     device="cuda",
#     batch_size=32,
# ):
#     m = Wavelet(fs, freq_scale=freq_scale, out_scale="linear").to(device).eval()
#     pha, amp, freqs = m(x.to(device))
# 
#     if out_scale == "log":
#         amp = (amp + 1e-5).log()
#         if amp.isnan().any():
#             print("NaN is detected while taking the lograrithm of amplitude.")
# 
#     return pha, amp, freqs
# 
# 
# # @signal_fn
# # def wavelet(
# #     x,
# #     fs,
# #     freq_scale="linear",
# #     out_scale="linear",
# #     device="cuda",
# #     batch_size=32,
# # ):
# #     @signal_fn
# #     def _wavelet(
# #         x,
# #         fs,
# #         freq_scale="linear",
# #         out_scale="linear",
# #         device="cuda",
# #     ):
# #         m = (
# #             Wavelet(fs, freq_scale=freq_scale, out_scale=out_scale)
# #             .to(device)
# #             .eval()
# #         )
# #         pha, amp, freqs = m(x.to(device))
# 
# #         if out_scale == "log":
# #             amp = (amp + 1e-5).log()
# #             if amp.isnan().any():
# #                 print(
# #                     "NaN is detected while taking the lograrithm of amplitude."
# #                 )
# 
# #         return pha, amp, freqs
# 
# #     if len(x) <= batch_size:
# #         try:
# #             pha, amp, freqs = _wavelet(
# #                 x,
# #                 fs,
# #                 freq_scale=freq_scale,
# #                 out_scale=out_scale,
# #                 device=device,
# #             )
# #             torch.cuda.empty_cache()
# #             return pha, amp, freqs
# 
# #         except Exception as e:
# #             print(e)
# #             print("\nTrying Batch Mode...")
# 
# #     n_batches = (len(x) + batch_size - 1) // batch_size
# #     device_orig = x.device
# #     pha, amp, freqs = [], [], []
# #     for i_batch in tqdm(range(n_batches)):
# #         start = i_batch * batch_size
# #         end = (i_batch + 1) * batch_size
# #         _pha, _amp, _freqs = _wavelet(
# #             x[start:end],
# #             fs,
# #             freq_scale=freq_scale,
# #             out_scale=out_scale,
# #             device=device,
# #         )
# #         torch.cuda.empty_cache()
# #         # to CPU
# #         pha.append(_pha.cpu())
# #         amp.append(_amp.cpu())
# #         freqs.append(_freqs.cpu())
# 
# #     pha = torch.vstack(pha)
# #     amp = torch.vstack(amp)
# #     freqs = freqs[0]
# 
# #     try:
# #         pha = pha.to(device_orig)
# #         amp = amp.to(device_orig)
# #         freqs = freqs.to(device_orig)
# #     except Exception as e:
# #         print(
# #             f"\nError occurred while transferring wavelet outputs back to the original device. Proceeding with CPU tensor. \n\n({e})"
# #         )
# 
# #     sleep(0.5)
# #     torch.cuda.empty_cache()
# #     return pha, amp, freqs
# 
# 
# if __name__ == "__main__":
#     import sys
# 
#     import matplotlib.pyplot as plt
#     import numpy as np
# 
#     # Start
#     CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.gen.start(sys, plt, agg=True)
# 
#     # Parameters
#     FS = 512
#     SIG_TYPE = "chirp"
#     T_SEC = 4
# 
#     # Demo signal
#     xx, tt, fs = scitex.dsp.demo_sig(
#         batch_size=64,
#         n_chs=19,
#         n_segments=2,
#         t_sec=T_SEC,
#         fs=FS,
#         sig_type=SIG_TYPE,
#     )
# 
#     if SIG_TYPE in ["tensorpac", "pac"]:
#         i_segment = 0
#         xx = xx[:, :, i_segment, :]
# 
#     # Main
#     pha, amp, freqs = wavelet(xx, fs, device="cuda")
#     freqs = freqs[0, 0]
# 
#     # Plots
#     i_batch, i_ch = 0, 0
#     fig, axes = scitex.plt.subplots(nrows=3)
# 
#     # # Time vector for x-axis extents
#     # time_extent = [tt.min(), tt.max()]
# 
#     # Trace
#     axes[0].plot(tt, xx[i_batch, i_ch], label=SIG_TYPE)
#     axes[0].set_ylabel("Amplitude [?V]")
#     axes[0].legend(loc="upper left")
#     axes[0].set_title("Signal")
# 
#     # Amplitude
#     # extent = [time_extent[0], time_extent[1], freqs.min(), freqs.max()]
#     axes[1].imshow2d(
#         np.log(amp[i_batch, i_ch] + 1e-5).T,
#         cbar_label="Log(amplitude [?V]) [a.u.]",
#         aspect="auto",
#         # extent=extent,
#         # origin="lower",
#     )
#     axes[1] = scitex.plt.ax.set_ticks(axes[1], x_ticks=tt, y_ticks=freqs)
#     axes[1].set_ylabel("Frequency [Hz]")
#     axes[1].set_title("Amplitude")
# 
#     # Phase
#     axes[2].imshow2d(
#         pha[i_batch, i_ch].T,
#         cbar_label="Phase [rad]",
#         aspect="auto",
#         # extent=extent,
#         # origin="lower",
#     )
#     axes[2] = scitex.plt.ax.set_ticks(axes[2], x_ticks=tt, y_ticks=freqs)
#     axes[2].set_ylabel("Frequency [Hz]")
#     axes[2].set_title("Phase")
# 
#     fig.suptitle("Wavelet Transformation")
#     fig.supxlabel("Time [s]")
# 
#     for ax in axes:
#         ax = scitex.plt.ax.set_n_ticks(ax)
#         # ax.set_xlim(time_extent[0], time_extent[1])
# 
#     fig.tight_layout(rect=[0, 0.03, 1, 0.95])
# 
#     scitex.io.save(fig, "wavelet.png")
# 
#     # Close
#     scitex.gen.close(CONFIG)
# 
# # EOF
# 
# """
# /home/ywatanabe/proj/entrance/scitex/dsp/_wavelet.py
# """
# 
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/dsp/_wavelet.py
# --------------------------------------------------------------------------------
