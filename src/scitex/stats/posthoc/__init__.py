#!/usr/bin/env python3
# File: ./scitex_repo/src/scitex/stats/posthoc/__init__.py

"""
Post-hoc tests for pairwise comparisons after ANOVA.

Methods for conducting multiple pairwise comparisons with appropriate
error rate control.
"""

from ._tukey_hsd import posthoc_tukey
from ._games_howell import posthoc_games_howell
from ._dunnett import posthoc_dunnett

__all__ = [
    'posthoc_tukey',
    'posthoc_games_howell',
    'posthoc_dunnett',
]
