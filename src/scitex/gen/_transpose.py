#!./env/bin/python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-08-24 09:47:16 (ywatanabe)"
# ./src/scitex/gen/_transpose.py

from ..decorators import numpy_fn
import numpy as np


@numpy_fn
def transpose(arr_like, src_dims, tgt_dims):
    """
    Transpose an array-like object based on source and target dimensions.

    Parameters
    ----------
    arr_like : np.array
        The input array to be transposed.
    src_dims : np.array
        List of dimension names in the source order.
    tgt_dims : np.array
        List of dimension names in the target order.

    Returns
    -------
    np.array
        The transposed array.

    Raises
    ------
    AssertionError
        If source and target dimensions don't contain the same elements.
    """
    assert set(src_dims) == set(
        tgt_dims
    ), "Source and target dimensions must contain the same elements"
    return arr_like.transpose(*[np.where(src_dims == dim)[0][0] for dim in tgt_dims])
