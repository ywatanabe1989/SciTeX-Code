#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-20 00:29:47 (ywatanabe)"
# File: ./scitex_repo/src/scitex/ai/layer/_Pass.py

THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/ai/layer/_Pass.py"

import torch.nn as nn


class Pass(nn.Module):
    def __init__(
        self,
    ):
        super().__init__()

    def forward(self, x):
        return x


# EOF
