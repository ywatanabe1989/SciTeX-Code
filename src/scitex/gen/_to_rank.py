#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-02 13:05:47 (ywatanabe)"
# File: ./scitex_repo/src/scitex/gen/_to_rank.py
#!./env/bin/python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-08-29 22:10:06 (ywatanabe)"
# ./src/scitex/gen/data_processing/_to_rank.py

import torch

# from .._converters import
from ..decorators import torch_fn


@torch_fn
def to_rank(tensor, method="average"):
    sorted_tensor, indices = torch.sort(tensor)
    ranks = torch.empty_like(tensor)
    ranks[indices] = (
        torch.arange(len(tensor), dtype=tensor.dtype, device=tensor.device) + 1
    )

    if method == "average":
        ranks = ranks.float()
        ties = torch.nonzero(sorted_tensor[1:] == sorted_tensor[:-1])
        for i in range(len(ties)):
            start = ties[i]
            end = start + 1
            while (
                end < len(sorted_tensor) and sorted_tensor[end] == sorted_tensor[start]
            ):
                end += 1
            ranks[indices[start:end]] = ranks[indices[start:end]].mean()

    return ranks


# EOF
