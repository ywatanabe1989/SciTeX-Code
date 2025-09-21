#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-21 20:35:00 (ywatanabe)"
# File: _TimeSeriesBlockingSplit.py

"""
Time series split with blocking to handle multiple time series.

Useful when you have multiple patients/subjects with their own
time series that shouldn't be mixed.
"""

import numpy as np
from typing import Iterator, Optional, Tuple
from sklearn.model_selection import BaseCrossValidator


class TimeSeriesBlockingSplit(BaseCrossValidator):
    """
    Time series split with blocking to handle multiple time series.
    
    Useful when you have multiple patients/subjects with their own
    time series that shouldn't be mixed.
    
    Parameters
    ----------
    n_splits : int
        Number of splits
    test_ratio : float
        Proportion for test set
    
    Examples
    --------
    >>> from scitex.ml.classification import TimeSeriesBlockingSplit
    >>> import numpy as np
    >>> 
    >>> X = np.random.randn(100, 10)
    >>> y = np.random.randint(0, 2, 100)
    >>> timestamps = np.arange(100)
    >>> groups = np.repeat([0, 1, 2, 3], 25)  # 4 groups, 25 samples each
    >>> 
    >>> btscv = TimeSeriesBlockingSplit(n_splits=3)
    >>> for train_idx, test_idx in btscv.split(X, y, timestamps, groups):
    ...     print(f"Train: {len(train_idx)}, Test: {len(test_idx)}")
    """
    
    def __init__(self, n_splits: int = 5, test_ratio: float = 0.2):
        self.n_splits = n_splits
        self.test_ratio = test_ratio
    
    def split(
        self,
        X: np.ndarray,
        y: Optional[np.ndarray] = None,
        timestamps: Optional[np.ndarray] = None,
        groups: Optional[np.ndarray] = None,
    ) -> Iterator[Tuple[np.ndarray, np.ndarray]]:
        """
        Generate indices respecting group boundaries.
        
        Parameters
        ----------
        X : array-like, shape (n_samples, n_features)
            Training data
        y : array-like, shape (n_samples,)
            Target variable
        timestamps : array-like, shape (n_samples,)
            Timestamps for temporal ordering (required)
        groups : array-like, shape (n_samples,)
            Group labels (e.g., patient IDs) - required
        
        Yields
        ------
        train : ndarray
            Training set indices
        test : ndarray
            Test set indices
        """
        if groups is None:
            raise ValueError("groups must be provided for blocking time series split")
        
        if timestamps is None:
            raise ValueError("timestamps must be provided")
        
        unique_groups = np.unique(groups)
        
        for i in range(self.n_splits):
            train_indices = []
            test_indices = []
            
            for group in unique_groups:
                group_mask = groups == group
                group_indices = np.where(group_mask)[0]
                group_times = timestamps[group_mask]
                
                # Sort group by time
                time_order = np.argsort(group_times)
                sorted_group_indices = group_indices[time_order]
                
                # Split this group
                n_group = len(sorted_group_indices)
                test_size = int(n_group * self.test_ratio)
                train_size = n_group - test_size
                
                # Expanding window for this group
                split_point = train_size - (self.n_splits - i - 1) * (test_size // self.n_splits)
                split_point = max(1, min(split_point, train_size))
                
                train_indices.extend(sorted_group_indices[:split_point])
                test_indices.extend(sorted_group_indices[split_point:split_point + test_size])
            
            yield np.array(train_indices), np.array(test_indices)
    
    def get_n_splits(self, X=None, y=None, groups=None):
        """Returns the number of splitting iterations."""
        return self.n_splits