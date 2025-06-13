#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2023-05-04 21:50:22 (ywatanabe)"

import torch
import torch.nn as nn
import torch.nn.functional as F
from torchsummary import summary
import scitex
import numpy as np
import random


class DropoutChannels(nn.Module):
    def __init__(self, dropout=0.5):
        super().__init__()
        self.dropout = nn.Dropout(p=dropout)

    def forward(self, x):
        """x: [batch_size, n_chs, seq_len]"""
        if self.training:
            orig_chs = torch.arange(x.shape[1])

            indi_orig = self.dropout(torch.ones(x.shape[1])).bool()
            chs_to_shuffle = orig_chs[~indi_orig]

            x[:, chs_to_shuffle] = torch.randn(x[:, chs_to_shuffle].shape).to(x.device)

            # rand_chs = random.sample(list(np.array(chs_to_shuffle)), len(chs_to_shuffle))

            # swapped_chs = orig_chs.clone()
            # swapped_chs[~indi_orig] = torch.LongTensor(rand_chs)

            # x = x[:, swapped_chs.long(), :]

        return x


if __name__ == "__main__":
    ## Demo data
    bs, n_chs, seq_len = 16, 360, 1000
    x = torch.rand(bs, n_chs, seq_len)

    dc = DropoutChannels(dropout=0.1)
    print(dc(x).shape)  # [16, 19, 1000]

    # sb = SubjectBlock(n_chs=n_chs)
    # print(sb(x, s).shape) # [16, 270, 1000]

    # summary(sb, x, s)
