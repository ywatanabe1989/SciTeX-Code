#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-02 23:09:33 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/tests/scitex/plt/ax/_plot/test__plot_violin.py
# ----------------------------------------
import os

__FILE__ = "./tests/scitex/plt/ax/_plot/test__plot_violin.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest
from scitex.plt.ax._plot import plot_violin


class TestPlotViolin:
    def setup_method(self):
        # Setup test fixtures
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
        # Create sample data
        np.random.seed(42)
        data_size = 100
        self.data = pd.DataFrame(
            {
                "y": np.concatenate(
                    [
                        np.random.normal(0, 1, data_size),
                        np.random.normal(3, 1, data_size),
                    ]
                ),
                "x": np.repeat(["A", "B"], data_size),
            }
        )
        self.labels = self.data["x"].unique().tolist()
        self.data_list = [
            self.data[self.data["x"] == ll]["y"].tolist() for ll in self.labels
        ]
        # Create output directory if it doesn't exist
        self.out_dir = __file__.replace(".py", "_out")
        os.makedirs(self.out_dir, exist_ok=True)

    def teardown_method(self):
        # Clean up after tests
        plt.close(self.fig)

    def save_test_figure(self, method_name):
        """Helper method to save figure using method name"""
        from scitex.io import save

        spath = f"./{os.path.basename(__file__).replace('.py', '')}_{method_name}.jpg"
        save(self.fig, spath)
        # Check saved file
        actual_spath = os.path.join(self.out_dir, spath)
        assert os.path.exists(actual_spath), f"Failed to save figure to {spath}"

    def test_with_labels(self):
        # Test with hue parameter
        self.ax = plot_violin(self.ax, self.data_list, labels=self.labels)
        self.ax.set_title("Half Violin Plot with Labels")
        # Save figure
        self.save_test_figure("test_with_labels")

    def test_with_labels_half(self):
        # Test with hue parameter
        self.ax = plot_violin(self.ax, self.data_list, labels=self.labels, half=True)
        self.ax.set_title("Half Violin Plot with Labels Half")
        # Save figure
        self.save_test_figure("test_with_labels")

    # def test_plot_violin_savefig(self):
    #     ax = plot_violin(self.ax, data=self.data, x="x", y="y")
    #     ax.set_title("Half Violin Plot")

    #     # Saving
    #     from scitex.io import save

    #     spath = f"./{os.path.basename(__file__)}.jpg"
    #     save(self.fig, spath)

    #     # Check saved file
    #     ACTUAL_SAVE_DIR = __file__.replace(".py", "_out")
    #     actual_spath = os.path.join(ACTUAL_SAVE_DIR, spath)
    #     assert os.path.exists(
    #         actual_spath
    #     ), f"Failed to save figure to {spath}"


if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/ax/_plot/_plot_violin.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-05-02 22:01:54 (ywatanabe)"
# # File: /home/ywatanabe/proj/scitex_repo/src/scitex/plt/ax/_plot/_plot_violin.py
# # ----------------------------------------
# import os
# __FILE__ = (
#     "./src/scitex/plt/ax/_plot/_plot_violin.py"
# )
# __DIR__ = os.path.dirname(__FILE__)
# # ----------------------------------------
#
# import matplotlib
# import matplotlib.pyplot as plt
# import numpy as np
# import pandas as pd
# import seaborn as sns
#
#
# def plot_violin(
#     ax,
#     data_list,
#     labels=None,
#     colors=None,
#     half=False,
#     **kwargs,
# ):
#     """
#     Plot a violin plot using seaborn.
#
#     Parameters
#     ----------
#     ax : matplotlib.axes.Axes
#         The axes to plot on
#     data_list : list
#         List of arrays to plot as violins
#     labels : list, optional
#         Labels for each array in data_list
#     colors : list, optional
#         Colors for each violin
#     half : bool, optional
#         If True, plots only the left half of the violins, default False
#     **kwargs
#         Additional keyword arguments passed to seaborn.violinplot
#
#     Returns
#     -------
#     ax : matplotlib.axes.Axes
#         The axes object with the plot
#     """
#     # Convert list-style data to DataFrame
#     all_values = []
#     all_groups = []
#
#     for idx, values in enumerate(data_list):
#         all_values.extend(values)
#         group_label = (
#             labels[idx] if labels and idx < len(labels) else f"x {idx}"
#         )
#         all_groups.extend([group_label] * len(values))
#
#     # Create DataFrame
#     df = pd.DataFrame({"x": all_groups, "y": all_values})
#
#     # Setup colors if provided
#     if colors:
#         if isinstance(colors, list):
#             kwargs["palette"] = {
#                 group: color
#                 for group, color in zip(
#                     set(all_groups), colors[: len(set(all_groups))]
#                 )
#             }
#         else:
#             kwargs["palette"] = colors
#
#     # Call seaborn-based function
#     return sns_plot_violin(
#         ax, data=df, x="x", y="y", hue="x", half=half, **kwargs
#     )
#
#
# def sns_plot_violin(
#     ax, data=None, x=None, y=None, hue=None, half=False, **kwargs
# ):
#     """
#     Plot a violin plot with option for half violins.
#     Parameters
#     ----------
#     ax : matplotlib.axes.Axes
#         The axes to plot on
#     data : DataFrame
#         The dataframe containing the data
#     x : str
#         Column name for x-axis variable
#     y : str
#         Column name for y-axis variable
#     hue : str, optional
#         Column name for hue variable
#     half : bool, optional
#         If True, plots only the left half of the violins, default False
#     **kwargs
#         Additional keyword arguments passed to seaborn.violinplot
#     Returns
#     -------
#     ax : matplotlib.axes.Axes
#         The axes object with the plot
#     """
#     assert isinstance(
#         ax, matplotlib.axes._axes.Axes
#     ), "First argument must be a matplotlib axis"
#
#     if not half:
#         # Standard violin plot
#         return sns.violinplot(data=data, x=x, y=y, hue=hue, ax=ax, **kwargs)
#
#     # Create a copy of the dataframe to avoid modifying the original
#     df = data.copy()
#
#     # If no hue provided, create default hue
#     if hue is None:
#         df["_hue"] = "default"
#         hue = "_hue"
#
#     # Add fake hue for the right side
#     df["_fake_hue"] = df[hue] + "_right"
#
#     # Adjust hue_order and palette if provided
#     if "hue_order" in kwargs:
#         kwargs["hue_order"] = kwargs["hue_order"] + [
#             h + "_right" for h in kwargs["hue_order"]
#         ]
#     else:
#         kwargs["hue_order"] = []
#         for group in df[x].unique().tolist():
#             kwargs["hue_order"].append(group)
#             kwargs["hue_order"].append(group + "_right")
#
#     if "palette" in kwargs:
#         palette = kwargs["palette"]
#         if isinstance(palette, dict):
#             kwargs["palette"] = {
#                 **palette,
#                 **{k + "_right": v for k, v in palette.items()},
#             }
#         elif isinstance(palette, list):
#             kwargs["palette"] = palette + palette
#
#     # Conc left and right
#     df_left = df[[x, y]]
#     df_right = df[["_fake_hue", y]].rename(columns={"_fake_hue": x})
#     df_right[y] = [np.nan for _ in range(len(df_right))]
#     df_conc = pd.concat([df_left, df_right], axis=0, ignore_index=True)
#     df_conc = df_conc.sort_values(x)
#
#     # Plot
#     sns.violinplot(
#         data=df_conc, x=x, y=y, hue="x", split=True, ax=ax, **kwargs
#     )
#
#     # Remove right half of violins
#     for collection in ax.collections:
#         if isinstance(collection, plt.matplotlib.collections.PolyCollection):
#             collection.set_clip_path(None)
#
#     # Adjust legend
#     if ax.legend_ is not None:
#         handles, labels = ax.get_legend_handles_labels()
#         ax.legend(handles[: len(handles) // 2], labels[: len(labels) // 2])
#
#     return ax
#
#
# # def _plot_half_violin(ax, data=None, x=None, y=None, hue=None, **kwargs):
#
# #     assert isinstance(
# #         ax, matplotlib.axes._axes.Axes
# #     ), "First argument must be a matplotlib axis"
#
# #     # Prepare data
# #     df = data.copy()
# #     if hue is None:
# #         df["_hue"] = "default"
# #         hue = "_hue"
#
# #     # Add fake hue for the right side
# #     df["_fake_hue"] = df[hue] + "_right"
#
# #     # Adjust hue_order and palette if provided
# #     if "hue_order" in kwargs:
# #         kwargs["hue_order"] = kwargs["hue_order"] + [
# #             h + "_right" for h in kwargs["hue_order"]
# #         ]
#
# #     if "palette" in kwargs:
# #         palette = kwargs["palette"]
# #         if isinstance(palette, dict):
# #             kwargs["palette"] = {
# #                 **palette,
# #                 **{k + "_right": v for k, v in palette.items()},
# #             }
# #         elif isinstance(palette, list):
# #             kwargs["palette"] = palette + palette
#
# #     # Plot
# #     sns.violinplot(
# #         data=df, x=x, y=y, hue="_fake_hue", split=True, ax=ax, **kwargs
# #     )
#
# #     # Remove right half of violins
# #     for collection in ax.collections:
# #         if isinstance(collection, plt.matplotlib.collections.PolyCollection):
# #             collection.set_clip_path(None)
#
# #     # Adjust legend
# #     if ax.legend_ is not None:
# #         handles, labels = ax.get_legend_handles_labels()
# #         ax.legend(handles[: len(handles) // 2], labels[: len(labels) // 2])
#
# #     return ax
#
# # import matplotlib
# # import matplotlib.pyplot as plt
# # import seaborn as sns
#
# # def plot_violin_half(ax, data=None, x=None, y=None, hue=None, **kwargs):
# #     """
# #     Plot a half violin plot (showing only the left side of violins).
#
# #     Parameters
# #     ----------
# #     ax : matplotlib.axes.Axes
# #         The axes to plot on
# #     data : DataFrame
# #         The dataframe containing the data
# #     x : str
# #         Column name for x-axis variable
# #     y : str
# #         Column name for y-axis variable
# #     hue : str, optional
# #         Column name for hue variable
# #     **kwargs
# #         Additional keyword arguments passed to seaborn.violinplot
#
# #     Returns
# #     -------
# #     ax : matplotlib.axes.Axes
# #         The axes object with the plot
# #     """
# #     assert isinstance(
# #         ax, matplotlib.axes._axes.Axes
# #     ), "First argument must be a matplotlib axis"
#
# #     # Prepare data
# #     df = data.copy()
# #     if hue is None:
# #         df["_hue"] = "default"
# #         hue = "_hue"
#
# #     # Add fake hue for the right side
# #     df["_fake_hue"] = df[hue] + "_right"
#
# #     # Adjust hue_order and palette if provided
# #     if "hue_order" in kwargs:
# #         kwargs["hue_order"] = kwargs["hue_order"] + [
# #             h + "_right" for h in kwargs["hue_order"]
# #         ]
# #     if "palette" in kwargs:
# #         palette = kwargs["palette"]
# #         if isinstance(palette, dict):
# #             kwargs["palette"] = {
# #                 **palette,
# #                 **{k + "_right": v for k, v in palette.items()},
# #             }
# #         elif isinstance(palette, list):
# #             kwargs["palette"] = palette + palette
#
# #     # Plot
# #     sns.violinplot(
# #         data=df, x=x, y=y, hue="_fake_hue", split=True, ax=ax, **kwargs
# #     )
#
# #     # Remove right half of violins
# #     for collection in ax.collections:
# #         if isinstance(collection, matplotlib.collections.PolyCollection):
# #             collection.set_clip_path(None)
#
# #     # Adjust legend
# #     if ax.legend_ is not None:
# #         handles, labels = ax.get_legend_handles_labels()
# #         ax.legend(handles[: len(handles) // 2], labels[: len(labels) // 2])
#
# #     return ax
#
#
# ## Probably working
# def half_violin(ax, data=None, x=None, y=None, hue=None, **kwargs):
#     # Prepare data
#     df = data.copy()
#     if hue is None:
#         df["_hue"] = "default"
#         hue = "_hue"
#
#     # Add fake hue for the right side
#     df["_fake_hue"] = df[hue] + "_right"
#
#     # Adjust hue_order and palette if provided
#     if "hue_order" in kwargs:
#         kwargs["hue_order"] = kwargs["hue_order"] + [
#             h + "_right" for h in kwargs["hue_order"]
#         ]
#
#     if "palette" in kwargs:
#         palette = kwargs["palette"]
#         if isinstance(palette, dict):
#             kwargs["palette"] = {
#                 **palette,
#                 **{k + "_right": v for k, v in palette.items()},
#             }
#         elif isinstance(palette, list):
#             kwargs["palette"] = palette + palette
#
#     # Plot
#     sns.violinplot(
#         data=df, x=x, y=y, hue="_fake_hue", split=True, ax=ax, **kwargs
#     )
#
#     # Remove right half of violins
#     for collection in ax.collections:
#         if isinstance(collection, plt.matplotlib.collections.PolyCollection):
#             collection.set_clip_path(None)
#
#     # Adjust legend
#     if ax.legend_ is not None:
#         handles, labels = ax.get_legend_handles_labels()
#         ax.legend(handles[: len(handles) // 2], labels[: len(labels) // 2])
#
#     return ax
#
#
# # import scitex
# # import numpy as np
# # fig, ax = scitex.plt.subplots()
# # # Test with list data
# # data_list = [
# #     np.random.normal(0, 1, 100),
# #     np.random.normal(2, 1.5, 100),
# #     np.random.normal(5, 0.8, 100),
# # ]
# # labels = ["x A", "x B", "x C"]
# # colors = ["red", "blue", "green"]
# # half = True
# # ax = half_violin(
# #     ax, data_list, x=""
# # )
#
# # EOF
# --------------------------------------------------------------------------------
# End of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/ax/_plot/_plot_violin.py
# --------------------------------------------------------------------------------
