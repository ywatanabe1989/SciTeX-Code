#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-04 02:58:04 (ywatanabe)"
# File: ./scitex_repo/src/scitex/linalg/_distance.py

import numpy as np
import scipy.spatial.distance as _distance

from ..decorators._numpy_fn import numpy_fn
from ..decorators._wrap import wrap


@numpy_fn
def euclidean_distance(uu, vv, axis=0):
    """
    Compute the Euclidean distance between two arrays along the specified axis.

    Parameters
    ----------
    uu : array_like
        First input array.
    vv : array_like
        Second input array.
    axis : int, optional
        Axis along which to compute the distance. Default is 0.

    Returns
    -------
    array_like
        Euclidean distance array along the specified axis.
    """
    uu, vv = np.atleast_1d(uu), np.atleast_1d(vv)

    if uu.shape[axis] != vv.shape[axis]:
        raise ValueError(f"Shape along axis {axis} must match")

    uu = np.moveaxis(uu, axis, 0)
    vv = np.moveaxis(vv, axis, 0)

    uu_tgt_shape = [uu.shape[0]] + list(uu.shape[1:]) + [1] * (vv.ndim - 1)
    vv_tgt_shape = [vv.shape[0]] + [1] * (uu.ndim - 1) + list(vv.shape[1:])

    uu_reshaped = uu.reshape(uu_tgt_shape)
    vv_reshaped = vv.reshape(vv_tgt_shape)

    diff = uu_reshaped - vv_reshaped
    euclidean_dist = np.sqrt(np.sum(diff**2, axis=axis))
    return euclidean_dist


@wrap
def cdist(*args, **kwargs):
    return _distance.cdist(*args, **kwargs)


edist = euclidean_distance

# Optionally, manually copy the original docstring
# euclidean_distance.__doc__ = _distance.euclidean.__doc__
cdist.__doc__ = _distance.cdist.__doc__


# EOF
