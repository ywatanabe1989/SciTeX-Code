#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-21 20:30:00 (ywatanabe)"
# File: _TimeSeriesStratifiedSplit.py

"""
Time series cross-validation with stratification support.

This splitter ensures:
1. Test data is always chronologically after training data
2. Optional validation set between train and test
3. Class balance preservation in splits
4. Gap period between train and test to avoid leakage
"""

import numpy as np
from typing import Iterator, Optional, Tuple
from sklearn.model_selection import BaseCrossValidator
from sklearn.utils.validation import _num_samples


class TimeSeriesStratifiedSplit(BaseCrossValidator):
    """
    Time series cross-validation with stratification support.
    
    This splitter ensures:
    1. Test data is always chronologically after training data
    2. Optional validation set between train and test
    3. Class balance preservation in splits
    4. Gap period between train and test to avoid leakage
    
    Parameters
    ----------
    n_splits : int
        Number of splits (folds)
    test_ratio : float
        Proportion of data for test set (default: 0.2)
    val_ratio : float
        Proportion of data for validation set (default: 0.1)
    gap : int
        Number of samples to exclude between train and test (default: 0)
    stratify : bool
        Whether to maintain class proportions (default: True)
    
    Examples
    --------
    >>> from scitex.ml.classification import TimeSeriesStratifiedSplit
    >>> import numpy as np
    >>> 
    >>> X = np.random.randn(100, 10)
    >>> y = np.random.randint(0, 2, 100)
    >>> timestamps = np.arange(100)
    >>> 
    >>> tscv = TimeSeriesStratifiedSplit(n_splits=3)
    >>> for train_idx, test_idx in tscv.split(X, y, timestamps):
    ...     print(f"Train: {len(train_idx)}, Test: {len(test_idx)}")
    """
    
    def __init__(
        self,
        n_splits: int = 5,
        test_ratio: float = 0.2,
        val_ratio: float = 0.1,
        gap: int = 0,
        stratify: bool = True,
    ):
        self.n_splits = n_splits
        self.test_ratio = test_ratio
        self.val_ratio = val_ratio
        self.gap = gap
        self.stratify = stratify
    
    def split(
        self,
        X: np.ndarray,
        y: Optional[np.ndarray] = None,
        timestamps: Optional[np.ndarray] = None,
        groups: Optional[np.ndarray] = None,
    ) -> Iterator[Tuple[np.ndarray, np.ndarray]]:
        """
        Generate indices to split data into training and test sets.
        
        Parameters
        ----------
        X : array-like, shape (n_samples, n_features)
            Training data
        y : array-like, shape (n_samples,)
            Target variable
        timestamps : array-like, shape (n_samples,)
            Timestamps for temporal ordering (required)
        groups : array-like, shape (n_samples,), optional
            Group labels for grouped CV
        
        Yields
        ------
        train : ndarray
            Training set indices
        test : ndarray
            Test set indices
        """
        if timestamps is None:
            raise ValueError("timestamps must be provided for time series split")
        
        n_samples = _num_samples(X)
        indices = np.arange(n_samples)
        
        # Sort by timestamp
        time_order = np.argsort(timestamps)
        sorted_indices = indices[time_order]
        sorted_y = y[time_order] if y is not None else None
        
        # Calculate split sizes
        test_size = int(n_samples * self.test_ratio)
        val_size = int(n_samples * self.val_ratio) if self.val_ratio > 0 else 0
        
        # Generate splits with expanding training window
        for i in range(self.n_splits):
            # Expanding window approach
            train_end = n_samples - test_size - val_size - self.gap
            train_end = train_end - (self.n_splits - i - 1) * (test_size // self.n_splits)
            train_end = max(test_size, train_end)  # Ensure min training size
            
            # Apply gap
            test_start = train_end + self.gap + val_size
            test_end = min(test_start + test_size, n_samples)
            
            # Get indices
            train_indices = sorted_indices[:train_end]
            test_indices = sorted_indices[test_start:test_end]
            
            # Apply stratification if requested
            if self.stratify and y is not None and sorted_y is not None:
                train_indices = self._stratify_indices(
                    train_indices, sorted_y, len(train_indices)
                )
                test_indices = self._stratify_indices(
                    test_indices, sorted_y, len(test_indices)
                )
            
            yield train_indices, test_indices
    
    def split_with_val(
        self,
        X: np.ndarray,
        y: Optional[np.ndarray] = None,
        timestamps: Optional[np.ndarray] = None,
        groups: Optional[np.ndarray] = None,
    ) -> Iterator[Tuple[np.ndarray, np.ndarray, np.ndarray]]:
        """
        Generate indices with separate validation set.
        
        Yields
        ------
        train : ndarray
            Training set indices
        val : ndarray
            Validation set indices
        test : ndarray
            Test set indices
        """
        if timestamps is None:
            raise ValueError("timestamps must be provided for time series split")
        
        n_samples = _num_samples(X)
        indices = np.arange(n_samples)
        
        # Sort by timestamp
        time_order = np.argsort(timestamps)
        sorted_indices = indices[time_order]
        sorted_y = y[time_order] if y is not None else None
        
        # Calculate split sizes
        test_size = int(n_samples * self.test_ratio)
        val_size = int(n_samples * self.val_ratio) if self.val_ratio > 0 else 0
        
        # Generate splits
        for i in range(self.n_splits):
            # Expanding window
            train_end = n_samples - test_size - val_size - self.gap * 2
            train_end = train_end - (self.n_splits - i - 1) * (test_size // self.n_splits)
            train_end = max(test_size, train_end)
            
            # Validation set
            val_start = train_end + self.gap
            val_end = val_start + val_size
            
            # Test set
            test_start = val_end + self.gap
            test_end = min(test_start + test_size, n_samples)
            
            # Get indices
            train_indices = sorted_indices[:train_end]
            val_indices = sorted_indices[val_start:val_end]
            test_indices = sorted_indices[test_start:test_end]
            
            # Apply stratification
            if self.stratify and y is not None and sorted_y is not None:
                train_indices = self._stratify_indices(
                    train_indices, sorted_y, len(train_indices)
                )
                val_indices = self._stratify_indices(
                    val_indices, sorted_y, len(val_indices)
                )
                test_indices = self._stratify_indices(
                    test_indices, sorted_y, len(test_indices)
                )
            
            yield train_indices, val_indices, test_indices
    
    def _stratify_indices(
        self, indices: np.ndarray, y: np.ndarray, target_size: int
    ) -> np.ndarray:
        """Apply stratification to maintain class balance."""
        classes = np.unique(y[indices])
        
        # Calculate class proportions
        class_counts = [np.sum(y[indices] == cls) for cls in classes]
        total_count = sum(class_counts)
        class_ratios = [count / total_count for count in class_counts]
        
        # Sample from each class
        stratified = []
        for cls, ratio in zip(classes, class_ratios):
            cls_indices = indices[y[indices] == cls]
            n_samples = int(target_size * ratio)
            stratified.extend(cls_indices[:n_samples])
        
        return np.array(stratified)
    
    def get_n_splits(self, X=None, y=None, groups=None):
        """Returns the number of splitting iterations in the CV."""
        return self.n_splits