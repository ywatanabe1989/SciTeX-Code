#!/usr/bin/env python3
# File: ./scitex_repo/src/scitex/stats/power/__init__.py

"""
Statistical power analysis.

Power analysis helps determine required sample sizes and assess
the probability of detecting true effects.
"""

from ._power import (
    power_ttest,
    sample_size_ttest,
)

__all__ = [
    'power_ttest',
    'sample_size_ttest',
]
