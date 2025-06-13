# --------------------------------------------------------------------------------

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/stats/tests/__corr_test_multi.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-10-07 22:59:12 (ywatanabe)"
#
# from bisect import bisect_right
# import numpy as np
# import scitex
# from scipy import stats
# from typing import Any, Literal, Dict, Callable
# from ...decorators import numpy_fn
# import multiprocessing as mp
# from functools import partial
# import pandas as pd
# # def _compute_surrogate(args):
# #     data1, data2, corr_func, seed = args
# #     np.random.seed(seed)
#
# #     data1 = data1
# #     data2 = np.random.permutation(data2)
#
# #     non_nan_indices = ~(np.isnan(data1) | np.isnan(data2))
# #     data1, data2 = data1[non_nan_indices], data2[non_nan_indices]
#
# #     return corr_func(data1, data2)[0]
# def _compute_surrogate(args):
#     data1, data2, corr_func, seed = args
#     np.random.seed(seed)
#
#     data2 = np.random.permutation(data2)
#
#     if corr_func == stats.spearmanr:
#         return corr_func(data1, data2)[0]
#     else:
#         non_nan_indices = ~(np.isnan(data1) | np.isnan(data2))
#         return corr_func(data1[non_nan_indices], data2[non_nan_indices])[0]
#
# def _corr_test_base(
#     data1: np.ndarray,
#     data2: np.ndarray,
#     only_significant: bool,
#     n_perm: int,
#     seed: int,
#     corr_func: Callable,
#     test_name: str,
#     n_jobs: int = -1
# ) -> Dict[str, Any]:
#     np.random.seed(seed)
#     seeds = np.random.randint(0, n_perm*100, size=n_perm)
#
#     if corr_func != stats.spearmanr:
#         # Convert to numeric, replacing non-numeric values with NaN
#         data1 = pd.to_numeric(data1, errors='coerce')
#         data2 = pd.to_numeric(data2, errors='coerce')
#
#         # Remove NaN values
#         mask = ~(np.isnan(data1) | np.isnan(data2))
#         data1 = data1[mask]
#         data2 = data2[mask]
#
#     if len(data1) < 2 or len(data2) < 2:
#         raise ValueError("Not enough valid numeric data points for correlation.")
#
#     corr_obs, _ = corr_func(data1, data2)
#
#     # def _corr_test_base(
#     #     data1: np.ndarray,
#     #     data2: np.ndarray,
#     #     only_significant: bool,
#     #     n_perm: int,
#     #     seed: int,
#     #     corr_func: Callable,
#     #     test_name: str,
#     #     n_jobs: int = -1
#     # ) -> Dict[str, Any]:
#     #     # Random seed
#     #     np.random.seed(seed)
#     #     seeds = np.random.randint(0, n_perm*100, size=n_perm)
#
#     #     # Convert data to numeric type and handle non-numeric values
#     #     data1 = np.asarray(data1, dtype=float)
#     #     data2 = np.asarray(data2, dtype=float)
#
#     #     # Remove NaN values
#     #     mask = ~(np.isnan(data1) | np.isnan(data2))
#     #     data1 = data1[mask]
#     #     data2 = data2[mask]
#
#     #     corr_obs, _ = corr_func(data1, data2)
#
#     if n_jobs != 1:
#         n_jobs = mp.cpu_count() if n_jobs == -1 else n_jobs
#         with mp.Pool(n_jobs) as pool:
#             surrogate = np.array(pool.map(_compute_surrogate,
#                                           [(data1, data2, corr_func, s) for s in seeds]))
#     else:
#         surrogate = np.array([
#             _compute_surrogate((data1, data2, corr_func, s))
#             for s in seeds
#         ])
#
#     # Add normality test for surrogate distribution
#     _, p_normal = stats.normaltest(surrogate)
#     if not p_normal > 0.05:
#         print(f"Warning: Surrogate distribution may not be normal (p={p_normal:.3f})")
#
#
#     rank = bisect_right(sorted(surrogate), corr_obs)
#     pvalue = min(rank, n_perm - rank) / n_perm * 2
#
#     stars = scitex.stats.p2stars(pvalue)
#     sample_size = len(data1)
#     effect_size = np.abs(corr_obs)
#
#     result_string = (
#         f"{test_name} Corr. = {corr_obs:.3f}; p-value = {pvalue:.3f} "
#         f"(n={sample_size:,}, eff={effect_size:.3f}) {stars}"
#     )
#
#     if not only_significant or (only_significant and pvalue < 0.05):
#         print(result_string)
#
#     return {
#         "p_value": round(pvalue, 3),
#         "stars": stars,
#         "effsize": round(effect_size, 3),
#         "corr": round(corr_obs, 3),
#         "surrogate": surrogate,
#         "n": sample_size,
#         "test_name": f"Permutation-based {test_name} correlation test",
#         "statistic": round(corr_obs, 3),
#         "H0": f"There is no {test_name.lower()} correlation between the two variables",
#     }
#
# @numpy_fn
# def corr_test_spearman(
#     data1: np.ndarray,
#     data2: np.ndarray,
#     only_significant: bool = False,
#     n_perm: int = 1_000,
#     seed: int = 42,
# ) -> Dict[str, Any]:
#     return _corr_test_base(data1, data2, only_significant, n_perm, seed, stats.spearmanr, "Spearman")
#
# @numpy_fn
# def corr_test_pearson(
#     data1: np.ndarray,
#     data2: np.ndarray,
#     only_significant: bool = False,
#     n_perm: int = 1_000,
#     seed: int = 42,
# ) -> Dict[str, Any]:
#     return _corr_test_base(data1, data2, only_significant, n_perm, seed, stats.pearsonr, "Pearson")
#
# @numpy_fn
# def corr_test(
#     data1: np.ndarray,
#     data2: np.ndarray,
#     test: Literal["pearson", "spearman"] = "pearson",
#     only_significant: bool = False,
#     n_perm: int = 1_000,
#     seed: int = 42,
# ) -> Dict[str, Any]:
#     """
#     Performs a correlation test between two datasets using permutation.
#
#     Parameters
#     ----------
#     data1 : np.ndarray
#         First dataset for correlation.
#     data2 : np.ndarray
#         Second dataset for correlation.
#     test : {"pearson", "spearman"}, optional
#         Type of correlation test to perform. Default is "pearson".
#     only_significant : bool, optional
#         If True, only prints significant results. Default is False.
#     n_perm : int, optional
#         Number of permutations for the test. Default is 1,000.
#     seed : int, optional
#         Random seed for reproducibility. Default is 42.
#
#     Returns
#     -------
#     Dict[str, Any]
#         Contains 'p_value', 'stars', 'effsize', 'corr', 'surrogate', 'n', 'test_name', 'statistic', and 'H0'.
#
#     Example
#     -------
#     >>> xx = np.array([3, 4, 4, 5, 7, 8, 10, 12, 13, 15])
#     >>> yy = np.array([2, 4, 4, 5, 4, 7, 8, 19, 14, 10])
#     >>> results = corr_test(xx, yy, test="pearson")
#     """
#     if test == "spearman":
#         return corr_test_spearman(data1, data2, only_significant, n_perm, seed)
#     elif test == "pearson":
#         return corr_test_pearson(data1, data2, only_significant, n_perm, seed)
#     else:
#         raise ValueError("Invalid test type. Choose 'pearson' or 'spearman'.")
#
# if __name__ == "__main__":
#     xx = np.array([3, 4, 4, 5, 7, 8, 10, 12, 13, 15])
#     yy = np.array([2, 4, 4, 5, 4, 7, 8, 19, 14, 10])
#     results_pearson = corr_test(xx, yy)
#     results_spearman = corr_test(xx, yy, test="spearman")
#     print("Pearson results:", results_pearson)
#     print("Spearman results:", results_spearman)
# # #!/usr/bin/env python3
# # # -*- coding: utf-8 -*-
# # # Time-stamp: "2024-10-06 12:02:18 (ywatanabe)"
#
# # from bisect import bisect_right
# # import numpy as np
# # import scitex
# # from scipy import stats
# # from typing import Any, Literal, Dict, List
#
# # def _corr_test_base(
# #     data1: np.ndarray,
# #     data2: np.ndarray,
# #     only_significant: bool,
# #     n_perm: int,
# #     seed: int,
# #     corr_func: callable,
# #     test_name: str
# # ) -> Dict[str, Any]:
# #     np.random.seed(seed)
#
# #     non_nan_indices = ~(np.isnan(data1) | np.isnan(data2))
# #     data1, data2 = data1[non_nan_indices], data2[non_nan_indices]
#
# #     corr_obs, _ = corr_func(data1, data2)
# #     surrogate = [
# #         corr_func(data1, np.random.permutation(data2))[0]
# #         for _ in range(n_perm)
# #     ]
#
# #     rank = bisect_right(sorted(surrogate), corr_obs)
# #     pvalue = min(rank, n_perm - rank) / n_perm * 2
#
# #     stars = scitex.stats.p2stars(pvalue)
# #     sample_size = len(data1)
# #     effect_size = np.abs(corr_obs)
#
# #     # result_string = (
# #     #     f"{test_name} Corr. = {corr_obs:.3f}; p-value = {pvalue:.3f} "
# #     #     f"(n={sample_size:,}, eff={effect_size:.3f}) {stars}"
# #     # )
#
# #     if not only_significant or (only_significant and pvalue < 0.05):
# #         print(result_string)
#
# #     return {
# #         "p_value": round(pvalue, 3),
# #         "stars": stars,
# #         "effsize": round(effect_size, 3),
# #         "corr": round(corr_obs, 3),
# #         "surrogate": np.array(surrogate),
# #         "n": sample_size,
# #         "test_name": f"Permutation-based {test_name} correlation",
# #         "statistic": round(corr_obs, 3),
# #         "H0": f"There is no {test_name.lower()} correlation between the two variables",
# #     }
#
# # def corr_test_spearman(
# #     data1: np.ndarray,
# #     data2: np.ndarray,
# #     only_significant: bool = False,
# #     n_perm: int = 1_000,
# #     seed: int = 42,
# # ) -> Dict[str, Any]:
# #     return _corr_test_base(data1, data2, only_significant, n_perm, seed, stats.spearmanr, "Spearman")
#
# # def corr_test_pearson(
# #     data1: np.ndarray,
# #     data2: np.ndarray,
# #     only_significant: bool = False,
# #     n_perm: int = 1_000,
# #     seed: int = 42,
# # ) -> Dict[str, Any]:
# #     return _corr_test_base(data1, data2, only_significant, n_perm, seed, stats.pearsonr, "Pearson")
#
# # def corr_test(
# #     data1: np.ndarray,
# #     data2: np.ndarray,
# #     test: Literal["pearson", "spearman"] = "pearson",
# #     only_significant: bool = False,
# #     n_perm: int = 1_000,
# #     seed: int = 42,
# # ) -> Dict[str, Any]:
# #     """
# #     Performs a correlation test between two datasets using permutation.
#
# #     Parameters
# #     ----------
# #     data1 : np.ndarray
# #         First dataset for correlation.
# #     data2 : np.ndarray
# #         Second dataset for correlation.
# #     test : {"pearson", "spearman"}, optional
# #         Type of correlation test to perform. Default is "pearson".
# #     only_significant : bool, optional
# #         If True, only prints significant results. Default is False.
# #     n_perm : int, optional
# #         Number of permutations for the test. Default is 1,000.
# #     seed : int, optional
# #         Random seed for reproducibility. Default is 42.
#
# #     Returns
# #     -------
# #     Dict[str, Any]
# #         Contains 'p_value', 'stars', 'effsize', 'corr', 'surrogate', 'n', 'test_name', 'statistic', and 'H0'.
#
# #     Example
# #     -------
# #     >>> xx = np.array([3, 4, 4, 5, 7, 8, 10, 12, 13, 15])
# #     >>> yy = np.array([2, 4, 4, 5, 4, 7, 8, 19, 14, 10])
# #     >>> results = corr_test(xx, yy, test="pearson")
# #     """
# #     if test == "spearman":
# #         return corr_test_spearman(data1, data2, only_significant, n_perm, seed)
# #     elif test == "pearson":
# #         return corr_test_pearson(data1, data2, only_significant, n_perm, seed)
# #     else:
# #         raise ValueError("Invalid test type. Choose 'spearman' or 'pearson'.")
#
# # if __name__ == "__main__":
# #     xx = np.array([3, 4, 4, 5, 7, 8, 10, 12, 13, 15])
# #     yy = np.array([2, 4, 4, 5, 4, 7, 8, 19, 14, 10])
# #     results_spearman = corr_test(xx, yy)
# #     results_pearson = corr_test(xx, yy, test="pearson")
# #     print("Spearman results:", results_spearman)
# #     print("Pearson results:", results_pearson)

# --------------------------------------------------------------------------------
# End of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/stats/tests/__corr_test_multi.py
# --------------------------------------------------------------------------------
