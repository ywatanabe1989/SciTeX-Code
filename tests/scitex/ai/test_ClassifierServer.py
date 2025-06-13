#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-01 16:00:00 (ywatanabe)"
# File: ./tests/scitex/ai/test_ClassifierServer.py

"""Tests for scitex.ai.ClassifierServer module."""

import pytest
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.pipeline import Pipeline
from scitex.ai.classifier_server import ClassifierServer


class TestClassifierServer:
    """Test suite for ClassifierServer class."""

    @pytest.fixture
    def server(self):
        """Create a basic ClassifierServer instance."""
        return ClassifierServer()

    @pytest.fixture
    def server_with_weights(self):
        """Create a ClassifierServer with class weights."""
        return ClassifierServer(class_weight={0: 1.0, 1: 2.0}, random_state=123)

    def test_initialization_default(self, server):
        """Test default initialization."""
        assert server.class_weight is None
        assert server.random_state == 42
        assert hasattr(server, 'clf_candi')
        assert isinstance(server.clf_candi, dict)

    def test_initialization_with_params(self, server_with_weights):
        """Test initialization with custom parameters."""
        assert server_with_weights.class_weight == {0: 1.0, 1: 2.0}
        assert server_with_weights.random_state == 123

    def test_available_classifiers(self, server):
        """Test that expected classifiers are available."""
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
            "SVC",
        ]
        
        for clf_name in expected_classifiers:
            assert clf_name in server.clf_candi

    def test_list_property(self, server):
        """Test the list property returns classifier names."""
        clf_list = server.list
        assert isinstance(clf_list, list)
        assert len(clf_list) == 11  # Number of classifiers
        assert "SVC" in clf_list
        assert "LogisticRegression" in clf_list

    def test_call_without_scaler(self, server):
        """Test calling server to get classifier without scaler."""
        clf = server("SVC")
        
        # Should return the raw classifier
        assert hasattr(clf, 'fit')
        assert hasattr(clf, 'predict')
        assert clf.__class__.__name__ == 'SVC'

    def test_call_with_scaler(self, server):
        """Test calling server to get classifier with scaler."""
        scaler = StandardScaler()
        clf = server("SVC", scaler=scaler)
        
        # Should return a pipeline
        assert isinstance(clf, Pipeline)
        assert len(clf.steps) == 2
        assert clf.steps[0][0] == 'standardscaler'
        assert clf.steps[1][0] == 'svc'

    def test_call_with_different_scalers(self, server):
        """Test with different types of scalers."""
        # StandardScaler
        clf1 = server("LogisticRegression", scaler=StandardScaler())
        assert isinstance(clf1, Pipeline)
        
        # MinMaxScaler
        clf2 = server("LogisticRegression", scaler=MinMaxScaler())
        assert isinstance(clf2, Pipeline)
        assert clf2.steps[0][0] == 'minmaxscaler'

    def test_invalid_classifier_error(self, server):
        """Test error handling for invalid classifier name."""
        with pytest.raises(ValueError, match="Unknown classifier: InvalidClassifier"):
            server("InvalidClassifier")

    def test_class_weight_propagation(self, server_with_weights):
        """Test that class weights are properly set in classifiers."""
        # Classifiers that support class_weight
        weight_supporting = [
            "Perceptron", "PassiveAggressiveClassifier", 
            "LogisticRegression", "SGDClassifier", 
            "RidgeClassifier", "LinearSVC", "SVC"
        ]
        
        for clf_name in weight_supporting:
            clf = server_with_weights.clf_candi[clf_name]
            assert hasattr(clf, 'class_weight')
            assert clf.class_weight == {0: 1.0, 1: 2.0}

    def test_random_state_propagation(self, server_with_weights):
        """Test that random state is properly set in classifiers."""
        # Classifiers that support random_state
        random_state_supporting = [
            "Perceptron", "PassiveAggressiveClassifier",
            "LogisticRegression", "SGDClassifier", "RidgeClassifier",
            "GaussianProcessClassifier", "AdaBoostClassifier",
            "LinearSVC", "SVC"
        ]
        
        for clf_name in random_state_supporting:
            clf = server_with_weights.clf_candi[clf_name]
            assert hasattr(clf, 'random_state')
            assert clf.random_state == 123

    def test_classifiers_are_sklearn_compatible(self, server):
        """Test that all classifiers are sklearn compatible."""
        for clf_name, clf in server.clf_candi.items():
            # Check sklearn estimator interface
            assert hasattr(clf, 'fit')
            assert hasattr(clf, 'predict')
            assert isinstance(clf, BaseEstimator)

    def test_independent_classifier_instances(self, server):
        """Test that calling server returns independent instances."""
        clf1 = server("SVC")
        clf2 = server("SVC")
        
        # Should be the same instance (from clf_candi)
        assert clf1 is clf2

    def test_qda_no_class_weight(self, server_with_weights):
        """Test that QDA doesn't have class_weight parameter."""
        qda = server_with_weights.clf_candi["QuadraticDiscriminantAnalysis"]
        assert not hasattr(qda, 'class_weight')

    def test_knn_no_random_state(self, server_with_weights):
        """Test that KNN doesn't have random_state parameter."""
        knn = server_with_weights.clf_candi["KNeighborsClassifier"]
        assert not hasattr(knn, 'random_state')

    def test_pipeline_preserves_random_state(self, server_with_weights):
        """Test that pipeline preserves classifier's random state."""
        pipeline = server_with_weights("SVC", scaler=StandardScaler())
        svc = pipeline.steps[1][1]
        assert svc.random_state == 123

    @pytest.mark.parametrize("clf_name", [
        "Perceptron", "LogisticRegression", "SVC", "LinearSVC",
        "SGDClassifier", "RidgeClassifier", "AdaBoostClassifier"
    ])
    def test_each_classifier_basic_functionality(self, server, clf_name):
        """Test basic functionality of each classifier."""
        clf = server(clf_name)
        
        # Very basic test - just check it's a valid classifier
        assert hasattr(clf, 'fit')
        assert hasattr(clf, 'predict')
        
        # Check it's the right type
        expected_class = clf_name
        if expected_class == "LinearSVC":
            expected_class = "LinearSVC"
        elif expected_class == "SVC":
            expected_class = "SVC"
        assert clf.__class__.__name__ == expected_class

    def test_example_usage(self):
        """Test the example usage from docstring."""
        clf_server = ClassifierServer(class_weight={0: 1.0, 1: 2.0}, random_state=42)
        clf = clf_server("SVC", scaler=StandardScaler())
        
        assert isinstance(clf, Pipeline)
        assert 'CatBoostClassifier' not in clf_server.list  # Not included by default
        assert 'Perceptron' in clf_server.list


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

# --------------------------------------------------------------------------------
# Start of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/ai/ClassifierServer.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-12-12 06:49:15 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/ai/ClassifierServer.py
#
# THIS_FILE = "/data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/ai/ClassifierServer.py"
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
#             "AdaBoostClassifier": _AdaBoostClassifier(
#                 random_state=random_state
#             ),
#             "LinearSVC": _LinearSVC(
#                 class_weight=self.class_weight, random_state=random_state
#             ),
#             "SVC": _SVC(
#                 class_weight=self.class_weight, random_state=random_state
#             ),
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
# End of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/ai/ClassifierServer.py
# --------------------------------------------------------------------------------
