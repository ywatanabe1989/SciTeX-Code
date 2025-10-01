#!/usr/bin/env python3
# File: ./scitex_repo/src/scitex/stats/utils/__init__.py

"""
Statistical utilities.

Helper functions for effect sizes, power analysis, formatting, and data normalization.
"""

# Effect sizes
from ._effect_size import (
    cohens_d,
    cliffs_delta,
    prob_superiority,
    eta_squared,
    epsilon_squared,
    interpret_cohens_d,
    interpret_cliffs_delta,
    interpret_prob_superiority,
    interpret_eta_squared,
    interpret_epsilon_squared,
)

# Power analysis
from ._power import (
    power_ttest,
    sample_size_ttest,
)

# Formatters
from ._formatters import (
    p2stars,
)

# Normalizers
from ._normalizers import (
    force_dataframe,
)

__all__ = [
    # Effect sizes
    'cohens_d',
    'cliffs_delta',
    'prob_superiority',
    'eta_squared',
    'epsilon_squared',
    'interpret_cohens_d',
    'interpret_cliffs_delta',
    'interpret_prob_superiority',
    'interpret_eta_squared',
    'interpret_epsilon_squared',

    # Power analysis
    'power_ttest',
    'sample_size_ttest',

    # Formatters
    'p2stars',

    # Normalizers
    'force_dataframe',
]
