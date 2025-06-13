#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2023-05-15 17:09:58 (ywatanabe)"

import torch
import torch.nn as nn
import torch.nn.functional as F
from torchsummary import summary
import scitex
import numpy as np
import scitex


class BHead(nn.Module):
    def __init__(self, n_chs_in, n_chs_out):
        super().__init__()
        self.sa = scitex.nn.SpatialAttention(n_chs_in)
        self.conv11 = nn.Conv1d(
            in_channels=n_chs_in, out_channels=n_chs_out, kernel_size=1
        )

    def forward(self, x):
        x = self.sa(x)
        x = self.conv11(x)
        return x


class BNet(nn.Module):
    def __init__(self, BNet_config, MNet_config):
        super().__init__()
        self.dummy_param = nn.Parameter(torch.empty(0))
        # N_VIRTUAL_CHS = 32
        # "n_virtual_chs":16,

        self.sc = scitex.nn.SwapChannels()
        self.dc = scitex.nn.DropoutChannels(dropout=0.01)
        self.fgc = scitex.nn.FreqGainChanger(
            BNet_config["n_bands"], BNet_config["SAMP_RATE"]
        )
        self.heads = nn.ModuleList(
            [
                BHead(n_ch, BNet_config["n_virtual_chs"]).to(self.dummy_param.device)
                for n_ch in BNet_config["n_chs_of_modalities"]
            ]
        )

        self.cgcs = [
            scitex.nn.ChannelGainChanger(n_ch)
            for n_ch in BNet_config["n_chs_of_modalities"]
        ]
        # self.cgc = scitex.nn.ChannelGainChanger(N_VIRTUAL_CHS)

        # MNet_config["n_chs"] = BNet_config["n_virtual_chs"]  # BNet_config["n_chs"] # override

        n_chs = BNet_config["n_virtual_chs"]
        self.blk1 = scitex.nn.ResNetBasicBlock(n_chs, n_chs)
        self.blk2 = scitex.nn.ResNetBasicBlock(int(n_chs / 2**1), int(n_chs / 2**1))
        self.blk3 = scitex.nn.ResNetBasicBlock(int(n_chs / 2**2), int(n_chs / 2**2))
        self.blk4 = scitex.nn.ResNetBasicBlock(int(n_chs / 2**3), int(n_chs / 2**3))
        self.blk5 = scitex.nn.ResNetBasicBlock(1, 1)
        self.blk6 = scitex.nn.ResNetBasicBlock(1, 1)
        self.blk7 = scitex.nn.ResNetBasicBlock(1, 1)

        # self.MNet = scitex.nn.MNet_1000(MNet_config)

        # self.fcs = nn.ModuleList(
        #     [
        #         nn.Sequential(
        #             # nn.Linear(N_FC_IN, config["n_fc1"]),
        #             nn.Mish(),
        #             nn.Dropout(BNet_config["d_ratio1"]),
        #             nn.Linear(BNet_config["n_fc1"], BNet_config["n_fc2"]),
        #             nn.Mish(),
        #             nn.Dropout(BNet_config["d_ratio2"]),
        #             nn.Linear(BNet_config["n_fc2"], BNet_config["n_classes_of_modalities"][i_head]),
        #         )
        #         for i_head, _ in enumerate(range(len(BNet_config["n_chs_of_modalities"])))
        #     ]
        # )

    @staticmethod
    def _znorm_along_the_last_dim(x):
        return (x - x.mean(dim=-1, keepdims=True)) / x.std(dim=-1, keepdims=True)

    def forward(self, x, i_head):
        x = self._znorm_along_the_last_dim(x)
        # x = self.sc(x)
        x = self.dc(x)
        x = self.fgc(x)
        x = self.cgcs[i_head](x)
        x = self.heads[i_head](x)

        x = self.blk1(x)
        x = F.avg_pool1d(x.transpose(1, 2), kernel_size=2).transpose(1, 2)
        x = F.avg_pool1d(x, kernel_size=2)
        x = self.blk2(x)
        x = F.avg_pool1d(x.transpose(1, 2), kernel_size=2).transpose(1, 2)
        x = F.avg_pool1d(x, kernel_size=2)
        x = self.blk3(x)
        x = F.avg_pool1d(x.transpose(1, 2), kernel_size=2).transpose(1, 2)
        x = F.avg_pool1d(x, kernel_size=2)
        x = self.blk4(x)
        x = F.avg_pool1d(x.transpose(1, 2), kernel_size=2).transpose(1, 2)
        x = F.avg_pool1d(x, kernel_size=2)

        x = self.blk5(x)
        x = F.avg_pool1d(x, kernel_size=2)
        x = self.blk6(x)
        x = F.avg_pool1d(x, kernel_size=2)
        x = self.blk7(x)
        x = F.avg_pool1d(x, kernel_size=2)

        import ipdb

        ipdb.set_trace()

        # x = self.cgc(x)
        x = self.MNet.forward_bb(x)
        x = self.fcs[i_head](x)
        return x


# BNet_config = {
#     "n_chs": 32,
#     "n_bands": 6,
#     "SAMP_RATE": 1000,
# }
BNet_config = {
    "n_bands": 6,
    "n_virtual_chs": 16,
    "SAMP_RATE": 250,
    "n_fc1": 1024,
    "d_ratio1": 0.85,
    "n_fc2": 256,
    "d_ratio2": 0.85,
}


if __name__ == "__main__":
    ## Demo data
    # MEG
    BS, N_CHS, SEQ_LEN = 16, 160, 1024
    x_MEG = torch.rand(BS, N_CHS, SEQ_LEN).cuda()
    # EEG
    BS, N_CHS, SEQ_LEN = 16, 19, 1024
    x_EEG = torch.rand(BS, N_CHS, SEQ_LEN).cuda()

    # m = scitex.nn.ResNetBasicBlock(19, 19).cuda()
    # m(x_EEG)
    # model = MNetBackBorn(scitex.nn.MNet_config).cuda()
    # model(x_MEG)
    # Model
    BNet_config["n_chs_of_modalities"] = [160, 19]
    BNet_config["n_classes_of_modalities"] = [2, 4]
    model = BNet(BNet_config, scitex.nn.MNet_config).cuda()

    # MEG
    y = model(x_MEG, 0)
    y = model(x_EEG, 1)

    # # EEG
    # y = model(x_EEG)

    y.sum().backward()
