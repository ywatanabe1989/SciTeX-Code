#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-09 21:30:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/tests/scitex/stats/multiple/test__fdr_correction_enhanced.py
# ----------------------------------------
"""
Enhanced test suite for FDR correction with comprehensive testing patterns.

Tests the False Discovery Rate correction implementation with:
- Property-based testing
- Performance benchmarks
- Statistical correctness verification
- Edge cases and error handling
"""

import warnings
from unittest.mock import patch, MagicMock

import numpy as np
import pytest
from hypothesis import given, strategies as st, assume, settings
from scipy import stats as scipy_stats

import scitex
from scitex.stats.multiple import fdr_correction


# ----------------------------------------
# Fixtures
# ----------------------------------------

@pytest.fixture
def p_value_scenarios():
    """Various p-value scenarios for testing."""
    n = 100
    
    return {
        'uniform': np.random.uniform(0, 1, n),  # All null true
        'mixed': np.concatenate([
            np.random.beta(0.5, 10, 20),  # True effects (small p-values)
            np.random.uniform(0, 1, 80)    # Null effects
        ]),
        'all_significant': np.random.beta(0.5, 10, n),  # All effects
        'all_null': np.random.uniform(0.2, 1, n),      # No effects
        'borderline': np.random.uniform(0.04, 0.06, n), # Around alpha
        'sparse': np.concatenate([
            np.array([0.001, 0.002, 0.003]),  # Few strong effects
            np.random.uniform(0.1, 1, n-3)     # Rest null
        ]),
        'dense': np.random.beta(2, 5, n),  # Many moderate effects
    }


@pytest.fixture
def simulation_data():
    """Simulate multiple testing scenario with known ground truth."""
    n_tests = 1000
    n_true_effects = 100  # 10% true effects
    
    # Generate true labels
    true_effects = np.zeros(n_tests, dtype=bool)
    true_indices = np.random.choice(n_tests, n_true_effects, replace=False)
    true_effects[true_indices] = True
    
    # Generate p-values
    p_values = np.zeros(n_tests)
    
    # True effects: small p-values from beta distribution
    p_values[true_effects] = np.random.beta(0.5, 10, n_true_effects)
    
    # Null effects: uniform distribution
    p_values[~true_effects] = np.random.uniform(0, 1, n_tests - n_true_effects)
    
    return {
        'p_values': p_values,
        'true_effects': true_effects,
        'n_tests': n_tests,
        'n_true': n_true_effects,
    }


# ----------------------------------------
# Basic Functionality Tests
# ----------------------------------------

class TestBasicFunctionality:
    """Test basic FDR correction functionality."""
    
    def test_simple_correction(self):
        """Test basic FDR correction."""
        p_values = np.array([0.001, 0.008, 0.039, 0.041, 0.042, 0.06, 0.074, 0.205, 0.212, 0.216])
        
        # Apply FDR correction
        reject, p_adjusted = fdr_correction(p_values, alpha=0.05)
        
        # Basic checks
        assert len(reject) == len(p_values)
        assert len(p_adjusted) == len(p_values)
        assert reject.dtype == bool
        
        # Monotonicity of adjusted p-values
        assert all(p_adjusted[i] <= p_adjusted[i+1] for i in range(len(p_adjusted)-1))
        
        # Adjusted p-values should be >= original
        assert all(p_adjusted >= p_values)
        
    def test_known_example(self):
        """Test with known example from literature."""
        # Example from Benjamini & Hochberg (1995)
        p_values = np.array([0.0001, 0.0004, 0.0019, 0.0095, 0.0201, 
                            0.0278, 0.0298, 0.0344, 0.0459, 0.3240, 
                            0.4262, 0.5719, 0.6528, 0.7590, 1.000])
        
        reject, p_adjusted = fdr_correction(p_values, alpha=0.05)
        
        # First 4 should be rejected at alpha=0.05
        expected_rejects = 4
        assert np.sum(reject) == expected_rejects
        assert all(reject[:expected_rejects])
        assert not any(reject[expected_rejects:])
        
    @pytest.mark.parametrize("method", ['fdr_bh', 'fdr_by', 'fdr_tsbh', 'fdr_tsbky'])
    def test_different_methods(self, method):
        """Test different FDR methods."""
        p_values = np.random.uniform(0, 1, 100)
        p_values[:10] = np.random.beta(0.5, 10, 10)  # Add some small p-values
        
        reject, p_adjusted = fdr_correction(p_values, alpha=0.05, method=method)
        
        # Should return valid results
        assert len(reject) == len(p_values)
        assert len(p_adjusted) == len(p_values)
        
        # Method-specific checks
        if method == 'fdr_by':
            # BY is more conservative than BH
            reject_bh, _ = fdr_correction(p_values, alpha=0.05, method='fdr_bh')
            assert np.sum(reject) <= np.sum(reject_bh)


# ----------------------------------------
# Parametrized Tests
# ----------------------------------------

class TestParametrized:
    """Parametrized tests for comprehensive coverage."""
    
    @pytest.mark.parametrize("n_tests", [10, 100, 1000, 10000])
    def test_different_sizes(self, n_tests):
        """Test with different numbers of tests."""
        p_values = np.random.uniform(0, 1, n_tests)
        
        reject, p_adjusted = fdr_correction(p_values)
        
        assert len(reject) == n_tests
        assert len(p_adjusted) == n_tests
        
    @pytest.mark.parametrize("alpha", [0.01, 0.05, 0.10, 0.20])
    def test_different_alpha_levels(self, alpha):
        """Test with different significance levels."""
        p_values = np.random.uniform(0, 1, 100)
        p_values[:20] = np.random.beta(0.5, 10, 20)
        
        reject, p_adjusted = fdr_correction(p_values, alpha=alpha)
        
        # More rejections with higher alpha
        if alpha > 0.05:
            reject_05, _ = fdr_correction(p_values, alpha=0.05)
            assert np.sum(reject) >= np.sum(reject_05)
            
    @pytest.mark.parametrize("is_sorted", [True, False])
    def test_sorted_input(self, is_sorted):
        """Test with sorted vs unsorted input."""
        p_values = np.random.uniform(0, 1, 100)
        
        if is_sorted:
            p_values = np.sort(p_values)
            reject, p_adjusted = fdr_correction(p_values, is_sorted=True)
        else:
            reject, p_adjusted = fdr_correction(p_values, is_sorted=False)
            
        # Results should be valid regardless
        assert len(reject) == len(p_values)
        assert all(p_adjusted >= p_values)


# ----------------------------------------
# Property-Based Tests
# ----------------------------------------

class TestPropertyBased:
    """Property-based tests using Hypothesis."""
    
    @given(
        p_values=st.lists(
            st.floats(min_value=0.0, max_value=1.0),
            min_size=1,
            max_size=1000
        ).map(np.array),
        alpha=st.floats(min_value=0.01, max_value=0.20)
    )
    @settings(max_examples=50, deadline=5000)
    def test_fdr_properties(self, p_values, alpha):
        """Test fundamental properties of FDR correction."""
        assume(not np.any(np.isnan(p_values)))
        
        reject, p_adjusted = fdr_correction(p_values, alpha=alpha)
        
        # Property 1: Adjusted p-values are non-decreasing
        sorted_idx = np.argsort(p_values)
        p_adj_sorted = p_adjusted[sorted_idx]
        assert all(p_adj_sorted[i] <= p_adj_sorted[i+1] for i in range(len(p_adj_sorted)-1))
        
        # Property 2: Adjusted p-values >= original p-values
        assert all(p_adjusted >= p_values)
        
        # Property 3: Rejected p-values have adjusted p <= alpha
        assert all(p_adjusted[reject] <= alpha + 1e-10)  # Small tolerance
        
        # Property 4: Non-rejected p-values have adjusted p > alpha
        assert all(p_adjusted[~reject] > alpha - 1e-10)
        
    @given(
        n_tests=st.integers(min_value=10, max_value=1000),
        prop_true=st.floats(min_value=0.0, max_value=0.5)
    )
    def test_power_control(self, n_tests, prop_true):
        """Test that FDR control is maintained."""
        # Generate scenario
        n_true = int(n_tests * prop_true)
        n_null = n_tests - n_true
        
        # Generate p-values
        if n_true > 0:
            p_true = np.random.beta(0.5, 10, n_true)
        else:
            p_true = np.array([])
            
        p_null = np.random.uniform(0, 1, n_null)
        p_values = np.concatenate([p_true, p_null])
        
        # Track which are truly null
        is_null = np.concatenate([np.zeros(n_true, dtype=bool), 
                                 np.ones(n_null, dtype=bool)])
        
        # Apply FDR
        alpha = 0.05
        reject, _ = fdr_correction(p_values, alpha=alpha)
        
        # Calculate false discovery proportion
        if np.sum(reject) > 0:
            fdp = np.sum(reject & is_null) / np.sum(reject)
            # FDR should control expected FDP
            # In practice, we check it's not too high
            assert fdp <= alpha * 2  # Allow some variance


# ----------------------------------------
# Edge Cases and Error Handling
# ----------------------------------------

class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_empty_input(self):
        """Test with empty input."""
        p_values = np.array([])
        reject, p_adjusted = fdr_correction(p_values)
        
        assert len(reject) == 0
        assert len(p_adjusted) == 0
        
    def test_single_p_value(self):
        """Test with single p-value."""
        p_values = np.array([0.03])
        reject, p_adjusted = fdr_correction(p_values, alpha=0.05)
        
        assert len(reject) == 1
        assert reject[0] == True
        assert p_adjusted[0] == 0.03
        
    def test_all_p_values_one(self):
        """Test when all p-values are 1."""
        p_values = np.ones(100)
        reject, p_adjusted = fdr_correction(p_values)
        
        assert not any(reject)
        assert all(p_adjusted == 1.0)
        
    def test_all_p_values_zero(self):
        """Test when all p-values are 0."""
        p_values = np.zeros(100)
        reject, p_adjusted = fdr_correction(p_values)
        
        assert all(reject)
        assert all(p_adjusted == 0.0)
        
    def test_nan_values(self):
        """Test handling of NaN values."""
        p_values = np.array([0.01, np.nan, 0.03, 0.04, np.nan])
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            reject, p_adjusted = fdr_correction(p_values)
            
        # NaN should remain NaN
        assert np.isnan(p_adjusted[1])
        assert np.isnan(p_adjusted[4])
        
        # Non-NaN values should be processed
        assert not np.isnan(p_adjusted[0])
        assert not np.isnan(p_adjusted[2])
        
    def test_invalid_alpha(self):
        """Test with invalid alpha values."""
        p_values = np.random.uniform(0, 1, 100)
        
        # Alpha outside [0, 1]
        with pytest.raises((ValueError, AssertionError)):
            fdr_correction(p_values, alpha=1.5)
            
        with pytest.raises((ValueError, AssertionError)):
            fdr_correction(p_values, alpha=-0.1)
            
    def test_duplicate_p_values(self):
        """Test with duplicate p-values."""
        p_values = np.array([0.01, 0.01, 0.05, 0.05, 0.05, 0.10])
        reject, p_adjusted = fdr_correction(p_values, alpha=0.05)
        
        # Should handle duplicates correctly
        assert len(reject) == len(p_values)
        assert len(p_adjusted) == len(p_values)


# ----------------------------------------
# Statistical Correctness Tests
# ----------------------------------------

class TestStatisticalCorrectness:
    """Test statistical correctness of FDR procedure."""
    
    def test_comparison_with_scipy(self):
        """Compare with scipy implementation."""
        p_values = np.random.uniform(0, 1, 100)
        p_values[:10] = np.random.beta(0.5, 10, 10)
        
        # Our implementation
        reject_ours, p_adj_ours = fdr_correction(p_values, alpha=0.05, method='fdr_bh')
        
        # Scipy implementation
        from scipy.stats import false_discovery_control
        p_adj_scipy = false_discovery_control(p_values, method='bh')
        reject_scipy = p_adj_scipy <= 0.05
        
        # Should match closely
        np.testing.assert_array_almost_equal(p_adj_ours, p_adj_scipy, decimal=10)
        np.testing.assert_array_equal(reject_ours, reject_scipy)
        
    def test_step_up_procedure(self):
        """Test the step-up procedure logic."""
        # Hand-calculated example
        p_values = np.array([0.01, 0.04, 0.03, 0.05, 0.20])
        alpha = 0.05
        
        # Sort p-values
        sorted_idx = np.argsort(p_values)
        sorted_p = p_values[sorted_idx]  # [0.01, 0.03, 0.04, 0.05, 0.20]
        
        # BH step-up: find largest i such that P(i) <= (i/m) * alpha
        m = len(p_values)
        threshold = np.arange(1, m+1) / m * alpha  # [0.01, 0.02, 0.03, 0.04, 0.05]
        
        # P(4) = 0.05 <= 0.04 is False
        # P(3) = 0.04 <= 0.03 is False  
        # P(2) = 0.03 <= 0.02 is False
        # P(1) = 0.01 <= 0.01 is True
        
        reject, _ = fdr_correction(p_values, alpha=alpha, method='fdr_bh')
        
        # Only first in sorted order should be rejected
        assert np.sum(reject) == 1
        assert reject[0] == True  # p=0.01
        
    def test_fdr_control_simulation(self, simulation_data):
        """Test FDR control through simulation."""
        p_values = simulation_data['p_values']
        true_effects = simulation_data['true_effects']
        
        # Apply FDR correction
        alpha = 0.05
        reject, _ = fdr_correction(p_values, alpha=alpha)
        
        # Calculate actual FDR
        n_discoveries = np.sum(reject)
        n_false_discoveries = np.sum(reject & ~true_effects)
        
        if n_discoveries > 0:
            actual_fdr = n_false_discoveries / n_discoveries
            # FDR should be controlled at alpha level (with some tolerance)
            assert actual_fdr <= alpha * 1.5  # Allow 50% tolerance
            
        # Calculate power
        n_true_discoveries = np.sum(reject & true_effects)
        n_true_effects = np.sum(true_effects)
        power = n_true_discoveries / n_true_effects if n_true_effects > 0 else 0
        
        # Should have reasonable power
        assert power > 0.5  # At least 50% power


# ----------------------------------------
# Performance Tests
# ----------------------------------------

class TestPerformance:
    """Test performance characteristics."""
    
    def test_large_scale_performance(self, stats_performance_monitor):
        """Test performance with large numbers of tests."""
        sizes = [1000, 10000, 100000]
        
        for size in sizes:
            p_values = np.random.uniform(0, 1, size)
            
            with stats_performance_monitor.measure(f'fdr_{size}'):
                reject, p_adjusted = fdr_correction(p_values)
                
        # Check scaling
        for i in range(len(sizes)-1):
            perf = stats_performance_monitor.compare(
                f'fdr_{sizes[i]}',
                f'fdr_{sizes[i+1]}'
            )
            # Should scale roughly linearly (allowing for overhead)
            size_ratio = sizes[i+1] / sizes[i]
            assert 1/perf['speedup'] < size_ratio * 2
            
    def test_sorted_vs_unsorted_performance(self, stats_performance_monitor):
        """Test performance difference between sorted and unsorted input."""
        p_values = np.random.uniform(0, 1, 10000)
        p_values_sorted = np.sort(p_values)
        
        # Unsorted
        with stats_performance_monitor.measure('unsorted'):
            reject1, p_adj1 = fdr_correction(p_values, is_sorted=False)
            
        # Sorted
        with stats_performance_monitor.measure('sorted'):
            reject2, p_adj2 = fdr_correction(p_values_sorted, is_sorted=True)
            
        # Sorted should be faster
        perf = stats_performance_monitor.compare('sorted', 'unsorted')
        assert perf['speedup'] > 1.0  # Sorted is faster
        
        # Results should be equivalent
        idx = np.argsort(p_values)
        np.testing.assert_array_equal(reject1[idx], reject2)
        np.testing.assert_array_almost_equal(p_adj1[idx], p_adj2)


# ----------------------------------------
# Mock Tests
# ----------------------------------------

class TestMocking:
    """Tests using mocks."""
    
    @patch('numpy.argsort')
    def test_sorting_called(self, mock_argsort):
        """Test that sorting is called when needed."""
        p_values = np.array([0.5, 0.1, 0.3])
        mock_argsort.return_value = np.array([1, 2, 0])
        
        # Call with is_sorted=False
        fdr_correction(p_values, is_sorted=False)
        mock_argsort.assert_called_once()
        
        # Reset mock
        mock_argsort.reset_mock()
        
        # Call with is_sorted=True
        fdr_correction(p_values, is_sorted=True)
        mock_argsort.assert_not_called()
        
    def test_method_dispatch(self):
        """Test that correct method is called."""
        p_values = np.random.uniform(0, 1, 100)
        
        # Test each method
        methods = ['fdr_bh', 'fdr_by', 'fdr_tsbh', 'fdr_tsbky']
        results = {}
        
        for method in methods:
            reject, p_adj = fdr_correction(p_values, method=method)
            results[method] = (reject, p_adj)
            
        # Different methods should give different results
        # BY should be most conservative
        assert np.sum(results['fdr_by'][0]) <= np.sum(results['fdr_bh'][0])


# ----------------------------------------
# Integration Tests
# ----------------------------------------

class TestIntegration:
    """Integration tests with real-world scenarios."""
    
    def test_genomics_scenario(self):
        """Test with genomics-like data (many tests, few effects)."""
        # Simulate gene expression data
        n_genes = 20000
        n_differential = 200  # 1% differentially expressed
        
        # Generate p-values
        p_values = np.random.uniform(0, 1, n_genes)
        diff_idx = np.random.choice(n_genes, n_differential, replace=False)
        p_values[diff_idx] = np.random.beta(0.5, 10, n_differential)
        
        # Apply FDR
        reject, p_adjusted = fdr_correction(p_values, alpha=0.05)
        
        # Should find some but not all differential genes
        n_found = np.sum(reject)
        assert 50 < n_found < n_differential * 2
        
        # Check enrichment in true positives
        true_positive_rate = np.sum(reject[diff_idx]) / n_differential
        false_positive_rate = np.sum(reject[~np.isin(np.arange(n_genes), diff_idx)]) / (n_genes - n_differential)
        
        assert true_positive_rate > false_positive_rate * 5  # Significant enrichment
        
    def test_multiple_comparison_workflow(self):
        """Test complete multiple comparison workflow."""
        # Simulate multiple group comparisons
        n_groups = 5
        n_per_group = 30
        n_variables = 100
        
        # Generate data with some true differences
        p_values = []
        
        for var in range(n_variables):
            # 10% of variables have true differences
            if var < 10:
                # True effect: groups have different means
                groups = [np.random.normal(i*0.5, 1, n_per_group) for i in range(n_groups)]
            else:
                # No effect: all groups same
                groups = [np.random.normal(0, 1, n_per_group) for i in range(n_groups)]
                
            # Perform ANOVA
            f_stat, p_val = scipy_stats.f_oneway(*groups)
            p_values.append(p_val)
            
        p_values = np.array(p_values)
        
        # Apply multiple comparison correction
        reject, p_adjusted = fdr_correction(p_values, alpha=0.05)
        
        # Should detect most true effects
        true_effects = np.arange(10)
        detected = np.sum(reject[true_effects])
        assert detected >= 5  # At least half detected


if __name__ == "__main__":
    pytest.main([__file__, "-v"])