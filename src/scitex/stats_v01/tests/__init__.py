#!/usr/bin/env python3
"""Scitex tests module."""

from .__corr_test import corr_test, corr_test_pearson, corr_test_spearman
from .__corr_test_multi import corr_test as corr_test_multi
from .__corr_test_single import corr_test as corr_test_single, _corr_test_base
from ._brunner_munzel_test import brunner_munzel_test
from ._nocorrelation_test import calc_partial_corrcoef, nocorrelation_test
from ._smirnov_grubbs import smirnov_grubbs

__all__ = [
    "brunner_munzel_test",
    "calc_partial_corrcoef",
    "corr_test",
    "corr_test_multi",
    "corr_test_single",
    "corr_test_pearson",
    "corr_test_spearman",
    "_corr_test_base",
    "nocorrelation_test",
    "smirnov_grubbs",
]
