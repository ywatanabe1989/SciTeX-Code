#!/usr/bin/env python3
"""
SciTeX Stats Module - Professional Statistical Testing Framework

Clean, normalized API for statistical analysis with publication-ready outputs.

Organized submodules:
- tests: 16 statistical tests (parametric, nonparametric, normality, correlation, categorical)
- correct: 3 multiple comparison correction methods
- effect_sizes: Effect size computations and interpretations
- power: Statistical power analysis
- utils: Formatters and normalizers (for backward compatibility)
"""

# Import new organized submodules
from . import tests
from . import correct
from . import effect_sizes
from . import power
from . import utils
from . import posthoc
from . import descriptive

__all__ = [
    # Main submodules
    "tests",
    "correct",
    "effect_sizes",
    "power",
    "utils",
    "posthoc",
    "descriptive",
]

__version__ = "2.0.0"
