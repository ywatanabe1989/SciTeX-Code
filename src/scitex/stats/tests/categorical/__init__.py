#!/usr/bin/env python3
# File: ./scitex_repo/src/scitex/stats/tests/categorical/__init__.py

"""
Categorical data tests.

Tests for analyzing contingency tables and categorical associations.
"""

from ._test_chi2 import test_chi2
from ._test_fisher import test_fisher
from ._test_mcnemar import test_mcnemar
from ._test_cochran_q import test_cochran_q

__all__ = [
    'test_chi2',
    'test_fisher',
    'test_mcnemar',
    'test_cochran_q',
]
