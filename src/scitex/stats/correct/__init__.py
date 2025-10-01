#!/usr/bin/env python3
# File: ./scitex_repo/src/scitex/stats/correct/__init__.py

"""
Multiple comparison correction methods.

Methods for controlling family-wise error rate (FWER) or false discovery rate (FDR)
when performing multiple statistical tests.
"""

from ._correct_bonferroni import correct_bonferroni
from ._correct_fdr import correct_fdr
from ._correct_holm import correct_holm
from ._correct_sidak import correct_sidak

__all__ = [
    'correct_bonferroni',
    'correct_fdr',
    'correct_holm',
    'correct_sidak',
]
