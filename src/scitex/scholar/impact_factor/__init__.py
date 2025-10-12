#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Impact factor module - Journal-level metrics for Scholar.

Provides two methods:
1. JCR database lookup (fast, requires JCR data) - jcr/
2. Citation-based estimation (slower, no data needed) - estimation/ (under development)

Data location: src/scitex/scholar/data/impact_factor/ (gitignored)
"""

from .ImpactFactorEngine import ImpactFactorEngine, get_journal_metrics

__all__ = [
    "ImpactFactorEngine",
    "get_journal_metrics",
]

# EOF
