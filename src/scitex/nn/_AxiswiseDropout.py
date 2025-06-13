#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-03-30 07:27:27 (ywatanabe)"

import torch
import torch.nn as nn
import torch.nn.functional as F


class AxiswiseDropout(nn.Module):
    def __init__(self, dropout_prob=0.5, dim=1):
        super(AxiswiseDropout, self).__init__()
        self.dropout_prob = dropout_prob
        self.dim = dim

    def forward(self, x):
        if self.training:
            sizes = [s if i == self.dim else 1 for i, s in enumerate(x.size())]
            dropout_mask = F.dropout(
                torch.ones(*sizes, device=x.device, dtype=x.dtype),
                self.dropout_prob,
                True,
            )

            # Expand the mask to the size of the input tensor and apply it
            return x * dropout_mask.expand_as(x)
        return x
