#!/usr/bin/env python3
"""Scitex multiple module."""

from ._bonferroni_correction import bonferroni_correction, bonferroni_correction_torch
from ._fdr_correction import ArrayLike, fdr_correction
from ._multicompair import multicompair

__all__ = [
    "ArrayLike",
    "bonferroni_correction",
    "bonferroni_correction_torch",
    "fdr_correction",
    "multicompair",
]
