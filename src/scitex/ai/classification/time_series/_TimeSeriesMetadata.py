#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-21 20:48:00 (ywatanabe)"
# File: _TimeSeriesMetadata.py

"""
Time series metadata dataclass.

Stores comprehensive metadata about time series datasets for informed
cross-validation strategy selection.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Tuple, Any


@dataclass
class TimeSeriesMetadata:
    """
    Metadata about the time series data.
    
    This dataclass captures essential characteristics of time series data
    that inform the selection of appropriate cross-validation strategies.
    
    Attributes
    ----------
    n_samples : int
        Total number of samples in the dataset
    n_features : int
        Number of features per sample
    n_classes : Optional[int]
        Number of unique classes (None for regression)
    has_groups : bool
        Whether data contains group/subject identifiers
    group_sizes : Optional[Dict[Any, int]]
        Mapping of group IDs to their sample counts
    time_range : Optional[Tuple[float, float]]
        Minimum and maximum timestamp values
    sampling_rate : Optional[float]
        Samples per time unit (e.g., Hz for sensor data)
    has_gaps : bool
        Whether the time series has temporal gaps
    max_gap_size : Optional[float]
        Maximum gap between consecutive timestamps
    is_balanced : bool
        Whether classes are balanced (for classification)
    class_distribution : Optional[Dict[Any, float]]
        Mapping of class labels to their proportions
    
    Examples
    --------
    >>> import numpy as np
    >>> from scitex.ml.classification import TimeSeriesMetadata
    >>> 
    >>> # Create metadata for a dataset
    >>> metadata = TimeSeriesMetadata(
    ...     n_samples=1000,
    ...     n_features=10,
    ...     n_classes=2,
    ...     has_groups=True,
    ...     group_sizes={0: 250, 1: 250, 2: 250, 3: 250},
    ...     time_range=(0.0, 999.0),
    ...     sampling_rate=1.0,
    ...     has_gaps=False,
    ...     max_gap_size=None,
    ...     is_balanced=True,
    ...     class_distribution={0: 0.5, 1: 0.5}
    ... )
    >>> 
    >>> print(f"Dataset has {metadata.n_samples} samples")
    >>> print(f"Number of groups: {len(metadata.group_sizes) if metadata.group_sizes else 0}")
    """
    
    n_samples: int
    n_features: int
    n_classes: Optional[int] = None
    has_groups: bool = False
    group_sizes: Optional[Dict[Any, int]] = None
    time_range: Optional[Tuple[float, float]] = None
    sampling_rate: Optional[float] = None
    has_gaps: bool = False
    max_gap_size: Optional[float] = None
    is_balanced: bool = True
    class_distribution: Optional[Dict[Any, float]] = None
    
    def get_summary(self) -> str:
        """
        Generate human-readable summary of the metadata.
        
        Returns
        -------
        str
            Formatted summary string
        """
        lines = [
            f"Time Series Dataset Metadata:",
            f"  Samples: {self.n_samples}",
            f"  Features: {self.n_features}",
        ]
        
        if self.n_classes is not None:
            lines.append(f"  Classes: {self.n_classes}")
            if self.class_distribution:
                lines.append(f"  Class balance: {self.class_distribution}")
        
        if self.has_groups and self.group_sizes:
            n_groups = len(self.group_sizes)
            avg_size = sum(self.group_sizes.values()) / n_groups
            lines.append(f"  Groups: {n_groups} (avg size: {avg_size:.1f})")
        
        if self.time_range:
            duration = self.time_range[1] - self.time_range[0]
            lines.append(f"  Time range: {duration:.2f} units")
        
        if self.sampling_rate:
            lines.append(f"  Sampling rate: {self.sampling_rate:.2f} Hz")
        
        if self.has_gaps:
            lines.append(f"  Has gaps: Yes (max: {self.max_gap_size:.2f})")
        
        return "\n".join(lines)
    
    def suggest_strategy(self) -> str:
        """
        Suggest appropriate CV strategy based on metadata.
        
        Returns
        -------
        str
            Suggested strategy name
        """
        if self.has_groups:
            return "blocking"
        elif self.n_classes and not self.is_balanced:
            return "stratified"
        elif self.sampling_rate and self.sampling_rate > 10:
            return "sliding"  # High frequency data
        else:
            return "expanding"  # Default for simple time series