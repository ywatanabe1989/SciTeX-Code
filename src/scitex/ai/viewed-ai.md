4,982 lines & 13,608 words

# Repository View
#### Repository: `/data/gpfs/projects/punim2354/ywatanabe/SciTeX-Code/src/scitex/ai`
#### Output: `/data/gpfs/projects/punim2354/ywatanabe/SciTeX-Code/src/scitex/ai/viewed-ai.md`

## Configurations
##### Tree:
- Maximum depth: 3
- .gitignore respected
- Blacklist expresssions:
```plaintext
node_modules,.*,*.py[cod],__pycache__,*.elc,env,env-[0-9]*.[0-9]*,[1-2][0-9][0-9
][0-9]Y-*,htmlcov,*.sif,*.img,*.image,*.sandbox,*.log,logs,build,dist,*_back,*_b
ackup,*old*,.old,RUNNING,FINISHED
```

#### File content:
- Number of head: 50
- Whitelist extensions:
```plaintext
.txt,.md,.org,.el,.sh,.py,.yaml,.yml,.json,.def
```
- Blacklist expressions:
```plaintext
*.mat,*.npy,*.npz,*.csv,*.pkl,*.jpg,*.jpeg,*.mp4,*.pth,*.db*,*.out,*.err,*.cbm,*
.pt,*.egg-info,*.aux,*.pdf,*.png,*.tiff,*.wav
```


## Tree contents
.
├── activation
│   ├── _define.py
│   └── __init__.py
├── classification
│   ├── Classifier.py
│   ├── CrossValidationExperiment.py
│   ├── examples
│   │   └── timeseries_cv_demo.py
│   ├── __init__.py
│   ├── README.md
│   ├── reporters
│   │   ├── _BaseClassificationReporter.py
│   │   ├── _ClassificationReporter.py
│   │   ├── __init__.py
│   │   ├── _MultiClassificationReporter.py
│   │   └── _SingleClassificationReporter.py
│   └── timeseries
│       ├── __init__.py
│       ├── _normalize_timestamp.py
│       ├── README.md
│       ├── run_all.sh
│       ├── _TimeSeriesBlockingSplit.py
│       ├── _TimeSeriesCalendarSplit.py
│       ├── _TimeSeriesMetadata.py
│       ├── _TimeSeriesSlidingWindowSplit.py
│       ├── _TimeSeriesSlidingWindowSplit_v01-not-using-n_splits.py
│       ├── _TimeSeriesStrategy.py
│       └── _TimeSeriesStratifiedSplit.py
├── clustering
│   ├── __init__.py
│   ├── _pca.py
│   └── _umap.py
├── feature_extraction
│   ├── __init__.py
│   └── vit.py
├── _gen_ai
│   ├── _Anthropic.py
│   ├── _BaseGenAI.py
│   ├── _calc_cost.py
│   ├── _DeepSeek.py
│   ├── _format_output_func.py
│   ├── _genai_factory.py
│   ├── _Google.py
│   ├── _Groq.py
│   ├── __init__.py
│   ├── _Llama.py
│   ├── _OpenAI.py
│   ├── _PARAMS.py
│   └── _Perplexity.py
├── __init__.py
├── loss
│   ├── __init__.py
│   ├── _L1L2Losses.py
│   └── multi_task_loss.py
├── metrics
│   ├── _calc_bacc_from_conf_mat.py
│   ├── _calc_bacc.py
│   ├── _calc_clf_report.py
│   ├── _calc_conf_mat.py
│   ├── _calc_feature_importance.py
│   ├── _calc_mcc.py
│   ├── _calc_pre_rec_auc.py
│   ├── _calc_roc_auc.py
│   ├── _calc_seizure_prediction_metrics.py
│   ├── _calc_silhouette_score.py
│   ├── __init__.py
│   └── _normalize_labels.py
├── optim
│   ├── _get_set.py
│   ├── __init__.py
│   ├── MIGRATION.md
│   ├── _optimizers.py
│   └── Ranger_Deep_Learning_Optimizer
│       ├── __init__.py
│       ├── LICENSE
│       ├── ranger-init.jpg
│       ├── ranger-with-gc-options.jpg
│       ├── README.md
│       └── setup.py
├── plt
│   ├── __init__.py
│   ├── _plot_conf_mat.py
│   ├── _plot_feature_importance.py
│   ├── _plot_learning_curve.py
│   ├── _plot_optuna_study.py
│   ├── _plot_pre_rec_curve.py
│   └── _plot_roc_curve.py
├── README.md
├── sampling
│   └── undersample.py
├── sk
│   ├── _clf.py
│   ├── __init__.py
│   └── _to_sktime.py
├── sklearn
│   ├── clf.py
│   ├── __init__.py
│   └── to_sktime.py
├── training
│   ├── _EarlyStopping.py
│   ├── __init__.py
│   ├── _LearningCurveLogger.py
│   └── legacy
│       ├── early_stopping.py
│       └── learning_curve_logger.py
├── utils
│   ├── _check_params.py
│   ├── _default_dataset.py
│   ├── _format_samples_for_sktime.py
│   ├── grid_search.py
│   ├── __init__.py
│   ├── _label_encoder.py
│   ├── _merge_labels.py
│   ├── _sliding_window_data_augmentation.py
│   ├── _under_sample.py
│   └── _verify_n_gpus.py
└── viewed-ai.md


## File contents

### `./activation/_define.py`

```python
import torch.nn as nn


def define(act_str):
    acts_dict = {
        "relu": nn.ReLU(),
        "swish": nn.SiLU(),
        "mish": nn.Mish(),
        "lrelu": nn.LeakyReLU(0.1),
    }
    return acts_dict[act_str]

...
```


### `./activation/__init__.py`

```python
#!/usr/bin/env python3
"""Scitex act module."""

from ._define import define

__all__ = [
    "define",
]

...
```


### `./classification/Classifier.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-12-12 06:49:15 (ywatanabe)"
# File: ./scitex_repo/src/scitex/ai/Classifier.py

THIS_FILE = (
    "/data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/ai/Classifier.py"
)

"""
Functionality:
    * Provides a unified interface for initializing various scikit-learn classifiers
    * Supports optional preprocessing with StandardScaler

Input:
    * Classifier name as string
    * Optional class weights for imbalanced datasets
    * Optional scaler for feature preprocessing

Output:
    * Initialized classifier or pipeline with scaler

Prerequisites:
    * scikit-learn
    * Optional: CatBoost for CatBoostClassifier
"""

from typing import Dict, List, Optional, Union

from sklearn.base import BaseEstimator as _BaseEstimator
from sklearn.discriminant_analysis import (
    QuadraticDiscriminantAnalysis as _QuadraticDiscriminantAnalysis,
)
from sklearn.ensemble import AdaBoostClassifier as _AdaBoostClassifier
from sklearn.gaussian_process import (
    GaussianProcessClassifier as _GaussianProcessClassifier,
)
from sklearn.linear_model import LogisticRegression as _LogisticRegression
from sklearn.linear_model import (
    PassiveAggressiveClassifier as _PassiveAggressiveClassifier,
)
from sklearn.linear_model import Perceptron as _Perceptron
from sklearn.linear_model import RidgeClassifier as _RidgeClassifier
from sklearn.linear_model import SGDClassifier as _SGDClassifier
from sklearn.neighbors import KNeighborsClassifier as _KNeighborsClassifier
from sklearn.pipeline import Pipeline as _Pipeline
from sklearn.pipeline import make_pipeline as _make_pipeline
from sklearn.preprocessing import StandardScaler as _StandardScaler
from sklearn.svm import SVC as _SVC
from sklearn.svm import LinearSVC as _LinearSVC

...
```


### `./classification/CrossValidationExperiment.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-22 00:54:37 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/ml/classification/cross_validation.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Cross-validation helper for streamlined machine learning experiments.

Provides a high-level interface for running cross-validation with
automatic metric tracking, validation, and report generation.
"""

import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

import numpy as np
import pandas as pd
from sklearn.model_selection import BaseCrossValidator, StratifiedKFold

from .reporters import ClassificationReporter


class CrossValidationExperiment:
    """
    Streamlined cross-validation experiment runner.

    This class handles:
    - Cross-validation splitting
    - Model training and evaluation
    - Automatic metric calculation
    - Hyperparameter tracking
    - Progress monitoring
    - Report generation

    Parameters
    ----------
    name : str
        Experiment name
    model_fn : Callable
        Function that returns a model instance
    cv : BaseCrossValidator, optional
        Cross-validation splitter (default: 5-fold stratified)

...
```


### `./classification/examples/timeseries_cv_demo.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-21 20:20:00 (ywatanabe)"
# File: timeseries_cv_demo.py

"""
Examples demonstrating the time series cross-validation modules.

This script shows how to use:
1. Individual time series CV splitters
2. The intelligent TimeSeriesCVCoordinator
3. Integration with classification reporters
"""

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import balanced_accuracy_score
import matplotlib.pyplot as plt
from typing import List, Tuple


def generate_synthetic_timeseries(
    n_samples: int = 1000,
    n_features: int = 10,
    n_groups: int = None,
    noise_level: float = 0.1,
    imbalance_ratio: float = 0.5,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Generate synthetic time series data for demonstration.
    
    Returns
    -------
    X : Features
    y : Labels (binary)
    timestamps : Time points
    groups : Group labels (if n_groups specified)
    """
    np.random.seed(42)
    
    # Generate features with temporal correlation
    X = np.zeros((n_samples, n_features))
    for i in range(n_features):
        # AR(1) process with different parameters
        phi = 0.3 + i * 0.05  # Autocorrelation
        X[:, i] = np.random.randn(n_samples)
        for t in range(1, n_samples):
            X[t, i] = phi * X[t-1, i] + np.sqrt(1 - phi**2) * np.random.randn()

...
```


### `./classification/__init__.py`

```python
#!/usr/bin/env python3
"""Classification utilities with unified API."""

# Import reporters
from .reporters import ClassificationReporter, SingleTaskClassificationReporter

# Import other existing modules
from .Classifier import Classifier
from .CrossValidationExperiment import CrossValidationExperiment, quick_experiment

# Import time series module
from . import timeseries

# Import time series CV utilities from submodule
from .timeseries import (
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
    # Reporters
    "ClassificationReporter",
    "SingleTaskClassificationReporter",
    # Classifier management
    "Classifier",
    # Cross-validation
    "CrossValidationExperiment",
    "CVExperiment",  # Alias
    "quick_experiment",
    # Time series module
    "timeseries",
    # Time series CV splitters (re-exported from timeseries module)
    "TimeSeriesStratifiedSplit",
    "TimeSeriesBlockingSplit",
    "TimeSeriesSlidingWindowSplit",
    "TimeSeriesCalendarSplit",
    "TimeSeriesStrategy",
    "TimeSeriesMetadata",
]

...
```


### `./classification/README.md`

```markdown
# SciTeX Classification Module

A comprehensive classification module for scientific machine learning experiments with standardized reporting, validation, and publication-ready outputs.

## Overview

The classification module provides:
- **Modular reporter utilities** for metric calculation and storage
- **Single and multi-task classification reporters** with automatic file organization
- **Validation utilities** to ensure completeness and scientific rigor
- **Publication-ready exports** in multiple formats (CSV, LaTeX, Markdown)
- **Decoupled architecture** without hard dependencies on scitex.io

## Directory Structure

```
src/scitex/ai/classification/
├── __init__.py
├── README.md (this file)
├── _Classifiers.py              # Classifier implementations
├── Classifier.py          # Server for classifier services
├── _ClassificationReporter.py   # Base reporter class
├── _SingleClassificationReporter.py    # Single-task reporter
├── _MultiClassificationReporter.py     # Multi-task reporter
└── reporter_utils/              # Modular utilities
    ├── __init__.py
    ├── metrics.py               # Pure metric calculations
    ├── storage.py               # Standalone storage (no scitex.io dependency)
    ├── data_models.py           # Type-safe data models
    ├── validation.py            # Validation and completeness checks
    ├── aggregation.py           # Cross-fold aggregation
    └── reporting.py             # Report generation utilities
```

## Quick Start

### Basic Usage

```python
from scitex.ai.classification.reporter_utils import (
    calc_bacc,
    calc_mcc,
    MetricStorage,
    create_summary_table,
    generate_markdown_report
)

# Calculate metrics
ba = calc_bacc(y_true, y_pred, fold=0)
mcc = calc_mcc(y_true, y_pred, fold=0)
```

...
```


### `./classification/reporters/_BaseClassificationReporter.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-22 15:00:10 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/ml/classification/reporters/_BaseClassificationReporter.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Base Classification Reporter - Unified API Interface.

This module provides the base class and interface for all classification reporters,
ensuring consistent APIs and behavior across single-task and multi-task scenarios.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import numpy as np
from scitex import logging

logger = logging.getLogger(__name__)


class BaseClassificationReporter(ABC):
    """
    Abstract base class for all classification reporters.

    This class defines the unified API that all classification reporters must implement,
    ensuring consistent parameter names, method signatures, and behavior.

    Parameters
    ----------
    output_dir : Union[str, Path]
        Base directory for outputs. If None, creates timestamped directory.
    precision : int, default 3
        Number of decimal places for numerical outputs
    """

    def __init__(
        self,
        output_dir: Union[str, Path],
        precision: int = 3,
        verbose=True,
    ):
        self.precision = precision

...
```


### `./classification/reporters/_ClassificationReporter.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-02 06:38:58 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/ml/classification/reporters/_ClassificationReporter.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Unified Classification Reporter.

A single, unified reporter that handles both single-task and multi-task
classification scenarios seamlessly.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import numpy as np

# Import base class and single reporter for internal use
from ._BaseClassificationReporter import (BaseClassificationReporter,
                                          ReporterConfig)
from ._SingleClassificationReporter import SingleTaskClassificationReporter
from .reporter_utils.storage import MetricStorage


class ClassificationReporter(BaseClassificationReporter):
    """
    Unified classification reporter for single and multi-task scenarios.

    This reporter automatically adapts to your use case:
    - Single task: Just use it without specifying tasks
    - Multiple tasks: Specify tasks upfront or create them dynamically
    - Seamless switching between single and multi-task workflows

    Features:
    - Comprehensive metrics calculation (balanced accuracy, MCC, ROC-AUC, PR-AUC, etc.)
    - Automated visualization generation:
      * Confusion matrices
      * ROC and Precision-Recall curves
      * Feature importance plots (via plotter)
      * CV aggregation plots with faded fold lines
      * Comprehensive metrics dashboard
    - Multi-format report generation (Org, Markdown, LaTeX, HTML, DOCX, PDF)
    - Cross-validation support with automatic fold aggregation
    - Multi-task classification tracking

...
```


### `./classification/reporters/__init__.py`

```python
#!/usr/bin/env python3
"""Reporter implementations for classification."""

# Export the unified reporter and single-task reporter
from ._ClassificationReporter import ClassificationReporter
from ._SingleClassificationReporter import SingleTaskClassificationReporter

__all__ = [
    "ClassificationReporter",
    "SingleTaskClassificationReporter",
]
...
```


### `./classification/reporters/_MultiClassificationReporter.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-22 15:00:55 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/ml/classification/reporters/_MultiClassificationReporter.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Improved Multiple Tasks Classification Reporter with unified API.

Enhanced version that addresses all identified issues:
- Unified API interface matching SingleTaskClassificationReporter
- Lazy directory creation
- Numerical precision control
- Graceful plotting with error handling
- Consistent parameter names
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import numpy as np

# Import base class and improved single reporter
from ._BaseClassificationReporter import (BaseClassificationReporter,
                                          ReporterConfig)
from ._SingleClassificationReporter import SingleTaskClassificationReporter
from .reporter_utils.storage import MetricStorage


class MultipleTasksClassificationReporter(BaseClassificationReporter):
    """
    Improved multi-task classification reporter with unified API.

    This reporter manages multiple SingleTaskClassificationReporter instances,
    one for each target/task, providing a unified interface for multi-task scenarios.

    Key improvements:
    - Same API as SingleTaskClassificationReporter (calculate_metrics method)
    - Lazy directory creation (no empty folders)
    - Numerical precision control
    - Graceful plotting with proper error handling
    - Consistent parameter names across all methods

    Parameters
    ----------

...
```


### `./classification/reporters/_SingleClassificationReporter.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-03 01:21:52 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/ml/classification/reporters/_SingleClassificationReporter.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/ml/classification/reporters/_SingleClassificationReporter.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

__FILE__ = __file__

from pprint import pprint

"""
Improved Single Classification Reporter with unified API.

Enhanced version that addresses all identified issues:
- Unified API interface
- Lazy directory creation
- Numerical precision control
- Graceful plotting with error handling
- Consistent parameter names
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import numpy as np
import pandas as pd
from scitex.logging import getLogger

# Import base class and utilities
from ._BaseClassificationReporter import (BaseClassificationReporter,
                                          ReporterConfig)
# Import original metric calculation functions (these are good)
from .reporter_utils import (calc_bacc, calc_clf_report, calc_conf_mat,
                             calc_mcc, calc_pre_rec_auc, calc_roc_auc)
from .reporter_utils._Plotter import Plotter
from .reporter_utils.reporting import (create_summary_statistics,
                                       generate_latex_report,
                                       generate_markdown_report,
                                       generate_org_report)
from .reporter_utils.storage import MetricStorage, save_metric

logger = getLogger(__name__)


...
```


### `./classification/timeseries/__init__.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-21 20:45:00 (ywatanabe)"
# File: timeseries/__init__.py

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
...
```


### `./classification/timeseries/_normalize_timestamp.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-22 15:21:06 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/ml/classification/timeseries/_normalize_timestamp.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Timestamp Standardization Utilities

Functionality:
- Standardizes timestamps to consistent format defined in CONFIG.FORMATS.TIMESTAMP
- Handles various input formats (datetime objects, strings, timestamps)
- Provides UTC normalization
- Ensures consistent timestamp formatting across the codebase

Input formats supported:
- datetime objects (with or without timezone)
- Unix timestamps (int/float)
- Various string formats

Output:
- Standardized timestamp strings in format: "%Y-%m-%d %H:%M:%S.%f"
- UTC normalized timestamps
- Validation utilities

Prerequisites:
- CONFIG.FORMATS.TIMESTAMP for standard format
"""

"""Imports"""
import argparse
from datetime import datetime, timezone
from typing import Union

import scitex as stx

"""Parameters"""
# Default standard format if CONFIG not available
try:
    CONFIG = stx.io.load_configs()
    STANDARD_FORMAT = CONFIG.FORMATS.TIMESTAMP
except (AttributeError, ImportError):
    # Fallback to a sensible default
    STANDARD_FORMAT = "%Y-%m-%d %H:%M:%S.%f"


...
```


### `./classification/timeseries/README.md`

```markdown
# Time Series Cross-Validation Module

Production-ready time series cross-validation utilities with temporal integrity guarantees and enhanced visualizations.

## 🎯 Overview

This module provides specialized cross-validation strategies for time series data, ensuring:
- **Temporal order preservation** (no future data leakage)
- **Visual verification** with scatter plot overlays
- **SciTeX framework integration** for standalone testing
- **Support for multiple time series scenarios**
- **Calendar-aware splitting** with business logic
- **Robust timestamp handling** across formats

## 📊 Visual Comparison of Splitters

### TimeSeriesStratifiedSplit
```
Maintains class balance while preserving temporal order
Supports optional validation set between train and test

Without validation:              With validation (val_ratio=0.15):
Fold 0: [TTTTTTTTTT]    [SSS]   Fold 0: [TTTTTTTT]  [VV]  [SSS]
Fold 1: [TTTTTTTTTTTT]  [SSS]   Fold 1: [TTTTTTTTTT][VV]  [SSS]
Fold 2: [TTTTTTTTTTTTTT][SSS]   Fold 2: [TTTTTTTTTTTT][VV][SSS]
        └─ Expanding ─┘  Test            └─Expanding─┘ Val  Test
        
Legend: T=Train, V=Validation, S=teSt
```

### TimeSeriesSlidingWindowSplit
```
Fixed-size windows sliding through time
Optional validation carved from training window

Without validation:              With validation (val_ratio=0.2):
Fold 0: [TTTT]  [SS]            Fold 0: [TTT][V]  [SS]
Fold 1:    [TTTT]  [SS]         Fold 1:    [TTT][V]  [SS]
Fold 2:       [TTTT]  [SS]      Fold 2:       [TTT][V]  [SS]
        └─Win─┘ Gap └Test┘              └Train┘Val Gap└Test┘
        
Legend: T=Train, V=Validation, S=teSt, Gap=temporal separation
```

### TimeSeriesBlockingSplit
```
Multiple subjects with temporal separation per subject
Each subject gets its own train/val/test split

Without validation:                    With validation (val_ratio=0.15):
```

...
```


### `./classification/timeseries/run_all.sh`

```bash
#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-22 17:50:10 (ywatanabe)"
# File: ./src/scitex/ml/classification/timeseries/run_all.sh

THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
LOG_PATH="$THIS_DIR/.$(basename $0).log"
echo > "$LOG_PATH"

BLACK='\033[0;30m'
LIGHT_GRAY='\033[0;37m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo_info() { echo -e "${LIGHT_GRAY}$1${NC}"; }
echo_success() { echo -e "${GREEN}$1${NC}"; }
echo_warning() { echo -e "${YELLOW}$1${NC}"; }
echo_error() { echo -e "${RED}$1${NC}"; }
# ---------------------------------------

python -m  scitex.ml.classification.timeseries._TimeSeriesBlockingSplit
python -m  scitex.ml.classification.timeseries._TimeSeriesCalendarSplit
python -m  scitex.ml.classification.timeseries._TimeSeriesMetadata
python -m  scitex.ml.classification.timeseries._TimeSeriesSlidingWindowSplit
python -m  scitex.ml.classification.timeseries._TimeSeriesStrategy
python -m  scitex.ml.classification.timeseries._TimeSeriesStratifiedSplit

# EOF
...
```


### `./classification/timeseries/_TimeSeriesBlockingSplit.py`

```python
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

...
```


### `./classification/timeseries/_TimeSeriesCalendarSplit.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-22 17:15:00 (ywatanabe)"
# File: _TimeSeriesCalendarSplit.py

__FILE__ = "_TimeSeriesCalendarSplit.py"

"""
Functionalities:
  - Implements calendar-based time series cross-validation
  - Splits data based on calendar intervals (monthly, weekly, daily)
  - Ensures temporal order preservation with no data leakage
  - Supports flexible interval definitions (D, W, M, Q, Y)
  - Provides visualization with scatter plots showing actual data points
  - Useful for financial data, sales forecasting, seasonal patterns

Dependencies:
  - packages:
    - numpy
    - pandas
    - sklearn
    - matplotlib
    - scitex

IO:
  - input-files:
    - None (generates synthetic calendar-based data for demonstration)
  - output-files:
    - ./calendar_splits_demo.png (visualization with scatter plots)
"""

"""Imports"""
import os
import sys
import argparse
import numpy as np
import pandas as pd
from typing import Iterator, Optional, Tuple, Union, Literal
from sklearn.model_selection import BaseCrossValidator
from sklearn.utils.validation import _num_samples
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import scitex as stx
from scitex import logging

# Import timestamp normalizer (internally uses to_datetime helper)
from ._normalize_timestamp import normalize_timestamp, to_datetime

logger = logging.getLogger(__name__)


...
```


### `./classification/timeseries/_TimeSeriesMetadata.py`

```python
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

...
```


### `./classification/timeseries/_TimeSeriesSlidingWindowSplit.py`

```python
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


...
```


### `./classification/timeseries/_TimeSeriesSlidingWindowSplit_v01-not-using-n_splits.py`

```python
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


...
```


### `./classification/timeseries/_TimeSeriesStrategy.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-21 20:45:00 (ywatanabe)"
# File: _TimeSeriesStrategy.py

"""
Time series cross-validation strategy enumeration.

Defines available strategies for time series CV.
"""

from enum import Enum


class TimeSeriesStrategy(Enum):
    """
    Available time series CV strategies.
    
    Attributes
    ----------
    STRATIFIED : str
        Single time series with class balance preservation
    BLOCKING : str
        Multiple independent time series (e.g., different patients)
    SLIDING : str
        Sliding window approach with fixed-size windows
    EXPANDING : str
        Expanding window where training set grows over time
    FIXED : str
        Fixed train/test split at specific time point
    """
    
    STRATIFIED = "stratified"  # Single time series with class balance
    BLOCKING = "blocking"  # Multiple time series (e.g., patients)
    SLIDING = "sliding"  # Sliding window approach
    EXPANDING = "expanding"  # Expanding window (train grows)
    FIXED = "fixed"  # Fixed train/test split
    
    @classmethod
    def from_string(cls, value: str) -> 'TimeSeriesStrategy':
        """
        Create strategy from string value.
        
        Parameters
        ----------
        value : str
            String representation of strategy
            
        Returns
        -------

...
```


### `./classification/timeseries/_TimeSeriesStratifiedSplit.py`

```python
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

...
```


### `./clustering/__init__.py`

```python
#!/usr/bin/env python3
"""Scitex clustering module."""

from ._pca import pca
from ._umap import main, umap

__all__ = [
    "main",
    "pca",
    "umap",
]

...
```


### `./clustering/_pca.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-05-14 00:58:26 (ywatanabe)"

import matplotlib.pyplot as plt
import scitex
import numpy as np
import seaborn as sns
from natsort import natsorted
from sklearn.decomposition import PCA
from sklearn.preprocessing import LabelEncoder


def pca(
    data_all,
    labels_all,
    axes_titles=None,
    title="PCA Clustering",
    alpha=0.1,
    s=3,
    use_independent_legend=False,
    add_super_imposed=False,
    palette="viridis",
):

    assert len(data_all) == len(labels_all)

    if isinstance(data_all, list):
        data_all = list(data_all)
        labels_all = list(labels_all)

    le = LabelEncoder()
    # le.fit(np.hstack(labels_all))
    le.fit(natsorted(np.hstack(labels_all)))
    labels_all = [le.transform(labels) for labels in labels_all]

    pca_model = PCA(n_components=2)

    ncols = len(data_all) + 1 if add_super_imposed else len(data_all)
    share = True if ncols > 1 else False
    fig, axes = plt.subplots(ncols=ncols, sharex=share, sharey=share)

    fig.suptitle(title)
    fig.supxlabel("PCA 1")
    fig.supylabel("PCA 2")

    for ii, (data, labels) in enumerate(zip(data_all, labels_all)):
        if ii == 0:
            _pca = pca_model.fit(data)
            embedding = _pca.transform(data)

...
```


### `./clustering/_umap.py`

```python
#!./env/bin/python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-09-12 05:37:55 (ywatanabe)"
# _umap_dev.py


"""
This script does XYZ.
"""


"""
Imports
"""
import sys

import matplotlib.pyplot as plt
import scitex
import numpy as np
import umap.umap_ as umap_orig
from natsort import natsorted
from sklearn.preprocessing import LabelEncoder

# sys.path = ["."] + sys.path
# from scripts import utils, load

"""
Warnings
"""
# warnings.simplefilter("ignore", UserWarning)


"""
Config
"""
# CONFIG = scitex.gen.load_configs()


"""
Functions & Classes
"""


def umap(
    data,
    labels,
    hues=None,
    hues_colors=None,
    axes=None,
    axes_titles=None,

...
```


### `./feature_extraction/__init__.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-20 10:53:22 (ywatanabe)"
# File: ./scitex_repo/src/scitex/ai/feature_extraction/__init__.py

THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/ai/feature_extraction/__init__.py"

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-10-22 19:51:47 (ywatanabe)"
# File: __init__.py

import os as __os
import importlib as __importlib
import inspect as __inspect
import warnings as __warnings

# Get the current directory
current_dir = __os.path.dirname(__file__)

# Iterate through all Python files in the current directory
for filename in __os.listdir(current_dir):
    if filename.endswith(".py") and not filename.startswith("__"):
        module_name = filename[:-3]  # Remove .py extension
        try:
            module = __importlib.import_module(f".{module_name}", package=__name__)
            
            # Import only functions and classes from the module
            for name, obj in __inspect.getmembers(module):
                if __inspect.isfunction(obj) or __inspect.isclass(obj):
                    if not name.startswith("_"):
                        globals()[name] = obj
        except ImportError as e:
            # Warn about modules that couldn't be imported due to missing dependencies
            __warnings.warn(
                f"Could not import {module_name} from scitex.ai.feature_extraction: {str(e)}. "
                f"Some functionality may be unavailable. "
                f"Consider installing missing dependencies if you need this module.",
                ImportWarning,
                stacklevel=2
            )

# Clean up temporary variables
del __os, __importlib, __inspect, __warnings, current_dir
if 'filename' in locals():
    del filename
if 'module_name' in locals():
    del module_name
if 'module' in locals():
    del module

...
```


### `./feature_extraction/vit.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-27 21:36:51 (ywatanabe)"
# File: ./scitex_repo/src/scitex/ai/feature_extraction/vit.py

THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/ai/feature_extraction/vit.py"

"""
Functionality:
    Extracts features from images using Vision Transformer (ViT) models
Input:
    Image arrays of arbitrary dimensions
Output:
    Feature vectors (1000-dimensional embeddings)
Prerequisites:
    torch, PIL, torchvision
"""

import os as _os
from typing import Tuple, Union

import torch
import torch as _torch
import numpy as np
from pytorch_pretrained_vit import ViT
from torchvision import transforms as _transforms

# from ...decorators import batch_torch_fn


def _setup_device(device: Union[str, None]) -> str:
    if device is None:
        device = "cuda" if _torch.cuda.is_available() else "cpu"
    return device


class VitFeatureExtractor:
    def __init__(
        self,
        model_name="B_16",
        torch_home="./models",
        device=None,
    ):
        self.valid_models = [
            "B_16",
            "B_32",
            "L_16",
            "L_32",
            "B_16_imagenet1k",
            "B_32_imagenet1k",

...
```


### `./_gen_ai/_Anthropic.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-24 19:20:24 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/ai/_gen_ai/_Anthropic.py
# ----------------------------------------
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionality:
    - Implements Anthropic AI (Claude) interface
    - Handles both streaming and static text generation
Input:
    - User prompts and chat history
    - Model configurations and API credentials
Output:
    - Generated text responses from Claude models
    - Token usage statistics
Prerequisites:
    - Anthropic API key (ANTHROPIC_API_KEY environment variable)
    - anthropic package
"""

"""Imports"""
import sys
from typing import Dict, Generator, List, Optional

import anthropic
import matplotlib.pyplot as plt

from ._BaseGenAI import BaseGenAI

"""Functions & Classes"""
class Anthropic(BaseGenAI):
    def __init__(
        self,
        system_setting: str = "",
        api_key: Optional[str] = os.getenv("ANTHROPIC_API_KEY"),
        model: str = "claude-3-opus-20240229",
        stream: bool = False,
        seed: Optional[int] = None,
        n_keep: int = 1,
        temperature: float = 1.0,
        chat_history: Optional[List[Dict[str, str]]] = None,
        max_tokens: int = 100_000,
    ) -> None:

        if model == "claude-3-7-sonnet-2025-0219":

...
```


### `./_gen_ai/_BaseGenAI.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-03 11:55:54 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/ai/_gen_ai/_BaseGenAI.py
# ----------------------------------------
import os

__FILE__ = "./src/scitex/ai/_gen_ai/_BaseGenAI.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import base64
import sys
from abc import ABC, abstractmethod
from typing import Any, Dict, Generator, List, Optional, Union

import matplotlib.pyplot as plt
import numpy as np

from ...io._load import load
from ._calc_cost import calc_cost
from ._format_output_func import format_output_func
from ._PARAMS import MODELS


class BaseGenAI(ABC):
    def __init__(
        self,
        system_setting: str = "",
        model: str = "",
        api_key: str = "",
        stream: bool = False,
        seed: Optional[int] = None,
        n_keep: int = 1,
        temperature: float = 1.0,
        provider: str = "",
        chat_history: Optional[List[Dict[str, str]]] = None,
        max_tokens: int = 4_096,
    ) -> None:
        self.provider = provider
        self.system_setting = system_setting
        self.model = model
        self.api_key = api_key
        self.stream = stream
        self.seed = seed
        self.n_keep = n_keep
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.input_tokens = 0
        self.output_tokens = 0

...
```


### `./_gen_ai/_calc_cost.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-04 01:37:36 (ywatanabe)"
# File: ./scitex_repo/src/scitex/ai/_gen_ai/_calc_cost.py

"""
Functionality:
    - Calculates usage costs for AI model API calls
    - Handles token-based pricing for different models
Input:
    - Model name
    - Number of input and output tokens used
Output:
    - Total cost in USD based on token usage
Prerequisites:
    - MODELS parameter dictionary with pricing information
    - pandas package
"""

from typing import Union, Any
import pandas as pd

from ._PARAMS import MODELS


def calc_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """Calculates API usage cost based on token count.

    Example
    -------
    >>> cost = calc_cost("gpt-4", 100, 50)
    >>> print(f"${cost:.4f}")
    $0.0030

    Parameters
    ----------
    model : str
        Name of the AI model
    input_tokens : int
        Number of input tokens used
    output_tokens : int
        Number of output tokens used

    Returns
    -------
    float
        Total cost in USD

    Raises
    ------

...
```


### `./_gen_ai/_DeepSeek.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-08 20:33:49 (ywatanabe)"
# File: ./scitex_repo/src/scitex/ai/_gen_ai/_DeepSeek.py

"""
1. Functionality:
   - Implements DeepSeek Code LLM API interface
2. Input:
   - Text prompts for code generation
3. Output:
   - Generated code responses (streaming or static)
4. Prerequisites:
   - DEEPSEEK_API_KEY environment variable
   - requests library
"""

"""Imports"""
import json
import os
import sys
from typing import Dict, Generator, List, Optional

import scitex
import requests

from ._BaseGenAI import BaseGenAI

"""Warnings"""
# scitex.pd.ignore_SettingWithCopyWarning()
# warnings.simplefilter("ignore", UserWarning)
# with warnings.catch_warnings():
#     warnings.simplefilter("ignore", UserWarning)

"""Parameters"""
# from scitex.io import load_configs
# CONFIG = load_configs()

"""Functions & Classes"""
from openai import OpenAI as _OpenAI

"""Functions & Classes"""


class DeepSeek(BaseGenAI):
    def __init__(
        self,
        system_setting="",
        model="deepseek-chat",
        api_key="",

...
```


### `./_gen_ai/_format_output_func.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-04 01:39:25 (ywatanabe)"
# File: ./scitex_repo/src/scitex/ai/_gen_ai/_format_output_func.py

"""
Functionality:
    - Formats AI model output text
    - Wraps URLs in HTML anchor tags
    - Converts markdown to HTML
    - Handles DOI links specially
Input:
    - Raw text output from AI models
    - Optional API key for masking
Output:
    - Formatted HTML text with proper link handling
Prerequisites:
    - markdown2 package
    - Regular expressions support
"""

"""Imports"""
import re
import sys
from typing import List, Optional

import markdown2
import matplotlib.pyplot as plt
import scitex

"""Functions & Classes"""


def format_output_func(out_text: str) -> str:
    """Formats AI output text with proper link handling and markdown conversion.

    Example
    -------
    >>> text = "Check https://example.com or doi:10.1234/abc"
    >>> print(format_output_func(text))
    Check <a href="https://example.com">https://example.com</a> or <a href="https://doi.org/10.1234/abc">https://doi.org/10.1234/abc</a>

    Parameters
    ----------
    out_text : str
        Raw text output from AI model

    Returns
    -------
    str

...
```


### `./_gen_ai/_genai_factory.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-03 11:57:10 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/ai/_gen_ai/_genai_factory.py
# ----------------------------------------
import os

__FILE__ = "./src/scitex/ai/_gen_ai/_genai_factory.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import random

from ._Anthropic import Anthropic
from ._DeepSeek import DeepSeek
from ._Google import Google
from ._Groq import Groq
from ._Llama import Llama
from ._OpenAI import OpenAI
from ._PARAMS import MODELS
from ._Perplexity import Perplexity


def genai_factory(
    model="gpt-3.5-turbo",
    stream=False,
    api_key=None,
    seed=None,
    temperature=1.0,
    n_keep=1,
    chat_history=None,
    max_tokens=4096,
):
    """Factory function to create an instance of an AI model handler."""
    AVAILABLE_MODELS = MODELS.name.tolist()

    if model not in AVAILABLE_MODELS:
        raise ValueError(
            f'Model "{model}" is not available. Please choose from:{MODELS.name.tolist()}'
        )

    provider = MODELS[MODELS.name == model].provider.iloc[0]

    # model_class = globals()[provider]
    model_class = {
        "OpenAI": OpenAI,
        "Anthropic": Anthropic,
        "Google": Google,
        "Llama": Llama,
        "Perplexity": Perplexity,

...
```


### `./_gen_ai/_Google.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-02-06 13:47:23 (ywatanabe)"
# File: _Google.py

THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/ai/_gen_ai/_Google.py"


"""
Functionality:
    - Implements Google's Generative AI (Gemini) interface
    - Handles both streaming and static text generation
Input:
    - User prompts and chat history
    - Model configurations and API credentials
Output:
    - Generated text responses from Gemini models
    - Token usage statistics
Prerequisites:
    - Google API key (GOOGLE_API_KEY environment variable)
    - google.generativeai package
"""

"""Imports"""
import os
import sys
from pprint import pprint
from typing import Any, Dict, Generator, List, Optional

import matplotlib.pyplot as plt
import scitex

try:
    from google import genai
except ImportError:
    genai = None

from ._BaseGenAI import BaseGenAI

"""Functions & Classes"""


class Google(BaseGenAI):
    def __init__(
        self,
        system_setting: str = "",
        api_key: Optional[str] = os.getenv("GOOGLE_API_KEY"),
        model: str = "gemini-1.5-pro-latest",
        stream: bool = False,
        seed: Optional[int] = None,

...
```


### `./_gen_ai/_Groq.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-28 02:47:54 (ywatanabe)"
# File: ./scitex_repo/src/scitex/ai/_gen_ai/_Groq.py

THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/ai/_gen_ai/_Groq.py"

"""
Functionality:
    - Implements GLOQ AI interface
    - Handles both streaming and static text generation
Input:
    - User prompts and chat history
    - Model configurations and API credentials
Output:
    - Generated text responses
    - Token usage statistics
Prerequisites:
    - GLOQ API key (GLOQ_API_KEY environment variable)
    - gloq package
"""

"""Imports"""
import os
import sys
from typing import Any, Dict, Generator, List, Optional, Union

from groq import Groq as _Groq
import matplotlib.pyplot as plt

from ._BaseGenAI import BaseGenAI

"""Functions & Classes"""


class Groq(BaseGenAI):
    def __init__(
        self,
        system_setting: str = "",
        api_key: Optional[str] = os.getenv("GROQ_API_KEY"),
        model: str = "llama3-8b-8192",
        stream: bool = False,
        seed: Optional[int] = None,
        n_keep: int = 1,
        temperature: float = 0.5,
        chat_history: Optional[List[Dict[str, str]]] = None,
        max_tokens: int = 8000,
    ) -> None:
        max_tokens = min(max_tokens, 8000)
        if not api_key:

...
```


### `./_gen_ai/__init__.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-14 13:51:57 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/ai/_gen_ai/__init__.py
# ----------------------------------------
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
#!./env/bin/python3
# Time-stamp: "2024-07-29 14:55:00 (ywatanabe)"
# /home/ywatanabe/proj/scitex/src/scitex/ml/_gen_ai/__init__.py

from ._PARAMS import MODELS
from ._BaseGenAI import BaseGenAI
from ._Anthropic import Anthropic
from ._DeepSeek import DeepSeek
from ._Google import Google
from ._Groq import Groq
from ._Llama import Llama
from ._OpenAI import OpenAI
from ._Perplexity import Perplexity
from ._calc_cost import calc_cost
from ._format_output_func import format_output_func
from ._genai_factory import genai_factory as GenAI

__all__ = [
    "GenAI"
    # "MODELS",
    # "BaseGenAI",
    # "Anthropic",
    # "DeepSeek",
    # "Google",
    # "Groq",
    # "Llama",
    # "OpenAI",
    # "Perplexity",
    # "calc_cost",
    # "format_output_func",
    # "genai_factory",
]

# EOF

...
```


### `./_gen_ai/_Llama.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-05 21:11:08 (ywatanabe)"
# File: ./scitex_repo/src/scitex/ai/_gen_ai/_Llama.py

"""Imports"""
import os
import sys
from typing import List, Optional

import matplotlib.pyplot as plt
import scitex

try:
    from llama import Dialog
    from llama import Llama as _Llama
except:
    pass

from ._BaseGenAI import BaseGenAI

"""Functions & Classes"""


def print_envs():
    settings = {
        "MASTER_ADDR": os.getenv("MASTER_ADDR", "localhost"),
        "MASTER_PORT": os.getenv("MASTER_PORT", "12355"),
        "WORLD_SIZE": os.getenv("WORLD_SIZE", "1"),
        "RANK": os.getenv("RANK", "0"),
    }

    print("Environment Variable Settings:")
    for key, value in settings.items():
        print(f"{key}: {value}")
    print()


class Llama(BaseGenAI):
    def __init__(
        self,
        ckpt_dir: str = "",
        tokenizer_path: str = "",
        system_setting: str = "",
        model: str = "Meta-Llama-3-8B",
        max_seq_len: int = 32_768,
        max_batch_size: int = 4,
        max_gen_len: Optional[int] = None,
        stream: bool = False,
        seed: Optional[int] = None,

...
```


### `./_gen_ai/_OpenAI.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-01-22 01:21:11 (ywatanabe)"
# File: _OpenAI.py

THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/ai/_gen_ai/_OpenAI.py"


"""Imports"""
import os
from openai import OpenAI as _OpenAI
from ._BaseGenAI import BaseGenAI

"""Functions & Classes"""


class OpenAI(BaseGenAI):
    def __init__(
        self,
        system_setting="",
        model="",
        api_key=os.getenv("OPENAI_API_KEY"),
        stream=False,
        seed=None,
        n_keep=1,
        temperature=1.0,
        chat_history=None,
        max_tokens=None,
    ):
        self.passed_model = model

        # import scitex
        # scitex.str.print_debug()
        # scitex.gen.printc(model)

        if model.startswith("o"):
            for reasoning_effort in ["low", "midium", "high"]:
                model = model.replace(f"-{reasoning_effort}", "")

        # Set max_tokens based on model
        if max_tokens is None:
            if "gpt-4-turbo" in model:
                max_tokens = 128_000
            elif "gpt-4" in model:
                max_tokens = 8_192
            elif "gpt-3.5-turbo-16k" in model:
                max_tokens = 16_384
            elif "gpt-3.5" in model:
                max_tokens = 4_096
            else:

...
```


### `./_gen_ai/_PARAMS.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-30 06:38:18 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/ai/_gen_ai/_PARAMS.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/ai/_gen_ai/PARAMS.py"

import pandas as pd

# https://api-docs.deepseek.com/quick_start/pricing
DEEPSEEK_MODELS = [
    {
        "name": "deepseek-reasoner",
        "input_cost": 0.14,
        "output_cost": 2.19,
        "api_key_env": "DEEPSEEK_API_KEY",
        "provider": "DeepSeek",
    },
    {
        "name": "deepseek-chat",
        "input_cost": 0.014,
        "output_cost": 0.28,
        "api_key_env": "DEEPSEEK_API_KEY",
        "provider": "DeepSeek",
    },
    {
        "name": "deepseek-coder",
        "input_cost": 0.014,
        "output_cost": 0.28,
        "api_key_env": "DEEPSEEK_API_KEY",
        "provider": "DeepSeek",
    },
]

# https://openai.com/api/pricing/
OPENAI_MODELS = [
    # o3
    {
        "name": "o3",
        "input_cost": 10.00,
        "output_cost": 40.00,
        "api_key_env": "OPENAI_API_KEY",
        "provider": "OpenAI",
    },

...
```


### `./_gen_ai/_Perplexity.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-11 04:11:10 (ywatanabe)"
# File: ./scitex_repo/src/scitex/ai/_gen_ai/_Perplexity.py

"""
Functionality:
    - Implements Perplexity AI interface using OpenAI-compatible API
    - Provides access to Llama and Mixtral models
Input:
    - User prompts and chat history
    - Model configurations and API credentials
Output:
    - Generated text responses from Perplexity models
    - Token usage statistics
Prerequisites:
    - Perplexity API key
    - openai package
"""

"""Imports"""
import os
import sys
from pprint import pprint
from typing import Dict, Generator, List, Optional

import matplotlib.pyplot as plt
from openai import OpenAI

from ._BaseGenAI import BaseGenAI

"""Functions & Classes"""


class Perplexity(BaseGenAI):
    def __init__(
        self,
        system_setting: str = "",
        model: str = "",
        api_key: str = "",
        stream: bool = False,
        seed: Optional[int] = None,
        n_keep: int = 1,
        temperature: float = 1.0,
        chat_history: Optional[List[Dict[str, str]]] = None,
        max_tokens: Optional[int] = None,  # Added parameter
    ) -> None:
        # Set max_tokens based on model if not provided
        if max_tokens is None:
            max_tokens = 128_000 if "128k" in model else 32_000

...
```


### `./__init__.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-19 10:50:54 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/ai/__init__.py
# ----------------------------------------
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
"""Scitex AI module for machine learning and artificial intelligence utilities."""

# Lazy imports to avoid loading heavy dependencies eagerly
from .classification import ClassificationReporter
from .training._LearningCurveLogger import LearningCurveLogger
from .training._EarlyStopping import EarlyStopping
from .loss import MultiTaskLoss
from .classification import Classifier
from .optim import get_optimizer, set_optimizer

# Import submodules to make them accessible
from . import activation
from . import classification
from . import clustering
from . import feature_extraction
# from . import layer
from . import loss
from . import metrics
from . import optim
from . import plt
from . import sampling
from . import sklearn
from . import training
from . import utils

# Lazy import for GenAI (heavy anthropic dependency)
def __getattr__(name):
    if name == "GenAI":
        from ._gen_ai import GenAI
        return GenAI
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    # "Classifiers",  # Moved to .old directory
    "LearningCurveLogger",
    "ClassificationReporter",
    "EarlyStopping",
    "MultiTaskLoss",
    "GenAI",  # Lazy loaded
    "Classifier",
    "get_optimizer",

...
```


### `./loss/__init__.py`

```python
#!/usr/bin/env python3
"""Scitex loss module."""

from ._L1L2Losses import elastic, l1, l2
from .multi_task_loss import MultiTaskLoss

__all__ = [
    "elastic",
    "l1",
    "l2",
    "MultiTaskLoss",
]

...
```


### `./loss/_L1L2Losses.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-07 18:53:03 (ywatanabe)"
# File: ./scitex_repo/src/scitex/ai/loss/_L1L2Losses.py

import torch


def l1(model, lambda_l1=0.01):
    lambda_l1 = torch.tensor(lambda_l1)
    l1 = torch.tensor(0.0).cuda()
    for param in model.parameters():  # fixme; is this OK?
        l1 += torch.abs(param).sum()
    return l1


def l2(model, lambda_l2=0.01):
    lambda_l2 = torch.tensor(lambda_l2)
    l2 = torch.tensor(0.0).cuda()
    for param in model.parameters():  # fixme; is this OK?
        l2 += torch.norm(param).sum()
    return l2


def elastic(model, alpha=1.0, l1_ratio=0.5):
    assert 0 <= l1_ratio <= 1

    L1 = l1(model)
    L2 = l2(model)

    return alpha * (l1_ratio * L1 + (1 - l1_ratio) * L2)


# EOF

...
```


### `./loss/multi_task_loss.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-07 19:07:29 (ywatanabe)"
# File: ./scitex_repo/src/scitex/ai/loss/MultiTaskLoss.py

import numpy as np
import torch
import torch.nn as nn

from ...repro import fix_seeds


class MultiTaskLoss(nn.Module):
    """
    # https://openaccess.thecvf.com/content_cvpr_2018/papers/Kendall_Multi-Task_Learning_Using_CVPR_2018_paper.pdf

    Example:
        are_regression = [False, False]
        mtl = MultiTaskLoss(are_regression)
        losses = [torch.rand(1, requires_grad=True) for _ in range(len(are_regression))]
        loss = mtl(losses)
        print(loss)
        # [tensor([0.4215], grad_fn=<AddBackward0>), tensor([0.6190], grad_fn=<AddBackward0>)]
    """

    def __init__(self, are_regression=[False, False], reduction="none"):
        super().__init__()
        fix_seeds(np=np, torch=torch, show=False)
        n_tasks = len(are_regression)

        self.register_buffer("are_regression", torch.tensor(are_regression))

        # for the numercal stability, log(variables) are learned.
        self.log_vars = torch.nn.Parameter(torch.zeros(n_tasks))
        self.reduction = reduction

    def forward(self, losses):
        vars = torch.exp(self.log_vars).type_as(losses[0])
        stds = vars ** (1 / 2)
        coeffs = 1 / ((self.are_regression + 1) * vars)
        scaled_losses = [
            coeffs[i] * losses[i] + torch.log(stds[i]) for i in range(len(losses))
        ]
        return scaled_losses


# EOF

...
```


### `./metrics/_calc_bacc_from_conf_mat.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-02 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/ml/metrics/_calc_bacc_from_conf_mat.py

"""Calculate balanced accuracy from confusion matrix."""

__FILE__ = __file__

import numpy as np


def calc_bacc_from_conf_mat(cm: np.ndarray) -> float:
    """
    Calculate balanced accuracy from confusion matrix.

    Parameters
    ----------
    cm : np.ndarray
        Confusion matrix

    Returns
    -------
    float
        Balanced accuracy
    """
    try:
        per_class = np.diag(cm) / np.sum(cm, axis=1)
        return float(np.nanmean(per_class))
    except:
        return np.nan


# Convenience aliases
bACC_from_conf_mat = calc_bacc_from_conf_mat
balanced_accuracy_from_conf_mat = calc_bacc_from_conf_mat

# EOF

...
```


### `./metrics/_calc_bacc.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-02 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/ml/metrics/_calc_bacc.py

"""Calculate balanced accuracy metric."""

__FILE__ = __file__

from typing import Any, Dict, List, Optional
import numpy as np
from sklearn.metrics import balanced_accuracy_score
from ._normalize_labels import normalize_labels


def calc_bacc(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    labels: Optional[List] = None,
    fold: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Calculate balanced accuracy with robust label handling.

    Parameters
    ----------
    y_true : np.ndarray
        True labels (can be str or int)
    y_pred : np.ndarray
        Predicted labels (can be str or int)
    labels : List, optional
        Expected label list
    fold : int, optional
        Fold number for tracking

    Returns
    -------
    Dict[str, Any]
        {'metric': 'balanced_accuracy', 'value': float, 'fold': int}
    """
    try:
        y_true_norm, y_pred_norm, label_names, _ = normalize_labels(
            y_true, y_pred, labels
        )
        value = balanced_accuracy_score(y_true_norm, y_pred_norm)
        return {
            "metric": "balanced_accuracy",
            "value": float(value),
            "fold": fold,
            "labels": label_names,

...
```


### `./metrics/_calc_clf_report.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-02 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/ml/metrics/_calc_clf_report.py

"""Generate classification report."""

__FILE__ = __file__

from typing import Any, Dict, List, Optional
import pandas as pd
from sklearn.metrics import classification_report
from ._normalize_labels import normalize_labels


def calc_clf_report(
    y_true,
    y_pred,
    labels: Optional[List] = None,
    fold: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Generate classification report with robust label handling.

    Parameters
    ----------
    y_true : np.ndarray
        True labels (can be str or int)
    y_pred : np.ndarray
        Predicted labels (can be str or int)
    labels : List, optional
        Expected label list
    fold : int, optional
        Fold number for tracking

    Returns
    -------
    Dict[str, Any]
        {
            'metric': 'classification_report',
            'value': pd.DataFrame,
            'fold': int,
            'labels': list
        }
    """
    try:
        y_true_norm, y_pred_norm, label_names, _ = normalize_labels(
            y_true, y_pred, labels
        )


...
```


### `./metrics/_calc_conf_mat.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-02 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/ml/metrics/_calc_conf_mat.py

"""Calculate confusion matrix."""

__FILE__ = __file__

from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix as sklearn_confusion_matrix
from ._normalize_labels import normalize_labels


def calc_conf_mat(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    labels: Optional[List] = None,
    fold: Optional[int] = None,
    normalize: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Calculate confusion matrix with robust label handling.

    Parameters
    ----------
    y_true : np.ndarray
        True labels (can be str or int)
    y_pred : np.ndarray
        Predicted labels (can be str or int)
    labels : List, optional
        Expected label list
    fold : int, optional
        Fold number for tracking
    normalize : str, optional
        'true', 'pred', 'all', or None

    Returns
    -------
    Dict[str, Any]
        {
            'metric': 'confusion_matrix',
            'value': pd.DataFrame,
            'fold': int,
            'labels': list
        }
    """
    try:

...
```


### `./metrics/_calc_feature_importance.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-03 04:00:00 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/ml/metrics/_calc_feature_importance.py

"""
Calculate feature importance from trained models.

This module provides a unified interface for extracting feature importance
from various model types (tree-based, linear models, etc.).
"""

from typing import Dict, List, Optional, Tuple
import numpy as np


def calc_feature_importance(
    model,
    feature_names: Optional[List[str]] = None,
    top_n: Optional[int] = None,
) -> Tuple[Dict[str, float], np.ndarray]:
    """
    Calculate feature importance from a trained model.

    Parameters
    ----------
    model : object
        Trained model with feature importance attributes
        Supports:
        - Tree-based: feature_importances_ (RandomForest, XGBoost, etc.)
        - Linear: coef_ (LogisticRegression, LinearSVC, etc.)
    feature_names : List[str], optional
        Names of features. If None, uses feature_0, feature_1, ...
    top_n : int, optional
        Return only top N most important features

    Returns
    -------
    importance_dict : Dict[str, float]
        Dictionary mapping feature names to importance scores
    importance_array : np.ndarray
        Array of importance scores (same order as feature_names)

    Raises
    ------
    ValueError
        If model doesn't support feature importance extraction

    Examples
    --------

...
```


### `./metrics/_calc_mcc.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-02 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/ml/metrics/_calc_mcc.py

"""Calculate Matthews Correlation Coefficient."""

__FILE__ = __file__

from typing import Any, Dict, List, Optional
import numpy as np
from sklearn.metrics import matthews_corrcoef
from ._normalize_labels import normalize_labels


def calc_mcc(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    labels: Optional[List] = None,
    fold: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Calculate Matthews Correlation Coefficient with robust label handling.

    Parameters
    ----------
    y_true : np.ndarray
        True labels (can be str or int)
    y_pred : np.ndarray
        Predicted labels (can be str or int)
    labels : List, optional
        Expected label list
    fold : int, optional
        Fold number for tracking

    Returns
    -------
    Dict[str, Any]
        {'metric': 'mcc', 'value': float, 'fold': int}
    """
    try:
        y_true_norm, y_pred_norm, label_names, _ = normalize_labels(
            y_true, y_pred, labels
        )
        value = matthews_corrcoef(y_true_norm, y_pred_norm)
        return {
            "metric": "mcc",
            "value": float(value),
            "fold": fold,
            "labels": label_names,

...
```


### `./metrics/_calc_pre_rec_auc.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-02 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/ml/metrics/_calc_pre_rec_auc.py

"""Calculate Precision-Recall AUC."""

__FILE__ = __file__

from typing import Any, Dict, List, Optional
import numpy as np
from sklearn.metrics import average_precision_score, precision_recall_curve


def calc_pre_rec_auc(
    y_true: np.ndarray,
    y_proba: np.ndarray,
    labels: Optional[List] = None,
    fold: Optional[int] = None,
    return_curve: bool = False,
) -> Dict[str, Any]:
    """
    Calculate Precision-Recall AUC with robust handling.

    Parameters
    ----------
    y_true : np.ndarray
        True labels (can be str or int)
    y_proba : np.ndarray
        Predicted probabilities
    labels : List, optional
        Expected label list
    fold : int, optional
        Fold number for tracking
    return_curve : bool
        Whether to return PR curve data

    Returns
    -------
    Dict[str, Any]
        {'metric': 'pr_auc', 'value': float, 'fold': int}
    """
    try:
        # Normalize labels
        if labels is not None:
            unique_labels = np.unique(y_true)
            label_names = labels
            # If data contains integers, assume they map to label indices
            if isinstance(unique_labels[0], (int, np.integer)):
                y_true_norm = y_true.astype(int)

...
```


### `./metrics/_calc_roc_auc.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-02 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/ml/metrics/_calc_roc_auc.py

"""Calculate ROC AUC score."""

__FILE__ = __file__

from typing import Any, Dict, List, Optional
import numpy as np
from sklearn.metrics import roc_auc_score, roc_curve


def calc_roc_auc(
    y_true: np.ndarray,
    y_proba: np.ndarray,
    labels: Optional[List] = None,
    fold: Optional[int] = None,
    return_curve: bool = False,
) -> Dict[str, Any]:
    """
    Calculate ROC AUC score with robust handling.

    Parameters
    ----------
    y_true : np.ndarray
        True labels (can be str or int)
    y_proba : np.ndarray
        Predicted probabilities
    labels : List, optional
        Expected label list
    fold : int, optional
        Fold number for tracking
    return_curve : bool
        Whether to return ROC curve data

    Returns
    -------
    Dict[str, Any]
        {'metric': 'roc_auc', 'value': float, 'fold': int}
    """
    try:
        # Normalize labels
        if labels is not None:
            unique_labels = np.unique(y_true)
            label_names = labels
            # If data contains integers, assume they map to label indices
            if isinstance(unique_labels[0], (int, np.integer)):
                y_true_norm = y_true.astype(int)

...
```


### `./metrics/_calc_seizure_prediction_metrics.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-03 01:56:15 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/ml/metrics/_calc_seizure_prediction_metrics.py
"""Calculate clinical seizure prediction metrics.

This module provides both window-based and event-based seizure prediction metrics
following FDA/clinical guidelines.

Two Approaches:
  1. Window-based: Measures % of seizure time windows detected
  2. Event-based: Measures % of seizure events detected (≥1 alarm per event)

Key Metrics:
  - seizure_sensitivity: % detected (interpretation depends on window vs event-based)
  - fp_per_hour: False positives per hour during interictal periods
  - time_in_warning: % of total time in alarm state

Clinical Targets (FDA guidelines):
  - Sensitivity ≥ 90%
  - FP/h ≤ 0.2
  - Time in warning ≤ 20%
"""
from __future__ import annotations
from typing import Dict
import numpy as np
import pandas as pd


def calc_seizure_window_prediction_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    metadata: pd.DataFrame,
    window_duration_min: float = 1.0,
) -> Dict[str, float]:
    """Calculate clinical seizure prediction metrics (window-based).

    This function calculates window-based sensitivity, meaning it measures
    the percentage of seizure time windows that were correctly identified.
    This is NOT event-based sensitivity (which would measure % of seizure
    events detected regardless of how many windows within each event).

    Parameters
    ----------
    y_true : np.ndarray
        True labels (string: 'seizure' or 'interictal_control')
    y_pred : np.ndarray
        Predicted labels (string: 'seizure' or 'interictal_control')
    metadata : pd.DataFrame
        Metadata with 'seizure_type' column indicating seizure/interictal periods

...
```


### `./metrics/_calc_silhouette_score.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-20 00:22:25 (ywatanabe)"
# File: ./scitex_repo/src/scitex/ai/silhoute_score_block.py

THIS_FILE = "/data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/ai/silhoute_score_block.py"

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-03 03:03:13 (ywatanabe)"
# File: ./scitex_repo/src/scitex/ai/silhoute_score_block.py

# https://gist.github.com/AlexandreAbraham/5544803

""" Unsupervised evaluation metrics. """

# License: BSD Style.

from itertools import combinations as _combinations

import numpy as _np

# from sklearn.externals.joblib import Parallel, delayed
from joblib import Parallel as _Parallel
from joblib import delayed as _delayed
from sklearn.metrics.pairwise import distance_metrics as _distance_metrics
from sklearn.metrics.pairwise import pairwise_distances as _pairwise_distances
from sklearn.utils import check_random_state as _check_random_state


def calc_silhouette_score_slow(
    X, labels, metric="euclidean", sample_size=None, random_state=None, **kwds
):
    """Compute the mean Silhouette Coefficient of all samples.

    This method is computationally expensive compared to the reference one.

    The Silhouette Coefficient is calculated using the mean intra-cluster
    distance (a) and the mean nearest-cluster distance (b) for each sample.
    The Silhouette Coefficient for a sample is ``(b - a) / max(a, b)``.
    To clarrify, b is the distance between a sample and the nearest cluster
    that b is not a part of.

    This function returns the mean Silhoeutte Coefficient over all samples.
    To obtain the values for each sample, use silhouette_samples

    The best value is 1 and the worst value is -1. Values near 0 indicate
    overlapping clusters. Negative values genly indicate that a sample has
    been assigned to the wrong cluster, as a different cluster is more similar.


...
```


### `./metrics/__init__.py`

```python
#!/usr/bin/env python3
"""Scitex metrics module.

Standardized naming convention:
- calc_* functions: Modern standardized metric calculations
- Legacy names (bACC, balanced_accuracy, etc.): For backward compatibility
"""

# Modern standardized calc_* functions
from ._normalize_labels import normalize_labels as _normalize_labels
from ._calc_bacc import calc_bacc
from ._calc_mcc import calc_mcc
from ._calc_conf_mat import calc_conf_mat
from ._calc_clf_report import calc_clf_report
from ._calc_roc_auc import calc_roc_auc
from ._calc_pre_rec_auc import calc_pre_rec_auc
from ._calc_bacc_from_conf_mat import calc_bacc_from_conf_mat
from ._calc_seizure_prediction_metrics import (
    calc_seizure_window_prediction_metrics,
    calc_seizure_event_prediction_metrics,
    calc_seizure_prediction_metrics,  # backward compat alias
)
from ._calc_silhouette_score import (
    calc_silhouette_score_slow,
    calc_silhouette_samples_slow,
    calc_silhouette_score_block,
    calc_silhouette_samples_block,
)
from ._calc_feature_importance import (
    calc_feature_importance,
    calc_permutation_importance,
)

__all__ = [
    "calc_bacc",
    "calc_mcc",
    "calc_conf_mat",
    "calc_clf_report",
    "calc_roc_auc",
    "calc_pre_rec_auc",
    "calc_bacc_from_conf_mat",
    "calc_seizure_window_prediction_metrics",
    "calc_seizure_event_prediction_metrics",
    "calc_seizure_prediction_metrics",  # backward compat alias
    "calc_silhouette_score_slow",
    "calc_silhouette_samples_slow",
    "calc_silhouette_score_block",
    "calc_silhouette_samples_block",
    "calc_feature_importance",
    "calc_permutation_importance",

...
```


### `./metrics/_normalize_labels.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-02 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/ml/metrics/_normalize_labels.py

"""Label normalization utility for classification metrics."""

__FILE__ = __file__

from typing import List, Optional, Tuple
import numpy as np
from sklearn.preprocessing import LabelEncoder


def normalize_labels(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    labels: Optional[List] = None,
) -> Tuple[np.ndarray, np.ndarray, List, LabelEncoder]:
    """
    Normalize labels using sklearn.preprocessing.LabelEncoder.

    Parameters
    ----------
    y_true : np.ndarray
        True labels (can be str or int)
    y_pred : np.ndarray
        Predicted labels (can be str or int)
    labels : List, optional
        Expected label list. If provided, will be used as display names.

    Returns
    -------
    y_true_norm : np.ndarray
        Normalized true labels (integers 0, 1, 2, ...)
    y_pred_norm : np.ndarray
        Normalized predicted labels (integers 0, 1, 2, ...)
    label_names : List
        List of label names in order
    encoder : LabelEncoder
        Fitted encoder for inverse transform

    Notes
    -----
    Uses sklearn.preprocessing.LabelEncoder for robust label handling.
    Handles the edge case where data contains integers but labels are strings
    (e.g., y_true=[0,1,0,1] with labels=['Negative', 'Positive']).
    """
    # Get unique values from data
    all_data_labels = np.unique(np.concatenate([y_true, y_pred]))

...
```


### `./optim/_get_set.py`

```python
#!/usr/bin/env python3
"""Optimizer utilities - legacy interface maintained for compatibility."""

import warnings
from ._optimizers import get_optimizer, set_optimizer


def set(models, optim_str, lr):
    """Sets an optimizer to models.

    DEPRECATED: Use set_optimizer instead.
    """
    warnings.warn(
        "scitex.ai.optim.set is deprecated. Use scitex.ai.optim.set_optimizer instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return set_optimizer(models, optim_str, lr)


def get(optim_str):
    """Get optimizer class by name.

    DEPRECATED: Use get_optimizer instead.
    """
    warnings.warn(
        "scitex.ai.optim.get is deprecated. Use scitex.ai.optim.get_optimizer instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return get_optimizer(optim_str)

...
```


### `./optim/__init__.py`

```python
#!/usr/bin/env python3
"""Scitex optim module."""

from ._get_set import get, set
from ._optimizers import get_optimizer, set_optimizer, RANGER_AVAILABLE

__all__ = [
    "get",
    "get_optimizer",
    "set",
    "set_optimizer",
    "RANGER_AVAILABLE",
]

...
```


### `./optim/MIGRATION.md`

```markdown
# Ranger Optimizer Migration Guide

## Overview
The Ranger optimizer has been migrated from a vendored implementation to use the external `pytorch-optimizer` package.

## Changes

### Before
```python
from scitex.ai.optim.Ranger_Deep_Learning_Optimizer.ranger.ranger2020 import Ranger
```

### After
```python
from pytorch_optimizer import Ranger21 as Ranger
```

## Installation
```bash
pip install pytorch-optimizer
```

## Backward Compatibility
- The old API (`scitex.ai.optim.get` and `scitex.ai.optim.set`) still works but shows deprecation warnings
- The vendored Ranger code is used as fallback if pytorch-optimizer is not installed
- New code should use `get_optimizer` and `set_optimizer`

## Example Usage

### Old API (deprecated)
```python
optimizer = scitex.ai.optim.set(model, 'ranger', lr=0.001)
```

### New API
```python
optimizer = scitex.ai.optim.set_optimizer(model, 'ranger', lr=0.001)
```

## Removal Timeline
- Version 1.12.0: Deprecation warnings added
- Version 2.0.0: Vendored Ranger code will be removed
- Users must install pytorch-optimizer for Ranger support

...
```


### `./optim/_optimizers.py`

```python
#!/usr/bin/env python3
"""Optimizer utilities using external packages."""

import torch.optim as optim

# Use pytorch-optimizer package for Ranger when available
try:
    from pytorch_optimizer import Ranger21 as Ranger

    RANGER_AVAILABLE = True
except ImportError:
    # Fallback to vendored version temporarily
    try:
        from .Ranger_Deep_Learning_Optimizer.ranger.ranger2020 import Ranger

        RANGER_AVAILABLE = True
    except ImportError:
        RANGER_AVAILABLE = False
        Ranger = None


def get_optimizer(name: str):
    """Get optimizer class by name.

    Args:
        name: Optimizer name (adam, ranger, rmsprop, sgd)

    Returns:
        Optimizer class

    Raises:
        ValueError: If optimizer name is not supported
    """
    optimizers = {"adam": optim.Adam, "rmsprop": optim.RMSprop, "sgd": optim.SGD}

    if name == "ranger":
        if not RANGER_AVAILABLE:
            raise ImportError(
                "Ranger optimizer not available. "
                "Please install pytorch-optimizer: pip install pytorch-optimizer"
            )
        optimizers["ranger"] = Ranger

    if name not in optimizers:
        raise ValueError(
            f"Unknown optimizer: {name}. " f"Available: {list(optimizers.keys())}"
        )

    return optimizers[name]


...
```


### `./optim/Ranger_Deep_Learning_Optimizer/__init__.py`

```python

...
```


### `./optim/Ranger_Deep_Learning_Optimizer/LICENSE`

```plaintext
                                 Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

   TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

   1. Definitions.

      "License" shall mean the terms and conditions for use, reproduction,
      and distribution as defined by Sections 1 through 9 of this document.

      "Licensor" shall mean the copyright owner or entity authorized by
      the copyright owner that is granting the License.

      "Legal Entity" shall mean the union of the acting entity and all
      other entities that control, are controlled by, or are under common
      control with that entity. For the purposes of this definition,
      "control" means (i) the power, direct or indirect, to cause the
      direction or management of such entity, whether by contract or
      otherwise, or (ii) ownership of fifty percent (50%) or more of the
      outstanding shares, or (iii) beneficial ownership of such entity.

      "You" (or "Your") shall mean an individual or Legal Entity
      exercising permissions granted by this License.

      "Source" form shall mean the preferred form for making modifications,
      including but not limited to software source code, documentation
      source, and configuration files.

      "Object" form shall mean any form resulting from mechanical
      transformation or translation of a Source form, including but
      not limited to compiled object code, generated documentation,
      and conversions to other media types.

      "Work" shall mean the work of authorship, whether in Source or
      Object form, made available under the License, as indicated by a
      copyright notice that is included in or attached to the work
      (an example is provided in the Appendix below).

      "Derivative Works" shall mean any work, whether in Source or Object
      form, that is based on (or derived from) the Work and for which the
      editorial revisions, annotations, elaborations, or other modifications
      represent, as a whole, an original work of authorship. For the purposes
      of this License, Derivative Works shall not include works that remain
      separable from, or merely link (or bind by name) to the interfaces of,
      the Work and Derivative Works thereof.

      "Contribution" shall mean any work of authorship, including
      the original version of the Work and any modifications or additions
      to that Work or Derivative Works thereof, that is intentionally

...
```


### `./optim/Ranger_Deep_Learning_Optimizer/README.md`

```markdown
# Ranger-Deep-Learning-Optimizer 
</br>
Ranger - a synergistic optimizer combining RAdam (Rectified Adam) and LookAhead, and now GC (gradient centralization) in one optimizer.
</br>

#### quick note - Ranger21 is now in beta and is Ranger with a host of new improvements.  
Recommend you compare results with Ranger21:  https://github.com/lessw2020/Ranger21

### Latest version 20.9.4 - updates Gradient Centralization to GC2 (thanks to GC developer) and removes addcmul_ deprecation warnings in PyTorch 1.60. 
</br> </br>
*Latest version is in ranger2020.py - looking at a few other additions before integrating into the main ranger.py.  

What is Gradient Centralization? = "GC can be viewed as a projected gradient descent method with a constrained loss function. The Lipschitzness of the constrained loss function and its gradient is better so that the training process becomes more efficient and stable."  Source paper:  https://arxiv.org/abs/2004.01461v2
</br>
Ranger now uses Gradient Centralization by default, and applies it to all conv and fc layers by default.  However, everything is customizable so you can test with and without on your own datasets.  (Turn on off via "use_gc" flag at init).
</br>
### Best training results - use a 75% flat lr, then step down and run lower lr for 25%, or cosine descend last 25%. 

</br> Per extensive testing - It's important to note that simply running one learning rate the entire time will not produce optimal results.  
Effectively Ranger will end up 'hovering' around the optimal zone, but can't descend into it unless it has some additional run time at a lower rate to drop down into the optimal valley.

### Full customization at init: 
<div  align="center"><img src="ranger-with-gc-options.jpg" height="80%" width="80%" alt=""/></div>
</br>
Ranger will now print out id and gc settings at init so you can confirm the optimizer settings at train time:
<div  align="center"><img src="ranger-init.jpg" height="80%" width="80%" alt=""/></div>

/////////////////////

Medium article with more info:  
https://medium.com/@lessw/new-deep-learning-optimizer-ranger-synergistic-combination-of-radam-lookahead-for-the-best-of-2dc83f79a48d

Multiple updates:
1 - Ranger is the optimizer we used to beat the high scores for 12 different categories on the FastAI leaderboards!  (Previous records all held with AdamW optimizer).

2 - Highly recommend combining Ranger with: Mish activation function, and flat+ cosine anneal training curve.

3 - Based on that, also found .95 is better than .90 for beta1 (momentum) param (ala betas=(0.95, 0.999)).

Fixes:
1 - Differential Group learning rates now supported.  This was fix in RAdam and ported here thanks to @sholderbach.
2 - save and then load may leave first run weights stranded in memory, slowing down future runs = fixed.

### Installation
Clone the repo, cd into it and install it in editable mode (`-e` option).
That way, these is no more need to re-install the package after modification.
```bash
git clone https://github.com/lessw2020/Ranger-Deep-Learning-Optimizer
cd Ranger-Deep-Learning-Optimizer
pip install -e . 
```

...
```


### `./optim/Ranger_Deep_Learning_Optimizer/setup.py`

```python
#!/usr/bin/env python

import os
from setuptools import find_packages, setup


def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as f:
        return f.read()


setup(
    name="ranger",
    version="0.1.dev0",
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
    package_dir={"ranger": os.path.join(".", "ranger")},
    description="Ranger - a synergistic optimizer using RAdam "
    "(Rectified Adam) and LookAhead in one codebase ",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    author="Less Wright",
    license="Apache",
    install_requires=["torch"],
)

...
```


### `./plt/__init__.py`

```python
#!/usr/bin/env python3
"""Scitex centralized plotting module.

Note: Metric calculation functions (calc_*) are imported from scitex.ml.metrics
but re-exported here for backward compatibility. New code should import directly
from scitex.ml.metrics instead.
"""

from ._plot_conf_mat import calc_bACC_from_conf_mat, calc_bacc_from_conf_mat, plot_conf_mat, conf_mat
from ._plot_learning_curve import (
    plot_learning_curve,
    _prepare_metrics_df,
    _configure_accuracy_axis,
    _plot_training_data,
    _plot_validation_data,
    _plot_test_data,
    _add_epoch_vlines,
    _select_epoch_ticks,
)
from ._plot_optuna_study import optuna_study, plot_optuna_study
from ._plot_roc_curve import plot_roc_curve
from ._plot_pre_rec_curve import plot_pre_rec_curve
from ._plot_feature_importance import (
    plot_feature_importance,
    plot_feature_importance_cv_summary,
)

# Backward compatibility aliases
learning_curve = plot_learning_curve
plot_tra = _plot_training_data
process_i_global = _prepare_metrics_df
scatter_tes = _plot_test_data
scatter_val = _plot_validation_data
select_ticks = _select_epoch_ticks
set_yaxis_for_acc = _configure_accuracy_axis
vline_at_epochs = _add_epoch_vlines

__all__ = [
    # Plotting functions
    "plot_conf_mat",
    "conf_mat",  # backward compat
    "plot_learning_curve",
    "learning_curve",  # backward compat
    "optuna_study",
    "plot_optuna_study",
    "plot_roc_curve",
    "plot_pre_rec_curve",
    "plot_feature_importance",
    "plot_feature_importance_cv_summary",
    "plot_tra",

...
```


### `./plt/_plot_conf_mat.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-02 07:15:10 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/ml/plt/plot_conf_mat.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import argparse

import matplotlib
import numpy as np
import pandas as pd
import scitex
import seaborn as sns
from matplotlib import ticker
from mpl_toolkits.axes_grid1 import make_axes_locatable
from sklearn.metrics import balanced_accuracy_score
from sklearn.metrics import confusion_matrix as sklearn_confusion_matrix

# Import metric calculation from centralized location (SoC: metrics in scitex.ml.metrics)
from scitex.ml.metrics import calc_bacc_from_conf_mat

# Aliases for backward compatibility
calc_bACC_from_conf_mat = calc_bacc_from_conf_mat


def plot_conf_mat(
    cm=None,
    y_true=None,
    y_pred=None,
    y_pred_proba=None,
    labels=None,
    sorted_labels=None,
    pred_labels=None,
    sorted_pred_labels=None,
    true_labels=None,
    sorted_true_labels=None,
    label_rotation_xy=(15, 15),
    title="Confusion Matrix",
    colorbar=True,
    x_extend_ratio=1.0,
    y_extend_ratio=1.0,
    ax=None,
    spath=None,
):
    """

...
```


### `./plt/_plot_feature_importance.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-03 04:10:00 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/ml/plt/plot_feature_importance.py

"""
Plot feature importance from trained models.

This module provides visualization functions for feature importance,
supporting both single-fold and cross-validation summary plots.
"""

from pathlib import Path
from typing import Dict, List, Optional, Union
import numpy as np
import matplotlib.pyplot as plt
import scitex as stx


def plot_feature_importance(
    importance: Union[np.ndarray, Dict[str, float]],
    feature_names: Optional[List[str]] = None,
    top_n: int = 20,
    title: str = "Feature Importance",
    xlabel: str = "Importance",
    figsize: tuple = (10, 8),
    spath: Optional[Union[str, Path]] = None,
) -> plt.Figure:
    """
    Plot feature importance as a horizontal bar chart.

    Parameters
    ----------
    importance : np.ndarray or Dict[str, float]
        Feature importance values. If array, must match feature_names length.
        If dict, keys are feature names and values are importances.
    feature_names : List[str], optional
        Names of features (required if importance is array)
    top_n : int, default 20
        Number of top features to display
    title : str, default "Feature Importance"
        Plot title
    xlabel : str, default "Importance"
        X-axis label
    figsize : tuple, default (10, 8)
        Figure size
    spath : Union[str, Path], optional
        Path to save the figure

    Returns

...
```


### `./plt/_plot_learning_curve.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-02 19:50:54 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/ml/plt/plot_learning_curve.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
# Time-stamp: "2024-03-12 19:52:48 (ywatanabe)"

import argparse
import re

import numpy as np
import pandas as pd
import scitex
from scitex.plt.color import str2hex


def _prepare_metrics_df(metrics_df):
    """Prepare metrics DataFrame with i_global as index."""
    if metrics_df.index.name != "i_global":
        try:
            metrics_df = metrics_df.set_index("i_global")
        except KeyError:
            print(
                "Error: The DataFrame does not contain a column named 'i_global'. "
                "Please check the column names."
            )
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
    metrics_df["i_global"] = metrics_df.index  # alias
    return metrics_df


def _configure_accuracy_axis(ax, metric_key):
    """Configure y-axis for accuracy metrics."""
    if re.search("[aA][cC][cC]", metric_key):
        ax.set_ylim(0, 1)
        ax.set_yticks([0, 0.5, 1.0])
    return ax


def _plot_training_data(ax, metrics_df, metric_key, linewidth=1, color=None):
    """Plot training phase data as line."""
    if color is None:
        color = str2hex("blue")


...
```


### `./plt/_plot_optuna_study.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-02 18:46:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/ml/plt/plot_optuna_study.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
  - Loads Optuna study and generates various visualizations
  - Creates optimization history, parameter importances, slice plots
  - Saves study history and visualization results

Dependencies:
  - packages:
    - optuna
    - pandas
    - scitex

IO:
  - input-files:
    - Optuna study database (.db file)
  - output-files:
    - study_history.csv
    - optimization_history.png/html
    - param_importances.png/html
    - slice.png/html
    - contour.png/html
    - parallel_coordinate.png/html
"""

"""Imports"""
import argparse

import scitex as stx
from scitex import logging

logger = logging.getLogger(__name__)


def plot_optuna_study(lpath, value_str, sort=False):
    """
    Loads an Optuna study and generates various visualizations for each target metric.

    Parameters:
    - lpath (str): Path to the Optuna study database.

...
```


### `./plt/_plot_pre_rec_curve.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-02 19:44:06 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/ml/plt/plot_pre_rec_curve.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import argparse

import numpy as np
from scitex.plt.color import get_colors_from_conf_matap
from sklearn.metrics import average_precision_score, precision_recall_curve


def _solve_intersection(f1, a, b):
    """Determine intersection of line (y = ax + b) and iso-f1 curve."""
    _a = 2 * a
    _b = -a * f1 + 2 * b - f1
    _c = -b * f1

    x_f = (-_b + np.sqrt(_b**2 - 4 * _a * _c)) / (2 * _a)
    y_f = a * x_f + b

    return (x_f, y_f)


def _to_onehot(class_indices, n_classes):
    """Convert class indices to one-hot encoding."""
    eye = np.eye(n_classes, dtype=int)
    return eye[class_indices]


def plot_pre_rec_curve(true_class, pred_proba, labels, ax=None, spath=None):
    """
    Plot precision-recall curve.

    Parameters
    ----------
    true_class : array-like
        True class labels
    pred_proba : array-like
        Predicted probabilities
    labels : list
        Class labels
    ax : matplotlib axis, optional
        Axis to plot on. If None, creates new figure

...
```


### `./plt/_plot_roc_curve.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-02 19:44:13 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/ml/plt/plot_roc_curve.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import argparse

import numpy as np
import scitex
from scitex.plt.color import get_colors_from_conf_matap
from sklearn.metrics import roc_auc_score, roc_curve


def _to_onehot(class_indices, n_classes):
    """Convert class indices to one-hot encoding."""
    eye = np.eye(n_classes, dtype=int)
    return eye[class_indices]


def plot_roc_curve(true_class, pred_proba, labels, ax=None, spath=None):
    """
    Plot ROC-AUC curve.

    Parameters
    ----------
    true_class : array-like
        True class labels
    pred_proba : array-like
        Predicted probabilities
    labels : list
        Class labels
    ax : matplotlib axis, optional
        Axis to plot on. If None, creates new figure
    spath : str, optional
        Path to save figure

    Returns
    -------
    fig : matplotlib.figure.Figure
        Figure object
    metrics : dict
        ROC metrics
    """
    import scitex as stx

...
```


### `./README.md`

```markdown
# SciTeX AI Module

The AI module provides machine learning and artificial intelligence utilities for the SciTeX framework.

## Overview

The AI module is organized into several submodules:

### Core Components

- **`genai`** - Generative AI integration with multiple providers (OpenAI, Anthropic, Google, etc.)
- **`training`** - Training utilities (EarlyStopping, LearningCurveLogger)
- **`classification`** - Classification tools (ClassificationReporter, Classifier)

### Neural Network Components

- **`layer`** - Custom neural network layers
- **`loss`** - Loss functions for training
- **`act`** - Activation functions
- **`optim`** - Optimizers and optimization utilities

### Analysis & Visualization

- **`plt`** - AI-specific plotting utilities
- **`metrics`** - Performance metrics
- **`clustering`** - Clustering algorithms (UMAP, PCA)
- **`feature_extraction`** - Feature extraction methods

### Utilities

- **`utils`** - General AI/ML utilities
- **`sampling`** - Data sampling methods
- **`sklearn`** - Scikit-learn integration

## Installation

```bash
pip install scitex
```

## Quick Start

### Generative AI (GenAI)

The GenAI module provides a unified interface for multiple AI providers:

```python
from scitex.ai.genai import GenAI

# Basic usage
```

...
```


### `./sampling/undersample.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-24 10:13:17 (ywatanabe)"
# File: ./scitex_repo/src/scitex/ai/sampling/undersample.py

THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/ai/sampling/undersample.py"

from typing import Tuple
from ...types import ArrayLike

try:
    from imblearn.under_sampling import RandomUnderSampler
    IMBLEARN_AVAILABLE = True
except ImportError:
    IMBLEARN_AVAILABLE = False


def undersample(
    X: ArrayLike, y: ArrayLike, random_state: int = 42
) -> Tuple[ArrayLike, ArrayLike]:
    """Undersample data preserving input type.

    Args:
        X: Features array-like of shape (n_samples, n_features)
        y: Labels array-like of shape (n_samples,)
    Returns:
        Resampled X, y of same type as input
        
    Raises:
        ImportError: If imblearn is not installed
    """
    if not IMBLEARN_AVAILABLE:
        raise ImportError(
            "The undersample function requires the imbalanced-learn package. "
            "Install it with: pip install imbalanced-learn"
        )
    
    rus = RandomUnderSampler(random_state=random_state)
    X_resampled, y_resampled = rus.fit_resample(X, y)
    return X_resampled, y_resampled


# EOF

...
```


### `./sk/_clf.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-03-23 17:36:05 (ywatanabe)"

import numpy as np
from sklearn.decomposition import PCA
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.linear_model import LogisticRegression, RidgeClassifierCV
from sklearn.pipeline import make_pipeline
from sklearn.svm import SVC, LinearSVC
from sktime.classification.deep_learning.cnn import CNNClassifier
from sktime.classification.deep_learning.inceptiontime import (
    InceptionTimeClassifier,
)
from sktime.classification.deep_learning.lstmfcn import LSTMFCNClassifier
from sktime.classification.dummy import DummyClassifier
from sktime.classification.feature_based import TSFreshClassifier
from sktime.classification.hybrid import HIVECOTEV2
from sktime.classification.interval_based import TimeSeriesForestClassifier
from sktime.classification.kernel_based import RocketClassifier, TimeSeriesSVC
from sktime.transformations.panel.reduce import Tabularizer
from sktime.transformations.panel.rocket import Rocket

# _rocket_pipeline = make_pipeline(
#     Rocket(n_jobs=-1),
#     RidgeClassifierCV(alphas=np.logspace(-3, 3, 10)),
# )


# def rocket_pipeline(*args, **kwargs):
#     return _rocket_pipeline


def rocket_pipeline(*args, **kwargs):
    return make_pipeline(
        Rocket(*args, **kwargs),
        LogisticRegression(
            max_iter=1000
        ),  # Increase max_iter if needed for convergence
        # RidgeClassifierCV(alphas=np.logspace(-3, 3, 10)),
        # SVC(probability=True, kernel="linear"),
    )


# def rocket_pipeline(*args, **kwargs):
#     return make_pipeline(
#         Rocket(*args, **kwargs),
#         SelectKBest(f_classif, k=500),
#         PCA(n_components=100),

...
```


### `./sk/__init__.py`

```python
#!/usr/bin/env python3
"""Scitex sk module."""

from ._clf import GB_pipeline, rocket_pipeline
from ._to_sktime import to_sktime_df

__all__ = [
    "GB_pipeline",
    "rocket_pipeline",
    "to_sktime_df",
]

...
```


### `./sk/_to_sktime.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-03-05 13:17:04 (ywatanabe)"

# import warnings

import numpy as np
import pandas as pd
import torch


def to_sktime_df(X):
    """
    Converts a dataset to a format compatible with sktime, encapsulating each sample as a pandas DataFrame.

    Arguments:
    - X (numpy.ndarray or torch.Tensor or pandas.DataFrame): The input dataset with shape (n_samples, n_chs, seq_len).
      It should be a 3D array-like structure containing the time series data.

    Return:
    - sktime_df (pandas.DataFrame): A DataFrame where each element is a pandas Series representing a univariate time series.

    Data Types and Shapes:
    - If X is a numpy.ndarray, it should have the shape (n_samples, n_chs, seq_len).
    - If X is a torch.Tensor, it should have the shape (n_samples, n_chs, seq_len) and will be converted to a numpy array.
    - If X is a pandas.DataFrame, it is assumed to already be in the correct format and will be returned as is.

    References:
    - sktime: https://github.com/alan-turing-institute/sktime

    Examples:
    --------
    >>> X_np = np.random.rand(64, 160, 1024)
    >>> sktime_df = to_sktime_df(X_np)
    >>> type(sktime_df)
    <class 'pandas.core.frame.DataFrame'>
    """
    if isinstance(X, pd.DataFrame):
        return X
    elif torch.is_tensor(X):
        X = X.numpy()
    elif not isinstance(X, np.ndarray):
        raise ValueError(
            "Input X must be a numpy.ndarray, torch.Tensor, or pandas.DataFrame"
        )

    X = X.astype(np.float64)

    def _format_a_sample_for_sktime(x):
        """

...
```


### `./sklearn/clf.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-03-23 17:36:05 (ywatanabe)"

import numpy as np
from sklearn.decomposition import PCA
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.linear_model import LogisticRegression, RidgeClassifierCV
from sklearn.pipeline import make_pipeline
from sklearn.svm import SVC, LinearSVC
from sktime.classification.deep_learning.cnn import CNNClassifier
from sktime.classification.deep_learning.inceptiontime import (
    InceptionTimeClassifier,
)
from sktime.classification.deep_learning.lstmfcn import LSTMFCNClassifier
from sktime.classification.dummy import DummyClassifier
from sktime.classification.feature_based import TSFreshClassifier
from sktime.classification.hybrid import HIVECOTEV2
from sktime.classification.interval_based import TimeSeriesForestClassifier
from sktime.classification.kernel_based import RocketClassifier, TimeSeriesSVC
from sktime.transformations.panel.reduce import Tabularizer
from sktime.transformations.panel.rocket import Rocket

# _rocket_pipeline = make_pipeline(
#     Rocket(n_jobs=-1),
#     RidgeClassifierCV(alphas=np.logspace(-3, 3, 10)),
# )


# def rocket_pipeline(*args, **kwargs):
#     return _rocket_pipeline


def rocket_pipeline(*args, **kwargs):
    return make_pipeline(
        Rocket(*args, **kwargs),
        LogisticRegression(
            max_iter=1000
        ),  # Increase max_iter if needed for convergence
        # RidgeClassifierCV(alphas=np.logspace(-3, 3, 10)),
        # SVC(probability=True, kernel="linear"),
    )


# def rocket_pipeline(*args, **kwargs):
#     return make_pipeline(
#         Rocket(*args, **kwargs),
#         SelectKBest(f_classif, k=500),
#         PCA(n_components=100),

...
```


### `./sklearn/__init__.py`

```python
#!/usr/bin/env python3
"""Sklearn wrappers and utilities."""

import warnings

try:
    from .clf import *
except ImportError as e:
    warnings.warn(
        f"Could not import clf from scitex.ai.sklearn: {str(e)}. "
        f"Some functionality may be unavailable. "
        f"Consider installing missing dependencies if you need this module.",
        ImportWarning,
        stacklevel=2
    )

try:
    from .to_sktime import *
except ImportError as e:
    warnings.warn(
        f"Could not import to_sktime from scitex.ai.sklearn: {str(e)}. "
        f"Some functionality may be unavailable. "
        f"Consider installing missing dependencies if you need this module.",
        ImportWarning,
        stacklevel=2
    )

...
```


### `./sklearn/to_sktime.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-03-05 13:17:04 (ywatanabe)"

# import warnings

import numpy as np
import pandas as pd
import torch


def to_sktime_df(X):
    """
    Converts a dataset to a format compatible with sktime, encapsulating each sample as a pandas DataFrame.

    Arguments:
    - X (numpy.ndarray or torch.Tensor or pandas.DataFrame): The input dataset with shape (n_samples, n_chs, seq_len).
      It should be a 3D array-like structure containing the time series data.

    Return:
    - sktime_df (pandas.DataFrame): A DataFrame where each element is a pandas Series representing a univariate time series.

    Data Types and Shapes:
    - If X is a numpy.ndarray, it should have the shape (n_samples, n_chs, seq_len).
    - If X is a torch.Tensor, it should have the shape (n_samples, n_chs, seq_len) and will be converted to a numpy array.
    - If X is a pandas.DataFrame, it is assumed to already be in the correct format and will be returned as is.

    References:
    - sktime: https://github.com/alan-turing-institute/sktime

    Examples:
    --------
    >>> X_np = np.random.rand(64, 160, 1024)
    >>> sktime_df = to_sktime_df(X_np)
    >>> type(sktime_df)
    <class 'pandas.core.frame.DataFrame'>
    """
    if isinstance(X, pd.DataFrame):
        return X
    elif torch.is_tensor(X):
        X = X.detach().numpy()
    elif not isinstance(X, np.ndarray):
        raise ValueError(
            "Input X must be a numpy.ndarray, torch.Tensor, or pandas.DataFrame"
        )

    X = X.astype(np.float64)

    def _format_a_sample_for_sktime(x):
        """

...
```


### `./training/_EarlyStopping.py`

```python
#!/usr/bin/env python3
# Time-stamp: "2024-09-07 01:09:38 (ywatanabe)"

import os

import scitex
import numpy as np


class EarlyStopping:
    """
    Early stops the training if the validation score doesn't improve after a given patience period.

    """

    def __init__(self, patience=7, verbose=False, delta=1e-5, direction="minimize"):
        """
        Args:
            patience (int): How long to wait after last time validation score improved.
                            Default: 7
            verbose (bool): If True, prints a message for each validation score improvement.
                            Default: False
            delta (float): Minimum change in the monitored quantity to qualify as an improvement.
                            Default: 0
        """
        self.patience = patience
        self.verbose = verbose
        self.direction = direction

        self.delta = delta

        # default
        self.counter = 0
        self.best_score = np.inf if direction == "minimize" else -np.inf
        self.best_i_global = None
        self.models_spaths_dict = {}

    def is_best(self, val_score):
        is_smaller = val_score < self.best_score - abs(self.delta)
        is_larger = self.best_score + abs(self.delta) < val_score
        return is_smaller if self.direction == "minimize" else is_larger

    def __call__(self, current_score, models_spaths_dict, i_global):
        # The 1st call
        if self.best_score is None:
            self.save(current_score, models_spaths_dict, i_global)
            return False

        # After the 2nd call
        if self.is_best(current_score):

...
```


### `./training/__init__.py`

```python
#!/usr/bin/env python3
"""Training utilities."""

from ._EarlyStopping import EarlyStopping
from ._LearningCurveLogger import LearningCurveLogger

__all__ = ["EarlyStopping", "LearningCurveLogger"]

...
```


### `./training/_LearningCurveLogger.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2024-11-20 08:49:50 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/ml/training/_LearningCurveLogger.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionality:
    - Records and visualizes learning curves during model training
    - Supports tracking of multiple metrics across training/validation/test phases
    - Generates plots showing training progress over iterations and epochs
    - Delegates plotting to scitex.ml.plt.plot_learning_curve for consistency

Input:
    - Training metrics dictionary containing loss, accuracy, predictions etc.
    - Step information (Training/Validation/Test)

Output:
    - Learning curve plots via scitex.ml.plt.plot_learning_curve
    - DataFrames with recorded metrics
    - Training progress prints

Prerequisites:
    - PyTorch
    - scikit-learn
    - matplotlib
    - pandas
    - numpy
    - scitex
"""

import re
import warnings
from collections import defaultdict
from pprint import pprint
from typing import Any, Dict, List, Optional, Union

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


class LearningCurveLogger:
    """Records and visualizes learning metrics during model training.

...
```


### `./training/legacy/early_stopping.py`

```python
#!/usr/bin/env python3
# Time-stamp: "2024-09-07 01:09:38 (ywatanabe)"

import os

import scitex
import numpy as np


class EarlyStopping:
    """
    Early stops the training if the validation score doesn't improve after a given patience period.

    """

    def __init__(self, patience=7, verbose=False, delta=1e-5, direction="minimize"):
        """
        Args:
            patience (int): How long to wait after last time validation score improved.
                            Default: 7
            verbose (bool): If True, prints a message for each validation score improvement.
                            Default: False
            delta (float): Minimum change in the monitored quantity to qualify as an improvement.
                            Default: 0
        """
        self.patience = patience
        self.verbose = verbose
        self.direction = direction

        self.delta = delta

        # default
        self.counter = 0
        self.best_score = np.inf if direction == "minimize" else -np.inf
        self.best_i_global = None
        self.models_spaths_dict = {}

    def is_best(self, val_score):
        is_smaller = val_score < self.best_score - abs(self.delta)
        is_larger = self.best_score + abs(self.delta) < val_score
        return is_smaller if self.direction == "minimize" else is_larger

    def __call__(self, current_score, models_spaths_dict, i_global):
        # The 1st call
        if self.best_score is None:
            self.save(current_score, models_spaths_dict, i_global)
            return False

        # After the 2nd call
        if self.is_best(current_score):

...
```


### `./training/legacy/learning_curve_logger.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-20 08:49:50 (ywatanabe)"
# File: ./scitex_repo/src/scitex/ai/_LearningCurveLogger.py

THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/ai/_LearningCurveLogger.py"

"""
Functionality:
    - Records and visualizes learning curves during model training
    - Supports tracking of multiple metrics across training/validation/test phases
    - Generates plots showing training progress over iterations and epochs

Input:
    - Training metrics dictionary containing loss, accuracy, predictions etc.
    - Step information (Training/Validation/Test)

Output:
    - Learning curve plots
    - Dataframes with recorded metrics
    - Training progress prints

Prerequisites:
    - PyTorch
    - scikit-learn
    - matplotlib
    - pandas
    - numpy
"""

import re as _re
from collections import defaultdict as _defaultdict
from pprint import pprint as _pprint
from typing import Dict as _Dict
from typing import List as _List
from typing import Union as _Union
from typing import Optional as _Optional
from typing import Any as _Any

import matplotlib as _matplotlib
import matplotlib.figure
import pandas as _pd
import numpy as _np
import warnings as _warnings
import torch as _torch


class LearningCurveLogger:
    """Records and visualizes learning metrics during model training.


...
```


### `./utils/_check_params.py`

```python
#!/usr/bin/env python3
# Time-stamp: "2024-02-17 12:38:40 (ywatanabe)"

from pprint import pprint as _pprint
from time import sleep

# def get_params(model, tgt_name=None, sleep_sec=2, show=False):

#     name_shape_dict = {}
#     for name, param in model.named_parameters():
#         learnable = "Learnable" if param.requires_grad else "Freezed"

#         if (tgt_name is not None) & (name == tgt_name):
#             return param
#         if tgt_name is None:
#             # print(f"\n{param}\n{param.shape}\nname: {name}\n")
#             if show is True:
#                 print(
#                     f"\n{param}: {param.shape}\nname: {name}\nStatus: {learnable}\n"
#                 )
#                 sleep(sleep_sec)
#             name_shape_dict[name] = list(param.shape)

#     if tgt_name is None:
#         print()
#         _pprint(name_shape_dict)
#         print()


def check_params(model, tgt_name=None, show=False):

    out_dict = {}

    for name, param in model.named_parameters():
        learnable = "Learnable" if param.requires_grad else "Freezed"

        if tgt_name is None:
            out_dict[name] = (param.shape, learnable)

        elif (tgt_name is not None) & (name == tgt_name):
            out_dict[name] = (param.shape, learnable)

        elif (tgt_name is not None) & (name != tgt_name):
            continue

    if show:
        for k, v in out_dict.items():
            print(f"\n{k}\n{v}")

    return out_dict

...
```


### `./utils/_default_dataset.py`

```python
#!/usr/bin/env python3

from torch.utils.data import Dataset
import numpy as np


class DefaultDataset(Dataset):
    """
    Apply transform for the first element of arrs_list

    Example:
        n = 1024
        n_chs = 19
        X = np.random.rand(n, n_chs, 1000)
        T = np.random.randint(0, 4, size=(n, 1))
        S = np.random.randint(0, 999, size=(n, 1))
        Sr = np.random.randint(0, 4, size=(n, 1))

        arrs_list = [X, T, S, Sr]
        transform = None
        ds = _DefaultDataset(arrs_list, transform=transform)
        len(ds) # 1024
    """

    def __init__(self, arrs_list, transform=None):
        self.arrs_list = arrs_list
        self.arrs = arrs_list  # alias

        assert np.all([len(arr) for arr in arrs_list])

        self.length = len(arrs_list[0])
        self.transform = transform

    def __len__(self):
        return self.length

    def __getitem__(self, idx):
        arrs_list_idx = [arr[idx] for arr in self.arrs_list]

        # Here, you might want to transform, or apply DA on X as a numpy array
        if self.transform:
            dtype_orig = arrs_list_idx[0].dtype
            arrs_list_idx[0] = self.transform(
                arrs_list_idx[0].astype(np.float64)
            ).astype(dtype_orig)
        return arrs_list_idx

...
```


### `./utils/_format_samples_for_sktime.py`

```python
import pandas as pd
import torch
import numpy as np


def _format_a_sample_for_sktime(x):
    """
    x.shape: (n_chs, seq_len)
    """
    dims = pd.Series(
        [pd.Series(x[d], name=f"dim_{d}") for d in range(len(x))],
        index=[f"dim_{i}" for i in np.arange(len(x))],
    )
    return dims


def format_samples_for_sktime(X):
    """
    X.shape: (n_samples, n_chs, seq_len)
    """
    if torch.is_tensor(X):
        X = X.numpy()  # (64, 160, 1024)

        X = X.astype(np.float64)

    return pd.DataFrame([_format_a_sample_for_sktime(X[i]) for i in range(len(X))])

...
```


### `./utils/grid_search.py`

```python
#!./env/bin/python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-04-22 23:54:02"
# Author: Yusuke Watanabe (ywata1989@gmail.com)

"""
This script defines scitex.ml.utils.grid_search
"""

# Imports
import itertools as _itertools
import random as _random
import sys as _sys

import matplotlib.pyplot as _plt
import scitex as _scitex


# Functions
def yield_grids(params_grid: dict, random=False):
    """
    Generator function that yields combinations of parameters from a grid.

    Args:
        params_grid (dict): A dictionary where keys are parameter names and values are lists of parameter values.
        random (bool): If True, yields the parameter combinations in random order.

    Yields:
        dict: A dictionary of parameters for one set of conditions from the grid.

    Example:
        # Parameters
        params_grid = {
            "batch_size": [2**i for i in range(7)],
            "n_chs": [2**i for i in range(7)],
            "seq_len": [2**i for i in range(15)],
            "fs": [2**i for i in range(8, 11)],
            "n_segments": [2**i for i in range(6)],
            "n_bands_pha": [2**i for i in range(7)],
            "n_bands_amp": [2**i for i in range(7)],
            "precision": ['fp16', 'fp32'],
            "device": ['cpu', 'cuda'],
            "package": ['tensorpac', 'scitex'],
        }

        # Example of using the generator
        for param_dict in yield_grids(params_grid, random=True):
            print(param_dict)
    """
    combinations = list(_itertools.product(*params_grid.values()))

...
```


### `./utils/__init__.py`

```python
#!/usr/bin/env python3
"""Scitex utils module."""

from ._check_params import check_params
from ._default_dataset import DefaultDataset
from ._format_samples_for_sktime import format_samples_for_sktime
from ._label_encoder import LabelEncoder
from ._merge_labels import merge_labels
from ._sliding_window_data_augmentation import sliding_window_data_augmentation
from ._under_sample import under_sample
from ._verify_n_gpus import verify_n_gpus

__all__ = [
    "DefaultDataset",
    "LabelEncoder",
    "check_params",
    "format_samples_for_sktime",
    "merge_labels",
    "sliding_window_data_augmentation",
    "under_sample",
    "verify_n_gpus",
]

...
```


### `./utils/_label_encoder.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-03-02 09:52:28 (ywatanabe)"

from warnings import warn

import numpy as np
import pandas as pd
import torch
from sklearn.preprocessing import LabelEncoder as SklearnLabelEncoder


class LabelEncoder(SklearnLabelEncoder):
    """
    An extension of the sklearn.preprocessing.LabelEncoder that supports incremental learning.
    This means it can handle new classes without forgetting the old ones.

    Attributes:
        classes_ (np.ndarray): Holds the label for each class.

    Example usage:
        encoder = IncrementalLabelEncoder()
        encoder.fit(np.array(["apple", "banana"]))
        encoded_labels = encoder.transform(["apple", "banana"])  # This will give you the encoded labels

        encoder.fit(["cherry"])  # Incrementally add "cherry"
        encoder.transform(["apple", "banana", "cherry"])  # Now it works, including "cherry"

        # Now you can use inverse_transform with the encoded labels
        print(encoder.classes_)
        original_labels = encoder.inverse_transform(encoded_labels)
        print(original_labels)  # This should print ['apple', 'banana']
    """

    def __init__(self):
        super().__init__()
        self.classes_ = np.array([])

    def _check_input(self, y):
        """
        Check and convert the input to a NumPy array if it is a list, tuple, pandas.Series, pandas.DataFrame, or torch.Tensor.

        Arguments:
            y (list, tuple, pd.Series, pd.DataFrame, torch.Tensor): The input labels.

        Returns:
            np.ndarray: The input labels converted to a NumPy array.
        """
        if isinstance(y, (list, tuple)):
            y = np.array(y)

...
```


### `./utils/_merge_labels.py`

```python
#!/usr/bin/env python3

import scitex
import numpy as np

# y1, y2 = T_tra, M_tra
# def merge_labels(y1, y2):
#     y = [str(z1) + "-" + str(z2) for z1, z2 in zip(y1, y2)]
#     conv_d = {z: i for i, z in enumerate(np.unique(y))}
#     y = [conv_d[z] for z in y]
#     return y


def merge_labels(*ys, to_int=False):
    if not len(ys) > 1:  # Check if more than two arguments are passed
        return ys[0]
    else:
        y = [scitex.gen.connect_nums(zs) for zs in zip(*ys)]
        if to_int:
            conv_d = {z: i for i, z in enumerate(np.unique(y))}
            y = [conv_d[z] for z in y]
        return np.array(y)

...
```


### `./utils/_sliding_window_data_augmentation.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-01-24 13:56:36 (ywatanabe)"

import random


def sliding_window_data_augmentation(x, window_size_pts):
    start = random.randint(0, x.shape[-1] - window_size_pts)
    end = start + window_size_pts
    return x[..., start:end]

...
```


### `./utils/_under_sample.py`

```python
#!/usr/bin/env python3


from collections import Counter

import numpy as np


def under_sample(y, replace=False):
    """
    Input:
        Labels
    Return:
        Indices

    Example:
        t = ['a', 'b', 'c', 'b', 'c', 'a', 'c']
        print(under_sample(t))
        # [5 0 1 3 4 6]
        print(under_sample(t))
        # [5 0 1 3 6 2]
    """

    # find the minority and majority classes
    class_counts = Counter(y)
    # majority_class = max(class_counts, key=class_counts.get)
    minority_class = min(class_counts, key=class_counts.get)

    # compute the number of sample to draw from the majority class using
    # a negative binomial distribution
    n_minority_class = class_counts[minority_class]
    n_majority_resampled = n_minority_class

    # draw randomly with or without replacement
    indices = np.hstack(
        [
            np.random.choice(
                np.flatnonzero(y == k),
                size=n_majority_resampled,
                replace=replace,
            )
            for k in class_counts.keys()
        ]
    )

    return indices


if __name__ == "__main__":
    t = np.array(["a", "b", "c", "b", "c", "a", "c"])

...
```


### `./utils/_verify_n_gpus.py`

```python
import torch
import warnings


def verify_n_gpus(n_gpus):
    if torch.cuda.device_count() < n_gpus:
        warnings.warn(
            f"N_GPUS ({n_gpus}) is larger "
            f"than n_gpus torch can acesses (= {torch.cuda.device_count()})"
            f"Please check $CUDA_VISIBLE_DEVICES and your setting in this script.",
            UserWarning,
        )
        return torch.cuda.device_count()

    else:
        return n_gpus

...
```

