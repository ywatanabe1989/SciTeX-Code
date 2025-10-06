#!/usr/bin/env python3
# File: ./scitex_repo/src/scitex/stats/tests/correlation/__init__.py

"""
Correlation tests.

Tests for measuring association between continuous variables.
"""

from ._test_pearson import test_pearson
from ._test_spearman import test_spearman
from ._test_kendall import test_kendall

__all__ = [
    'test_pearson',
    'test_spearman',
    'test_kendall',
]
