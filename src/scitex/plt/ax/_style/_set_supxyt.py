#!./env/bin/python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-07-13 07:56:46 (ywatanabe)"
# Author: Yusuke Watanabe (ywatanabe@scitex.ai)

"""
This script does XYZ.
"""

# Imports
import matplotlib.pyplot as plt

from ._format_label import format_label


# Functions
def set_supxyt(ax, xlabel=False, ylabel=False, title=False, format_labels=True):
    """Sets xlabel, ylabel and title"""
    fig = ax.get_figure()

    # if xlabel is not False:
    #     fig.supxlabel(xlabel)

    # if ylabel is not False:
    #     fig.supylabel(ylabel)

    # if title is not False:
    #     fig.suptitle(title)
    if xlabel is not False:
        xlabel = format_label(xlabel) if format_labels else xlabel
        fig.supxlabel(xlabel)

    if ylabel is not False:
        ylabel = format_label(ylabel) if format_labels else ylabel
        fig.supylabel(ylabel)

    if title is not False:
        title = format_label(title) if format_labels else title
        fig.suptitle(title)

    return ax


def set_supxytc(ax, xlabel=False, ylabel=False, title=False, caption=False, methods=False, stats=False, significance=False, format_labels=True):
    """Sets figure-level xlabel, ylabel, title, and caption with SciTeX-Paper integration
    
    Parameters
    ----------
    ax : matplotlib.axes.Axes or scitex AxisWrapper
        The axes to modify (figure accessed via ax.get_figure())
    xlabel : str or False, optional
        Figure-level X-axis label, by default False
    ylabel : str or False, optional 
        Figure-level Y-axis label, by default False
    title : str or False, optional
        Figure-level title (suptitle), by default False
    caption : str or False, optional
        Figure-level caption to store for later use with scitex.io.save(), by default False
    methods : str or False, optional
        Overall methods description for SciTeX-Paper integration, by default False
    stats : str or False, optional
        Overall statistical analysis details for SciTeX-Paper integration, by default False
    significance : str or False, optional
        Significance statement for SciTeX-Paper integration, by default False
    format_labels : bool, optional
        Whether to apply automatic formatting, by default True
        
    Returns
    -------
    ax : matplotlib.axes.Axes or scitex AxisWrapper
        The modified axes
        
    Examples
    --------
    >>> fig, ((ax1, ax2), (ax3, ax4)) = scitex.plt.subplots(2, 2)
    >>> # Add plots to each panel...
    >>> ax1.set_supxytc(xlabel='Time (s)', ylabel='Signal Amplitude', 
    ...                 title='Multi-Panel Analysis',
    ...                 caption='Comprehensive analysis showing (A) raw data, (B) filtered signal, (C) power spectrum, and (D) phase analysis.',
    ...                 methods='All experiments performed using standardized protocols.',
    ...                 significance='This work demonstrates novel therapeutic targets.')
    >>> scitex.io.save(fig, 'multi_panel.png')  # Caption automatically saved
    """
    # Set labels and title using existing function
    set_supxyt(ax, xlabel=xlabel, ylabel=ylabel, title=title, format_labels=format_labels)
    
    # Store figure-level caption and extended metadata
    if caption is not False or methods is not False or stats is not False or significance is not False:
        fig = ax.get_figure()
        # Store comprehensive figure-level metadata
        fig_metadata = {
            'main_caption': caption if caption is not False else None,
            'methods': methods if methods is not False else None,
            'stats': stats if stats is not False else None,
            'significance': significance if significance is not False else None
        }
        
        fig._scitex_figure_metadata = fig_metadata
        
        # Backward compatibility - also store simple caption
        if caption is not False:
            fig._scitex_main_caption = caption
    
    return ax


if __name__ == "__main__":
    # Start
    CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.session.start(sys, plt)

    # (YOUR AWESOME CODE)

    # Close
    scitex.session.close(CONFIG)

# EOF
