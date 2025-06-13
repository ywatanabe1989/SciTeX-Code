#!/usr/bin/env python3

import numpy as np
import scipy.stats as stats
from statsmodels.stats.multicomp import MultiComparison


def multicompair(data, labels, testfunc=None):
    # https://pythonhealthcare.org/2018/04/13/55-statistics-multi-comparison-with-tukeys-test-and-the-holm-bonferroni-method/
    _labels = labels.copy()
    # Set up the data for comparison (creates a specialised object)
    for i_labels in range(len(_labels)):
        _labels[i_labels] = [_labels[i_labels] for i_data in range(len(data[i_labels]))]

    data, _labels = np.hstack(data), np.hstack(_labels)
    MultiComp = MultiComparison(data, _labels)

    if testfunc is not None:
        # print(MultiComp.allpairtest(testfunc, mehotd='bonf', pvalidx=1))
        return MultiComp.allpairtest(testfunc, method="bonf", pvalidx=1)
    else:
        # print(MultiComp.tukeyhsd().summary())
        return MultiComp.tukeyhsd().summary()


# t_statistic, p_value = scipy.stats.ttest_ind(data1, data2, equal_var=False) # Welch's t test
# W_statistic, p_value = scipy.stats.brunnermunzel(data1, data2)
# H_statistic, p_value = scipy.stats.kruskal(*data) # one-way ANOVA on RANKs
