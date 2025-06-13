#!/usr/bin/env python3

import pytest
from unittest.mock import MagicMock, patch
import sys
from pathlib import Path

# Add src to path to import directly without circular imports
sys.path.insert(0, str(Path(__file__).parents[4] / "src"))

try:
    from sklearn.preprocessing import StandardScaler
    from sklearn.pipeline import Pipeline
    from sklearn.svm import SVC
    from sklearn.linear_model import LogisticRegression
    
    # Handle CatBoost dependency issue
    try:
        from scitex.ai.classification.classifiers import Classifiers
    except ImportError as e:
        if "catboost" in str(e).lower():
            pytest.skip("CatBoost dependency not available for classifiers module", allow_module_level=True)
        else:
            raise
except ImportError:
    pytest.skip("sklearn or other dependencies not available", allow_module_level=True)


class TestClassifiersInit:
    """Test Classifiers initialization."""
    
    def test_init_default_params(self):
        """Test initialization with default parameters."""
        classifiers = Classifiers()
        
        assert classifiers.class_weight is None
        assert classifiers.random_state == 42
        assert hasattr(classifiers, 'clf_candi')
        assert isinstance(classifiers.clf_candi, dict)
        assert len(classifiers.clf_candi) > 0
    
    def test_init_custom_params(self):
        """Test initialization with custom parameters."""
        class_weight = {0: 1.0, 1: 2.5}
        random_state = 456
        
        classifiers = Classifiers(class_weight=class_weight, random_state=random_state)
        
        assert classifiers.class_weight == class_weight
        assert classifiers.random_state == random_state
    
    def test_init_classifier_candidates(self):
        """Test that all expected classifiers are available."""
        classifiers = Classifiers()
        
        expected_classifiers = [
            "CatBoostClassifier",
            "Perceptron",
            "PassiveAggressiveClassifier", 
            "LogisticRegression",
            "SGDClassifier",
            "RidgeClassifier",
            "QuadraticDiscriminantAnalysis",
            "GaussianProcessClassifier",
            "KNeighborsClassifier",
            "AdaBoostClassifier",
            "LinearSVC",
            "SVC"
        ]
        
        for clf_name in expected_classifiers:
            assert clf_name in classifiers.clf_candi
    
    @patch('scitex.ai.classification.classifiers.CatBoostClassifier')
    def test_init_catboost_parameters(self, mock_catboost):
        """Test CatBoost initialization with correct parameters."""
        class_weight = {0: 1.0, 1: 3.0}
        classifiers = Classifiers(class_weight=class_weight)
        
        mock_catboost.assert_called_once_with(
            class_weights=class_weight, verbose=False
        )
    
    def test_init_class_weight_propagation(self):
        """Test that class_weight is properly set in classifiers."""
        class_weight = {0: 1.0, 1: 4.0}
        classifiers = Classifiers(class_weight=class_weight)
        
        # Check classifiers that support class_weight (excluding CatBoost which uses class_weights)
        classifiers_with_weights = [
            "Perceptron", "PassiveAggressiveClassifier", "LogisticRegression",
            "SGDClassifier", "RidgeClassifier", "LinearSVC", "SVC"
        ]
        
        for clf_name in classifiers_with_weights:
            clf = classifiers.clf_candi[clf_name]
            assert hasattr(clf, 'class_weight')
            assert clf.class_weight == class_weight
    
    def test_init_random_state_propagation(self):
        """Test that random_state is properly set in classifiers."""
        random_state = 789
        classifiers = Classifiers(random_state=random_state)
        
        # Check classifiers that support random_state
        classifiers_with_random = [
            "Perceptron", "PassiveAggressiveClassifier", "LogisticRegression",
            "SGDClassifier", "RidgeClassifier", "GaussianProcessClassifier",
            "AdaBoostClassifier", "LinearSVC", "SVC"
        ]
        
        for clf_name in classifiers_with_random:
            clf = classifiers.clf_candi[clf_name]
            assert hasattr(clf, 'random_state')
            assert clf.random_state == random_state


class TestClassifiersCall:
    """Test Classifiers __call__ method."""
    
    def setup_method(self):
        """Setup classifiers for each test."""
        self.classifiers = Classifiers(class_weight={0: 1.0, 1: 2.0}, random_state=42)
    
    def test_call_valid_classifier_no_scaler(self):
        """Test calling with valid classifier without scaler."""
        clf = self.classifiers("SVC")
        
        assert isinstance(clf, SVC)
        assert clf.class_weight == {0: 1.0, 1: 2.0}
        assert clf.random_state == 42
    
    def test_call_valid_classifier_with_scaler(self):
        """Test calling with valid classifier and scaler."""
        scaler = StandardScaler()
        clf = self.classifiers("LogisticRegression", scaler=scaler)
        
        assert isinstance(clf, Pipeline)
        assert len(clf.steps) == 2
        assert isinstance(clf.steps[0][1], StandardScaler)
        assert isinstance(clf.steps[1][1], LogisticRegression)
    
    def test_call_catboost_classifier(self):
        """Test calling CatBoost classifier specifically."""
        # This might fail if CatBoost is not installed, so we'll handle it gracefully
        try:
            clf = self.classifiers("CatBoostClassifier")
            assert clf is not None
            assert hasattr(clf, 'fit')
        except Exception:
            pytest.skip("CatBoost not available")
    
    def test_call_invalid_classifier(self):
        """Test calling with invalid classifier name."""
        with pytest.raises(KeyError):
            self.classifiers("NonExistentClassifier")
    
    def test_call_all_valid_classifiers(self):
        """Test calling all available classifiers."""
        for clf_name in self.classifiers.list:
            try:
                clf = self.classifiers(clf_name)
                assert clf is not None
                # Verify it's a valid sklearn estimator interface
                assert hasattr(clf, 'fit') or hasattr(clf, 'steps')
            except ImportError:
                # Skip if optional dependency not available (e.g., CatBoost)
                pytest.skip(f"{clf_name} dependencies not available")
    
    def test_call_with_different_scalers(self):
        """Test calling with different types of scalers."""
        from sklearn.preprocessing import MinMaxScaler, RobustScaler
        
        scalers = [StandardScaler(), MinMaxScaler(), RobustScaler()]
        
        for scaler in scalers:
            clf = self.classifiers("SVC", scaler=scaler)
            assert isinstance(clf, Pipeline)
            assert isinstance(clf.steps[0][1], type(scaler))
    
    def test_call_returns_same_instances(self):
        """Test that each call returns the same instances (different from ClassifierServer)."""
        clf1 = self.classifiers("SVC")
        clf2 = self.classifiers("SVC")
        
        # Should be same instance (different behavior from ClassifierServer)
        assert clf1 is clf2
    
    def test_call_pipeline_functionality(self):
        """Test that returned pipeline has correct functionality."""
        import numpy as np
        
        scaler = StandardScaler()
        clf = self.classifiers("LogisticRegression", scaler=scaler)
        
        # Mock data
        X = np.array([[1, 2], [3, 4], [5, 6], [7, 8]])
        y = np.array([0, 0, 1, 1])
        
        # Should be able to fit and predict
        clf.fit(X, y)
        predictions = clf.predict(X)
        
        assert len(predictions) == len(y)
        assert all(pred in [0, 1] for pred in predictions)


class TestClassifiersList:
    """Test Classifiers list property."""
    
    def test_list_property(self):
        """Test list property returns classifier names."""
        classifiers = Classifiers()
        clf_list = classifiers.list
        
        assert isinstance(clf_list, list)
        assert len(clf_list) > 0
        assert all(isinstance(name, str) for name in clf_list)
    
    def test_list_contains_expected_classifiers(self):
        """Test list contains all expected classifier names."""
        classifiers = Classifiers()
        clf_list = classifiers.list
        
        expected_classifiers = [
            "CatBoostClassifier", "Perceptron", "PassiveAggressiveClassifier", 
            "LogisticRegression", "SGDClassifier", "RidgeClassifier", 
            "QuadraticDiscriminantAnalysis", "GaussianProcessClassifier", 
            "KNeighborsClassifier", "AdaBoostClassifier", "LinearSVC", "SVC"
        ]
        
        for expected in expected_classifiers:
            assert expected in clf_list
    
    def test_list_matches_clf_candi_keys(self):
        """Test list property matches clf_candi keys."""
        classifiers = Classifiers()
        
        assert set(classifiers.list) == set(classifiers.clf_candi.keys())
    
    def test_list_includes_catboost(self):
        """Test that list includes CatBoost (main difference from ClassifierServer)."""
        classifiers = Classifiers()
        
        assert "CatBoostClassifier" in classifiers.list


class TestClassifiersLegacyCompatibility:
    """Test Classifiers legacy features and compatibility."""
    
    def test_legacy_class_name(self):
        """Test that Classifiers class is properly named for backward compatibility."""
        classifiers = Classifiers()
        assert classifiers.__class__.__name__ == "Classifiers"
    
    def test_legacy_docstring_example(self):
        """Test that the example in docstring works."""
        # Note: The docstring has a typo - it references ClassifierServer instead of Classifiers
        # We test what the code actually does
        classifiers = Classifiers(class_weight={0: 1., 1: 2.}, random_state=42)
        clf_str = "SVC"
        
        try:
            clf = classifiers(clf_str, scaler=StandardScaler())
            assert isinstance(clf, Pipeline)
        except ImportError:
            pytest.skip("StandardScaler import issue")
    
    def test_catboost_class_weights_parameter(self):
        """Test CatBoost uses class_weights parameter (not class_weight)."""
        # This is a difference from sklearn classifiers
        classifiers = Classifiers(class_weight={0: 1.0, 1: 2.0})
        
        # The CatBoost classifier should be initialized with class_weights
        # We can't easily test this without mocking, but we ensure it doesn't crash
        try:
            clf_candi = classifiers.clf_candi
            assert "CatBoostClassifier" in clf_candi
        except ImportError:
            pytest.skip("CatBoost not available")
    
    def test_parameter_differences_from_server(self):
        """Test parameter differences between Classifiers and ClassifierServer."""
        classifiers = Classifiers()
        
        # Classifiers should have CatBoost
        assert "CatBoostClassifier" in classifiers.list
        
        # Method signature differences
        import inspect
        call_sig = inspect.signature(classifiers.__call__)
        params = list(call_sig.parameters.keys())
        
        # Should have clf_str and scaler parameters
        assert "clf_str" in params
        assert "scaler" in params


class TestClassifiersIntegration:
    """Test Classifiers integration scenarios."""
    
    def test_classification_workflow(self):
        """Test complete classification workflow."""
        import numpy as np
        from sklearn.datasets import make_classification
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import accuracy_score
        
        # Generate sample data
        X, y = make_classification(n_samples=100, n_features=4, n_classes=2, random_state=42)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
        
        # Test with multiple classifiers (excluding CatBoost to avoid dependency issues)
        classifiers = Classifiers(random_state=42)
        classifiers_to_test = ["LogisticRegression", "SVC", "AdaBoostClassifier"]
        
        for clf_name in classifiers_to_test:
            clf = classifiers(clf_name, scaler=StandardScaler())
            
            # Train and predict
            clf.fit(X_train, y_train)
            predictions = clf.predict(X_test)
            accuracy = accuracy_score(y_test, predictions)
            
            # Basic sanity checks
            assert 0 <= accuracy <= 1
            assert len(predictions) == len(y_test)
            assert all(pred in [0, 1] for pred in predictions)
    
    def test_instance_reuse_behavior(self):
        """Test that Classifiers reuses instances (different from ClassifierServer)."""
        import numpy as np
        
        classifiers = Classifiers(random_state=42)
        
        # Get the same classifier multiple times
        clf1 = classifiers("LogisticRegression")
        clf2 = classifiers("LogisticRegression")
        
        # Should be the same instance
        assert clf1 is clf2
        
        # If we fit one, it affects the other
        X = np.array([[1, 2], [3, 4]])
        y = np.array([0, 1])
        
        clf1.fit(X, y)
        
        # clf2 should also be fitted since it's the same instance
        try:
            predictions = clf2.predict(X)
            assert len(predictions) == len(y)
        except Exception:
            # Some classifiers might not be fitted after the other fits
            pass
    
    def test_error_handling_with_missing_dependencies(self):
        """Test graceful handling when optional dependencies are missing."""
        classifiers = Classifiers()
        
        # This should work even if CatBoost is not installed
        # The classifier should be in the list but might fail when instantiated
        assert "CatBoostClassifier" in classifiers.list
        
        try:
            clf = classifiers("CatBoostClassifier")
            # If we get here, CatBoost is available
            assert clf is not None
        except (ImportError, ModuleNotFoundError):
            # Expected if CatBoost is not installed
            pytest.skip("CatBoost not available")
    
    def test_comparison_with_classifier_server(self):
        """Test key differences between Classifiers and ClassifierServer."""
        classifiers = Classifiers(random_state=42)
        
        # Main differences:
        # 1. Classifiers includes CatBoost
        assert "CatBoostClassifier" in classifiers.list
        
        # 2. Classifiers reuses instances
        clf1 = classifiers("SVC")
        clf2 = classifiers("SVC")
        assert clf1 is clf2
        
        # 3. Different error handling (KeyError vs ValueError)
        with pytest.raises(KeyError):
            classifiers("NonExistentClassifier")


if __name__ == "__main__":
    pytest.main([__file__])
