#!/usr/bin/env python3
"""Classification utilities with unified API."""

# Import the unified reporter - the only public API
from .reporters import ClassificationReporter

# Import other existing modules
from ._ClassifierServer import ClassifierServer
from .cross_validation import CrossValidationExperiment, quick_experiment

# Import time series module
from . import time_series

# Import time series CV utilities from submodule
from .time_series import (
    TimeSeriesStratifiedSplit,
    TimeSeriesBlockingSplit,
    TimeSeriesSlidingWindowSplit,
    TimeSeriesCalendarSplit,
    TimeSeriesStrategy,
    TimeSeriesMetadata,
)

# Backward compatibility alias
CVExperiment = CrossValidationExperiment

__all__ = [
    # Main reporter (unified API)
    "ClassificationReporter",
    # Classifier management
    "ClassifierServer",
    # Cross-validation
    "CrossValidationExperiment",
    "CVExperiment",  # Alias
    "quick_experiment",
    # Time series module
    "time_series",
    # Time series CV splitters (re-exported from time_series module)
    "TimeSeriesStratifiedSplit",
    "TimeSeriesBlockingSplit",
    "TimeSeriesSlidingWindowSplit",
    "TimeSeriesCalendarSplit",
    "TimeSeriesStrategy",
    "TimeSeriesMetadata",
]
