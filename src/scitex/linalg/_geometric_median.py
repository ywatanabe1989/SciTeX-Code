#!./env/bin/python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-09-26 19:41:01 (ywatanabe)"
# /home/ywatanabe/proj/scitex/src/scitex/linalg/_geometric_median.py


"""
This script does XYZ.
"""

import torch
from geom_median.torch import compute_geometric_median
from ..decorators import torch_fn

# @torch_fn
# def geometric_median(xx, dim=-1):
#     indi = [slice(None) for _ in range(xx.ndim)]
#     indi[dim] = slice(None)
#     xx[indi]  # how can I loop over the designated dim??

#     return compute_geometric_median(xx).median


@torch_fn
def geometric_median(xx, dim=-1):

    # Ensure dim is a positive index
    if dim < 0:
        dim = xx.ndim + dim
        dim = torch.tensor(dim).to(xx.device)

    # Create a list of slices to access all elements along each dimension
    indi = [slice(None)] * xx.ndim

    # Get the size of the dimension we want to loop over
    dim_size = xx.shape[dim]

    points = []
    # Loop over each index in the specified dimension
    for i in range(dim_size):
        indi[dim] = i
        # Set the slice for the current index in the target dimension
        slice_data = xx[tuple(indi)]  # Extract the data for the current index
        points.append(slice_data)

    out = compute_geometric_median(points).median

    return out


if __name__ == "__main__":
    # # Argument Parser
    # import argparse
    # parser = argparse.ArgumentParser(description='')
    # parser.add_argument('--var', '-v', type=int, default=1, help='')
    # parser.add_argument('--flag', '-f', action='store_true', default=False, help='')
    # args = parser.parse_args()

    # Main
    CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.gen.start(sys, plt, verbose=False)
    main()
    scitex.gen.close(CONFIG, verbose=False, notify=False)

# EOF
