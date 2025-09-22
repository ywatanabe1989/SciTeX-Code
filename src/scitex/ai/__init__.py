#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-19 10:50:54 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/ai/__init__.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/ai/__init__.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
"""Scitex AI module for machine learning and artificial intelligence utilities."""

from .classification import ClassificationReporter
from .training._LearningCurveLogger import LearningCurveLogger
from .training._EarlyStopping import EarlyStopping
from .loss import MultiTaskLoss
from ._gen_ai import GenAI
from .classification import ClassifierServer
from .optim import get_optimizer, set_optimizer

# Import submodules to make them accessible
from . import activation
from . import classification
from . import clustering
from . import feature_extraction
from . import layer
from . import loss
from . import metrics
from . import optim
from . import plt
from . import sampling
from . import sklearn
from . import training
from . import utils

__all__ = [
    # "Classifiers",  # Moved to .old directory
    "LearningCurveLogger",
    "ClassificationReporter",
    "EarlyStopping",
    "MultiTaskLoss",
    "GenAI",
    "ClassifierServer",
    "get_optimizer",
    "set_optimizer",
    # Submodules
    "activation",
    "classification",
    "clustering",
    "feature_extraction",
    # "genai",
    "layer",
    "loss",
    "metrics",
    "optim",
    "plt",
    "sampling",
    "sklearn",
    "training",
    "utils",
]

# EOF
