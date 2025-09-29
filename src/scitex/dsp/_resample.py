#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-04-13 02:35:11 (ywatanabe)"


import torch
import torchaudio.transforms as T
from ..decorators import signal_fn
import scitex


@signal_fn
def resample(x, src_fs, tgt_fs, t=None):
    xr = T.Resample(src_fs, tgt_fs, dtype=x.dtype).to(x.device)(x)
    if t is None:
        return xr
    if t is not None:
        tr = torch.linspace(t[0], t[-1], xr.shape[-1])
        return xr, tr


if __name__ == "__main__":
    import sys

    import matplotlib.pyplot as plt

    # Start
    CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.session.start(sys, plt)

    # Parameters
    T_SEC = 1
    SIG_TYPE = "chirp"
    SRC_FS = 128
    TGT_FS_UP = 256
    TGT_FS_DOWN = 64
    FREQS_HZ = [10, 30, 100, 300]

    # Demo Signal
    xx, tt, fs = scitex.dsp.demo_sig(
        t_sec=T_SEC, fs=SRC_FS, freqs_hz=FREQS_HZ, sig_type=SIG_TYPE
    )

    # Resampling
    xd, td = scitex.dsp.resample(xx, fs, TGT_FS_DOWN, t=tt)
    xu, tu = scitex.dsp.resample(xx, fs, TGT_FS_UP, t=tt)

    # Plots
    i_batch, i_ch = 0, 0
    fig, axes = plt.subplots(nrows=3, sharex=True, sharey=True)
    axes[0].plot(tt, xx[i_batch, i_ch], label=f"Original ({SRC_FS} Hz)")
    axes[1].plot(td, xd[i_batch, i_ch], label=f"Down-sampled ({TGT_FS_DOWN} Hz)")
    axes[2].plot(tu, xu[i_batch, i_ch], label=f"Up-sampled ({TGT_FS_UP} Hz)")
    for ax in axes:
        ax.legend(loc="upper left")

    axes[-1].set_xlabel("Time [s]")
    fig.supylabel("Amplitude [?V]")
    fig.suptitle("Resampling")
    scitex.io.save(fig, "traces.png")
    # plt.show()

# EOF

"""
/home/ywatanabe/proj/entrance/scitex/dsp/_resample.py
"""
