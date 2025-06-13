#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-02 22:21:41 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/plt/ax/_plot/_plot_heatmap.py
# ----------------------------------------
import os

__FILE__ = "./src/scitex/plt/ax/_plot/_plot_heatmap.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import matplotlib
import matplotlib.pyplot as plt
import numpy as np


def plot_heatmap(
    ax,
    data,
    x_labels=None,
    y_labels=None,
    cmap="viridis",
    cbar_label="ColorBar Label",
    annot_format="{x:.1f}",
    show_annot=True,
    annot_color_lighter="black",
    annot_color_darker="white",
    **kwargs,
):
    """
    Plot a heatmap on the given axes.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes to plot on
    data : array-like
        The 2D data to display as heatmap
    x_labels : list, optional
        Labels for the x-axis
    y_labels : list, optional
        Labels for the y-axis
    cmap : str or matplotlib colormap, optional
        Colormap to use, default "viridis"
    cbar_label : str, optional
        Label for the colorbar, default "ColorBar Label"
    show_annot : bool, optional
        Whether to annotate the heatmap with values, default True
    annot_format : str, optional
        Format string for annotations, default "{x:.1f}"
    annot_color_lighter : str, optional
        Color for annotations on lighter background, default "black"
    annot_color_darker : str, optional
        Color for annotations on darker background, default "white"
    **kwargs
        Additional keyword arguments passed to matplotlib.axes.Axes.imshow()

    Returns
    -------
    im : matplotlib.image.AxesImage
        The image object created by imshow
    cbar : matplotlib.colorbar.Colorbar
        The colorbar object
    """

    im, cbar = _mpl_heatmap(
        data,
        x_labels,
        y_labels,
        ax=ax,
        cmap=cmap,
        cbarlabel=cbar_label,
    )

    if show_annot:
        textcolors = _switch_annot_colors(cmap, annot_color_lighter, annot_color_darker)
        texts = _mpl_annotate_heatmap(
            im,
            valfmt=annot_format,
            textcolors=textcolors,
        )

    return ax, im, cbar


def _switch_annot_colors(cmap, annot_color_lighter, annot_color_darker):
    # Get colormap
    cmap_obj = plt.cm.get_cmap(cmap)

    # Sample the colormap at its extremes
    dark_color = cmap_obj(0.1)  # Not using 0.0 to avoid edge effects
    light_color = cmap_obj(0.9)  # Not using 1.0 to avoid edge effects

    # Calculate perceived brightness
    dark_brightness = (
        0.2126 * dark_color[0] + 0.7152 * dark_color[1] + 0.0722 * dark_color[2]
    )
    light_brightness = (
        0.2126 * light_color[0] + 0.7152 * light_color[1] + 0.0722 * light_color[2]
    )

    # Choose text colors based on background brightness
    if dark_brightness < 0.5:
        return (annot_color_lighter, annot_color_darker)
    else:
        return (annot_color_darker, annot_color_lighter)


def _mpl_heatmap(
    data, row_labels, col_labels, ax=None, cbar_kw=None, cbarlabel="", **kwargs
):
    """
    A function to annotate a heatmap.

    Parameters
    ----------
    im : matplotlib.image.AxesImage
        The image to be annotated
    data : array-like, optional
        Data used to annotate. If None, the image's array is used
    valfmt : str or matplotlib.ticker.Formatter, optional
        Format of the annotations, default "{x:.2f}"
    textcolors : tuple of str, optional
        Colors for the annotations. The first is used for values below
        threshold, the second for those above, default ("lightgray", "black")
    threshold : float, optional
        Value in normalized colormap space (0 to 1) above which the
        second color is used. If None, 0.7*max(data) is used
    **textkw
        Additional keyword arguments passed to matplotlib.axes.Axes.text()

    Returns
    -------
    texts : list of matplotlib.text.Text
        The annotation text objects
    """

    if ax is None:
        ax = plt.gca()

    if cbar_kw is None:
        cbar_kw = {}

    # Plot the heatmap
    im = ax.imshow(data, **kwargs)

    # Create colorbar
    cbar = ax.figure.colorbar(im, ax=ax, **cbar_kw)
    cbar.ax.set_ylabel(cbarlabel, rotation=-90, va="bottom")

    # Show all ticks and label them with the respective list entries.
    ax.set_xticks(
        range(data.shape[1]),
        labels=col_labels,
        # rotation=45,
        # ha="right",
        # rotation_mode="anchor",
    )
    ax.set_yticks(range(data.shape[0]), labels=row_labels)

    # Let the horizontal axes labeling appear on top.
    ax.tick_params(top=False, bottom=True, labeltop=False, labelbottom=True)

    # Turn spines off
    ax.spines[:].set_visible(False)

    ax.set_xticks(np.arange(data.shape[1] + 1) - 0.5, minor=True)
    ax.set_yticks(np.arange(data.shape[0] + 1) - 0.5, minor=True)
    ax.tick_params(which="minor", bottom=False, left=False)

    return im, cbar


def _mpl_annotate_heatmap(
    im,
    data=None,
    valfmt="{x:.2f}",
    textcolors=("lightgray", "black"),
    threshold=None,
    **textkw,
):
    """
    A function to annotate a heatmap.

    Parameters
    ----------
    im : matplotlib.image.AxesImage
        The image to be annotated
    data : array-like, optional
        Data used to annotate. If None, the image's array is used
    valfmt : str or matplotlib.ticker.Formatter, optional
        Format of the annotations, default "{x:.2f}"
    textcolors : tuple of str, optional
        Colors for the annotations. The first is used for values below
        threshold, the second for those above, default ("lightgray", "black")
    threshold : float, optional
        Value in normalized colormap space (0 to 1) above which the
        second color is used. If None, 0.7*max(data) is used
    **textkw
        Additional keyword arguments passed to matplotlib.axes.Axes.text()

    Returns
    -------
    texts : list of matplotlib.text.Text
        The annotation text objects
    """

    if not isinstance(data, (list, np.ndarray)):
        data = im.get_array()

    # Normalize the threshold to the images color range.
    if threshold is not None:
        threshold = im.norm(threshold)
    else:
        # Use 0.7 instead of 0.5 for better visibility with most colormaps
        threshold = im.norm(data.max()) * 0.7

    # Set default alignment to center, but allow it to be
    # overwritten by textkw.
    kw = dict(horizontalalignment="center", verticalalignment="center")
    kw.update(textkw)

    # Get the formatter in case a string is supplied
    if isinstance(valfmt, str):
        valfmt = matplotlib.ticker.StrMethodFormatter(valfmt)

    # Loop over the data and create a `Text` for each "pixel".
    # Change the text's color depending on the data.
    texts = []
    for ii in range(data.shape[0]):
        for jj in range(data.shape[1]):
            kw.update(color=textcolors[int(im.norm(data[ii, jj]) > threshold)])
            text = im.axes.text(jj, ii, valfmt(data[ii, jj], None), **kw)
            texts.append(text)

    return texts


if __name__ == "__main__":
    import matplotlib
    import matplotlib as mpl
    import matplotlib.pyplot as plt
    import numpy as np

    data = np.random.rand(5, 10)
    x_labels = [f"X{ii+1}" for ii in range(5)]
    y_labels = [f"Y{ii+1}" for ii in range(10)]

    fig, ax = plt.subplots()

    im, cbar = plot_heatmap(
        ax,
        data,
        x_labels=x_labels,
        y_labels=y_labels,
        show_annot=True,
        annot_color_lighter="white",
        annot_color_darker="black",
        cmap="Blues",
    )

    fig.tight_layout()
    plt.show()
    # EOF

# EOF
