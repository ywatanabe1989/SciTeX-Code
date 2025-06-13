#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2023-05-15 16:46:54 (ywatanabe)"

import torch
import torch.nn as nn
from torchsummary import summary


class ResNet1D(nn.Module):
    """
    A representative convolutional neural network for signal classification tasks.
    """

    def __init__(self, n_chs=19, n_out=10, n_blks=5):
        super().__init__()

        # Parameters
        N_CHS = n_chs
        _N_FILTS_PER_CH = 4
        N_FILTS = N_CHS * _N_FILTS_PER_CH
        N_BLKS = n_blks

        # Convolutional layers
        self.res_conv_blk_layers = nn.Sequential(
            ResNetBasicBlock(N_CHS, N_FILTS),
            *[ResNetBasicBlock(N_FILTS, N_FILTS) for _ in range(N_BLKS - 1)],
        )

        # ## FC layer
        # self.fc = nn.Sequential(
        #     nn.Linear(N_FILTS, 64),
        #     nn.ReLU(),
        #     nn.Dropout(p=0.5),
        #     nn.Linear(64, 32),
        #     nn.ReLU(),
        #     nn.Dropout(p=0.5),
        #     nn.Linear(32, n_out),
        # )

    def forward(self, x):
        x = self.res_conv_blk_layers(x)
        # x = x.mean(axis=-1)
        # x = self.fc(x)
        return x


class ResNetBasicBlock(nn.Module):
    """The basic block of the ResNet1D model"""

    def __init__(self, in_chs, out_chs):
        super(ResNetBasicBlock, self).__init__()
        self.in_chs = in_chs
        self.out_chs = out_chs

        self.conv7 = self.conv_k(in_chs, out_chs, k=7, p=3)
        self.bn7 = nn.BatchNorm1d(out_chs)
        self.activation7 = nn.ReLU()

        self.conv5 = self.conv_k(out_chs, out_chs, k=5, p=2)
        self.bn5 = nn.BatchNorm1d(out_chs)
        self.activation5 = nn.ReLU()

        self.conv3 = self.conv_k(out_chs, out_chs, k=3, p=1)
        self.bn3 = nn.BatchNorm1d(out_chs)
        self.activation3 = nn.ReLU()

        self.expansion_conv = self.conv_k(in_chs, out_chs, k=1, p=0)

        self.bn = nn.BatchNorm1d(out_chs)
        self.activation = nn.ReLU()

    @staticmethod
    def conv_k(in_chs, out_chs, k=1, s=1, p=1):
        """Build size k kernel's convolution layer with padding"""
        return nn.Conv1d(
            in_chs, out_chs, kernel_size=k, stride=s, padding=p, bias=False
        )

    def forward(self, x):
        residual = x

        x = self.conv7(x)
        x = self.bn7(x)
        x = self.activation7(x)

        x = self.conv5(x)
        x = self.bn5(x)
        x = self.activation5(x)

        x = self.conv3(x)
        x = self.bn3(x)
        x = self.activation3(x)

        if self.in_chs != self.out_chs:
            residual = self.expansion_conv(residual)
        residual = self.bn(residual)

        x = x + residual
        x = self.activation(x)

        return x


if __name__ == "__main__":
    import sys

    sys.path.append("./DEAP/")
    import utils

    # Demo data
    bs, n_chs, seq_len = 16, 32, 8064
    Xb = torch.rand(bs, n_chs, seq_len)

    model = ResNet1D(
        n_chs=n_chs,
        n_out=4,
    )  # utils.load_yaml("./config/global.yaml")["EMOTIONS"]
    y = model(Xb)  # 16,4
    summary(model, Xb)
