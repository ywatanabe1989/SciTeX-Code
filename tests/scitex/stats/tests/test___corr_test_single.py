#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-08 05:52:10 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/stats/tests/test___corr_test_single.py

"""
Tests for single correlation test functions.
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch
from scipy import stats

from scitex.stats.tests import (
    _corr_test_base,
    corr_test_spearman,
    corr_test_pearson,
    corr_test
)


class TestCorrTestBase:
    """Test _corr_test_base function."""
    
    def test_corr_test_base_pearson(self):
        """Test base correlation test with Pearson."""
        data1 = np.array([1, 2, 3, 4, 5])
        data2 = np.array([2, 4, 6, 8, 10])
        
        with patch('builtins.print'):
            result = _corr_test_base(
                data1, data2, 
                only_significant=False,
                num_permutations=100,
                seed=42,
                corr_func=stats.pearsonr,
                test_name="Pearson"
            )
        
        assert "p_value" in result
        assert "corr" in result
        assert result["corr"] == 1.0  # Perfect correlation
        assert result["test_name"] == "Permutation-based Pearson correlation"
        assert result["n"] == 5
    
    def test_corr_test_base_spearman(self):
        """Test base correlation test with Spearman."""
        data1 = np.array([1, 2, 3, 4, 5])
        data2 = np.array([1, 3, 2, 5, 4])
        
        with patch('builtins.print'):
            result = _corr_test_base(
                data1, data2,
                only_significant=False,
                num_permutations=100,
                seed=42,
                corr_func=stats.spearmanr,
                test_name="Spearman"
            )
        
        assert "p_value" in result
        assert "corr" in result
        assert "surrogate" in result
        assert len(result["surrogate"]) == 100
        assert result["test_name"] == "Permutation-based Spearman correlation"
    
    def test_corr_test_base_with_nans(self):
        """Test handling of NaN values."""
        data1 = np.array([1, 2, np.nan, 4, 5])
        data2 = np.array([2, np.nan, 6, 8, 10])
        
        with patch('builtins.print'):
            result = _corr_test_base(
                data1, data2,
                only_significant=False,
                num_permutations=50,
                seed=42,
                corr_func=stats.pearsonr,
                test_name="Pearson"
            )
        
        # Should only use non-NaN pairs
        assert result["n"] == 3  # Only indices 0, 3, 4 are valid
    
    def test_corr_test_base_only_significant(self):
        """Test only_significant parameter."""
        data1 = np.random.RandomState(42).randn(50)
        data2 = np.random.RandomState(43).randn(50)
        
        with patch('builtins.print') as mock_print:
            result = _corr_test_base(
                data1, data2,
                only_significant=True,
                num_permutations=100,
                seed=42,
                corr_func=stats.pearsonr,
                test_name="Pearson"
            )
        
        # Should only print if p < 0.05
        if result["p_value"] >= 0.05:
            mock_print.assert_not_called()
        else:
            mock_print.assert_called_once()
    
    def test_corr_test_base_effect_size(self):
        """Test effect size calculation."""
        data1 = np.array([1, 2, 3, 4, 5])
        data2 = np.array([5, 4, 3, 2, 1])  # Negative correlation
        
        with patch('builtins.print'):
            result = _corr_test_base(
                data1, data2,
                only_significant=False,
                num_permutations=100,
                seed=42,
                corr_func=stats.pearsonr,
                test_name="Pearson"
            )
        
        # Effect size should be absolute value of correlation
        assert result["effsize"] == abs(result["corr"])
        assert result["corr"] == -1.0
        assert result["effsize"] == 1.0
    
    def test_corr_test_base_p_value_calculation(self):
        """Test p-value calculation logic."""
        # Create data with known moderate correlation
        np.random.seed(42)
        data1 = np.arange(20)
        data2 = data1 + np.random.normal(0, 2, 20)
        
        with patch('builtins.print'):
            result = _corr_test_base(
                data1, data2,
                only_significant=False,
                num_permutations=1000,
                seed=42,
                corr_func=stats.pearsonr,
                test_name="Pearson"
            )
        
        # P-value should be between 0 and 1
        assert 0 <= result["p_value"] <= 1
        # Surrogate should have expected number of permutations
        assert len(result["surrogate"]) == 1000


class TestCorrTestSpearman:
    """Test corr_test_spearman function."""
    
    def test_spearman_basic(self):
        """Test basic Spearman correlation."""
        data1 = np.array([1, 2, 3, 4, 5])
        data2 = np.array([1, 3, 2, 5, 4])
        
        with patch('builtins.print'):
            result = corr_test_spearman(data1, data2, seed=42)
        
        assert result["test_name"] == "Permutation-based Spearman correlation"
        assert "corr" in result
        assert "p_value" in result
        assert result["n"] == 5
    
    def test_spearman_perfect_monotonic(self):
        """Test Spearman with perfect monotonic relationship."""
        data1 = np.array([1, 2, 3, 4, 5])
        data2 = np.array([10, 20, 30, 40, 50])  # Perfect monotonic
        
        with patch('builtins.print'):
            result = corr_test_spearman(data1, data2, num_permutations=100, seed=42)
        
        assert result["corr"] == 1.0
        # P-value should be very small for perfect correlation
        assert result["p_value"] < 0.05
    
    def test_spearman_parameters(self):
        """Test parameter passing."""
        data1 = np.random.randn(20)
        data2 = np.random.randn(20)
        
        with patch('scitex.stats.tests.__corr_test_single._corr_test_base') as mock_base:
            mock_base.return_value = {"test": "result"}
            
            corr_test_spearman(
                data1, data2,
                only_significant=True,
                num_permutations=500,
                seed=123
            )
            
            # Verify parameters were passed correctly
            mock_base.assert_called_once()
            args = mock_base.call_args[0]
            assert args[2] == True  # only_significant
            assert args[3] == 500   # num_permutations
            assert args[4] == 123   # seed
            assert args[5] == stats.spearmanr
            assert args[6] == "Spearman"


class TestCorrTestPearson:
    """Test corr_test_pearson function."""
    
    def test_pearson_basic(self):
        """Test basic Pearson correlation."""
        data1 = np.array([1, 2, 3, 4, 5])
        data2 = np.array([2, 4, 6, 8, 10])
        
        with patch('builtins.print'):
            result = corr_test_pearson(data1, data2, seed=42)
        
        assert result["test_name"] == "Permutation-based Pearson correlation"
        assert result["corr"] == 1.0  # Perfect linear correlation
        assert result["p_value"] < 0.05
    
    def test_pearson_negative_correlation(self):
        """Test Pearson with negative correlation."""
        data1 = np.array([1, 2, 3, 4, 5])
        data2 = np.array([5, 4, 3, 2, 1])
        
        with patch('builtins.print'):
            result = corr_test_pearson(data1, data2, num_permutations=100, seed=42)
        
        assert result["corr"] == -1.0
        assert result["effsize"] == 1.0  # Absolute value
    
    def test_pearson_no_correlation(self):
        """Test Pearson with no correlation."""
        np.random.seed(42)
        data1 = np.random.randn(100)
        data2 = np.random.randn(100)
        
        with patch('builtins.print'):
            result = corr_test_pearson(data1, data2, num_permutations=100, seed=42)
        
        # Should have low correlation and high p-value
        assert abs(result["corr"]) < 0.2
        assert result["p_value"] > 0.05
    
    def test_pearson_parameters(self):
        """Test parameter passing."""
        data1 = np.random.randn(20)
        data2 = np.random.randn(20)
        
        with patch('scitex.stats.tests.__corr_test_single._corr_test_base') as mock_base:
            mock_base.return_value = {"test": "result"}
            
            corr_test_pearson(
                data1, data2,
                only_significant=True,
                num_permutations=200,
                seed=456
            )
            
            # Verify parameters were passed correctly
            mock_base.assert_called_once()
            args = mock_base.call_args[0]
            assert args[2] == True  # only_significant
            assert args[3] == 200   # num_permutations
            assert args[4] == 456   # seed
            assert args[5] == stats.pearsonr
            assert args[6] == "Pearson"


class TestCorrTest:
    """Test main corr_test function."""
    
    def test_corr_test_pearson_default(self):
        """Test default Pearson correlation."""
        data1 = np.array([1, 2, 3, 4, 5])
        data2 = np.array([2, 4, 6, 8, 10])
        
        with patch('builtins.print'):
            result = corr_test(data1, data2)
        
        assert result["test_name"] == "Permutation-based Pearson correlation"
        assert result["corr"] == 1.0
    
    def test_corr_test_spearman_selection(self):
        """Test Spearman selection."""
        data1 = np.array([1, 2, 3, 4, 5])
        data2 = np.array([1, 3, 2, 5, 4])
        
        with patch('builtins.print'):
            result = corr_test(data1, data2, test="spearman")
        
        assert result["test_name"] == "Permutation-based Spearman correlation"
    
    def test_corr_test_invalid_test(self):
        """Test invalid test type."""
        data1 = np.array([1, 2, 3])
        data2 = np.array([4, 5, 6])
        
        with pytest.raises(ValueError, match="Invalid test type"):
            corr_test(data1, data2, test="kendall")
    
    def test_corr_test_parameter_forwarding(self):
        """Test that parameters are forwarded correctly."""
        data1 = np.random.randn(20)
        data2 = np.random.randn(20)
        
        # Test Pearson forwarding
        with patch('scitex.stats.tests.__corr_test_single.corr_test_pearson') as mock_pearson:
            mock_pearson.return_value = {"test": "pearson_result"}
            
            result = corr_test(
                data1, data2,
                test="pearson",
                only_significant=True,
                num_permutations=300,
                seed=789
            )
            
            mock_pearson.assert_called_once_with(
                data1, data2, True, 300, 789
            )
            assert result == {"test": "pearson_result"}
        
        # Test Spearman forwarding
        with patch('scitex.stats.tests.__corr_test_single.corr_test_spearman') as mock_spearman:
            mock_spearman.return_value = {"test": "spearman_result"}
            
            result = corr_test(
                data1, data2,
                test="spearman",
                only_significant=False,
                num_permutations=150,
                seed=321
            )
            
            mock_spearman.assert_called_once_with(
                data1, data2, False, 150, 321
            )
            assert result == {"test": "spearman_result"}
    
    def test_corr_test_example_data(self):
        """Test with the example data from docstring."""
        xx = np.array([3, 4, 4, 5, 7, 8, 10, 12, 13, 15])
        yy = np.array([2, 4, 4, 5, 4, 7, 8, 19, 14, 10])
        
        with patch('builtins.print'):
            # Test Pearson
            result_pearson = corr_test(xx, yy, test="pearson", seed=42)
            assert "corr" in result_pearson
            assert "p_value" in result_pearson
            assert result_pearson["n"] == 10
            
            # Test Spearman
            result_spearman = corr_test(xx, yy, test="spearman", seed=42)
            assert "corr" in result_spearman
            assert "p_value" in result_spearman
            assert result_spearman["n"] == 10
    
    def test_corr_test_output_format(self):
        """Test the output format and required fields."""
        data1 = np.random.randn(50)
        data2 = data1 + np.random.randn(50) * 0.5  # Add noise
        
        with patch('builtins.print'):
            result = corr_test(data1, data2, num_permutations=100, seed=42)
        
        # Check all required fields are present
        required_fields = [
            "p_value", "stars", "effsize", "corr", 
            "surrogate", "n", "test_name", "statistic", "H0"
        ]
        for field in required_fields:
            assert field in result
        
        # Check field types
        assert isinstance(result["p_value"], float)
        assert isinstance(result["stars"], str)
        assert isinstance(result["effsize"], float)
        assert isinstance(result["corr"], float)
        assert isinstance(result["surrogate"], np.ndarray)
        assert isinstance(result["n"], int)
        assert isinstance(result["test_name"], str)
        assert isinstance(result["statistic"], float)
        assert isinstance(result["H0"], str)
        
        # Check H0 hypothesis text
        assert "no pearson correlation" in result["H0"].lower()


if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])
