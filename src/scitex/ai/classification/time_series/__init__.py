#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-21 20:45:00 (ywatanabe)"
# File: time_series/__init__.py

"""
Time series cross-validation utilities for classification.

This module provides specialized cross-validation strategies for time series data,
ensuring proper temporal ordering and preventing data leakage.
"""

# Import splitters
from ._TimeSeriesStratifiedSplit import TimeSeriesStratifiedSplit
from ._TimeSeriesBlockingSplit import TimeSeriesBlockingSplit
from ._TimeSeriesSlidingWindowSplit import TimeSeriesSlidingWindowSplit
from ._TimeSeriesCalendarSplit import TimeSeriesCalendarSplit

# Import metadata and strategy
from ._TimeSeriesStrategy import TimeSeriesStrategy
from ._TimeSeriesMetadata import TimeSeriesMetadata

# Import timestamp normalizer
from ._normalize_timestamp import normalize_timestamp

__all__ = [
    # Main time series CV splitters
    "TimeSeriesStratifiedSplit",
    "TimeSeriesBlockingSplit", 
    "TimeSeriesSlidingWindowSplit",
    "TimeSeriesCalendarSplit",
    
    # Support classes
    "TimeSeriesStrategy",
    "TimeSeriesMetadata",
    
    # Timestamp normalizer
    "normalize_timestamp",
]