#!/usr/bin/env python3
"""Linear algebra utilities module for scitex."""

from ._distance import euclidean_distance, cdist, edist
from ._geometric_median import geometric_median
from ._misc import cosine, nannorm, rebase_a_vec, three_line_lengths_to_coords

__all__ = [
    "euclidean_distance",
    "cdist",
    "edist", 
    "geometric_median",
    "cosine",
    "nannorm",
    "rebase_a_vec",
    "three_line_lengths_to_coords",
]
