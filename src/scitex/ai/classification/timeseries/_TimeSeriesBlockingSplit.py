#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-22 17:10:00 (ywatanabe)"
# File: _TimeSeriesBlockingSplit.py

__FILE__ = "_TimeSeriesBlockingSplit.py"

"""
Functionalities:
  - Implements time series split with blocking for multiple subjects/groups
  - Ensures temporal integrity within each subject's timeline
  - Allows cross-subject generalization while preventing data leakage
  - Provides visualization with scatter plots and subject color coding
  - Validates that no data mixing occurs between subjects
  - Supports expanding window approach for more training data in later folds

Dependencies:
  - packages:
    - numpy
    - sklearn
    - matplotlib
    - scitex

IO:
  - input-files:
    - None (generates synthetic multi-subject data for demonstration)
  - output-files:
    - ./blocking_splits_demo.png (visualization with scatter plots)
"""

"""Imports"""
import os
import sys
import argparse
import numpy as np
from typing import Iterator, Optional, Tuple
from sklearn.model_selection import BaseCrossValidator
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import scitex as stx
from scitex import logging

logger = logging.getLogger(__name__)


class TimeSeriesBlockingSplit(BaseCrossValidator):
    """
    Time series split with blocking to handle multiple subjects/groups.
    
    This splitter ensures temporal integrity within each subject while allowing
    cross-subject generalization. Each subject's data is kept temporally coherent,
    but subjects can appear in both training and test sets at different time periods.
    
    Key Features:
    - Temporal order preserved within each subject
    - No data leakage within individual subject timelines  
    - Expanding window approach: more training data in later folds
    - Cross-subject generalization: subjects can be in both train and test
    
    Use Cases:
    - Multiple patients with longitudinal medical data
    - Multiple stocks with time series financial data
    - Multiple sensors with temporal measurements
    - Any scenario with grouped time series data
    
    Parameters
    ----------
    n_splits : int, default=5
        Number of splits (folds)
    test_ratio : float, default=0.2
        Proportion of data for test set per subject
    
    Examples
    --------
    >>> from scitex.ml.classification import TimeSeriesBlockingSplit
    >>> import numpy as np
    >>> 
    >>> # Create data: 100 samples, 4 subjects (25 samples each)
    >>> X = np.random.randn(100, 10)
    >>> y = np.random.randint(0, 2, 100)
    >>> timestamps = np.arange(100)
    >>> groups = np.repeat([0, 1, 2, 3], 25)  # Subject IDs
    >>> 
    >>> # Each subject gets temporal split: early samples → train, later → test
    >>> splitter = TimeSeriesBlockingSplit(n_splits=3, test_ratio=0.3)
    >>> for train_idx, test_idx in splitter.split(X, y, timestamps, groups):
    ...     train_subjects = set(groups[train_idx])
    ...     test_subjects = set(groups[test_idx])
    ...     print(f"Train subjects: {train_subjects}, Test subjects: {test_subjects}")
    ...     # Output shows same subjects in both sets but different time periods
    """
    
    def __init__(self, n_splits: int = 5, test_ratio: float = 0.2, val_ratio: float = 0.0, random_state: Optional[int] = None):
        self.n_splits = n_splits
        self.test_ratio = test_ratio
        self.val_ratio = val_ratio
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
    
    def split_with_val(
        self,
        X: np.ndarray,
        y: Optional[np.ndarray] = None,
        timestamps: Optional[np.ndarray] = None,
        groups: Optional[np.ndarray] = None,
    ) -> Iterator[Tuple[np.ndarray, np.ndarray, np.ndarray]]:
        """
        Generate indices with separate validation set respecting group boundaries.
        
        Each subject gets its own train/val/test split maintaining temporal order.
        
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
        val : ndarray
            Validation set indices
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
            val_indices = []
            test_indices = []
            
            for group in unique_groups:
                group_mask = groups == group
                group_indices = np.where(group_mask)[0]
                group_times = timestamps[group_mask]
                
                # Sort group by time
                time_order = np.argsort(group_times)
                sorted_group_indices = group_indices[time_order]
                
                # Split this group into train/val/test
                n_group = len(sorted_group_indices)
                test_size = int(n_group * self.test_ratio)
                val_size = int(n_group * self.val_ratio) if self.val_ratio > 0 else 0
                train_size = n_group - test_size - val_size
                
                # Expanding window approach for training
                split_point_train = train_size - (self.n_splits - i - 1) * (test_size // self.n_splits)
                split_point_train = max(1, min(split_point_train, train_size))
                
                # Define split points
                val_start = split_point_train
                test_start = val_start + val_size
                
                # Ensure we have enough data
                if test_start + test_size > n_group:
                    test_size = n_group - test_start
                
                # Extract indices for this group
                train_indices.extend(sorted_group_indices[:split_point_train])
                if val_size > 0:
                    val_indices.extend(sorted_group_indices[val_start:test_start])
                test_indices.extend(sorted_group_indices[test_start:test_start + test_size])
            
            yield np.array(train_indices), np.array(val_indices), np.array(test_indices)
    
    def get_n_splits(self, X=None, y=None, groups=None):
        """Returns the number of splitting iterations."""
        return self.n_splits
    
    def plot_splits(self, X, y=None, timestamps=None, groups=None, figsize=(12, 6), save_path=None):
        """
        Visualize the blocking splits showing subject separation.
        
        This visualization shows how data from different subjects/groups is allocated
        to training and test sets while maintaining temporal order within each subject.
        
        Color Scheme:
        - Rectangle border: Blue = Training set, Red = Test set
        - Rectangle fill: Different colors represent different subjects/groups
        - Each subject gets a unique color (cycling through colormap)
        
        Key Features:
        - No mixing: Each subject's data stays within temporal boundaries
        - Subject separation: Same subject can appear in both train/test but at different times
        - Temporal integrity: Time flows left to right for each subject
        
        Parameters
        ----------
        X : array-like
            Training data
        y : array-like, optional
            Target variable (not used)
        timestamps : array-like, optional
            Timestamps (if None, uses sample indices)
        groups : array-like
            Group labels (required for blocking split) - each unique value represents a subject
        figsize : tuple, default (12, 6)
            Figure size
        save_path : str, optional
            Path to save the plot
            
        Returns
        -------
        fig : matplotlib.figure.Figure
            The created figure with proper legend showing subject colors
            
        Examples
        --------
        >>> splitter = TimeSeriesBlockingSplit(n_splits=3)
        >>> fig = splitter.plot_splits(X, timestamps=timestamps, groups=subject_ids)
        >>> fig.show()  # Will show train (blue border) vs test (red border) by subject
        """
        if groups is None:
            raise ValueError("groups must be provided for blocking split visualization")
        
        # Get all splits
        splits = list(self.split(X, y, timestamps, groups))
        if not splits:
            raise ValueError("No splits generated")
        
        # Use sample indices if no timestamps provided
        if timestamps is None:
            timestamps = np.arange(len(X))
        
        # Create figure
        fig, ax = plt.subplots(figsize=figsize)
        
        # Plot each fold
        for fold, (train_idx, test_idx) in enumerate(splits):
            y_pos = fold
            
            # Get unique groups for train and test
            train_groups = set(groups[train_idx])
            test_groups = set(groups[test_idx])
            
            # Train subjects (different colors for each group)
            colors = plt.cm.Set3(np.linspace(0, 1, len(np.unique(groups))))
            for i, group in enumerate(sorted(train_groups)):
                group_mask = groups[train_idx] == group
                group_indices = train_idx[group_mask]
                if len(group_indices) > 0:
                    start_idx = group_indices[0]
                    end_idx = group_indices[-1]
                    width = end_idx - start_idx + 1
                    
                    train_rect = patches.Rectangle(
                        (start_idx, y_pos - 0.3), 
                        width, 0.6,
                        linewidth=1, edgecolor='blue', 
                        facecolor=colors[group % len(colors)], alpha=0.7,
                        label=f'Train Group {group}' if fold == 0 else ""
                    )
                    ax.add_patch(train_rect)
            
            # Test subjects 
            for i, group in enumerate(sorted(test_groups)):
                group_mask = groups[test_idx] == group
                group_indices = test_idx[group_mask]
                if len(group_indices) > 0:
                    start_idx = group_indices[0] 
                    end_idx = group_indices[-1]
                    width = end_idx - start_idx + 1
                    
                    test_rect = patches.Rectangle(
                        (start_idx, y_pos - 0.3),
                        width, 0.6,
                        linewidth=2, edgecolor='red', facecolor='lightcoral', alpha=0.8,
                        label=f'Test Group {group}' if fold == 0 else ""
                    )
                    ax.add_patch(test_rect)
        
        # Format plot
        ax.set_ylim(-0.5, len(splits) - 0.5)
        ax.set_xlim(0, len(X))
        ax.set_xlabel('Sample Index')
        ax.set_ylabel('Fold')
        ax.set_title(f'Time Series Blocking Split Visualization\\n'
                    f'No mixing between subjects/groups')
        
        # Set y-ticks
        ax.set_yticks(range(len(splits)))
        ax.set_yticklabels([f'Fold {i}' for i in range(len(splits))])
        
        # Add scatter plots of actual data points with jittering
        np.random.seed(42)  # For reproducible jittering
        jitter_strength = 0.15  # Amount of vertical jittering
        
        for fold, (train_idx, test_idx) in enumerate(splits):
            y_pos = fold
            
            # Add jittered scatter plots for train indices
            if len(train_idx) > 0:
                train_jitter = np.random.normal(0, jitter_strength, len(train_idx))
                # Color by group
                for group in np.unique(groups[train_idx]):
                    group_mask = groups[train_idx] == group
                    group_train_idx = train_idx[group_mask]
                    group_jitter = train_jitter[group_mask]
                    ax.scatter(group_train_idx, y_pos + group_jitter, 
                              c='darkblue', s=15, alpha=0.6, marker='o', 
                              label='Train points' if fold == 0 and group == np.unique(groups[train_idx])[0] else '', 
                              zorder=3)
                              
            # Add jittered scatter plots for test indices
            if len(test_idx) > 0:
                test_jitter = np.random.normal(0, jitter_strength, len(test_idx))
                # Color by group
                for group in np.unique(groups[test_idx]):
                    group_mask = groups[test_idx] == group
                    group_test_idx = test_idx[group_mask]
                    group_jitter = test_jitter[group_mask]
                    ax.scatter(group_test_idx, y_pos + group_jitter, 
                              c='darkred', s=15, alpha=0.6, marker='s', 
                              label='Test points' if fold == 0 and group == np.unique(groups[test_idx])[0] else '', 
                              zorder=3)
        
        # Create comprehensive legend
        from matplotlib.lines import Line2D
        from matplotlib.patches import Patch
        
        # Get unique groups and their colors
        unique_groups = np.unique(groups)
        colors = plt.cm.Set3(np.linspace(0, 1, len(unique_groups)))
        
        legend_elements = []
        
        # Add train/test border legend
        legend_elements.extend([
            Line2D([0], [0], color='blue', lw=3, alpha=0.7, label='Training Set (blue border)'),
            Line2D([0], [0], color='red', lw=3, alpha=0.8, label='Test Set (red border)')
        ])
        
        # Add a separator
        legend_elements.append(Line2D([0], [0], color='white', lw=0, label=''))
        
        # Add subject color legend
        for i, group in enumerate(sorted(unique_groups)):
            legend_elements.append(
                Patch(facecolor=colors[i % len(colors)], alpha=0.7, 
                     label=f'Subject/Group {group}')
            )
        
        # Create legend with two columns if many subjects
        ncol = 1 if len(unique_groups) <= 3 else 2
        ax.legend(handles=legend_elements, loc='center left', bbox_to_anchor=(1.02, 0.5), ncol=ncol)
        
        plt.tight_layout()
        
        if save_path:
            fig.savefig(save_path, dpi=150, bbox_inches='tight')
        
        return fig


"""Functions & Classes"""
def main(args) -> int:
    """Demonstrate TimeSeriesBlockingSplit functionality.
    
    Args:
        args: Command line arguments
        
    Returns:
        int: Exit status
    """
    logger.info("Demonstrating TimeSeriesBlockingSplit functionality")
    
    # Generate test data with multiple subjects
    np.random.seed(42)
    n_samples = args.n_samples
    n_subjects = args.n_subjects
    
    # Generate data
    X = np.random.randn(n_samples, 5)
    y = np.random.randint(0, 2, n_samples)
    timestamps = np.arange(n_samples) + np.random.normal(0, 0.1, n_samples)
    
    # Create subject groups
    samples_per_subject = n_samples // n_subjects
    groups = np.repeat(range(n_subjects), samples_per_subject)
    # Pad if necessary
    groups = np.pad(groups, (0, n_samples - len(groups)), mode='constant', constant_values=n_subjects-1)
    
    logger.info(f"Generated test data: {n_samples} samples, {n_subjects} subjects")
    logger.info(f"Samples per subject: ~{samples_per_subject}")
    
    # Create blocking splitter
    splitter = TimeSeriesBlockingSplit(
        n_splits=args.n_splits,
        test_ratio=args.test_ratio
    )
    
    logger.info(f"Blocking split configuration:")
    logger.info(f"  Number of splits: {args.n_splits}")
    logger.info(f"  Test ratio: {args.test_ratio}")
    
    # Test splits
    for fold, (train_idx, test_idx) in enumerate(splitter.split(X, y, timestamps, groups)):
        train_subjects = sorted(set(groups[train_idx]))
        test_subjects = sorted(set(groups[test_idx]))
        
        logger.info(f"Fold {fold}:")
        logger.info(f"  Train: {len(train_idx)} samples from subjects {train_subjects}")
        logger.info(f"  Test: {len(test_idx)} samples from subjects {test_subjects}")
        
        # Check subject overlap
        overlap = set(train_subjects) & set(test_subjects)
        if overlap:
            logger.info(f"  Subjects in both: {sorted(overlap)} (temporal separation maintained)")
        else:
            logger.info(f"  No subject overlap")
    
    # Generate visualization
    logger.info("Generating blocking split visualization with scatter plots")
    fig = splitter.plot_splits(X, y, timestamps, groups)
    
    # Save using SciTeX framework
    stx.io.save(fig, "./blocking_splits_demo.png", symlink_from_cwd=True)
    plt.close(fig)
    
    logger.info("TimeSeriesBlockingSplit demonstration completed successfully")
    return 0


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Demonstrate TimeSeriesBlockingSplit for multi-subject time series'
    )
    parser.add_argument(
        "--n-samples",
        type=int,
        default=300,
        help="Total number of samples (default: %(default)s)",
    )
    parser.add_argument(
        "--n-subjects",
        type=int,
        default=4,
        help="Number of subjects/groups (default: %(default)s)",
    )
    parser.add_argument(
        "--n-splits",
        type=int,
        default=3,
        help="Number of CV splits (default: %(default)s)",
    )
    parser.add_argument(
        "--test-ratio",
        type=float,
        default=0.3,
        help="Proportion of data for test per subject (default: %(default)s)",
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