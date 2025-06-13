#!./env/bin/python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-04-10 11:59:49 (ywatanabe)"


def ensure_even_len(x):
    if x.shape[-1] % 2 == 0:
        return x
    else:
        return x[..., :-1]
