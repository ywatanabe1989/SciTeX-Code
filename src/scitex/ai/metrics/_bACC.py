#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-02-26 16:32:42 (ywatanabe)"

import warnings

import numpy as np
import torch
from sklearn.metrics import balanced_accuracy_score


def bACC(true_class, pred_class):
    """
    Calculates the balanced accuracy score between predicted and true class labels.

    Parameters:
    - true_class (array-like or torch.Tensor): True class labels.
    - pred_class (array-like or torch.Tensor): Predicted class labels.

    Returns:
    - bACC (float): The balanced accuracy score rounded to three decimal places.
    """
    if isinstance(true_class, torch.Tensor):  # [REVISED]
        true_class = true_class.detach().cpu().numpy()  # [REVISED]
    if isinstance(pred_class, torch.Tensor):  # [REVISED]
        pred_class = pred_class.detach().cpu().numpy()  # [REVISED]

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        bACC_score = balanced_accuracy_score(
            true_class.reshape(-1),  # [REVISED]
            pred_class.reshape(-1),  # [REVISED]
        )
    return round(bACC_score, 3)  # [REVISED]


# Snake_case alias for consistency
def balanced_accuracy(true_class, pred_class):
    """
    Calculates the balanced accuracy score between predicted and true class labels.
    
    This is an alias for bACC() with snake_case naming.
    
    Parameters:
    - true_class (array-like or torch.Tensor): True class labels.
    - pred_class (array-like or torch.Tensor): Predicted class labels.
    
    Returns:
    - float: The balanced accuracy score rounded to three decimal places.
    """
    return bACC(true_class, pred_class)
