#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-05-25 17:25:00 (ywatanabe)"
# File: ./tests/scitex/stats/tests/test___corr_test.py

"""
Test module for scitex.stats.tests._corr_test
"""

import numpy as np
import pytest
from scipy import stats
from unittest.mock import patch, MagicMock
import multiprocessing as mp


class TestCorrTest:
    """Test cases for correlation test functions"""

    @pytest.fixture
    def sample_data(self):
        """Generate sample data for correlation tests"""
        np.random.seed(42)
        n = 100

        # Positively correlated data
        x = np.random.randn(n)
        y_pos = 2 * x + np.random.randn(n) * 0.5

        # Negatively correlated data
        y_neg = -2 * x + np.random.randn(n) * 0.5

        # Uncorrelated data
        y_uncorr = np.random.randn(n)

        # Data with NaNs
        x_nan = x.copy()
        x_nan[::10] = np.nan

        return {
            "x": x,
            "y_pos": y_pos,
            "y_neg": y_neg,
            "y_uncorr": y_uncorr,
            "x_nan": x_nan,
        }

    def test_corr_test_spearman(self, sample_data):
        """Test Spearman correlation test"""
        from scitex.stats.tests import corr_test_spearman

        # Test positive correlation
        result = corr_test_spearman(sample_data["x"], sample_data["y_pos"], n_perm=100)

        assert isinstance(result, dict)
        assert "r" in result
        assert "p" in result
        assert "CI" in result
        assert result["r"] > 0.5  # Should be positively correlated
        assert result["p"] < 0.05  # Should be significant

    def test_corr_test_pearson(self, sample_data):
        """Test Pearson correlation test"""
        from scitex.stats.tests import corr_test_pearson

        # Test negative correlation
        result = corr_test_pearson(sample_data["x"], sample_data["y_neg"], n_perm=100)

        assert isinstance(result, dict)
        assert "r" in result
        assert "p" in result
        assert "CI" in result
        assert result["r"] < -0.5  # Should be negatively correlated
        assert result["p"] < 0.05  # Should be significant

    def test_corr_test_with_nan(self, sample_data):
        """Test correlation with NaN values"""
        from scitex.stats.tests import corr_test

        # Test with NaN values
        result = corr_test(
            sample_data["x_nan"], sample_data["y_pos"], method="pearson", n_perm=100
        )

        assert isinstance(result, dict)
        assert not np.isnan(result["r"])  # Should handle NaNs properly

    def test_corr_test_no_correlation(self, sample_data):
        """Test with uncorrelated data"""
        from scitex.stats.tests import corr_test

        result = corr_test(
            sample_data["x"], sample_data["y_uncorr"], method="spearman", n_perm=100
        )

        assert isinstance(result, dict)
        assert abs(result["r"]) < 0.3  # Should be low correlation
        assert result["p"] > 0.05  # Should not be significant

    def test_corr_test_only_significant(self, sample_data):
        """Test only_significant parameter"""
        from scitex.stats.tests import corr_test

        # Test with uncorrelated data and only_significant=True
        result = corr_test(
            sample_data["x"],
            sample_data["y_uncorr"],
            method="pearson",
            only_significant=True,
            n_perm=100,
        )

        # Should return None or empty result for non-significant
        assert result is None or result.get("p", 0) > 0.05

    def test_compute_surrogate(self):
        """Test surrogate computation function"""
        from scitex.stats.tests import _compute_surrogate

        data1 = np.random.randn(100)
        data2 = np.random.randn(100)

        # Test with Pearson correlation
        args = (data1, data2, stats.pearsonr, 42)
        surrogate_r = _compute_surrogate(args)

        assert isinstance(surrogate_r, (float, np.floating))
        assert -1 <= surrogate_r <= 1

    def test_corr_test_methods(self, sample_data):
        """Test different correlation methods"""
        from scitex.stats.tests import corr_test

        methods = ["pearson", "spearman"]

        for method in methods:
            result = corr_test(
                sample_data["x"], sample_data["y_pos"], method=method, n_perm=100
            )

            assert isinstance(result, dict)
            assert "r" in result
            assert "p" in result
            assert "method" in result
            assert result["method"] == method

    def test_corr_test_confidence_interval(self, sample_data):
        """Test confidence interval computation"""
        from scitex.stats.tests import corr_test

        result = corr_test(
            sample_data["x"],
            sample_data["y_pos"],
            method="pearson",
            n_perm=1000,  # More permutations for stable CI
        )

        assert "CI" in result
        assert len(result["CI"]) == 2
        assert result["CI"][0] < result["r"] < result["CI"][1]

    @pytest.mark.parametrize("n_jobs", [1, 2, -1])
    def test_corr_test_parallel(self, sample_data, n_jobs):
        """Test parallel processing with different n_jobs"""
        from scitex.stats.tests import corr_test

        result = corr_test(
            sample_data["x"],
            sample_data["y_pos"],
            method="spearman",
            n_perm=100,
            n_jobs=n_jobs,
        )

        assert isinstance(result, dict)
        assert "r" in result

    def test_corr_test_reproducibility(self, sample_data):
        """Test reproducibility with same seed"""
        from scitex.stats.tests import corr_test

        # Run twice with same seed
        result1 = corr_test(
            sample_data["x"],
            sample_data["y_pos"],
            method="pearson",
            n_perm=100,
            seed=42,
        )

        result2 = corr_test(
            sample_data["x"],
            sample_data["y_pos"],
            method="pearson",
            n_perm=100,
            seed=42,
        )

        # Results should be identical
        assert result1["r"] == result2["r"]
        assert result1["p"] == result2["p"]

    def test_corr_test_input_validation(self):
        """Test input validation"""
        from scitex.stats.tests import corr_test

        # Test with mismatched lengths
        data1 = np.random.randn(100)
        data2 = np.random.randn(50)

        with pytest.raises(Exception):
            corr_test(data1, data2)

        # Test with invalid method
        with pytest.raises(Exception):
            corr_test(data1, data1, method="invalid_method")


# EOF

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/stats/tests/__corr_test.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-10-06 12:04:31 (ywatanabe)"
# 
# from bisect import bisect_right
# import numpy as np
# import scitex
# from scipy import stats
# from typing import Any, Literal, Dict, Callable
# 
# 
# def _corr_test_base(
#     data1: np.ndarray,
#     data2: np.ndarray,
#     only_significant: bool,
#     num_permutations: int,
#     seed: int,
#     corr_func: Callable,
#     test_name: str,
# ) -> Dict[str, Any]:
#     np.random.seed(seed)
# 
#     non_nan_indices = ~(np.isnan(data1) | np.isnan(data2))
#     data1, data2 = data1[non_nan_indices], data2[non_nan_indices]
# 
#     corr_obs, _ = corr_func(data1, data2)
#     surrogate = np.array(
#         [
#             corr_func(data1, np.random.permutation(data2))[0]
#             for _ in range(num_permutations)
#         ]
#     )
# 
#     rank = bisect_right(sorted(surrogate), corr_obs)
#     pvalue = min(rank, num_permutations - rank) / num_permutations * 2
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
#         "test_name": f"Permutation-based {test_name} correlation",
#         "statistic": round(corr_obs, 3),
#         "H0": f"There is no {test_name.lower()} correlation between the two variables",
#     }
# 
# 
# def corr_test_spearman(
#     data1: np.ndarray,
#     data2: np.ndarray,
#     only_significant: bool = False,
#     num_permutations: int = 1_000,
#     seed: int = 42,
# ) -> Dict[str, Any]:
#     return _corr_test_base(
#         data1,
#         data2,
#         only_significant,
#         num_permutations,
#         seed,
#         stats.spearmanr,
#         "Spearman",
#     )
# 
# 
# def corr_test_pearson(
#     data1: np.ndarray,
#     data2: np.ndarray,
#     only_significant: bool = False,
#     num_permutations: int = 1_000,
#     seed: int = 42,
# ) -> Dict[str, Any]:
#     return _corr_test_base(
#         data1,
#         data2,
#         only_significant,
#         num_permutations,
#         seed,
#         stats.pearsonr,
#         "Pearson",
#     )
# 
# 
# def corr_test(
#     data1: np.ndarray,
#     data2: np.ndarray,
#     test: Literal["pearson", "spearman"] = "pearson",
#     only_significant: bool = False,
#     num_permutations: int = 1_000,
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
#     num_permutations : int, optional
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
#         return corr_test_spearman(
#             data1, data2, only_significant, num_permutations, seed
#         )
#     elif test == "pearson":
#         return corr_test_pearson(data1, data2, only_significant, num_permutations, seed)
#     else:
#         raise ValueError("Invalid test type. Choose 'pearson' or 'spearman'.")
# 
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
# #     num_permutations: int,
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
# #         for _ in range(num_permutations)
# #     ]
# 
# #     rank = bisect_right(sorted(surrogate), corr_obs)
# #     pvalue = min(rank, num_permutations - rank) / num_permutations * 2
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
# #     num_permutations: int = 1_000,
# #     seed: int = 42,
# # ) -> Dict[str, Any]:
# #     return _corr_test_base(data1, data2, only_significant, num_permutations, seed, stats.spearmanr, "Spearman")
# 
# # def corr_test_pearson(
# #     data1: np.ndarray,
# #     data2: np.ndarray,
# #     only_significant: bool = False,
# #     num_permutations: int = 1_000,
# #     seed: int = 42,
# # ) -> Dict[str, Any]:
# #     return _corr_test_base(data1, data2, only_significant, num_permutations, seed, stats.pearsonr, "Pearson")
# 
# # def corr_test(
# #     data1: np.ndarray,
# #     data2: np.ndarray,
# #     test: Literal["pearson", "spearman"] = "pearson",
# #     only_significant: bool = False,
# #     num_permutations: int = 1_000,
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
# #     num_permutations : int, optional
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
# #         return corr_test_spearman(data1, data2, only_significant, num_permutations, seed)
# #     elif test == "pearson":
# #         return corr_test_pearson(data1, data2, only_significant, num_permutations, seed)
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
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/stats/tests/__corr_test.py
# --------------------------------------------------------------------------------
