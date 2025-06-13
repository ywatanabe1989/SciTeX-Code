#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-04-06 01:36:18 (ywatanabe)"

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


# Functions
def calc_norm_resample_filt_hilbert(xx, tt, fs, sig_type, verbose=True):
    sigs = {"index": ("signal", "time", "fs")}  # Collector

    if sig_type == "tensorpac":
        xx = xx[:, :, 0]

    sigs[f"orig"] = (xx, tt, fs)

    # Normalization
    sigs["z_normed"] = (scitex.dsp.norm.z(xx), tt, fs)
    sigs["minmax_normed"] = (scitex.dsp.norm.minmax(xx), tt, fs)

    # Resampling
    sigs["resampled"] = (
        scitex.dsp.resample(xx, fs, TGT_FS),
        tt[:: int(fs / TGT_FS)],
        TGT_FS,
    )

    # Noise injection
    sigs["gaussian_noise_added"] = (scitex.dsp.add_noise.gauss(xx), tt, fs)
    sigs["white_noise_added"] = (scitex.dsp.add_noise.white(xx), tt, fs)
    sigs["pink_noise_added"] = (scitex.dsp.add_noise.pink(xx), tt, fs)
    sigs["brown_noise_added"] = (scitex.dsp.add_noise.brown(xx), tt, fs)

    # Filtering
    sigs[f"bandpass_filted ({LOW_HZ} - {HIGH_HZ} Hz)"] = (
        scitex.dsp.filt.bandpass(xx, fs, low_hz=LOW_HZ, high_hz=HIGH_HZ),
        tt,
        fs,
    )

    sigs[f"bandstop_filted ({LOW_HZ} - {HIGH_HZ} Hz)"] = (
        scitex.dsp.filt.bandstop(xx, fs, low_hz=LOW_HZ, high_hz=HIGH_HZ),
        tt,
        fs,
    )
    sigs[f"bandstop_gauss (sigma = {SIGMA})"] = (
        scitex.dsp.filt.gauss(xx, sigma=SIGMA),
        tt,
        fs,
    )

    # Hilbert Transformation
    pha, amp = scitex.dsp.hilbert(xx)
    sigs["hilbert_amp"] = (amp, tt, fs)
    sigs["hilbert_pha"] = (pha, tt, fs)

    sigs = pd.DataFrame(sigs).set_index("index")

    if verbose:
        print(sigs.index)
        print(sigs.columns)

    return sigs


def plot_signals(plt, sigs, sig_type):
    fig, axes = plt.subplots(nrows=len(sigs.columns), sharex=True)

    i_batch = 0
    i_ch = 0
    for ax, (i_col, col) in zip(axes, enumerate(sigs.columns)):

        if col == "hilbert_amp":  # add the original signal to the ax
            _col = "orig"
            (
                _xx,
                _tt,
                _fs,
            ) = sigs[_col]
            ax.plot(_tt, _xx[i_batch, i_ch], label=_col, c=CC["blue"])

        # Main
        xx, tt, fs = sigs[col]
        # if sig_type == "tensorpac":
        #     xx = xx[:, :, 0]

        try:
            ax.plot(
                tt,
                xx[i_batch, i_ch],
                label=col,
                c=CC["red"] if col == "hilbert_amp" else CC["blue"],
            )
        except Exception as e:
            print(e)
            import ipdb

            ipdb.set_trace()

        # Adjustments
        ax.legend(loc="upper left")
        ax.set_xlim(tt[0], tt[-1])

        ax = scitex.plt.ax.set_n_ticks(ax)

    fig.supxlabel("Time [s]")
    fig.supylabel("Voltage")
    fig.suptitle(sig_type)
    return fig


def plot_wavelet(plt, sigs, sig_col, sig_type):

    xx, tt, fs = sigs[sig_col]
    # if sig_type == "tensorpac":
    #     xx = xx[:, :, 0]

    # Wavelet Transformation
    wavelet_coef, ff_ww = scitex.dsp.wavelet(xx, fs)

    i_batch = 0
    i_ch = 0

    # Main
    fig, axes = plt.subplots(nrows=2, sharex=True)
    # Signal
    axes[0].plot(
        tt,
        xx[i_batch, i_ch],
        label=sig_col,
        c=CC["blue"],
    )
    # Adjusts
    axes[0].legend(loc="upper left")
    axes[0].set_xlim(tt[0], tt[-1])
    axes[0].set_ylabel("Voltage")
    axes[0] = scitex.plt.ax.set_n_ticks(axes[0])

    # Wavelet Spectrogram
    axes[1].imshow(
        wavelet_coef[i_batch, i_ch],
        aspect="auto",
        extent=[tt[0], tt[-1], 512, 1],
        label="wavelet_coefficient",
    )
    # axes[1].set_xlabel("Time [s]")
    axes[1].set_ylabel("Frequency [Hz]")
    # axes[1].legend(loc="upper left")
    axes[1].invert_yaxis()

    fig.supxlabel("Time [s]")
    fig.suptitle(sig_type)

    return fig


def plot_psd(plt, sigs, sig_col, sig_type):

    xx, tt, fs = sigs[sig_col]

    # if sig_type == "tensorpac":
    #     xx = xx[:, :, 0]

    # Power Spetrum Density
    psd, ff_pp = scitex.dsp.psd(xx, fs)

    # Main
    i_batch = 0
    i_ch = 0
    fig, axes = plt.subplots(nrows=2, sharex=False)

    # Signal
    axes[0].plot(
        tt,
        xx[i_batch, i_ch],
        label=sig_col,
        c=CC["blue"],
    )
    # Adjustments
    axes[0].legend(loc="upper left")
    axes[0].set_xlim(tt[0], tt[-1])
    axes[0].set_xlabel("Time [s]")
    axes[0].set_ylabel("Voltage")
    axes[0] = scitex.plt.ax.set_n_ticks(axes[0])

    # PSD
    axes[1].plot(ff_pp, psd[i_batch, i_ch], label="PSD")
    axes[1].set_yscale("log")
    axes[1].set_ylabel("Power [uV^2 / Hz]")
    axes[1].set_xlabel("Frequency [Hz]")

    fig.suptitle(sig_type)

    return fig


if __name__ == "__main__":

    # Parameters
    T_SEC = 4
    SIG_TYPES = [
        # "uniform",
        # "gauss",
        # "periodic",
        # "chirp",
        # "ripple",
        # "meg",
        "tensorpac",
    ]
    SRC_FS = 1024
    TGT_FS = 512
    FREQS_HZ = [10, 30, 100]
    LOW_HZ = 20
    HIGH_HZ = 50
    SIGMA = 10

    plt, CC = scitex.plt.configure_mpl(plt, fig_scale=10)
    sdir = "/home/ywatanabe/proj/entrance/scitex/dsp/example/"

    for sig_type in SIG_TYPES:
        # Demo Signal
        xx, tt, fs = scitex.dsp.demo_sig(
            t_sec=T_SEC, fs=SRC_FS, freqs_hz=FREQS_HZ, sig_type=sig_type
        )

        # Apply calculations on the original signal
        sigs = calc_norm_resample_filt_hilbert(xx, tt, fs, sig_type)

        # Plots signals
        fig = plot_signals(plt, sigs, sig_type)
        scitex.io.save(fig, sdir + f"{sig_type}/1_signals.png")

        # Plots wavelet coefficients and PSD
        for sig_col in sigs.columns:

            if "hilbert" in sig_col:
                continue

            fig = plot_wavelet(plt, sigs, sig_col, sig_type)
            scitex.io.save(fig, sdir + f"{sig_type}/2_wavelet_{sig_col}.png")

            fig = plot_psd(plt, sigs, sig_col, sig_type)
            scitex.io.save(fig, sdir + f"{sig_type}/3_psd_{sig_col}.png")

    # plt.show()

    """
    python ./dsp/example.py
    """
