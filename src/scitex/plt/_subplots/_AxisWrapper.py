#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-01 17:11:28 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/plt/_subplots/_AxisWrapper.py
# ----------------------------------------
import os

__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import warnings
from functools import wraps

import matplotlib

from ._AxisWrapperMixins import (
    AdjustmentMixin,
    MatplotlibPlotMixin,
    SeabornMixin,
    TrackingMixin,
    UnitAwareMixin,
)


class AxisWrapper(MatplotlibPlotMixin, SeabornMixin, AdjustmentMixin, TrackingMixin, UnitAwareMixin):
    def __init__(self, fig_scitex, axis_mpl, track):
        """Initialize the AxisWrapper.
        
        Args:
            fig_scitex: Parent figure wrapper
            axis_mpl: Matplotlib axis to wrap
            track: Whether to track plotting operations
        """
        self._fig_mpl = fig_scitex._fig_mpl
        # Axis Properties
        # self.axis = axis_mpl
        # self._axis = axis_mpl
        # self._axis_scitex = self
        self._axis_mpl = axis_mpl

        # Axes Properties
        # self.axes = axis_mpl
        # self._axes = axis_mpl
        self._axes_mpl = axis_mpl
        # self._axes_scitex = self

        # Tracking properties
        self._ax_history = {}
        self._method_counters = {}  # Track method counts for auto-generated IDs
        self.track = track
        self.id = 0
        self._counter_part = matplotlib.axes.Axes
        
        # Initialize unit awareness
        UnitAwareMixin.__init__(self)

    def get_figure(self, root=True):
        """Get the figure, compatible with matplotlib 3.8+"""
        return self._fig_mpl
    
    def twinx(self):
        """Create a twin y-axis and wrap it with AxisWrapper."""
        twin_ax = self._axes_mpl.twinx()
        # Create a mock figure wrapper for the twin axis
        class MockFigWrapper:
            def __init__(self, fig_mpl):
                self._fig_mpl = fig_mpl
        mock_fig = MockFigWrapper(self._fig_mpl)
        return AxisWrapper(fig_scitex=mock_fig, axis_mpl=twin_ax, track=self.track)
    
    def twiny(self):
        """Create a twin x-axis and wrap it with AxisWrapper."""
        twin_ax = self._axes_mpl.twiny()
        # Create a mock figure wrapper for the twin axis
        class MockFigWrapper:
            def __init__(self, fig_mpl):
                self._fig_mpl = fig_mpl
        mock_fig = MockFigWrapper(self._fig_mpl)
        return AxisWrapper(fig_scitex=mock_fig, axis_mpl=twin_ax, track=self.track)

    def __getattr__(self, name):
        # 0. Check if the attribute is explicitly defined in AxisWrapper or its Mixins
        #    This check happens implicitly before __getattr__ is called.
        #    If a method like `plot` is defined in BasicPlotMixin, it will be found first.

        # print(f"Attribute of AxisWrapper: {name}")

        # 1. Try to get the attribute from the wrapped axes instance
        if hasattr(self._axes_mpl, name):
            orig_attr = getattr(self._axes_mpl, name)

            if callable(orig_attr):

                @wraps(orig_attr)
                def wrapper(*args, **kwargs):
                    id_value = kwargs.pop("id", None)
                    track_override = kwargs.pop("track", None)

                    # Call the original matplotlib method
                    result = orig_attr(*args, **kwargs)

                    # Determine if tracking should occur
                    should_track = (
                        track_override if track_override is not None else self.track
                    )

                    # Track the method call if tracking enabled
                    # Expanded list of matplotlib plotting methods to track
                    tracking_methods = {
                        # Basic plots
                        'plot', 'scatter', 'bar', 'barh', 'hist', 'boxplot', 'violinplot',
                        # Line plots
                        'fill_between', 'fill_betweenx', 'errorbar', 'step', 'stem',
                        # Statistical plots  
                        'hist2d', 'hexbin', 'pie',
                        # Contour plots
                        'contour', 'contourf', 'tricontour', 'tricontourf',
                        # Image plots
                        'imshow', 'matshow', 'spy',
                        # Quiver plots
                        'quiver', 'streamplot',
                        # 3D-related (if axes3d)
                        'plot3D', 'scatter3D', 'bar3d', 'plot_surface', 'plot_wireframe',
                        # Text and annotations (data-containing)
                        'annotate', 'text'
                    }
                    if should_track and name in tracking_methods:
                        # Use the _track method from TrackingMixin
                        # If no id provided, it will auto-generate one
                        try:
                            # Convert args to tracked_dict for consistency with other tracking
                            tracked_dict = {"args": args}
                            self._track(
                                should_track, id_value, name, tracked_dict, kwargs
                            )
                        except AttributeError:
                            warnings.warn(
                                f"Tracking setup incomplete for AxisWrapper ({name}).",
                                UserWarning,
                                stacklevel=2,
                            )
                        except Exception as e:
                            # Silently continue if tracking fails to not break plotting
                            pass
                    return result  # Return the result of the original call

                return wrapper
            else:
                # If it's a non-callable attribute (property, etc.), return it directly
                return orig_attr

        # 2. If not found on instance, try the counterpart type (fallback)
        if hasattr(self._counter_part, name):
            counterpart_attr = getattr(self._counter_part, name)
            warnings.warn(
                f"SciTeX Axis_MplWrapper: '{name}' not directly handled. "
                f"Falling back to underlying '{self._counter_part.__name__}' attribute.",
                UserWarning,
                stacklevel=2,
            )
            # If the counterpart attribute is callable (likely a method descriptor)
            if callable(counterpart_attr):
                # Return a new function that calls the counterpart method on self._axes_mpl
                @wraps(counterpart_attr)
                def fallback_method(*args, **kwargs):
                    # Note: No id/track handling for fallback methods
                    return counterpart_attr(self._axes_mpl, *args, **kwargs)

                return fallback_method
            else:
                # Non-callable class attribute. Attempt to get from instance again,
                # otherwise return the class attribute/descriptor.
                try:
                    return getattr(self._axes_mpl, name)
                except AttributeError:
                    return counterpart_attr

        # 3. If not found anywhere, raise AttributeError
        raise AttributeError(
            f"'{type(self).__name__}' object and its underlying '{self._counter_part.__name__}' "
            f"have no attribute '{name}'"
        )

    def __dir__(self):
        # Start with attributes from the class and all parent classes (mixins)
        attrs = set()
        
        # Get attributes from all parent classes including mixins
        for cls in self.__class__.__mro__:
            attrs.update(cls.__dict__.keys())
        
        # Add instance attributes
        attrs.update(self.__dict__.keys())
        
        # Safely get matplotlib axes attributes
        try:
            # Get attributes from the wrapped matplotlib axes
            if hasattr(self._axes_mpl, '__class__'):
                # Get class methods from matplotlib.axes.Axes
                for cls in self._axes_mpl.__class__.__mro__:
                    attrs.update(name for name in cls.__dict__.keys() if not name.startswith('_'))
            
            # Add instance attributes of the matplotlib axes
            if hasattr(self._axes_mpl, '__dict__'):
                attrs.update(name for name in self._axes_mpl.__dict__.keys() if not name.startswith('_'))
                
        except Exception:
            # If any error occurs, add common matplotlib methods manually
            attrs.update(['plot', 'scatter', 'bar', 'barh', 'hist', 'boxplot', 
                         'set_xlabel', 'set_ylabel', 'set_title', 'legend',
                         'set_xlim', 'set_ylim', 'grid', 'annotate', 'text'])
        
        # Remove private attributes
        attrs = {attr for attr in attrs if not attr.startswith('_')}
        
        return sorted(attrs)
        
    def flatten(self):
        """Return a list containing just this axis.
        
        This method makes AxisWrapper compatible with code that calls flatten()
        on an axes collection. It returns a list containing just this single axis
        to maintain consistency with AxesWrapper.flatten().
        
        Returns:
            list: A list containing this axis wrapper
            
        Example:
            # When working with either AxesWrapper or AxisWrapper, this works:
            axes_list = list(axes.flatten())
        """
        return [self]


"""
import matplotlib.pyplot as plt
import scitex.plt as mplt

fig_scitex, axes = plt.subplots(ncols=2)
mfig_scitex, maxes = mplt.subplots(ncols=2)

print(set(dir(mfig_scitex)) - set(dir(fig_scitex)))
print(set(dir(maxes)) - set(dir(axes)))

is_compatible = np.all([kk in set(dir(msubplots)) for kk in set(dir(counter_part))])
if is_compatible:
    print(f"{msubplots.__name__} is compatible with {counter_part.__name__}")
else:
    print(f"{msubplots.__name__} is incompatible with {counter_part.__name__}")
"""

# EOF
