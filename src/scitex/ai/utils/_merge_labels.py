#!/usr/bin/env python3

import scitex
import numpy as np

# y1, y2 = T_tra, M_tra
# def merge_labels(y1, y2):
#     y = [str(z1) + "-" + str(z2) for z1, z2 in zip(y1, y2)]
#     conv_d = {z: i for i, z in enumerate(np.unique(y))}
#     y = [conv_d[z] for z in y]
#     return y


def merge_labels(*ys, to_int=False):
    if not len(ys) > 1:  # Check if more than two arguments are passed
        return ys[0]
    else:
        y = [scitex.gen.connect_nums(zs) for zs in zip(*ys)]
        if to_int:
            conv_d = {z: i for i, z in enumerate(np.unique(y))}
            y = [conv_d[z] for z in y]
        return np.array(y)
