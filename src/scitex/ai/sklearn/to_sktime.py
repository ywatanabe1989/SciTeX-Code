#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-03-05 13:17:04 (ywatanabe)"

# import warnings

import numpy as np
import pandas as pd
import torch


def to_sktime_df(X):
    """
    Converts a dataset to a format compatible with sktime, encapsulating each sample as a pandas DataFrame.

    Arguments:
    - X (numpy.ndarray or torch.Tensor or pandas.DataFrame): The input dataset with shape (n_samples, n_chs, seq_len).
      It should be a 3D array-like structure containing the time series data.

    Return:
    - sktime_df (pandas.DataFrame): A DataFrame where each element is a pandas Series representing a univariate time series.

    Data Types and Shapes:
    - If X is a numpy.ndarray, it should have the shape (n_samples, n_chs, seq_len).
    - If X is a torch.Tensor, it should have the shape (n_samples, n_chs, seq_len) and will be converted to a numpy array.
    - If X is a pandas.DataFrame, it is assumed to already be in the correct format and will be returned as is.

    References:
    - sktime: https://github.com/alan-turing-institute/sktime

    Examples:
    --------
    >>> X_np = np.random.rand(64, 160, 1024)
    >>> sktime_df = to_sktime_df(X_np)
    >>> type(sktime_df)
    <class 'pandas.core.frame.DataFrame'>
    """
    if isinstance(X, pd.DataFrame):
        return X
    elif torch.is_tensor(X):
        X = X.detach().numpy()
    elif not isinstance(X, np.ndarray):
        raise ValueError(
            "Input X must be a numpy.ndarray, torch.Tensor, or pandas.DataFrame"
        )

    X = X.astype(np.float64)

    def _format_a_sample_for_sktime(x):
        """
        Formats a single sample for sktime compatibility.

        Arguments:
        - x (numpy.ndarray): A 2D array with shape (n_chs, seq_len) representing a single sample.

        Return:
        - dims (pandas.Series): A Series where each element is a pandas Series representing a univariate time series.
        """
        return pd.Series([pd.Series(x[d], name=f"dim_{d}") for d in range(x.shape[0])])

    sktime_df = pd.DataFrame(
        [_format_a_sample_for_sktime(X[i]) for i in range(X.shape[0])]
    )
    return sktime_df


# # Obsolete warning for future compatibility
# def to_sktime(*args, **kwargs):
#     warnings.warn(
#         "to_sktime is deprecated; use to_sktime_df instead.", FutureWarning
#     )
#     return to_sktime_df(*args, **kwargs)


# import pandas as pd
# import numpy as np
# import torch

# def to_sktime(X):
#     """
#     X.shape: (n_samples, n_chs, seq_len)
#     """

#     def _format_a_sample_for_sktime(x):
#         """
#         x.shape: (n_chs, seq_len)
#         """
#         dims = pd.Series(
#             [pd.Series(x[d], name=f"dim_{d}") for d in range(len(x))],
#             index=[f"dim_{i}" for i in np.arange(len(x))],
#         )
#         return dims

#     if torch.is_tensor(X):
#         X = X.numpy()
#         X = X.astype(np.float64)

#     return pd.DataFrame(
#         [_format_a_sample_for_sktime(X[i]) for i in range(len(X))]
#     )
