#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-24 10:13:17 (ywatanabe)"
# File: ./scitex_repo/src/scitex/ai/sampling/undersample.py

THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/ai/sampling/undersample.py"

from typing import Tuple
from ...types import ArrayLike
from imblearn.under_sampling import RandomUnderSampler


def undersample(
    X: ArrayLike, y: ArrayLike, random_state: int = 42
) -> Tuple[ArrayLike, ArrayLike]:
    """Undersample data preserving input type.

    Args:
        X: Features array-like of shape (n_samples, n_features)
        y: Labels array-like of shape (n_samples,)
    Returns:
        Resampled X, y of same type as input
    """
    rus = RandomUnderSampler(random_state=random_state)
    X_resampled, y_resampled = rus.fit_resample(X, y)
    return X_resampled, y_resampled


# EOF
