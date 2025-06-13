#!/usr/bin/env python3
# Time-stamp: "2021-09-25 15:39:51 (ylab)"

import numpy as np
import torch
import scitex


def bonferroni_correction(pval, alpha=0.05):
    # https://github.com/mne-tools/mne-python/blob/main/mne/stats/multi_comp.py
    """P-value correction with Bonferroni method.

    Parameters
    ----------
    pval : array_like
        Set of p-values of the individual tests.
    alpha : float
        Error rate.

    Returns
    -------
    reject : array, bool
        True if a hypothesis is rejected, False if not.
    pval_corrected : array
        P-values adjusted for multiple hypothesis testing to limit FDR.
    """
    pval = np.asarray(pval)
    pval_corrected = pval * float(pval.size)
    # p-values must not be larger than 1.
    pval_corrected = pval_corrected.clip(max=1.0)
    reject = pval_corrected < alpha
    return reject, pval_corrected


def bonferroni_correction_torch(pvals, alpha=0.05):
    """P-value correction with Bonferroni method.

    Parameters
    ----------
    pvals : array_like
        Set of p-values of the individual tests.
    alpha : float
        Error rate.

    Returns
    -------
    reject : array, bool
        True if a hypothesis is rejected, False if not.
    pvals_corrected : array
        P-values adjusted for multiple hypothesis testing to limit FDR.
    """
    pvals = torch.tensor(pvals)
    pvals_corrected = pvals * torch.tensor(pvals.size()).float()
    # p-values must not be larger than 1.
    pvals_corrected = pvals_corrected.clip(max=1.0)
    reject = pvals_corrected < alpha
    return reject, pvals_corrected


if __name__ == "__main__":
    pvals_npy = np.array([0.02, 0.03, 0.05])
    pvals_torch = torch.tensor(np.array([0.02, 0.03, 0.05]))

    reject, pvals_corrected = bonferroni_correction(pvals_npy, alpha=0.05)

    reject_torch, pvals_corrected_torch = bonferroni_correction_torch(
        pvals_torch, alpha=0.05
    )

    arr = pvals_corrected.astype(float)
    tor = pvals_corrected_torch.numpy().astype(float)
    print(scitex.gen.isclose(arr, tor))
