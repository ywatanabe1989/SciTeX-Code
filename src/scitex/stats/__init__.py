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
from ._two_sample_tests import ttest_ind, brunner_munzel, mannwhitneyu, ttest, bm_test
from ._additional_tests import (
    f_oneway, kruskal, chi2_contingency, shapiro, pearsonr, spearmanr,
    sem, trim_mean, probplot, norm, t, chi2, nct, multitest, anova, chisquare
)

__all__ = [
    "anova",
    "bm_test",
    "bonferroni_correction",
    "brunner_munzel",
    "brunner_munzel_test",
    "calc_partial_corr",
    "chi2",
    "chi2_contingency",
    "chisquare",
    "corr_test",
    "corr_test_multi",
    "corr_test_pearson",
    "corr_test_spearman",
    "describe",
    "f_oneway",
    "fdr_correction",
    "kruskal",
    "mannwhitneyu",
    "multicompair",
    "multitest",
    "nan",
    "nct",
    "nocorrelation_test",
    "norm",
    "p2stars",
    "pearsonr",
    "probplot",
    "real",
    "sem",
    "shapiro",
    "smirnov_grubbs",
    "spearmanr",
    "t",
    "trim_mean",
    "ttest",
    "ttest_ind",
]
