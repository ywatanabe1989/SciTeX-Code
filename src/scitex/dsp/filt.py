#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-04 02:05:47 (ywatanabe)"
# File: ./scitex_repo/src/scitex/dsp/filt.py

import scitex
import numpy as np

from ..decorators import signal_fn

# No top-level imports from nn module to avoid circular dependency
# Filters will be imported inside functions when needed


@signal_fn
def gauss(x, sigma, t=None):
    from ..nn._Filters import GaussianFilter
    return GaussianFilter(sigma)(x, t=t)


@signal_fn
def bandpass(x, fs, bands, t=None):
    import torch
    from ..nn._Filters import BandPassFilter

    # Convert bands to tensor if it's not already
    if not isinstance(bands, torch.Tensor):
        bands = torch.tensor(bands, dtype=torch.float32)
    return BandPassFilter(bands, fs, x.shape[-1])(x, t=t)


@signal_fn
def bandstop(x, fs, bands, t=None):
    from ..nn._Filters import BandStopFilter
    return BandStopFilter(bands, fs, x.shape[-1])(x, t=t)


@signal_fn
def lowpass(x, fs, cutoffs_hz, t=None):
    from ..nn._Filters import LowPassFilter
    return LowPassFilter(cutoffs_hz, fs, x.shape[-1])(x, t=t)


@signal_fn
def highpass(x, fs, cutoffs_hz, t=None):
    from ..nn._Filters import HighPassFilter
    return HighPassFilter(cutoffs_hz, fs, x.shape[-1])(x, t=t)


def _custom_print(x):
    print(type(x), x.shape)


if __name__ == "__main__":
    import sys

    import matplotlib.pyplot as plt
    import torch

    # Start
    CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.gen.start(sys, plt)

    # Parametes
    T_SEC = 1
    SRC_FS = 1024
    FREQS_HZ = list(np.linspace(0, 500, 10, endpoint=False).astype(int))
    SIG_TYPE = "periodic"
    BANDS = np.vstack([[80, 310]])
    SIGMA = 3

    # Demo Signal
    xx, tt, fs = scitex.dsp.demo_sig(
        t_sec=T_SEC,
        fs=SRC_FS,
        freqs_hz=FREQS_HZ,
        sig_type=SIG_TYPE,
    )

    # Filtering
    x_bp, t_bp = scitex.dsp.filt.bandpass(xx, fs, BANDS, t=tt)
    x_bs, t_bs = scitex.dsp.filt.bandstop(xx, fs, BANDS, t=tt)
    x_lp, t_lp = scitex.dsp.filt.lowpass(xx, fs, BANDS[:, 0], t=tt)
    x_hp, t_hp = scitex.dsp.filt.highpass(xx, fs, BANDS[:, 1], t=tt)
    x_g, t_g = scitex.dsp.filt.gauss(xx, sigma=SIGMA, t=tt)
    filted = {
        f"Original (Sum of {FREQS_HZ}-Hz signals)": (xx, tt, fs),
        f"Bandpass-filtered ({BANDS[0][0]} - {BANDS[0][1]} Hz)": (
            x_bp,
            t_bp,
            fs,
        ),
        f"Bandstop-filtered ({BANDS[0][0]} - {BANDS[0][1]} Hz)": (
            x_bs,
            t_bs,
            fs,
        ),
        f"Lowpass-filtered ({BANDS[0][0]} Hz)": (x_lp, t_lp, fs),
        f"Highpass-filtered ({BANDS[0][1]} Hz)": (x_hp, t_hp, fs),
        f"Gaussian-filtered (sigma = {SIGMA} SD [point])": (x_g, t_g, fs),
    }

    # Plots traces
    fig, axes = plt.subplots(nrows=len(filted), ncols=1, sharex=True, sharey=True)
    i_batch = 0
    i_ch = 0
    i_filt = 0
    for ax, (k, v) in zip(axes, filted.items()):
        _xx, _tt, _fs = v
        if _xx.ndim == 3:
            _xx = _xx[i_batch, i_ch]
        elif _xx.ndim == 4:
            _xx = _xx[i_batch, i_ch, i_filt]
        ax.plot(_tt, _xx, label=k)
        ax.legend(loc="upper left")

    fig.suptitle("Filtered")
    fig.supxlabel("Time [s]")
    fig.supylabel("Amplitude")

    scitex.io.save(fig, "traces.png")

    # Calculates and Plots PSD
    fig, axes = plt.subplots(nrows=len(filted), ncols=1, sharex=True, sharey=True)
    i_batch = 0
    i_ch = 0
    i_filt = 0
    for ax, (k, v) in zip(axes, filted.items()):
        _xx, _tt, _fs = v

        _psd, ff = scitex.dsp.psd(_xx, _fs)
        if _psd.ndim == 3:
            _psd = _psd[i_batch, i_ch]
        elif _psd.ndim == 4:
            _psd = _psd[i_batch, i_ch, i_filt]

        ax.plot(ff, _psd, label=k)
        ax.legend(loc="upper left")

        for bb in np.hstack(BANDS):
            ax.axvline(x=bb, color=CC["grey"], linestyle="--")

    fig.suptitle("PSD (power spectrum density) of filtered signals")
    fig.supxlabel("Frequency [Hz]")
    fig.supylabel("log(Power [uV^2 / Hz]) [a.u.]")
    scitex.io.save(fig, "psd.png")

    # Close
    scitex.gen.close(CONFIG)

# EOF

"""
/home/ywatanabe/proj/scitex/src/scitex/dsp/filt.py
"""

# EOF
