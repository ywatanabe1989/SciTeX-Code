#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-04-11 21:50:09 (ywatanabe)"

import torch
import torch.nn as nn


class PSD(nn.Module):
    def __init__(self, sample_rate, prob=False, dim=-1):
        super(PSD, self).__init__()
        self.sample_rate = sample_rate
        self.dim = dim
        self.prob = prob

    def forward(self, signal):

        is_complex = signal.is_complex()
        if is_complex:
            signal_fft = torch.fft.fft(signal, dim=self.dim)
            freqs = torch.fft.fftfreq(signal.size(self.dim), 1 / self.sample_rate).to(
                signal.device
            )

        else:
            signal_fft = torch.fft.rfft(signal, dim=self.dim)
            freqs = torch.fft.rfftfreq(signal.size(self.dim), 1 / self.sample_rate).to(
                signal.device
            )

        power_spectrum = torch.abs(signal_fft) ** 2
        power_spectrum = power_spectrum / signal.size(self.dim)

        psd = power_spectrum * (1.0 / self.sample_rate)

        # To probability if specified
        if self.prob:
            psd /= psd.sum(dim=self.dim, keepdims=True)

        return psd, freqs
