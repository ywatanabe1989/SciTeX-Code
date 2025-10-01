#!/usr/bin/env python3
# File: ./scitex_repo/src/scitex/stats/tests/parametric/__init__.py

"""
Parametric statistical tests.

Tests that assume normal distribution and/or specific distributional properties.
"""

from ._test_ttest import (
    test_ttest_ind,
    test_ttest_rel,
    test_ttest_1samp
)

from ._test_anova import test_anova
from ._test_anova_rm import test_anova_rm
from ._test_anova_2way import test_anova_2way

__all__ = [
    'test_ttest_ind',
    'test_ttest_rel',
    'test_ttest_1samp',
    'test_anova',
    'test_anova_rm',
    'test_anova_2way',
]
