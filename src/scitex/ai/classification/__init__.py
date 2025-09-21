#!/usr/bin/env python3
"""Classification utilities."""

# Import improved reporters (clean replacements)
from ._SingleClassificationReporter import SingleTaskClassificationReporter
from ._MultiClassificationReporter import (
    MultipleTasksClassificationReporter,
    create_multi_task_reporter,
)

# Import base classes and utilities
from ._BaseClassificationReporter import (
    BaseClassificationReporter,
    ReporterConfig,
)

# Import other existing modules
from ._ClassifierServer import ClassifierServer
from .cross_validation import CrossValidationExperiment, quick_experiment

# Import reporter utilities
from . import reporter_utils

# Import time series module
from . import time_series

# Import time series CV utilities from submodule
from .time_series import (
    TimeSeriesStratifiedSplit,
    TimeSeriesBlockingSplit,
    TimeSeriesSlidingWindowSplit,
    TimeSeriesStrategy,
    TimeSeriesMetadata,
)

# Backward compatibility aliases
ClassificationReporter = MultipleTasksClassificationReporter
SingleClassificationReporter = SingleTaskClassificationReporter

CVExperiment = CrossValidationExperiment

__all__ = [
    # Core reporters (improved versions)
    "SingleTaskClassificationReporter",
    "MultipleTasksClassificationReporter",
    "create_multi_task_reporter",
    # Base classes and configuration
    "BaseClassificationReporter",
    "ReporterConfig",
    # Aliases for convenience
    "ClassificationReporter",  # Alias for MultipleTasksClassificationReporter
    "SingleClassificationReporter",  # Alias for SingleTaskClassificationReporter
    # Classifier management
    "ClassifierServer",
    # Cross-validation
    "CrossValidationExperiment",
    "CVExperiment",  # Alias
    "quick_experiment",
    "reporter_utils",
    # Time series module
    "time_series",
    # Time series CV splitters (re-exported from time_series module)
    "TimeSeriesStratifiedSplit",
    "TimeSeriesBlockingSplit",
    "TimeSeriesSlidingWindowSplit",
    "TimeSeriesStrategy",
    "TimeSeriesMetadata",
]
