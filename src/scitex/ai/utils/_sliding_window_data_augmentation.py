#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-01-24 13:56:36 (ywatanabe)"

import random


def sliding_window_data_augmentation(x, window_size_pts):
    start = random.randint(0, x.shape[-1] - window_size_pts)
    end = start + window_size_pts
    return x[..., start:end]
