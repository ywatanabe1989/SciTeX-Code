#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2023-04-23 11:02:34 (ywatanabe)"

import torch
import torch.nn as nn
import torch.nn.functional as F
from torchsummary import summary
import scitex
import numpy as np
import julius

# BANDS_LIM_HZ_DICT = {
#     "delta": [0.5, 4],
#     "theta": [4, 8],
#     "lalpha": [8, 10],
#     "halpha": [10, 13],
#     "beta": [13, 32],
#     "gamma": [32, 75],
# }


# class FreqDropout(nn.Module):
#     def __init__(self, n_bands, samp_rate, dropout_ratio=0.5):
#         super().__init__()
#         self.dropout = nn.Dropout(p=0.5)
#         self.n_bands = n_bands
#         self.samp_rate = samp_rate
#         # self.
#         self.register_buffer("ones", torch.ones(self.n_bands))

#     def forward(self, x):
#         """x: [batch_size, n_chs, seq_len]"""
#         x = julius.bands.split_bands(x, self.samp_rate, n_bands=self.n_bands)

#         gains_orig = x.reshape(len(x), -1).abs().sum(axis=-1)
#         sum_gains_orig = gains_orig.sum()

#         # use_freqs = self.dropout(torch.ones(self.n_bands)).bool().long()
#         use_freqs = self.dropout(self.ones) / 2 # .bool().long()

#         gains = gains_orig * use_freqs
#         sum_gains = gains.sum()
#         gain_ratio = sum_gains / sum_gains_orig


#         x *= use_freqs.unsqueeze(-1).unsqueeze(-1).unsqueeze(-1)
#         x /= gain_ratio
#         x = x.sum(axis=0)

#         return x


class FreqGainChanger(nn.Module):
    def __init__(self, n_bands, samp_rate, dropout_ratio=0.5):
        super().__init__()
        self.dropout = nn.Dropout(p=0.5)
        self.n_bands = n_bands
        self.samp_rate = samp_rate
        # self.register_buffer("ones", torch.ones(self.n_bands))

    def forward(self, x):
        """x: [batch_size, n_chs, seq_len]"""
        if self.training:
            x = julius.bands.split_bands(x, self.samp_rate, n_bands=self.n_bands)
            freq_gains = (
                torch.rand(self.n_bands)
                .unsqueeze(-1)
                .unsqueeze(-1)
                .unsqueeze(-1)
                .to(x.device)
                + 0.5
            )
            freq_gains = F.softmax(freq_gains, dim=0)
            x = (x * freq_gains).sum(axis=0)

        return x
        # import ipdb; ipdb.set_trace()

        # gains_orig = x.reshape(len(x), -1).abs().sum(axis=-1)
        # sum_gains_orig = gains_orig.sum()

        # # use_freqs = self.dropout(torch.ones(self.n_bands)).bool().long()
        # use_freqs = self.dropout(self.ones) / 2 # .bool().long()

        # gains = gains_orig * use_freqs
        # sum_gains = gains.sum()
        # gain_ratio = sum_gains / sum_gains_orig

        # x *= use_freqs.unsqueeze(-1).unsqueeze(-1).unsqueeze(-1)
        # x /= gain_ratio
        # x = x.sum(axis=0)

        # return x


if __name__ == "__main__":
    # Parameters
    N_BANDS = 10
    SAMP_RATE = 1000
    BS, N_CHS, SEQ_LEN = 16, 360, 1000

    # Demo data
    x = torch.rand(BS, N_CHS, SEQ_LEN).cuda()

    # Feedforward
    fgc = FreqGainChanger(N_BANDS, SAMP_RATE).cuda()
    # fd.eval()
    y = fgc(x)
    y.sum().backward()
