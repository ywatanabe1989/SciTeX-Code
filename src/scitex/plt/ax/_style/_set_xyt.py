#!./env/bin/python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-07-13 08:14:19 (ywatanabe)"
# Author: Yusuke Watanabe (ywatanabe@scitex.ai)

"""
This script does XYZ.
"""

# Imports
import matplotlib.pyplot as plt

from ._format_label import format_label


# Functions
def set_xyt(ax, x=False, y=False, t=False, format_labels=True):
    """Sets xlabel, ylabel and title"""

    if x is not False:
        x = format_label(x) if format_labels else x
        ax.set_xlabel(x)

    if y is not False:
        y = format_label(y) if format_labels else y
        ax.set_ylabel(y)

    if t is not False:
        t = format_label(t) if format_labels else t
        ax.set_title(t)

    return ax


def set_xytc(ax, x=False, y=False, t=False, c=False, methods=False, stats=False, format_labels=True):
    """Sets xlabel, ylabel, title, and caption with SciTeX-Paper integration
    
    Parameters
    ----------
    ax : matplotlib.axes.Axes or scitex AxisWrapper
        The axes to modify
    x : str or False, optional
        X-axis label, by default False
    y : str or False, optional 
        Y-axis label, by default False
    t : str or False, optional
        Title, by default False
    c : str or False, optional
        Caption to store for later use with scitex.io.save(), by default False
    methods : str or False, optional
        Methods description for SciTeX-Paper integration, by default False
    stats : str or False, optional
        Statistical analysis details for SciTeX-Paper integration, by default False
    format_labels : bool, optional
        Whether to apply automatic formatting, by default True
        
    Returns
    -------
    ax : matplotlib.axes.Axes or scitex AxisWrapper
        The modified axes
        
    Examples
    --------
    >>> fig, ax = scitex.plt.subplots()
    >>> ax.plot(x, y)
    >>> ax.set_xytc(x='Time (s)', y='Voltage (mV)', 
    ...             t='Neural Signal', 
    ...             c='Example neural recording showing action potentials.',
    ...             methods='Intracellular recordings performed using patch-clamp technique.',
    ...             stats='Data analyzed using t-test with p<0.05 significance.')
    >>> scitex.io.save(fig, 'neural_signal.png')  # Caption automatically saved
    """
    # Set labels and title using existing function
    set_xyt(ax, x=x, y=y, t=t, format_labels=format_labels)
    
    # Store caption and extended metadata for later use by scitex.io.save()
    if c is not False or methods is not False or stats is not False:
        # Store comprehensive metadata as axis attribute for retrieval by save function
        metadata = {
            'caption': c if c is not False else None,
            'methods': methods if methods is not False else None,
            'stats': stats if stats is not False else None
        }
        
        if hasattr(ax, '_scitex_metadata'):
            ax._scitex_metadata.update(metadata)
        else:
            # For matplotlib axes, store in figure metadata
            fig = ax.get_figure()
            if not hasattr(fig, '_scitex_metadata'):
                fig._scitex_metadata = {}
            # Use axis position as identifier
            fig._scitex_metadata[ax] = metadata
            
        # Backward compatibility - also store simple caption
        if c is not False:
            if hasattr(ax, '_scitex_caption'):
                ax._scitex_caption = c
            else:
                fig = ax.get_figure()
                if not hasattr(fig, '_scitex_captions'):
                    fig._scitex_captions = {}
                fig._scitex_captions[ax] = c
    
    return ax


if __name__ == "__main__":
    # Start
    CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.session.start(sys, plt)

    # (YOUR AWESOME CODE)

    # Close
    scitex.session.close(CONFIG)

# EOF

"""
/ssh:ywatanabe@444:/home/ywatanabe/proj/entrance/scitex/plt/ax/_set_lt.py
"""
