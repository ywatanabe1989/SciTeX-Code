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
        TimeSeriesStrategy
            Corresponding enum value
            
        Raises
        ------
        ValueError
            If value doesn't match any strategy
        """
        value_lower = value.lower()
        for strategy in cls:
            if strategy.value == value_lower:
                return strategy
        raise ValueError(
            f"Unknown strategy: {value}. "
            f"Valid options are: {[s.value for s in cls]}"
        )
    
    def get_description(self) -> str:
        """
        Get human-readable description of the strategy.
        
        Returns
        -------
        str
            Description of the strategy
        """
        descriptions = {
            self.STRATIFIED: "Maintains class balance while respecting time order",
            self.BLOCKING: "Handles multiple independent time series",
            self.SLIDING: "Uses fixed-size sliding windows through time",
            self.EXPANDING: "Training set expands while test moves forward",
            self.FIXED: "Single fixed split at specific time point"
        }
        return descriptions.get(self, "Unknown strategy")