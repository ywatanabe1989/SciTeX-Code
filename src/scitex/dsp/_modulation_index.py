#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-04 02:09:55 (ywatanabe)"
# File: ./scitex_repo/src/scitex/dsp/_modulation_index.py

import torch

from ..decorators import signal_fn
from ..nn._ModulationIndex import ModulationIndex


@signal_fn
def modulation_index(pha, amp, n_bins=18, amp_prob=False):
    """
    pha: (batch_size, n_chs, n_freqs_pha, n_segments, seq_len)
    amp: (batch_size, n_chs, n_freqs_amp, n_segments, seq_len)
    """
    return ModulationIndex(n_bins=n_bins, amp_prob=amp_prob)(pha, amp)


def _reshape(x, batch_size=2, n_chs=4):
    return (
        torch.tensor(x)
        .float()
        .unsqueeze(0)
        .unsqueeze(0)
        .repeat(batch_size, n_chs, 1, 1, 1)
    )


if __name__ == "__main__":
    import sys

    import matplotlib.pyplot as plt
    import scitex

    # Start
    CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.gen.start(sys, plt, fig_scale=3)

    # Parameters
    FS = 512
    T_SEC = 5

    # Demo signal
    xx, tt, fs = scitex.dsp.demo_sig(fs=FS, t_sec=T_SEC, sig_type="tensorpac")
    # xx.shape: (8, 19, 20, 512)

    # Tensorpac
    (
        pha,
        amp,
        freqs_pha,
        freqs_amp,
        pac_tp,
    ) = scitex.dsp.utils.pac.calc_pac_with_tensorpac(xx, fs, t_sec=T_SEC)

    # GPU calculation with scitex.dsp.nn.ModulationIndex
    pha, amp = _reshape(pha), _reshape(amp)
    pac_scitex = scitex.dsp.modulation_index(pha, amp).cpu().numpy()
    i_batch, i_ch = 0, 0
    pac_scitex = pac_scitex[i_batch, i_ch]

    # Plots
    fig = scitex.dsp.utils.pac.plot_PAC_scitex_vs_tensorpac(
        pac_scitex, pac_tp, freqs_pha, freqs_amp
    )
    fig.suptitle("MI (modulation index) calculation")
    scitex.io.save(fig, "modulation_index.png")

    # Close
    scitex.gen.close(CONFIG)

# EOF

"""
/home/ywatanabe/proj/entrance/scitex/dsp/_modulation_index.py
"""

# EOF
