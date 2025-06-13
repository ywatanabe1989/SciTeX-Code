#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-03-02 09:52:28 (ywatanabe)"

from warnings import warn

import numpy as np
import pandas as pd
import torch
from sklearn.preprocessing import LabelEncoder as SklearnLabelEncoder


class LabelEncoder(SklearnLabelEncoder):
    """
    An extension of the sklearn.preprocessing.LabelEncoder that supports incremental learning.
    This means it can handle new classes without forgetting the old ones.

    Attributes:
        classes_ (np.ndarray): Holds the label for each class.

    Example usage:
        encoder = IncrementalLabelEncoder()
        encoder.fit(np.array(["apple", "banana"]))
        encoded_labels = encoder.transform(["apple", "banana"])  # This will give you the encoded labels

        encoder.fit(["cherry"])  # Incrementally add "cherry"
        encoder.transform(["apple", "banana", "cherry"])  # Now it works, including "cherry"

        # Now you can use inverse_transform with the encoded labels
        print(encoder.classes_)
        original_labels = encoder.inverse_transform(encoded_labels)
        print(original_labels)  # This should print ['apple', 'banana']
    """

    def __init__(self):
        super().__init__()
        self.classes_ = np.array([])

    def _check_input(self, y):
        """
        Check and convert the input to a NumPy array if it is a list, tuple, pandas.Series, pandas.DataFrame, or torch.Tensor.

        Arguments:
            y (list, tuple, pd.Series, pd.DataFrame, torch.Tensor): The input labels.

        Returns:
            np.ndarray: The input labels converted to a NumPy array.
        """
        if isinstance(y, (list, tuple)):
            y = np.array(y)
        elif isinstance(y, pd.Series):
            y = y.values
        elif isinstance(y, torch.Tensor):
            y = y.numpy()
        return y

    def fit(self, y):
        """
        Fit the label encoder with an array of labels, incrementally adding new classes.

        Arguments:
            y (list, tuple, np.ndarray, pd.Series, pd.DataFrame, torch.Tensor): The input labels.

        Returns:
            IncrementalLabelEncoder: The instance itself.
        """
        y = self._check_input(y)
        new_unique_labels = np.unique(y)
        unique_labels = np.unique(np.concatenate((self.classes_, new_unique_labels)))
        self.classes_ = unique_labels
        return self

    def transform(self, y):
        """
        Transform labels to normalized encoding.

        Arguments:
            y (list, tuple, np.ndarray, pd.Series, pd.DataFrame, torch.Tensor): The input labels.

        Returns:
            np.ndarray: The encoded labels as a NumPy array.

        Raises:
            ValueError: If the input contains new labels that haven't been seen during `fit`.
        """

        y = self._check_input(y)
        diff = set(y) - set(self.classes_)
        if diff:
            raise ValueError(f"y contains new labels: {diff}")
        return super().transform(y)

    def inverse_transform(self, y):
        """
        Transform labels back to original encoding.

        Arguments:
            y (np.ndarray): The encoded labels as a NumPy array.

        Returns:
            np.ndarray: The original labels as a NumPy array.
        """

        return super().inverse_transform(y)


# # Obsolete warning for future compatibility
# class LabelEncoder(IncrementalLabelEncoder):
#     def __init__(self, *args, **kwargs):
#         """
#         Initialize the LabelEncoder with a deprecation warning.
#         """
#         warn(
#             "LabelEncoder is now obsolete; use IncrementalLabelEncoder instead.",
#             category=FutureWarning,
#         )
#         super().__init__(*args, **kwargs)


if __name__ == "__main__":
    # Example usage of IncrementalLabelEncoder
    le = LabelEncoder()
    le.fit(["A", "B"])
    print(le.classes_)

    le.fit(["C"])
    print(le.classes_)

    le.inverse_transform([0, 1, 2])

    le.fit(["X"])
    print(le.classes_)

    le.inverse_transform([3])
