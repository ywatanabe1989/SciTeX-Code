#!/usr/bin/env python3
# File: ./scitex_repo/src/scitex/stats/tests/nonparametric/__init__.py

"""
Non-parametric statistical tests.

Distribution-free tests that don't assume normality.
Robust to outliers and suitable for ordinal data.
"""

from ._test_brunner_munzel import test_brunner_munzel
from ._test_wilcoxon import test_wilcoxon
from ._test_kruskal import test_kruskal
from ._test_mannwhitneyu import test_mannwhitneyu
from ._test_friedman import test_friedman

__all__ = [
    'test_brunner_munzel',
    'test_wilcoxon',
    'test_kruskal',
    'test_mannwhitneyu',
    'test_friedman',
]
