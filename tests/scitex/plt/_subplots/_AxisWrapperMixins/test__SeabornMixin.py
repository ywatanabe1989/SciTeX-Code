#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-18 16:32:56 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/tests/scitex/plt/_subplots/_AxisWrapperMixins/test__SeabornMixin.py
# ----------------------------------------
import os

__FILE__ = "./tests/scitex/plt/_subplots/_AxisWrapperMixins/test__SeabornMixin.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import matplotlib
import scitex
import numpy as np
import pandas as pd

matplotlib.use("agg")

ACTUAL_SAVE_DIR = __file__.replace(".py", "_out")


def test_sns_barplot():
    """Test sns_barplot function"""
    # Figure
    fig, ax = scitex.plt.subplots()
    # Data
    data = pd.DataFrame(
        {"category": ["A", "B", "C", "D", "E"], "values": [25, 40, 30, 55, 15]}
    )
    # Plot
    ax.sns_barplot(data=data, x="category", y="values", palette="viridis")
    # Visualization
    ax.set_xyt("Categories", "Values", "Seaborn Barplot Test")
    # Saving
    spath = f"./sns_barplot_test.png"
    scitex.io.save(fig, spath, symlink_from_cwd=False)
    # Closing
    scitex.plt.close(fig)
    # Assertion
    actual_spath = os.path.join(ACTUAL_SAVE_DIR, spath)
    assert os.path.exists(actual_spath), f"Failed to save figure to {spath}"


def test_sns_boxplot():
    """Test sns_boxplot function"""
    # Figure
    fig, ax = scitex.plt.subplots()
    # Data
    data = pd.DataFrame(
        {
            "group": np.repeat(["A", "B", "C"], 30),
            "value": np.concatenate(
                [
                    np.random.normal(0, 1, 30),
                    np.random.normal(3, 1, 30),
                    np.random.normal(6, 1, 30),
                ]
            ),
        }
    )
    # Plot
    ax.sns_boxplot(data=data, x="group", y="value", notch=True, strip=True)
    # Visualization
    ax.set_xyt("Groups", "Values", "Seaborn Boxplot with Strip Test")
    # Saving
    spath = f"./sns_boxplot_test.png"
    scitex.io.save(fig, spath, symlink_from_cwd=False)
    # Closing
    scitex.plt.close(fig)
    # Assertion
    actual_spath = os.path.join(ACTUAL_SAVE_DIR, spath)
    assert os.path.exists(actual_spath), f"Failed to save figure to {spath}"


def test_sns_heatmap():
    """Test sns_heatmap function"""
    # Figure
    fig, ax = scitex.plt.subplots()
    # Data
    data = np.random.rand(10, 10)
    correlation_matrix = np.corrcoef(data)
    # Plot
    ax.sns_heatmap(correlation_matrix, annot=True, cmap="coolwarm", vmin=-1, vmax=1)
    # Visualization
    ax.set_xyt("Features", "Features", "Seaborn Heatmap Test")
    # Saving
    spath = f"./sns_heatmap_test.png"
    scitex.io.save(fig, spath, symlink_from_cwd=False)
    # Closing
    scitex.plt.close(fig)
    # Assertion
    actual_spath = os.path.join(ACTUAL_SAVE_DIR, spath)
    assert os.path.exists(actual_spath), f"Failed to save figure to {spath}"


def test_sns_heatmap_xyz():
    """Test sns_heatmap with xyz=True"""
    # Figure
    fig, ax = scitex.plt.subplots()
    # Data
    data = pd.DataFrame(np.random.rand(10, 10))
    # Plot
    ax.sns_heatmap(data, xyz=True, cmap="viridis")
    # Visualization
    ax.set_xyt("X", "Y", "Seaborn Heatmap with XYZ Test")
    # Saving
    spath = f"./sns_heatmap_xyz_test.png"
    scitex.io.save(fig, spath, symlink_from_cwd=False)
    # Closing
    scitex.plt.close(fig)
    # Assertion
    actual_spath = os.path.join(ACTUAL_SAVE_DIR, spath)
    assert os.path.exists(actual_spath), f"Failed to save figure to {spath}"


def test_sns_histplot():
    """Test sns_histplot function"""
    # Figure
    fig, ax = scitex.plt.subplots()
    # Data
    data = pd.DataFrame(
        {
            "value": np.concatenate(
                [np.random.normal(0, 1, 1000), np.random.normal(4, 1, 500)]
            ),
            "group": np.concatenate([np.repeat("A", 1000), np.repeat("B", 500)]),
        }
    )
    # Plot
    ax.sns_histplot(data=data, x="value", hue="group", element="step", bins=30)
    # Visualization
    ax.set_xyt("Values", "Count", "Seaborn Histplot Test")
    # Saving
    spath = f"./sns_histplot_test.png"
    scitex.io.save(fig, spath, symlink_from_cwd=False)
    # Closing
    scitex.plt.close(fig)
    # Assertion
    actual_spath = os.path.join(ACTUAL_SAVE_DIR, spath)
    assert os.path.exists(actual_spath), f"Failed to save figure to {spath}"


def test_sns_kdeplot():
    """Test sns_kdeplot function"""
    # Figure
    fig, ax = scitex.plt.subplots()
    # Data
    data = pd.DataFrame(
        {
            "value": np.concatenate(
                [np.random.normal(0, 1, 500), np.random.normal(3, 1, 500)]
            ),
            "group": np.concatenate([np.repeat("A", 500), np.repeat("B", 500)]),
        }
    )
    # Plot
    ax.sns_kdeplot(data=data, x="value", hue="group", fill=True)
    # Visualization
    ax.set_xyt("Values", "Density", "Seaborn KDE Plot Test")
    # Saving
    spath = f"./sns_kdeplot_test.png"
    scitex.io.save(fig, spath, symlink_from_cwd=False)
    # Closing
    scitex.plt.close(fig)
    # Assertion
    actual_spath = os.path.join(ACTUAL_SAVE_DIR, spath)
    assert os.path.exists(actual_spath), f"Failed to save figure to {spath}"


def test_sns_scatterplot():
    """Test sns_scatterplot function"""
    # Figure
    fig, ax = scitex.plt.subplots()
    # Data
    data = pd.DataFrame(
        {
            "x": np.random.rand(100),
            "y": np.random.rand(100),
            "size": np.random.rand(100) * 100,
            "category": np.random.choice(["A", "B", "C"], 100),
        }
    )
    # Plot
    ax.sns_scatterplot(data=data, x="x", y="y", size="size", hue="category")
    # Visualization
    ax.set_xyt("X Values", "Y Values", "Seaborn Scatterplot Test")
    # Saving
    spath = f"./sns_scatterplot_test.png"
    scitex.io.save(fig, spath, symlink_from_cwd=False)
    # Closing
    scitex.plt.close(fig)
    # Assertion
    actual_spath = os.path.join(ACTUAL_SAVE_DIR, spath)
    assert os.path.exists(actual_spath), f"Failed to save figure to {spath}"


def test_sns_swarmplot():
    """Test sns_swarmplot function"""
    # Figure
    fig, ax = scitex.plt.subplots()
    # Data
    data = pd.DataFrame(
        {
            "group": np.repeat(["A", "B", "C", "D"], 25),
            "value": np.concatenate(
                [
                    np.random.normal(0, 1, 25),
                    np.random.normal(2, 1, 25),
                    np.random.normal(4, 1, 25),
                    np.random.normal(6, 1, 25),
                ]
            ),
        }
    )
    # Plot
    ax.sns_swarmplot(data=data, x="group", y="value", palette="Set2")
    # Visualization
    ax.set_xyt("Groups", "Values", "Seaborn Swarmplot Test")
    # Saving
    spath = f"./sns_swarmplot_test.png"
    scitex.io.save(fig, spath, symlink_from_cwd=False)
    # Closing
    scitex.plt.close(fig)
    # Assertion
    actual_spath = os.path.join(ACTUAL_SAVE_DIR, spath)
    assert os.path.exists(actual_spath), f"Failed to save figure to {spath}"


def test_sns_stripplot():
    """Test sns_stripplot function"""
    # Figure
    fig, ax = scitex.plt.subplots()
    # Data
    data = pd.DataFrame(
        {
            "group": np.repeat(["A", "B", "C"], 30),
            "value": np.concatenate(
                [
                    np.random.normal(0, 1, 30),
                    np.random.normal(3, 1, 30),
                    np.random.normal(6, 1, 30),
                ]
            ),
        }
    )
    # Plot
    ax.sns_stripplot(data=data, x="group", y="value", jitter=True, palette="Set3")
    # Visualization
    ax.set_xyt("Groups", "Values", "Seaborn Stripplot Test")
    # Saving
    spath = f"./sns_stripplot_test.png"
    scitex.io.save(fig, spath, symlink_from_cwd=False)
    # Closing
    scitex.plt.close(fig)
    # Assertion
    actual_spath = os.path.join(ACTUAL_SAVE_DIR, spath)
    assert os.path.exists(actual_spath), f"Failed to save figure to {spath}"


def test_sns_violinplot():
    """Test sns_violinplot function"""
    # Figure
    fig, ax = scitex.plt.subplots()
    # Data
    data = pd.DataFrame(
        {
            "group": np.repeat(["A", "B", "C", "D"], 30),
            "value": np.concatenate(
                [
                    np.random.normal(0, 1, 30),
                    np.random.normal(3, 1, 30),
                    np.random.normal(6, 1, 30),
                    np.random.normal(9, 1, 30),
                ]
            ),
        }
    )
    # Plot
    ax.sns_violinplot(data=data, x="group", y="value", inner="stick")
    # Visualization
    ax.set_xyt("Groups", "Values", "Seaborn Violinplot Test")
    # Saving
    spath = f"./sns_violinplot_test.png"
    scitex.io.save(fig, spath, symlink_from_cwd=False)
    # Closing
    scitex.plt.close(fig)
    # Assertion
    actual_spath = os.path.join(ACTUAL_SAVE_DIR, spath)
    assert os.path.exists(actual_spath), f"Failed to save figure to {spath}"


# def test_sns_violinplot_half():
#     """Test sns_violinplot with half=True"""
#     # Figure
#     fig, ax = scitex.plt.subplots()
#     # Data
#     data = pd.DataFrame(
#         {
#             "group": np.repeat(["A", "B", "C"], 30),
#             "value": np.concatenate(
#                 [
#                     np.random.normal(0, 1, 30),
#                     np.random.normal(3, 1, 30),
#                     np.random.normal(6, 1, 30),
#                 ]
#             ),
#         }
#     )
#     # Plot
#     ax.sns_violinplot(data=data, x="group", y="value", half=True)
#     # Visualization
#     ax.set_xyt("Groups", "Values", "Seaborn Half Violinplot Test")
#     # Saving
#     spath = f"./sns_violinplot_half_test.png"
#     scitex.io.save(fig, spath, symlink_from_cwd=False)
#     # Closing
#     scitex.plt.close(fig)
#     # Assertion
#     actual_spath = os.path.join(ACTUAL_SAVE_DIR, spath)
#     assert os.path.exists(actual_spath), f"Failed to save figure to {spath}"

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/_subplots/_AxisWrapperMixins/_SeabornMixin.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-05-01 16:27:16 (ywatanabe)"
# # File: /home/ywatanabe/proj/_scitex_repo/src/scitex/plt/_subplots/_AxisWrapperMixins/_SeabornMixin.py
# # ----------------------------------------
# import os
# __FILE__ = (
#     "./src/scitex/plt/_subplots/_AxisWrapperMixins/_SeabornMixin.py"
# )
# __DIR__ = os.path.dirname(__FILE__)
# # ----------------------------------------
#
# from functools import wraps
#
# import scitex
# import numpy as np
# import pandas as pd
# import seaborn as sns
#
# from ....plt import ax as ax_module
#
#
# def sns_copy_doc(func):
#     @wraps(func)
#     def wrapper(self, *args, **kwargs):
#         return func(self, *args, **kwargs)
#
#     wrapper.__doc__ = getattr(sns, func.__name__.split("sns_")[-1]).__doc__
#     return wrapper
#
#
# class SeabornMixin:
#
#     def _sns_base(
#         self, method_name, *args, track=True, track_obj=None, id=None, **kwargs
#     ):
#         sns_method_name = method_name.split("sns_")[-1]
#
#         with self._no_tracking():
#             sns_plot_fn = getattr(sns, sns_method_name)
#
#             if kwargs.get("hue_colors"):
#                 kwargs = scitex.gen.alternate_kwarg(
#                     kwargs, primary_key="palette", alternate_key="hue_colors"
#                 )
#
#             self._axis_mpl = sns_plot_fn(ax=self._axis_mpl, *args, **kwargs)
#
#         # Track the plot if required
#         track_obj = track_obj if track_obj is not None else args
#         self._track(track, id, method_name, track_obj, kwargs)
#
#     def _sns_base_xyhue(
#         self, method_name, *args, track=True, id=None, **kwargs
#     ):
#         """Formats data passed to sns functions with (data=data, x=x, y=y) keyword arguments"""
#         df = kwargs.get("data")
#         x, y, hue = kwargs.get("x"), kwargs.get("y"), kwargs.get("hue")
#
#         track_obj = (
#             self._sns_prepare_xyhue(df, x, y, hue) if df is not None else None
#         )
#         self._sns_base(
#             method_name,
#             *args,
#             track=track,
#             track_obj=track_obj,
#             id=id,
#             **kwargs,
#         )
#
#     def _sns_prepare_xyhue(
#         self, data=None, x=None, y=None, hue=None, **kwargs
#     ):
#         """Returns obj to track"""
#         data = data.reset_index()
#
#         if hue is not None:
#             if x is None and y is None:
#
#                 return data
#             elif x is None:
#
#                 agg_dict = {}
#                 for hh in data[hue].unique():
#                     agg_dict[hh] = data.loc[data[hue] == hh, y]
#                 df = scitex.pd.force_df(agg_dict)
#                 return df
#
#             elif y is None:
#
#                 df = pd.concat(
#                     [
#                         data.loc[data[hue] == hh, x]
#                         for hh in data[hue].unique()
#                     ],
#                     axis=1,
#                 )
#                 return df
#             else:
#                 pivoted_data = data.pivot_table(
#                     values=y,
#                     index=data.index,
#                     columns=[x, hue],
#                     aggfunc="first",
#                 )
#                 pivoted_data.columns = [
#                     f"{col[0]}-{col[1]}" for col in pivoted_data.columns
#                 ]
#                 return pivoted_data
#         else:
#             if x is None and y is None:
#                 return data
#
#             elif x is None:
#                 return data[[y]]
#
#             elif y is None:
#                 return data[[x]]
#
#             else:
#                 return data.pivot_table(
#                     values=y, index=data.index, columns=x, aggfunc="first"
#                 )
#
#     @sns_copy_doc
#     def sns_barplot(
#         self, data=None, x=None, y=None, track=True, id=None, **kwargs
#     ):
#         self._sns_base_xyhue(
#             "sns_barplot", data=data, x=x, y=y, track=track, id=id, **kwargs
#         )
#
#     @sns_copy_doc
#     def sns_boxplot(
#         self,
#         data=None,
#         x=None,
#         y=None,
#         strip=False,
#         track=True,
#         id=None,
#         **kwargs,
#     ):
#         self._sns_base_xyhue(
#             "sns_boxplot", data=data, x=x, y=y, track=track, id=id, **kwargs
#         )
#         if strip:
#             strip_kwargs = kwargs.copy()
#             strip_kwargs.pop("notch", None)  # Remove boxplot-specific kwargs
#             strip_kwargs.pop("whis", None)
#             self.sns_stripplot(
#                 data=data,
#                 x=x,
#                 y=y,
#                 track=False,
#                 id=f"{id}_strip",
#                 **strip_kwargs,
#             )
#
#     @sns_copy_doc
#     def sns_heatmap(self, *args, xyz=False, track=True, id=None, **kwargs):
#         method_name = "sns_heatmap"
#         df = args[0]
#         if xyz:
#             df = scitex.pd.to_xyz(df)
#         self._sns_base(
#             method_name, *args, track=track, track_obj=df, id=id, **kwargs
#         )
#
#     @sns_copy_doc
#     def sns_histplot(
#         self, data=None, x=None, y=None, track=True, id=None, **kwargs
#     ):
#         self._sns_base_xyhue(
#             "sns_histplot", data=data, x=x, y=y, track=track, id=id, **kwargs
#         )
#
#     @sns_copy_doc
#     def sns_kdeplot(
#         self,
#         data=None,
#         x=None,
#         y=None,
#         xlim=None,
#         ylim=None,
#         track=True,
#         id=None,
#         **kwargs,
#     ):
#         if kwargs.get("hue"):
#             hues = data[kwargs["hue"]]
#
#             if x is not None:
#                 lim = xlim
#                 for hue in np.unique(hues):
#                     _data = data.loc[hues == hue, x]
#                     self.plot_kde(_data, xlim=lim, label=hue, id=hue, **kwargs)
#
#             if y is not None:
#                 lim = ylim
#                 for hue in np.unique(hues):
#                     _data = data.loc[hues == hue, y]
#                     self.plot_kde(_data, xlim=lim, label=hue, id=hue, **kwargs)
#
#         else:
#             if x is not None:
#                 _data, lim = data[x], xlim
#             if y is not None:
#                 _data, lim = data[y], ylim
#             self.plot_kde(_data, xlim=lim, **kwargs)
#
#     @sns_copy_doc
#     def sns_pairplot(self, *args, track=True, id=None, **kwargs):
#         self._sns_base("sns_pairplot", *args, track=track, id=id, **kwargs)
#
#     @sns_copy_doc
#     def sns_scatterplot(
#         self, data=None, x=None, y=None, track=True, id=None, **kwargs
#     ):
#         self._sns_base_xyhue(
#             "sns_scatterplot",
#             data=data,
#             x=x,
#             y=y,
#             track=track,
#             id=id,
#             **kwargs,
#         )
#
#     @sns_copy_doc
#     def sns_swarmplot(
#         self, data=None, x=None, y=None, track=True, id=None, **kwargs
#     ):
#         self._sns_base_xyhue(
#             "sns_swarmplot", data=data, x=x, y=y, track=track, id=id, **kwargs
#         )
#
#     @sns_copy_doc
#     def sns_stripplot(
#         self, data=None, x=None, y=None, track=True, id=None, **kwargs
#     ):
#         self._sns_base_xyhue(
#             "sns_stripplot", data=data, x=x, y=y, track=track, id=id, **kwargs
#         )
#
#     # @sns_copy_doc
#     # def sns_violinplot(
#     #     self, data=None, x=None, y=None, track=True, id=None, **kwargs
#     # ):
#     #     self._sns_base_xyhue(
#     #         "sns_violinplot", data=data, x=x, y=y, track=track, id=id, **kwargs
#     #     )
#
#     @sns_copy_doc
#     def sns_violinplot(
#         self,
#         data=None,
#         x=None,
#         y=None,
#         track=True,
#         id=None,
#         half=False,
#         **kwargs,
#     ):
#         if half:
#             with self._no_tracking():
#                 self._axis_mpl = ax_module.plot_half_violin(
#                     self._axis_mpl, data=data, x=x, y=y, **kwargs
#                 )
#         else:
#             self._sns_base_xyhue(
#                 "sns_violinplot",
#                 data=data,
#                 x=x,
#                 y=y,
#                 track=track,
#                 id=id,
#                 **kwargs,
#             )
#
#         # Tracking
#         track_obj = self._sns_prepare_xyhue(data, x, y, kwargs.get("hue"))
#         self._track(track, id, "sns_violinplot", track_obj, kwargs)
#
#         return self._axis_mpl
#
#     @sns_copy_doc
#     def sns_jointplot(self, *args, track=True, id=None, **kwargs):
#         self._sns_base("sns_jointplot", *args, track=track, id=id, **kwargs)
#
# # EOF
# --------------------------------------------------------------------------------
# End of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/_subplots/_AxisWrapperMixins/_SeabornMixin.py
# --------------------------------------------------------------------------------

# EOF
