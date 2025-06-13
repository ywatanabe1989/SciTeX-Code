#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-03-30 07:26:35 (ywatanabe)"

import torch.nn as nn


class TransposeLayer(nn.Module):
    def __init__(
        self,
        axis1,
        axis2,
    ):
        super().__init__()
        self.axis1 = axis1
        self.axis2 = axis2

    def forward(self, x):
        return x.transpose(self.axis1, self.axis2)
