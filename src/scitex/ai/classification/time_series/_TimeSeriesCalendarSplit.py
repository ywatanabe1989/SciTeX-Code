#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: _TimeSeriesCalendarSplit.py

"""
Calendar-based time series cross-validation splitter.

Splits data based on calendar intervals (e.g., monthly, weekly, daily).
Useful for financial data, sales forecasting, and other time-sensitive applications.
"""

import numpy as np
import pandas as pd
from typing import Iterator, Optional, Tuple, Union, Literal
from sklearn.model_selection import BaseCrossValidator
from sklearn.utils.validation import _num_samples

# Import timestamp normalizer (internally uses to_datetime helper)
from ._normalize_timestamp import normalize_timestamp, to_datetime


class TimeSeriesCalendarSplit(BaseCrossValidator):
    """
    Calendar-based time series cross-validation splitter.
    
    Splits data based on calendar intervals (e.g., months, weeks, days).
    Ensures temporal order is preserved and no data leakage occurs.
    
    Parameters
    ----------
    interval : str
        Time interval for splitting. Options:
        - 'D': Daily
        - 'W': Weekly  
        - 'M': Monthly
        - 'Q': Quarterly
        - 'Y': Yearly
        Or any pandas frequency string
    n_train_intervals : int
        Number of intervals to use for training
    n_test_intervals : int
        Number of intervals to use for testing (default: 1)
    gap_intervals : int
        Number of intervals to skip between train and test (default: 0)
    step_intervals : int
        Number of intervals to step forward for next fold (default: 1)
    
    Examples
    --------
    >>> from scitex.ml.classification import TimeSeriesCalendarSplit
    >>> import pandas as pd
    >>> import numpy as np
    >>> 
    >>> # Create sample data with daily timestamps
    >>> dates = pd.date_range('2023-01-01', '2023-12-31', freq='D')
    >>> X = np.random.randn(len(dates), 10)
    >>> y = np.random.randint(0, 2, len(dates))
    >>> 
    >>> # Monthly splits: 6 months train, 1 month test
    >>> tscal = TimeSeriesCalendarSplit(interval='M', n_train_intervals=6)
    >>> for train_idx, test_idx in tscal.split(X, y, timestamps=dates):
    ...     print(f"Train: {dates[train_idx[0]]:%Y-%m} to {dates[train_idx[-1]]:%Y-%m}")
    ...     print(f"Test:  {dates[test_idx[0]]:%Y-%m} to {dates[test_idx[-1]]:%Y-%m}")
    """
    
    def __init__(
        self,
        interval: str = 'M',
        n_train_intervals: int = 12,
        n_test_intervals: int = 1,
        gap_intervals: int = 0,
        step_intervals: int = 1,
    ):
        self.interval = interval
        self.n_train_intervals = n_train_intervals
        self.n_test_intervals = n_test_intervals
        self.gap_intervals = gap_intervals
        self.step_intervals = step_intervals
    
    def split(
        self,
        X: np.ndarray,
        y: Optional[np.ndarray] = None,
        timestamps: Optional[Union[np.ndarray, pd.DatetimeIndex]] = None,
        groups: Optional[np.ndarray] = None,
    ) -> Iterator[Tuple[np.ndarray, np.ndarray]]:
        """
        Generate calendar-based train/test splits.
        
        Parameters
        ----------
        X : array-like, shape (n_samples, n_features)
            Training data
        y : array-like, shape (n_samples,), optional
            Target variable
        timestamps : array-like or pd.DatetimeIndex, shape (n_samples,)
            Timestamps for each sample (required)
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
            raise ValueError("timestamps must be provided for calendar-based splitting")
        
        n_samples = _num_samples(X)
        indices = np.arange(n_samples)
        
        # Convert timestamps to pandas datetime if needed
        if not isinstance(timestamps, pd.DatetimeIndex):
            # Use normalizer to handle various formats
            # Convert each timestamp to datetime then to pandas DatetimeIndex
            datetime_list = []
            for ts in timestamps:
                dt = to_datetime(ts)
                # Remove timezone info for pandas compatibility
                if dt.tzinfo is not None:
                    dt = dt.replace(tzinfo=None)
                datetime_list.append(dt)
            timestamps = pd.DatetimeIndex(datetime_list)
        
        # Create DataFrame for easier manipulation
        df = pd.DataFrame({
            'index': indices,
            'timestamp': timestamps
        })
        
        # Sort by timestamp
        df = df.sort_values('timestamp')
        
        # Group by the specified interval
        df['interval'] = df['timestamp'].dt.to_period(self.interval)
        unique_intervals = df['interval'].unique()
        
        # Calculate total intervals needed per fold
        intervals_per_fold = (
            self.n_train_intervals + 
            self.gap_intervals + 
            self.n_test_intervals
        )
        
        # Generate splits
        n_intervals = len(unique_intervals)
        start_idx = 0
        
        while start_idx + intervals_per_fold <= n_intervals:
            # Define train intervals
            train_end = start_idx + self.n_train_intervals
            train_intervals = unique_intervals[start_idx:train_end]
            
            # Define test intervals (after gap)
            test_start = train_end + self.gap_intervals
            test_end = test_start + self.n_test_intervals
            
            if test_end > n_intervals:
                break
            
            test_intervals = unique_intervals[test_start:test_end]
            
            # Get indices for train and test
            train_mask = df['interval'].isin(train_intervals)
            test_mask = df['interval'].isin(test_intervals)
            
            train_indices = df.loc[train_mask, 'index'].values
            test_indices = df.loc[test_mask, 'index'].values
            
            yield train_indices, test_indices
            
            # Move to next fold
            start_idx += self.step_intervals
    
    def get_n_splits(self, X=None, y=None, timestamps=None):
        """
        Calculate number of splits.
        
        Parameters
        ----------
        X : array-like, optional
            Not used directly
        y : array-like, optional
            Not used
        timestamps : array-like or pd.DatetimeIndex, optional
            Timestamps to determine number of possible splits
        
        Returns
        -------
        n_splits : int
            Number of splits. Returns -1 if timestamps is None.
        """
        if timestamps is None:
            return -1  # Can't determine without timestamps
        
        # Convert timestamps to pandas datetime if needed
        if not isinstance(timestamps, pd.DatetimeIndex):
            # Use normalizer to handle various formats
            # Convert each timestamp to datetime then to pandas DatetimeIndex
            datetime_list = []
            for ts in timestamps:
                dt = to_datetime(ts)
                # Remove timezone info for pandas compatibility
                if dt.tzinfo is not None:
                    dt = dt.replace(tzinfo=None)
                datetime_list.append(dt)
            timestamps = pd.DatetimeIndex(datetime_list)
        
        # Count unique intervals
        intervals = timestamps.to_period(self.interval).unique()
        n_intervals = len(intervals)
        
        # Calculate how many complete folds we can create
        intervals_per_fold = (
            self.n_train_intervals + 
            self.gap_intervals + 
            self.n_test_intervals
        )
        
        if n_intervals < intervals_per_fold:
            return 0
        
        # Calculate number of possible splits with stepping
        n_splits = (n_intervals - intervals_per_fold) // self.step_intervals + 1
        return max(0, n_splits)