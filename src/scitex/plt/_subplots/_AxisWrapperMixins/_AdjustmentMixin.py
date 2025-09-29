#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-07 15:49:20 (ywatanabe)"
# File: /ssh:ywatanabe@sp:/home/ywatanabe/proj/.claude-worktree/scitex_repo/src/scitex/plt/_subplots/_AxisWrapperMixins/_AdjustmentMixin.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/plt/_subplots/_AxisWrapperMixins/_AdjustmentMixin.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from typing import List, Optional, Union

from ....plt import ax as ax_module


class AdjustmentMixin:
    """Mixin class for matplotlib axis adjustments."""

    def rotate_labels(
        self,
        x: float = None,
        y: float = None,
        x_ha: str = None,
        y_ha: str = None,
        x_va: str = None,
        y_va: str = None,
        auto_adjust: bool = True,
        scientific_convention: bool = True,
        tight_layout: bool = False,
    ) -> None:
        """Rotate x and y axis labels with automatic positioning.
        
        Parameters
        ----------
        x : float or None, optional
            Rotation angle for x-axis labels in degrees. 
            If None or 0, x-axis labels are not rotated. Default is None.
        y : float or None, optional
            Rotation angle for y-axis labels in degrees.
            If None or 0, y-axis labels are not rotated. Default is None.
        x_ha : str or None, optional
            Horizontal alignment for x-axis labels. If None, automatically determined.
        y_ha : str or None, optional
            Horizontal alignment for y-axis labels. If None, automatically determined.
        x_va : str or None, optional
            Vertical alignment for x-axis labels. If None, automatically determined.
        y_va : str or None, optional
            Vertical alignment for y-axis labels. If None, automatically determined.
        auto_adjust : bool, optional
            Whether to automatically adjust alignment. Default is True.
        scientific_convention : bool, optional
            Whether to follow scientific conventions. Default is True.
        tight_layout : bool, optional
            Whether to apply tight_layout to prevent overlapping. Default is False.
        """
        self._axis_mpl = ax_module.rotate_labels(
            self._axis_mpl, x=x, y=y, x_ha=x_ha, y_ha=y_ha,
            x_va=x_va, y_va=y_va, auto_adjust=auto_adjust,
            scientific_convention=scientific_convention,
            tight_layout=tight_layout
        )

    def legend(self, loc: str = "upper left", **kwargs) -> None:
        """Places legend at specified location, with support for outside positions.

        Parameters
        ----------
        loc : str
            Legend position. Standard matplotlib positions plus:
            - "outer": Automatically place legend outside plot area (right side)
            - "separate": Save legend as a separate figure file
            - upper/lower/center variants: e.g. "upper right out", "lower left out"
            - directional shortcuts: "right", "left", "upper", "lower"
            - center variants: "center right out", "center left out"
            - alternative formats: "right upper out", "left lower out" etc.
        **kwargs : dict
            Additional keyword arguments passed to legend()
            For "separate": can include 'filename' (default: 'legend.png')
        """
        import matplotlib.pyplot as plt
        
        # Handle special cases
        if loc == "outer":
            # Place legend outside on the right, adjusting figure to make room
            legend = self._axis_mpl.legend(
                loc='center left', 
                bbox_to_anchor=(1.02, 0.5),
                **kwargs
            )
            # Adjust figure to prevent legend cutoff
            if hasattr(self, '_figure_wrapper') and self._figure_wrapper:
                self._figure_wrapper._fig_mpl.tight_layout()
                self._figure_wrapper._fig_mpl.subplots_adjust(right=0.85)
            return legend
            
        elif loc == "separate":
            # Set flag to save legend separately when figure is saved
            import warnings
            
            handles, labels = self._axis_mpl.get_legend_handles_labels()
            if not handles:
                warnings.warn("No legend handles found. Create plots with labels first.")
                return None
            
            # Store legend params for later use during save
            fig = self._axis_mpl.get_figure()
            if not hasattr(fig, '_separate_legend_params'):
                fig._separate_legend_params = []
            
            # Extract separate-specific kwargs
            figsize = kwargs.pop('figsize', (4, 3))
            dpi = kwargs.pop('dpi', 150)
            frameon = kwargs.pop('frameon', True)
            fancybox = kwargs.pop('fancybox', True)
            shadow = kwargs.pop('shadow', True)
            
            # Store parameters for this axes
            # Include axis index or name for unique filenames
            axis_id = None
            
            # Try to find axis index in parent figure
            try:
                fig_axes = fig.get_axes()
                for idx, ax in enumerate(fig_axes):
                    if ax is self._axis_mpl:
                        axis_id = f"ax_{idx:02d}"
                        break
            except:
                pass
            
            # If not found, try subplot spec
            if axis_id is None and hasattr(self._axis_mpl, 'get_subplotspec'):
                try:
                    spec = self._axis_mpl.get_subplotspec()
                    if spec is not None:
                        # Get grid shape and position
                        gridspec = spec.get_gridspec()
                        nrows, ncols = gridspec.get_geometry()
                        rowspan = spec.rowspan
                        colspan = spec.colspan
                        # Calculate flat index from row/col position
                        row_start = rowspan.start if hasattr(rowspan, 'start') else rowspan
                        col_start = colspan.start if hasattr(colspan, 'start') else colspan
                        flat_idx = row_start * ncols + col_start
                        axis_id = f"ax_{flat_idx:02d}"
                except:
                    pass
            
            # Fallback to sequential numbering
            if axis_id is None:
                axis_id = f"ax_{len(fig._separate_legend_params):02d}"
                
            fig._separate_legend_params.append({
                'axis': self._axis_mpl,
                'axis_id': axis_id,
                'handles': handles,
                'labels': labels,
                'figsize': figsize,
                'dpi': dpi,
                'frameon': frameon,
                'fancybox': fancybox,
                'shadow': shadow,
                'kwargs': kwargs
            })
            
            # Remove legend from main figure immediately
            if self._axis_mpl.get_legend():
                self._axis_mpl.get_legend().remove()
            
            return None

        # Original outside positions
        outside_positions = {
            # Upper right variants
            "upper right out": ("center left", (1.15, 0.85)),
            "right upper out": ("center left", (1.15, 0.85)),
            # Center right variants
            "center right out": ("center left", (1.15, 0.5)),
            "right out": ("center left", (1.15, 0.5)),
            "right": ("center left", (1.05, 0.5)),
            # Lower right variants
            "lower right out": ("center left", (1.15, 0.15)),
            "right lower out": ("center left", (1.15, 0.15)),
            # Upper left variants
            "upper left out": ("center right", (-0.25, 0.85)),
            "left upper out": ("center right", (-0.25, 0.85)),
            # Center left variants
            "center left out": ("center right", (-0.25, 0.5)),
            "left out": ("center right", (-0.25, 0.5)),
            "left": ("center right", (-0.15, 0.5)),
            # Lower left variants
            "lower left out": ("center right", (-0.25, 0.15)),
            "left lower out": ("center right", (-0.25, 0.15)),
            # Upper center variants
            "upper center out": ("lower center", (0.5, 1.25)),
            "upper out": ("lower center", (0.5, 1.25)),
            # Lower center variants
            "lower center out": ("upper center", (0.5, -0.25)),
            "lower out": ("upper center", (0.5, -0.25)),
        }

        if loc in outside_positions:
            location, bbox = outside_positions[loc]
            return self._axis_mpl.legend(loc=location, bbox_to_anchor=bbox, **kwargs)
        return self._axis_mpl.legend(loc=loc, **kwargs)

    def set_xyt(
        self,
        x: Optional[str] = None,
        y: Optional[str] = None,
        t: Optional[str] = None,
        format_labels: bool = True,
    ) -> None:
        self._axis_mpl = ax_module.set_xyt(
            self._axis_mpl,
            x=x,
            y=y,
            t=t,
            format_labels=format_labels,
        )

    def set_xytc(
        self,
        x: Optional[str] = None,
        y: Optional[str] = None,
        t: Optional[str] = None,
        c: Optional[str] = None,
        format_labels: bool = True,
    ) -> None:
        """Set xlabel, ylabel, title, and caption for automatic saving.

        Parameters
        ----------
        x : str, optional
            X-axis label
        y : str, optional
            Y-axis label
        t : str, optional
            Title
        c : str, optional
            Caption to be saved automatically with scitex.io.save()
        format_labels : bool, optional
            Whether to apply automatic formatting, by default True
        """
        self._axis_mpl = ax_module.set_xytc(
            self._axis_mpl,
            x=x,
            y=y,
            t=t,
            c=c,
            format_labels=format_labels,
        )

        # Store caption in this wrapper for easy access
        if c is not False and c is not None:
            self._scitex_caption = c

    def set_supxyt(
        self,
        xlabel: Optional[str] = None,
        ylabel: Optional[str] = None,
        title: Optional[str] = None,
        format_labels: bool = True,
    ) -> None:
        self._axis_mpl = ax_module.set_supxyt(
            self._axis_mpl,
            xlabel=xlabel,
            ylabel=ylabel,
            title=title,
            format_labels=format_labels,
        )

    def set_supxytc(
        self,
        xlabel: Optional[str] = None,
        ylabel: Optional[str] = None,
        title: Optional[str] = None,
        caption: Optional[str] = None,
        format_labels: bool = True,
    ) -> None:
        """Set figure-level xlabel, ylabel, title, and caption for automatic saving.

        Parameters
        ----------
        xlabel : str, optional
            Figure-level X-axis label
        ylabel : str, optional
            Figure-level Y-axis label
        title : str, optional
            Figure-level title (suptitle)
        caption : str, optional
            Figure-level caption to be saved automatically with scitex.io.save()
        format_labels : bool, optional
            Whether to apply automatic formatting, by default True
        """
        self._axis_mpl = ax_module.set_supxytc(
            self._axis_mpl,
            xlabel=xlabel,
            ylabel=ylabel,
            title=title,
            caption=caption,
            format_labels=format_labels,
        )

        # Store figure-level caption for easy access
        if caption is not False and caption is not None:
            fig = self._axis_mpl.get_figure()
            fig._scitex_main_caption = caption

    def set_meta(
        self,
        caption=None,
        methods=None,
        stats=None,
        keywords=None,
        experimental_details=None,
        journal_style=None,
        significance=None,
        **kwargs
    ) -> None:
        """Set comprehensive scientific metadata with YAML export capability.

        Parameters
        ----------
        caption : str, optional
            Figure caption text
        methods : str, optional
            Experimental methods description
        stats : str, optional
            Statistical analysis details
        keywords : List[str], optional
            Keywords for categorization
        experimental_details : Dict[str, Any], optional
            Structured experimental parameters
        journal_style : str, optional
            Target journal style
        significance : str, optional
            Significance statement
        **kwargs : additional metadata
            Any additional metadata fields
        """
        self._axis_mpl = ax_module.set_meta(
            self._axis_mpl,
            caption=caption,
            methods=methods,
            stats=stats,
            keywords=keywords,
            experimental_details=experimental_details,
            journal_style=journal_style,
            significance=significance,
            **kwargs
        )

    def set_figure_meta(
        self,
        caption=None,
        methods=None,
        stats=None,
        significance=None,
        funding=None,
        conflicts=None,
        data_availability=None,
        **kwargs
    ) -> None:
        """Set figure-level metadata for multi-panel figures.

        Parameters
        ----------
        caption : str, optional
            Figure-level caption
        methods : str, optional
            Overall experimental methods
        stats : str, optional
            Overall statistical approach
        significance : str, optional
            Significance and implications
        funding : str, optional
            Funding acknowledgments
        conflicts : str, optional
            Conflict of interest statement
        data_availability : str, optional
            Data availability statement
        **kwargs : additional metadata
            Any additional figure-level metadata
        """
        self._axis_mpl = ax_module.set_figure_meta(
            self._axis_mpl,
            caption=caption,
            methods=methods,
            stats=stats,
            significance=significance,
            funding=funding,
            conflicts=conflicts,
            data_availability=data_availability,
            **kwargs
        )

    def set_ticks(
        self,
        xvals: Optional[List[Union[int, float]]] = None,
        xticks: Optional[List[str]] = None,
        yvals: Optional[List[Union[int, float]]] = None,
        yticks: Optional[List[str]] = None,
    ) -> None:
        self._axis_mpl = ax_module.set_ticks(
            self._axis_mpl,
            xvals=xvals,
            xticks=xticks,
            yvals=yvals,
            yticks=yticks,
        )

    def set_n_ticks(self, n_xticks: int = 4, n_yticks: int = 4) -> None:
        self._axis_mpl = ax_module.set_n_ticks(
            self._axis_mpl, n_xticks=n_xticks, n_yticks=n_yticks
        )

    def hide_spines(
        self,
        top: bool = True,
        bottom: bool = False,
        left: bool = False,
        right: bool = True,
        ticks: bool = False,
        labels: bool = False,
    ) -> None:
        self._axis_mpl = ax_module.hide_spines(
            self._axis_mpl,
            top=top,
            bottom=bottom,
            left=left,
            right=right,
            ticks=ticks,
            labels=labels,
        )

    def extend(self, x_ratio: float = 1.0, y_ratio: float = 1.0) -> None:
        self._axis_mpl = ax_module.extend(
            self._axis_mpl, x_ratio=x_ratio, y_ratio=y_ratio
        )

    def shift(self, dx: float = 0, dy: float = 0) -> None:
        self._axis_mpl = ax_module.shift(self._axis_mpl, dx=dx, dy=dy)

# EOF
