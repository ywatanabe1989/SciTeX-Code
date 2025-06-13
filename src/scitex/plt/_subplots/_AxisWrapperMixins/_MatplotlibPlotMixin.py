#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-18 17:51:44 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/plt/_subplots/_AxisWrapperMixins/_MatplotlibPlotMixin.py
# ----------------------------------------
import os

__FILE__ = "./src/scitex/plt/_subplots/_AxisWrapperMixins/_MatplotlibPlotMixin.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from functools import wraps
from typing import Any, Dict, List, Optional, Tuple, Union

import matplotlib
import numpy as np
import pandas as pd
from scipy.stats import gaussian_kde

from ....pd import to_xyz
from ....types import ArrayLike


class MatplotlibPlotMixin:
    """Mixin class for basic plotting operations."""
    
    def _get_ax_module(self):
        """Lazy import ax module to avoid circular imports."""
        from ....plt import ax as ax_module
        return ax_module

    def plot_image(
        self,
        arr_2d: ArrayLike,
        track: bool = True,
        id: Optional[str] = None,
        **kwargs,
    ) -> None:
        # Method Name for downstream csv exporting
        method_name = "plot_image"

        # Plotting with pure matplotlib methods under non-tracking context
        with self._no_tracking():
            self._axis_mpl = self._get_ax_module().plot_image(self._axis_mpl, arr_2d, **kwargs)

        # Tracking
        tracked_dict = {"image_df": pd.DataFrame(arr_2d)}
        if kwargs.get("xyz", False):
            tracked_dict["image_df"] = to_xyz(tracked_dict["image_df"])
        self._track(
            track,
            id,
            method_name,
            tracked_dict,
            None,
        )

        return self._axis_mpl

    def plot_kde(
        self,
        data: ArrayLike,
        cumulative=False,
        fill=False,
        track: bool = True,
        id: Optional[str] = None,
        **kwargs,
    ) -> None:
        # Method Name for downstream csv exporting
        method_name = "plot_kde"

        # Sample count as label
        n_samples = (~np.isnan(data)).sum()
        if kwargs.get("label"):
            kwargs["label"] = f"{kwargs['label']} (n={n_samples})"

        # Xlim (kwargs["xlim"] is not accepted in downstream plotters)
        xlim = kwargs.get("xlim")
        if not xlim:
            xlim = (np.nanmin(data), np.nanmax(data))

        # X
        xx = np.linspace(xlim[0], xlim[1], int(1e3))

        # Y
        density = gaussian_kde(data)(xx)
        density /= density.sum()

        # Cumulative
        if cumulative:
            density = np.cumsum(density)

        # Plotting with pure matplotlib methods under non-tracking context
        with self._no_tracking():
            # Filled Line
            if fill:
                self._axis_mpl.fill_between(
                    xx,
                    density,
                )
            # Simple Line
            else:
                self._axis_mpl.plot(xx, density)

        # Tracking
        tracked_dict = {
            "x": xx,
            "kde": density,
            "n": n_samples,
        }
        self._track(
            track,
            id,
            method_name,
            tracked_dict,
            None,
        )

        return self._axis_mpl

    def plot_conf_mat(
        self,
        data: ArrayLike,
        x_labels: Optional[List[str]] = None,
        y_labels: Optional[List[str]] = None,
        title: str = "Confusion Matrix",
        cmap: str = "Blues",
        cbar: bool = True,
        cbar_kw: Dict[str, Any] = {},
        label_rotation_xy: Tuple[float, float] = (15, 15),
        x_extend_ratio: float = 1.0,
        y_extend_ratio: float = 1.0,
        calc_bacc: bool = False,
        track: bool = True,
        id: Optional[str] = None,
        **kwargs,
    ) -> None:
        # Method Name for downstream csv exporting
        method_name = "plot_conf_mat"

        # Plotting with pure matplotlib methods under non-tracking context
        with self._no_tracking():
            self._axis_mpl, bacc_val = self._get_ax_module().plot_conf_mat(
                self._axis_mpl,
                data,
                x_labels=x_labels,
                y_labels=y_labels,
                title=title,
                cmap=cmap,
                cbar=cbar,
                cbar_kw=cbar_kw,
                label_rotation_xy=label_rotation_xy,
                x_extend_ratio=x_extend_ratio,
                y_extend_ratio=y_extend_ratio,
                calc_bacc=calc_bacc,
                **kwargs,
            )

        tracked_dict = {"balanced_accuracy": bacc_val}
        # Tracking
        self._track(track, id, method_name, tracked_dict, None)

        return self._axis_mpl, bacc_val

    # @wraps removed to avoid circular import
    def plot_rectangle(
        self,
        xx: float,
        yy: float,
        width: float,
        height: float,
        track: bool = True,
        id: Optional[str] = None,
        **kwargs,
    ) -> None:
        # Method Name for downstream csv exporting
        method_name = "plot_rectangle"

        # Plotting with pure matplotlib methods under non-tracking context
        with self._no_tracking():
            self._axis_mpl = self._get_ax_module().plot_rectangle(
                self._axis_mpl, xx, yy, width, height, **kwargs
            )

        # Tracking
        tracked_dict = {"xx": xx, "yy": yy, "width": width, "height": height}
        self._track(track, id, method_name, tracked_dict, None)

        return self._axis_mpl

    # @wraps removed to avoid circular import
    def plot_fillv(
        self,
        starts: ArrayLike,
        ends: ArrayLike,
        color: str = "red",
        alpha: float = 0.2,
        track: bool = True,
        id: Optional[str] = None,
        **kwargs,
    ) -> None:
        # Method Name for downstream csv exporting
        method_name = "plot_fillv"

        # Plotting with pure matplotlib methods under non-tracking context
        with self._no_tracking():
            self._axis_mpl = self._get_ax_module().plot_fillv(
                self._axis_mpl, starts, ends, color=color, alpha=alpha
            )

        # Tracking
        tracked_dict = {"starts": starts, "ends": ends}
        self._track(track, id, method_name, tracked_dict, None)

        return self._axis_mpl

    def plot_box(
        self,
        data: ArrayLike,
        track: bool = True,
        id: Optional[str] = None,
        **kwargs,
    ) -> None:
        # Method Name for downstream csv exporting
        method_name = "plot_box"

        # Copy data
        _data = data.copy()

        # Sample count as label
        n = len(data)
        if kwargs.get("label"):
            kwargs["label"] = kwargs["label"] + f" (n={n})"

        # Plotting with pure matplotlib methods under non-tracking context
        with self._no_tracking():
            self._axis_mpl.boxplot(data, **kwargs)

        # Tracking
        tracked_dict = {
            "data": _data,
            "n": [n for ii in range(len(data))],
        }
        self._track(track, id, method_name, tracked_dict, None)

        return self._axis_mpl
        
    def hist(
        self,
        x: ArrayLike,
        bins: Union[int, str, ArrayLike] = 10,
        range: Optional[Tuple[float, float]] = None,
        align_bins: bool = True,
        track: bool = True,
        id: Optional[str] = None,
        **kwargs,
    ) -> None:
        """
        Plot a histogram.
        
        This is an override of the standard matplotlib hist function to ensure
        that histogram bin data is properly tracked for CSV export and bins are
        aligned for histograms on the same axis.
        
        Args:
            x: Input data
            bins: Bin specification (count, edges, or algorithm)
            range: Optional histogram range (min, max)
            align_bins: Whether to align bins with other histograms on this axis
            track: Whether to track this operation
            id: Identifier for tracking
            **kwargs: Additional keywords passed to matplotlib hist
            
        Returns:
            Histogram output
        """
        # Method Name for downstream csv exporting
        method_name = "hist"
        
        # Get the axis ID for bin alignment
        axis_id = str(hash(self._axis_mpl))
        hist_id = id if id is not None else str(self.id)
        
        # Align bins if requested and not the first histogram on this axis
        if align_bins:
            from ....plt.utils import histogram_bin_manager
            bins, range = histogram_bin_manager.register_histogram(
                axis_id, hist_id, x, bins, range
            )
        
        # Plotting with pure matplotlib methods under non-tracking context
        with self._no_tracking():
            hist_data = self._axis_mpl.hist(x, bins=bins, range=range, **kwargs)
        
        # Save histogram result for CSV export
        # hist_data[0] = counts, hist_data[1] = bin_edges
        tracked_dict = {
            "args": (x,),
            "hist_result": (hist_data[0], hist_data[1]),
            "bins": bins,
            "range": range,
        }
        
        self._track(track, id, method_name, tracked_dict, kwargs)
        
        return hist_data

    # @wraps removed to avoid circular import
    def plot_raster(
        self,
        positions: List[ArrayLike],
        time: Optional[ArrayLike] = None,
        labels: Optional[List[str]] = None,
        colors: Optional[List[str]] = None,
        track: bool = True,
        id: Optional[str] = None,
        **kwargs,
    ) -> None:
        # Method Name for downstream csv exporting
        method_name = "plot_raster"

        # Plotting with pure matplotlib methods under non-tracking context
        with self._no_tracking():
            self._axis_mpl, raster_digit_df = self._get_ax_module().plot_raster(
                self._axis_mpl, positions, time=time
            )

        # Tracking
        tracked_dict = {"raster_digit_df": raster_digit_df}
        self._track(track, id, method_name, tracked_dict, None)

        return self._axis_mpl, raster_digit_df

    # @wraps removed to avoid circular import
    def plot_ecdf(
        self,
        data: ArrayLike,
        track: bool = True,
        id: Optional[str] = None,
        **kwargs,
    ) -> None:
        # Method Name for downstream csv exporting
        method_name = "plot_ecdf"

        # Plotting with pure matplotlib methods under non-tracking context
        with self._no_tracking():
            self._axis_mpl, ecdf_df = self._get_ax_module().plot_ecdf(
                self._axis_mpl, data, **kwargs
            )

        # Tracking
        tracked_dict = {"ecdf_df": ecdf_df}
        self._track(track, id, method_name, tracked_dict, None)

        return self._axis_mpl, ecdf_df

    # @wraps removed to avoid circular import
    def plot_joyplot(
        self,
        data: ArrayLike,
        orientation: str = "vertical",
        track: bool = True,
        id: Optional[str] = None,
        **kwargs,
    ) -> None:
        # Method Name for downstream csv exporting
        method_name = "plot_joyplot"

        # Plotting with pure matplotlib methods under non-tracking context
        with self._no_tracking():
            self._axis_mpl = self._get_ax_module().plot_joyplot(
                self._axis_mpl, data, orientation=orientation, **kwargs
            )

        # Tracking
        tracked_dict = {"joyplot_data": data}
        self._track(track, id, method_name, tracked_dict, None)

        return self._axis_mpl

    # @wraps removed to avoid circular import
    def plot_joyplot(
        self,
        data: ArrayLike,
        track: bool = True,
        id: Optional[str] = None,
        **kwargs,
    ) -> None:
        # Method Name for downstream csv exporting
        method_name = "plot_joyplot"

        # Plotting with pure matplotlib methods under non-tracking context
        with self._no_tracking():
            self._axis_mpl = self._get_ax_module().plot_joyplot(self._axis_mpl, data, **kwargs)

        # Tracking
        tracked_dict = {"joyplot_data": data}
        self._track(track, id, method_name, tracked_dict, None)

        return self._axis_mpl

    # @wraps removed to avoid circular import
    def plot_scatter_hist(
        self,
        x: ArrayLike,
        y: ArrayLike,
        hist_bins: int = 20,
        scatter_alpha: float = 0.6,
        scatter_size: float = 20,
        scatter_color: str = "blue",
        hist_color_x: str = "blue",
        hist_color_y: str = "red",
        hist_alpha: float = 0.5,
        scatter_ratio: float = 0.8,
        track: bool = True,
        id: Optional[str] = None,
        **kwargs,
    ) -> None:
        """Plot a scatter plot with marginal histograms."""
        # Method Name for downstream csv exporting
        method_name = "plot_scatter_hist"

        # Plotting with pure matplotlib methods under non-tracking context
        with self._no_tracking():
            self._axis_mpl, ax_histx, ax_histy, hist_data = self._get_ax_module().plot_scatter_hist(
                self._axis_mpl,
                x,
                y,
                hist_bins=hist_bins,
                scatter_alpha=scatter_alpha,
                scatter_size=scatter_size,
                scatter_color=scatter_color,
                hist_color_x=hist_color_x,
                hist_color_y=hist_color_y,
                hist_alpha=hist_alpha,
                scatter_ratio=scatter_ratio,
                **kwargs,
            )

        # Tracking
        tracked_dict = {
            "x": x,
            "y": y,
            "hist_x": hist_data["hist_x"],
            "hist_y": hist_data["hist_y"],
            "bin_edges_x": hist_data["bin_edges_x"],
            "bin_edges_y": hist_data["bin_edges_y"],
        }
        self._track(track, id, method_name, tracked_dict, None)

        return self._axis_mpl, ax_histx, ax_histy, hist_data

    # @wraps removed to avoid circular import
    def plot_heatmap(
        self,
        data: ArrayLike,
        x_labels: Optional[List[str]] = None,
        y_labels: Optional[List[str]] = None,
        cmap: str = "viridis",
        cbar_label: str = "ColorBar Label",
        value_format: str = "{x:.1f}",
        show_annot: bool = True,
        annot_color_lighter: str = "white",
        annot_color_darker: str = "black",
        track: bool = True,
        id: Optional[str] = None,
        **kwargs,
    ) -> Tuple[matplotlib.image.AxesImage, matplotlib.colorbar.Colorbar]:
        """Plot a heatmap on the axes."""
        # Method Name for downstream csv exporting
        method_name = "plot_heatmap"

        # Plotting with pure matplotlib methods under non-tracking context
        with self._no_tracking():
            ax, im, cbar = self._get_ax_module().plot_heatmap(
                self._axis_mpl,
                data,
                x_labels=x_labels,
                y_labels=y_labels,
                cmap=cmap,
                cbar_label=cbar_label,
                value_format=value_format,
                show_annot=show_annot,
                annot_color_lighter=annot_color_lighter,
                annot_color_darker=annot_color_darker,
                **kwargs,
            )

        # Tracking
        tracked_dict = {
            "data": data,
            "x_labels": x_labels,
            "y_labels": y_labels,
        }
        self._track(track, id, method_name, tracked_dict, None)

        return ax, im, cbar

    # @wraps removed to avoid circular import
    def plot_violin(
        self,
        data: Union[pd.DataFrame, List, ArrayLike],
        x=None,
        y=None,
        hue=None,
        labels=None,
        colors=None,
        half=False,
        track: bool = True,
        id: Optional[str] = None,
        **kwargs,
    ) -> None:
        """Plot a violin plot."""
        # Method Name for downstream csv exporting
        method_name = "plot_violin"

        # Plotting with pure matplotlib methods under non-tracking context
        with self._no_tracking():
            # Handle the list-style input case
            if isinstance(data, list) and all(
                isinstance(item, (list, np.ndarray)) for item in data
            ):
                self._axis_mpl = self._get_ax_module().plot_violin(
                    self._axis_mpl,
                    data_list=data,
                    labels=labels,
                    colors=colors,
                    half=half,
                    **kwargs,
                )
            # Handle DataFrame or other inputs
            else:
                self._axis_mpl = self._get_ax_module().plot_violin(
                    self._axis_mpl,
                    data=data,
                    x=x,
                    y=y,
                    hue=hue,
                    half=half,
                    **kwargs,
                )

        # Tracking
        tracked_dict = {
            "data": data,
            "x": x,
            "y": y,
            "hue": hue,
            "half": half,
            "labels": labels,
            "colors": colors,
        }
        self._track(track, id, method_name, tracked_dict, None)
        return self._axis_mpl

    # def plot_area(
    #     self,
    #     x: ArrayLike,
    #     y: ArrayLike,
    #     stacked: bool = False,
    #     fill: bool = True,
    #     alpha: float = 0.5,
    #     track: bool = True,
    #     id: Optional[str] = None,
    #     **kwargs,
    # ) -> None:
    #     """Plot an area plot."""
    #     # Method Name for downstream csv exporting
    #     method_name = "plot_area"

    #     # Plotting with pure matplotlib methods under non-tracking context
    #     with self._no_tracking():
    #         self._axis_mpl = self._get_ax_module().plot_area(
    #             self._axis_mpl,
    #             x,
    #             y,
    #             stacked=stacked,
    #             fill=fill,
    #             alpha=alpha,
    #             **kwargs,
    #         )

    #     # Tracking
    #     tracked_dict = {"x": x, "y": y}
    #     self._track(track, id, method_name, tracked_dict, None)

    #     return self._axis_mpl

    # def plot_radar(
    #     self,
    #     data: ArrayLike,
    #     categories: List[str],
    #     groups: Optional[List[str]] = None,
    #     fill: bool = True,
    #     alpha: float = 0.2,
    #     grid_step: int = 5,
    #     track: bool = True,
    #     id: Optional[str] = None,
    #     **kwargs,
    # ) -> None:
    #     """Plot a radar/spider chart."""
    #     # Method Name for downstream csv exporting
    #     method_name = "plot_radar"

    #     # Convert data to DataFrame if not already
    #     if not isinstance(data, pd.DataFrame):
    #         if groups is not None:
    #             data = pd.DataFrame(data, columns=categories, index=groups)
    #         else:
    #             data = pd.DataFrame(data, columns=categories)

    #     # Plotting with pure matplotlib methods under non-tracking context
    #     with self._no_tracking():
    #         self._axis_mpl = self._get_ax_module().plot_radar(
    #             self._axis_mpl,
    #             data,
    #             categories=categories,
    #             fill=fill,
    #             alpha=alpha,
    #             grid_step=grid_step,
    #             **kwargs,
    #         )

    #     # Tracking
    #     tracked_dict = {"radar_data": data}
    #     self._track(track, id, method_name, tracked_dict, None)

    #     return self._axis_mpl

    # def plot_bubble(
    #     self,
    #     x: ArrayLike,
    #     y: ArrayLike,
    #     size: ArrayLike,
    #     color: Optional[ArrayLike] = None,
    #     size_scale: float = 1000.0,
    #     alpha: float = 0.6,
    #     colormap: str = "viridis",
    #     show_colorbar: bool = True,
    #     colorbar_label: str = "",
    #     track: bool = True,
    #     id: Optional[str] = None,
    #     **kwargs,
    # ) -> None:
    #     """Plot a bubble chart."""
    #     # Method Name for downstream csv exporting
    #     method_name = "plot_bubble"

    #     # Plotting with pure matplotlib methods under non-tracking context
    #     with self._no_tracking():
    #         self._axis_mpl = self._get_ax_module().plot_bubble(
    #             self._axis_mpl,
    #             x,
    #             y,
    #             size,
    #             color=color,
    #             size_scale=size_scale,
    #             alpha=alpha,
    #             colormap=colormap,
    #             show_colorbar=show_colorbar,
    #             colorbar_label=colorbar_label,
    #             **kwargs,
    #         )

    #     # Tracking
    #     tracked_dict = {"x": x, "y": y, "size": size}
    #     if color is not None:
    #         tracked_dict["color"] = color

    #     self._track(track, id, method_name, tracked_dict, None)

    #     return self._axis_mpl

    # def plot_ridgeline(
    #     self,
    #     data: ArrayLike,
    #     labels: Optional[List[str]] = None,
    #     overlap: float = 0.8,
    #     fill: bool = True,
    #     alpha: float = 0.6,
    #     colormap: str = "viridis",
    #     bandwidth: Optional[float] = None,
    #     track: bool = True,
    #     id: Optional[str] = None,
    #     **kwargs,
    # ) -> None:
    #     """Plot a ridgeline plot (similar to joyplot but with KDE)."""
    #     # Method Name for downstream csv exporting
    #     method_name = "plot_ridgeline"

    #     # Ensure data is in correct format
    #     if isinstance(data, pd.DataFrame):
    #         _data = [data[col].dropna().values for col in data.columns]
    #         if labels is None:
    #             labels = list(data.columns)
    #     elif isinstance(data, list):
    #         _data = data
    #     else:
    #         _data = [data]

    #     # Plotting with pure matplotlib methods under non-tracking context
    #     with self._no_tracking():
    #         self._axis_mpl, ridge_data = self._get_ax_module().plot_ridgeline(
    #             self._axis_mpl,
    #             _data,
    #             labels=labels,
    #             overlap=overlap,
    #             fill=fill,
    #             alpha=alpha,
    #             colormap=colormap,
    #             bandwidth=bandwidth,
    #             **kwargs,
    #         )

    #     # Tracking
    #     tracked_dict = {
    #         "ridgeline_data": _data,
    #         "kde_x": ridge_data["kde_x"],
    #         "kde_y": ridge_data["kde_y"],
    #     }
    #     if labels is not None:
    #         tracked_dict["labels"] = labels
    #     self._track(track, id, method_name, tracked_dict, None)

    #     return self._axis_mpl, ridge_data

    # def plot_parallel_coordinates(
    #     self,
    #     data: pd.DataFrame,
    #     class_column: Optional[str] = None,
    #     colormap: str = "viridis",
    #     alpha: float = 0.5,
    #     track: bool = True,
    #     id: Optional[str] = None,
    #     **kwargs,
    # ) -> None:
    #     """Plot parallel coordinates."""
    #     # Method Name for downstream csv exporting
    #     method_name = "plot_parallel_coordinates"

    #     # Plotting with pure matplotlib methods under non-tracking context
    #     with self._no_tracking():
    #         self._axis_mpl = self._get_ax_module().plot_parallel_coordinates(
    #             self._axis_mpl,
    #             data,
    #             class_column=class_column,
    #             colormap=colormap,
    #             alpha=alpha,
    #             **kwargs,
    #         )

    #     # Tracking
    #     tracked_dict = {"parallel_data": data}
    #     self._track(track, id, method_name, tracked_dict, None)

    #     return self._axis_mpl

    # @wraps removed to avoid circular import
    def plot_line(
        self,
        data: ArrayLike,
        xx: Optional[ArrayLike] = None,
        track: bool = True,
        id: Optional[str] = None,
        **kwargs,
    ) -> None:
        """Plot a simple line."""
        # Method Name for downstream csv exporting
        method_name = "plot_line"

        # Plotting with pure matplotlib methods under non-tracking context
        with self._no_tracking():
            self._axis_mpl, plot_df = self._get_ax_module().plot_line(
                self._axis_mpl, data, xx=xx, **kwargs
            )

        # Tracking
        tracked_dict = {"plot_df": plot_df}
        self._track(track, id, method_name, tracked_dict, None)

        return self._axis_mpl, plot_df

    # @wraps removed to avoid circular import
    def plot_mean_std(
        self,
        data: ArrayLike,
        xx: Optional[ArrayLike] = None,
        sd: float = 1,
        track: bool = True,
        id: Optional[str] = None,
        **kwargs,
    ) -> None:
        """Plot mean line with standard deviation shading."""
        # Method Name for downstream csv exporting
        method_name = "plot_mean_std"

        # Plotting with pure matplotlib methods under non-tracking context
        with self._no_tracking():
            self._axis_mpl, plot_df = self._get_ax_module().plot_mean_std(
                self._axis_mpl, data, xx=xx, sd=sd, **kwargs
            )

        # Tracking
        tracked_dict = {"plot_df": plot_df}
        self._track(track, id, method_name, tracked_dict, None)

        return self._axis_mpl, plot_df

    # @wraps removed to avoid circular import
    def plot_mean_ci(
        self,
        data: ArrayLike,
        xx: Optional[ArrayLike] = None,
        perc: float = 95,
        track: bool = True,
        id: Optional[str] = None,
        **kwargs,
    ) -> None:
        """Plot mean line with confidence interval shading."""
        # Method Name for downstream csv exporting
        method_name = "plot_mean_ci"

        # Plotting with pure matplotlib methods under non-tracking context
        with self._no_tracking():
            self._axis_mpl, plot_df = self._get_ax_module().plot_mean_ci(
                self._axis_mpl, data, xx=xx, perc=perc, **kwargs
            )

        # Tracking
        tracked_dict = {"plot_df": plot_df}
        self._track(track, id, method_name, tracked_dict, None)

        return self._axis_mpl, plot_df

    # @wraps removed to avoid circular import
    def plot_median_iqr(
        self,
        data: ArrayLike,
        xx: Optional[ArrayLike] = None,
        track: bool = True,
        id: Optional[str] = None,
        **kwargs,
    ) -> None:
        """Plot median line with interquartile range shading."""
        # Method Name for downstream csv exporting
        method_name = "plot_median_iqr"

        # Plotting with pure matplotlib methods under non-tracking context
        with self._no_tracking():
            self._axis_mpl, plot_df = self._get_ax_module().plot_median_iqr(
                self._axis_mpl, data, xx=xx, **kwargs
            )

        # Tracking
        tracked_dict = {"plot_df": plot_df}
        self._track(track, id, method_name, tracked_dict, None)

        return self._axis_mpl, plot_df

    # @wraps removed to avoid circular import
    def plot_shaded_line(
        self,
        xs: ArrayLike,
        ys_lower: ArrayLike,
        ys_middle: ArrayLike,
        ys_upper: ArrayLike,
        color: str or Optional[Union[str, List[str]]] = None,
        label: str or Optional[Union[str, List[str]]] = None,
        track: bool = True,
        id: Optional[str] = None,
        **kwargs,
    ) -> None:
        """Plot a line with shaded area between lower and upper bounds."""
        # Method Name for downstream csv exporting
        method_name = "plot_shaded_line"

        # Plotting with pure matplotlib methods under non-tracking context
        with self._no_tracking():
            self._axis_mpl, plot_df = self._get_ax_module().plot_shaded_line(
                self._axis_mpl,
                xs,
                ys_lower,
                ys_middle,
                ys_upper,
                color=color,
                label=label,
                **kwargs,
            )

        # Tracking
        tracked_dict = {"plot_df": plot_df}
        self._track(track, id, method_name, tracked_dict, None)

        return self._axis_mpl, plot_df

# EOF
