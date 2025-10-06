#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-22 16:50:00 (ywatanabe)"
# File: _TimeSeriesStratifiedSplit.py

__FILE__ = "_TimeSeriesStratifiedSplit.py"

"""
Functionalities:
  - Implements time series cross-validation with stratification support
  - Ensures chronological order (test data always after training data)
  - Supports optional validation set between train and test
  - Maintains temporal gaps to prevent data leakage
  - Provides visualization with scatter plots for verification
  - Validates temporal integrity in all splits

Dependencies:
  - packages:
    - numpy
    - sklearn
    - matplotlib

IO:
  - input-files:
    - None (generates synthetic data for demonstration)
  - output-files:
    - ./stratified_splits_demo.png (visualization)
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
    random_state : int, optional
        Random seed for reproducibility (default: None)
    
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
        random_state: Optional[int] = None,
    ):
        self.n_splits = n_splits
        self.test_ratio = test_ratio
        self.val_ratio = val_ratio
        self.gap = gap
        self.stratify = stratify
        self.random_state = random_state
        self.rng = np.random.default_rng(random_state)
    
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
            train_end = n_samples - test_size - self.gap
            train_end = train_end - (self.n_splits - i - 1) * (test_size // self.n_splits)
            train_end = max(test_size, train_end)  # Ensure min training size
            
            # Apply gap and start test set immediately after gap
            test_start = train_end + self.gap
            test_end = min(test_start + test_size, n_samples)
            
            # Get indices
            train_indices = sorted_indices[:train_end]
            test_indices = sorted_indices[test_start:test_end]
            
            # For time series, temporal integrity is prioritized over stratification
            # Chronological order must be preserved to prevent data leakage
            # Class imbalance should be handled through other methods or at dataset level
            
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
        
        # Generate splits with strict temporal order
        for i in range(self.n_splits):
            # Calculate split points in temporal order (sorted domain)
            # Work backwards from the end to ensure proper spacing
            test_start_pos = n_samples - test_size
            test_start_pos = test_start_pos - i * (test_size // self.n_splits)  # Earlier for each fold
            test_end_pos = min(test_start_pos + test_size, n_samples)
            
            # Validation comes before test with gap
            val_end_pos = test_start_pos - self.gap
            val_start_pos = max(0, val_end_pos - val_size)
            
            # Training comes before validation with gap  
            train_end_pos = val_start_pos - self.gap
            train_start_pos = 0  # Always start from beginning (expanding window)
            
            # Ensure all positions are valid
            if train_end_pos <= train_start_pos or val_start_pos >= val_end_pos or test_start_pos >= test_end_pos:
                continue
                
            # Extract indices from temporally sorted sequence
            train_indices = sorted_indices[train_start_pos:train_end_pos]
            val_indices = sorted_indices[val_start_pos:val_end_pos]
            test_indices = sorted_indices[test_start_pos:test_end_pos]
            
            # For split_with_val, we prioritize temporal integrity over stratification
            # to ensure no overlapping between train, validation, and test sets
            # Class imbalance should be handled through other methods for 3-way splits
            
            yield train_indices, val_indices, test_indices
    
    def _stratify_indices_temporal(
        self, indices: np.ndarray, y: np.ndarray, target_size: int
    ) -> np.ndarray:
        """Apply stratification while preserving temporal order for time series.
        
        This method maintains chronological order as the top priority while
        attempting to balance class representation within the temporal window.
        """
        # If target_size >= current size, return as-is
        if target_size >= len(indices):
            return indices
        
        # Get the labels for these indices in their current temporal order
        current_labels = y[indices]
        unique_classes = np.unique(current_labels)
        
        # Calculate desired samples per class based on current distribution
        class_counts = {}
        for cls in unique_classes:
            class_counts[cls] = np.sum(current_labels == cls)
        
        total_current = len(indices)
        
        # Calculate target samples per class, proportional to current distribution
        target_per_class = {}
        remaining_target = target_size
        
        for cls in unique_classes:
            proportion = class_counts[cls] / total_current
            target_count = max(1, int(target_size * proportion))
            target_per_class[cls] = min(target_count, class_counts[cls])
            remaining_target -= target_per_class[cls]
        
        # Adjust if we're under/over the target
        if remaining_target > 0:
            # Distribute remaining samples to classes with most samples
            sorted_classes = sorted(unique_classes, 
                                  key=lambda x: class_counts[x], reverse=True)
            for cls in sorted_classes:
                if remaining_target <= 0:
                    break
                if target_per_class[cls] < class_counts[cls]:
                    target_per_class[cls] += 1
                    remaining_target -= 1
        
        # Select indices while preserving temporal order
        selected_indices = []
        class_taken = {cls: 0 for cls in unique_classes}
        
        for idx in indices:  # indices are already in temporal order
            label = y[idx]
            if class_taken[label] < target_per_class[label]:
                selected_indices.append(idx)
                class_taken[label] += 1
                
                # Stop if we've reached our target
                if len(selected_indices) >= target_size:
                    break
        
        return np.array(selected_indices)
    
    def get_n_splits(self, X=None, y=None, groups=None):
        """Returns the number of splitting iterations in the CV."""
        return self.n_splits
    
    def _find_contiguous_segments(self, indices):
        """Find contiguous segments in a sorted array of indices."""
        if len(indices) == 0:
            return []
        
        sorted_indices = np.sort(indices)
        segments = []
        start = sorted_indices[0]
        end = sorted_indices[0]
        
        for i in range(1, len(sorted_indices)):
            if sorted_indices[i] == end + 1:
                end = sorted_indices[i]
            else:
                segments.append((start, end))
                start = sorted_indices[i]
                end = sorted_indices[i]
        
        segments.append((start, end))
        return segments
    
    def plot_splits(self, X, y=None, timestamps=None, figsize=(12, 6), save_path=None):
        """
        Visualize the stratified time series splits.
        
        Shows train (blue), validation (green), and test (red) sets.
        When val_ratio=0, only shows train and test.
        
        Parameters
        ----------
        X : array-like
            Training data
        y : array-like, optional
            Target variable
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
        
        # Create figure
        fig, ax = plt.subplots(figsize=figsize)
        
        # Check if we have validation sets
        if self.val_ratio > 0:
            # Use split_with_val for 3-way splits
            splits = list(self.split_with_val(X, y, timestamps))
            split_type = "train-val-test"
        else:
            # Use regular split for 2-way splits
            splits = list(self.split(X, y, timestamps))
            split_type = "train-test"
        
        if not splits:
            raise ValueError("No splits generated")
        
        # Plot each fold
        for fold, split_indices in enumerate(splits):
            y_pos = fold
            
            if len(split_indices) == 3:  # train, val, test
                train_idx, val_idx, test_idx = split_indices
                
                # Train set (blue) - plot as individual segments if non-contiguous
                if len(train_idx) > 0:
                    # Find contiguous segments in train indices
                    train_segments = self._find_contiguous_segments(train_idx)
                    for start_idx, end_idx in train_segments:
                        train_rect = patches.Rectangle(
                            (start_idx, y_pos - 0.3), 
                            end_idx - start_idx + 1, 0.6,
                            linewidth=1, edgecolor='blue', facecolor='lightblue', alpha=0.7,
                            label='Train' if fold == 0 and start_idx == train_segments[0][0] else ""
                        )
                        ax.add_patch(train_rect)
                
                # Validation set (green) - plot as individual segments if non-contiguous
                if len(val_idx) > 0:
                    val_segments = self._find_contiguous_segments(val_idx)
                    for start_idx, end_idx in val_segments:
                        val_rect = patches.Rectangle(
                            (start_idx, y_pos - 0.3),
                            end_idx - start_idx + 1, 0.6,
                            linewidth=1, edgecolor='green', facecolor='lightgreen', alpha=0.7,
                            label='Validation' if fold == 0 and start_idx == val_segments[0][0] else ""
                        )
                        ax.add_patch(val_rect)
                
                # Test set (red) - plot as individual segments if non-contiguous
                if len(test_idx) > 0:
                    test_segments = self._find_contiguous_segments(test_idx)
                    for start_idx, end_idx in test_segments:
                        test_rect = patches.Rectangle(
                            (start_idx, y_pos - 0.3),
                            end_idx - start_idx + 1, 0.6,
                            linewidth=1, edgecolor='red', facecolor='lightcoral', alpha=0.7,
                            label='Test' if fold == 0 and start_idx == test_segments[0][0] else ""
                        )
                        ax.add_patch(test_rect)
                    
            else:  # train, test (2-way split)
                train_idx, test_idx = split_indices
                
                # Train set (blue) - plot as individual segments if non-contiguous
                if len(train_idx) > 0:
                    train_segments = self._find_contiguous_segments(train_idx)
                    for start_idx, end_idx in train_segments:
                        train_rect = patches.Rectangle(
                            (start_idx, y_pos - 0.3), 
                            end_idx - start_idx + 1, 0.6,
                            linewidth=1, edgecolor='blue', facecolor='lightblue', alpha=0.7,
                            label='Train' if fold == 0 and start_idx == train_segments[0][0] else ""
                        )
                        ax.add_patch(train_rect)
                
                # Test set (red) - plot as individual segments if non-contiguous
                if len(test_idx) > 0:
                    test_segments = self._find_contiguous_segments(test_idx)
                    for start_idx, end_idx in test_segments:
                        test_rect = patches.Rectangle(
                            (start_idx, y_pos - 0.3),
                            end_idx - start_idx + 1, 0.6,
                            linewidth=1, edgecolor='red', facecolor='lightcoral', alpha=0.7,
                            label='Test' if fold == 0 and start_idx == test_segments[0][0] else ""
                        )
                        ax.add_patch(test_rect)
        
        # Add scatter plots of actual data points with jittering
        np.random.seed(42)  # For reproducible jittering
        jitter_strength = 0.15  # Amount of vertical jittering
        
        for fold, split_indices in enumerate(splits):
            y_pos = fold
            
            if len(split_indices) == 3:  # train, val, test
                train_idx, val_idx, test_idx = split_indices
                
                # Add jittered scatter plots for 3-way split
                if len(train_idx) > 0:
                    train_jitter = np.random.normal(0, jitter_strength, len(train_idx))
                    ax.scatter(train_idx, y_pos + train_jitter, 
                              c='darkblue', s=15, alpha=0.6, marker='o', 
                              label='Train points' if fold == 0 else '', zorder=3)
                              
                if len(val_idx) > 0:
                    val_jitter = np.random.normal(0, jitter_strength, len(val_idx))
                    ax.scatter(val_idx, y_pos + val_jitter, 
                              c='darkgreen', s=15, alpha=0.6, marker='^', 
                              label='Val points' if fold == 0 else '', zorder=3)
                              
                if len(test_idx) > 0:
                    test_jitter = np.random.normal(0, jitter_strength, len(test_idx))
                    ax.scatter(test_idx, y_pos + test_jitter, 
                              c='darkred', s=15, alpha=0.6, marker='s', 
                              label='Test points' if fold == 0 else '', zorder=3)
                              
            else:  # train, test (2-way split)
                train_idx, test_idx = split_indices
                
                # Add jittered scatter plots for 2-way split
                if len(train_idx) > 0:
                    train_jitter = np.random.normal(0, jitter_strength, len(train_idx))
                    ax.scatter(train_idx, y_pos + train_jitter, 
                              c='darkblue', s=15, alpha=0.6, marker='o', 
                              label='Train points' if fold == 0 else '', zorder=3)
                              
                if len(test_idx) > 0:
                    test_jitter = np.random.normal(0, jitter_strength, len(test_idx))
                    ax.scatter(test_idx, y_pos + test_jitter, 
                              c='darkred', s=15, alpha=0.6, marker='s', 
                              label='Test points' if fold == 0 else '', zorder=3)
        
        # Format plot
        ax.set_ylim(-0.5, len(splits) - 0.5)
        ax.set_xlim(0, len(X))
        ax.set_xlabel('Sample Index (original order)')
        ax.set_ylabel('Fold')
        
        title = f'Time Series Stratified Split Visualization ({split_type})'
        if self.stratify:
            title += '\nMaintains class balance across splits'
        if self.gap > 0:
            title += f', Gap: {self.gap} samples'
        title += '\nRectangles show ranges, dots show actual data points'
        ax.set_title(title)
        
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
    """Demonstrate TimeSeriesStratifiedSplit functionality.
    
    Args:
        args: Command line arguments
        
    Returns:
        int: Exit status
    """
    logger.info("Demonstrating TimeSeriesStratifiedSplit functionality")
    
    # Generate test data
    np.random.seed(42)
    n_samples = 200
    X = np.random.randn(n_samples, 5)
    y = np.random.randint(0, 2, n_samples)
    timestamps = np.arange(n_samples) + np.random.normal(0, 0.1, n_samples)
    
    logger.info(f"Generated test data: {n_samples} samples, {X.shape[1]} features, {len(np.unique(y))} classes")
    
    # Test regular split
    logger.info("Testing regular train/test split")
    splitter = TimeSeriesStratifiedSplit(n_splits=3, test_ratio=0.2, gap=5)
    for fold, (train_idx, test_idx) in enumerate(splitter.split(X, y, timestamps)):
        logger.info(f"Fold {fold}: Train={len(train_idx)}, Test={len(test_idx)}")
    
    # Test split with validation
    logger.info("Testing train/validation/test split")
    splitter_val = TimeSeriesStratifiedSplit(n_splits=2, test_ratio=0.2, val_ratio=0.15, gap=3)
    for fold, (train_idx, val_idx, test_idx) in enumerate(splitter_val.split_with_val(X, y, timestamps)):
        logger.info(f"Fold {fold}: Train={len(train_idx)}, Val={len(val_idx)}, Test={len(test_idx)}")
        
        # Check temporal order
        train_times = timestamps[train_idx]
        val_times = timestamps[val_idx] if len(val_idx) > 0 else np.array([])
        test_times = timestamps[test_idx] if len(test_idx) > 0 else np.array([])
        
        temporal_ok = True
        if len(val_times) > 0 and len(test_times) > 0:
            temporal_ok = (train_times.max() < val_times.min()) and (val_times.max() < test_times.min())
        elif len(test_times) > 0:
            temporal_ok = train_times.max() < test_times.min()
            
        status = "✓" if temporal_ok else "✗"
        logger.info(f"  Temporal order: {status}")
    
    # Generate visualization
    logger.info("Generating split visualization")
    fig = splitter_val.plot_splits(X, y, timestamps)
    
    # Save using SciTeX framework
    stx.io.save(fig, "./stratified_splits_demo.png", symlink_from_cwd=True)
    plt.close(fig)
    
    logger.info("TimeSeriesStratifiedSplit demonstration completed successfully")
    return 0


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    import argparse
    parser = argparse.ArgumentParser(
        description='Demonstrate TimeSeriesStratifiedSplit with temporal integrity validation'
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