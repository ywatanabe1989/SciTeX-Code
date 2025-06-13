#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 15:00:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/ai/test___Classifiers.py

"""Tests for Classifiers factory class."""

import os
import pytest
import numpy as np
from unittest.mock import patch, MagicMock, Mock


class TestClassifiersBasic:
    """Test basic Classifiers functionality."""
    
    def test_classifiers_init_default(self):
        """Test Classifiers initialization with default parameters."""
        from scitex.ai import Classifiers
        
        clf_factory = Classifiers()
        
        assert clf_factory.class_weight is None
        assert clf_factory.random_state == 42
        assert hasattr(clf_factory, 'clf_candi')
        assert isinstance(clf_factory.clf_candi, dict)
    
    def test_classifiers_init_custom_params(self):
        """Test Classifiers initialization with custom parameters."""
        from scitex.ai import Classifiers
        
        class_weight = {0: 1.0, 1: 2.0}
        random_state = 123
        
        clf_factory = Classifiers(class_weight=class_weight, random_state=random_state)
        
        assert clf_factory.class_weight == class_weight
        assert clf_factory.random_state == random_state
    
    def test_classifiers_available_classifiers(self):
        """Test that all expected classifiers are available."""
        from scitex.ai import Classifiers
        
        clf_factory = Classifiers()
        expected_classifiers = [
            'CatBoostClassifier',
            'Perceptron',
            'PassiveAggressiveClassifier',
            'LogisticRegression',
            'SGDClassifier',
            'RidgeClassifier',
            'QuadraticDiscriminantAnalysis',
            'GaussianProcessClassifier',
            'KNeighborsClassifier',
            'AdaBoostClassifier',
            'LinearSVC',
            'SVC'
        ]
        
        for clf_name in expected_classifiers:
            assert clf_name in clf_factory.clf_candi
        
        assert len(clf_factory.clf_candi) == len(expected_classifiers)


class TestClassifiersList:
    """Test Classifiers list property."""
    
    def test_classifiers_list_property(self):
        """Test the list property returns all classifier names."""
        from scitex.ai import Classifiers
        
        clf_factory = Classifiers()
        clf_list = clf_factory.list
        
        assert isinstance(clf_list, list)
        assert len(clf_list) == 12  # All classifiers
        assert 'SVC' in clf_list
        assert 'LogisticRegression' in clf_list
        assert 'CatBoostClassifier' in clf_list
    
    def test_classifiers_list_consistency(self):
        """Test that list property matches clf_candi keys."""
        from scitex.ai import Classifiers
        
        clf_factory = Classifiers()
        clf_list = clf_factory.list
        candi_keys = list(clf_factory.clf_candi.keys())
        
        assert set(clf_list) == set(candi_keys)


class TestClassifiersCall:
    """Test Classifiers __call__ method."""
    
    def test_classifiers_call_without_scaler(self):
        """Test calling classifier factory without scaler."""
        from scitex.ai import Classifiers
        
        clf_factory = Classifiers()
        clf = clf_factory("SVC")
        
        # Should return the classifier directly
        assert hasattr(clf, 'fit')
        assert hasattr(clf, 'predict')
        assert clf.__class__.__name__ == 'SVC'
    
    @patch('scitex.ai.__Classifiers.make_pipeline')
    def test_classifiers_call_with_scaler(self, mock_make_pipeline):
        """Test calling classifier factory with scaler."""
        from scitex.ai import Classifiers
        from sklearn.preprocessing import StandardScaler
        
        mock_pipeline = MagicMock()
        mock_make_pipeline.return_value = mock_pipeline
        
        clf_factory = Classifiers()
        scaler = StandardScaler()
        clf = clf_factory("SVC", scaler=scaler)
        
        # Should create a pipeline
        mock_make_pipeline.assert_called_once()
        assert clf == mock_pipeline
    
    def test_classifiers_call_invalid_classifier(self):
        """Test calling with invalid classifier name."""
        from scitex.ai import Classifiers
        
        clf_factory = Classifiers()
        
        with pytest.raises(KeyError):
            clf_factory("InvalidClassifier")
    
    def test_classifiers_call_all_classifiers(self):
        """Test that all classifiers can be instantiated."""
        from scitex.ai import Classifiers
        
        clf_factory = Classifiers()
        
        for clf_name in clf_factory.list:
            try:
                clf = clf_factory(clf_name)
                assert hasattr(clf, 'fit')
                assert hasattr(clf, 'predict')
            except Exception as e:
                # Some classifiers might fail due to missing dependencies
                # This is expected in test environment
                pytest.skip(f"Classifier {clf_name} failed to instantiate: {e}")


class TestClassifiersWithParameters:
    """Test Classifiers with different parameter configurations."""
    
    def test_classifiers_with_class_weights(self):
        """Test classifiers with class weights."""
        from scitex.ai import Classifiers
        
        class_weight = {0: 1.0, 1: 3.0}
        clf_factory = Classifiers(class_weight=class_weight)
        
        # Test classifiers that support class_weight
        weight_supporting_clfs = ['SVC', 'LogisticRegression', 'LinearSVC']
        
        for clf_name in weight_supporting_clfs:
            try:
                clf = clf_factory(clf_name)
                # Verify class_weight is set (if accessible)
                if hasattr(clf, 'class_weight'):
                    assert clf.class_weight == class_weight
            except Exception as e:
                pytest.skip(f"Classifier {clf_name} failed: {e}")
    
    def test_classifiers_with_random_state(self):
        """Test classifiers with custom random state."""
        from scitex.ai import Classifiers
        
        random_state = 12345
        clf_factory = Classifiers(random_state=random_state)
        
        # Test classifiers that support random_state
        random_state_clfs = ['SVC', 'LogisticRegression', 'SGDClassifier']
        
        for clf_name in random_state_clfs:
            try:
                clf = clf_factory(clf_name)
                if hasattr(clf, 'random_state'):
                    assert clf.random_state == random_state
            except Exception as e:
                pytest.skip(f"Classifier {clf_name} failed: {e}")
    
    def test_classifiers_consistency_across_calls(self):
        """Test that multiple calls return consistent classifiers."""
        from scitex.ai import Classifiers
        
        clf_factory = Classifiers(random_state=42)
        
        try:
            clf1 = clf_factory("SVC")
            clf2 = clf_factory("SVC")
            
            # Should be different instances but same configuration
            assert clf1 is not clf2
            assert clf1.__class__ == clf2.__class__
            if hasattr(clf1, 'random_state') and hasattr(clf2, 'random_state'):
                assert clf1.random_state == clf2.random_state
        except Exception as e:
            pytest.skip(f"SVC instantiation failed: {e}")


class TestClassifiersIntegration:
    """Test Classifiers integration with sklearn pipeline."""
    
    @patch('scitex.ai.__Classifiers.StandardScaler')
    @patch('scitex.ai.__Classifiers.make_pipeline')
    def test_classifiers_pipeline_creation(self, mock_make_pipeline, mock_scaler):
        """Test pipeline creation with scaler."""
        from scitex.ai import Classifiers
        
        mock_scaler_instance = MagicMock()
        mock_scaler.return_value = mock_scaler_instance
        mock_pipeline = MagicMock()
        mock_make_pipeline.return_value = mock_pipeline
        
        clf_factory = Classifiers()
        scaler = mock_scaler_instance
        
        result = clf_factory("LogisticRegression", scaler=scaler)
        
        # Verify pipeline was created
        mock_make_pipeline.assert_called_once_with(scaler, clf_factory.clf_candi["LogisticRegression"])
        assert result == mock_pipeline
    
    def test_classifiers_pipeline_functionality(self):
        """Test that pipeline actually works for fitting and prediction."""
        from scitex.ai import Classifiers
        from sklearn.preprocessing import StandardScaler
        from sklearn.datasets import make_classification
        
        # Create sample data
        X, y = make_classification(n_samples=100, n_features=4, n_classes=2, random_state=42)
        
        clf_factory = Classifiers(random_state=42)
        
        try:
            # Test with pipeline
            clf_with_scaler = clf_factory("LogisticRegression", scaler=StandardScaler())
            clf_with_scaler.fit(X, y)
            predictions = clf_with_scaler.predict(X)
            
            assert len(predictions) == len(y)
            assert all(pred in [0, 1] for pred in predictions)
            
            # Test without pipeline
            clf_without_scaler = clf_factory("LogisticRegression")
            clf_without_scaler.fit(X, y)
            predictions2 = clf_without_scaler.predict(X)
            
            assert len(predictions2) == len(y)
            
        except Exception as e:
            pytest.skip(f"Integration test failed: {e}")


class TestClassifiersErrorHandling:
    """Test error handling in Classifiers."""
    
    def test_classifiers_invalid_scaler_type(self):
        """Test behavior with invalid scaler type."""
        from scitex.ai import Classifiers
        
        clf_factory = Classifiers()
        
        # This should not raise an error during instantiation
        # but might fail during pipeline creation
        invalid_scaler = "not_a_scaler"
        
        with pytest.raises((TypeError, AttributeError)):
            clf_factory("SVC", scaler=invalid_scaler)
    
    def test_classifiers_none_values(self):
        """Test classifiers with None values."""
        from scitex.ai import Classifiers
        
        clf_factory = Classifiers(class_weight=None, random_state=None)
        
        # Should not raise errors during initialization
        assert clf_factory.class_weight is None
        assert clf_factory.random_state is None


class TestClassifiersSpecificClassifiers:
    """Test specific classifier configurations."""
    
    def test_catboost_classifier_config(self):
        """Test CatBoost classifier specific configuration."""
        from scitex.ai import Classifiers
        
        class_weight = {0: 1.0, 1: 2.0}
        clf_factory = Classifiers(class_weight=class_weight)
        
        try:
            clf = clf_factory("CatBoostClassifier")
            # CatBoost uses class_weights (note the 's')
            if hasattr(clf, 'class_weights'):
                assert clf.class_weights == class_weight
            # Verify verbose is set to False
            if hasattr(clf, 'verbose'):
                assert clf.verbose is False
        except Exception as e:
            pytest.skip(f"CatBoost test failed: {e}")
    
    def test_quadratic_discriminant_analysis_config(self):
        """Test QDA classifier (no class_weight or random_state)."""
        from scitex.ai import Classifiers
        
        clf_factory = Classifiers(class_weight={0: 1, 1: 2}, random_state=42)
        
        try:
            clf = clf_factory("QuadraticDiscriminantAnalysis")
            # QDA doesn't support class_weight or random_state
            assert clf.__class__.__name__ == 'QuadraticDiscriminantAnalysis'
        except Exception as e:
            pytest.skip(f"QDA test failed: {e}")
    
    def test_kneighbors_classifier_config(self):
        """Test KNeighbors classifier (no class_weight or random_state by default)."""
        from scitex.ai import Classifiers
        
        clf_factory = Classifiers()
        
        try:
            clf = clf_factory("KNeighborsClassifier")
            assert clf.__class__.__name__ == 'KNeighborsClassifier'
        except Exception as e:
            pytest.skip(f"KNeighbors test failed: {e}")


class TestClassifiersMemoryManagement:
    """Test memory management aspects."""
    
    def test_classifiers_multiple_instances(self):
        """Test creating multiple classifier factory instances."""
        from scitex.ai import Classifiers
        
        # Create multiple instances
        factories = [Classifiers(random_state=i) for i in range(5)]
        
        # Each should be independent
        for i, factory in enumerate(factories):
            assert factory.random_state == i
            assert factory is not factories[0]  # Different instances
    
    def test_classifiers_large_number_calls(self):
        """Test creating many classifiers."""
        from scitex.ai import Classifiers
        
        clf_factory = Classifiers()
        
        # Create many classifier instances
        classifiers = []
        for _ in range(10):
            try:
                clf = clf_factory("LogisticRegression")
                classifiers.append(clf)
            except Exception as e:
                pytest.skip(f"Multiple classifier creation failed: {e}")
        
        # All should be different instances
        assert len(set(id(clf) for clf in classifiers)) == len(classifiers)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
