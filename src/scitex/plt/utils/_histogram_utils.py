#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-18 18:14:26 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/utils/_histogram_utils.py
# ----------------------------------------
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import numpy as np
from typing import List, Tuple, Union, Optional, Dict

class HistogramBinManager:
    """
    Utility class to manage histogram bin alignment across multiple histograms.
    
    This class maintains a registry of histograms and their bin configurations
    for each axis, allowing histograms on the same axis to use consistent binning.
    
    Attributes:
        _axis_registry (Dict): Registry of bin configurations by axis ID
    """
    
    def __init__(self):
        self._axis_registry = {}
        
    def register_histogram(self, 
                          axis_id: str, 
                          hist_id: str, 
                          data: np.ndarray, 
                          bins: Union[int, str, np.ndarray] = 10,
                          range: Optional[Tuple[float, float]] = None):
        """
        Register a histogram with the bin manager.
        
        Args:
            axis_id (str): Identifier for the axis
            hist_id (str): Identifier for the histogram
            data (np.ndarray): The data array for the histogram
            bins (Union[int, str, np.ndarray]): Number of bins or bin edges
            range (Optional[Tuple[float, float]]): Range of the histogram
        
        Returns:
            Tuple[int, Tuple[float, float]]: Consistent bins and range for the axis
        """
        # Initialize registry for this axis if needed
        if axis_id not in self._axis_registry:
            self._axis_registry[axis_id] = {
                'histograms': {},
                'common_config': None
            }
        
        # Calculate data range if not provided
        if range is None:
            range = (np.min(data), np.max(data))
        
        # Store histogram info in registry
        self._axis_registry[axis_id]['histograms'][hist_id] = {
            'data': data,
            'bins': bins,
            'range': range
        }
        
        # Calculate common configuration if needed
        if self._axis_registry[axis_id]['common_config'] is None:
            self._update_common_config(axis_id)
        
        return self._axis_registry[axis_id]['common_config']
    
    def _update_common_config(self, axis_id: str):
        """
        Update the common bin configuration for an axis.
        
        Args:
            axis_id (str): Identifier for the axis
        """
        histograms = self._axis_registry[axis_id]['histograms']
        
        if not histograms:
            return
        
        # Find common range across all histograms on this axis
        min_val = min(hist['range'][0] for hist in histograms.values())
        max_val = max(hist['range'][1] for hist in histograms.values())
        
        # Use maximum number of bins from all histograms
        # (if any histogram uses a string or array for bins, this gets more complex)
        bins_values = [hist['bins'] for hist in histograms.values() 
                     if isinstance(hist['bins'], int)]
        
        # Default to 10 bins if no integer bin counts
        n_bins = max(bins_values) if bins_values else 10
        
        # Set common configuration
        self._axis_registry[axis_id]['common_config'] = (n_bins, (min_val, max_val))
        
    def get_common_config(self, axis_id: str) -> Tuple[int, Tuple[float, float]]:
        """
        Get the common bin configuration for an axis.
        
        Args:
            axis_id (str): Identifier for the axis
            
        Returns:
            Tuple[int, Tuple[float, float]]: Common bins and range for the axis
        """
        if axis_id in self._axis_registry:
            return self._axis_registry[axis_id]['common_config']
        
        # Default if axis not registered
        return (10, (0, 1))
        
    def clear_axis(self, axis_id: str):
        """
        Clear registry for a specific axis.
        
        Args:
            axis_id (str): Identifier for the axis to clear
        """
        if axis_id in self._axis_registry:
            del self._axis_registry[axis_id]
            
    def clear_all(self):
        """Clear the entire registry."""
        self._axis_registry = {}


# Global instance
histogram_bin_manager = HistogramBinManager()