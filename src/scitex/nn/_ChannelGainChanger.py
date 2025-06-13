#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2023-04-23 11:02:45 (ywatanabe)"

import torch
import torch.nn as nn
import torch.nn.functional as F
from torchsummary import summary
import scitex
import numpy as np


class ChannelGainChanger(nn.Module):
    def __init__(
        self,
        n_chs,
    ):
        super().__init__()
        self.n_chs = n_chs

    def forward(self, x):
        """x: [batch_size, n_chs, seq_len]"""
        if self.training:
            ch_gains = (
                torch.rand(self.n_chs).unsqueeze(0).unsqueeze(-1).to(x.device) + 0.5
            )
            ch_gains = F.softmax(ch_gains, dim=1)
            x *= ch_gains

        return x


if __name__ == "__main__":
    ## Demo data
    bs, n_chs, seq_len = 16, 360, 1000
    x = torch.rand(bs, n_chs, seq_len)

    cgc = ChGainChanger(n_chs)
    print(cgc(x).shape)  # [16, 19, 1000]

    # sb = SubjectBlock(n_chs=n_chs)
    # print(sb(x, s).shape) # [16, 270, 1000]

    # summary(sb, x, s)
