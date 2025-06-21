#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-19 15:36:54 (ywatanabe)"
# File: /ssh:ywatanabe@sp:/home/ywatanabe/proj/scitex_repo/src/scitex/plt/_subplots/_AxesWrapper.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/plt/_subplots/_AxesWrapper.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from functools import wraps

import numpy as np
import pandas as pd


class AxesWrapper:
    def __init__(self, fig_scitex, axes_scitex):
        self._fig_scitex = fig_scitex
        self._axes_scitex = axes_scitex

    def get_figure(self, root=True):
        """Get the figure, compatible with matplotlib 3.8+"""
        return self._fig_scitex

    def __dir__(self):
        # Combine attributes from both self and the wrapped matplotlib axes
        attrs = set(dir(self.__class__))
        attrs.update(object.__dir__(self))

        # Add attributes from the axes objects if available
        if hasattr(self, "_axes_scitex") and self._axes_scitex is not None:
            # Get attributes from the first axis if there are any
            if self._axes_scitex.size > 0:
                first_ax = self._axes_scitex.flat[0]
                attrs.update(dir(first_ax))

        return sorted(attrs)

    def __getattr__(self, name):
        # Note that self._axes_scitex is "numpy.ndarray"
        # print(f"Attribute of AxesWrapper: {name}")
        methods = []
        try:
            for axis in self._axes_scitex.flat:
                methods.append(getattr(axis, name))
        except Exception:
            methods = []

        if methods and all(callable(m) for m in methods):

            @wraps(methods[0])
            def wrapper(*args, **kwargs):
                return [
                    getattr(ax, name)(*args, **kwargs)
                    for ax in self._axes_scitex.flat
                ]

            return wrapper

        if methods and not callable(methods[0]):
            return methods

        def dummy(*args, **kwargs):
            return None

        return dummy

    # def __getitem__(self, index):
    #     subset = self._axes_scitex[index]
    #     if isinstance(index, slice):
    #         return AxesWrapper(self._fig_scitex, subset)
    #     return subset

    def __getitem__(self, index):
        subset = self._axes_scitex[index]
        if isinstance(subset, np.ndarray):
            return AxesWrapper(self._fig_scitex, subset)
        return subset

    def __setitem__(self, index, value):
        """Support item assignment for axes[row, col] = new_axis operations."""
        self._axes_scitex[index] = value

    def __iter__(self):
        return iter(self._axes_scitex)

    def __len__(self):
        return self._axes_scitex.size

    def __array__(self):
        """Support conversion to numpy array.

        This allows using np.array(axes) on an AxesWrapper instance, returning
        a NumPy array with the same shape as the original axes array.

        Notes:
            - While this enables compatibility with NumPy functions, not all
              operations will work correctly due to the nature of the wrapped
              objects.
            - For flattening operations, use the dedicated `flatten()` method
              instead of `np.array(axes).flatten()`:

                  # RECOMMENDED:
                  flat_axes = list(axes.flatten())

                  # AVOID (may cause "invalid __array_struct__" error):
                  flat_axes = np.array(axes).flatten()

        Returns:
            np.ndarray: Array of wrapped axes with the same shape
        """
        import warnings

        # Show a warning to help users avoid common mistakes
        warnings.warn(
            "Converting AxesWrapper to numpy array. If you're trying to flatten "
            "the axes, use 'list(axes.flatten())' instead of 'np.array(axes).flatten()'.",
            UserWarning,
            stacklevel=2,
        )

        # Convert the underlying axes to a compatible numpy array representation
        flat_axes = [ax for ax in self._axes_scitex.flat]
        array_compatible = np.empty(len(flat_axes), dtype=object)
        for idx, ax in enumerate(flat_axes):
            array_compatible[idx] = ax
        return array_compatible.reshape(self._axes_scitex.shape)

    def legend(self, loc="upper left"):
        return [ax.legend(loc=loc) for ax in self._axes_scitex.flat]

    @property
    def history(self):
        return [ax.history for ax in self._axes_scitex.flat]

    @property
    def shape(self):
        return self._axes_scitex.shape

    @property
    def flat(self):
        """Return a flat iterator over all axes.
        
        This property provides direct access to the flattened axes array,
        matching numpy array behavior.
        
        Returns:
            Iterator over all axes in row-major (C-style) order
        """
        return self._axes_scitex.flat

    def flatten(self):
        """Return a flattened array of all axes in the AxesWrapper.

        This method collects all axes from the flat iterator and returns them
        as a NumPy array. This ensures compatibility with code that expects
        a flat collection of axes.

        Returns:
            np.ndarray: A flattened array containing all axes

        Example:
            # Preferred way to get a list of all axes:
            axes_list = list(axes.flatten())

            # Alternatively, if you need a NumPy array:
            axes_array = axes.flatten()
        """
        return np.array([ax for ax in self._axes_scitex.flat])

    def export_as_csv(self):
        dfs = []
        for ii, ax in enumerate(self._axes_scitex.flat):
            df = ax.export_as_csv()
            df.columns = [f"ax_{ii:02d}_{col}" for col in df.columns]
            dfs.append(df)
        return pd.concat(dfs, axis=1) if dfs else pd.DataFrame()

# EOF
