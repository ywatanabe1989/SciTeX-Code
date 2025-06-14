#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-09 21:16:00"
# File: /tests/scitex/ai/sk/test__clf_enhanced.py
# ----------------------------------------
"""
Enhanced tests for scitex.ai.sk._clf module implementing advanced testing patterns.

This module demonstrates:
- Comprehensive fixtures for scikit-learn/sktime pipelines
- Property-based testing for pipeline robustness
- Edge case handling (empty data, single sample, etc.)
- Performance benchmarking for time series classifiers
- Mock isolation for component testing
- Integration with sklearn/sktime ecosystem
- Cross-validation and metric validation
"""

import pytest
import numpy as np
import pandas as pd
from unittest.mock import patch, MagicMock, call
from hypothesis import given, strategies as st, settings, assume
import time
import warnings
from sklearn.pipeline import Pipeline
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.exceptions import NotFittedError
from sktime.transformations.panel.rocket import Rocket
from sktime.transformations.panel.reduce import Tabularizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import GradientBoostingClassifier
import joblib
import tempfile
import os

try:
    from scitex.ai.sk import rocket_pipeline, GB_pipeline
except ImportError:
    pytest.skip("scitex.ai.sk module not available", allow_module_level=True)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def time_series_datasets():
    """Provide various time series datasets for testing."""
    np.random.seed(42)
    
    # Standard multivariate time series
    n_samples, n_features, n_timesteps = 100, 3, 50
    X_standard = np.random.randn(n_samples, n_features, n_timesteps)
    y_standard = np.random.randint(0, 2, n_samples)
    
    # Single feature time series
    X_univariate = np.random.randn(100, 1, 50)
    y_univariate = np.random.randint(0, 3, 100)
    
    # Very short time series
    X_short = np.random.randn(50, 5, 10)
    y_short = np.random.randint(0, 2, 50)
    
    # Long time series
    X_long = np.random.randn(50, 3, 500)
    y_long = np.random.randint(0, 4, 50)
    
    # Imbalanced classes
    y_imbalanced = np.concatenate([np.zeros(90), np.ones(10)])
    X_imbalanced = np.random.randn(100, 3, 50)
    
    # Edge cases
    X_single = np.random.randn(1, 3, 50)  # Single sample
    y_single = np.array([0])
    
    X_empty = np.array([]).reshape(0, 3, 50)  # Empty dataset
    y_empty = np.array([])
    
    return {
        'standard': (X_standard, y_standard),
        'univariate': (X_univariate, y_univariate),
        'short': (X_short, y_short),
        'long': (X_long, y_long),
        'imbalanced': (X_imbalanced, y_imbalanced),
        'single_sample': (X_single, y_single),
        'empty': (X_empty, y_empty),
    }


@pytest.fixture
def problematic_datasets():
    """Provide datasets with various problematic characteristics."""
    # Contains NaN values
    X_nan = np.random.randn(50, 3, 30)
    X_nan[0, 0, 0] = np.nan
    y_nan = np.random.randint(0, 2, 50)
    
    # Contains infinite values
    X_inf = np.random.randn(50, 3, 30)
    X_inf[0, 0, 0] = np.inf
    y_inf = np.random.randint(0, 2, 50)
    
    # All zeros
    X_zeros = np.zeros((50, 3, 30))
    y_zeros = np.random.randint(0, 2, 50)
    
    # Constant values
    X_constant = np.ones((50, 3, 30)) * 42
    y_constant = np.random.randint(0, 2, 50)
    
    # High variance
    X_high_var = np.random.randn(50, 3, 30) * 1000
    y_high_var = np.random.randint(0, 2, 50)
    
    return {
        'nan': (X_nan, y_nan),
        'inf': (X_inf, y_inf),
        'zeros': (X_zeros, y_zeros),
        'constant': (X_constant, y_constant),
        'high_variance': (X_high_var, y_high_var),
    }


@pytest.fixture
def pipeline_configurations():
    """Provide various pipeline configurations for testing."""
    return [
        # Default Rocket pipeline
        {},
        # Custom n_kernels
        {'n_kernels': 100},
        {'n_kernels': 1000},
        # With random state
        {'random_state': 42},
        # Multiple parameters
        {'n_kernels': 500, 'random_state': 123},
    ]


@pytest.fixture
def performance_monitor():
    """Monitor pipeline performance metrics."""
    class PerformanceMonitor:
        def __init__(self):
            self.fit_times = []
            self.predict_times = []
            self.transform_times = []
            self.memory_usage = []
        
        def time_fit(self, pipeline, X, y):
            start = time.time()
            pipeline.fit(X, y)
            self.fit_times.append(time.time() - start)
            return pipeline
        
        def time_predict(self, pipeline, X):
            start = time.time()
            predictions = pipeline.predict(X)
            self.predict_times.append(time.time() - start)
            return predictions
        
        def time_transform(self, transformer, X):
            start = time.time()
            transformed = transformer.transform(X)
            self.transform_times.append(time.time() - start)
            return transformed
        
        def get_summary(self):
            return {
                'avg_fit_time': np.mean(self.fit_times) if self.fit_times else 0,
                'avg_predict_time': np.mean(self.predict_times) if self.predict_times else 0,
                'avg_transform_time': np.mean(self.transform_times) if self.transform_times else 0,
                'total_operations': len(self.fit_times) + len(self.predict_times),
            }
    
    return PerformanceMonitor()


@pytest.fixture
def mock_components():
    """Provide mocked sklearn/sktime components for isolation testing."""
    mock_rocket = MagicMock(spec=Rocket)
    mock_rocket.transform.return_value = np.random.randn(100, 500)
    mock_rocket.n_kernels = 10000
    
    mock_lr = MagicMock(spec=LogisticRegression)
    mock_lr.predict.return_value = np.random.randint(0, 2, 100)
    mock_lr.predict_proba.return_value = np.random.rand(100, 2)
    
    mock_gb = MagicMock(spec=GradientBoostingClassifier)
    mock_gb.predict.return_value = np.random.randint(0, 2, 100)
    
    mock_tabularizer = MagicMock(spec=Tabularizer)
    mock_tabularizer.transform.return_value = np.random.randn(100, 150)
    
    return {
        'rocket': mock_rocket,
        'logistic_regression': mock_lr,
        'gradient_boosting': mock_gb,
        'tabularizer': mock_tabularizer,
    }


# ============================================================================
# Basic Functionality Tests
# ============================================================================

class TestRocketPipelineBasics:
    """Test basic rocket_pipeline functionality."""
    
    def test_pipeline_creation_default(self):
        """Test pipeline creation with default parameters."""
        pipeline = rocket_pipeline()
        
        assert isinstance(pipeline, Pipeline)
        assert len(pipeline.steps) == 2
        assert pipeline.steps[0][0] == 'rocket'
        assert pipeline.steps[1][0] == 'logisticregression'
        assert isinstance(pipeline.steps[0][1], Rocket)
        assert isinstance(pipeline.steps[1][1], LogisticRegression)
        
        # Check LogisticRegression max_iter
        lr = pipeline.steps[1][1]
        assert lr.max_iter == 1000
    
    @pytest.mark.parametrize('config', [
        {'n_kernels': 100},
        {'n_kernels': 500, 'random_state': 42},
        {'normalise': False},
    ])
    def test_pipeline_creation_with_params(self, config):
        """Test pipeline creation with custom parameters."""
        pipeline = rocket_pipeline(**config)
        
        rocket = pipeline.steps[0][1]
        for key, value in config.items():
            if hasattr(rocket, key):
                assert getattr(rocket, key) == value
    
    def test_pipeline_sklearn_interface(self):
        """Test that pipeline implements sklearn interface."""
        pipeline = rocket_pipeline()
        
        # Check required methods
        assert hasattr(pipeline, 'fit')
        assert hasattr(pipeline, 'predict')
        assert hasattr(pipeline, 'predict_proba')
        assert hasattr(pipeline, 'score')
        assert hasattr(pipeline, 'get_params')
        assert hasattr(pipeline, 'set_params')
    
    def test_pipeline_fit_predict(self, time_series_datasets):
        """Test basic fit and predict functionality."""
        X, y = time_series_datasets['standard']
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        pipeline = rocket_pipeline(n_kernels=100)  # Small for speed
        
        # Fit
        pipeline.fit(X_train, y_train)
        
        # Predict
        y_pred = pipeline.predict(X_test)
        assert y_pred.shape == y_test.shape
        assert set(y_pred).issubset(set(y_train))  # Predictions contain known classes
        
        # Score
        score = pipeline.score(X_test, y_test)
        assert 0 <= score <= 1


# ============================================================================
# GB Pipeline Tests
# ============================================================================

class TestGBPipelineBasics:
    """Test basic GB_pipeline functionality."""
    
    def test_gb_pipeline_structure(self):
        """Test GB_pipeline structure."""
        assert isinstance(GB_pipeline, Pipeline)
        assert len(GB_pipeline.steps) == 2
        assert GB_pipeline.steps[0][0] == 'tabularizer'
        assert GB_pipeline.steps[1][0] == 'gradientboostingclassifier'
        assert isinstance(GB_pipeline.steps[0][1], Tabularizer)
        assert isinstance(GB_pipeline.steps[1][1], GradientBoostingClassifier)
    
    def test_gb_pipeline_fit_predict(self, time_series_datasets):
        """Test GB_pipeline fit and predict."""
        X, y = time_series_datasets['standard']
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Clone pipeline to avoid modifying global object
        pipeline = joblib.loads(joblib.dumps(GB_pipeline))
        
        # Fit and predict
        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)
        
        assert y_pred.shape == y_test.shape
        accuracy = accuracy_score(y_test, y_pred)
        assert 0 <= accuracy <= 1


# ============================================================================
# Property-Based Tests
# ============================================================================

class TestPipelineProperties:
    """Property-based tests for pipeline robustness."""
    
    @given(
        n_samples=st.integers(min_value=10, max_value=200),
        n_features=st.integers(min_value=1, max_value=10),
        n_timesteps=st.integers(min_value=5, max_value=100),
        n_classes=st.integers(min_value=2, max_value=5)
    )
    @settings(max_examples=20, deadline=None)
    def test_rocket_handles_various_dimensions(self, n_samples, n_features, n_timesteps, n_classes):
        """Test that rocket pipeline handles various data dimensions."""
        # Generate random data
        X = np.random.randn(n_samples, n_features, n_timesteps)
        y = np.random.randint(0, n_classes, n_samples)
        
        # Ensure we have at least 2 samples per class for splitting
        unique_classes, counts = np.unique(y, return_counts=True)
        assume(all(count >= 2 for count in counts))
        
        pipeline = rocket_pipeline(n_kernels=50)  # Small for speed
        
        try:
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, stratify=y, random_state=42
            )
            
            # Fit and predict
            pipeline.fit(X_train, y_train)
            predictions = pipeline.predict(X_test)
            
            # Validate output
            assert predictions.shape == y_test.shape
            assert set(predictions).issubset(set(y_train))
            
        except ValueError as e:
            # Some dimension combinations might be invalid
            if "at least" in str(e) or "too small" in str(e):
                pytest.skip(f"Invalid dimensions: {e}")
            else:
                raise
    
    @given(
        n_kernels=st.integers(min_value=10, max_value=1000),
        random_state=st.integers(min_value=0, max_value=1000)
    )
    @settings(max_examples=10, deadline=None)
    def test_rocket_parameter_consistency(self, n_kernels, random_state):
        """Test that parameters are consistently applied."""
        pipeline1 = rocket_pipeline(n_kernels=n_kernels, random_state=random_state)
        pipeline2 = rocket_pipeline(n_kernels=n_kernels, random_state=random_state)
        
        # Generate data
        X = np.random.randn(50, 3, 30)
        y = np.random.randint(0, 2, 50)
        
        # Fit both pipelines
        pipeline1.fit(X, y)
        pipeline2.fit(X, y)
        
        # Predictions should be identical with same random state
        pred1 = pipeline1.predict(X)
        pred2 = pipeline2.predict(X)
        
        assert np.array_equal(pred1, pred2)


# ============================================================================
# Edge Case Tests
# ============================================================================

class TestPipelineEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_empty_data_error(self, time_series_datasets):
        """Test that empty data raises appropriate error."""
        X_empty, y_empty = time_series_datasets['empty']
        pipeline = rocket_pipeline(n_kernels=10)
        
        with pytest.raises(ValueError):
            pipeline.fit(X_empty, y_empty)
    
    def test_single_sample_warning(self, time_series_datasets):
        """Test behavior with single sample."""
        X_single, y_single = time_series_datasets['single_sample']
        pipeline = rocket_pipeline(n_kernels=10)
        
        # Should raise error or warning about insufficient samples
        with pytest.raises(ValueError):
            pipeline.fit(X_single, y_single)
    
    def test_nan_handling(self, problematic_datasets):
        """Test handling of NaN values."""
        X_nan, y_nan = problematic_datasets['nan']
        pipeline = rocket_pipeline(n_kernels=10)
        
        # Rocket should handle NaN appropriately (either error or impute)
        # The exact behavior depends on the implementation
        try:
            pipeline.fit(X_nan, y_nan)
            # If it doesn't error, check predictions are valid
            predictions = pipeline.predict(X_nan[:5])
            assert not np.any(np.isnan(predictions))
        except ValueError as e:
            # Expected if Rocket doesn't handle NaN
            assert "NaN" in str(e) or "missing" in str(e).lower()
    
    def test_infinite_values(self, problematic_datasets):
        """Test handling of infinite values."""
        X_inf, y_inf = problematic_datasets['inf']
        pipeline = rocket_pipeline(n_kernels=10)
        
        # Should either handle or raise error
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                pipeline.fit(X_inf, y_inf)
                predictions = pipeline.predict(X_inf[:5])
                assert np.all(np.isfinite(predictions))
            except ValueError:
                pass  # Expected for some configurations
    
    def test_constant_features(self, problematic_datasets):
        """Test handling of constant features."""
        X_constant, y_constant = problematic_datasets['constant']
        pipeline = rocket_pipeline(n_kernels=10)
        
        # Should handle constant features
        pipeline.fit(X_constant, y_constant)
        predictions = pipeline.predict(X_constant[:10])
        assert predictions.shape == (10,)
    
    def test_not_fitted_error(self, time_series_datasets):
        """Test that unfitted pipeline raises NotFittedError."""
        X, _ = time_series_datasets['standard']
        pipeline = rocket_pipeline()
        
        with pytest.raises(NotFittedError):
            pipeline.predict(X)


# ============================================================================
# Performance Tests
# ============================================================================

class TestPipelinePerformance:
    """Test performance characteristics."""
    
    @pytest.mark.benchmark
    def test_rocket_fit_time_scaling(self, time_series_datasets, performance_monitor):
        """Test how fit time scales with data size."""
        sizes = [20, 50, 100]
        times = []
        
        for size in sizes:
            X, y = time_series_datasets['standard']
            X_subset = X[:size]
            y_subset = y[:size]
            
            pipeline = rocket_pipeline(n_kernels=100)
            
            start = time.time()
            pipeline.fit(X_subset, y_subset)
            fit_time = time.time() - start
            times.append(fit_time)
        
        # Check that time increases with size (roughly)
        assert times[-1] > times[0] * 0.5  # Allow for overhead
    
    def test_prediction_speed(self, time_series_datasets, performance_monitor):
        """Test prediction speed."""
        X, y = time_series_datasets['standard']
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        pipeline = rocket_pipeline(n_kernels=100)
        pipeline = performance_monitor.time_fit(pipeline, X_train, y_train)
        
        # Time predictions
        predictions = performance_monitor.time_predict(pipeline, X_test)
        
        summary = performance_monitor.get_summary()
        assert summary['avg_predict_time'] < summary['avg_fit_time']  # Prediction faster than fit
    
    def test_memory_efficiency(self, time_series_datasets):
        """Test memory usage of pipelines."""
        X, y = time_series_datasets['long']  # Long time series
        
        pipeline = rocket_pipeline(n_kernels=100)
        
        # Fit pipeline
        pipeline.fit(X, y)
        
        # Check model size
        import pickle
        model_size = len(pickle.dumps(pipeline))
        
        # Model should be reasonably sized (not storing all training data)
        data_size = X.nbytes
        assert model_size < data_size * 2  # Model smaller than 2x data


# ============================================================================
# Integration Tests
# ============================================================================

class TestPipelineIntegration:
    """Test integration with sklearn ecosystem."""
    
    def test_cross_validation(self, time_series_datasets):
        """Test pipeline with cross-validation."""
        X, y = time_series_datasets['standard']
        pipeline = rocket_pipeline(n_kernels=50)
        
        # Perform cross-validation
        scores = cross_val_score(pipeline, X, y, cv=3, scoring='accuracy')
        
        assert len(scores) == 3
        assert all(0 <= score <= 1 for score in scores)
        assert np.mean(scores) > 0.3  # Should do better than random
    
    def test_pipeline_persistence(self, time_series_datasets, tmp_path):
        """Test saving and loading pipelines."""
        X, y = time_series_datasets['standard']
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Create and fit pipeline
        pipeline = rocket_pipeline(n_kernels=50, random_state=42)
        pipeline.fit(X_train, y_train)
        original_predictions = pipeline.predict(X_test)
        
        # Save pipeline
        model_path = tmp_path / "rocket_pipeline.pkl"
        joblib.dump(pipeline, model_path)
        
        # Load pipeline
        loaded_pipeline = joblib.load(model_path)
        loaded_predictions = loaded_pipeline.predict(X_test)
        
        # Predictions should be identical
        assert np.array_equal(original_predictions, loaded_predictions)
    
    def test_pipeline_cloning(self, time_series_datasets):
        """Test that pipelines can be properly cloned."""
        from sklearn.base import clone
        
        X, y = time_series_datasets['standard']
        
        # Create and fit original pipeline
        original = rocket_pipeline(n_kernels=50, random_state=42)
        original.fit(X, y)
        
        # Clone pipeline
        cloned = clone(original)
        
        # Cloned pipeline should not be fitted
        with pytest.raises(NotFittedError):
            cloned.predict(X)
        
        # But can be fitted independently
        cloned.fit(X, y)
        predictions = cloned.predict(X[:10])
        assert predictions.shape == (10,)


# ============================================================================
# Mock-based Tests
# ============================================================================

class TestPipelineWithMocks:
    """Test pipeline components in isolation using mocks."""
    
    @patch('scitex.ai.sk._clf.Rocket')
    @patch('scitex.ai.sk._clf.LogisticRegression')
    def test_rocket_pipeline_component_interaction(self, mock_lr_class, mock_rocket_class):
        """Test component interaction in rocket pipeline."""
        # Setup mocks
        mock_rocket = MagicMock()
        mock_rocket.transform.return_value = np.random.randn(80, 500)
        mock_rocket_class.return_value = mock_rocket
        
        mock_lr = MagicMock()
        mock_lr.predict.return_value = np.array([0, 1] * 10)
        mock_lr_class.return_value = mock_lr
        
        # Create pipeline
        pipeline = rocket_pipeline(n_kernels=100)
        
        # Generate test data
        X = np.random.randn(80, 3, 50)
        y = np.random.randint(0, 2, 80)
        
        # Fit pipeline
        pipeline.fit(X, y)
        
        # Verify Rocket was called correctly
        mock_rocket.fit.assert_called_once()
        mock_rocket.transform.assert_called()
        
        # Verify LogisticRegression was called with transformed data
        mock_lr.fit.assert_called_once()
        transformed_shape = mock_lr.fit.call_args[0][0].shape
        assert transformed_shape[0] == 80  # Same number of samples
        assert transformed_shape[1] == 500  # Rocket features
    
    def test_gb_pipeline_mocked_components(self, mock_components):
        """Test GB pipeline with mocked components."""
        with patch('scitex.ai.sk._clf.Tabularizer', return_value=mock_components['tabularizer']):
            with patch('scitex.ai.sk._clf.GradientBoostingClassifier', 
                      return_value=mock_components['gradient_boosting']):
                
                # Need to recreate the pipeline with mocked components
                from scitex.ai.sk import make_pipeline
                mocked_pipeline = make_pipeline(
                    mock_components['tabularizer'],
                    mock_components['gradient_boosting']
                )
                
                # Test data
                X = np.random.randn(50, 3, 30)
                y = np.random.randint(0, 2, 50)
                
                # Fit and predict
                mocked_pipeline.fit(X, y)
                predictions = mocked_pipeline.predict(X)
                
                # Verify components were called
                mock_components['tabularizer'].fit.assert_called_once()
                mock_components['tabularizer'].transform.assert_called()
                mock_components['gradient_boosting'].fit.assert_called_once()
                mock_components['gradient_boosting'].predict.assert_called_once()


# ============================================================================
# Classification Metrics Tests
# ============================================================================

class TestClassificationMetrics:
    """Test classification performance metrics."""
    
    def test_binary_classification_metrics(self, time_series_datasets):
        """Test binary classification performance."""
        X, y = time_series_datasets['standard']
        # Ensure binary classification
        y = (y > np.median(y)).astype(int)
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        pipeline = rocket_pipeline(n_kernels=100, random_state=42)
        pipeline.fit(X_train, y_train)
        
        # Get predictions and probabilities
        y_pred = pipeline.predict(X_test)
        y_proba = pipeline.predict_proba(X_test)
        
        # Calculate metrics
        from sklearn.metrics import roc_auc_score, precision_recall_fscore_support
        
        accuracy = accuracy_score(y_test, y_pred)
        auc = roc_auc_score(y_test, y_proba[:, 1])
        precision, recall, f1, _ = precision_recall_fscore_support(
            y_test, y_pred, average='binary'
        )
        
        # Should achieve reasonable performance
        assert accuracy > 0.5  # Better than random
        assert 0 <= auc <= 1
        assert 0 <= precision <= 1
        assert 0 <= recall <= 1
        assert 0 <= f1 <= 1
    
    def test_multiclass_classification_metrics(self, time_series_datasets):
        """Test multiclass classification performance."""
        X, _ = time_series_datasets['standard']
        # Create multiclass problem
        y = np.random.randint(0, 4, len(X))
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        pipeline = rocket_pipeline(n_kernels=100, random_state=42)
        pipeline.fit(X_train, y_train)
        
        y_pred = pipeline.predict(X_test)
        
        # Get classification report
        report = classification_report(y_test, y_pred, output_dict=True)
        
        # Check report structure
        assert 'accuracy' in report
        assert 'macro avg' in report
        assert 'weighted avg' in report
        
        # Check per-class metrics exist
        for class_label in np.unique(y_test):
            assert str(class_label) in report


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

# EOF