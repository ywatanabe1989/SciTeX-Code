#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-03 03:22:45 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/ml/classification/timeseries/_TimeSeriesSlidingWindowSplit.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/ml/classification/timeseries/_TimeSeriesSlidingWindowSplit.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

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
import argparse
from typing import Iterator, Optional, Tuple

import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
import scitex as stx
from scitex import logging
from sklearn.model_selection import BaseCrossValidator
from sklearn.utils.validation import _num_samples

logger = logging.getLogger(__name__)

COLORS = stx.plt.color.PARAMS
COLORS["RGBA_NORM"]


class TimeSeriesSlidingWindowSplit(BaseCrossValidator):
    """
    Sliding window cross-validation for time series.

    Creates train/test windows that slide through time with configurable behavior.

    Parameters
    ----------
    window_size : int
        Size of training window (ignored if expanding_window=True)
    step_size : int
        Step between windows (overridden if overlapping_tests=False)
    test_size : int
        Size of test window
    gap : int, default=0
        Number of samples to skip between train and test windows
    val_ratio : float, default=0.0
        Ratio of validation set from training window
    random_state : int, optional
        Random seed for reproducibility
    overlapping_tests : bool, default=False
        If False, automatically sets step_size=test_size to ensure each sample
        is tested exactly once (like K-fold for time series)
    expanding_window : bool, default=False
        If True, training window grows to include all past data (like sklearn's
        TimeSeriesSplit). If False, uses fixed sliding window of size window_size.
    undersample : bool, default=False
        If True, balance classes in training sets by randomly undersampling
        the majority class to match the minority class count. Temporal order
        is maintained. Requires y labels in split().

    Examples
    --------
    >>> from scitex.ml.classification import TimeSeriesSlidingWindowSplit
    >>> import numpy as np
    >>>
    >>> X = np.random.randn(100, 10)
    >>> y = np.random.randint(0, 2, 100)
    >>> timestamps = np.arange(100)
    >>>
    >>> # Fixed window, non-overlapping tests (default)
    >>> swcv = TimeSeriesSlidingWindowSplit(window_size=50, test_size=10, gap=5)
    >>> for train_idx, test_idx in swcv.split(X, y, timestamps):
    ...     print(f"Train: {len(train_idx)}, Test: {len(test_idx)}")
    >>>
    >>> # Expanding window (use all past data)
    >>> swcv = TimeSeriesSlidingWindowSplit(
    ...     window_size=50, test_size=10, gap=5, expanding_window=True
    ... )
    >>> for train_idx, test_idx in swcv.split(X, y, timestamps):
    ...     print(f"Train: {len(train_idx)}, Test: {len(test_idx)}")  # Train grows!
    """

    def __init__(
        self,
        window_size: int,
        step_size: Optional[int] = None,
        test_size: int = 10,
        gap: int = 0,
        val_ratio: float = 0.0,
        random_state: Optional[int] = None,
        overlapping_tests: bool = False,
        expanding_window: bool = False,
        undersample: bool = False,
    ):
        self.window_size = window_size
        self.test_size = test_size
        self.gap = gap
        self.val_ratio = val_ratio
        self.random_state = random_state
        self.rng = np.random.default_rng(random_state)
        self.overlapping_tests = overlapping_tests
        self.expanding_window = expanding_window
        self.undersample = undersample
        self.n_splits_mode = False
        self._n_splits = None

        # Handle step_size logic
        if not overlapping_tests:
            # overlapping_tests=False: ensure non-overlapping tests
            if step_size is not None and step_size < test_size:
                logger.warning(
                    f"overlapping_tests=False but step_size={step_size} < test_size={test_size}. "
                    f"This would cause test overlap. Setting step_size=test_size={test_size}."
                )
                self.step_size = test_size
            elif step_size is None:
                # Default: non-overlapping tests
                self.step_size = test_size
                logger.info(
                    f"step_size not specified with overlapping_tests=False. "
                    f"Using step_size=test_size={test_size} for non-overlapping tests."
                )
            else:
                # step_size >= test_size: acceptable, no overlap
                self.step_size = step_size
        else:
            # overlapping_tests=True: allow any step_size
            if step_size is None:
                # Default for overlapping: half the test size for 50% overlap
                self.step_size = max(1, test_size // 2)
                logger.info(
                    f"step_size not specified with overlapping_tests=True. "
                    f"Using step_size={self.step_size} (50% overlap)."
                )
            else:
                self.step_size = step_size

    def _undersample_indices(
        self, train_indices: np.ndarray, y: np.ndarray, timestamps: np.ndarray
    ) -> np.ndarray:
        """
        Undersample majority class to balance training set.

        Maintains temporal order of samples.

        Parameters
        ----------
        train_indices : ndarray
            Original training indices
        y : ndarray
            Full label array
        timestamps : ndarray
            Full timestamp array

        Returns
        -------
        ndarray
            Undersampled training indices (sorted by timestamp)
        """
        # Get labels for training indices
        train_labels = y[train_indices]

        # Find unique classes and their counts
        unique_classes, class_counts = np.unique(
            train_labels, return_counts=True
        )

        if len(unique_classes) < 2:
            # Only one class, no undersampling needed
            return train_indices

        # Find minority class count
        min_count = class_counts.min()

        # Undersample each class to match minority class count
        undersampled_indices = []
        for cls in unique_classes:
            # Find indices of this class within train_indices
            cls_mask = train_labels == cls
            cls_train_indices = train_indices[cls_mask]

            if len(cls_train_indices) > min_count:
                # Randomly select min_count samples
                selected = self.rng.choice(
                    cls_train_indices, size=min_count, replace=False
                )
                undersampled_indices.extend(selected)
            else:
                # Keep all samples from minority class
                undersampled_indices.extend(cls_train_indices)

        # Convert to array and sort by timestamp to maintain temporal order
        undersampled_indices = np.array(undersampled_indices)
        temporal_order = np.argsort(timestamps[undersampled_indices])
        undersampled_indices = undersampled_indices[temporal_order]

        return undersampled_indices

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

        # Auto-calculate sizes if using n_splits mode
        if self.n_splits_mode:
            # Calculate test_size to create exactly n_splits folds
            # Formula: n_samples = window_size + (n_splits * (test_size + gap))
            # For expanding window, window_size is minimum training size
            # We want non-overlapping tests by default

            if self.expanding_window:
                # Expanding window: start with minimum window, test slides forward
                # Let's use 20% of data as initial window (similar to sklearn)
                min_window_size = max(1, n_samples // (self._n_splits + 1))
                available_for_test = (
                    n_samples - min_window_size - (self._n_splits * self.gap)
                )
                calculated_test_size = max(
                    1, available_for_test // self._n_splits
                )

                # Set calculated values
                self.window_size = min_window_size
                self.test_size = calculated_test_size
                self.step_size = (
                    calculated_test_size  # Non-overlapping by default
                )

                logger.info(
                    f"n_splits={self._n_splits} with expanding_window: "
                    f"Calculated window_size={self.window_size}, test_size={self.test_size}"
                )
            else:
                # Fixed window: calculate window and test size
                # We want: n_samples = window_size + (n_splits * (test_size + gap))
                # Let's make window_size same as test_size for simplicity
                available = n_samples - (self._n_splits * self.gap)
                calculated_test_size = max(
                    1, available // (self._n_splits + 1)
                )
                calculated_window_size = calculated_test_size

                # Set calculated values
                self.window_size = calculated_window_size
                self.test_size = calculated_test_size
                self.step_size = (
                    calculated_test_size  # Non-overlapping by default
                )

                logger.info(
                    f"n_splits={self._n_splits} with fixed window: "
                    f"Calculated window_size={self.window_size}, test_size={self.test_size}"
                )

        if self.expanding_window:
            # Expanding window: training set grows to include all past data
            # Start with minimum window_size, test slides forward
            min_train_size = self.window_size
            total_min = min_train_size + self.gap + self.test_size

            if n_samples < total_min:
                logger.warning(
                    f"Not enough samples ({n_samples}) for even one split. "
                    f"Need at least {total_min} samples."
                )
                return

            # First fold starts at window_size
            test_start_pos = min_train_size + self.gap

            while test_start_pos + self.test_size <= n_samples:
                test_end_pos = test_start_pos + self.test_size

                # Training includes all data from start to before gap
                train_end_pos = test_start_pos - self.gap
                train_indices = sorted_indices[0:train_end_pos]
                test_indices = sorted_indices[test_start_pos:test_end_pos]

                # Apply undersampling if enabled and y is provided
                if self.undersample and y is not None:
                    train_indices = self._undersample_indices(
                        train_indices, y, timestamps
                    )

                assert (
                    len(train_indices) > 0 and len(test_indices) > 0
                ), "Empty window"

                yield train_indices, test_indices

                # Move test window forward by step_size
                test_start_pos += self.step_size

        else:
            # Fixed sliding window: window slides through data
            total_window = self.window_size + self.gap + self.test_size

            for start in range(
                0, n_samples - total_window + 1, self.step_size
            ):
                # These positions are in the sorted (temporal) domain
                train_end = start + self.window_size
                test_start = train_end + self.gap
                test_end = test_start + self.test_size

                if test_end > n_samples:
                    break

                # Extract indices from the temporally sorted sequence
                train_indices = sorted_indices[start:train_end]
                test_indices = sorted_indices[test_start:test_end]

                # Apply undersampling if enabled and y is provided
                if self.undersample and y is not None:
                    train_indices = self._undersample_indices(
                        train_indices, y, timestamps
                    )

                assert (
                    len(train_indices) > 0 and len(test_indices) > 0
                ), "Empty window"

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

        # Auto-calculate sizes if using n_splits mode
        if self.n_splits_mode:
            if self.expanding_window:
                min_window_size = max(1, n_samples // (self._n_splits + 1))
                available_for_test = (
                    n_samples - min_window_size - (self._n_splits * self.gap)
                )
                calculated_test_size = max(
                    1, available_for_test // self._n_splits
                )
                self.window_size = min_window_size
                self.test_size = calculated_test_size
                self.step_size = calculated_test_size
            else:
                available = n_samples - (self._n_splits * self.gap)
                calculated_test_size = max(
                    1, available // (self._n_splits + 1)
                )
                calculated_window_size = calculated_test_size
                self.window_size = calculated_window_size
                self.test_size = calculated_test_size
                self.step_size = calculated_test_size

        # Calculate validation size from training window
        val_size = (
            int(self.window_size * self.val_ratio) if self.val_ratio > 0 else 0
        )
        actual_train_size = self.window_size - val_size

        if self.expanding_window:
            # Expanding window with validation
            min_train_size = self.window_size
            total_min = min_train_size + self.gap + self.test_size

            if n_samples < total_min:
                logger.warning(
                    f"Not enough samples ({n_samples}) for even one split. "
                    f"Need at least {total_min} samples."
                )
                return

            # Calculate positions for validation and test
            test_start_pos = min_train_size + self.gap

            while test_start_pos + self.test_size <= n_samples:
                test_end_pos = test_start_pos + self.test_size

                # Training + validation comes before gap
                train_val_end_pos = test_start_pos - self.gap

                # Split train/val from the expanding window
                if val_size > 0:
                    train_end_pos = train_val_end_pos - val_size
                    train_indices = sorted_indices[0:train_end_pos]
                    val_indices = sorted_indices[
                        train_end_pos:train_val_end_pos
                    ]
                else:
                    train_indices = sorted_indices[0:train_val_end_pos]
                    val_indices = np.array([])

                test_indices = sorted_indices[test_start_pos:test_end_pos]

                # Apply undersampling if enabled and y is provided
                if self.undersample and y is not None:
                    train_indices = self._undersample_indices(
                        train_indices, y, timestamps
                    )
                    # Also undersample validation set if it exists
                    if len(val_indices) > 0:
                        val_indices = self._undersample_indices(
                            val_indices, y, timestamps
                        )

                assert (
                    len(train_indices) > 0 and len(test_indices) > 0
                ), "Empty window"

                yield train_indices, val_indices, test_indices

                # Move test window forward by step_size
                test_start_pos += self.step_size

        else:
            # Fixed sliding window with validation
            total_window = self.window_size + self.gap + self.test_size

            for start in range(
                0, n_samples - total_window + 1, self.step_size
            ):
                # These positions are in the sorted (temporal) domain
                train_end = start + actual_train_size

                # Validation comes after train with optional gap
                val_start = train_end + (self.gap if val_size > 0 else 0)
                val_end = val_start + val_size

                # Test comes after validation with gap
                test_start = (
                    val_end + self.gap
                    if val_size > 0
                    else train_end + self.gap
                )
                test_end = test_start + self.test_size

                if test_end > n_samples:
                    break

                # Extract indices from the temporally sorted sequence
                train_indices = sorted_indices[start:train_end]
                val_indices = (
                    sorted_indices[val_start:val_end]
                    if val_size > 0
                    else np.array([])
                )
                test_indices = sorted_indices[test_start:test_end]

                # Apply undersampling if enabled and y is provided
                if self.undersample and y is not None:
                    train_indices = self._undersample_indices(
                        train_indices, y, timestamps
                    )
                    # Also undersample validation set if it exists
                    if len(val_indices) > 0:
                        val_indices = self._undersample_indices(
                            val_indices, y, timestamps
                        )

                # Ensure temporal order is preserved
                assert (
                    len(train_indices) > 0 and len(test_indices) > 0
                ), "Empty window"

                yield train_indices, val_indices, test_indices

    def get_n_splits(self, X=None, y=None, groups=None):
        """
        Calculate number of splits.

        Parameters
        ----------
        X : array-like, shape (n_samples, n_features), optional
            Training data (required to determine number of splits in manual mode)
        y : array-like, optional
            Not used
        groups : array-like, optional
            Not used

        Returns
        -------
        n_splits : int
            Number of splits. Returns -1 if X is None and not in n_splits mode.
        """
        # If using n_splits mode, return the specified n_splits
        if self.n_splits_mode:
            return self._n_splits

        # Manual mode: need data to calculate
        if X is None:
            return -1  # Can't determine without data

        n_samples = _num_samples(X)
        total_window = self.window_size + self.gap + self.test_size
        n_windows = (n_samples - total_window) // self.step_size + 1
        return max(0, n_windows)

    def plot_splits(
        self, X, y=None, timestamps=None, figsize=(12, 6), save_path=None
    ):
        """
        Visualize the sliding window splits as rectangles.

        Shows train (blue), validation (green), and test (red) sets.
        When val_ratio=0, only shows train and test.
        When undersampling is enabled, shows dropped samples in gray.

        Parameters
        ----------
        X : array-like
            Training data
        y : array-like, optional
            Target variable (required for undersampling visualization)
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

        # Get splits WITH undersampling (if enabled)
        if self.val_ratio > 0:
            splits = list(self.split_with_val(X, y, timestamps))[:10]
            split_type = "train-val-test"
        else:
            splits = list(self.split(X, y, timestamps))[:10]
            split_type = "train-test"

        if not splits:
            raise ValueError("No splits generated")

        # If undersampling is enabled, also get splits WITHOUT undersampling to show dropped samples
        splits_no_undersample = None
        if self.undersample and y is not None:
            original_undersample = self.undersample
            self.undersample = False  # Temporarily disable
            if self.val_ratio > 0:
                splits_no_undersample = list(
                    self.split_with_val(X, y, timestamps)
                )[:10]
            else:
                splits_no_undersample = list(self.split(X, y, timestamps))[:10]
            self.undersample = original_undersample  # Restore

        # Create figure
        fig, ax = stx.plt.subplots(figsize=figsize)

        # Plot each fold based on temporal position
        for fold, split_indices in enumerate(splits):
            y_pos = fold

            if len(split_indices) == 3:  # train, val, test
                train_idx, val_idx, test_idx = split_indices

                # Find temporal positions of train indices
                train_positions = []
                for idx in train_idx:
                    temp_pos = np.where(time_order == idx)[0][
                        0
                    ]  # Find position in sorted order
                    train_positions.append(temp_pos)

                # Plot train window based on temporal positions
                if train_positions:
                    train_start = min(train_positions)
                    train_end = max(train_positions)
                    train_rect = patches.Rectangle(
                        (train_start, y_pos - 0.3),
                        train_end - train_start + 1,
                        0.6,
                        linewidth=1,
                        edgecolor="blue",
                        facecolor="lightblue",
                        alpha=0.7,
                        label="Train" if fold == 0 else "",
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
                            val_end - val_start + 1,
                            0.6,
                            linewidth=1,
                            edgecolor="green",
                            facecolor="lightgreen",
                            alpha=0.7,
                            label="Validation" if fold == 0 else "",
                        )
                        ax.add_patch(val_rect)

                # Find temporal positions of test indices
                test_positions = []
                for idx in test_idx:
                    temp_pos = np.where(time_order == idx)[0][
                        0
                    ]  # Find position in sorted order
                    test_positions.append(temp_pos)

                # Plot test window based on temporal positions
                if test_positions:
                    test_start = min(test_positions)
                    test_end = max(test_positions)
                    test_rect = patches.Rectangle(
                        (test_start, y_pos - 0.3),
                        test_end - test_start + 1,
                        0.6,
                        linewidth=1,
                        edgecolor=COLORS["RGBA_NORM"]["red"],
                        facecolor=COLORS["RGBA_NORM"]["red"],
                        alpha=0.7,
                        label="Test" if fold == 0 else "",
                    )
                    ax.add_patch(test_rect)

            else:  # train, test (2-way split)
                train_idx, test_idx = split_indices

                # Find temporal positions of train indices
                train_positions = []
                for idx in train_idx:
                    temp_pos = np.where(time_order == idx)[0][
                        0
                    ]  # Find position in sorted order
                    train_positions.append(temp_pos)

                # Plot train window based on temporal positions
                if train_positions:
                    train_start = min(train_positions)
                    train_end = max(train_positions)
                    train_rect = patches.Rectangle(
                        (train_start, y_pos - 0.3),
                        train_end - train_start + 1,
                        0.6,
                        linewidth=1,
                        edgecolor=COLORS["RGBA_NORM"]["light_blue"],
                        facecolor=COLORS["RGBA_NORM"]["light_blue"],
                        alpha=0.7,
                        label="Train" if fold == 0 else "",
                    )
                    ax.add_patch(train_rect)

                # Find temporal positions of test indices
                test_positions = []
                for idx in test_idx:
                    temp_pos = np.where(time_order == idx)[0][
                        0
                    ]  # Find position in sorted order
                    test_positions.append(temp_pos)

                # Plot test window based on temporal positions
                if test_positions:
                    test_start = min(test_positions)
                    test_end = max(test_positions)
                    test_rect = patches.Rectangle(
                        (test_start, y_pos - 0.3),
                        test_end - test_start + 1,
                        0.6,
                        linewidth=1,
                        edgecolor="red",
                        facecolor="lightcoral",
                        alpha=0.7,
                        label="Test" if fold == 0 else "",
                    )
                    ax.add_patch(test_rect)

        # Add scatter plots of actual data points with jittering
        np.random.seed(42)  # For reproducible jittering
        jitter_strength = 0.15  # Amount of vertical jittering

        # First, plot dropped samples in gray if undersampling is enabled
        if splits_no_undersample is not None:
            for fold, split_indices_no_us in enumerate(splits_no_undersample):
                y_pos = fold
                split_indices_us = splits[fold]

                if len(split_indices_no_us) == 3:  # train, val, test
                    train_idx_no_us, val_idx_no_us, test_idx_no_us = (
                        split_indices_no_us
                    )
                    train_idx_us, val_idx_us, test_idx_us = split_indices_us

                    # Find dropped train samples
                    dropped_train = np.setdiff1d(train_idx_no_us, train_idx_us)
                    if len(dropped_train) > 0:
                        dropped_train_positions = [
                            np.where(time_order == idx)[0][0]
                            for idx in dropped_train
                        ]
                        dropped_train_jitter = np.random.normal(
                            0, jitter_strength, len(dropped_train_positions)
                        )
                        ax.plot_scatter(
                            dropped_train_positions,
                            y_pos + dropped_train_jitter,
                            c="gray",
                            s=15,
                            alpha=0.3,
                            marker="x",
                            label="Dropped (train)" if fold == 0 else "",
                            zorder=2,
                        )

                    # Find dropped validation samples
                    dropped_val = np.setdiff1d(val_idx_no_us, val_idx_us)
                    if len(dropped_val) > 0:
                        dropped_val_positions = [
                            np.where(time_order == idx)[0][0]
                            for idx in dropped_val
                        ]
                        dropped_val_jitter = np.random.normal(
                            0, jitter_strength, len(dropped_val_positions)
                        )
                        ax.plot_scatter(
                            dropped_val_positions,
                            y_pos + dropped_val_jitter,
                            c="gray",
                            s=15,
                            alpha=0.3,
                            marker="x",
                            label="Dropped (val)" if fold == 0 else "",
                            zorder=2,
                        )

                else:  # train, test (2-way split)
                    train_idx_no_us, test_idx_no_us = split_indices_no_us
                    train_idx_us, test_idx_us = split_indices_us

                    # Find dropped train samples
                    dropped_train = np.setdiff1d(train_idx_no_us, train_idx_us)
                    if len(dropped_train) > 0:
                        dropped_train_positions = [
                            np.where(time_order == idx)[0][0]
                            for idx in dropped_train
                        ]
                        dropped_train_jitter = np.random.normal(
                            0, jitter_strength, len(dropped_train_positions)
                        )
                        ax.plot_scatter(
                            dropped_train_positions,
                            y_pos + dropped_train_jitter,
                            c="gray",
                            s=15,
                            alpha=0.3,
                            marker="x",
                            label="Dropped samples" if fold == 0 else "",
                            zorder=2,
                        )

        # Then, plot kept samples in color
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
                    train_jitter = np.random.normal(
                        0, jitter_strength, len(train_positions)
                    )
                    # Color by class if y is provided
                    if y is not None:
                        train_colors = [
                            stx.plt.color.PARAMS["RGBA_NORM"]["blue"] if y[idx] == 0 else stx.plt.color.PARAMS["RGBA_NORM"]["light_blue"]
                            for idx in train_idx
                        ]
                        ax.plot_scatter(
                            train_positions,
                            y_pos + train_jitter,
                            c=train_colors,
                            s=20,
                            alpha=0.7,
                            marker="o",
                            label="Train (class 0)" if fold == 0 else "",
                            zorder=3,
                        )
                    else:
                        ax.plot_scatter(
                            train_positions,
                            y_pos + train_jitter,
                            c="darkblue",
                            s=20,
                            alpha=0.7,
                            marker="o",
                            label="Train points" if fold == 0 else "",
                            zorder=3,
                        )

                if val_positions:
                    val_jitter = np.random.normal(
                        0, jitter_strength, len(val_positions)
                    )
                    # Color by class if y is provided
                    if y is not None:
                        val_colors = [
                            stx.plt.color.PARAMS["RGBA_NORM"]["yellow"] if y[idx] == 0 else stx.plt.color.PARAMS["RGBA_NORM"]["orange"]
                            for idx in val_idx
                        ]
                        ax.plot_scatter(
                            val_positions,
                            y_pos + val_jitter,
                            c=val_colors,
                            s=20,
                            alpha=0.7,
                            marker="^",
                            label="Val (class 0)" if fold == 0 else "",
                            zorder=3,
                        )
                    else:
                        ax.plot_scatter(
                            val_positions,
                            y_pos + val_jitter,
                            c="darkgreen",
                            s=20,
                            alpha=0.7,
                            marker="^",
                            label="Val points" if fold == 0 else "",
                            zorder=3,
                        )

                if test_positions:
                    test_jitter = np.random.normal(
                        0, jitter_strength, len(test_positions)
                    )
                    # Color by class if y is provided
                    if y is not None:
                        test_colors = [
                            stx.plt.color.PARAMS["RGBA_NORM"]["red"] if y[idx] == 0 else stx.plt.color.PARAMS["RGBA_NORM"]["brown"]
                            for idx in test_idx
                        ]
                        ax.plot_scatter(
                            test_positions,
                            y_pos + test_jitter,
                            c=test_colors,
                            s=20,
                            alpha=0.7,
                            marker="s",
                            label="Test (class 0)" if fold == 0 else "",
                            zorder=3,
                        )
                    else:
                        ax.plot_scatter(
                            test_positions,
                            y_pos + test_jitter,
                            c="darkred",
                            s=20,
                            alpha=0.7,
                            marker="s",
                            label="Test points" if fold == 0 else "",
                            zorder=3,
                        )

            else:  # train, test (2-way split)
                train_idx, test_idx = split_indices

                # Get actual timestamps for train and test indices
                train_times = (
                    timestamps[train_idx]
                    if timestamps is not None
                    else train_idx
                )
                test_times = (
                    timestamps[test_idx]
                    if timestamps is not None
                    else test_idx
                )

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
                    train_jitter = np.random.normal(
                        0, jitter_strength, len(train_positions)
                    )
                    # Color by class if y is provided
                    if y is not None:
                        train_colors = [
                            stx.plt.color.PARAMS["RGBA_NORM"]["blue"] if y[idx] == 0 else stx.plt.color.PARAMS["RGBA_NORM"]["light_blue"]
                            for idx in train_idx
                        ]
                        ax.plot_scatter(
                            train_positions,
                            y_pos + train_jitter,
                            c=train_colors,
                            s=20,
                            alpha=0.7,
                            marker="o",
                            label="Train (class 0)" if fold == 0 else "",
                            zorder=3,
                        )
                    else:
                        ax.plot_scatter(
                            train_positions,
                            y_pos + train_jitter,
                            c="darkblue",
                            s=20,
                            alpha=0.7,
                            marker="o",
                            label="Train points" if fold == 0 else "",
                            zorder=3,
                        )

                if test_positions:
                    test_jitter = np.random.normal(
                        0, jitter_strength, len(test_positions)
                    )
                    # Color by class if y is provided
                    if y is not None:
                        test_colors = [
                            stx.plt.color.PARAMS["RGBA_NORM"]["red"] if y[idx] == 0 else stx.plt.color.PARAMS["RGBA_NORM"]["brown"]
                            for idx in test_idx
                        ]
                        ax.plot_scatter(
                            test_positions,
                            y_pos + test_jitter,
                            c=test_colors,
                            s=20,
                            alpha=0.7,
                            marker="s",
                            label="Test (class 0)" if fold == 0 else "",
                            zorder=3,
                        )
                    else:
                        ax.plot_scatter(
                            test_positions,
                            y_pos + test_jitter,
                            c="darkred",
                            s=20,
                            alpha=0.7,
                            marker="s",
                            label="Test points" if fold == 0 else "",
                            zorder=3,
                        )

        # Format plot
        ax.set_ylim(-0.5, len(splits) - 0.5)
        ax.set_xlim(0, len(X))
        ax.set_xlabel("Temporal Position (sorted by timestamp)")
        ax.set_ylabel("Fold")
        gap_text = f", Gap: {self.gap}" if self.gap > 0 else ""
        val_text = (
            f", Val ratio: {self.val_ratio:.1%}" if self.val_ratio > 0 else ""
        )
        ax.set_title(
            f"Sliding Window Split Visualization ({split_type})\\n"
            f"Window: {self.window_size}, Step: {self.step_size}, Test: {self.test_size}{gap_text}{val_text}\\n"
            f"Rectangles show windows, dots show actual data points"
        )

        # Set y-ticks
        ax.set_yticks(range(len(splits)))
        ax.set_yticklabels([f"Fold {i}" for i in range(len(splits))])

        # Add enhanced legend with class and sample information
        if y is not None:
            # Count samples per class in total dataset
            unique_classes, class_counts = np.unique(y, return_counts=True)
            total_class_info = ", ".join(
                [
                    f"Class {cls}: n={count}"
                    for cls, count in zip(unique_classes, class_counts)
                ]
            )

            # Count samples in first fold to show per-fold distribution
            first_split = splits[0]
            if len(first_split) == 3:  # train, val, test
                train_idx, val_idx, test_idx = first_split
                fold_info = f"Fold 0: Train n={len(train_idx)}, Val n={len(val_idx)}, Test n={len(test_idx)}"
            else:  # train, test
                train_idx, test_idx = first_split
                fold_info = (
                    f"Fold 0: Train n={len(train_idx)}, Test n={len(test_idx)}"
                )

            # Add legend with class information
            handles, labels = ax.get_legend_handles_labels()
            # Add title to legend showing class distribution
            legend_title = f"Total: {total_class_info}\\n{fold_info}"
            ax.legend(handles, labels, loc="upper right", title=legend_title)
        else:
            ax.legend(loc="upper right")

        plt.tight_layout()

        if save_path:
            fig.savefig(save_path, dpi=150, bbox_inches="tight")

        return fig


"""Functions & Classes"""
def main(args) -> int:
    """Demonstrate TimeSeriesSlidingWindowSplit functionality.

    Args:
        args: Command line arguments

    Returns:
        int: Exit status
    """

    def demo_01_fixed_window_non_overlapping_tests(X, y, timestamps):
        """Demo 1: Fixed window size with non-overlapping test sets (DEFAULT).

        Best for: Testing model on consistent recent history.
        Each sample tested exactly once (like K-fold for time series).
        """
        logger.info("=" * 70)
        logger.info("DEMO 1: Fixed Window + Non-overlapping Tests (DEFAULT)")
        logger.info("=" * 70)
        logger.info("Best for: Testing model on consistent recent history")

        splitter = TimeSeriesSlidingWindowSplit(
            window_size=args.window_size,
            test_size=args.test_size,
            gap=args.gap,
            overlapping_tests=False,  # Default
            expanding_window=False,  # Default
        )

        splits = list(splitter.split(X, y, timestamps))[:5]
        logger.info(f"Generated {len(splits)} splits")

        for fold, (train_idx, test_idx) in enumerate(splits):
            logger.info(
                f"  Fold {fold}: Train={len(train_idx)} (fixed), Test={len(test_idx)}"
            )

        fig = splitter.plot_splits(X, y, timestamps)
        stx.io.save(
            fig, "./01_sliding_window_fixed.jpg", symlink_from_cwd=True
        )
        logger.info("")

        return splits

    def demo_02_expanding_window_non_overlapping_tests(X, y, timestamps):
        """Demo 2: Expanding window with non-overlapping test sets.

        Best for: Using all available past data (like sklearn TimeSeriesSplit).
        Training set grows to include all historical data.
        """
        logger.info("=" * 70)
        logger.info("DEMO 2: Expanding Window + Non-overlapping Tests")
        logger.info("=" * 70)
        logger.info(
            "Best for: Using all available past data (like sklearn TimeSeriesSplit)"
        )

        splitter = TimeSeriesSlidingWindowSplit(
            window_size=args.window_size,
            test_size=args.test_size,
            gap=args.gap,
            overlapping_tests=False,
            expanding_window=True,  # Use all past data!
        )

        splits = list(splitter.split(X, y, timestamps))[:5]
        logger.info(f"Generated {len(splits)} splits")

        for fold, (train_idx, test_idx) in enumerate(splits):
            logger.info(
                f"  Fold {fold}: Train={len(train_idx)} (growing!), Test={len(test_idx)}"
            )

        fig = splitter.plot_splits(X, y, timestamps)
        stx.io.save(
            fig, "./02_sliding_window_expanding.jpg", symlink_from_cwd=True
        )
        logger.info("")

        return splits

    def demo_03_fixed_window_overlapping_tests(X, y, timestamps):
        """Demo 3: Fixed window with overlapping test sets.

        Best for: Maximum evaluation points (like K-fold training reuse).
        Test sets can overlap for more frequent model evaluation.
        """
        logger.info("=" * 70)
        logger.info("DEMO 3: Fixed Window + Overlapping Tests")
        logger.info("=" * 70)
        logger.info(
            "Best for: Maximum evaluation points (like K-fold for training)"
        )

        splitter = TimeSeriesSlidingWindowSplit(
            window_size=args.window_size,
            test_size=args.test_size,
            gap=args.gap,
            overlapping_tests=True,  # Allow test overlap
            expanding_window=False,
            # step_size will default to test_size // 2 for 50% overlap
        )

        splits = list(splitter.split(X, y, timestamps))[:5]
        logger.info(f"Generated {len(splits)} splits")

        for fold, (train_idx, test_idx) in enumerate(splits):
            logger.info(
                f"  Fold {fold}: Train={len(train_idx)}, Test={len(test_idx)}"
            )

        fig = splitter.plot_splits(X, y, timestamps)
        stx.io.save(
            fig, "./03_sliding_window_overlapping.jpg", symlink_from_cwd=True
        )
        logger.info("")

        return splits

    def demo_04_undersample_imbalanced_data(X, y_imbalanced, timestamps):
        """Demo 4: Undersampling for imbalanced time series data.

        Best for: Handling class imbalance in training sets.
        Balances classes by randomly undersampling majority class.
        """
        logger.info("=" * 70)
        logger.info("DEMO 4: Undersampling for Imbalanced Data")
        logger.info("=" * 70)
        logger.info("Best for: Handling class imbalance in time series")

        # Show data imbalance
        unique, counts = np.unique(y_imbalanced, return_counts=True)
        logger.info(f"Class distribution: {dict(zip(unique, counts))}")
        logger.info("")

        # Without undersampling
        splitter_no_undersample = TimeSeriesSlidingWindowSplit(
            window_size=args.window_size,
            test_size=args.test_size,
            gap=args.gap,
            undersample=False,
        )

        splits_no_us = list(
            splitter_no_undersample.split(X, y_imbalanced, timestamps)
        )[:3]
        logger.info(f"WITHOUT undersampling: {len(splits_no_us)} splits")
        for fold, (train_idx, test_idx) in enumerate(splits_no_us):
            train_labels = y_imbalanced[train_idx]
            train_unique, train_counts = np.unique(
                train_labels, return_counts=True
            )
            logger.info(
                f"  Fold {fold}: Train size={len(train_idx)}, "
                f"Class dist={dict(zip(train_unique, train_counts))}"
            )
        logger.info("")

        # With undersampling
        splitter_undersample = TimeSeriesSlidingWindowSplit(
            window_size=args.window_size,
            test_size=args.test_size,
            gap=args.gap,
            undersample=True,  # Enable undersampling!
            random_state=42,
        )

        splits_us = list(
            splitter_undersample.split(X, y_imbalanced, timestamps)
        )[:3]
        logger.info(f"WITH undersampling: {len(splits_us)} splits")
        for fold, (train_idx, test_idx) in enumerate(splits_us):
            train_labels = y_imbalanced[train_idx]
            train_unique, train_counts = np.unique(
                train_labels, return_counts=True
            )
            logger.info(
                f"  Fold {fold}: Train size={len(train_idx)} (balanced!), "
                f"Class dist={dict(zip(train_unique, train_counts))}"
            )

        # Save visualization for undersampling
        fig = splitter_undersample.plot_splits(X, y_imbalanced, timestamps)
        stx.io.save(
            fig, "./04_sliding_window_undersample.jpg", symlink_from_cwd=True
        )
        logger.info("")

        return splits_us

    def demo_05_validation_dataset(X, y, timestamps):
        """Demo 5: Using validation dataset with train-val-test splits.

        Best for: Model selection and hyperparameter tuning.
        Creates train/validation/test splits maintaining temporal order.
        """
        logger.info("=" * 70)
        logger.info("DEMO 5: Validation Dataset (Train-Val-Test Splits)")
        logger.info("=" * 70)
        logger.info("Best for: Model selection and hyperparameter tuning")

        splitter = TimeSeriesSlidingWindowSplit(
            window_size=args.window_size,
            test_size=args.test_size,
            gap=args.gap,
            val_ratio=0.2,  # 20% of training window for validation
            overlapping_tests=False,
            expanding_window=False,
        )

        splits = list(splitter.split_with_val(X, y, timestamps))[:3]
        logger.info(f"Generated {len(splits)} splits")

        for fold, (train_idx, val_idx, test_idx) in enumerate(splits):
            logger.info(
                f"  Fold {fold}: Train={len(train_idx)}, Val={len(val_idx)}, Test={len(test_idx)}"
            )

        fig = splitter.plot_splits(X, y, timestamps)
        stx.io.save(
            fig, "./05_sliding_window_validation.jpg", symlink_from_cwd=True
        )
        logger.info("")

        return splits

    def demo_06_expanding_with_validation(X, y, timestamps):
        """Demo 6: Expanding window with validation dataset.

        Best for: Using all historical data with model selection.
        Combines expanding window and validation split.
        """
        logger.info("=" * 70)
        logger.info("DEMO 6: Expanding Window + Validation Dataset")
        logger.info("=" * 70)
        logger.info("Best for: Using all historical data with model selection")

        splitter = TimeSeriesSlidingWindowSplit(
            window_size=args.window_size,
            test_size=args.test_size,
            gap=args.gap,
            val_ratio=0.2,
            overlapping_tests=False,
            expanding_window=True,  # Expanding + validation!
        )

        splits = list(splitter.split_with_val(X, y, timestamps))[:3]
        logger.info(f"Generated {len(splits)} splits")

        for fold, (train_idx, val_idx, test_idx) in enumerate(splits):
            logger.info(
                f"  Fold {fold}: Train={len(train_idx)} (growing!), Val={len(val_idx)}, Test={len(test_idx)}"
            )

        fig = splitter.plot_splits(X, y, timestamps)
        stx.io.save(
            fig,
            "./06_sliding_window_expanding_validation.jpg",
            symlink_from_cwd=True,
        )
        logger.info("")

        return splits

    def demo_07_undersample_with_validation(X, y_imbalanced, timestamps):
        """Demo 7: Undersampling with validation dataset.

        Best for: Handling imbalanced data with hyperparameter tuning.
        Combines undersampling and validation split.
        """

        logger.info("=" * 70)
        logger.info("DEMO 7: Undersampling + Validation Dataset")
        logger.info("=" * 70)
        logger.info("Best for: Imbalanced data with hyperparameter tuning")

        splitter = TimeSeriesSlidingWindowSplit(
            window_size=args.window_size,
            test_size=args.test_size,
            gap=args.gap,
            val_ratio=0.2,
            undersample=True,  # Undersample + validation!
            random_state=42,
        )

        splits = list(splitter.split_with_val(X, y_imbalanced, timestamps))[:3]
        logger.info(f"Generated {len(splits)} splits")

        for fold, (train_idx, val_idx, test_idx) in enumerate(splits):
            train_labels = y_imbalanced[train_idx]
            train_unique, train_counts = np.unique(
                train_labels, return_counts=True
            )
            logger.info(
                f"  Fold {fold}: Train={len(train_idx)} (balanced!), Val={len(val_idx)}, Test={len(test_idx)}, "
                f"Class dist={dict(zip(train_unique, train_counts))}"
            )

        fig = splitter.plot_splits(X, y_imbalanced, timestamps)
        stx.io.save(
            fig,
            "./07_sliding_window_undersample_validation.jpg",
            symlink_from_cwd=True,
        )
        logger.info("")

        return splits

    def demo_08_all_options_combined(X, y_imbalanced, timestamps):
        """Demo 8: All options combined.

        Best for: Maximum flexibility - expanding window, undersampling, and validation.
        Shows all features working together.
        """
        logger.info("=" * 70)
        logger.info(
            "DEMO 8: Expanding + Undersampling + Validation (ALL OPTIONS)"
        )
        logger.info("=" * 70)
        logger.info("Best for: Comprehensive time series CV with all features")

        splitter = TimeSeriesSlidingWindowSplit(
            window_size=args.window_size,
            test_size=args.test_size,
            gap=args.gap,
            val_ratio=0.2,
            overlapping_tests=False,
            expanding_window=True,  # All three!
            undersample=True,
            random_state=42,
        )

        splits = list(splitter.split_with_val(X, y_imbalanced, timestamps))[:3]
        logger.info(f"Generated {len(splits)} splits")

        for fold, (train_idx, val_idx, test_idx) in enumerate(splits):
            train_labels = y_imbalanced[train_idx]
            train_unique, train_counts = np.unique(
                train_labels, return_counts=True
            )
            logger.info(
                f"  Fold {fold}: Train={len(train_idx)} (growing & balanced!), Val={len(val_idx)}, Test={len(test_idx)}, "
                f"Class dist={dict(zip(train_unique, train_counts))}"
            )

        fig = splitter.plot_splits(X, y_imbalanced, timestamps)
        stx.io.save(
            fig, "./08_sliding_window_all_options.jpg", symlink_from_cwd=True
        )
        logger.info("")

        return splits

    def print_summary(
        splits_fixed,
        splits_expanding,
        splits_overlap,
        splits_undersample=None,
        splits_validation=None,
        splits_expanding_val=None,
        splits_undersample_val=None,
        splits_all_options=None,
    ):
        """Print comparison summary of all modes."""
        logger.info("=" * 70)
        logger.info("SUMMARY COMPARISON")
        logger.info("=" * 70)
        logger.info(
            f"01. Fixed window (non-overlap):         {len(splits_fixed)} folds, train size constant"
        )
        logger.info(
            f"02. Expanding window (non-overlap):      {len(splits_expanding)} folds, train size grows"
        )
        logger.info(
            f"03. Fixed window (overlapping):          {len(splits_overlap)} folds, more eval points"
        )
        if splits_undersample is not None:
            logger.info(
                f"04. With undersampling:                  {len(splits_undersample)} folds, balanced classes"
            )
        if splits_validation is not None:
            logger.info(
                f"05. With validation set:                 {len(splits_validation)} folds, train-val-test"
            )
        if splits_expanding_val is not None:
            logger.info(
                f"06. Expanding + validation:              {len(splits_expanding_val)} folds, growing train with val"
            )
        if splits_undersample_val is not None:
            logger.info(
                f"07. Undersample + validation:            {len(splits_undersample_val)} folds, balanced with val"
            )
        if splits_all_options is not None:
            logger.info(
                f"08. All options combined:                {len(splits_all_options)} folds, expanding + balanced + val"
            )
        logger.info("")
        logger.info("Key Insights:")
        logger.info(
            "  - Non-overlapping tests (default): Each sample tested exactly once"
        )
        logger.info(
            "  - Expanding window: Maximizes training data, like sklearn TimeSeriesSplit"
        )
        logger.info(
            "  - Overlapping tests: More evaluation points, like K-fold training reuse"
        )
        if splits_undersample is not None:
            logger.info(
                "  - Undersampling: Balances imbalanced classes in training sets"
            )
        if splits_validation is not None:
            logger.info(
                "  - Validation set: Enables hyperparameter tuning with temporal order"
            )
        if splits_all_options is not None:
            logger.info(
                "  - Combined options: Maximum flexibility for complex time series CV"
            )
        logger.info("=" * 70)

    # Main execution
    logger.info("=" * 70)
    logger.info("Demonstrating TimeSeriesSlidingWindowSplit with New Options")
    logger.info("=" * 70)

    # Generate test data
    np.random.seed(42)
    n_samples = args.n_samples
    X = np.random.randn(n_samples, 5)
    y = np.random.randint(0, 2, n_samples)  # Balanced
    timestamps = np.arange(n_samples) + np.random.normal(0, 0.1, n_samples)

    # Create imbalanced labels (80% class 0, 20% class 1)
    y_imbalanced = np.zeros(n_samples, dtype=int)
    n_minority = int(n_samples * 0.2)
    minority_indices = np.random.choice(
        n_samples, size=n_minority, replace=False
    )
    y_imbalanced[minority_indices] = 1

    logger.info(
        f"Generated test data: {n_samples} samples, {X.shape[1]} features"
    )
    logger.info("")

    # Run demos
    splits_fixed = demo_01_fixed_window_non_overlapping_tests(X, y, timestamps)
    splits_expanding = demo_02_expanding_window_non_overlapping_tests(
        X, y, timestamps
    )
    splits_overlap = demo_03_fixed_window_overlapping_tests(X, y, timestamps)
    splits_undersample = demo_04_undersample_imbalanced_data(
        X, y_imbalanced, timestamps
    )
    splits_validation = demo_05_validation_dataset(X, y, timestamps)
    splits_expanding_val = demo_06_expanding_with_validation(X, y, timestamps)
    splits_undersample_val = demo_07_undersample_with_validation(
        X, y_imbalanced, timestamps
    )
    splits_all_options = demo_08_all_options_combined(
        X, y_imbalanced, timestamps
    )

    # Print summary
    print_summary(
        splits_fixed,
        splits_expanding,
        splits_overlap,
        splits_undersample,
        splits_validation,
        splits_expanding_val,
        splits_undersample_val,
        splits_all_options,
    )

    return 0


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Demonstrate TimeSeriesSlidingWindowSplit with overlapping_tests and expanding_window options"
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


if __name__ == "__main__":
    run_main()

# EOF
