#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-26 10:33:30 (ywatanabe)"
# File: ./scitex_repo/src/scitex/nn/_PAC.py

THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/nn/_PAC.py"

# Imports
import sys
import warnings

import matplotlib.pyplot as plt
import scitex
import torch
import torch.nn as nn


# Functions
class PAC(nn.Module):
    def __init__(
        self,
        seq_len,
        fs,
        pha_start_hz=2,
        pha_end_hz=20,
        pha_n_bands=50,
        amp_start_hz=60,
        amp_end_hz=160,
        amp_n_bands=30,
        n_perm=None,
        trainable=False,
        in_place=True,
        fp16=False,
        amp_prob=False,
    ):
        super().__init__()

        self.fp16 = fp16
        self.n_perm = n_perm
        self.amp_prob = amp_prob
        self.trainable = trainable

        if n_perm is not None:
            if not isinstance(n_perm, int):
                raise ValueError("n_perm should be None or an integer.")

        # caps amp_end_hz
        factor = 0.8
        amp_end_hz = int(min(fs / 2 / (1 + factor) - 1, amp_end_hz))

        self.bandpass = self.init_bandpass(
            seq_len,
            fs,
            pha_start_hz=pha_start_hz,
            pha_end_hz=pha_end_hz,
            pha_n_bands=pha_n_bands,
            amp_start_hz=amp_start_hz,
            amp_end_hz=amp_end_hz,
            amp_n_bands=amp_n_bands,
            fp16=fp16,
            trainable=trainable,
        )

        self.hilbert = scitex.nn.Hilbert(seq_len, dim=-1, fp16=fp16)

        self.Modulation_index = scitex.nn.ModulationIndex(
            n_bins=18,
            fp16=fp16,
            amp_prob=amp_prob,
        )

        # Data Handlers
        self.dh_pha = scitex.gen.DimHandler()
        self.dh_amp = scitex.gen.DimHandler()

    def forward(self, x):
        """x.shape: (batch_size, n_chs, seq_len) or (batch_size, n_chs, n_segments, seq_len)"""

        with torch.set_grad_enabled(bool(self.trainable)):
            x = self._ensure_4d_input(x)
            # (batch_size, n_chs, n_segments, seq_len)

            batch_size, n_chs, n_segments, seq_len = x.shape

            x = x.reshape(batch_size * n_chs, n_segments, seq_len)
            # (batch_size * n_chs, n_segments, seq_len)

            x = self.bandpass(x, edge_len=0)
            # (batch_size*n_chs, n_segments, n_pha_bands + n_amp_bands, seq_len)

            x = self.hilbert(x)
            # (batch_size*n_chs, n_segments, n_pha_bands + n_amp_bands, seq_len, pha + amp)

            x = x.reshape(batch_size, n_chs, *x.shape[1:])
            # (batch_size, n_chs, n_segments, n_pha_bands + n_amp_bands, seq_len, pha + amp)

            x = x.transpose(2, 3)
            # (batch_size, n_chs, n_pha_bands + n_amp_bands, n_segments, pha + amp)

            if self.fp16:
                x = x.half()

            pha = x[:, :, : len(self.PHA_MIDS_HZ), :, :, 0]
            # (batch_size, n_chs, n_freqs_pha, n_segments, sequence_length)

            amp = x[:, :, -len(self.AMP_MIDS_HZ) :, :, :, 1]
            # (batch_size, n_chs, n_freqs_amp, n_segments, sequence_length)()

            edge_len = int(pha.shape[-1] // 8)

            pha = pha[..., edge_len:-edge_len].half()
            amp = amp[..., edge_len:-edge_len].half()

            pac_or_amp_prob = self.Modulation_index(pha, amp)  # .squeeze()
            # print(pac_or_amp_prob.shape)
            # pac_or_amp_prob = pac_or_amp_prob.squeeze()

            if self.n_perm is None:
                return pac_or_amp_prob
            else:
                return self.to_z_using_surrogate(pha, amp, pac_or_amp_prob)

    def to_z_using_surrogate(self, pha, amp, observed):
        surrogates = self.generate_surrogates(pha, amp)
        mm = surrogates.mean(dim=2).to(observed.device)
        ss = surrogates.std(dim=2).to(observed.device)
        return (observed - mm) / (ss + 1e-5)

        # if self.amp_prob:
        #     amp_prob = self.Modulation_index(pha, amp).squeeze()
        #     amp_prob.shape  # torch.Size([2, 8, 50, 50, 3, 18])
        #     pac_surrogates = self.generate_surrogates(pha, amp)
        #     # torch.Size([2, 8, 3, 50, 50, 3, 18])
        #     __import__("ipdb").set_trace()
        #     return amp_prob

        # elif not self.amp_prob:
        #     pac = self.Modulation_index(pha, amp).squeeze() # torch.Size([2, 8, 50, 50])

        # if self.n_perm is not None:
        #     pac_surrogates = self.generate_surrogates(pha, amp)
        #     # torch.Size([2, 8, 3, 50, 50]) # self.amp_prob = False
        #     __import__("ipdb").set_trace()
        #     mm = pac_surrogates.mean(dim=2).to(pac.device)
        #     ss = pac_surrogates.std(dim=2).to(pac.device)
        #     pac_z = (pac - mm) / (ss + 1e-5)
        #     return pac_z

        # return pac

    def generate_surrogates(self, pha, amp, bs=1):
        # Shape of pha: [batch_size, n_chs, n_freqs_pha, n_segments, sequence_length]
        batch_size, n_chs, n_freqs_pha, n_segments, seq_len = pha.shape
        _, _, n_freqs_amp, _, _ = amp.shape

        # cut and shuffle
        cut_points = torch.randint(seq_len, (self.n_perm,), device=pha.device)
        ranges = torch.arange(seq_len, device=pha.device)
        indices = cut_points.unsqueeze(0) - ranges.unsqueeze(1)

        pha = pha[..., indices]
        amp = amp.unsqueeze(-1).expand(-1, -1, -1, -1, -1, self.n_perm)

        pha = self.dh_pha.fit(pha, keepdims=[2, 3, 4])
        amp = self.dh_amp.fit(amp, keepdims=[2, 3, 4])

        if self.fp16:
            pha = pha.half()
            amp = amp.half()

        # print("\nCalculating surrogate PAC values...")

        surrogate_pacs = []
        n_batches = (len(pha) + bs - 1) // bs
        device = "cuda"
        with torch.no_grad():
            # ########################################
            # # fixme
            # pha = pha.to(device)
            # amp = amp.to(device)
            # ########################################

            for i_batch in range(n_batches):
                start = i_batch * bs
                end = min((i_batch + 1) * bs, pha.shape[0])

                _pha = pha[start:end].unsqueeze(1).to(device)  # n_chs = 1
                _amp = amp[start:end].unsqueeze(1).to(device)  # n_chs = 1

                _surrogate_pacs = self.Modulation_index(_pha, _amp).cpu()
                surrogate_pacs.append(_surrogate_pacs)

                # # Optionally clear cache if memory is an issue
                # torch.cuda.empty_cache()

        torch.cuda.empty_cache()
        surrogate_pacs = torch.vstack(surrogate_pacs).squeeze()
        surrogate_pacs = self.dh_pha.unfit(surrogate_pacs)

        return surrogate_pacs

    def init_bandpass(
        self,
        seq_len,
        fs,
        pha_start_hz=2,
        pha_end_hz=20,
        pha_n_bands=50,
        amp_start_hz=60,
        amp_end_hz=160,
        amp_n_bands=30,
        trainable=False,
        fp16=False,
    ):

        # A static, gen purpose BandPassFilter
        if not trainable:
            # First, bands definitions for phase and amplitude are declared
            self.BANDS_PHA = self.calc_bands_pha(
                start_hz=pha_start_hz,
                end_hz=pha_end_hz,
                n_bands=pha_n_bands,
            )
            self.BANDS_AMP = self.calc_bands_amp(
                start_hz=amp_start_hz,
                end_hz=amp_end_hz,
                n_bands=amp_n_bands,
            )
            bands_all = torch.vstack([self.BANDS_PHA, self.BANDS_AMP])

            # Instanciation of the static bandpass filter module
            self.bandpass = scitex.nn.BandPassFilter(
                bands_all,
                fs,
                seq_len,
                fp16=fp16,
            )
            self.PHA_MIDS_HZ = self.BANDS_PHA.mean(-1)
            self.AMP_MIDS_HZ = self.BANDS_AMP.mean(-1)

        # A trainable BandPassFilter specifically for PAC calculation. Bands will be optimized.
        elif trainable:
            self.bandpass = scitex.nn.DifferentiableBandPassFilter(
                seq_len,
                fs,
                fp16=fp16,
                pha_low_hz=pha_start_hz,
                pha_high_hz=pha_end_hz,
                pha_n_bands=pha_n_bands,
                amp_low_hz=amp_start_hz,
                amp_high_hz=amp_end_hz,
                amp_n_bands=amp_n_bands,
            )
            self.PHA_MIDS_HZ = self.bandpass.pha_mids
            self.AMP_MIDS_HZ = self.bandpass.amp_mids

        return self.bandpass

    @staticmethod
    def calc_bands_pha(start_hz=2, end_hz=20, n_bands=100):
        start_hz = start_hz if start_hz is not None else 2
        end_hz = end_hz if end_hz is not None else 20
        mid_hz = torch.linspace(start_hz, end_hz, n_bands)
        return torch.cat(
            (
                mid_hz.unsqueeze(1) - mid_hz.unsqueeze(1) / 4.0,
                mid_hz.unsqueeze(1) + mid_hz.unsqueeze(1) / 4.0,
            ),
            dim=1,
        )

    @staticmethod
    def calc_bands_amp(start_hz=30, end_hz=160, n_bands=100):
        start_hz = start_hz if start_hz is not None else 30
        end_hz = end_hz if end_hz is not None else 160
        mid_hz = torch.linspace(start_hz, end_hz, n_bands)
        return torch.cat(
            (
                mid_hz.unsqueeze(1) - mid_hz.unsqueeze(1) / 8.0,
                mid_hz.unsqueeze(1) + mid_hz.unsqueeze(1) / 8.0,
            ),
            dim=1,
        )

    @staticmethod
    def _ensure_4d_input(x):
        if x.ndim != 4:
            message = f"Input tensor must be 4D with the shape (batch_size, n_chs, n_segments, seq_len). Received shape: {x.shape}"

        if x.ndim == 3:
            # warnings.warn(
            #     "'n_segments' was determined to be 1, assuming your input is (batch_size, n_chs, seq_len).",
            #     UserWarning,
            # )
            x = x.unsqueeze(-2)

        if x.ndim != 4:
            raise ValueError(message)

        return x


if __name__ == "__main__":
    # Start
    CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.session.start(sys, plt)

    ts = scitex.gen.TimeStamper()

    # Parameters
    FS = 512
    T_SEC = 8
    PLOT = False
    fp16 = True
    trainable = False
    n_perm = 3
    in_place = True
    amp_prob = True

    # Demo Signal
    xx, tt, fs = scitex.dsp.demo_sig(
        batch_size=2,
        n_chs=8,
        n_segments=3,
        fs=FS,
        t_sec=T_SEC,
        sig_type="tensorpac",
        # sig_type="pac",
    )
    xx = torch.tensor(xx).cuda()
    xx.requires_grad = False
    # (2, 8, 2, 4096)

    # PAC object initialization
    ts("PAC initialization starts")
    m = PAC(
        xx.shape[-1],
        fs,
        pha_start_hz=2,
        pha_end_hz=20,
        pha_n_bands=50,
        amp_start_hz=60,
        amp_end_hz=160,
        amp_n_bands=50,
        fp16=fp16,
        trainable=trainable,
        n_perm=n_perm,
        in_place=in_place,
        amp_prob=amp_prob,
    ).cuda()
    ts("PAC initialization ends")

    # PAC calculation
    ts("PAC calculation starts")
    pac = m(xx)
    ts("PAC calculation ends")

    """
    amp_prob = m(xx)
    amp_prob = amp_prob.reshape(-1, amp_prob.shape[-1])
    xx = m.Modulation_index.pha_bin_centers
    plt.bar(xx, amp_prob[0])
    """

    scitex.gen.print_block(f"PAC calculation time: {ts.delta(-1,-2):.3f} sec", c="yellow")
    # 0.17 sec
    scitex.gen.print_block(
        f"x.shape: {xx.shape}"
        f"\nfp16: {fp16}"
        f"\ntrainable: {trainable}"
        f"\nn_perm: {n_perm}"
        f"\nin_place: {in_place}"
    )

    # # Plots
    # if PLOT:
    #     pac = pac.detach().cpu().numpy()
    #     fig, ax = scitex.plt.subplots()
    #     ax.imshow2d(pac[0, 0], cbar_label="PAC value [zscore]")
    #     ax.set_ticks(
    #         x_vals=m.PHA_MIDS_HZ,
    #         x_ticks=np.linspace(m.PHA_MIDS_HZ[0], m.PHA_MIDS_HZ[-1], 4),
    #         y_vals=m.AMP_MIDS_HZ,
    #         y_ticks=np.linspace(m.AMP_MIDS_HZ[0], m.AMP_MIDS_HZ[-1], 4),
    #     )
    #     ax.set_xyt(
    #         "Frequency for phase [Hz]",
    #         "Amplitude for phase [Hz]",
    #         "PAC values",
    #     )
    #     plt.show()


# EOF

"""
/home/ywatanabe/proj/entrance/scitex/dsp/nn/_PAC.py
"""

# # close
# fig, axes = scitex.plt.subplots(ncols=2)
# axes[0].imshow2d(pac_scitex[i_batch, i_ch])
# axes[1].imshow2d(pac_tp)
# scitex.io.save(fig, CONFIG["SDIR"] + "pac.png")
# import numpy as np
# np.corrcoef(pac_scitex[i_batch, i_ch], pac_tp)[0, 1]
# import matplotlib

# plt.close("all")
# matplotlib.use("TkAgg")
# plt.scatter(pac_scitex[i_batch, i_ch].reshape(-1), pac_tp.reshape(-1))
# plt.show()


# EOF
