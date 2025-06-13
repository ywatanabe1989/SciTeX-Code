#!/usr/bin/env python3
"""Scitex stats module."""

from ._calc_partial_corr import calc_partial_corr
from ._corr_test_multi import corr_test_multi, nocorrelation_test
from ._corr_test_wrapper import corr_test, corr_test_pearson, corr_test_spearman
from ._describe_wrapper import describe
from ._multiple_corrections import bonferroni_correction, fdr_correction, multicompair
from ._nan_stats import nan, real
from ._p2stars import p2stars
from ._p2stars_wrapper import p2stars
from ._statistical_tests import brunner_munzel_test, smirnov_grubbs

__all__ = [
    "bonferroni_correction",
    "brunner_munzel_test",
    "calc_partial_corr",
    "corr_test",
    "corr_test_multi",
    "corr_test_pearson",
    "corr_test_spearman",
    "describe",
    "fdr_correction",
    "multicompair",
    "nan",
    "nocorrelation_test",
    "p2stars",
    "p2stars",
    "real",
    "smirnov_grubbs",
]
