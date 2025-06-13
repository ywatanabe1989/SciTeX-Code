import pytest
import numpy as np
import pandas as pd
import scitex


class TestCalcPartialCorr:
    """Test partial correlation calculation function."""

    def test_import(self):
        """Test function can be imported."""
        assert hasattr(scitex.stats, "calc_partial_corr")

    def test_basic_partial_correlation(self):
        """Test basic partial correlation calculation."""
        # Create data with known relationships
        np.random.seed(42)
        n = 100
        
        # z influences both x and y
        z = np.random.randn(n)
        x = 0.7 * z + np.random.randn(n) * 0.5
        y = 0.6 * z + np.random.randn(n) * 0.5
        
        # Calculate partial correlation
        partial_corr = scitex.stats.calc_partial_corr(x, y, z)
        
        # Should be close to zero after removing z's influence
        assert isinstance(partial_corr, float)
        assert -1 <= partial_corr <= 1
        assert abs(partial_corr) < 0.3  # Should be small

    def test_perfect_mediation(self):
        """Test case where z perfectly mediates x-y relationship."""
        n = 100
        z = np.linspace(0, 10, n)
        x = 2 * z  # Perfect relationship with z
        y = 3 * z  # Perfect relationship with z
        
        # x and y are correlated only through z
        partial_corr = scitex.stats.calc_partial_corr(x, y, z)
        
        # Should be exactly 0 (or very close due to numerical precision)
        assert abs(partial_corr) < 1e-10

    def test_independent_control(self):
        """Test when control variable is independent."""
        np.random.seed(42)
        n = 100
        
        # x and y are correlated
        x = np.random.randn(n)
        y = 0.8 * x + np.random.randn(n) * 0.3
        
        # z is independent
        z = np.random.randn(n)
        
        # Regular correlation
        regular_corr = np.corrcoef(x, y)[0, 1]
        
        # Partial correlation should be similar to regular
        partial_corr = scitex.stats.calc_partial_corr(x, y, z)
        
        assert abs(partial_corr - regular_corr) < 0.1

    def test_negative_relationships(self):
        """Test with negative correlations."""
        np.random.seed(42)
        n = 100
        
        z = np.random.randn(n)
        x = -0.6 * z + np.random.randn(n) * 0.4
        y = 0.7 * z + np.random.randn(n) * 0.4
        
        partial_corr = scitex.stats.calc_partial_corr(x, y, z)
        
        # Should handle negative correlations correctly
        assert isinstance(partial_corr, float)
        assert -1 <= partial_corr <= 1

    def test_array_like_inputs(self):
        """Test with different array-like inputs."""
        n = 50
        
        # Lists
        x_list = list(np.random.randn(n))
        y_list = list(np.random.randn(n))
        z_list = list(np.random.randn(n))
        
        result_list = scitex.stats.calc_partial_corr(x_list, y_list, z_list)
        assert isinstance(result_list, float)
        
        # Pandas Series
        df = pd.DataFrame({
            'x': np.random.randn(n),
            'y': np.random.randn(n),
            'z': np.random.randn(n)
        })
        
        result_series = scitex.stats.calc_partial_corr(df['x'], df['y'], df['z'])
        assert isinstance(result_series, float)

    def test_edge_cases(self):
        """Test edge cases."""
        # Perfect correlations
        n = 100
        x = np.arange(n)
        y = x.copy()
        z = np.random.randn(n)
        
        partial_corr = scitex.stats.calc_partial_corr(x, y, z)
        assert partial_corr > 0.9  # Should still be highly correlated
        
        # All same values
        x_const = np.ones(n)
        y_const = np.ones(n)
        z_const = np.ones(n)
        
        # Should handle constant values gracefully
        with pytest.warns(RuntimeWarning):
            result = scitex.stats.calc_partial_corr(x_const, y_const, z_const)
            assert np.isnan(result) or result == 0

    def test_precision(self):
        """Test that high precision calculation works."""
        # The function uses float128 internally
        n = 100
        x = np.random.randn(n) * 1e-10  # Very small values
        y = np.random.randn(n) * 1e-10
        z = np.random.randn(n) * 1e-10
        
        partial_corr = scitex.stats.calc_partial_corr(x, y, z)
        
        # Should still return valid result
        assert isinstance(partial_corr, float)
        assert -1 <= partial_corr <= 1

    def test_real_world_example(self):
        """Test with a real-world scenario."""
        np.random.seed(42)
        n = 200
        
        # Age affects both income and health
        age = np.random.uniform(20, 70, n)
        
        # Income somewhat depends on age
        income = 20000 + 1000 * age + np.random.randn(n) * 10000
        
        # Health score somewhat depends on age (negative relationship)
        health = 100 - 0.5 * age + np.random.randn(n) * 10
        
        # Calculate correlations
        raw_corr = np.corrcoef(income, health)[0, 1]
        partial_corr = scitex.stats.calc_partial_corr(income, health, age)
        
        # Raw correlation should be negative (older -> more income but worse health)
        assert raw_corr < 0
        
        # Partial correlation should be closer to zero
        assert abs(partial_corr) < abs(raw_corr)


class TestPartialCorrValidation:
    """Test validation and error handling."""

    def test_mismatched_lengths(self):
        """Test with mismatched input lengths."""
        x = np.random.randn(100)
        y = np.random.randn(90)  # Different length
        z = np.random.randn(100)
        
        # Should raise an error or handle gracefully
        with pytest.raises((ValueError, Exception)):
            scitex.stats.calc_partial_corr(x, y, z)

    def test_minimum_samples(self):
        """Test with minimum number of samples."""
        # Need at least 3 samples for correlation
        x = [1, 2, 3]
        y = [2, 3, 4]
        z = [3, 4, 5]
        
        result = scitex.stats.calc_partial_corr(x, y, z)
        assert isinstance(result, float)

    def test_single_sample(self):
        """Test with single sample."""
        x = [1]
        y = [2]
        z = [3]
        
        # Should handle edge case
        with pytest.raises((ValueError, Exception)):
            scitex.stats.calc_partial_corr(x, y, z)


if __name__ == "__main__":
    import os

    pytest.main([os.path.abspath(__file__), "-v"])

# --------------------------------------------------------------------------------
# Start of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/stats/_calc_partial_corr.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
#
# import numpy as np
#
#
# def calc_partial_corr(x, y, z):
#     """remove the influence of the variable z from the correlation between x and y."""
#
#     x = np.array(x).astype(np.float128)
#     y = np.array(y).astype(np.float128)
#     z = np.array(z).astype(np.float128)
#
#     r_xy = np.corrcoef(x, y)[0, 1]
#     r_xz = np.corrcoef(x, z)[0, 1]
#     r_yz = np.corrcoef(y, z)[0, 1]
#     r_xy_z = (r_xy - r_xz * r_yz) / (np.sqrt(1 - r_xz**2) * np.sqrt(1 - r_yz**2))
#     return float(r_xy_z)

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/_scitex_repo/src/scitex/stats/_calc_partial_corr.py
# --------------------------------------------------------------------------------
