#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-26 10:30:34 (ywatanabe)"
# File: ./scitex_repo/src/scitex/dsp/utils/_zero_pad.py

THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/dsp/utils/_zero_pad.py"

import numpy as np
import torch
import torch.nn.functional as F
from ...decorators import torch_fn


def _zero_pad_1d(x, target_length):
    """Zero pad a 1D tensor to target length."""
    if not isinstance(x, torch.Tensor):
        x = torch.tensor(x)
    padding_needed = target_length - len(x)
    padding_left = padding_needed // 2
    padding_right = padding_needed - padding_left
    return F.pad(x, (padding_left, padding_right), "constant", 0)


def zero_pad(xs, dim=0):
    """Zero pad a list of arrays to the same length.

    Args:
        xs: List of tensors or arrays
        dim: Dimension to stack along

    Returns:
        Stacked tensor with zero padding
    """
    # Convert to tensors if needed
    tensors = []
    for x in xs:
        if isinstance(x, np.ndarray):
            tensors.append(torch.tensor(x))
        elif isinstance(x, torch.Tensor):
            tensors.append(x)
        else:
            tensors.append(torch.tensor(x))

    max_len = max([len(x) for x in tensors])
    return torch.stack([_zero_pad_1d(x, max_len) for x in tensors], dim=dim)


# EOF
