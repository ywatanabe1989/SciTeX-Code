#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-01 19:32:38 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/tests/scitex/plt/ax/_plot/test__plot_statistical_shaded_line.py
# ----------------------------------------
import os

__FILE__ = "./tests/scitex/plt/ax/_plot/test__plot_statistical_shaded_line.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------


def test_plot_line_savefig():
    import matplotlib.pyplot as plt
    import numpy as np
    from scitex.plt.ax._plot import plot_line

    fig, ax = plt.subplots()
    data = np.sin(np.linspace(0, 10, 100))
    ax, df = plot_line(ax, data)

    # Saving
    from scitex.io import save

    spath = f"./{os.path.basename(__file__)}.jpg"
    save(fig, spath)

    # Check saved file
    ACTUAL_SAVE_DIR = __file__.replace(".py", "_out")
    actual_spath = os.path.join(ACTUAL_SAVE_DIR, spath)
    assert os.path.exists(actual_spath), f"Failed to save figure to {spath}"


def test_plot_mean_std_savefig():
    import matplotlib.pyplot as plt
    import numpy as np
    from scitex.plt.ax._plot import plot_mean_std

    fig, ax = plt.subplots()
    data = np.random.normal(0, 1, (10, 100))
    ax, df = plot_mean_std(ax, data, label="Test")

    # Saving
    from scitex.io import save

    spath = f"./{os.path.basename(__file__)}.jpg"
    save(fig, spath)

    # Check saved file
    ACTUAL_SAVE_DIR = __file__.replace(".py", "_out")
    actual_spath = os.path.join(ACTUAL_SAVE_DIR, spath)
    assert os.path.exists(actual_spath), f"Failed to save figure to {spath}"


def test_plot_mean_ci_savefig():
    import matplotlib.pyplot as plt
    import numpy as np
    from scitex.plt.ax._plot import plot_mean_ci

    fig, ax = plt.subplots()
    data = np.random.normal(0, 1, (10, 100))
    ax, df = plot_mean_ci(ax, data, label="Test")

    # Saving
    from scitex.io import save

    spath = f"./{os.path.basename(__file__)}.jpg"
    save(fig, spath)

    # Check saved file
    ACTUAL_SAVE_DIR = __file__.replace(".py", "_out")
    actual_spath = os.path.join(ACTUAL_SAVE_DIR, spath)
    assert os.path.exists(actual_spath), f"Failed to save figure to {spath}"


def test_plot_median_iqr_savefig():
    import matplotlib.pyplot as plt
    import numpy as np
    from scitex.plt.ax._plot import plot_median_iqr

    fig, ax = plt.subplots()
    data = np.random.normal(0, 1, (10, 100))
    ax, df = plot_median_iqr(ax, data, label="Test")

    # Saving
    from scitex.io import save

    spath = f"./{os.path.basename(__file__)}.jpg"
    save(fig, spath)

    # Check saved file
    ACTUAL_SAVE_DIR = __file__.replace(".py", "_out")
    actual_spath = os.path.join(ACTUAL_SAVE_DIR, spath)
    assert os.path.exists(actual_spath), f"Failed to save figure to {spath}"

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/plt/ax/_plot/_plot_statistical_shaded_line.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-04-30 20:50:45 (ywatanabe)"
# # File: /home/ywatanabe/proj/scitex_repo/src/scitex/plt/ax/_plot_statistical_shaded_line.py
# # ----------------------------------------
# import os
# 
# __FILE__ = "./src/scitex/plt/ax/_plot_statistical_shaded_line.py"
# __DIR__ = os.path.dirname(__FILE__)
# # ----------------------------------------
# 
# import matplotlib
# import numpy as np
# import pandas as pd
# from ....plt.utils import assert_valid_axis
# 
# from ._plot_shaded_line import plot_shaded_line as scitex_plt_plot_shaded_line
# 
# 
# def plot_line(axis, data, xx=None, **kwargs):
#     """
#     Plot a simple line.
#     
#     Parameters
#     ----------
#     axis : matplotlib.axes.Axes or scitex.plt._subplots.AxisWrapper
#         The axis to plot on
#     data : array-like
#         Data to plot
#     xx : array-like, optional
#         X coordinates for the data. If None, will use np.arange(len(data))
#     **kwargs
#         Additional keyword arguments passed to axis.plot()
#         
#     Returns
#     -------
#     axis : matplotlib.axes.Axes or scitex.plt._subplots.AxisWrapper
#         The axis with the plot
#     df : pandas.DataFrame
#         DataFrame with x and y values
#     """
#     assert_valid_axis(axis, "First argument must be a matplotlib axis or scitex axis wrapper")
#     data = np.asarray(data)
#     assert data.ndim <= 2, f"Data must be 1D or 2D, got {data.ndim}D"
#     if xx is None:
#         xx = np.arange(len(data))
#     else:
#         xx = np.asarray(xx)
#     assert len(xx) == len(
#         data
#     ), f"xx length ({len(xx)}) must match data length ({len(data)})"
#     axis.plot(xx, data, **kwargs)
#     return axis, pd.DataFrame({"x": xx, "y": data})
# 
# 
# def plot_mean_std(axis, data, xx=None, sd=1, **kwargs):
#     """
#     Plot mean line with standard deviation shading.
#     
#     Parameters
#     ----------
#     axis : matplotlib.axes.Axes or scitex.plt._subplots.AxisWrapper
#         The axis to plot on
#     data : array-like
#         Data to plot, can be 1D or 2D. If 2D, mean and std are calculated across the first dimension
#     xx : array-like, optional
#         X coordinates for the data. If None, will use np.arange(len(data))
#     sd : float, optional
#         Number of standard deviations for the shaded region. Default is 1
#     **kwargs
#         Additional keyword arguments passed to plot_shaded_line()
#         
#     Returns
#     -------
#     axis : matplotlib.axes.Axes or scitex.plt._subplots.AxisWrapper
#         The axis with the plot
#     """
#     assert_valid_axis(axis, "First argument must be a matplotlib axis or scitex axis wrapper")
#     assert isinstance(sd, (int, float)), f"sd must be a number, got {type(sd)}"
#     assert sd >= 0, f"sd must be non-negative, got {sd}"
#     data = np.asarray(data)
#     assert data.ndim <= 2, f"Data must be 1D or 2D, got {data.ndim}D"
#     if xx is None:
#         xx = np.arange(data.shape[1] if data.ndim > 1 else len(data))
#     else:
#         xx = np.asarray(xx)
#     expected_len = data.shape[1] if data.ndim > 1 else len(data)
#     assert (
#         len(xx) == expected_len
#     ), f"xx length ({len(xx)}) must match data length ({expected_len})"
# 
#     if data.ndim == 1:
#         central = data
#         error = np.zeros_like(central)
#     else:
#         central = np.nanmean(data, axis=0)
#         error = np.nanstd(data, axis=0) * sd
# 
#     y_lower = central - error
#     y_upper = central + error
#     n_samples = data.shape[0] if data.ndim > 1 else 1
# 
#     if "label" in kwargs and kwargs["label"]:
#         kwargs["label"] = f"{kwargs['label']} (n={n_samples})"
# 
#     return scitex_plt_plot_shaded_line(axis, xx, y_lower, central, y_upper, **kwargs)
# 
# 
# def plot_mean_ci(axis, data, xx=None, perc=95, **kwargs):
#     """
#     Plot mean line with confidence interval shading.
#     
#     Parameters
#     ----------
#     axis : matplotlib.axes.Axes or scitex.plt._subplots.AxisWrapper
#         The axis to plot on
#     data : array-like
#         Data to plot, can be 1D or 2D. If 2D, mean and percentiles are calculated across the first dimension
#     xx : array-like, optional
#         X coordinates for the data. If None, will use np.arange(len(data))
#     perc : float, optional
#         Confidence interval percentage (0-100). Default is 95
#     **kwargs
#         Additional keyword arguments passed to plot_shaded_line()
#         
#     Returns
#     -------
#     axis : matplotlib.axes.Axes or scitex.plt._subplots.AxisWrapper
#         The axis with the plot
#     """
#     assert_valid_axis(axis, "First argument must be a matplotlib axis or scitex axis wrapper")
#     assert isinstance(
#         perc, (int, float)
#     ), f"perc must be a number, got {type(perc)}"
#     assert 0 <= perc <= 100, f"perc must be between 0 and 100, got {perc}"
#     data = np.asarray(data)
#     assert data.ndim <= 2, f"Data must be 1D or 2D, got {data.ndim}D"
# 
#     if xx is None:
#         xx = np.arange(data.shape[1] if data.ndim > 1 else len(data))
#     else:
#         xx = np.asarray(xx)
# 
#     expected_len = data.shape[1] if data.ndim > 1 else len(data)
#     assert (
#         len(xx) == expected_len
#     ), f"xx length ({len(xx)}) must match data length ({expected_len})"
# 
#     if data.ndim == 1:
#         central = data
#         y_lower = central
#         y_upper = central
#     else:
#         central = np.nanmean(data, axis=0)
#         # Calculate CI bounds
#         alpha = 1 - perc / 100
#         y_lower_perc = alpha / 2 * 100
#         y_upper_perc = (1 - alpha / 2) * 100
#         y_lower = np.nanpercentile(data, y_lower_perc, axis=0)
#         y_upper = np.nanpercentile(data, y_upper_perc, axis=0)
# 
#     n_samples = data.shape[0] if data.ndim > 1 else 1
# 
#     if "label" in kwargs and kwargs["label"]:
#         kwargs["label"] = f"{kwargs['label']} (n={n_samples}, CI={perc}%)"
# 
#     return scitex_plt_plot_shaded_line(axis, xx, y_lower, central, y_upper, **kwargs)
# 
# 
# def plot_median_iqr(axis, data, xx=None, **kwargs):
#     """
#     Plot median line with interquartile range shading.
#     
#     Parameters
#     ----------
#     axis : matplotlib.axes.Axes or scitex.plt._subplots.AxisWrapper
#         The axis to plot on
#     data : array-like
#         Data to plot, can be 1D or 2D. If 2D, median and IQR are calculated across the first dimension
#     xx : array-like, optional
#         X coordinates for the data. If None, will use np.arange(len(data))
#     **kwargs
#         Additional keyword arguments passed to plot_shaded_line()
#         
#     Returns
#     -------
#     axis : matplotlib.axes.Axes or scitex.plt._subplots.AxisWrapper
#         The axis with the plot
#     """
#     assert_valid_axis(axis, "First argument must be a matplotlib axis or scitex axis wrapper")
#     data = np.asarray(data)
#     assert data.ndim <= 2, f"Data must be 1D or 2D, got {data.ndim}D"
# 
#     if xx is None:
#         xx = np.arange(data.shape[1] if data.ndim > 1 else len(data))
#     else:
#         xx = np.asarray(xx)
# 
#     expected_len = data.shape[1] if data.ndim > 1 else len(data)
#     assert (
#         len(xx) == expected_len
#     ), f"xx length ({len(xx)}) must match data length ({expected_len})"
# 
#     if data.ndim == 1:
#         central = data
#         y_lower = central
#         y_upper = central
#     else:
#         central = np.nanmedian(data, axis=0)
#         y_lower = np.nanpercentile(data, 25, axis=0)
#         y_upper = np.nanpercentile(data, 75, axis=0)
# 
#     n_samples = data.shape[0] if data.ndim > 1 else 1
# 
#     if "label" in kwargs and kwargs["label"]:
#         kwargs["label"] = f"{kwargs['label']} (n={n_samples}, IQR)"
# 
#     return scitex_plt_plot_shaded_line(axis, xx, y_lower, central, y_upper, **kwargs)
# 
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/plt/ax/_plot/_plot_statistical_shaded_line.py
# --------------------------------------------------------------------------------
