#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2021-12-12 14:50:37 (ywatanabe)"


from catboost import CatBoostClassifier
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
from sklearn.ensemble import AdaBoostClassifier
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.linear_model import (
    LogisticRegression,
    PassiveAggressiveClassifier,
    Perceptron,
    RidgeClassifier,
    SGDClassifier,
)
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC, LinearSVC


class Classifiers(object):
    """Instanciates one of scikit-learn-like Clasifiers in the same manner.

    Example:
        clf_server = ClassifierServer(class_weight={0:1., 1:2.}, random_state=42)
        clf_str = "SVC"
        clf = clf_server(clf_str, scaler=StandardScaler())

    Note:
        clf_str is acceptable if it is in the list below.

        ['CatBoostClassifier',
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
         'SVC']
    """

    def __init__(self, class_weight=None, random_state=42):
        self.class_weight = class_weight
        self.random_state = random_state

        self.clf_candi = {
            "CatBoostClassifier": CatBoostClassifier(
                class_weights=self.class_weight, verbose=False
            ),
            "Perceptron": Perceptron(
                penalty="l2", class_weight=self.class_weight, random_state=random_state
            ),
            "PassiveAggressiveClassifier": PassiveAggressiveClassifier(
                class_weight=self.class_weight, random_state=random_state
            ),
            "LogisticRegression": LogisticRegression(
                class_weight=self.class_weight, random_state=random_state
            ),
            "SGDClassifier": SGDClassifier(
                class_weight=self.class_weight, random_state=random_state
            ),
            "RidgeClassifier": RidgeClassifier(
                class_weight=self.class_weight, random_state=random_state
            ),
            "QuadraticDiscriminantAnalysis": QuadraticDiscriminantAnalysis(),
            "GaussianProcessClassifier": GaussianProcessClassifier(
                random_state=random_state
            ),
            "KNeighborsClassifier": KNeighborsClassifier(),
            "AdaBoostClassifier": AdaBoostClassifier(random_state=random_state),
            "LinearSVC": LinearSVC(
                class_weight=self.class_weight, random_state=random_state
            ),
            "SVC": SVC(class_weight=self.class_weight, random_state=random_state),
        }

    def __call__(self, clf_str, scaler=None):
        if scaler is not None:
            clf = make_pipeline(scaler, self.clf_candi[clf_str])  # fixme
        else:
            clf = self.clf_candi[clf_str]
        return clf

    @property
    def list(
        self,
    ):
        clf_list = list(self.clf_candi.keys())
        return clf_list


if __name__ == "__main__":
    clf_server = ClassifierServer()
    # l = clf_server.list
    clf = clf_server("SVC", scaler=StandardScaler())
