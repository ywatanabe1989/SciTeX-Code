#!/usr/bin/env python3
# -*- coding: utf-8 -*-
<<<<<<< HEAD
# Timestamp: "2025-07-14 13:52:58 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/ai/__init__.py
=======
# Timestamp: "2025-06-24 19:06:38 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/ai/__init__.py
>>>>>>> 6395efc4edb88c5cf39d9f55c6c44dfbc685a6fe
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/ai/__init__.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
"""Scitex AI module for machine learning and artificial intelligence utilities."""

from ._LearningCurveLogger import LearningCurveLogger
from .__Classifiers import Classifiers
from .classification_reporter import ClassificationReporter, MultiClassificationReporter
from .early_stopping import EarlyStopping
from .loss import MultiTaskLoss
# from .genai import GenAI
<<<<<<< HEAD
from ._gen_ai import GenAI
=======
from ._gen_ai import genai_factory as GenAI
>>>>>>> 6395efc4edb88c5cf39d9f55c6c44dfbc685a6fe
from .classification import ClassifierServer
from .optim import get_optimizer, set_optimizer

# Import submodules to make them accessible
from . import act
from . import classification
from . import clustering
from . import feature_extraction
# from . import genai
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
    "Classifiers",
    "LearningCurveLogger",
    "ClassificationReporter",
    "MultiClassificationReporter",
    "EarlyStopping",
    "MultiTaskLoss",
    "GenAI",
    "ClassifierServer",
    "get_optimizer",
    "set_optimizer",
    # Submodules
    "act",
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
