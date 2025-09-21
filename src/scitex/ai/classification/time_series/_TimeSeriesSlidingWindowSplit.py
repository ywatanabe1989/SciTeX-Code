#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-21 20:40:00 (ywatanabe)"
# File: _TimeSeriesSlidingWindowSplit.py

"""
Sliding window cross-validation for time series.

Creates overlapping train/test windows that slide through time.
"""

import numpy as np
from typing import Iterator, Optional, Tuple
from sklearn.model_selection import BaseCrossValidator
from sklearn.utils.validation import _num_samples


class TimeSeriesSlidingWindowSplit(BaseCrossValidator):
    """
    Sliding window cross-validation for time series.
    
    Creates overlapping train/test windows that slide through time.
    
    Parameters
    ----------
    window_size : int
        Size of training window
    step_size : int
        Step between windows
    test_size : int
        Size of test window
    
    Examples
    --------
    >>> from scitex.ml.classification import TimeSeriesSlidingWindowSplit
    >>> import numpy as np
    >>> 
    >>> X = np.random.randn(100, 10)
    >>> y = np.random.randint(0, 2, 100)
    >>> timestamps = np.arange(100)
    >>> 
    >>> swcv = TimeSeriesSlidingWindowSplit(window_size=50, step_size=10, test_size=10)
    >>> for train_idx, test_idx in swcv.split(X, y, timestamps):
    ...     print(f"Train: {len(train_idx)}, Test: {len(test_idx)}")
    """
    
    def __init__(self, window_size: int, step_size: int, test_size: int):
        self.window_size = window_size
        self.step_size = step_size
        self.test_size = test_size
    
    def split(
        self,
        X: np.ndarray,
        y: Optional[np.ndarray] = None,
        timestamps: Optional[np.ndarray] = None,
        groups: Optional[np.ndarray] = None,
    ) -> Iterator[Tuple[np.ndarray, np.ndarray]]:
        """
        Generate sliding window splits.
        
        Parameters
        ----------
        X : array-like, shape (n_samples, n_features)
            Training data
        y : array-like, shape (n_samples,), optional
            Target variable
        timestamps : array-like, shape (n_samples,), optional
            Timestamps for temporal ordering. If None, uses sequential order
        groups : array-like, shape (n_samples,), optional
            Group labels (not used in this splitter)
        
        Yields
        ------
        train : ndarray
            Training set indices
        test : ndarray
            Test set indices
        """
        if timestamps is None:
            timestamps = np.arange(len(X))
        
        n_samples = _num_samples(X)
        indices = np.arange(n_samples)
        
        # Sort by timestamp
        time_order = np.argsort(timestamps)
        sorted_indices = indices[time_order]
        
        # Generate windows
        for start in range(0, n_samples - self.window_size - self.test_size, self.step_size):
            train_end = start + self.window_size
            test_end = train_end + self.test_size
            
            if test_end > n_samples:
                break
            
            train_indices = sorted_indices[start:train_end]
            test_indices = sorted_indices[train_end:test_end]
            
            yield train_indices, test_indices
    
    def get_n_splits(self, X=None, y=None, groups=None):
        """
        Calculate number of splits.
        
        Parameters
        ----------
        X : array-like, shape (n_samples, n_features), optional
            Training data (required to determine number of splits)
        y : array-like, optional
            Not used
        groups : array-like, optional
            Not used
        
        Returns
        -------
        n_splits : int
            Number of splits. Returns -1 if X is None.
        """
        if X is None:
            return -1  # Can't determine without data
        
        n_samples = _num_samples(X)
        n_windows = (n_samples - self.window_size - self.test_size) // self.step_size + 1
        return max(1, n_windows)