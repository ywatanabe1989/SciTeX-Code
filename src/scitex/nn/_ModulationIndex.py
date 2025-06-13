#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-04 02:08:01 (ywatanabe)"
# File: ./scitex_repo/src/scitex/nn/_ModulationIndex.py

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-10-15 14:12:55 (ywatanabe)"

"""
This script defines the ModulationIndex module.
"""

# Imports
import sys
import warnings

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F


# Functions
class ModulationIndex(nn.Module):
    def __init__(self, n_bins=18, fp16=False, amp_prob=False):
        super(ModulationIndex, self).__init__()
        self.n_bins = n_bins
        self.fp16 = fp16
        self.register_buffer(
            "pha_bin_cutoffs", torch.linspace(-np.pi, np.pi, n_bins + 1)
        )

        self.amp_prob = amp_prob

    @property
    def pha_bin_centers(
        self,
    ):
        return (
            ((self.pha_bin_cutoffs[1:] + self.pha_bin_cutoffs[:-1]) / 2)
            .detach()
            .cpu()
            .numpy()
        )

    def forward(self, pha, amp, epsilon=1e-9):
        """
        Compute the Modulation Index based on phase (pha) and amplitude (amp) tensors.

        Parameters:
        - pha (torch.Tensor): Tensor of phase values with shape
                              (batch_size, n_channels, n_freqs_pha, n_segments, sequence_length).
        - amp (torch.Tensor): Tensor of amplitude values with a similar shape as pha.
                              (batch_size, n_channels, n_freqs_amp, n_segments, sequence_length).

        Returns:
        - MI (torch.Tensor): The Modulation Index for each batch and channel.
        """
        assert pha.ndim == amp.ndim == 5

        if self.fp16:
            pha, amp = pha.half().contiguous(), amp.half().contiguous()
        else:
            pha, amp = pha.float().contiguous(), amp.float().contiguous()

        device = pha.device

        pha_masks = self._phase_to_masks(pha, self.pha_bin_cutoffs.to(device))
        # (batch_size, n_channels, n_freqs_pha, n_segments, sequence_length, n_bins)

        # Expands amp and masks to utilize broadcasting
        # i_batch = 0
        # i_chs = 1
        i_freqs_pha = 2
        i_freqs_amp = 3
        # i_segments = 4
        i_time = 5
        i_bins = 6

        # Coupling
        pha_masks = pha_masks.unsqueeze(i_freqs_amp)
        amp = amp.unsqueeze(i_freqs_pha).unsqueeze(i_bins)

        amp_bins = pha_masks * amp  # this is the most memory-consuming process

        # # Batch processing to reduce maximum VRAM occupancy
        # pha_masks = self.dh_pha.fit(pha_masks, keepdims=[2, 3, 5, 6])
        # amp = self.dh_amp.fit(amp, keepdims=[2, 3, 5, 6])
        # n_chunks = len(pha_masks) // self.chunk_size
        # amp_bins = []
        # for i_chunk in range(n_chunks):
        #     start = i_chunk * self.chunk_size
        #     end = (i_chunk + 1) * self.chunk_size
        #     _amp_bins = pha_masks[start:end] * amp[start:end]
        #     amp_bins.append(_amp_bins.cpu())
        # amp_bins = torch.cat(amp_bins)
        # amp_bins = self.dh_pha.unfit(amp_bins)
        # pha_masks = self.dh_pha.unfit(pha_masks)
        # Takes mean amplitude in each bin
        amp_sums = amp_bins.sum(dim=i_time, keepdims=True).to(device)
        counts = pha_masks.sum(dim=i_time, keepdims=True)
        amp_means = amp_sums / (counts + epsilon)

        amp_probs = amp_means / (amp_means.sum(dim=-1, keepdims=True) + epsilon)

        if self.amp_prob:
            return amp_probs.detach().cpu()

        """
        matplotlib.use("TkAgg")
        fig, ax = scitex.plt.subplots(subplot_kw={'polar': True})
        yy = amp_probs[0, 0, 0, 0, 0, 0, :].detach().cpu().numpy()
        xx = ((self.pha_bin_cutoffs[1:] + self.pha_bin_cutoffs[:-1]) / 2).detach().cpu().numpy()
        ax.bar(xx, yy, width=.1)
        plt.show()
        """

        MI = (
            torch.log(torch.tensor(self.n_bins, device=device) + epsilon)
            + (amp_probs * (amp_probs + epsilon).log()).sum(dim=-1)
        ) / torch.log(torch.tensor(self.n_bins, device=device))

        # Squeeze the n_bin dimension
        MI = MI.squeeze(-1)

        # Takes mean along the n_segments dimension
        i_segment = -1
        MI = MI.mean(axis=i_segment)

        if MI.isnan().any():
            warnings.warn("NaN values detected in Modulation Index calculation.")
            # raise ValueError(
            #     "NaN values detected in Modulation Index calculation."
            # )

        return MI

    @staticmethod
    def _phase_to_masks(pha, phase_bin_cutoffs):
        n_bins = int(len(phase_bin_cutoffs) - 1)
        bin_indices = (
            (torch.bucketize(pha, phase_bin_cutoffs, right=False) - 1).clamp(
                0, n_bins - 1
            )
        ).long()
        one_hot_masks = (
            F.one_hot(
                bin_indices,
                num_classes=n_bins,
            )
            .bool()
            .to(pha.device)
        )
        return one_hot_masks


def _reshape(x, batch_size=2, n_chs=4):
    return (
        torch.tensor(x)
        .float()
        .unsqueeze(0)
        .unsqueeze(0)
        .repeat(batch_size, n_chs, 1, 1, 1)
    )


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import scitex

    # Start
    CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.gen.start(sys, plt, fig_scale=3)

    # Parameters
    FS = 512
    T_SEC = 1
    device = "cuda"

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

    m = ModulationIndex(n_bins=18, fp16=True).to(device)

    pac_scitex = m(pha.to(device), amp.to(device))

    # pac_scitex = scitex.dsp.modulation_index(pha, amp).cpu().numpy()
    i_batch, i_ch = 0, 0
    pac_scitex = pac_scitex[i_batch, i_ch].squeeze().numpy()

    # Plots
    fig = scitex.dsp.utils.pac.plot_PAC_scitex_vs_tensorpac(
        pac_scitex, pac_tp, freqs_pha, freqs_amp
    )
    # fig = plot_PAC_scitex_vs_tensorpac(pac_scitex, pac_tp, freqs_pha, freqs_amp)
    scitex.io.save(fig, CONFIG["SDIR"] + "modulation_index.png")  # plt.show()

    # Close
    scitex.gen.close(CONFIG)

# EOF

"""
/home/ywatanabe/proj/entrance/scitex/nn/_ModulationIndex.py
"""


# EOF
