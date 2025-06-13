#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 14:55:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/io/_load_modules/test__catboost.py

"""
Comprehensive tests for CatBoost model loading functionality.

Tests cover:
- Basic CatBoost classifier and regressor loading
- Model validation and prediction functionality
- Error handling for invalid inputs
- File extension validation
- Import error handling when CatBoost not available
- Model format compatibility testing
- Advanced model features and configurations
"""

import os
import sys
import tempfile
import pytest
from unittest.mock import Mock, patch, MagicMock
import numpy as np


class TestLoadCatBoost:
    """Test suite for _load_catboost function."""

    @pytest.fixture
    def mock_catboost_available(self):
        """Mock CatBoost availability."""
        with patch('scitex.io._load_modules._catboost.CATBOOST_AVAILABLE', True):
            yield

    @pytest.fixture
    def mock_catboost_unavailable(self):
        """Mock CatBoost unavailability."""
        with patch('scitex.io._load_modules._catboost.CATBOOST_AVAILABLE', False):
            yield

    @pytest.fixture
    def mock_catboost_classifier(self):
        """Mock CatBoost classifier."""
        mock_classifier = Mock()
        mock_classifier.load_model = Mock(return_value=mock_classifier)
        mock_classifier.predict = Mock(return_value=np.array([0, 1, 0, 1, 1]))
        mock_classifier.predict_proba = Mock(return_value=np.random.rand(5, 2))
        mock_classifier.get_feature_importance = Mock(return_value=np.random.rand(10))
        return mock_classifier

    @pytest.fixture
    def mock_catboost_regressor(self):
        """Mock CatBoost regressor."""
        mock_regressor = Mock()
        mock_regressor.load_model = Mock(return_value=mock_regressor)
        mock_regressor.predict = Mock(return_value=np.random.rand(5))
        mock_regressor.get_feature_importance = Mock(return_value=np.random.rand(10))
        return mock_regressor

    def test_import_error_when_catboost_unavailable(self, mock_catboost_unavailable):
        """Test ImportError when CatBoost is not installed."""
from scitex.io._load_modules import _load_catboost
        
        with pytest.raises(ImportError, match="CatBoost is not installed"):
            _load_catboost("model.cbm")

    def test_valid_extension_check(self, mock_catboost_available):
        """Test that function validates .cbm extension."""
from scitex.io._load_modules import _load_catboost
        
        invalid_extensions = [
            "model.pkl",
            "model.joblib", 
            "model.json",
            "model.txt",
            "model.h5",
            "model.pth",
            "model.onnx",
            "model.cbm.bak"  # Double extension
        ]
        
        for invalid_path in invalid_extensions:
            with pytest.raises(ValueError, match="File must have .cbm extension"):
                _load_catboost(invalid_path)

    def test_classifier_loading_success(self, mock_catboost_available):
        """Test successful CatBoost classifier loading."""
        import scitex.io._load_modules._catboost as catboost_module
        
        # Mock CatBoost classes
        mock_classifier_class = Mock()
        mock_regressor_class = Mock()
        mock_instance = Mock()
        mock_loaded_model = Mock()
        mock_instance.load_model.return_value = mock_loaded_model
        mock_classifier_class.return_value = mock_instance
        
        # Patch the classes into the module
        with patch.object(catboost_module, 'CatBoostClassifier', mock_classifier_class), \
             patch.object(catboost_module, 'CatBoostRegressor', mock_regressor_class):
            
            result = catboost_module._load_catboost("model.cbm")
            
            mock_classifier_class.assert_called_once()
            mock_instance.load_model.assert_called_once_with("model.cbm")
            assert result == mock_loaded_model

    def test_regressor_loading_fallback(self, mock_catboost_available):
        """Test fallback to regressor when classifier loading fails."""
        import scitex.io._load_modules._catboost as catboost_module
        
        # Mock CatBoost classes
        mock_classifier_class = Mock()
        mock_regressor_class = Mock()
        
        # Setup classifier to fail
        mock_classifier_instance = Mock()
        mock_classifier_instance.load_model.side_effect = Exception("Classifier loading failed")
        mock_classifier_class.return_value = mock_classifier_instance
        
        # Setup regressor to succeed
        mock_regressor_instance = Mock()
        mock_loaded_model = Mock()
        mock_regressor_instance.load_model.return_value = mock_loaded_model
        mock_regressor_class.return_value = mock_regressor_instance
        
        # Patch both classes
        with patch.object(catboost_module, 'CatBoostClassifier', mock_classifier_class), \
             patch.object(catboost_module, 'CatBoostRegressor', mock_regressor_class):
            
            result = catboost_module._load_catboost("model.cbm")
            
            # Verify classifier was tried first
            mock_classifier_class.assert_called_once()
            mock_classifier_instance.load_model.assert_called_once_with("model.cbm")
            
            # Verify regressor was tried as fallback
            mock_regressor_class.assert_called_once()
            mock_regressor_instance.load_model.assert_called_once_with("model.cbm")
            
            assert result == mock_loaded_model

    def test_kwargs_passed_to_load_model(self, mock_catboost_available):
        """Test that kwargs are passed to load_model method."""
        import scitex.io._load_modules._catboost as catboost_module
        
        # Mock CatBoost classes
        mock_classifier_class = Mock()
        mock_regressor_class = Mock()
        mock_instance = Mock()
        mock_loaded_model = Mock()
        mock_instance.load_model.return_value = mock_loaded_model
        mock_classifier_class.return_value = mock_instance
        
        # Patch classes
        with patch.object(catboost_module, 'CatBoostClassifier', mock_classifier_class), \
             patch.object(catboost_module, 'CatBoostRegressor', mock_regressor_class):
            
            custom_kwargs = {'format': 'cbm', 'ignore_checkpoints': True}
            catboost_module._load_catboost("model.cbm", **custom_kwargs)
            
            mock_instance.load_model.assert_called_once_with("model.cbm", **custom_kwargs)

    def test_real_catboost_classifier_loading(self):
        """Test loading real CatBoost classifier if available."""
        try:
            import catboost
from scitex.io._load_modules import _load_catboost
            
            # Create and train a simple classifier
            X = np.random.rand(100, 5)
            y = np.random.randint(0, 2, 100)
            
            model = catboost.CatBoostClassifier(
                iterations=10, 
                verbose=False,
                random_seed=42
            )
            model.fit(X, y)
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix='.cbm', delete=False) as f:
                model.save_model(f.name)
                temp_path = f.name
            
            try:
                # Load using our function
                loaded_model = _load_catboost(temp_path)
                
                # Verify model functionality
                assert hasattr(loaded_model, 'predict')
                assert hasattr(loaded_model, 'predict_proba')
                
                # Test prediction
                predictions = loaded_model.predict(X[:5])
                assert len(predictions) == 5
                assert all(pred in [0, 1] for pred in predictions)
                
                # Test probability prediction
                probabilities = loaded_model.predict_proba(X[:5])
                assert probabilities.shape == (5, 2)
                assert np.allclose(probabilities.sum(axis=1), 1.0)
                
            finally:
                os.unlink(temp_path)
                
        except ImportError:
            pytest.skip("CatBoost not available for real testing")

    def test_real_catboost_regressor_loading(self):
        """Test loading real CatBoost regressor if available."""
        try:
            import catboost
from scitex.io._load_modules import _load_catboost
            
            # Create and train a simple regressor
            X = np.random.rand(100, 5)
            y = np.random.rand(100) * 100  # Continuous target
            
            model = catboost.CatBoostRegressor(
                iterations=10, 
                verbose=False,
                random_seed=42
            )
            model.fit(X, y)
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix='.cbm', delete=False) as f:
                model.save_model(f.name)
                temp_path = f.name
            
            try:
                # Load using our function
                loaded_model = _load_catboost(temp_path)
                
                # Verify model functionality
                assert hasattr(loaded_model, 'predict')
                
                # Test prediction
                predictions = loaded_model.predict(X[:5])
                assert len(predictions) == 5
                assert all(isinstance(pred, (int, float, np.number)) for pred in predictions)
                
            finally:
                os.unlink(temp_path)
                
        except ImportError:
            pytest.skip("CatBoost not available for real testing")

    def test_model_with_categorical_features(self):
        """Test loading model trained with categorical features."""
        try:
            import catboost
            import pandas as pd
from scitex.io._load_modules import _load_catboost
            
            # Create dataset with categorical features
            np.random.seed(42)
            data = pd.DataFrame({
                'numeric1': np.random.rand(100),
                'numeric2': np.random.rand(100),
                'category1': np.random.choice(['A', 'B', 'C'], 100),
                'category2': np.random.choice(['X', 'Y'], 100)
            })
            y = np.random.randint(0, 2, 100)
            
            categorical_features = ['category1', 'category2']
            
            model = catboost.CatBoostClassifier(
                iterations=10,
                verbose=False,
                cat_features=categorical_features,
                random_seed=42
            )
            model.fit(data, y)
            
            # Save and load model
            with tempfile.NamedTemporaryFile(suffix='.cbm', delete=False) as f:
                model.save_model(f.name)
                temp_path = f.name
            
            try:
                loaded_model = _load_catboost(temp_path)
                
                # Test prediction with categorical data
                test_data = data.iloc[:5]
                predictions = loaded_model.predict(test_data)
                assert len(predictions) == 5
                
            finally:
                os.unlink(temp_path)
                
        except ImportError:
            pytest.skip("CatBoost not available for categorical feature testing")

    def test_model_feature_importance(self):
        """Test that loaded model retains feature importance functionality."""
        try:
            import catboost
from scitex.io._load_modules import _load_catboost
            
            # Create and train model
            X = np.random.rand(100, 5)
            y = np.random.randint(0, 2, 100)
            
            model = catboost.CatBoostClassifier(
                iterations=10, 
                verbose=False,
                random_seed=42
            )
            model.fit(X, y)
            
            # Save and load model
            with tempfile.NamedTemporaryFile(suffix='.cbm', delete=False) as f:
                model.save_model(f.name)
                temp_path = f.name
            
            try:
                loaded_model = _load_catboost(temp_path)
                
                # Test feature importance
                importance = loaded_model.get_feature_importance()
                assert len(importance) == 5  # 5 features
                assert all(imp >= 0 for imp in importance)  # Non-negative importance
                
            finally:
                os.unlink(temp_path)
                
        except ImportError:
            pytest.skip("CatBoost not available for feature importance testing")

    def test_multiclass_classification_model(self):
        """Test loading multiclass classification model."""
        try:
            import catboost
from scitex.io._load_modules import _load_catboost
            
            # Create multiclass dataset
            X = np.random.rand(150, 4)
            y = np.random.randint(0, 3, 150)  # 3 classes
            
            model = catboost.CatBoostClassifier(
                iterations=10,
                verbose=False,
                random_seed=42
            )
            model.fit(X, y)
            
            # Save and load model
            with tempfile.NamedTemporaryFile(suffix='.cbm', delete=False) as f:
                model.save_model(f.name)
                temp_path = f.name
            
            try:
                loaded_model = _load_catboost(temp_path)
                
                # Test multiclass prediction
                predictions = loaded_model.predict(X[:5])
                assert len(predictions) == 5
                assert all(pred in [0, 1, 2] for pred in predictions)
                
                # Test multiclass probabilities
                probabilities = loaded_model.predict_proba(X[:5])
                assert probabilities.shape == (5, 3)  # 5 samples, 3 classes
                assert np.allclose(probabilities.sum(axis=1), 1.0)
                
            finally:
                os.unlink(temp_path)
                
        except ImportError:
            pytest.skip("CatBoost not available for multiclass testing")

    def test_edge_case_filenames(self, mock_catboost_available):
        """Test edge cases with filenames."""
        import scitex.io._load_modules._catboost as catboost_module
        
        # Mock CatBoost classes
        mock_classifier_class = Mock()
        mock_regressor_class = Mock()
        mock_instance = Mock()
        mock_loaded_model = Mock()
        mock_instance.load_model.return_value = mock_loaded_model
        mock_classifier_class.return_value = mock_instance
        
        with patch.object(catboost_module, 'CatBoostClassifier', mock_classifier_class), \
             patch.object(catboost_module, 'CatBoostRegressor', mock_regressor_class):
            
            # Test various valid .cbm filenames
            valid_names = [
                "model.cbm",
                "my_model.cbm",
                "model-v1.cbm",
                "model_final.cbm",
                "/path/to/model.cbm",
                "./model.cbm",
                "../model.cbm",
                "model with spaces.cbm",
                "模型.cbm",  # Unicode filename
            ]
            
            for name in valid_names:
                # Should work for .cbm files
                result = catboost_module._load_catboost(name)
                assert result == mock_loaded_model
            
            # Test uppercase extension separately due to case sensitivity
            result = catboost_module._load_catboost("UPPERCASE.CBM")
            assert result == mock_loaded_model

    def test_both_classifier_and_regressor_fail(self, mock_catboost_available):
        """Test when both classifier and regressor loading fail."""
        import scitex.io._load_modules._catboost as catboost_module
        
        # Mock CatBoost classes
        mock_classifier_class = Mock()
        mock_regressor_class = Mock()
        
        # Make both fail
        mock_classifier_instance = Mock()
        mock_classifier_instance.load_model.side_effect = Exception("Classifier failed")
        mock_classifier_class.return_value = mock_classifier_instance
        
        mock_regressor_instance = Mock()
        mock_regressor_instance.load_model.side_effect = Exception("Regressor failed")
        mock_regressor_class.return_value = mock_regressor_instance
        
        with patch.object(catboost_module, 'CatBoostClassifier', mock_classifier_class), \
             patch.object(catboost_module, 'CatBoostRegressor', mock_regressor_class):
            
            # Should raise the regressor exception (the final attempt)
            with pytest.raises(Exception, match="Regressor failed"):
                catboost_module._load_catboost("model.cbm")

    def test_integration_with_main_load_function(self):
        """Test integration with main scitex.io.load function."""
        try:
            import catboost
            import scitex
            
            # Create and save a model
            X = np.random.rand(50, 3)
            y = np.random.randint(0, 2, 50)
            
            model = catboost.CatBoostClassifier(
                iterations=5,
                verbose=False,
                random_seed=42
            )
            model.fit(X, y)
            
            with tempfile.NamedTemporaryFile(suffix='.cbm', delete=False) as f:
                model.save_model(f.name)
                temp_path = f.name
            
            try:
                # Test loading through main interface
                loaded_model = scitex.io.load(temp_path)
                
                # Verify functionality
                assert hasattr(loaded_model, 'predict')
                predictions = loaded_model.predict(X[:3])
                assert len(predictions) == 3
                
            finally:
                os.unlink(temp_path)
                
        except ImportError:
            pytest.skip("CatBoost not available for integration testing")


if __name__ == "__main__":
    pytest.main([os.path.abspath(__file__), "-v"])
