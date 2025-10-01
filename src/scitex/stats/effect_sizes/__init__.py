#!/usr/bin/env python3
# File: ./scitex_repo/src/scitex/stats/effect_sizes/__init__.py

"""
Effect size measures for statistical tests.

Effect sizes quantify the magnitude of differences or associations,
complementing statistical significance with practical importance.
"""

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

__all__ = [
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
]
