#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Comprehensive tests for scitex.stats module.

This module contains comprehensive tests for all statistical analysis utilities
in the scitex.stats module, covering descriptive statistics, correlation analysis,
multiple testing corrections, and various statistical tests.
"""

import pytest
import numpy as np
import pandas as pd
import warnings
import scitex.stats


class TestDescriptiveStatistics:
    """Test descriptive statistics functions."""

    def test_describe_basic(self):
        """Test basic describe functionality."""
        data = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        result = scitex.stats.describe(data)

        assert isinstance(result, dict)
        assert "mean" in result
        assert "std" in result
        assert "min" in result
        assert "max" in result
        assert result["mean"] == 5.5
        assert result["min"] == 1
        assert result["max"] == 10

    def test_describe_with_nan(self):
        """Test describe with NaN values."""
        data = np.array([1, 2, np.nan, 4, 5, np.nan, 7, 8, 9, 10])
        result = scitex.stats.describe(data)

        assert isinstance(result, dict)
        # Should handle NaN appropriately
        assert "mean" in result
        assert not np.isnan(result["mean"])

    def test_nan_statistics(self):
        """Test NaN-specific statistics."""
        data = np.array([1, 2, np.nan, 4, 5, np.nan, 7, 8, 9, 10])

        # Test nan counting/handling functions
        nan_info = scitex.stats.nan(data)
        assert "count" in nan_info
        assert "proportion" in nan_info
        assert nan_info["count"] == 2
        assert nan_info["proportion"] == 0.2

    def test_real_statistics(self):
        """Test statistics for real-valued data."""
        data = np.random.randn(100)

        # Test real number statistics
        real_stats = scitex.stats.real(data)
        assert "mean" in real_stats
        assert "median" in real_stats
        assert "std" in real_stats
        assert "skew" in real_stats
        assert "kurtosis" in real_stats


class TestCorrelationAnalysis:
    """Test correlation analysis functions."""

    def test_partial_correlation(self):
        """Test partial correlation calculation."""
        # Create correlated data
        n = 100
        x = np.random.randn(n)
        y = x + np.random.randn(n) * 0.5
        z = x + y + np.random.randn(n) * 0.5

        # Calculate partial correlation between x and y controlling for z
        partial_corr = scitex.stats.calc_partial_corr(x, y, z)

        assert isinstance(partial_corr, float)
        assert -1 <= partial_corr <= 1

    def test_partial_correlation_dataframe(self):
        """Test partial correlation with DataFrame input."""
        df = pd.DataFrame(
            {
                "x": np.random.randn(100),
                "y": np.random.randn(100),
                "z": np.random.randn(100),
            }
        )

        # Add correlation
        df["y"] = df["x"] + np.random.randn(100) * 0.5
        df["z"] = df["x"] + df["y"] + np.random.randn(100) * 0.5

        partial_corr = scitex.stats.calc_partial_corr(df["x"], df["y"], df["z"])
        assert isinstance(partial_corr, float)

    def test_correlation_test_single(self):
        """Test single correlation test."""
        x = np.random.randn(50)
        y = x + np.random.randn(50) * 0.5  # Correlated

        result = scitex.stats.corr_test(x, y)

        assert "correlation" in result
        assert "p_value" in result
        assert "confidence_interval" in result
        assert result["correlation"] > 0  # Should be positive
        assert 0 <= result["p_value"] <= 1

    def test_correlation_test_multiple(self):
        """Test correlation test with multiple comparisons."""
        # Create correlation matrix data
        n = 100
        data = pd.DataFrame(
            {"A": np.random.randn(n), "B": np.random.randn(n), "C": np.random.randn(n)}
        )

        # Add correlations
        data["B"] = data["A"] + np.random.randn(n) * 0.5
        data["C"] = data["B"] + np.random.randn(n) * 0.5

        result = scitex.stats.corr_test_multi(data)

        assert isinstance(result, pd.DataFrame)
        assert result.shape == (3, 3)  # Correlation matrix

    def test_no_correlation_test(self):
        """Test for absence of correlation."""
        x = np.random.randn(100)
        y = np.random.randn(100)  # Independent

        result = scitex.stats.nocorrelation_test(x, y)

        assert "statistic" in result
        assert "p_value" in result
        # With independent data, p-value should be high
        assert result["p_value"] > 0.05


class TestStatisticalTests:
    """Test various statistical tests."""

    def test_brunner_munzel_test(self):
        """Test Brunner-Munzel test for two samples."""
        # Create two samples with different distributions
        sample1 = np.random.normal(0, 1, 50)
        sample2 = np.random.normal(0.5, 1, 50)  # Shifted mean

        result = scitex.stats.brunner_munzel_test(sample1, sample2)

        assert "statistic" in result
        assert "p_value" in result
        assert 0 <= result["p_value"] <= 1

    def test_smirnov_grubbs_outlier_test(self):
        """Test Smirnov-Grubbs test for outliers."""
        # Create data with outlier
        data = np.random.normal(0, 1, 100)
        data = np.append(data, 10)  # Add outlier

        result = scitex.stats.smirnov_grubbs(data)

        assert "outliers" in result
        assert "test_statistic" in result
        assert "critical_value" in result
        assert len(result["outliers"]) > 0  # Should detect the outlier


class TestPValueFormatting:
    """Test p-value formatting functions."""

    def test_p2stars_basic(self):
        """Test p-value to stars conversion."""
        assert scitex.stats.p2stars(0.001) == "***"
        assert scitex.stats.p2stars(0.01) == "**"
        assert scitex.stats.p2stars(0.05) == "*"
        assert scitex.stats.p2stars(0.1) == "ns"
        assert scitex.stats.p2stars(0.5) == "ns"

    def test_p2stars_array(self):
        """Test p-value to stars conversion with array input."""
        p_values = np.array([0.001, 0.01, 0.05, 0.1, 0.5])
        stars = scitex.stats.p2stars(p_values)

        assert isinstance(stars, (list, np.ndarray))
        assert len(stars) == len(p_values)
        assert stars[0] == "***"
        assert stars[1] == "**"
        assert stars[2] == "*"
        assert stars[3] == "ns"
        assert stars[4] == "ns"

    def test_p2stars_custom_thresholds(self):
        """Test p-value to stars with custom thresholds."""
        # If function supports custom thresholds
        thresholds = [0.001, 0.01, 0.05]
        symbols = ["†††", "††", "†"]

        result = scitex.stats.p2stars(0.009, thresholds=thresholds, symbols=symbols)
        assert result == "††"


class TestMultipleTestingCorrections:
    """Test multiple testing correction methods."""

    def test_bonferroni_correction(self):
        """Test Bonferroni correction."""
        p_values = np.array([0.01, 0.04, 0.03, 0.05, 0.20])

        corrected = scitex.stats.bonferroni_correction(p_values)

        assert len(corrected) == len(p_values)
        assert all(corrected >= p_values)  # Corrected should be larger
        assert corrected[0] == 0.05  # 0.01 * 5
        assert corrected[4] == 1.0  # 0.20 * 5 = 1.0 (capped)

    def test_bonferroni_with_alpha(self):
        """Test Bonferroni correction with custom alpha."""
        p_values = np.array([0.01, 0.04, 0.03, 0.05, 0.20])
        alpha = 0.01

        result = scitex.stats.bonferroni_correction(p_values, alpha=alpha)

        if isinstance(result, dict):
            assert "corrected_p" in result
            assert "rejected" in result
            assert len(result["rejected"]) == len(p_values)

    def test_fdr_correction(self):
        """Test False Discovery Rate correction."""
        p_values = np.array([0.001, 0.008, 0.039, 0.041, 0.042, 0.074, 0.205])

        result = scitex.stats.fdr_correction(p_values)

        if isinstance(result, tuple):
            rejected, corrected = result
            assert len(rejected) == len(p_values)
            assert len(corrected) == len(p_values)
            assert all(isinstance(r, bool) for r in rejected)
        else:
            assert len(result) == len(p_values)

    def test_multicompair(self):
        """Test multiple comparison procedures."""
        # Create groups for comparison
        groups = []
        for i in range(4):
            groups.append(np.random.normal(i * 0.5, 1, 30))

        result = scitex.stats.multicompair(groups)

        assert isinstance(result, (dict, pd.DataFrame))
        if isinstance(result, dict):
            assert "p_values" in result
            assert "test_statistic" in result


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_data(self):
        """Test functions with empty data."""
        empty_array = np.array([])

        # Most functions should handle empty data gracefully
        with pytest.raises((ValueError, IndexError)):
            scitex.stats.describe(empty_array)

    def test_single_value(self):
        """Test functions with single value."""
        single_value = np.array([42])

        result = scitex.stats.describe(single_value)
        assert result["mean"] == 42
        assert result["std"] == 0

    def test_all_nan(self):
        """Test functions with all NaN values."""
        all_nan = np.array([np.nan, np.nan, np.nan])

        result = scitex.stats.nan(all_nan)
        assert result["count"] == 3
        assert result["proportion"] == 1.0

    def test_identical_values(self):
        """Test correlation with identical values."""
        x = np.ones(50)
        y = np.ones(50)

        # Correlation is undefined for constant arrays
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = scitex.stats.corr_test(x, y)
            # Should handle gracefully, possibly returning NaN


class TestIntegration:
    """Test integration scenarios combining multiple functions."""

    def test_complete_analysis_pipeline(self):
        """Test a complete statistical analysis pipeline."""
        # Generate experimental data
        np.random.seed(42)
        control = np.random.normal(100, 15, 50)
        treatment1 = np.random.normal(110, 15, 50)
        treatment2 = np.random.normal(105, 20, 50)
        treatment3 = np.random.normal(115, 18, 50)

        # Step 1: Descriptive statistics
        groups = {
            "control": control,
            "treatment1": treatment1,
            "treatment2": treatment2,
            "treatment3": treatment3,
        }

        descriptives = {}
        for name, data in groups.items():
            descriptives[name] = scitex.stats.describe(data)

        # Step 2: Multiple comparisons
        groups_list = [control, treatment1, treatment2, treatment3]
        comparison_result = scitex.stats.multicompair(groups_list)

        # Step 3: P-value corrections
        if isinstance(comparison_result, dict) and "p_values" in comparison_result:
            p_values = comparison_result["p_values"]
            bonf_corrected = scitex.stats.bonferroni_correction(p_values)
            fdr_corrected = scitex.stats.fdr_correction(p_values)

        # Step 4: Format results
        if "p_values" in locals():
            stars = scitex.stats.p2stars(p_values)

        # Verify pipeline completed
        assert len(descriptives) == 4
        assert all("mean" in desc for desc in descriptives.values())

    def test_correlation_analysis_pipeline(self):
        """Test correlation analysis with multiple variables."""
        # Create correlated data
        n = 200
        data = pd.DataFrame(
            {
                "age": np.random.uniform(20, 70, n),
                "income": np.random.exponential(50000, n),
                "education": np.random.randint(12, 20, n),
                "health_score": np.random.normal(75, 15, n),
            }
        )

        # Add correlations
        data["income"] += data["education"] * 5000
        data["health_score"] -= data["age"] * 0.5

        # Compute correlation matrix
        corr_matrix = scitex.stats.corr_test_multi(data)

        # Test partial correlations
        partial_corr_income_health = scitex.stats.calc_partial_corr(
            data["income"], data["health_score"], data["age"]
        )

        # Apply FDR correction to correlation p-values
        if hasattr(corr_matrix, "values"):
            p_values_flat = corr_matrix.values.flatten()
            fdr_results = scitex.stats.fdr_correction(p_values_flat)

        assert isinstance(partial_corr_income_health, float)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
