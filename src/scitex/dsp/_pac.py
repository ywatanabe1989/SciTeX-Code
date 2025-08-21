#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-26 22:24:40 (ywatanabe)"
# File: ./scitex_repo/src/scitex/dsp/_pac.py

THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/dsp/_pac.py"

import sys

import matplotlib.pyplot as plt
import numpy as np
import torch
from ..str import printc

from ..decorators import signal_fn, batch_fn
from ..nn._PAC import PAC

"""
scitex.dsp.pac function
"""


# @batch_fn
@signal_fn
def pac(
    x,
    fs,
    pha_start_hz=2,
    pha_end_hz=20,
    pha_n_bands=100,
    amp_start_hz=60,
    amp_end_hz=160,
    amp_n_bands=100,
    device="cuda",
    batch_size=1,
    batch_size_ch=-1,
    fp16=False,
    trainable=False,
    n_perm=None,
    amp_prob=False,
):
    """
    Compute the phase-amplitude coupling (PAC) for signals. This function automatically handles inputs as
    PyTorch tensors, NumPy arrays, or pandas DataFrames.

    Arguments:
    - x (torch.Tensor | np.ndarray | pd.DataFrame): Input signal. Shape can be either (batch_size, n_chs, seq_len) or
    - fs (float): Sampling frequency of the input signal.
    - pha_start_hz (float, optional): Start frequency for phase bands. Default is 2 Hz.
    - pha_end_hz (float, optional): End frequency for phase bands. Default is 20 Hz.
    - pha_n_bands (int, optional): Number of phase bands. Default is 100.
    - amp_start_hz (float, optional): Start frequency for amplitude bands. Default is 60 Hz.
    - amp_end_hz (float, optional): End frequency for amplitude bands. Default is 160 Hz.
    - amp_n_bands (int, optional): Number of amplitude bands. Default is 100.

    Returns:
    - torch.Tensor: PAC values. Shape: (batch_size, n_chs, pha_n_bands, amp_n_bands)
    - numpy.ndarray: Phase bands used for the computation.
    - numpy.ndarray: Amplitude bands used for the computation.

    Example:
        FS = 512
        T_SEC = 4
        xx, tt, fs = scitex.dsp.demo_sig(
            batch_size=1, n_chs=1, fs=FS, t_sec=T_SEC, sig_type="tensorpac"
        )
        pac, pha_mids_hz, amp_mids_hz = scitex.dsp.pac(xx, fs)
    """

    def process_ch_batching(m, x, batch_size_ch, device):
        n_chs = x.shape[1]
        n_batches = (n_chs + batch_size_ch - 1) // batch_size_ch

        agg = []
        for ii in range(n_batches):
            start, end = batch_size_ch * ii, min(batch_size_ch * (ii + 1), n_chs)
            _pac = m(x[:, start:end, :].to(device)).detach().cpu()
            agg.append(_pac)

        # return np.concatenate(agg, axis=1)
        return torch.cat(agg, dim=1)

    m = PAC(
        x.shape[-1],
        fs,
        pha_start_hz=pha_start_hz,
        pha_end_hz=pha_end_hz,
        pha_n_bands=pha_n_bands,
        amp_start_hz=amp_start_hz,
        amp_end_hz=amp_end_hz,
        amp_n_bands=amp_n_bands,
        fp16=fp16,
        trainable=trainable,
        n_perm=n_perm,
        amp_prob=amp_prob,
    ).to(device)

    if batch_size_ch == -1:
        return m(x.to(device)), m.PHA_MIDS_HZ, m.AMP_MIDS_HZ
    else:
        return (
            process_ch_batching(m, x, batch_size_ch, device),
            m.PHA_MIDS_HZ,
            m.AMP_MIDS_HZ,
        )


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import scitex

    # Start
    CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.session.start(sys, plt)

    pac, freqs_pha, freqs_amp = scitex.dsp.pac(
        np.random.rand(1, 16, 24000),
        400,
        batch_size=1,
        batch_size_ch=8,
        fp16=True,
        n_perm=16,
    )

#     # Parameters
#     FS = 512
#     T_SEC = 4
#     # IS_TRAINABLE = False
#     # FP16 = True

#     for IS_TRAINABLE in [True, False]:
#         for FP16 in [True, False]:

#             # Demo signal
#             xx, tt, fs = scitex.dsp.demo_sig(
#                 batch_size=1, n_chs=1, fs=FS, t_sec=T_SEC, sig_type="pac"
#             )


#             # scitex.str.print_debug()
#             # xx = np.random.rand(1,16,24000)
#             # fs = 400

#             # scitex calculation
#             pac_scitex, pha_mids_scitex, amp_mids_scitex = scitex.dsp.pac(
#                 xx,
#                 fs,
#                 pha_n_bands=50,
#                 amp_n_bands=30,
#                 trainable=IS_TRAINABLE,
#                 fp16=FP16,
#             )
#             i_batch, i_ch = 0, 0
#             pac_scitex = pac_scitex[i_batch, i_ch]

#             printc(type(pac_scitex))

#             # Tensorpac calculation
#             (
#                 _,
#                 _,
#                 _pha_mids_tp,
#                 _amp_mids_tp,
#                 pac_tp,
#             ) = scitex.dsp.utils.pac.calc_pac_with_tensorpac(xx, fs, T_SEC)

#             # Validates the consitency in frequency definitions
#             assert np.allclose(
#                 pha_mids_scitex, _pha_mids_tp
#             )
#             assert np.allclose(
#                 amp_mids_scitex, _amp_mids_tp
#             )

#             scitex.io.save(
#                 (pac_scitex, pac_tp, pha_mids_scitex, amp_mids_scitex),
#                 "./data/cache.npz",
#             )

#             # ################################################################################
#             # # cache
#             # pac_scitex, pac_tp, pha_mids_scitex, amp_mids_scitex = scitex.io.load(
#             #     "./data/cache.npz"
#             # )
#             # ################################################################################

#             # Plots
#             fig = scitex.dsp.utils.pac.plot_PAC_scitex_vs_tensorpac(
#                 pac_scitex, pac_tp, pha_mids_scitex, amp_mids_scitex
#             )
#             fig.suptitle(
#                 "Phase-Amplitude Coupling calculation\n\n(Bandpass Filtering -> Hilbert Transformation-> Modulation Index)"
#             )
#             plt.show()

#             scitex.gen.reload(scitex.dsp)

#             # Saves the figure
#             trainable_str = "trainable" if IS_TRAINABLE else "static"
#             fp_str = "fp16" if FP16 else "fp32"
#             scitex.io.save(
#                 fig, f"pac_with_{trainable_str}_bandpass_{fp_str}.png"
#             )


# def run_method_tests():
#     import scitex

#     # Test parameters
#     FS = 512
#     T_SEC = 4

#     class PACProcessor:
#         @batch_torch_fn
#         def process_pac(self, x, fs, **kwargs):
#             return pac(x, fs, **kwargs)

#         @signal_fn
#         def process_signal(self, x):
#             return x * 2

#     def run_method_basic_tests():
#         processor = PACProcessor()

#         # Generate test signal
#         xx, tt, fs = scitex.dsp.demo_sig(
#             batch_size=1, n_chs=1, fs=FS, t_sec=T_SEC, sig_type="pac"
#         )

#         try:
#             # Test method with batch processing
#             result_batch, pha_mids, amp_mids = processor.process_pac(
#                 xx, fs, pha_n_bands=50, amp_n_bands=30, batch_size=1
#             )
#             assert torch.is_tensor(result_batch)

#             # Test basic torch method
#             result_torch = processor.process_signal(xx)
#             assert torch.is_tensor(result_torch)

#             scitex.str.printc("Passed: Basic method tests", "yellow")
#         except Exception as err:
#             scitex.str.printc(f"Failed: Basic method tests - {str(err)}", "red")

#     def run_method_cuda_tests():
#         if not torch.cuda.is_available():
#             scitex.str.printc(
#                 "CUDA method tests skipped: No GPU available", "yellow"
#             )
#             return

#         processor = PACProcessor()
#         xx, tt, fs = scitex.dsp.demo_sig(
#             batch_size=1, n_chs=1, fs=FS, t_sec=T_SEC, sig_type="pac"
#         )

#         try:
#             # Test with CUDA
#             result_cuda, _, _ = processor.process_pac(xx, fs, device="cuda")
#             assert result_cuda.device.type == "cuda"

#             result_torch = processor.process_signal(xx, device="cuda")
#             assert result_torch.device.type == "cuda"

#             scitex.str.printc("Passed: CUDA method tests", "yellow")
#         except Exception as err:
#             scitex.str.printc(f"Failed: CUDA method tests - {str(err)}", "red")

#     def run_method_batch_size_tests():
#         processor = PACProcessor()
#         batch_sizes = [1, 2, 4]

#         for batch_size in batch_sizes:
#             try:
#                 xx, tt, fs = scitex.dsp.demo_sig(
#                     batch_size=batch_size,
#                     n_chs=1,
#                     fs=FS,
#                     t_sec=T_SEC,
#                     sig_type="pac",
#                 )

#                 result, _, _ = processor.process_pac(
#                     xx, fs, batch_size=batch_size
#                 )
#                 assert result.shape[0] == batch_size

#                 scitex.str.printc(
#                     f"Passed: Method batch size test with size={batch_size}",
#                     "yellow",
#                 )
#             except Exception as err:
#                 scitex.str.printc(
#                     f"Failed: Method batch size test with size={batch_size} - {str(err)}",
#                     "red",
#                 )

#     # Execute method test suites
#     test_suites = [
#         ("Method Basic Tests", run_method_basic_tests),
#         ("Method CUDA Tests", run_method_cuda_tests),
#         ("Method Batch Size Tests", run_method_batch_size_tests),
#     ]

#     for test_name, test_func in test_suites:
#         test_func()


# if __name__ == "__main__":
#     run_method_tests()

# # EOF

# """
# python -m scitex.dsp._pac
# """

#

# EOF
