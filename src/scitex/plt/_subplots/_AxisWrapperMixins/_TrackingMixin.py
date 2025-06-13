#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-04-30 18:40:59 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/plt/_subplots/_AxisWrapperMixins/_TrackingMixin.py
# ----------------------------------------
import os

__FILE__ = "./src/scitex/plt/_subplots/_AxisWrapperMixins/_TrackingMixin.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionality:
    * Handles tracking and history management for matplotlib plot operations
Input:
    * Plot method calls, their arguments, and tracking configuration
Output:
    * Tracked plotting history and DataFrame export for analysis
Prerequisites:
    * pandas, matplotlib
"""

from contextlib import contextmanager

import pandas as pd

from .._export_as_csv import export_as_csv as _export_as_csv


class TrackingMixin:
    """Mixin class for tracking matplotlib plotting operations.

    Example
    -------
    >>> fig, ax = plt.subplots()
    >>> ax.track = True
    >>> ax.id = 0
    >>> ax._ax_history = OrderedDict()
    >>> ax.plot([1, 2, 3], [4, 5, 6], id="plot1")
    >>> print(ax.history)
    {'plot1': ('plot1', 'plot', {'plot_df': DataFrame, ...}, {})}
    """

    def _track(self, track, id, method_name, tracked_dict, kwargs=None):
        """Track plotting operation with auto-generated IDs.
        
        Args:
            track: Whether to track this operation
            id: Identifier for the plot (can be None)
            method_name: Name of the plotting method
            tracked_dict: Dictionary of tracked data
            kwargs: Original keyword arguments
        """
        # Extract id from kwargs and remove it before passing to matplotlib
        if kwargs is not None and hasattr(kwargs, "get") and "id" in kwargs:
            id = kwargs.pop("id")
        
        # Default kwargs to empty dict if None
        if kwargs is None:
            kwargs = {}

        if track is None:
            track = self.track

        if track:
            # If no ID was provided, generate one using method_name + counter
            if id is None:
                # Initialize method counters if not exist
                if not hasattr(self, '_method_counters'):
                    self._method_counters = {}
                
                # Get current counter value for this method and increment it
                counter = self._method_counters.get(method_name, 0)
                self._method_counters[method_name] = counter + 1
                
                # Format ID as method_name_counter (e.g., bar_1, plot_3)
                id = f"{method_name}_{counter}"
            
            # For backward compatibility
            self.id += 1
            
            # Store the tracking record
            self._ax_history[id] = (id, method_name, tracked_dict, kwargs)

    @contextmanager
    def _no_tracking(self):
        """Context manager to temporarily disable tracking."""
        original_track = self.track
        self.track = False
        try:
            yield
        finally:
            self.track = original_track

    @property
    def history(self):
        return {k: self._ax_history[k] for k in self._ax_history}

    @property
    def flat(self):
        if isinstance(self._axis_mpl, list):
            return self._axis_mpl
        else:
            return [self._axis_mpl]

    def reset_history(self):
        self._ax_history = {}

    def export_as_csv(self):
        """
        Export tracked plotting data to a DataFrame.
        """
        df = _export_as_csv(self.history)

        return df if df is not None else pd.DataFrame()
    
    def export_as_csv_for_sigmaplot(self, include_visual_params=True):
        """
        Export tracked plotting data to a DataFrame in SigmaPlot format.
        
        Parameters
        ----------
        include_visual_params : bool, optional
            Whether to include visual parameters (xlabel, ylabel, scales, etc.)
            at the top of the CSV. Default is True.
            
        Returns
        -------
        pandas.DataFrame
            DataFrame containing the plotted data formatted for SigmaPlot.
            
        Examples
        --------
        >>> fig, ax = scitex.plt.subplots()
        >>> ax.plot([1, 2, 3], [4, 5, 6])
        >>> ax.scatter([1, 2, 3], [7, 8, 9])
        >>> df = ax.export_as_csv_for_sigmaplot()
        >>> df.to_csv('for_sigmaplot.csv', index=False)
        """
        df = _export_as_csv(self.history)
        
        return df if df is not None else pd.DataFrame()

    # def _track(
    #     self,
    #     track: Optional[bool],
    #     plot_id: Optional[str],
    #     method_name: str,
    #     tracked_dict: Any,
    #     kwargs: Dict[str, Any]
    # ) -> None:
    #     """Tracks plotting operation if tracking is enabled."""
    #     if track is None:
    #         track = self.track
    #     if track:
    #         plot_id = plot_id if plot_id is not None else self.id
    #         self.id += 1
    #         self._ax_history[plot_id] = (plot_id, method_name, tracked_dict, kwargs)

    # @contextmanager
    # def _no_tracking(self) -> None:
    #     """Temporarily disables tracking within a context."""
    #     original_track = self.track
    #     self.track = False
    #     try:
    #         yield
    #     finally:
    #         self.track = original_track

    # @property
    # def history(self) -> Dict[str, Tuple]:
    #     """Returns the plotting history."""
    #     return dict(self._ax_history)

    # def reset_history(self) -> None:
    #     """Clears the plotting history."""
    #     self._ax_history = OrderedDict()

    # def export_as_csv(self) -> pd.DataFrame:
    #     """Converts plotting history to a SigmaPlot-compatible DataFrame."""
    #     df = _export_as_csv(self.history)
    #     return df if df is not None else pd.DataFrame()


# EOF
