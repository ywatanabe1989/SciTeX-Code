#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-26 22:24:13 (ywatanabe)"
# File: ./scitex_repo/src/scitex/dsp/utils/_differential_bandpass_filters.py

THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/dsp/utils/_differential_bandpass_filters.py"

import sys

import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.nn as nn

from ...decorators import torch_fn
from ...gen._to_even import to_even
from ...gen._to_odd import to_odd

try:
    from torchaudio.prototype.functional import sinc_impulse_response
except:
    pass


# Functions
@torch_fn
def init_bandpass_filters(
    sig_len,
    fs,
    pha_low_hz=2,
    pha_high_hz=20,
    pha_n_bands=30,
    amp_low_hz=60,
    amp_high_hz=160,
    amp_n_bands=50,
    cycle=3,
):
    # Learnable parameters
    pha_mids = nn.Parameter(torch.linspace(pha_low_hz, pha_high_hz, pha_n_bands))
    amp_mids = nn.Parameter(torch.linspace(amp_low_hz, amp_high_hz, amp_n_bands))
    filters = build_bandpass_filters(sig_len, fs, pha_mids, amp_mids, cycle)
    return filters, pha_mids, amp_mids


@torch_fn
def build_bandpass_filters(sig_len, fs, pha_mids, amp_mids, cycle):
    def _define_freqs(mids, factor):
        lows = mids - mids / factor
        highs = mids + mids / factor
        return lows, highs

    def define_order(low_hz, fs, sig_len, cycle):
        order = cycle * int((fs // low_hz))
        order = order if 3 * order >= sig_len else (sig_len - 1) // 3
        order = to_even(order)
        return order

    def _calc_filters(lows_hz, highs_hz, fs, order):
        nyq = fs / 2.0
        order = to_odd(order)
        # lowpass filters
        irs_ll = sinc_impulse_response(lows_hz / nyq, window_size=order)
        irs_hh = sinc_impulse_response(highs_hz / nyq, window_size=order)
        irs = irs_ll - irs_hh
        return irs

    # Main
    pha_lows, pha_highs = _define_freqs(pha_mids, factor=4.0)
    amp_lows, amp_highs = _define_freqs(amp_mids, factor=8.0)

    lowest = min(pha_lows.min().item(), amp_lows.min().item())
    order = define_order(lowest, fs, sig_len, cycle)

    pha_bp_filters = _calc_filters(pha_lows, pha_highs, fs, order)
    amp_bp_filters = _calc_filters(amp_lows, amp_highs, fs, order)
    return torch.vstack([pha_bp_filters, amp_bp_filters])


if __name__ == "__main__":
    import scitex

    # Start
    CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.session.start(sys, plt, agg=True)

    # Demo signal
    freqs_hz = [10, 30, 100, 300]
    fs = 1024
    xx, tt, fs = scitex.dsp.demo_sig(fs=fs, freqs_hz=freqs_hz)

    # Main
    filters, pha_mids, amp_mids = init_bandpass_filters(xx.shape[-1], fs)

    filters.sum().backward()  # OK. The filtering bands are trainable with backpropagation.

    # Update 'pha_mids' and 'amp_mids' in the forward method.
    # Then, re-build filters using optimized parameters like this:
    # self.filters = build_bandpass_filters(self.sig_len, self.fs, self.pha_mids, self.amp_mids, self.cycle)

    mids_all = np.concatenate(
        [pha_mids.detach().cpu().numpy(), amp_mids.detach().cpu().numpy()]
    )

    for i_filter in range(len(mids_all)):
        mid = mids_all[i_filter]
        fig = scitex.dsp.utils.filter.plot_filter_responses(
            filters[i_filter].detach().cpu().numpy(), fs, title=f"{mid:.1f} Hz"
        )
        scitex.io.save(
            fig,
            f"differentiable_bandpass_filter_reponses_filter#{i_filter:03d}_{mid:.1f}_Hz.png",
        )
    # plt.show()

# EOF

"""
python -m scitex.dsp.utils._differential_bandpass_filters
"""

# EOF
