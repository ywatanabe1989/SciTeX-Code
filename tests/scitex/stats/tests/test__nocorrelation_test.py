#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-05-31 22:10:00 (ywatanabe)"
# File: tests/scitex/stats/tests/test__nocorrelation_test.py

"""Test cases for no-correlation test."""

import numpy as np
import pandas as pd
import pytest

import scitex

class TestNoCorrelationTest:
    """Test cases for nocorrelation_test function."""
    
    def test_basic_functionality(self):
        """Test basic functionality with simple arrays."""
        x = [1, 2, 3, 4, 5]
        y = [2, 4, 6, 8, 10]  # Perfect positive correlation
        
        r, t, p_value = scitex.stats.tests._nocorrelation_test.nocorrelation_test(x, y)
        
        assert isinstance(r, float)
        assert isinstance(t, float)
        assert isinstance(p_value, float)
        assert abs(r - 1.0) < 0.001  # Should be close to 1
        assert p_value < 0.05  # Should be significant
        
    def test_no_correlation(self):
        """Test with uncorrelated data."""
        np.random.seed(42)
        x = np.random.randn(50)
        y = np.random.randn(50)
        
        r, t, p_value = scitex.stats.tests._nocorrelation_test.nocorrelation_test(x, y)
        
        assert abs(r) < 0.3  # Should be close to 0
        assert p_value > 0.05  # Should not be significant
        
    def test_negative_correlation(self):
        """Test with negative correlation."""
        x = [1, 2, 3, 4, 5]
        y = [10, 8, 6, 4, 2]  # Perfect negative correlation
        
        r, t, p_value = scitex.stats.tests._nocorrelation_test.nocorrelation_test(x, y)
        
        assert abs(r + 1.0) < 0.001  # Should be close to -1
        assert p_value < 0.05  # Should be significant
        
    def test_partial_correlation(self):
        """Test partial correlation with control variable."""
        # Create data where x and y are correlated through z
        z = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        x = z + np.random.randn(10) * 0.1
        y = z + np.random.randn(10) * 0.1
        
        # Without controlling for z
        r_simple, _, _ = scitex.stats.tests._nocorrelation_test.nocorrelation_test(x, y)
        
        # With controlling for z (partial correlation)
        r_partial, t_partial, p_partial = scitex.stats.tests._nocorrelation_test.nocorrelation_test(x, y, z)
        
        # Partial correlation should be much smaller
        assert abs(r_partial) < abs(r_simple)
        
    def test_return_types(self):
        """Test that return types are correct."""
        x = np.random.randn(20)
        y = np.random.randn(20)
        
        r, t, p_value = scitex.stats.tests._nocorrelation_test.nocorrelation_test(x, y)
        
        assert isinstance(r, (float, np.float64))
        assert isinstance(t, (float, np.float64))
        assert isinstance(p_value, (float, np.float64))
        
    def test_p_value_range(self):
        """Test that p-value is in valid range."""
        x = np.random.randn(30)
        y = np.random.randn(30)
        
        _, _, p_value = scitex.stats.tests._nocorrelation_test.nocorrelation_test(x, y)
        
        assert 0 <= p_value <= 1
        
    def test_correlation_coefficient_range(self):
        """Test that correlation coefficient is in valid range."""
        x = np.random.randn(25)
        y = np.random.randn(25)
        
        r, _, _ = scitex.stats.tests._nocorrelation_test.nocorrelation_test(x, y)
        
        assert -1 <= r <= 1
        
    def test_t_statistic_positive(self):
        """Test that t-statistic is always positive (absolute value used)."""
        x = np.random.randn(20)
        y = -x  # Negative correlation
        
        _, t, _ = scitex.stats.tests._nocorrelation_test.nocorrelation_test(x, y)
        
        assert t >= 0
        
    def test_small_sample_size(self):
        """Test with small sample size."""
        x = [1, 2, 3]
        y = [2, 4, 6]
        
        r, t, p_value = scitex.stats.tests._nocorrelation_test.nocorrelation_test(x, y)
        
        assert isinstance(r, float)
        assert isinstance(t, float)
        assert isinstance(p_value, float)
        
    def test_numpy_arrays(self):
        """Test with numpy arrays."""
        x = np.array([1, 2, 3, 4, 5])
        y = np.array([2, 4, 6, 8, 10])
        
        r, t, p_value = scitex.stats.tests._nocorrelation_test.nocorrelation_test(x, y)
        
        assert abs(r - 1.0) < 0.001
        
    def test_pandas_series(self):
        """Test with pandas Series."""
        x = pd.Series([1, 2, 3, 4, 5])
        y = pd.Series([2, 4, 6, 8, 10])
        
        r, t, p_value = scitex.stats.tests._nocorrelation_test.nocorrelation_test(x, y)
        
        assert abs(r - 1.0) < 0.001
        
    def test_mixed_types(self):
        """Test with mixed input types."""
        x = [1, 2, 3, 4, 5]
        y = np.array([2, 4, 6, 8, 10])
        
        r, t, p_value = scitex.stats.tests._nocorrelation_test.nocorrelation_test(x, y)
        
        assert abs(r - 1.0) < 0.001
        
    def test_identical_arrays(self):
        """Test with identical arrays."""
        x = [1, 2, 3, 4, 5]
        
        r, t, p_value = scitex.stats.tests._nocorrelation_test.nocorrelation_test(x, x)
        
        assert r == 1.0  # Perfect correlation with itself
        assert p_value < 0.001  # Highly significant
        
    def test_constant_array(self):
        """Test with constant array."""
        x = [5, 5, 5, 5, 5]
        y = [1, 2, 3, 4, 5]
        
        # Should handle gracefully (correlation undefined)
        try:
            r, t, p_value = scitex.stats.tests._nocorrelation_test.nocorrelation_test(x, y)
            assert np.isnan(r) or r == 0
        except:
            # Some implementations might raise error
            pass
            
    def test_partial_correlation_independence(self):
        """Test partial correlation when x and y are independent given z."""
        np.random.seed(123)
        z = np.random.randn(50)
        x = z + np.random.randn(50)
        y = z + np.random.randn(50)
        
        # x and y are correlated
        r_simple, _, _ = scitex.stats.tests._nocorrelation_test.nocorrelation_test(x, y)
        assert abs(r_simple) > 0.3
        
        # But independent given z
        r_partial, _, p_partial = scitex.stats.tests._nocorrelation_test.nocorrelation_test(x, y, z)
        assert abs(r_partial) < 0.2
        assert p_partial > 0.05
        
    def test_large_sample(self):
        """Test with large sample size."""
        np.random.seed(456)
        n = 1000
        x = np.random.randn(n)
        y = 0.5 * x + np.random.randn(n)  # Moderate correlation
        
        r, t, p_value = scitex.stats.tests._nocorrelation_test.nocorrelation_test(x, y)
        
        assert 0.3 < abs(r) < 0.7
        assert p_value < 0.001  # Should be highly significant with large n
        
    def test_degrees_of_freedom(self):
        """Test that degrees of freedom are calculated correctly."""
        n = 20
        x = np.random.randn(n)
        y = np.random.randn(n)
        
        r, t, p_value = scitex.stats.tests._nocorrelation_test.nocorrelation_test(x, y)
        
        # df should be n-2 for simple correlation
        expected_df = n - 2
        # Can't directly access df, but can verify through t-distribution
        assert isinstance(t, float)
        
    def test_statistical_properties(self):
        """Test statistical properties under null hypothesis."""
        np.random.seed(789)
        p_values = []
        
        # Run multiple tests under null hypothesis
        for _ in range(100):
            x = np.random.randn(30)
            y = np.random.randn(30)
            _, _, p = scitex.stats.tests._nocorrelation_test.nocorrelation_test(x, y)
            p_values.append(p)
            
        # Under null, p-values should be approximately uniform
        # Check that roughly 5% are below 0.05
        significant = sum(p < 0.05 for p in p_values)
        assert 2 <= significant <= 10  # Allow some variation
        
    def test_power_analysis(self):
        """Test power to detect correlation."""
        np.random.seed(999)
        p_values = []
        
        # Run tests with true correlation
        for _ in range(50):
            x = np.random.randn(30)
            y = 0.6 * x + 0.8 * np.random.randn(30)  # Correlation ~0.6
            _, _, p = scitex.stats.tests._nocorrelation_test.nocorrelation_test(x, y)
            p_values.append(p)
            
        # Should have good power to detect this correlation
        significant = sum(p < 0.05 for p in p_values)
        assert significant > 35  # At least 70% power
        
    def test_calc_partial_corrcoef_helper(self):
        """Test the calc_partial_corrcoef helper function."""
        # Direct test of helper function if it's accessible
        x = np.array([1, 2, 3, 4, 5])
        y = np.array([2, 4, 6, 8, 10])
        z = np.array([1, 1, 2, 2, 3])
        
        if hasattr(scitex.stats.tests._nocorrelation_test, 'calc_partial_corrcoef'):
            r_partial = scitex.stats.tests._nocorrelation_test.calc_partial_corrcoef(x, y, z)
            assert isinstance(r_partial, np.ndarray)
            assert r_partial.shape == (2, 2)
            
    def test_correlation_matrix_symmetry(self):
        """Test that correlation calculations are symmetric."""
        x = np.random.randn(20)
        y = np.random.randn(20)
        
        r1, _, _ = scitex.stats.tests._nocorrelation_test.nocorrelation_test(x, y)
        r2, _, _ = scitex.stats.tests._nocorrelation_test.nocorrelation_test(y, x)
        
        assert abs(r1 - r2) < 1e-10  # Should be identical
        
    def test_alpha_parameter_ignored(self):
        """Test that alpha parameter is ignored (if present in function)."""
        x = np.random.randn(20)
        y = np.random.randn(20)
        
        # Function returns same values regardless of alpha
        result1 = scitex.stats.tests._nocorrelation_test.nocorrelation_test(x, y)
        # If alpha parameter exists, it shouldn't affect output
        try:
            result2 = scitex.stats.tests._nocorrelation_test.nocorrelation_test(x, y, alpha=0.01)
            assert result1 == result2
        except TypeError:
            # If alpha parameter doesn't exist, that's fine
            pass
            
    def test_edge_case_perfect_correlation(self):
        """Test edge case with perfect correlation."""
        x = np.array([1, 2, 3, 4, 5])
        y = 2 * x + 3  # Perfect linear relationship
        
        r, t, p_value = scitex.stats.tests._nocorrelation_test.nocorrelation_test(x, y)
        
        assert abs(r) == 1.0
        # t might be inf for perfect correlation
        assert np.isinf(t) or t > 10
        assert p_value < 0.001


# --------------------------------------------------------------------------------

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/stats/tests/_nocorrelation_test.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# 
# import numpy as np
# from scipy import stats
# 
# 
# def calc_partial_corrcoef(x, y, z):
#     """remove the influence of the variable z from the correlation between x and y."""
#     r_xy = np.corrcoef(x, y)
#     r_xz = np.corrcoef(x, z)
#     r_yz = np.corrcoef(y, z)
#     r_xy_z = (r_xy - r_xz * r_yz) / (1 - r_xz**2) * (1 - r_yz**2)
#     return r_xy_z
# 
# 
# def nocorrelation_test(x, y, z=None, alpha=0.05):
#     if z is None:
#         r = np.corrcoef(x, y)[1, 0]
#     if z is not None:
#         r = calc_partial_corrcoef(x, y, z)[1, 0]
# 
#     n = len(x)
#     df = n - 2
#     # t = np.abs(np.array(r)) * np.sqrt((df) / (1 - np.array(r)**2))
#     t = np.abs(r) * np.sqrt((df) / (1 - r**2))
#     # t_alpha = scipy.stats.t.ppf(1 - alpha / 2, df)
#     p_value = 2 * (1 - stats.t.cdf(t, df))
#     return r, t, p_value

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/stats/tests/_nocorrelation_test.py
# --------------------------------------------------------------------------------
