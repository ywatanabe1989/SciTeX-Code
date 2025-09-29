#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-22 17:15:00 (ywatanabe)"
# File: _TimeSeriesCalendarSplit.py

__FILE__ = "_TimeSeriesCalendarSplit.py"

"""
Functionalities:
  - Implements calendar-based time series cross-validation
  - Splits data based on calendar intervals (monthly, weekly, daily)
  - Ensures temporal order preservation with no data leakage
  - Supports flexible interval definitions (D, W, M, Q, Y)
  - Provides visualization with scatter plots showing actual data points
  - Useful for financial data, sales forecasting, seasonal patterns

Dependencies:
  - packages:
    - numpy
    - pandas
    - sklearn
    - matplotlib
    - scitex

IO:
  - input-files:
    - None (generates synthetic calendar-based data for demonstration)
  - output-files:
    - ./calendar_splits_demo.png (visualization with scatter plots)
"""

"""Imports"""
import os
import sys
import argparse
import numpy as np
import pandas as pd
from typing import Iterator, Optional, Tuple, Union, Literal
from sklearn.model_selection import BaseCrossValidator
from sklearn.utils.validation import _num_samples
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import scitex as stx
from scitex import logging

# Import timestamp normalizer (internally uses to_datetime helper)
from ._normalize_timestamp import normalize_timestamp, to_datetime

logger = logging.getLogger(__name__)


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
        n_val_intervals: int = 0,
        gap_intervals: int = 0,
        step_intervals: int = 1,
    ):
        self.interval = interval
        self.n_train_intervals = n_train_intervals
        self.n_test_intervals = n_test_intervals
        self.n_val_intervals = n_val_intervals
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
    
    def split_with_val(
        self,
        X: np.ndarray,
        y: Optional[np.ndarray] = None,
        timestamps: Optional[Union[np.ndarray, pd.DatetimeIndex]] = None,
        groups: Optional[np.ndarray] = None,
    ) -> Iterator[Tuple[np.ndarray, np.ndarray, np.ndarray]]:
        """
        Generate calendar-based train/validation/test splits.
        
        The validation set comes after training but before test, maintaining
        temporal order: train < val < test.
        
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
        val : ndarray
            Validation set indices
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
        
        # Calculate total intervals needed per fold including validation
        intervals_per_fold = (
            self.n_train_intervals + 
            self.n_val_intervals +
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
            
            # Define validation intervals (after train)
            val_start = train_end
            val_end = val_start + self.n_val_intervals
            val_intervals = unique_intervals[val_start:val_end] if self.n_val_intervals > 0 else []
            
            # Define test intervals (after validation and gap)
            test_start = val_end + self.gap_intervals if self.n_val_intervals > 0 else train_end + self.gap_intervals
            test_end = test_start + self.n_test_intervals
            
            if test_end > n_intervals:
                break
            
            test_intervals = unique_intervals[test_start:test_end]
            
            # Get indices for train, validation, and test
            train_mask = df['interval'].isin(train_intervals)
            val_mask = df['interval'].isin(val_intervals) if len(val_intervals) > 0 else pd.Series([False] * len(df))
            test_mask = df['interval'].isin(test_intervals)
            
            train_indices = df.loc[train_mask, 'index'].values
            val_indices = df.loc[val_mask, 'index'].values if self.n_val_intervals > 0 else np.array([])
            test_indices = df.loc[test_mask, 'index'].values
            
            yield train_indices, val_indices, test_indices
            
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
    
    def plot_splits(self, X, y=None, timestamps=None, figsize=(12, 6), save_path=None):
        """
        Visualize the train/test splits as timeline rectangles with scatter plots.
        
        Parameters
        ----------
        X : array-like
            Training data (used to determine data size)
        y : array-like, optional
            Target variable (used for color-coding scatter points)
        timestamps : array-like or pd.DatetimeIndex
            Timestamps for each sample
        figsize : tuple, default (12, 6)
            Figure size (width, height)
        save_path : str, optional
            Path to save the plot
            
        Returns
        -------
        fig : matplotlib.figure.Figure
            The created figure
            
        Examples
        --------
        >>> splitter = TimeSeriesCalendarSplit(interval='M', n_train_intervals=6)
        >>> fig = splitter.plot_splits(X, timestamps=dates)
        >>> fig.savefig('calendar_splits.png')
        """
        # matplotlib is always available in SciTeX
        
        if timestamps is None:
            raise ValueError("timestamps must be provided for calendar split visualization")
        
        # Get all splits
        splits = list(self.split(X, y, timestamps))
        if not splits:
            raise ValueError("No splits generated. Check data size and splitter parameters.")
        
        # Convert timestamps for plotting
        if not isinstance(timestamps, pd.DatetimeIndex):
            datetime_list = []
            for ts in timestamps:
                dt = to_datetime(ts)
                if dt.tzinfo is not None:
                    dt = dt.replace(tzinfo=None)
                datetime_list.append(dt)
            timestamps = pd.DatetimeIndex(datetime_list)
        
        # Create figure
        fig, ax = plt.subplots(figsize=figsize)
        
        # Jitter strength for scatter plots
        jitter_strength = 0.15
        
        # Plot each fold
        for fold, (train_idx, test_idx) in enumerate(splits):
            y_pos = fold
            
            # Train period rectangle
            train_start = timestamps[train_idx[0]]
            train_end = timestamps[train_idx[-1]]
            train_width = (train_end - train_start).total_seconds() / 86400  # Convert to days
            
            train_rect = patches.Rectangle(
                (train_start, y_pos - 0.3), 
                pd.Timedelta(days=train_width), 0.6,
                linewidth=1, edgecolor='blue', facecolor='lightblue', alpha=0.3,
                label='Train Set (range)' if fold == 0 else ""
            )
            ax.add_patch(train_rect)
            
            # Add scatter plot for training data points
            train_times = timestamps[train_idx]
            train_jitter = np.random.normal(0, jitter_strength, len(train_idx))
            
            # Color by class if y is provided
            if y is not None:
                train_colors = ['darkblue' if yi == 0 else 'navy' for yi in y[train_idx]]
            else:
                train_colors = 'darkblue'
            
            ax.scatter(train_times, y_pos + train_jitter,
                      c=train_colors, s=20, alpha=0.6, marker='o',
                      label='Train data points' if fold == 0 else "", zorder=10)
            
            # Test period rectangle
            test_start = timestamps[test_idx[0]]
            test_end = timestamps[test_idx[-1]]
            test_width = (test_end - test_start).total_seconds() / 86400
            
            test_rect = patches.Rectangle(
                (test_start, y_pos - 0.3),
                pd.Timedelta(days=test_width), 0.6,
                linewidth=1, edgecolor='red', facecolor='lightcoral', alpha=0.3,
                label='Test Set (range)' if fold == 0 else ""
            )
            ax.add_patch(test_rect)
            
            # Add scatter plot for test data points
            test_times = timestamps[test_idx]
            test_jitter = np.random.normal(0, jitter_strength, len(test_idx))
            
            # Color by class if y is provided
            if y is not None:
                test_colors = ['darkred' if yi == 0 else 'firebrick' for yi in y[test_idx]]
            else:
                test_colors = 'darkred'
                
            ax.scatter(test_times, y_pos + test_jitter,
                      c=test_colors, s=20, alpha=0.6, marker='^',
                      label='Test data points' if fold == 0 else "", zorder=10)
        
        # Format plot
        ax.set_ylim(-0.5, len(splits) - 0.5)
        ax.set_xlim(timestamps.min(), timestamps.max())
        ax.set_xlabel('Time')
        ax.set_ylabel('Fold')
        ax.set_title(f'Time Series Calendar Split Visualization\\n'
                    f'Interval: {self.interval}, Train: {self.n_train_intervals}, '
                    f'Test: {self.n_test_intervals}')
        
        # Set y-ticks
        ax.set_yticks(range(len(splits)))
        ax.set_yticklabels([f'Fold {i}' for i in range(len(splits))])
        
        # Add legend
        ax.legend(loc='upper right')
        
        # Format x-axis
        ax.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        if save_path:
            fig.savefig(save_path, dpi=150, bbox_inches='tight')
        
        return fig


"""Functions & Classes"""
def main(args) -> int:
    """Demonstrate TimeSeriesCalendarSplit functionality.
    
    Args:
        args: Command line arguments
        
    Returns:
        int: Exit status
    """
    logger.info("Demonstrating TimeSeriesCalendarSplit functionality")
    
    # Generate test data with calendar-based timestamps
    np.random.seed(42)
    n_samples = args.n_samples
    
    # Create daily timestamps over several months
    start_date = pd.Timestamp(args.start_date)
    timestamps = pd.date_range(start=start_date, periods=n_samples, freq=args.data_freq)
    
    # Generate features and target
    X = np.random.randn(n_samples, 5)
    y = np.random.randint(0, 2, n_samples)
    
    logger.info(f"Generated test data: {n_samples} samples")
    logger.info(f"Date range: {timestamps[0].strftime('%Y-%m-%d')} to {timestamps[-1].strftime('%Y-%m-%d')}")
    logger.info(f"Data frequency: {args.data_freq}")
    
    # Create calendar splitter
    splitter = TimeSeriesCalendarSplit(
        interval=args.interval,
        n_train_intervals=args.n_train_intervals,
        n_test_intervals=args.n_test_intervals,
        gap_intervals=args.gap_intervals,
        step_intervals=args.step_intervals
    )
    
    logger.info(f"Calendar split configuration:")
    logger.info(f"  Interval: {args.interval}")
    logger.info(f"  Train intervals: {args.n_train_intervals}")
    logger.info(f"  Test intervals: {args.n_test_intervals}")
    logger.info(f"  Gap intervals: {args.gap_intervals}")
    logger.info(f"  Step intervals: {args.step_intervals}")
    
    # Test splits
    splits = []
    for fold, (train_idx, test_idx) in enumerate(splitter.split(X, y, timestamps=timestamps)):
        if fold >= args.max_folds:
            break
        splits.append((train_idx, test_idx))
        
        train_start = timestamps[train_idx[0]].strftime('%Y-%m-%d')
        train_end = timestamps[train_idx[-1]].strftime('%Y-%m-%d')
        test_start = timestamps[test_idx[0]].strftime('%Y-%m-%d')
        test_end = timestamps[test_idx[-1]].strftime('%Y-%m-%d')
        
        logger.info(f"Fold {fold}:")
        logger.info(f"  Train: {train_start} to {train_end} ({len(train_idx)} samples)")
        logger.info(f"  Test: {test_start} to {test_end} ({len(test_idx)} samples)")
        
        # Verify temporal order
        train_times = timestamps[train_idx]
        test_times = timestamps[test_idx]
        temporal_ok = train_times.max() < test_times.min()
        status = "✓" if temporal_ok else "✗"
        logger.info(f"  Temporal order: {status}")
    
    # Generate visualization
    logger.info("Generating calendar split visualization")
    fig = splitter.plot_splits(X, y, timestamps)
    
    # Save using SciTeX framework
    stx.io.save(fig, "./calendar_splits_demo.png", symlink_from_cwd=True)
    plt.close(fig)
    
    logger.info("TimeSeriesCalendarSplit demonstration completed successfully")
    return 0


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Demonstrate TimeSeriesCalendarSplit with calendar-based intervals'
    )
    parser.add_argument(
        "--n-samples",
        type=int,
        default=365,
        help="Number of samples to generate (default: %(default)s)",
    )
    parser.add_argument(
        "--start-date",
        type=str,
        default="2023-01-01",
        help="Start date for time series (default: %(default)s)",
    )
    parser.add_argument(
        "--data-freq",
        type=str,
        default="D",
        help="Frequency of data points (D=daily, H=hourly) (default: %(default)s)",
    )
    parser.add_argument(
        "--interval",
        type=str,
        default="M",
        help="Calendar interval (D=daily, W=weekly, M=monthly) (default: %(default)s)",
    )
    parser.add_argument(
        "--n-train-intervals",
        type=int,
        default=6,
        help="Number of intervals for training (default: %(default)s)",
    )
    parser.add_argument(
        "--n-test-intervals",
        type=int,
        default=1,
        help="Number of intervals for testing (default: %(default)s)",
    )
    parser.add_argument(
        "--gap-intervals",
        type=int,
        default=0,
        help="Gap intervals between train and test (default: %(default)s)",
    )
    parser.add_argument(
        "--step-intervals",
        type=int,
        default=1,
        help="Step intervals between folds (default: %(default)s)",
    )
    parser.add_argument(
        "--max-folds",
        type=int,
        default=3,
        help="Maximum number of folds to demonstrate (default: %(default)s)",
    )
    args = parser.parse_args()
    return args


def run_main() -> None:
    """Initialize scitex framework, run main function, and cleanup."""
    global CONFIG, CC, sys, plt, rng

    import sys
    import matplotlib.pyplot as plt
    import scitex as stx

    args = parse_args()

    CONFIG, sys.stdout, sys.stderr, plt, CC, rng = stx.session.start(
        sys,
        plt,
        args=args,
        file=__FILE__,
        sdir_suffix=None,
        verbose=False,
        agg=True,
    )

    exit_status = main(args)

    stx.session.close(
        CONFIG,
        verbose=False,
        notify=False,
        message="",
        exit_status=exit_status,
    )


if __name__ == '__main__':
    run_main()

# EOF