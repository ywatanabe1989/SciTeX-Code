#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-10-06 10:47:42 (ywatanabe)"
# _fdr_correction.py

"""
Functionality:
    - Implements False Discovery Rate (FDR) correction for multiple comparisons
    - Provides both NumPy and PyTorch implementations

Input:
    - Array-like object of p-values
    - Alpha level for significance
    - Method for correction ('indep' or 'negcorr')

Output:
    - Boolean array indicating rejected hypotheses
    - Array of corrected p-values

Prerequisites:
    - NumPy, PyTorch, pandas, statsmodels, and scitex packages
"""

"""Imports"""
from typing import Union, Tuple
import numpy as np
import torch
import pandas as pd
from statsmodels.stats.multitest import fdrcorrection
import scitex
from ...decorators import pandas_fn

ArrayLike = Union[np.ndarray, torch.Tensor, pd.Series]


@pandas_fn
def fdr_correction(results: pd.DataFrame) -> pd.DataFrame:
    """
    Apply FDR correction to p-value columns in a DataFrame.

    Example:
    --------
    >>> df = pd.DataFrame({'p_value': [0.01, 0.05, 0.1], 'other': [1, 2, 3]})
    >>> fdr_correction(df)
       p_value  other  p_value_fdr p_value_fdr_stars
    0     0.01      1    0.030000               **
    1     0.05      2    0.075000                *
    2     0.10      3    0.100000

    Parameters:
    -----------
    results : pd.DataFrame
        DataFrame containing p-value columns

    Returns:
    --------
    pd.DataFrame
        DataFrame with added FDR-corrected p-values and stars
    """
    pval_cols = scitex.stats.find_pval(results, multiple=True)
    if not pval_cols:
        return results

    for pval_col in pval_cols:
        non_nan = results.dropna(subset=[pval_col])
        nan_rows = results[results[pval_col].isna()]

        pvals = non_nan[pval_col]
        if isinstance(pvals, pd.DataFrame):
            pvals = pvals.values.flatten()

        _, fdr_corrected_pvals = fdrcorrection(pvals)
        non_nan[f"{pval_col}_fdr"] = fdr_corrected_pvals
        nan_rows[f"{pval_col}_fdr"] = np.nan

        results = pd.concat([non_nan, nan_rows]).sort_index()
        results[f"{pval_col}_fdr_stars"] = results[f"{pval_col}_fdr"].apply(
            scitex.stats.p2stars
        )

    return results


# def _ecdf(xx: ArrayLike) -> ArrayLike:
#     """Compute empirical cumulative distribution function."""
#     nobs = len(xx)
#     return np.arange(1, nobs + 1) / float(nobs)

# def _ecdf_torch(xx: torch.Tensor) -> torch.Tensor:
#     """Compute empirical cumulative distribution function using PyTorch."""
#     nobs = len(xx)
#     return torch.arange(1, nobs + 1, device=xx.device) / float(nobs)

# def fdr_correction_torch(pvals: torch.Tensor, alpha: float = 0.05, method: str = "indep") -> Tuple[torch.Tensor, torch.Tensor]:
#     """
#     P-value correction with False Discovery Rate (FDR) using PyTorch.

#     Example:
#     >>> pvals = torch.tensor([0.01, 0.02, 0.03, 0.04, 0.05])
#     >>> reject, pvals_corrected = fdr_correction_torch(pvals)
#     >>> print(reject, pvals_corrected)

#     Parameters:
#     -----------
#     pvals : torch.Tensor
#         Set of p-values of the individual tests
#     alpha : float, optional
#         Error rate (default is 0.05)
#     method : str, optional
#         'indep' for Benjamini/Hochberg, 'negcorr' for Benjamini/Yekutieli (default is 'indep')

#     Returns:
#     --------
#     reject : torch.Tensor
#         Boolean tensor indicating rejected hypotheses
#     pvals_corrected : torch.Tensor
#         Tensor of corrected p-values
#     """
#     shape_init = pvals.shape
#     pvals = pvals.ravel()

#     pvals_sortind = torch.argsort(pvals)
#     pvals_sorted = pvals[pvals_sortind]
#     sortrevind = pvals_sortind.argsort()

#     if method in ["i", "indep", "p", "poscorr"]:
#         ecdffactor = _ecdf_torch(pvals_sorted)
#     elif method in ["n", "negcorr"]:
#         cm = torch.sum(1.0 / torch.arange(1, len(pvals_sorted) + 1, device=pvals.device))
#         ecdffactor = _ecdf_torch(pvals_sorted) / cm
#     else:
#         raise ValueError("Method should be 'indep' or 'negcorr'")

#     ecdffactor = ecdffactor.to(pvals_sorted.dtype)

#     reject = pvals_sorted < (ecdffactor * alpha)

#     if reject.any():
#         rejectmax = torch.nonzero(reject, as_tuple=True)[0].max()
#     else:
#         rejectmax = torch.tensor(0, device=pvals.device)
#     reject[:rejectmax+1] = True

#     pvals_corrected_raw = pvals_sorted / ecdffactor
#     pvals_corrected = torch.minimum(torch.ones_like(pvals_corrected_raw), torch.cummin(pvals_corrected_raw.flip(0), 0)[0].flip(0))

#     pvals_corrected = pvals_corrected[sortrevind].reshape(shape_init)
#     reject = reject[sortrevind].reshape(shape_init)
#     return reject, pvals_corrected

if __name__ == "__main__":
    pvals = [0.02, 0.03, 0.05]
    pvals_torch = torch.tensor(np.array([0.02, 0.03, 0.05]))

    reject, pvals_corrected = fdr_correction(pd.DataFrame({"p_value": pvals}))

    reject_torch, pvals_corrected_torch = fdr_correction_torch(
        pvals_torch, alpha=0.05, method="indep"
    )

    arr = pvals_corrected["fdr_p_value"].to_numpy().astype(float)
    tor = pvals_corrected_torch.numpy().astype(float)
    print(scitex.gen.isclose(arr, tor))

# #!/usr/bin/env python3
# # Time-stamp: "2024-10-06 09:26:33 (ywatanabe)"

# """
# Functionality:
#     - Implements False Discovery Rate (FDR) correction for multiple comparisons
#     - Provides both NumPy and PyTorch implementations

# Input:
#     - Array-like object of p-values
#     - Alpha level for significance
#     - Method for correction ('indep' or 'negcorr')

# Output:
#     - Boolean array indicating rejected hypotheses
#     - Array of corrected p-values

# Prerequisites:
#     - NumPy, PyTorch, pandas, statsmodels, and scitex packages
# """

# """Imports"""
# from typing import Union, Tuple
# import numpy as np
# import torch
# import pandas as pd
# from statsmodels.stats.multitest import fdrcorrection
# import scitex

# ArrayLike = Union[np.ndarray, torch.Tensor, pd.Series]

# def fdr_correction(results: pd.DataFrame) -> pd.DataFrame:
#     """
#     Apply FDR correction to p-values in a DataFrame.

#     Example:
#     >>> df = pd.DataFrame({'p_value': [0.01, 0.02, 0.03, 0.04, 0.05]})
#     >>> corrected_df = fdr_correction(df)
#     >>> print(corrected_df)

#     Parameters:
#     -----------
#     results : pd.DataFrame
#         DataFrame containing a 'p_value' column

#     Returns:
#     --------
#     pd.DataFrame
#         DataFrame with added 'fdr_p_value' and 'fdr_stars' columns
#     """
#     if "p_value" not in results.columns:
#         return results
#     _, fdr_corrected_pvals = fdrcorrection(results["p_value"])
#     results["fdr_p_value"] = fdr_corrected_pvals
#     results["fdr_stars"] = results["fdr_p_value"].apply(scitex.stats.p2stars)
#     return results

# def fdr_correction(pvals, alpha=0.05, method="indep"):
#     # https://github.com/mne-tools/mne-python/blob/main/mne/stats/multi_comp.py
#     """P-value correction with False Discovery Rate (FDR).

#     Correction for multiple comparison using FDR :footcite:`GenoveseEtAl2002`.

#     This covers Benjamini/Hochberg for independent or positively correlated and
#     Benjamini/Yekutieli for gen or negatively correlated tests.

#     Parameters
#     ----------
#     pvals : array_like
#         Set of p-values of the individual tests.
#     alpha : float
#         Error rate.
#     method : 'indep' | 'negcorr'
#         If 'indep' it implements Benjamini/Hochberg for independent or if
#         'negcorr' it corresponds to Benjamini/Yekutieli.

#     Returns
#     -------
#     reject : array, bool
#         True if a hypothesis is rejected, False if not.
#     pval_corrected : array
#     alpha : float
#         Error rate.
#     method : 'indep' | 'negcorr'
#         If 'indep' it implements Benjamini/Hochberg for independent or if
#         'negcorr' it corresponds to Benjamini/Yekutieli.

#     Returns
#     -------
#     reject : array, bool
#         True if a hypothesis is rejected, False if not.
#     pval_corrected : array
#     alpha : float
#         Error rate.
#     method : 'indep' | 'negcorr'
#         If 'indep' it implements Benjamini/Hochberg for independent or if
#         'negcorr' it corresponds to Benjamini/Yekutieli.

#     Returns
#     -------
#     reject : array, bool
#         True if a hypothesis is rejected, False if not.
#     pval_corrected : array
#         P-values adjusted for multiple hypothesis testing to limit FDR.

#     Returns
#     -------
#     reject : array, bool
#         True if a hypothesis is rejected, False if not.
#     pval_corrected : array
#         P-values adjusted for multiple hypothesis testing to limit FDR.

#     References
#     ----------
#     .. footbibliography::
#     """
#     pvals = np.asarray(pvals)
#     shape_init = pvals.shape
#     pvals = pvals.ravel()

#     pvals_sortind = np.argsort(pvals)
#     pvals_sorted = pvals[pvals_sortind]
#     sortrevind = pvals_sortind.argsort()

#     if method in ["i", "indep", "p", "poscorr"]:
#         ecdffactor = _ecdf(pvals_sorted)
#     elif method in ["n", "negcorr"]:
#         cm = np.sum(1.0 / np.arange(1, len(pvals_sorted) + 1))
#         ecdffactor = _ecdf(pvals_sorted) / cm
#     else:
#         raise ValueError("Method should be 'indep' and 'negcorr'")

#     reject = pvals_sorted < (ecdffactor * alpha)
#     if reject.any():
#         rejectmax = max(np.nonzero(reject)[0])
#     else:
#         rejectmax = 0
#     reject[:rejectmax] = True

#     pvals_corrected_raw = pvals_sorted / ecdffactor
#     pvals_corrected = np.minimum.accumulate(pvals_corrected_raw[::-1])[::-1]
#     pvals_corrected[pvals_corrected > 1.0] = 1.0
#     pvals_corrected = pvals_corrected[sortrevind].reshape(shape_init)
#     reject = reject[sortrevind].reshape(shape_init)
#     return reject, pvals_corrected


# def fdr_correction(results: pd.DataFrame) -> pd.DataFrame:
#     if "p_value" not in results.columns:
#         return results
#     _, fdr_corrected_pvals = fdrcorrection(results["p_value"])
#     results["fdr_p_value"] = fdr_corrected_pvals
#     results["fdr_stars"] = results["fdr_p_value"].apply(scitex.stats.p2stars)
#     return results

# def _ecdf(xx: ArrayLike) -> ArrayLike:
#     """Compute empirical cumulative distribution function."""
#     nobs = len(xx)
#     return np.arange(1, nobs + 1) / float(nobs)

# def _ecdf_torch(xx: torch.Tensor) -> torch.Tensor:
#     """Compute empirical cumulative distribution function using PyTorch."""
#     nobs = len(xx)
#     return torch.arange(1, nobs + 1, device=xx.device) / float(nobs)

# def fdr_correction_torch(pvals: torch.Tensor, alpha: float = 0.05, method: str = "indep") -> Tuple[torch.Tensor, torch.Tensor]:
#     """
#     P-value correction with False Discovery Rate (FDR) using PyTorch.

#     Example:
#     >>> pvals = torch.tensor([0.01, 0.02, 0.03, 0.04, 0.05])
#     >>> reject, pvals_corrected = fdr_correction_torch(pvals)
#     >>> print(reject, pvals_corrected)

#     Parameters:
#     -----------
#     pvals : torch.Tensor
#         Set of p-values of the individual tests
#     alpha : float, optional
#         Error rate (default is 0.05)
#     method : str, optional
#         'indep' for Benjamini/Hochberg, 'negcorr' for Benjamini/Yekutieli (default is 'indep')

#     Returns:
#     --------
#     reject : torch.Tensor
#         Boolean tensor indicating rejected hypotheses
#     pvals_corrected : torch.Tensor
#         Tensor of corrected p-values
#     """
#     shape_init = pvals.shape
#     pvals = pvals.ravel()

#     pvals_sortind = torch.argsort(pvals)
#     pvals_sorted = pvals[pvals_sortind]
#     sortrevind = pvals_sortind.argsort()

#     if method in ["i", "indep", "p", "poscorr"]:
#         ecdffactor = _ecdf_torch(pvals_sorted)
#     elif method in ["n", "negcorr"]:
#         cm = torch.sum(1.0 / torch.arange(1, len(pvals_sorted) + 1, device=pvals.device))
#         ecdffactor = _ecdf_torch(pvals_sorted) / cm
#     else:
#         raise ValueError("Method should be 'indep' or 'negcorr'")

#     ecdffactor = ecdffactor.to(pvals_sorted.dtype)

#     reject = pvals_sorted < (ecdffactor * alpha)

#     if reject.any():
#         rejectmax = torch.nonzero(reject, as_tuple=True)[0].max()
#     else:
#         rejectmax = torch.tensor(0, device=pvals.device)
#     reject[:rejectmax+1] = True

#     pvals_corrected_raw = pvals_sorted / ecdffactor
#     pvals_corrected = torch.minimum(torch.ones_like(pvals_corrected_raw), torch.cummin(pvals_corrected_raw.flip(0), 0)[0].flip(0))

#     pvals_corrected = pvals_corrected[sortrevind].reshape(shape_init)
#     reject = reject[sortrevind].reshape(shape_init)
#     return reject, pvals_corrected


# if __name__ == "__main__":
#     pvals = [0.02, 0.03, 0.05]
#     pvals_torch = torch.tensor(np.array([0.02, 0.03, 0.05]))

#     reject, pvals_corrected = fdr_correction(pvals, alpha=0.05, method="indep")

#     reject_torch, pvals_corrected_torch = fdr_correction_torch(
#         pvals, alpha=0.05, method="indep"
#     )

#     arr = pvals_corrected.astype(float)
#     tor = pvals_corrected_torch.numpy().astype(float)
#     print(scitex.gen.isclose(arr, tor))
