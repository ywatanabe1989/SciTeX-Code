#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-05-31 22:00:00 (ywatanabe)"
# File: tests/scitex/stats/tests/test__brunner_munzel_test.py

"""Test cases for Brunner-Munzel test."""

import numpy as np
import pandas as pd
import pytest
import torch
import xarray as xr

import scitex

class TestBrunnerMunzelTest:
    """Test cases for brunner_munzel_test function."""
    
    def test_basic_functionality(self):
        """Test basic functionality with simple arrays."""
        x1 = [1, 2, 3, 4, 5]
        x2 = [2, 3, 4, 5, 6]
        result = scitex.stats.tests._brunner_munzel_test.brunner_munzel_test(x1, x2)
        
        assert isinstance(result, dict)
        assert 'w_statistic' in result
        assert 'p_value' in result
        assert 'n1' in result
        assert 'n2' in result
        assert 'dof' in result
        assert 'effsize' in result
        assert 'test_name' in result
        assert 'H0' in result
        
    def test_result_structure(self):
        """Test that result has all expected keys."""
        x1 = np.random.randn(20)
        x2 = np.random.randn(20)
        result = scitex.stats.tests._brunner_munzel_test.brunner_munzel_test(x1, x2)
        
        expected_keys = ['w_statistic', 'p_value', 'n1', 'n2', 'dof', 
                        'effsize', 'test_name', 'H0']
        assert all(key in result for key in expected_keys)
        
    def test_different_sample_sizes(self):
        """Test with different sample sizes."""
        x1 = np.random.randn(10)
        x2 = np.random.randn(20)
        result = scitex.stats.tests._brunner_munzel_test.brunner_munzel_test(x1, x2)
        
        assert result['n1'] == 10
        assert result['n2'] == 20
        
    def test_t_distribution(self):
        """Test with t distribution (default)."""
        x1 = np.random.randn(15)
        x2 = np.random.randn(15)
        result = scitex.stats.tests._brunner_munzel_test.brunner_munzel_test(
            x1, x2, distribution='t'
        )
        
        assert not np.isnan(result['dof'])
        assert result['dof'] > 0
        
    def test_normal_distribution(self):
        """Test with normal distribution."""
        x1 = np.random.randn(15)
        x2 = np.random.randn(15)
        result = scitex.stats.tests._brunner_munzel_test.brunner_munzel_test(
            x1, x2, distribution='normal'
        )
        
        assert np.isnan(result['dof'])
        
    def test_invalid_distribution(self):
        """Test with invalid distribution parameter."""
        x1 = np.random.randn(10)
        x2 = np.random.randn(10)
        
        with pytest.raises(ValueError, match="Distribution must be either 't' or 'normal'"):
            scitex.stats.tests._brunner_munzel_test.brunner_munzel_test(
                x1, x2, distribution='invalid'
            )
            
    def test_with_nan_values(self):
        """Test with NaN values in input."""
        x1 = [1, 2, np.nan, 4, 5]
        x2 = [2, 3, 4, np.nan, 6]
        result = scitex.stats.tests._brunner_munzel_test.brunner_munzel_test(x1, x2)
        
        assert result['n1'] == 4  # NaN removed
        assert result['n2'] == 4  # NaN removed
        
    def test_all_nan_input(self):
        """Test with all NaN values."""
        x1 = [np.nan, np.nan, np.nan]
        x2 = [np.nan, np.nan]
        
        with pytest.raises(ValueError, match="Input arrays must not be empty"):
            scitex.stats.tests._brunner_munzel_test.brunner_munzel_test(x1, x2)
            
    def test_empty_input(self):
        """Test with empty arrays."""
        x1 = []
        x2 = []
        
        with pytest.raises(ValueError, match="Input arrays must not be empty"):
            scitex.stats.tests._brunner_munzel_test.brunner_munzel_test(x1, x2)
            
    def test_round_factor(self):
        """Test rounding functionality."""
        x1 = np.random.randn(20)
        x2 = np.random.randn(20)
        
        result1 = scitex.stats.tests._brunner_munzel_test.brunner_munzel_test(
            x1, x2, round_factor=1
        )
        result2 = scitex.stats.tests._brunner_munzel_test.brunner_munzel_test(
            x1, x2, round_factor=5
        )
        
        # Check that rounding is applied
        assert len(str(result1['w_statistic']).split('.')[-1]) <= 1
        assert len(str(result2['w_statistic']).split('.')[-1]) <= 5
        
    def test_effect_size_range(self):
        """Test that effect size is in valid range [0, 1]."""
        x1 = np.random.randn(30)
        x2 = np.random.randn(30)
        result = scitex.stats.tests._brunner_munzel_test.brunner_munzel_test(x1, x2)
        
        assert 0 <= result['effsize'] <= 1
        
    def test_p_value_range(self):
        """Test that p-value is in valid range [0, 1]."""
        x1 = np.random.randn(25)
        x2 = np.random.randn(25)
        result = scitex.stats.tests._brunner_munzel_test.brunner_munzel_test(x1, x2)
        
        assert 0 <= result['p_value'] <= 1
        
    def test_identical_samples(self):
        """Test with identical samples."""
        x = np.random.randn(20)
        result = scitex.stats.tests._brunner_munzel_test.brunner_munzel_test(x, x)
        
        # Effect size should be approximately 0.5 for identical samples
        assert abs(result['effsize'] - 0.5) < 0.1
        
    def test_very_different_samples(self):
        """Test with very different samples."""
        x1 = np.random.randn(30) - 5
        x2 = np.random.randn(30) + 5
        result = scitex.stats.tests._brunner_munzel_test.brunner_munzel_test(x1, x2)
        
        # Should have low p-value for very different samples
        assert result['p_value'] < 0.01
        
    def test_numpy_arrays(self):
        """Test with numpy arrays."""
        x1 = np.array([1, 2, 3, 4, 5])
        x2 = np.array([2, 3, 4, 5, 6])
        result = scitex.stats.tests._brunner_munzel_test.brunner_munzel_test(x1, x2)
        
        assert isinstance(result, dict)
        assert result['n1'] == 5
        assert result['n2'] == 5
        
    def test_pandas_series(self):
        """Test with pandas Series."""
        x1 = pd.Series([1, 2, 3, 4, 5])
        x2 = pd.Series([2, 3, 4, 5, 6])
        result = scitex.stats.tests._brunner_munzel_test.brunner_munzel_test(x1, x2)
        
        assert isinstance(result, dict)
        assert result['n1'] == 5
        assert result['n2'] == 5
        
    def test_torch_tensors(self):
        """Test with PyTorch tensors."""
        x1 = torch.tensor([1.0, 2.0, 3.0, 4.0, 5.0])
        x2 = torch.tensor([2.0, 3.0, 4.0, 5.0, 6.0])
        result = scitex.stats.tests._brunner_munzel_test.brunner_munzel_test(x1, x2)
        
        assert isinstance(result, dict)
        assert result['n1'] == 5
        assert result['n2'] == 5
        
    def test_xarray_dataarray(self):
        """Test with xarray DataArray."""
        x1 = xr.DataArray([1, 2, 3, 4, 5])
        x2 = xr.DataArray([2, 3, 4, 5, 6])
        result = scitex.stats.tests._brunner_munzel_test.brunner_munzel_test(x1, x2)
        
        assert isinstance(result, dict)
        assert result['n1'] == 5
        assert result['n2'] == 5
        
    def test_mixed_types(self):
        """Test with mixed input types."""
        x1 = [1, 2, 3, 4, 5]
        x2 = np.array([2, 3, 4, 5, 6])
        result = scitex.stats.tests._brunner_munzel_test.brunner_munzel_test(x1, x2)
        
        assert isinstance(result, dict)
        assert result['n1'] == 5
        assert result['n2'] == 5
        
    def test_ties_handling(self):
        """Test handling of tied values."""
        x1 = [1, 1, 2, 2, 3]
        x2 = [2, 2, 3, 3, 4]
        result = scitex.stats.tests._brunner_munzel_test.brunner_munzel_test(x1, x2)
        
        assert isinstance(result, dict)
        assert 'w_statistic' in result
        
    def test_single_value_arrays(self):
        """Test with single value arrays."""
        x1 = [1]
        x2 = [2]
        
        # Should handle edge case appropriately
        result = scitex.stats.tests._brunner_munzel_test.brunner_munzel_test(x1, x2)
        assert result['n1'] == 1
        assert result['n2'] == 1
        
    def test_large_samples(self):
        """Test with large sample sizes."""
        np.random.seed(42)
        x1 = np.random.randn(1000)
        x2 = np.random.randn(1000) + 0.1
        result = scitex.stats.tests._brunner_munzel_test.brunner_munzel_test(x1, x2)
        
        assert result['n1'] == 1000
        assert result['n2'] == 1000
        # Large samples should give more precise results
        assert result['p_value'] < 0.05  # Small shift should be detectable
        
    def test_reproducibility(self):
        """Test that results are reproducible."""
        np.random.seed(123)
        x1 = np.random.randn(50)
        x2 = np.random.randn(50)
        
        result1 = scitex.stats.tests._brunner_munzel_test.brunner_munzel_test(x1, x2)
        result2 = scitex.stats.tests._brunner_munzel_test.brunner_munzel_test(x1, x2)
        
        assert result1['w_statistic'] == result2['w_statistic']
        assert result1['p_value'] == result2['p_value']
        
    def test_test_name_and_h0(self):
        """Test that test name and null hypothesis are correct."""
        x1 = np.random.randn(10)
        x2 = np.random.randn(10)
        result = scitex.stats.tests._brunner_munzel_test.brunner_munzel_test(x1, x2)
        
        assert result['test_name'] == 'Brunner-Munzel test'
        assert 'probability' in result['H0'].lower()
        assert '0.5' in result['H0']
        
    def test_statistical_properties(self):
        """Test statistical properties of the test."""
        np.random.seed(456)
        # Under null hypothesis (same distribution)
        p_values = []
        for _ in range(100):
            x1 = np.random.randn(20)
            x2 = np.random.randn(20)
            result = scitex.stats.tests._brunner_munzel_test.brunner_munzel_test(x1, x2)
            p_values.append(result['p_value'])
            
        # Under null, p-values should be approximately uniform
        # Check that roughly 5% are below 0.05
        significant = sum(p < 0.05 for p in p_values)
        assert 2 <= significant <= 10  # Allow some variation
        
    def test_power_against_shift(self):
        """Test power to detect location shift."""
        np.random.seed(789)
        # With shifted distribution
        p_values = []
        for _ in range(50):
            x1 = np.random.randn(30)
            x2 = np.random.randn(30) + 0.5  # Medium effect size
            result = scitex.stats.tests._brunner_munzel_test.brunner_munzel_test(x1, x2)
            p_values.append(result['p_value'])
            
        # Should have good power to detect medium effect
        significant = sum(p < 0.05 for p in p_values)
        assert significant > 25  # At least 50% power
        
    def test_edge_case_variance(self):
        """Test edge case with zero variance."""
        x1 = [1, 1, 1, 1, 1]
        x2 = [2, 2, 2, 2, 2]
        result = scitex.stats.tests._brunner_munzel_test.brunner_munzel_test(x1, x2)
        
        # Should handle constant values appropriately
        assert result['effsize'] == 0.0 or result['effsize'] == 1.0
        
    def test_integration_with_statistical_tests(self):
        """Test integration with other statistical tests."""
        np.random.seed(999)
        x1 = np.random.randn(25)
        x2 = np.random.randn(25) + 0.3
        
        # Run Brunner-Munzel test
        bm_result = scitex.stats.tests._brunner_munzel_test.brunner_munzel_test(x1, x2)
        
        # Should provide reasonable results
        assert isinstance(bm_result, dict)
        assert 0 < bm_result['p_value'] < 1
        assert 0 < bm_result['effsize'] < 1


# --------------------------------------------------------------------------------

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/stats/tests/_brunner_munzel_test.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-10-07 22:30:46 (ywatanabe)"
# # File: /home/ywatanabe/proj/_scitex_repo_openhands/src/scitex/stats/_brunner_munzel_test.py
#
# """
# 1. Functionality:
#    - Calculates Brunner-Munzel test scores for two independent samples
# 2. Input:
#    - Two arrays of numeric data values
# 3. Output:
#    - Dictionary containing test results (w_statistic, p_value, sample sizes, degrees of freedom, effect size, test name, and null hypothesis)
# 4. Prerequisites:
#    - NumPy, SciPy
# """
#
# """Imports"""
# import numpy as np
# from scipy import stats
# import pandas as pd
# import xarray as xr
# import torch
# from ...types import List, Tuple, Dict, Any, Union, Sequence, Literal, Iterable, ArrayLike
# from ...decorators import numpy_fn
#
# @numpy_fn
# def brunner_munzel_test(
#     x1: ArrayLike,
#     x2: ArrayLike,
#     distribution: str = "t",
#     round_factor: int = 3,
# ) -> Dict[str, Union[float, int, str]]:
#     """
#     Calculate Brunner-Munzel test scores.
#
#     Parameters
#     ----------
#     x1 : ArrayLike
#         Numeric data values from sample 1.
#     x2 : ArrayLike
#         Numeric data values from sample 2.
#     distribution : str, optional
#         Distribution to use for the test. Can be "t" or "normal" (default is "t").
#     round_factor : int, optional
#         Number of decimal places to round the results (default is 3).
#
#     Returns
#     -------
#     Dict[str, Union[float, int, str]]
#         Dictionary containing test results including w_statistic, p_value, sample sizes, degrees of freedom, effect size, test name, and null hypothesis.
#
#     Example
#     -------
#     >>> np.random.seed(42)
#     >>> xx = np.random.rand(100)
#     >>> yy = np.random.rand(100) + 0.1
#     >>> result = brunner_munzel_test(xx, yy)
#     >>> print(result)
#     {'w_statistic': -2.089, 'p_value': 0.038, 'n1': 100, 'n2': 100, 'dof': 197.0, 'effsize': 0.438, 'test_name': 'Brunner-Munzel test', 'H0': 'The probability that a randomly selected value from one population is greater than a randomly selected value from the other population is equal to 0.5'}
#     """
#     if distribution not in ["t", "normal"]:
#         raise ValueError("Distribution must be either 't' or 'normal'")
#
#     x1, x2 = np.asarray(x1).astype(float), np.asarray(x2).astype(float)
#     x1, x2 = x1[~np.isnan(x1)], x2[~np.isnan(x2)]
#     n1, n2 = len(x1), len(x2)
#
#     if n1 == 0 or n2 == 0:
#         raise ValueError(
#             "Input arrays must not be empty after removing NaN values"
#         )
#
#     R = stats.rankdata(np.concatenate([x1, x2]))
#     R1, R2 = R[:n1], R[n1:]
#     r1_mean, r2_mean = np.mean(R1), np.mean(R2)
#     Ri1, Ri2 = stats.rankdata(x1), stats.rankdata(x2)
#     var1 = np.var(R1 - Ri1, ddof=1)
#     var2 = np.var(R2 - Ri2, ddof=1)
#
#     w_statistic = ((n1 * n2) * (r2_mean - r1_mean)) / (
#         (n1 + n2) * np.sqrt(n1 * var1 + n2 * var2)
#     )
#
#     if distribution == "t":
#         dof = (n1 * var1 + n2 * var2) ** 2 / (
#             (n1 * var1) ** 2 / (n1 - 1) + (n2 * var2) ** 2 / (n2 - 1)
#         )
#         c = (
#             stats.t.cdf(abs(w_statistic), dof)
#             if not np.isinf(w_statistic)
#             else 0.0
#         )
#     else:
#         dof = np.nan
#         c = (
#             stats.norm.cdf(abs(w_statistic))
#             if not np.isinf(w_statistic)
#             else 0.0
#         )
#
#     p_value = min(c, 1.0 - c) * 2.0
#     effsize = (r2_mean - r1_mean) / (n1 + n2) + 0.5
#
#     return {
#         "w_statistic": round(w_statistic, round_factor),
#         "p_value": round(p_value, round_factor),
#         "n1": n1,
#         "n2": n2,
#         "dof": round(dof, round_factor),
#         "effsize": round(effsize, round_factor),
#         "test_name": "Brunner-Munzel test",
#         "H0": "The probability that a randomly selected value from one population is greater than a randomly selected value from the other population is equal to 0.5",
#     }
#
#
# # #!/usr/bin/env python3
#
# # import numpy as np
# # from scipy import stats
#
#
# # def brunner_munzel_test(x1, x2, distribution="t", round_factor=3):
# #     """Calculate Brunner-Munzel-test scores.
# #     Parameters:
# #       x1, x2: array_like
# #         Numeric data values from sample 1, 2.
# #     Returns:
# #       w:
# #         Calculated test statistic.
# #       p_value:
# #         Two-tailed p-value of test.
# #       dof:
# #         Degree of freedom.
# #       p:
# #         "P(x1 < x2) + 0.5 P(x1 = x2)" estimates.
# #     References:
# #       * https://oku.edu.mie-u.ac.jp/~okumura/stat/brunner-munzel.html
# #     Example:
# #       When sample number N is small, distribution='t' is recommended.
# #       d1 = np.array([1,2,1,1,1,1,1,1,1,1,2,4,1,1])
# #       d2 = np.array([3,3,4,3,1,2,3,1,1,5,4])
# #       print(bmtest(d1, d2, distribution='t'))
# #       print(bmtest(d1, d2, distribution='normal'))
# #       When sample number N is large, distribution='normal' is recommended; however,
# #       't' and 'normal' yield almost the same result.
# #       d1 = np.random.rand(1000)*100
# #       d2 = np.random.rand(10000)*110
# #       print(bmtest(d1, d2, distribution='t'))
# #       print(bmtest(d1, d2, distribution='normal'))
# #     """
#
# #     x1, x2 = np.hstack(x1), np.hstack(x2)
# #     x1, x2 = x1[~np.isnan(x1)], x2[~np.isnan(x2)]
# #     n1, n2 = len(x1), len(x2)
# #     R = stats.rankdata(list(x1) + list(x2))
# #     R1, R2 = R[:n1], R[n1:]
# #     r1_mean, r2_mean = np.mean(R1), np.mean(R2)
# #     Ri1, Ri2 = stats.rankdata(x1), stats.rankdata(x2)
# #     var1 = np.var([r - ri for r, ri in zip(R1, Ri1)], ddof=1)
# #     var2 = np.var([r - ri for r, ri in zip(R2, Ri2)], ddof=1)
# #     w_statistic = ((n1 * n2) * (r2_mean - r1_mean)) / (
# #         (n1 + n2) * np.sqrt(n1 * var1 + n2 * var2)
# #     )
# #     if distribution == "t":
# #         dof = (n1 * var1 + n2 * var2) ** 2 / (
# #             (n1 * var1) ** 2 / (n1 - 1) + (n2 * var2) ** 2 / (n2 - 1)
# #         )
# #         c = (
# #             stats.t.cdf(abs(w_statistic), dof)
# #             if not np.isinf(w_statistic)
# #             else 0.0
# #         )
# #     if distribution == "normal":
# #         dof = np.nan
# #         c = (
# #             stats.norm.cdf(abs(w_statistic))
# #             if not np.isinf(w_statistic)
# #             else 0.0
# #         )
# #     p_value = min(c, 1.0 - c) * 2.0
# #     effsize = (r2_mean - r1_mean) / (n1 + n2) + 0.5
# #     return dict(
# #         w_statistic=round(w_statistic, round_factor),
# #         p_value=round(p_value, round_factor),
# #         n1=n1,
# #         n2=n2,
# #         dof=round(dof, round_factor),
# #         effsize=round(effsize, round_factor),
# #         test_name="Brunner-Munzel test",
# #         H0="The probability that a randomly selected value from one population is greater than a randomly selected value from the other population is equal to 0.5",
# #     )

# --------------------------------------------------------------------------------
# End of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/stats/tests/_brunner_munzel_test.py
# --------------------------------------------------------------------------------
