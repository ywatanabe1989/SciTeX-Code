#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-29 03:46:53 (ywatanabe)"
# File: /ssh:ywatanabe@sp:/home/ywatanabe/proj/scitex_repo/src/scitex/plt/_subplots/_SubplotsWrapper.py
# ----------------------------------------
import os

__FILE__ = "./src/scitex/plt/_subplots/_SubplotsWrapper.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from collections import OrderedDict

import matplotlib.pyplot as plt
import numpy as np

from ._AxesWrapper import AxesWrapper
from ._AxisWrapper import AxisWrapper
from ._FigWrapper import FigWrapper


class SubplotsWrapper:
    """
    A wrapper class monitors data plotted using the ax methods from matplotlib.pyplot.
    This data can be converted into a CSV file formatted for SigmaPlot compatibility.
    """

    def __init__(self):
        self._subplots_wrapper_history = OrderedDict()
        self._fig_scitex = None
        self._counter_part = plt.subplots

    def __call__(self, *args, track=True, sharex=False, sharey=False, constrained_layout=None, **kwargs):

        # If constrained_layout is not specified, use it by default for better colorbar handling
        if constrained_layout is None and 'layout' not in kwargs:
            # Use a dict to set padding parameters for better spacing
            # Increased w_pad to prevent colorbar overlap
            kwargs['constrained_layout'] = {'w_pad': 0.1, 'h_pad': 0.1, 'wspace': 0.05, 'hspace': 0.05}
            
        # Start from the original matplotlib figure and axes
        self._fig_mpl, self._axes_mpl = self._counter_part(
            *args, sharex=sharex, sharey=sharey, **kwargs
        )

        # Wrap the figure
        self._fig_scitex = FigWrapper(self._fig_mpl)

        # Ensure axes_mpl is always an array
        axes_array_mpl = np.atleast_1d(self._axes_mpl)
        axes_shape_mpl = axes_array_mpl.shape

        # Handle single axis case
        if axes_array_mpl.size == 1:
            # Use squeeze() to get the scalar Axes object if it's a 0-d array
            ax_mpl_scalar = (
                axes_array_mpl.item() if axes_array_mpl.ndim == 0 else axes_array_mpl[0]
            )
            self._axis_scitex = AxisWrapper(self._fig_scitex, ax_mpl_scalar, track)
            self._fig_scitex.axes = np.atleast_1d([self._axis_scitex])
            return self._fig_scitex, self._axis_scitex

        # Handle multiple axes case
        axes_flat_mpl = axes_array_mpl.ravel()
        axes_flat_scitex_list = [
            AxisWrapper(self._fig_scitex, ax_, track) for ax_ in axes_flat_mpl
        ]

        # Reshape the axes_flat_scitex_list axes to match the original layout
        axes_array_scitex = np.array(axes_flat_scitex_list).reshape(axes_shape_mpl)

        # Wrap the array of axes
        self._axes_scitex = AxesWrapper(self._fig_scitex, axes_array_scitex)
        self._fig_scitex.axes = self._axes_scitex
        return self._fig_scitex, self._axes_scitex

    # def __getattr__(self, name):
    #     """
    #     Fallback to fetch attributes from the original matplotlib.pyplot.subplots function
    #     if they are not defined directly in this wrapper instance.
    #     This allows accessing attributes like __name__, __doc__ etc. from the original function.
    #     """
    #     print(f"Attribute of SubplotsWrapper: {name}")
    #     # Check if the attribute exists in the counterpart function
    #     if hasattr(self._counter_part, name):
    #         return getattr(self._counter_part, name)
    #     # Raise the standard error if not found in the wrapper or the counterpart
    #     raise AttributeError(
    #         f"'{type(self).__name__}' object and its counterpart '{self._counter_part.__name__}' have no attribute '{name}'"
    #     )

    def __dir__(
        self,
    ):
        """
        Provide combined directory for tab completion, including
        attributes from this wrapper and the original matplotlib.pyplot.subplots function.
        """
        # Get attributes defined explicitly in this instance/class
        local_attrs = set(super().__dir__())
        # Get attributes from the counterpart function
        try:
            counterpart_attrs = set(dir(self._counter_part))
        except Exception:
            counterpart_attrs = set()
        # Return the sorted union
        return sorted(local_attrs.union(counterpart_attrs))


# Instantiate the wrapper. This instance will be imported and used.
subplots = SubplotsWrapper()

if __name__ == "__main__":
    import matplotlib
    import scitex

    matplotlib.use("TkAgg")  # "TkAgg"

    fig, ax = subplots()
    ax.plot([1, 2, 3], [4, 5, 6], id="plot1")
    ax.plot([4, 5, 6], [1, 2, 3], id="plot2")
    scitex.io.save(fig, "/tmp/subplots_demo/plots.png")

    # Behaves like native matplotlib.pyplot.subplots without tracking
    fig, ax = subplots(track=False)
    ax.plot([1, 2, 3], [4, 5, 6], id="plot3")
    ax.plot([4, 5, 6], [1, 2, 3], id="plot4")
    scitex.io.save(fig, "/tmp/subplots_demo/plots.png")

    fig, ax = subplots()
    ax.scatter([1, 2, 3], [4, 5, 6], id="scatter1")
    ax.scatter([4, 5, 6], [1, 2, 3], id="scatter2")
    scitex.io.save(fig, "/tmp/subplots_demo/scatters.png")

    fig, ax = subplots()
    ax.boxplot([1, 2, 3], id="boxplot1")
    scitex.io.save(fig, "/tmp/subplots_demo/boxplot1.png")

    fig, ax = subplots()
    ax.bar(["A", "B", "C"], [4, 5, 6], id="bar1")
    scitex.io.save(fig, "/tmp/subplots_demo/bar1.png")

    print(ax.export_as_csv())
    #    plot1_plot_x  plot1_plot_y  plot2_plot_x  ...  boxplot1_boxplot_x  bar1_bar_x  bar1_bar_y
    # 0           1.0           4.0           4.0  ...                 1.0           A         4.0
    # 1           2.0           5.0           5.0  ...                 2.0           B         5.0
    # 2           3.0           6.0           6.0  ...                 3.0           C         6.0

    print(ax.export_as_csv().keys())  # plot3 and plot 4 are not tracked
    # [3 rows x 11 columns]
    # Index(['plot1_plot_x', 'plot1_plot_y', 'plot2_plot_x', 'plot2_plot_y',
    #        'scatter1_scatter_x', 'scatter1_scatter_y', 'scatter2_scatter_x',
    #        'scatter2_scatter_y', 'boxplot1_boxplot_x', 'bar1_bar_x', 'bar1_bar_y'],
    #       dtype='object')

    # If a path is passed, the sigmaplot-friendly dataframe is saved as a csv file.
    ax.export_as_csv("./tmp/subplots_demo/for_sigmaplot.csv")
    # Saved to: ./tmp/subplots_demo/for_sigmaplot.csv

"""
from matplotlib.pyplot import subplots as counter_part
from scitex.plt import subplots as msubplots
print(set(dir(msubplots)) - set(dir(counter_part)))
is_compatible = np.all([kk in set(dir(msubplots)) for kk in set(dir(counter_part))])
if is_compatible:
    print(f"{msubplots.__name__} is compatible with {counter_part.__name__}")
else:
    print(f"{msubplots.__name__} is incompatible with {counter_part.__name__}")
"""

# EOF
