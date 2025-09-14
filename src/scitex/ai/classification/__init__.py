#!/usr/bin/env python3
"""Classification utilities."""

from ._MultiClassificationReporter import MultipleTasksClassificationReporter
from ._ClassifierServer import ClassifierServer


from ._SingleClassificationReporter import SingleTaskClassificationReporter
from .cross_validation import CrossValidationExperiment, quick_experiment

# Import reporter utilities
from . import reporter_utils

# Alias for convenience - users can use either name
ClassificationReporter = MultipleTasksClassificationReporter
SingleClassificationReporter = SingleTaskClassificationReporter

CVExperiment = CrossValidationExperiment

__all__ = [
    # Original reporters
    "SingleTaskClassificationReporter",
    "MultipleTasksClassificationReporter",
    "ClassificationReporter",
    "ClassifierServer",

    # New v2 system
    "SingleTaskClassificationReporter",
    "SingleClassificationReporter",  # Points to v2
    "CrossValidationExperiment",
    "CVExperiment",
    "quick_experiment",
    "reporter_utils"
]
