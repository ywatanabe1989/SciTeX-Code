#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Feature selection utilities for machine learning.

This module provides comprehensive feature selection and importance analysis:
- Feature importance extraction from various model types
- Univariate feature selection (ANOVA F-test, chi2, mutual_info)
- Model-based feature selection (tree importances, L1 coefficients)
- Cross-fold feature consistency analysis
- Feature importance aggregation and visualization
"""

from .feature_selection import (
    extract_feature_importance,
    select_features_univariate,
    analyze_feature_consistency,
    aggregate_feature_importances,
    create_feature_importance_dataframe,
)

__all__ = [
    "extract_feature_importance",
    "select_features_univariate",
    "analyze_feature_consistency",
    "aggregate_feature_importances",
    "create_feature_importance_dataframe",
]

# EOF
