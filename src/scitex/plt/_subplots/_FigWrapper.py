#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-19 02:53:28 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/_subplots/_FigWrapper.py.new
# ----------------------------------------
import os

__FILE__ = "./src/scitex/plt/_subplots/_FigWrapper.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from functools import wraps
import warnings
import numpy as np
import pandas as pd


class FigWrapper:
    def __init__(self, fig_mpl):
        self._fig_mpl = fig_mpl
        self._last_saved_info = None
        self._not_saved_yet_flag = True
        self._called_from_mng_io_save = False

    @property
    def figure(
        self,
    ):
        return self._fig_mpl

    def __getattr__(self, attr):
        # print(f"Attribute of FigWrapper: {attr}")
        attr_mpl = getattr(self._fig_mpl, attr)

        if callable(attr_mpl):

            @wraps(attr_mpl)
            def wrapper(*args, track=None, id=None, **kwargs):
                results = attr_mpl(*args, **kwargs)
                # self._track(track, id, attr, args, kwargs)
                return results

            return wrapper

        else:
            return attr_mpl

    def __dir__(self):
        # Combine attributes from both self and the wrapped matplotlib figure
        attrs = set(dir(self.__class__))
        attrs.update(object.__dir__(self))
        attrs.update(dir(self._fig_mpl))
        return sorted(attrs)

    # def savefig(self, fname, *args, **kwargs):
    #     if not self._called_from_mng_io_save:
    #         warnings.warn(
    #             f"Instead of `FigWrapper.savefig({fname})`, use `scitex.io.save(fig, {fname}, symlink_from_cwd=True)` to handle symlink and export as csv.",
    #             UserWarning,
    #         )
    #         self._called_from_mng_io_save = False
    #     self._fig_mpl.savefig(fname, *args, **kwargs)

    def export_as_csv(self):
        """Export plotted data from all axes.
        
        This method collects data from all axes in the figure and combines 
        them into a single DataFrame with appropriate axis identifiers in 
        the column names.
        
        Returns:
            pd.DataFrame: Combined DataFrame with data from all axes,
                          with axis ID prefixes for each column.
        """
        dfs = []
        
        # Use the _traverse_axes helper method to iterate through all axes
        # regardless of their structure (single, array, list, etc.)
        for ii, ax in enumerate(self._traverse_axes()):
            # Try different ways to access the export_as_csv method
            df = None
            try:
                if hasattr(ax, '_axis_mpl') and hasattr(ax._axis_mpl, 'export_as_csv'):
                    # If it's a nested structure with _axis_mpl having export_as_csv
                    df = ax._axis_mpl.export_as_csv()
                elif hasattr(ax, 'export_as_csv'):
                    # Direct AxisWrapper object
                    df = ax.export_as_csv()
                else:
                    # Skip if no export method available
                    continue
            except Exception:
                continue
            
            # Process the DataFrame if it's not empty
            if df is not None and not df.empty:
                # Add axis ID prefix to column names if not already present
                prefix = f"ax_{ii:02d}_"
                df.columns = [
                    col if col.startswith(prefix) else f"{prefix}{col}" 
                    for col in df.columns
                ]
                dfs.append(df)
        
        # Return concatenated DataFrame or empty DataFrame if no data
        return pd.concat(dfs, axis=1) if dfs else pd.DataFrame()
    
    def _traverse_axes(self):
        """Helper method to traverse all axis wrappers in the figure."""
        if hasattr(self, 'axes'):
            # Check if we're dealing with an AxesWrapper instance
            if hasattr(self.axes, '_axes_scitex') and hasattr(self.axes._axes_scitex, 'flat'):
                # This is an AxesWrapper, get the individual AxisWrapper objects
                for ax in self.axes._axes_scitex.flat:
                    yield ax
            elif not hasattr(self.axes, '__iter__'):
                # Single axis case
                yield self.axes
            else:
                # Multiple axes case
                if hasattr(self.axes, 'flat'):
                    # 2D array of axes
                    for ax in self.axes.flat:
                        yield ax
                elif hasattr(self.axes, 'ravel'):
                    # Numpy array
                    for ax in self.axes.ravel():
                        yield ax
                elif isinstance(self.axes, (list, tuple)):
                    # List of axes
                    for ax in self.axes:
                        yield ax

    def legend(self, *args, loc="upper left", **kwargs):
        """Legend with upper left by default for all axes."""
        for ax in self._traverse_axes():
            try:
                ax.legend(*args, loc=loc, **kwargs)
            except Exception as e:
                pass

    def supxyt(self, x=False, y=False, t=False):
        """Wrapper for supxlabel, supylabel, and suptitle"""
        if x is not False:
            self._fig_mpl.supxlabel(x)
        if y is not False:
            self._fig_mpl.supylabel(y)
        if t is not False:
            self._fig_mpl.suptitle(t)
        return self._fig_mpl

    def tight_layout(self, *, rect=[0, 0.03, 1, 0.95], **kwargs):
        """Wrapper for tight_layout with rect=[0, 0.03, 1, 0.95] by default.
        
        Handles cases where certain axes (like colorbars) are incompatible
        with tight_layout. If the figure is using constrained_layout, this
        method does nothing as constrained_layout handles spacing automatically.
        """
        import warnings
        
        # Check if figure is already using constrained_layout
        if hasattr(self._fig_mpl, 'get_constrained_layout') and self._fig_mpl.get_constrained_layout():
            # Figure is using constrained_layout, which handles colorbars better
            # No need to call tight_layout
            return
        
        try:
            with warnings.catch_warnings():
                # Suppress the specific warning about incompatible axes
                warnings.filterwarnings("ignore", 
                                      message="This figure includes Axes that are not compatible with tight_layout")
                self._fig_mpl.tight_layout(rect=rect, **kwargs)
        except Exception:
            # If tight_layout fails completely, try constrained_layout as fallback
            try:
                self._fig_mpl.set_constrained_layout(True)
                self._fig_mpl.set_constrained_layout_pads(w_pad=0.04, h_pad=0.04)
            except Exception:
                # If both fail, do nothing - figure will use default layout
                pass

    def adjust_layout(self, **kwargs):
        """Adjust the constrained layout parameters.
        
        Parameters
        ----------
        w_pad : float, optional
            Width padding around axes (default: 0.05)
        h_pad : float, optional
            Height padding around axes (default: 0.05)
        wspace : float, optional
            Width space between subplots (default: 0.02)
        hspace : float, optional
            Height space between subplots (default: 0.02)
        rect : list of 4 floats, optional
            Rectangle in normalized figure coordinates to fit the whole layout
            [left, bottom, right, top] (default: [0, 0, 1, 1])
        """
        if hasattr(self._fig_mpl, 'get_constrained_layout') and self._fig_mpl.get_constrained_layout():
            # Update constrained layout parameters
            self._fig_mpl.set_constrained_layout_pads(**kwargs)
        else:
            # Fall back to tight_layout with rect parameter if provided
            if 'rect' in kwargs:
                self.tight_layout(rect=kwargs['rect'])
    
    def close(self):
        """Close the underlying matplotlib figure"""
        import matplotlib.pyplot as plt
        plt.close(self._fig_mpl)
    
    @property 
    def number(self):
        """Return the figure number for matplotlib.pyplot.close() compatibility"""
        return self._fig_mpl.number

    def __del__(self):
        """Cleanup when FigWrapper is deleted"""
        try:
            import matplotlib.pyplot as plt
            plt.close(self._fig_mpl)
        except:
            pass


# EOF
