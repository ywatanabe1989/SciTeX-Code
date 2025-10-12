#!/usr/bin/env python3
# File: ./scitex_repo/src/scitex/stats/tests/correlation/__init__.py

"""
Correlation tests.

Tests for measuring association between continuous variables.

Available Tests
---------------
Parametric:
    test_pearson : Pearson product-moment correlation

Non-parametric (rank-based):
    test_spearman : Spearman rank correlation
    test_kendall : Kendall's tau correlation

Robust regression:
    test_theilsen : Theil-Sen robust slope estimator
"""

from ._test_pearson import test_pearson
from ._test_spearman import test_spearman
from ._test_kendall import test_kendall
from ._test_theilsen import test_theilsen

__all__ = [
    'test_pearson',
    'test_spearman',
    'test_kendall',
    'test_theilsen',
]
