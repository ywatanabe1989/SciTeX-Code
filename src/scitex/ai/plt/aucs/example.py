#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-07 18:56:57 (ywatanabe)"
# File: ./scitex_repo/src/scitex/ai/plt/aucs/example.py

import matplotlib.pyplot as plt
import scitex
import numpy as np
from sklearn import datasets, svm
from sklearn.model_selection import train_test_split
from .roc_auc import roc_auc
from .pre_rec_auc import pre_rec_auc

################################################################################
## MNIST
################################################################################

digits = datasets.load_digits()

# flatten the images
n_samples = len(digits.images)
data = digits.images.reshape((n_samples, -1))

# Create a classifier: a support vector classifier
clf = svm.SVC(gamma=0.001, probability=True)

# Split data into 50% train and 50% test subsets
X_train, X_test, y_train, y_test = train_test_split(
    data, digits.target, test_size=0.5, shuffle=False
)

# Learn the digits on the train subset
clf.fit(X_train, y_train)

# Predict the value of the digit on the test subset
predicted_proba = clf.predict_proba(X_test)
predicted = clf.predict(X_test)

n_classes = len(np.unique(digits.target))
labels = ["Class {}".format(i) for i in range(n_classes)]

## Configures matplotlib
plt.rcParams["font.size"] = 20
plt.rcParams["legend.fontsize"] = "xx-small"
scale = 0.75
plt.rcParams["figure.figsize"] = (16 * scale, 9 * scale)

################################################################################
## Main
################################################################################
## ROC Curve
fig_roc, metrics_roc = roc_auc(plt, y_test, predicted_proba, labels)
fig_roc.show()
## Precision-Recall Curve
fig_pre_rec, metrics_pre_rec = pre_rec_auc(plt, y_test, predicted_proba, labels)
fig_pre_rec.show()

#

# EOF
