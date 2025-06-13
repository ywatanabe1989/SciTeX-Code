#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-04-01 18:14:44 (ywatanabe)"

import math

import torch
import torch.nn as nn
import torch.nn.functional as F
import torchaudio.transforms as T


class GaussianFilter(nn.Module):
    def __init__(self, radius, sigma=None):
        super().__init__()
        if sigma is None:
            sigma = radius / 2
        self.radius = radius
        self.register_buffer("kernel", self.gen_kernel_1d(radius, sigma=sigma))

    @staticmethod
    def gen_kernel_1d(radius, sigma=None):
        if sigma is None:
            sigma = radius / 2

        kernel_size = 2 * radius + 1
        x = torch.arange(kernel_size).float() - radius

        kernel = torch.exp(-0.5 * (x / sigma) ** 2)
        kernel = kernel / (sigma * math.sqrt(2 * math.pi))
        kernel = kernel / torch.sum(kernel)

        return kernel.unsqueeze(0).unsqueeze(0)

    def forward(self, x):
        """x.shape: (batch_size, n_chs, seq_len)"""

        if x.ndim == 1:
            x = x.unsqueeze(0).unsqueeze(0)
        elif x.ndim == 2:
            x = x.unsqueeze(1)

        channels = x.size(1)
        kernel = self.kernel.expand(channels, 1, -1).to(x.device).to(x.dtype)

        return torch.nn.functional.conv1d(
            x, kernel, padding=self.radius, groups=channels
        )
