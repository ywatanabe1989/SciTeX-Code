#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Effect size computations for statistical tests.

This module provides functions to compute and interpret various effect size measures:

Parametric Effect Sizes:
- Cohen's d: Standardized mean difference for t-tests
- Eta-squared (η²): Proportion of variance explained in ANOVA

Non-parametric Effect Sizes:
- Cliff's delta (δ): Ordinal effect size
- Probability of superiority P(X>Y): Common language effect size
- Epsilon-squared (ε²): Non-parametric analog of eta-squared

Each effect size comes with an interpretation function following standard
guidelines (Cohen, 1988; McGraw & Wong, 1992).
"""

from ._cohens_d import cohens_d, interpret_cohens_d
from ._cliffs_delta import cliffs_delta, interpret_cliffs_delta
from ._prob_superiority import prob_superiority, interpret_prob_superiority
from ._eta_squared import eta_squared, interpret_eta_squared
from ._epsilon_squared import epsilon_squared, interpret_epsilon_squared

__all__ = [
    # Parametric
    'cohens_d',
    'interpret_cohens_d',
    'eta_squared',
    'interpret_eta_squared',

    # Non-parametric
    'cliffs_delta',
    'interpret_cliffs_delta',
    'prob_superiority',
    'interpret_prob_superiority',
    'epsilon_squared',
    'interpret_epsilon_squared',
]
