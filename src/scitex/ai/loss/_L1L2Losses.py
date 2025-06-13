#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-07 18:53:03 (ywatanabe)"
# File: ./scitex_repo/src/scitex/ai/loss/_L1L2Losses.py

import torch


def l1(model, lambda_l1=0.01):
    lambda_l1 = torch.tensor(lambda_l1)
    l1 = torch.tensor(0.0).cuda()
    for param in model.parameters():  # fixme; is this OK?
        l1 += torch.abs(param).sum()
    return l1


def l2(model, lambda_l2=0.01):
    lambda_l2 = torch.tensor(lambda_l2)
    l2 = torch.tensor(0.0).cuda()
    for param in model.parameters():  # fixme; is this OK?
        l2 += torch.norm(param).sum()
    return l2


def elastic(model, alpha=1.0, l1_ratio=0.5):
    assert 0 <= l1_ratio <= 1

    L1 = l1(model)
    L2 = l2(model)

    return alpha * (l1_ratio * L1 + (1 - l1_ratio) * L2)


# EOF
