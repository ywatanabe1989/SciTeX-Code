#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-09 21:25:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/tests/scitex/stats/conftest_enhanced.py
# ----------------------------------------
"""
Enhanced pytest fixtures for scitex.stats module testing.

Provides comprehensive fixtures for statistical testing including:
- Various distributions
- Correlation patterns
- Time series data
- Hypothesis testing scenarios
- Performance benchmarking
"""

import os
import time
import tracemalloc
from contextlib import contextmanager
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest
import torch
from hypothesis import strategies as st
from scipy import stats as scipy_stats


# ----------------------------------------
# Random Seed Management
# ----------------------------------------

@pytest.fixture(autouse=True)
def set_random_seeds():
    """Ensure reproducible tests."""
    np.random.seed(42)
    torch.manual_seed(42)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(42)
    yield
    # Reset after test
    np.random.seed(None)


# ----------------------------------------
# Statistical Distributions
# ----------------------------------------

@pytest.fixture
def standard_distributions():
    """Standard statistical distributions for testing."""
    n = 1000
    return {
        'normal': np.random.normal(0, 1, n),
        'uniform': np.random.uniform(0, 1, n),
        'exponential': np.random.exponential(1, n),
        'poisson': np.random.poisson(5, n),
        'binomial': np.random.binomial(10, 0.5, n),
        'gamma': np.random.gamma(2, 2, n),
        'beta': np.random.beta(2, 5, n),
        'chi2': np.random.chisquare(5, n),
        't_dist': np.random.standard_t(5, n),
        'f_dist': np.random.f(5, 10, n),
        'lognormal': np.random.lognormal(0, 1, n),
        'weibull': np.random.weibull(2, n),
    }


@pytest.fixture
def special_distributions():
    """Special and edge-case distributions."""
    n = 1000
    return {
        'constant': np.full(n, 3.14),
        'bimodal': np.concatenate([
            np.random.normal(-2, 0.5, n//2),
            np.random.normal(2, 0.5, n//2)
        ]),
        'heavy_tailed': np.random.standard_t(2, n),
        'zero_inflated': np.where(
            np.random.random(n) < 0.3,
            0,
            np.random.exponential(2, n)
        ),
        'discrete': np.random.choice([1, 2, 3, 4, 5], n),
        'skewed_left': -np.random.gamma(2, 2, n),
        'skewed_right': np.random.gamma(2, 2, n),
        'outliers': np.concatenate([
            np.random.normal(0, 1, int(n*0.95)),
            np.random.normal(0, 10, int(n*0.05))
        ]),
        'truncated': np.clip(np.random.normal(0, 2, n), -3, 3),
    }


@pytest.fixture
def correlation_patterns():
    """Various correlation patterns for testing."""
    n = 500
    
    # Generate base variable
    x = np.random.normal(0, 1, n)
    
    patterns = {
        'independent': (x, np.random.normal(0, 1, n)),
        'perfect_positive': (x, x),
        'perfect_negative': (x, -x),
        'strong_positive': (x, x + np.random.normal(0, 0.3, n)),
        'strong_negative': (x, -x + np.random.normal(0, 0.3, n)),
        'weak_positive': (x, 0.3 * x + np.random.normal(0, 1, n)),
        'nonlinear': (x, x**2 + np.random.normal(0, 0.1, n)),
        'sinusoidal': (x, np.sin(x) + np.random.normal(0, 0.1, n)),
        'threshold': (x, np.where(x > 0, 1, -1) + np.random.normal(0, 0.1, n)),
    }
    
    return patterns


@pytest.fixture
def time_series_data():
    """Various time series patterns."""
    n = 1000
    t = np.arange(n)
    
    return {
        'white_noise': np.random.normal(0, 1, n),
        'random_walk': np.cumsum(np.random.normal(0, 1, n)),
        'trend': 0.01 * t + np.random.normal(0, 1, n),
        'seasonal': np.sin(2 * np.pi * t / 365) + np.random.normal(0, 0.1, n),
        'trend_seasonal': 0.01 * t + np.sin(2 * np.pi * t / 365) + np.random.normal(0, 0.1, n),
        'ar1': scipy_stats.arma_generate_sample([1, -0.7], [1], n),
        'ma1': scipy_stats.arma_generate_sample([1], [1, 0.5], n),
        'arma11': scipy_stats.arma_generate_sample([1, -0.7], [1, 0.5], n),
        'volatility_clustering': np.concatenate([
            np.random.normal(0, 0.5, n//3),
            np.random.normal(0, 2, n//3),
            np.random.normal(0, 0.5, n//3)
        ]),
    }


# ----------------------------------------
# Hypothesis Testing Data
# ----------------------------------------

@pytest.fixture
def hypothesis_test_data():
    """Data for hypothesis testing scenarios."""
    n = 100
    
    return {
        'two_sample_equal': {
            'group1': np.random.normal(0, 1, n),
            'group2': np.random.normal(0, 1, n),
            'expected_pvalue_range': (0.05, 1.0),
        },
        'two_sample_different': {
            'group1': np.random.normal(0, 1, n),
            'group2': np.random.normal(1, 1, n),
            'expected_pvalue_range': (0.0, 0.05),
        },
        'paired_equal': {
            'before': np.random.normal(0, 1, n),
            'after': lambda before: before + np.random.normal(0, 0.1, n),
            'expected_pvalue_range': (0.05, 1.0),
        },
        'paired_different': {
            'before': np.random.normal(0, 1, n),
            'after': lambda before: before + 0.5 + np.random.normal(0, 0.1, n),
            'expected_pvalue_range': (0.0, 0.05),
        },
        'anova_equal': {
            'groups': [np.random.normal(0, 1, n) for _ in range(3)],
            'expected_pvalue_range': (0.05, 1.0),
        },
        'anova_different': {
            'groups': [np.random.normal(i, 1, n) for i in range(3)],
            'expected_pvalue_range': (0.0, 0.05),
        },
    }


@pytest.fixture
def multiple_testing_data():
    """Data for multiple comparisons testing."""
    n_tests = 100
    n_samples = 50
    
    # Generate p-values: 10% true positives, 90% true negatives
    true_effects = np.random.random(n_tests) < 0.1
    
    p_values = []
    for is_true in true_effects:
        if is_true:
            # True effect: small p-value
            p = np.random.beta(0.5, 10)
        else:
            # No effect: uniform p-value
            p = np.random.uniform(0, 1)
        p_values.append(p)
    
    return {
        'p_values': np.array(p_values),
        'true_effects': true_effects,
        'n_tests': n_tests,
        'alpha': 0.05,
    }


# ----------------------------------------
# Data Quality Scenarios
# ----------------------------------------

@pytest.fixture
def data_quality_scenarios():
    """Various data quality issues for testing."""
    n = 1000
    
    return {
        'clean': np.random.normal(0, 1, n),
        'missing_random': np.where(
            np.random.random(n) < 0.1,
            np.nan,
            np.random.normal(0, 1, n)
        ),
        'missing_systematic': np.concatenate([
            np.random.normal(0, 1, int(n*0.8)),
            np.full(int(n*0.2), np.nan)
        ]),
        'outliers_symmetric': np.concatenate([
            np.random.normal(0, 1, int(n*0.98)),
            np.random.choice([-10, 10], int(n*0.02))
        ]),
        'outliers_asymmetric': np.concatenate([
            np.random.normal(0, 1, int(n*0.98)),
            np.random.uniform(10, 20, int(n*0.02))
        ]),
        'mixed_types': np.array([float(i) if i % 2 == 0 else i for i in range(n)]),
        'zeros_inflated': np.where(
            np.random.random(n) < 0.3,
            0,
            np.random.normal(0, 1, n)
        ),
        'inf_values': np.where(
            np.random.random(n) < 0.01,
            np.random.choice([np.inf, -np.inf]),
            np.random.normal(0, 1, n)
        ),
    }


# ----------------------------------------
# Tensor Data Fixtures
# ----------------------------------------

@pytest.fixture
def tensor_shapes():
    """Common tensor shapes for testing."""
    return {
        'vector': (100,),
        'matrix': (50, 100),
        'batch_vector': (32, 100),
        'batch_matrix': (32, 50, 100),
        'time_series': (32, 1000, 10),  # batch x time x features
        'image_batch': (16, 3, 224, 224),  # batch x channels x height x width
        'video_batch': (8, 30, 3, 128, 128),  # batch x frames x channels x H x W
        'high_dim': (10, 20, 30, 40),
        'tiny': (2, 3),
        'large': (1000, 1000),
    }


@pytest.fixture
def tensor_data_factory():
    """Factory for creating tensor data with specific properties."""
    def create_tensor(shape, dtype=torch.float32, dist='normal', device='cpu', **kwargs):
        """Create tensor with specified properties."""
        if dist == 'normal':
            mean = kwargs.get('mean', 0)
            std = kwargs.get('std', 1)
            data = torch.normal(mean, std, shape, dtype=dtype, device=device)
        elif dist == 'uniform':
            low = kwargs.get('low', 0)
            high = kwargs.get('high', 1)
            data = torch.empty(shape, dtype=dtype, device=device).uniform_(low, high)
        elif dist == 'zeros':
            data = torch.zeros(shape, dtype=dtype, device=device)
        elif dist == 'ones':
            data = torch.ones(shape, dtype=dtype, device=device)
        elif dist == 'range':
            data = torch.arange(np.prod(shape), dtype=dtype, device=device).reshape(shape)
        else:
            raise ValueError(f"Unknown distribution: {dist}")
        
        # Add noise if requested
        if kwargs.get('noise', 0) > 0:
            noise = torch.normal(0, kwargs['noise'], shape, dtype=dtype, device=device)
            data = data + noise
        
        # Add NaN values if requested
        if kwargs.get('nan_ratio', 0) > 0:
            mask = torch.rand(shape) < kwargs['nan_ratio']
            data[mask] = float('nan')
        
        return data
    
    return create_tensor


# ----------------------------------------
# Performance Monitoring
# ----------------------------------------

@pytest.fixture
def stats_performance_monitor():
    """Performance monitoring for statistical operations."""
    class StatsPerformanceMonitor:
        def __init__(self):
            self.results = {}
            
        @contextmanager
        def measure(self, name):
            """Context manager for measuring performance."""
            # CPU measurement
            start_time = time.perf_counter()
            tracemalloc.start()
            start_memory = tracemalloc.get_traced_memory()[0]
            
            yield self
            
            # Record metrics
            end_time = time.perf_counter()
            current_memory, peak_memory = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            self.results[name] = {
                'duration': end_time - start_time,
                'memory_used': current_memory - start_memory,
                'memory_peak': peak_memory,
                'timestamp': time.time(),
            }
            
        def compare(self, name1, name2):
            """Compare two measurements."""
            r1 = self.results[name1]
            r2 = self.results[name2]
            
            return {
                'speedup': r2['duration'] / r1['duration'],
                'memory_ratio': r1['memory_used'] / r2['memory_used'],
                'faster': name1 if r1['duration'] < r2['duration'] else name2,
            }
            
        def assert_performance(self, name, max_time=None, max_memory=None):
            """Assert performance constraints."""
            result = self.results[name]
            
            if max_time is not None and result['duration'] > max_time:
                raise AssertionError(
                    f"{name} took {result['duration']:.3f}s, expected < {max_time}s"
                )
                
            if max_memory is not None and result['memory_used'] > max_memory:
                raise AssertionError(
                    f"{name} used {result['memory_used']/1e6:.1f}MB, "
                    f"expected < {max_memory/1e6:.1f}MB"
                )
    
    return StatsPerformanceMonitor()


# ----------------------------------------
# Mock Fixtures
# ----------------------------------------

@pytest.fixture
def mock_scipy_stats():
    """Mock scipy.stats functions."""
    with patch('scipy.stats.ttest_ind') as mock_ttest, \
         patch('scipy.stats.pearsonr') as mock_pearson, \
         patch('scipy.stats.spearmanr') as mock_spearman, \
         patch('scipy.stats.kstest') as mock_kstest:
        
        # Configure return values
        mock_ttest.return_value = MagicMock(statistic=1.5, pvalue=0.05)
        mock_pearson.return_value = (0.8, 0.01)
        mock_spearman.return_value = MagicMock(correlation=0.7, pvalue=0.02)
        mock_kstest.return_value = MagicMock(statistic=0.1, pvalue=0.3)
        
        yield {
            'ttest_ind': mock_ttest,
            'pearsonr': mock_pearson,
            'spearmanr': mock_spearman,
            'kstest': mock_kstest,
        }


# ----------------------------------------
# Assertion Helpers
# ----------------------------------------

@pytest.fixture
def statistical_assertions():
    """Helper assertions for statistical tests."""
    class StatisticalAssertions:
        @staticmethod
        def assert_distribution_properties(data, expected_mean=None, expected_std=None, 
                                         tolerance=0.1):
            """Assert distribution has expected properties."""
            actual_mean = np.mean(data)
            actual_std = np.std(data)
            
            if expected_mean is not None:
                assert abs(actual_mean - expected_mean) < tolerance, \
                    f"Mean {actual_mean:.3f} != {expected_mean:.3f}"
                    
            if expected_std is not None:
                assert abs(actual_std - expected_std) < tolerance, \
                    f"Std {actual_std:.3f} != {expected_std:.3f}"
                    
        @staticmethod
        def assert_correlation(x, y, expected_corr, tolerance=0.1):
            """Assert correlation is as expected."""
            actual_corr = np.corrcoef(x, y)[0, 1]
            assert abs(actual_corr - expected_corr) < tolerance, \
                f"Correlation {actual_corr:.3f} != {expected_corr:.3f}"
                
        @staticmethod
        def assert_p_value_range(p_value, min_p=0.0, max_p=1.0):
            """Assert p-value is in expected range."""
            assert min_p <= p_value <= max_p, \
                f"P-value {p_value:.3f} not in range [{min_p}, {max_p}]"
                
        @staticmethod
        def assert_test_statistic_properties(statistic, df=None):
            """Assert test statistic has expected properties."""
            assert np.isfinite(statistic), "Test statistic should be finite"
            if df is not None:
                assert df > 0, "Degrees of freedom should be positive"
    
    return StatisticalAssertions()


# ----------------------------------------
# Hypothesis Strategies
# ----------------------------------------

@pytest.fixture
def stats_hypothesis_strategies():
    """Hypothesis strategies for statistical testing."""
    return {
        'sample_sizes': st.integers(min_value=10, max_value=1000),
        'correlations': st.floats(min_value=-1.0, max_value=1.0),
        'p_values': st.floats(min_value=0.0, max_value=1.0),
        'test_statistics': st.floats(min_value=-10.0, max_value=10.0),
        'alpha_levels': st.sampled_from([0.01, 0.05, 0.10]),
        'distributions': st.sampled_from(['normal', 'uniform', 'exponential']),
        'correlation_methods': st.sampled_from(['pearson', 'spearman', 'kendall']),
        'test_types': st.sampled_from(['two-sided', 'less', 'greater']),
    }


# ----------------------------------------
# Data Generation Helpers
# ----------------------------------------

@pytest.fixture
def generate_correlated_data():
    """Generate correlated data with specified correlation."""
    def _generate(n=100, correlation=0.5, seed=None):
        """Generate two correlated variables."""
        if seed is not None:
            np.random.seed(seed)
            
        # Generate correlated normal variables
        mean = [0, 0]
        cov = [[1, correlation], [correlation, 1]]
        x, y = np.random.multivariate_normal(mean, cov, n).T
        
        return x, y
    
    return _generate


@pytest.fixture
def generate_grouped_data():
    """Generate grouped data for ANOVA-like tests."""
    def _generate(n_groups=3, n_per_group=30, effect_size=0.0, seed=None):
        """Generate grouped data with optional effect."""
        if seed is not None:
            np.random.seed(seed)
            
        groups = []
        labels = []
        
        for i in range(n_groups):
            # Add effect to each group
            group_mean = i * effect_size
            group_data = np.random.normal(group_mean, 1, n_per_group)
            groups.append(group_data)
            labels.extend([f'Group_{i}'] * n_per_group)
            
        # Combine into single arrays
        data = np.concatenate(groups)
        labels = np.array(labels)
        
        return data, labels, groups
    
    return _generate


# ----------------------------------------
# Cleanup and Safety
# ----------------------------------------

@pytest.fixture(autouse=True)
def cleanup_warnings():
    """Clean up warnings after each test."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        yield


@pytest.fixture
def temporary_data_dir(tmp_path):
    """Create temporary directory for test data."""
    data_dir = tmp_path / "test_stats_data"
    data_dir.mkdir()
    
    # Create some test CSV files
    df1 = pd.DataFrame({
        'x': np.random.normal(0, 1, 100),
        'y': np.random.normal(0, 1, 100)
    })
    df1.to_csv(data_dir / "test_data.csv", index=False)
    
    yield data_dir


if __name__ == "__main__":
    print("This is a pytest conftest file for scitex.stats module.")
    print("Available fixtures:")
    print("- standard_distributions: Normal, uniform, exponential, etc.")
    print("- special_distributions: Bimodal, heavy-tailed, zero-inflated, etc.")
    print("- correlation_patterns: Various correlation scenarios")
    print("- time_series_data: AR, MA, ARMA, trends, seasonality")
    print("- hypothesis_test_data: Two-sample, paired, ANOVA scenarios")
    print("- stats_performance_monitor: Performance measurement tools")
    print("- statistical_assertions: Helper assertions")
    print("... and many more!")