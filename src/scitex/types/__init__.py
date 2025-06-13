#!/usr/bin/env python3
"""Scitex types module."""

from ._ArrayLike import ArrayLike, is_array_like
from ._ColorLike import ColorLike
from ._is_listed_X import is_list_of_type, is_listed_X

__all__ = [
    "ArrayLike",
    "ColorLike",
    "is_array_like",
    "is_list_of_type",
    "is_listed_X",
]
