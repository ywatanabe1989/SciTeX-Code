#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-12-12 06:49:15 (ywatanabe)"
# File: ./scitex_repo/src/scitex/ai/Classifier.py

THIS_FILE = (
    "/data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/ai/Classifier.py"
)

"""
Functionality:
    * Provides a unified interface for initializing various scikit-learn classifiers
    * Supports optional preprocessing with StandardScaler

Input:
    * Classifier name as string
    * Optional class weights for imbalanced datasets
    * Optional scaler for feature preprocessing

Output:
    * Initialized classifier or pipeline with scaler

Prerequisites:
    * scikit-learn
    * Optional: CatBoost for CatBoostClassifier
"""

from typing import Dict, List, Optional, Union

from sklearn.base import BaseEstimator as _BaseEstimator
from sklearn.discriminant_analysis import (
    QuadraticDiscriminantAnalysis as _QuadraticDiscriminantAnalysis,
)
from sklearn.ensemble import AdaBoostClassifier as _AdaBoostClassifier
from sklearn.gaussian_process import (
    GaussianProcessClassifier as _GaussianProcessClassifier,
)
from sklearn.linear_model import LogisticRegression as _LogisticRegression
from sklearn.linear_model import (
    PassiveAggressiveClassifier as _PassiveAggressiveClassifier,
)
from sklearn.linear_model import Perceptron as _Perceptron
from sklearn.linear_model import RidgeClassifier as _RidgeClassifier
from sklearn.linear_model import SGDClassifier as _SGDClassifier
from sklearn.neighbors import KNeighborsClassifier as _KNeighborsClassifier
from sklearn.pipeline import Pipeline as _Pipeline
from sklearn.pipeline import make_pipeline as _make_pipeline
from sklearn.preprocessing import StandardScaler as _StandardScaler
from sklearn.svm import SVC as _SVC
from sklearn.svm import LinearSVC as _LinearSVC


class Classifier:
    """
    Server for initializing various scikit-learn classifiers with consistent interface.

    Example
    -------
    >>> clf_server = Classifier(class_weight={0: 1.0, 1: 2.0}, random_state=42)
    >>> clf = clf_server("SVC", scaler=_StandardScaler())
    >>> print(clf_server.list)
    ['CatBoostClassifier', 'Perceptron', ...]

    Parameters
    ----------
    class_weight : Optional[Dict[int, float]]
        Class weights for handling imbalanced datasets
    random_state : int
        Random seed for reproducibility
    """

    def __init__(
        self,
        class_weight: Optional[Dict[int, float]] = None,
        random_state: int = 42,
    ):
        self.class_weight = class_weight
        self.random_state = random_state

        self.clf_candi = {
            "Perceptron": _Perceptron(
                penalty="l2",
                class_weight=self.class_weight,
                random_state=random_state,
            ),
            "PassiveAggressiveClassifier": _PassiveAggressiveClassifier(
                class_weight=self.class_weight, random_state=random_state
            ),
            "LogisticRegression": _LogisticRegression(
                class_weight=self.class_weight, random_state=random_state
            ),
            "SGDClassifier": _SGDClassifier(
                class_weight=self.class_weight, random_state=random_state
            ),
            "RidgeClassifier": _RidgeClassifier(
                class_weight=self.class_weight, random_state=random_state
            ),
            "QuadraticDiscriminantAnalysis": _QuadraticDiscriminantAnalysis(),
            "GaussianProcessClassifier": _GaussianProcessClassifier(
                random_state=random_state
            ),
            "KNeighborsClassifier": _KNeighborsClassifier(),
            "AdaBoostClassifier": _AdaBoostClassifier(random_state=random_state),
            "LinearSVC": _LinearSVC(
                class_weight=self.class_weight, random_state=random_state
            ),
            "SVC": _SVC(class_weight=self.class_weight, random_state=random_state),
        }

    def __call__(
        self, clf_str: str, scaler: Optional[_BaseEstimator] = None
    ) -> Union[_BaseEstimator, _Pipeline]:
        if clf_str not in self.clf_candi:
            raise ValueError(
                f"Unknown classifier: {clf_str}. Available options: {self.list}"
            )

        if scaler is not None:
            clf = _make_pipeline(scaler, self.clf_candi[clf_str])
        else:
            clf = self.clf_candi[clf_str]
        return clf

    @property
    def list(self) -> List[str]:
        return list(self.clf_candi.keys())


if __name__ == "__main__":
    clf_server = Classifier()
    clf = clf_server("SVC", scaler=_StandardScaler())
