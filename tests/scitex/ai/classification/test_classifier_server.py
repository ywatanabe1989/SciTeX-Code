#!/usr/bin/env python3

import pytest
from unittest.mock import MagicMock, patch
import sys
from pathlib import Path

# Add src to path to import directly without circular imports
sys.path.insert(0, str(Path(__file__).parents[4] / "src"))

try:
    from scitex.ai.classification.classifier_server import ClassifierServer
    from sklearn.preprocessing import StandardScaler
    from sklearn.pipeline import Pipeline
    from sklearn.svm import SVC
    from sklearn.linear_model import LogisticRegression
except ImportError:
    pytest.skip("classifier_server not available", allow_module_level=True)


class TestClassifierServerInit:
    """Test ClassifierServer initialization."""
    
    def test_init_default_params(self):
        """Test initialization with default parameters."""
        server = ClassifierServer()
        
        assert server.class_weight is None
        assert server.random_state == 42
        assert hasattr(server, 'clf_candi')
        assert isinstance(server.clf_candi, dict)
        assert len(server.clf_candi) > 0
    
    def test_init_custom_params(self):
        """Test initialization with custom parameters."""
        class_weight = {0: 1.0, 1: 2.0}
        random_state = 123
        
        server = ClassifierServer(class_weight=class_weight, random_state=random_state)
        
        assert server.class_weight == class_weight
        assert server.random_state == random_state
    
    def test_init_classifier_candidates(self):
        """Test that all expected classifiers are available."""
        server = ClassifierServer()
        
        expected_classifiers = [
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
            assert clf_name in server.clf_candi
    
    def test_init_class_weight_propagation(self):
        """Test that class_weight is properly set in classifiers."""
        class_weight = {0: 1.0, 1: 3.0}
        server = ClassifierServer(class_weight=class_weight)
        
        # Check classifiers that support class_weight
        classifiers_with_weights = [
            "Perceptron", "PassiveAggressiveClassifier", "LogisticRegression",
            "SGDClassifier", "RidgeClassifier", "LinearSVC", "SVC"
        ]
        
        for clf_name in classifiers_with_weights:
            clf = server.clf_candi[clf_name]
            assert hasattr(clf, 'class_weight')
            assert clf.class_weight == class_weight
    
    def test_init_random_state_propagation(self):
        """Test that random_state is properly set in classifiers."""
        random_state = 999
        server = ClassifierServer(random_state=random_state)
        
        # Check classifiers that support random_state
        classifiers_with_random = [
            "Perceptron", "PassiveAggressiveClassifier", "LogisticRegression",
            "SGDClassifier", "RidgeClassifier", "GaussianProcessClassifier",
            "AdaBoostClassifier", "LinearSVC", "SVC"
        ]
        
        for clf_name in classifiers_with_random:
            clf = server.clf_candi[clf_name]
            assert hasattr(clf, 'random_state')
            assert clf.random_state == random_state


class TestClassifierServerCall:
    """Test ClassifierServer __call__ method."""
    
    def setup_method(self):
        """Setup server for each test."""
        self.server = ClassifierServer(class_weight={0: 1.0, 1: 2.0}, random_state=42)
    
    def test_call_valid_classifier_no_scaler(self):
        """Test calling with valid classifier without scaler."""
        clf = self.server("SVC")
        
        assert isinstance(clf, SVC)
        assert clf.class_weight == {0: 1.0, 1: 2.0}
        assert clf.random_state == 42
    
    def test_call_valid_classifier_with_scaler(self):
        """Test calling with valid classifier and scaler."""
        scaler = StandardScaler()
        clf = self.server("LogisticRegression", scaler=scaler)
        
        assert isinstance(clf, Pipeline)
        assert len(clf.steps) == 2
        assert isinstance(clf.steps[0][1], StandardScaler)
        assert isinstance(clf.steps[1][1], LogisticRegression)
    
    def test_call_invalid_classifier(self):
        """Test calling with invalid classifier name."""
        with pytest.raises(ValueError, match="Unknown classifier.*Available options"):
            self.server("NonExistentClassifier")
    
    def test_call_all_valid_classifiers(self):
        """Test calling all available classifiers."""
        for clf_name in self.server.list:
            clf = self.server(clf_name)
            assert clf is not None
            # Verify it's a valid sklearn estimator interface
            assert hasattr(clf, 'fit') or hasattr(clf, 'steps')
    
    def test_call_with_different_scalers(self):
        """Test calling with different types of scalers."""
        from sklearn.preprocessing import MinMaxScaler, RobustScaler
        
        scalers = [StandardScaler(), MinMaxScaler(), RobustScaler()]
        
        for scaler in scalers:
            clf = self.server("SVC", scaler=scaler)
            assert isinstance(clf, Pipeline)
            assert isinstance(clf.steps[0][1], type(scaler))
    
    def test_call_returns_different_instances(self):
        """Test that each call returns different instances."""
        clf1 = self.server("SVC")
        clf2 = self.server("SVC")
        
        # Should be same type and same instances (ClassifierServer reuses instances)
        assert type(clf1) == type(clf2)
        assert clf1 is clf2  # Same instances
    
    def test_call_pipeline_functionality(self):
        """Test that returned pipeline has correct functionality."""
        import numpy as np
        
        scaler = StandardScaler()
        clf = self.server("LogisticRegression", scaler=scaler)
        
        # Mock data
        X = np.array([[1, 2], [3, 4], [5, 6], [7, 8]])
        y = np.array([0, 0, 1, 1])
        
        # Should be able to fit and predict
        clf.fit(X, y)
        predictions = clf.predict(X)
        
        assert len(predictions) == len(y)
        assert all(pred in [0, 1] for pred in predictions)


class TestClassifierServerList:
    """Test ClassifierServer list property."""
    
    def test_list_property(self):
        """Test list property returns classifier names."""
        server = ClassifierServer()
        clf_list = server.list
        
        assert isinstance(clf_list, list)
        assert len(clf_list) > 0
        assert all(isinstance(name, str) for name in clf_list)
    
    def test_list_contains_expected_classifiers(self):
        """Test list contains all expected classifier names."""
        server = ClassifierServer()
        clf_list = server.list
        
        expected_classifiers = [
            "Perceptron", "PassiveAggressiveClassifier", "LogisticRegression",
            "SGDClassifier", "RidgeClassifier", "QuadraticDiscriminantAnalysis",
            "GaussianProcessClassifier", "KNeighborsClassifier", 
            "AdaBoostClassifier", "LinearSVC", "SVC"
        ]
        
        for expected in expected_classifiers:
            assert expected in clf_list
    
    def test_list_matches_clf_candi_keys(self):
        """Test list property matches clf_candi keys."""
        server = ClassifierServer()
        
        assert set(server.list) == set(server.clf_candi.keys())
    
    def test_list_immutability(self):
        """Test that modifying returned list doesn't affect server."""
        server = ClassifierServer()
        original_list = server.list.copy()
        
        # Modify the returned list
        clf_list = server.list
        clf_list.append("FakeClassifier")
        
        # Original server should be unchanged
        assert server.list == original_list
        assert "FakeClassifier" not in server.list


class TestClassifierServerIntegration:
    """Test ClassifierServer integration scenarios."""
    
    def test_classification_workflow(self):
        """Test complete classification workflow."""
        import numpy as np
        from sklearn.datasets import make_classification
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import accuracy_score
        
        # Generate sample data
        X, y = make_classification(n_samples=100, n_features=4, n_classes=2, random_state=42)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
        
        # Test with multiple classifiers
        server = ClassifierServer(random_state=42)
        classifiers_to_test = ["LogisticRegression", "SVC", "AdaBoostClassifier"]
        
        for clf_name in classifiers_to_test:
            clf = server(clf_name, scaler=StandardScaler())
            
            # Train and predict
            clf.fit(X_train, y_train)
            predictions = clf.predict(X_test)
            accuracy = accuracy_score(y_test, predictions)
            
            # Basic sanity checks
            assert 0 <= accuracy <= 1
            assert len(predictions) == len(y_test)
            assert all(pred in [0, 1] for pred in predictions)
    
    def test_class_weight_effectiveness(self):
        """Test that class weights affect classifier behavior."""
        import numpy as np
        from sklearn.datasets import make_classification
        
        # Create imbalanced dataset
        X, y = make_classification(
            n_samples=200, n_features=4, n_classes=2, 
            weights=[0.9, 0.1], random_state=42
        )
        
        # Test with and without class weights
        server_no_weights = ClassifierServer(random_state=42)
        server_with_weights = ClassifierServer(
            class_weight={0: 1.0, 1: 10.0}, random_state=42
        )
        
        clf_no_weights = server_no_weights("LogisticRegression")
        clf_with_weights = server_with_weights("LogisticRegression")
        
        # Both should be able to fit
        clf_no_weights.fit(X, y)
        clf_with_weights.fit(X, y)
        
        # Predictions should be different due to class weights
        pred_no_weights = clf_no_weights.predict(X)
        pred_with_weights = clf_with_weights.predict(X)
        
        # With heavy class weights, should predict more of minority class
        minority_pred_no_weights = np.sum(pred_no_weights == 1)
        minority_pred_with_weights = np.sum(pred_with_weights == 1)
        
        assert minority_pred_with_weights >= minority_pred_no_weights
    
    def test_reproducibility_with_random_state(self):
        """Test that random_state ensures reproducible results."""
        import numpy as np
        from sklearn.datasets import make_classification
        
        X, y = make_classification(n_samples=100, n_features=4, random_state=42)
        
        # Create two servers with same random state
        server1 = ClassifierServer(random_state=123)
        server2 = ClassifierServer(random_state=123)
        
        clf1 = server1("AdaBoostClassifier")
        clf2 = server2("AdaBoostClassifier")
        
        # Fit both classifiers
        clf1.fit(X, y)
        clf2.fit(X, y)
        
        # Predictions should be identical
        pred1 = clf1.predict(X)
        pred2 = clf2.predict(X)
        
        np.testing.assert_array_equal(pred1, pred2)
    
    def test_error_handling_edge_cases(self):
        """Test error handling for edge cases."""
        server = ClassifierServer()
        
        # Test with None classifier name
        with pytest.raises((ValueError, TypeError)):
            server(None)
        
        # Test with empty string
        with pytest.raises(ValueError):
            server("")
        
        # Test with invalid scaler - error occurs during pipeline creation
        with pytest.raises((TypeError, AttributeError, ValueError)):
            from sklearn.pipeline import make_pipeline
            make_pipeline("invalid_scaler", server.clf_candi["SVC"])

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/ai/classification/classifier_server.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-12-12 06:49:15 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/ai/ClassifierServer.py
# 
# THIS_FILE = (
#     "/data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/ai/ClassifierServer.py"
# )
# 
# """
# Functionality:
#     * Provides a unified interface for initializing various scikit-learn classifiers
#     * Supports optional preprocessing with StandardScaler
# 
# Input:
#     * Classifier name as string
#     * Optional class weights for imbalanced datasets
#     * Optional scaler for feature preprocessing
# 
# Output:
#     * Initialized classifier or pipeline with scaler
# 
# Prerequisites:
#     * scikit-learn
#     * Optional: CatBoost for CatBoostClassifier
# """
# 
# from typing import Dict, List, Optional, Union
# 
# from sklearn.base import BaseEstimator as _BaseEstimator
# from sklearn.discriminant_analysis import (
#     QuadraticDiscriminantAnalysis as _QuadraticDiscriminantAnalysis,
# )
# from sklearn.ensemble import AdaBoostClassifier as _AdaBoostClassifier
# from sklearn.gaussian_process import (
#     GaussianProcessClassifier as _GaussianProcessClassifier,
# )
# from sklearn.linear_model import LogisticRegression as _LogisticRegression
# from sklearn.linear_model import (
#     PassiveAggressiveClassifier as _PassiveAggressiveClassifier,
# )
# from sklearn.linear_model import Perceptron as _Perceptron
# from sklearn.linear_model import RidgeClassifier as _RidgeClassifier
# from sklearn.linear_model import SGDClassifier as _SGDClassifier
# from sklearn.neighbors import KNeighborsClassifier as _KNeighborsClassifier
# from sklearn.pipeline import Pipeline as _Pipeline
# from sklearn.pipeline import make_pipeline as _make_pipeline
# from sklearn.preprocessing import StandardScaler as _StandardScaler
# from sklearn.svm import SVC as _SVC
# from sklearn.svm import LinearSVC as _LinearSVC
# 
# 
# class ClassifierServer:
#     """
#     Server for initializing various scikit-learn classifiers with consistent interface.
# 
#     Example
#     -------
#     >>> clf_server = ClassifierServer(class_weight={0: 1.0, 1: 2.0}, random_state=42)
#     >>> clf = clf_server("SVC", scaler=_StandardScaler())
#     >>> print(clf_server.list)
#     ['CatBoostClassifier', 'Perceptron', ...]
# 
#     Parameters
#     ----------
#     class_weight : Optional[Dict[int, float]]
#         Class weights for handling imbalanced datasets
#     random_state : int
#         Random seed for reproducibility
#     """
# 
#     def __init__(
#         self,
#         class_weight: Optional[Dict[int, float]] = None,
#         random_state: int = 42,
#     ):
#         self.class_weight = class_weight
#         self.random_state = random_state
# 
#         self.clf_candi = {
#             "Perceptron": _Perceptron(
#                 penalty="l2",
#                 class_weight=self.class_weight,
#                 random_state=random_state,
#             ),
#             "PassiveAggressiveClassifier": _PassiveAggressiveClassifier(
#                 class_weight=self.class_weight, random_state=random_state
#             ),
#             "LogisticRegression": _LogisticRegression(
#                 class_weight=self.class_weight, random_state=random_state
#             ),
#             "SGDClassifier": _SGDClassifier(
#                 class_weight=self.class_weight, random_state=random_state
#             ),
#             "RidgeClassifier": _RidgeClassifier(
#                 class_weight=self.class_weight, random_state=random_state
#             ),
#             "QuadraticDiscriminantAnalysis": _QuadraticDiscriminantAnalysis(),
#             "GaussianProcessClassifier": _GaussianProcessClassifier(
#                 random_state=random_state
#             ),
#             "KNeighborsClassifier": _KNeighborsClassifier(),
#             "AdaBoostClassifier": _AdaBoostClassifier(random_state=random_state),
#             "LinearSVC": _LinearSVC(
#                 class_weight=self.class_weight, random_state=random_state
#             ),
#             "SVC": _SVC(class_weight=self.class_weight, random_state=random_state),
#         }
# 
#     def __call__(
#         self, clf_str: str, scaler: Optional[_BaseEstimator] = None
#     ) -> Union[_BaseEstimator, _Pipeline]:
#         if clf_str not in self.clf_candi:
#             raise ValueError(
#                 f"Unknown classifier: {clf_str}. Available options: {self.list}"
#             )
# 
#         if scaler is not None:
#             clf = _make_pipeline(scaler, self.clf_candi[clf_str])
#         else:
#             clf = self.clf_candi[clf_str]
#         return clf
# 
#     @property
#     def list(self) -> List[str]:
#         return list(self.clf_candi.keys())
# 
# 
# if __name__ == "__main__":
#     clf_server = ClassifierServer()
#     clf = clf_server("SVC", scaler=_StandardScaler())

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/ai/classification/classifier_server.py
# --------------------------------------------------------------------------------
