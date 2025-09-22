#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-22 17:10:00 (ywatanabe)"
# File: _TimeSeriesSlidingWindowSplit.py

__FILE__ = "_TimeSeriesSlidingWindowSplit.py"

"""
Functionalities:
  - Implements sliding window cross-validation for time series
  - Creates overlapping train/test windows that slide through time
  - Supports temporal gaps between train and test sets
  - Provides visualization with scatter plots showing actual data points
  - Validates temporal order in all windows
  - Ensures no data leakage between train and test sets

Dependencies:
  - packages:
    - numpy
    - sklearn
    - matplotlib
    - scitex

IO:
  - input-files:
    - None (generates synthetic data for demonstration)
  - output-files:
    - ./sliding_window_demo.png (visualization with scatter plots)
"""

"""Imports"""
import os
import sys
import argparse
import numpy as np
from typing import Iterator, Optional, Tuple
from sklearn.model_selection import BaseCrossValidator
from sklearn.utils.validation import _num_samples
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import scitex as stx
from scitex import logging

logger = logging.getLogger(__name__)


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
    gap : int, default=0
        Number of samples to skip between train and test windows
    
    Examples
    --------
    >>> from scitex.ml.classification import TimeSeriesSlidingWindowSplit
    >>> import numpy as np
    >>> 
    >>> X = np.random.randn(100, 10)
    >>> y = np.random.randint(0, 2, 100)
    >>> timestamps = np.arange(100)
    >>> 
    >>> swcv = TimeSeriesSlidingWindowSplit(window_size=50, step_size=10, test_size=10, gap=5)
    >>> for train_idx, test_idx in swcv.split(X, y, timestamps):
    ...     print(f"Train: {len(train_idx)}, Test: {len(test_idx)}")
    ...     # Each window: [train_window] -> [gap] -> [test_window] -> step forward
    """
    
    def __init__(self, window_size: int, step_size: int, test_size: int, gap: int = 0, val_ratio: float = 0.0):
        self.window_size = window_size
        self.step_size = step_size
        self.test_size = test_size
        self.gap = gap
        self.val_ratio = val_ratio
    
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
        
        # Sort by timestamp to get temporal order
        time_order = np.argsort(timestamps)
        sorted_indices = indices[time_order]
        
        # Generate sliding windows in temporal order (after sorting)
        total_window = self.window_size + self.gap + self.test_size
        
        for start in range(0, n_samples - total_window + 1, self.step_size):
            # These positions are in the sorted (temporal) domain
            train_end = start + self.window_size
            test_start = train_end + self.gap
            test_end = test_start + self.test_size
            
            if test_end > n_samples:
                break
            
            # Extract indices from the temporally sorted sequence
            # These will be the original sample indices, but in temporal order
            train_indices = sorted_indices[start:train_end]
            test_indices = sorted_indices[test_start:test_end]
            
            # Ensure temporal order is preserved: all test indices should correspond to 
            # later time points than train indices
            assert len(train_indices) > 0 and len(test_indices) > 0, "Empty window"
            
            yield train_indices, test_indices
    
    def split_with_val(
        self,
        X: np.ndarray,
        y: Optional[np.ndarray] = None,
        timestamps: Optional[np.ndarray] = None,
        groups: Optional[np.ndarray] = None,
    ) -> Iterator[Tuple[np.ndarray, np.ndarray, np.ndarray]]:
        """
        Generate sliding window splits with validation set.
        
        The validation set comes after training but before test, maintaining
        temporal order: train < val < test.
        
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
        val : ndarray
            Validation set indices
        test : ndarray
            Test set indices
        """
        if timestamps is None:
            timestamps = np.arange(len(X))
        
        n_samples = _num_samples(X)
        indices = np.arange(n_samples)
        
        # Sort by timestamp to get temporal order
        time_order = np.argsort(timestamps)
        sorted_indices = indices[time_order]
        
        # Calculate validation size from training window
        val_size = int(self.window_size * self.val_ratio) if self.val_ratio > 0 else 0
        actual_train_size = self.window_size - val_size
        
        # Generate sliding windows in temporal order (after sorting)
        # Total window now includes train, val (with gap), and test (with gap)
        total_window = self.window_size + self.gap + self.test_size
        
        for start in range(0, n_samples - total_window + 1, self.step_size):
            # These positions are in the sorted (temporal) domain
            train_end = start + actual_train_size
            
            # Validation comes after train with optional gap
            val_start = train_end + (self.gap if val_size > 0 else 0)
            val_end = val_start + val_size
            
            # Test comes after validation with gap
            test_start = val_end + self.gap if val_size > 0 else train_end + self.gap
            test_end = test_start + self.test_size
            
            if test_end > n_samples:
                break
            
            # Extract indices from the temporally sorted sequence
            train_indices = sorted_indices[start:train_end]
            val_indices = sorted_indices[val_start:val_end] if val_size > 0 else np.array([])
            test_indices = sorted_indices[test_start:test_end]
            
            # Ensure temporal order is preserved
            assert len(train_indices) > 0 and len(test_indices) > 0, "Empty window"
            
            yield train_indices, val_indices, test_indices
    
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
        total_window = self.window_size + self.gap + self.test_size
        n_windows = (n_samples - total_window) // self.step_size + 1
        return max(0, n_windows)
    
    def plot_splits(self, X, y=None, timestamps=None, figsize=(12, 6), save_path=None):
        """
        Visualize the sliding window splits as rectangles.
        
        Shows train (blue), validation (green), and test (red) sets.
        When val_ratio=0, only shows train and test.
        
        Parameters
        ----------
        X : array-like
            Training data
        y : array-like, optional
            Target variable (not used)
        timestamps : array-like, optional
            Timestamps (if None, uses sample indices)
        figsize : tuple, default (12, 6)
            Figure size
        save_path : str, optional
            Path to save the plot
            
        Returns
        -------
        fig : matplotlib.figure.Figure
            The created figure
        """
        # Use sample indices if no timestamps provided
        if timestamps is None:
            timestamps = np.arange(len(X))
        
        # Get temporal ordering
        time_order = np.argsort(timestamps)
        sorted_timestamps = timestamps[time_order]
        
        # Check if we have validation sets
        if self.val_ratio > 0:
            # Use split_with_val for 3-way splits
            splits = list(self.split_with_val(X, y, timestamps))[:10]  # Limit for clarity
            split_type = "train-val-test"
        else:
            # Use regular split for 2-way splits
            splits = list(self.split(X, y, timestamps))[:10]  # Limit to 10 folds for clarity
            split_type = "train-test"
        
        if not splits:
            raise ValueError("No splits generated")
        
        # Create figure
        fig, ax = plt.subplots(figsize=figsize)
        
        # Plot each fold based on temporal position
        for fold, split_indices in enumerate(splits):
            y_pos = fold
            
            if len(split_indices) == 3:  # train, val, test
                train_idx, val_idx, test_idx = split_indices
                
                # Find temporal positions of train indices
                train_positions = []
                for idx in train_idx:
                    temp_pos = np.where(time_order == idx)[0][0]  # Find position in sorted order
                    train_positions.append(temp_pos)
                
                # Plot train window based on temporal positions
                if train_positions:
                    train_start = min(train_positions)
                    train_end = max(train_positions)
                    train_rect = patches.Rectangle(
                        (train_start, y_pos - 0.3), 
                        len(train_positions), 0.6,
                        linewidth=1, edgecolor='blue', facecolor='lightblue', alpha=0.7,
                        label='Train' if fold == 0 else ""
                    )
                    ax.add_patch(train_rect)
                
                # Find temporal positions of validation indices
                if len(val_idx) > 0:
                    val_positions = []
                    for idx in val_idx:
                        temp_pos = np.where(time_order == idx)[0][0]
                        val_positions.append(temp_pos)
                    
                    # Plot validation window
                    if val_positions:
                        val_start = min(val_positions)
                        val_end = max(val_positions)
                        val_rect = patches.Rectangle(
                            (val_start, y_pos - 0.3),
                            len(val_positions), 0.6,
                            linewidth=1, edgecolor='green', facecolor='lightgreen', alpha=0.7,
                            label='Validation' if fold == 0 else ""
                        )
                        ax.add_patch(val_rect)
                
                # Find temporal positions of test indices  
                test_positions = []
                for idx in test_idx:
                    temp_pos = np.where(time_order == idx)[0][0]  # Find position in sorted order
                    test_positions.append(temp_pos)
                
                # Plot test window based on temporal positions
                if test_positions:
                    test_start = min(test_positions)
                    test_end = max(test_positions)
                    test_rect = patches.Rectangle(
                        (test_start, y_pos - 0.3),
                        len(test_positions), 0.6,
                        linewidth=1, edgecolor='red', facecolor='lightcoral', alpha=0.7,
                        label='Test' if fold == 0 else ""
                    )
                    ax.add_patch(test_rect)
                    
            else:  # train, test (2-way split)
                train_idx, test_idx = split_indices
                
                # Find temporal positions of train indices
                train_positions = []
                for idx in train_idx:
                    temp_pos = np.where(time_order == idx)[0][0]  # Find position in sorted order
                    train_positions.append(temp_pos)
                
                # Plot train window based on temporal positions
                if train_positions:
                    train_start = min(train_positions)
                    train_end = max(train_positions)
                    train_rect = patches.Rectangle(
                        (train_start, y_pos - 0.3), 
                        len(train_positions), 0.6,
                        linewidth=1, edgecolor='blue', facecolor='lightblue', alpha=0.7,
                        label='Train' if fold == 0 else ""
                    )
                    ax.add_patch(train_rect)
                
                # Find temporal positions of test indices  
                test_positions = []
                for idx in test_idx:
                    temp_pos = np.where(time_order == idx)[0][0]  # Find position in sorted order
                    test_positions.append(temp_pos)
                
                # Plot test window based on temporal positions
                if test_positions:
                    test_start = min(test_positions)
                    test_end = max(test_positions)
                    test_rect = patches.Rectangle(
                        (test_start, y_pos - 0.3),
                        len(test_positions), 0.6,
                        linewidth=1, edgecolor='red', facecolor='lightcoral', alpha=0.7,
                        label='Test' if fold == 0 else ""
                    )
                    ax.add_patch(test_rect)
        
        # Add scatter plots of actual data points with jittering
        np.random.seed(42)  # For reproducible jittering
        jitter_strength = 0.15  # Amount of vertical jittering
        
        for fold, split_indices in enumerate(splits):
            y_pos = fold
            
            if len(split_indices) == 3:  # train, val, test
                train_idx, val_idx, test_idx = split_indices
                
                # Find temporal positions for scatter plot
                train_positions = []
                for idx in train_idx:
                    temp_pos = np.where(time_order == idx)[0][0]
                    train_positions.append(temp_pos)
                    
                val_positions = []
                if len(val_idx) > 0:
                    for idx in val_idx:
                        temp_pos = np.where(time_order == idx)[0][0]
                        val_positions.append(temp_pos)
                    
                test_positions = []
                for idx in test_idx:
                    temp_pos = np.where(time_order == idx)[0][0]
                    test_positions.append(temp_pos)
                
                # Add jittered scatter plots for 3-way split
                if train_positions:
                    train_jitter = np.random.normal(0, jitter_strength, len(train_positions))
                    ax.scatter(train_positions, y_pos + train_jitter, 
                              c='darkblue', s=20, alpha=0.7, marker='o', 
                              label='Train points' if fold == 0 else '', zorder=3)
                              
                if val_positions:
                    val_jitter = np.random.normal(0, jitter_strength, len(val_positions))
                    ax.scatter(val_positions, y_pos + val_jitter, 
                              c='darkgreen', s=20, alpha=0.7, marker='^', 
                              label='Val points' if fold == 0 else '', zorder=3)
                              
                if test_positions:
                    test_jitter = np.random.normal(0, jitter_strength, len(test_positions))
                    ax.scatter(test_positions, y_pos + test_jitter, 
                              c='darkred', s=20, alpha=0.7, marker='s', 
                              label='Test points' if fold == 0 else '', zorder=3)
                              
            else:  # train, test (2-way split)
                train_idx, test_idx = split_indices
                
                # Get actual timestamps for train and test indices
                train_times = timestamps[train_idx] if timestamps is not None else train_idx
                test_times = timestamps[test_idx] if timestamps is not None else test_idx
                
                # Find temporal positions for scatter plot
                train_positions = []
                for idx in train_idx:
                    temp_pos = np.where(time_order == idx)[0][0]
                    train_positions.append(temp_pos)
                    
                test_positions = []
                for idx in test_idx:
                    temp_pos = np.where(time_order == idx)[0][0]
                    test_positions.append(temp_pos)
                
                # Add jittered scatter plots for 2-way split
                if train_positions:
                    train_jitter = np.random.normal(0, jitter_strength, len(train_positions))
                    ax.scatter(train_positions, y_pos + train_jitter, 
                              c='darkblue', s=20, alpha=0.7, marker='o', 
                              label='Train points' if fold == 0 else '', zorder=3)
                              
                if test_positions:
                    test_jitter = np.random.normal(0, jitter_strength, len(test_positions))
                    ax.scatter(test_positions, y_pos + test_jitter, 
                              c='darkred', s=20, alpha=0.7, marker='s', 
                              label='Test points' if fold == 0 else '', zorder=3)
        
        # Format plot
        ax.set_ylim(-0.5, len(splits) - 0.5)
        ax.set_xlim(0, len(X))
        ax.set_xlabel('Temporal Position (sorted by timestamp)')
        ax.set_ylabel('Fold')
        gap_text = f', Gap: {self.gap}' if self.gap > 0 else ''
        val_text = f', Val ratio: {self.val_ratio:.1%}' if self.val_ratio > 0 else ''
        ax.set_title(f'Sliding Window Split Visualization ({split_type})\\n'
                    f'Window: {self.window_size}, Step: {self.step_size}, Test: {self.test_size}{gap_text}{val_text}\\n'
                    f'Rectangles show windows, dots show actual data points')
        
        # Set y-ticks
        ax.set_yticks(range(len(splits)))
        ax.set_yticklabels([f'Fold {i}' for i in range(len(splits))])
        
        # Add legend with scatter points
        ax.legend(loc='upper right')
        
        plt.tight_layout()
        
        if save_path:
            fig.savefig(save_path, dpi=150, bbox_inches='tight')
        
        return fig


"""Functions & Classes"""
def main(args) -> int:
    """Demonstrate TimeSeriesSlidingWindowSplit functionality.
    
    Args:
        args: Command line arguments
        
    Returns:
        int: Exit status
    """
    logger.info("Demonstrating TimeSeriesSlidingWindowSplit functionality")
    
    # Generate test data
    np.random.seed(42)
    n_samples = args.n_samples
    X = np.random.randn(n_samples, 5)
    y = np.random.randint(0, 2, n_samples)
    # Add noise to timestamps to test sorting
    timestamps = np.arange(n_samples) + np.random.normal(0, 0.1, n_samples)
    
    logger.info(f"Generated test data: {n_samples} samples, {X.shape[1]} features")
    
    # Create sliding window splitter
    splitter = TimeSeriesSlidingWindowSplit(
        window_size=args.window_size,
        step_size=args.step_size,
        test_size=args.test_size,
        gap=args.gap
    )
    
    logger.info(f"Sliding window configuration:")
    logger.info(f"  Window size: {args.window_size}")
    logger.info(f"  Step size: {args.step_size}")
    logger.info(f"  Test size: {args.test_size}")
    logger.info(f"  Gap: {args.gap}")
    
    # Test splits
    splits = list(splitter.split(X, y, timestamps))[:5]  # Limit to 5 folds for demo
    logger.info(f"Generated {len(splits)} splits")
    
    for fold, (train_idx, test_idx) in enumerate(splits):
        logger.info(f"Fold {fold}: Train={len(train_idx)}, Test={len(test_idx)}")
        
        # Verify temporal order
        train_times = timestamps[train_idx]
        test_times = timestamps[test_idx]
        
        temporal_ok = train_times.max() < test_times.min()
        status = "✓" if temporal_ok else "✗"
        logger.info(f"  Temporal order: {status}")
        
        if not temporal_ok:
            logger.warning(f"  Train max time: {train_times.max():.2f}")
            logger.warning(f"  Test min time: {test_times.min():.2f}")
    
    # Generate visualization
    logger.info("Generating sliding window visualization with scatter plots")
    fig = splitter.plot_splits(X, y, timestamps)
    
    # Save using SciTeX framework
    stx.io.save(fig, "./sliding_window_demo.png", symlink_from_cwd=True)
    plt.close(fig)
    
    logger.info("TimeSeriesSlidingWindowSplit demonstration completed successfully")
    return 0


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Demonstrate TimeSeriesSlidingWindowSplit with temporal validation'
    )
    parser.add_argument(
        "--n-samples",
        type=int,
        default=200,
        help="Number of samples to generate (default: %(default)s)",
    )
    parser.add_argument(
        "--window-size",
        type=int,
        default=50,
        help="Size of training window (default: %(default)s)",
    )
    parser.add_argument(
        "--step-size",
        type=int,
        default=15,
        help="Step between windows (default: %(default)s)",
    )
    parser.add_argument(
        "--test-size",
        type=int,
        default=20,
        help="Size of test window (default: %(default)s)",
    )
    parser.add_argument(
        "--gap",
        type=int,
        default=5,
        help="Gap between train and test (default: %(default)s)",
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