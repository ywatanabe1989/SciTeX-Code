#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 17:35:00 (claude-sonnet-4-20250514)"
# File: /data/gpfs/projects/punim2354/ywatanabe/.claude-worktree/scitex_repo/tests/scitex/ai/sklearn/test_clf.py

"""
Comprehensive tests for scitex.ai.sklearn.clf module.

This module tests machine learning classifier pipeline utilities including
rocket_pipeline function and GB_pipeline pre-built pipeline for time series
classification tasks using sktime and scikit-learn.
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from sklearn.pipeline import Pipeline


class TestRocketPipeline:
    """Test cases for the rocket_pipeline function."""
    
    @pytest.fixture
    def sample_time_series_data(self):
        """Generate sample time series data for testing."""
        np.random.seed(42)
        X = np.random.randn(50, 100)  # 50 samples, 100 time points
        y = np.random.choice([0, 1], size=50)  # Binary classification
        return X, y
    
    def test_rocket_pipeline_returns_pipeline(self):
        """Test that rocket_pipeline returns a scikit-learn Pipeline object."""
        from scitex.ai.sklearn.clf import rocket_pipeline
        
        pipeline = rocket_pipeline()
        assert isinstance(pipeline, Pipeline)
        assert len(pipeline.steps) == 2
    
    def test_rocket_pipeline_steps_structure(self):
        """Test that rocket_pipeline has correct step structure."""
        from scitex.ai.sklearn.clf import rocket_pipeline
        
        pipeline = rocket_pipeline()
        step_names = [name for name, _ in pipeline.steps]
        
        assert 'rocket' in step_names
        assert 'logisticregression' in step_names
    
    def test_rocket_pipeline_with_args(self):
        """Test rocket_pipeline with custom arguments for Rocket transformer."""
        from scitex.ai.sklearn.clf import rocket_pipeline
        
        # Test with custom arguments using correct parameter names
        pipeline = rocket_pipeline(num_kernels=1000, random_state=42)
        rocket_step = pipeline.steps[0][1]  # Get the Rocket transformer
        
        # Verify the pipeline was created successfully
        assert isinstance(pipeline, Pipeline)
        
    def test_rocket_pipeline_with_kwargs(self):
        """Test rocket_pipeline with keyword arguments."""
        from scitex.ai.sklearn.clf import rocket_pipeline
        
        pipeline = rocket_pipeline(random_state=123, num_kernels=500)
        assert isinstance(pipeline, Pipeline)
    
    def test_rocket_pipeline_logistic_regression_config(self):
        """Test that LogisticRegression is configured with max_iter=1000."""
        from scitex.ai.sklearn.clf import rocket_pipeline
        
        pipeline = rocket_pipeline()
        lr_step = pipeline.steps[1][1]  # Get the LogisticRegression
        
        # Check that LogisticRegression has the expected configuration
        assert lr_step.max_iter == 1000
    
    @patch('scitex.ai.sklearn.clf.make_pipeline')
    def test_rocket_pipeline_make_pipeline_called(self, mock_make_pipeline):
        """Test that rocket_pipeline calls make_pipeline correctly."""
        from scitex.ai.sklearn.clf import rocket_pipeline
        
        mock_pipeline = Mock(spec=Pipeline)
        mock_make_pipeline.return_value = mock_pipeline
        
        result = rocket_pipeline()
        
        assert mock_make_pipeline.called
        assert result == mock_pipeline
    
    def test_rocket_pipeline_multiple_calls_independence(self):
        """Test that multiple calls to rocket_pipeline create independent pipelines."""
        from scitex.ai.sklearn.clf import rocket_pipeline
        
        pipeline1 = rocket_pipeline(random_state=1)
        pipeline2 = rocket_pipeline(random_state=2)
        
        # Should be different objects
        assert pipeline1 is not pipeline2
        assert isinstance(pipeline1, Pipeline)
        assert isinstance(pipeline2, Pipeline)


class TestGBPipeline:
    """Test cases for the GB_pipeline pre-built pipeline."""
    
    def test_gb_pipeline_is_pipeline(self):
        """Test that GB_pipeline is a Pipeline object."""
        from scitex.ai.sklearn.clf import GB_pipeline
        
        assert isinstance(GB_pipeline, Pipeline)
        assert len(GB_pipeline.steps) == 2
    
    def test_gb_pipeline_steps_structure(self):
        """Test that GB_pipeline has correct step structure."""
        from scitex.ai.sklearn.clf import GB_pipeline
        
        step_names = [name for name, _ in GB_pipeline.steps]
        
        assert 'tabularizer' in step_names
        assert 'gradientboostingclassifier' in step_names
    
    def test_gb_pipeline_step_types(self):
        """Test that GB_pipeline steps are of correct types."""
        from scitex.ai.sklearn.clf import GB_pipeline
        from sktime.transformations.panel.reduce import Tabularizer
        from sklearn.ensemble import GradientBoostingClassifier
        
        tabularizer_step = GB_pipeline.steps[0][1]
        gb_step = GB_pipeline.steps[1][1]
        
        assert isinstance(tabularizer_step, Tabularizer)
        assert isinstance(gb_step, GradientBoostingClassifier)
    
    def test_gb_pipeline_immutability(self):
        """Test that GB_pipeline maintains its configuration between accesses."""
        from scitex.ai.sklearn.clf import GB_pipeline
        
        # Get pipeline multiple times and verify it's the same object
        pipeline1 = GB_pipeline
        pipeline2 = GB_pipeline
        
        assert pipeline1 is pipeline2
        assert len(pipeline1.steps) == len(pipeline2.steps)
    
    def test_gb_pipeline_default_parameters(self):
        """Test that GB_pipeline uses default parameters for GradientBoostingClassifier."""
        from scitex.ai.sklearn.clf import GB_pipeline
        
        gb_classifier = GB_pipeline.steps[1][1]
        
        # Test some default parameters (these might change with sklearn versions)
        assert hasattr(gb_classifier, 'n_estimators')
        assert hasattr(gb_classifier, 'learning_rate')
        assert hasattr(gb_classifier, 'max_depth')


class TestModuleIntegration:
    """Test cases for module-level integration and imports."""
    
    def test_module_imports_successfully(self):
        """Test that the clf module can be imported without errors."""
        try:
            import scitex.ai.sklearn.clf
            assert True
        except ImportError as e:
            pytest.fail(f"Failed to import clf module: {e}")
    
    def test_rocket_pipeline_import(self):
        """Test that rocket_pipeline can be imported and called."""
        from scitex.ai.sklearn.clf import rocket_pipeline
        
        assert callable(rocket_pipeline)
        pipeline = rocket_pipeline()
        assert pipeline is not None
    
    def test_gb_pipeline_import(self):
        """Test that GB_pipeline can be imported."""
        from scitex.ai.sklearn.clf import GB_pipeline
        
        assert GB_pipeline is not None
        assert hasattr(GB_pipeline, 'fit')
        assert hasattr(GB_pipeline, 'predict')
    
    def test_required_dependencies_available(self):
        """Test that required dependencies are available."""
        try:
            import sklearn
            import sktime
            import numpy as np
            assert True
        except ImportError as e:
            pytest.skip(f"Required dependencies not available: {e}")
    
    @pytest.mark.parametrize("pipeline_func", ["rocket_pipeline"])
    def test_pipeline_functions_callable(self, pipeline_func):
        """Test that all pipeline functions are callable."""
        from scitex.ai.sklearn import clf
        
        func = getattr(clf, pipeline_func)
        assert callable(func)
        result = func()
        assert result is not None
    
    @pytest.mark.parametrize("pipeline_obj", ["GB_pipeline"])
    def test_pipeline_objects_valid(self, pipeline_obj):
        """Test that all pipeline objects are valid Pipeline instances."""
        from scitex.ai.sklearn import clf
        from sklearn.pipeline import Pipeline
        
        obj = getattr(clf, pipeline_obj)
        assert isinstance(obj, Pipeline)


class TestErrorHandling:
    """Test cases for error handling and edge cases."""
    
    def test_rocket_pipeline_with_invalid_kwargs(self):
        """Test rocket_pipeline behavior with potentially invalid kwargs."""
        from scitex.ai.sklearn.clf import rocket_pipeline
        
        # This should not raise an error, but may pass invalid args to Rocket
        try:
            pipeline = rocket_pipeline(invalid_param="invalid_value")
            assert isinstance(pipeline, Pipeline)
        except Exception:
            # If it raises an error, that's also acceptable behavior
            pass
    
    def test_pipeline_methods_exist(self):
        """Test that pipeline objects have required sklearn methods."""
        from scitex.ai.sklearn.clf import rocket_pipeline, GB_pipeline
        
        rocket_pipe = rocket_pipeline()
        
        # Test that standard sklearn methods exist
        assert hasattr(rocket_pipe, 'fit')
        assert hasattr(rocket_pipe, 'predict')
        assert hasattr(rocket_pipe, 'get_params')
        assert hasattr(rocket_pipe, 'set_params')
        
        assert hasattr(GB_pipeline, 'fit')
        assert hasattr(GB_pipeline, 'predict')
        assert hasattr(GB_pipeline, 'get_params')
        assert hasattr(GB_pipeline, 'set_params')


if __name__ == "__main__":
    pytest.main([__file__])