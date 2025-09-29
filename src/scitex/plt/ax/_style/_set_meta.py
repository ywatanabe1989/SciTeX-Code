#!./env/bin/python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-04 11:35:00 (ywatanabe)"
# Author: Yusuke Watanabe (ywata1989@gmail.com)

"""
Scientific metadata management for figures with YAML export.
"""

# Imports
import yaml
from typing import Optional, List, Dict, Any


# Functions
def set_meta(ax, caption=None, methods=None, stats=None, keywords=None, 
             experimental_details=None, journal_style=None, 
             significance=None, **kwargs):
    """Set comprehensive scientific metadata for figures with YAML export
    
    Parameters
    ----------
    ax : matplotlib.axes.Axes or scitex AxisWrapper
        The axes to modify
    caption : str, optional
        Figure caption text
    methods : str, optional
        Experimental methods description
    stats : str, optional
        Statistical analysis details
    keywords : List[str], optional
        Keywords for categorization and search
    experimental_details : Dict[str, Any], optional
        Structured experimental parameters (n_samples, temperature, etc.)
    journal_style : str, optional
        Target journal style ('nature', 'science', 'ieee', 'cell', etc.)
    significance : str, optional
        Significance statement or implications
    **kwargs : additional metadata
        Any additional metadata fields
        
    Returns
    -------
    ax : matplotlib.axes.Axes or scitex AxisWrapper
        The modified axes
        
    Examples
    --------
    >>> fig, ax = scitex.plt.subplots()
    >>> ax.plot(x, y, id='neural_data')
    >>> ax.set_xyt(x='Time (ms)', y='Voltage (mV)', t='Neural Recording')
    >>> ax.set_meta(
    ...     caption='Intracellular recording showing action potentials.',
    ...     methods='Whole-cell patch-clamp in acute brain slices.',
    ...     stats='Statistical analysis using paired t-test (p<0.05).',
    ...     keywords=['electrophysiology', 'neural_recording', 'patch_clamp'],
    ...     experimental_details={
    ...         'n_samples': 15,
    ...         'temperature': 32,
    ...         'recording_duration': 600,
    ...         'electrode_resistance': '3-5 MΩ'
    ...     },
    ...     journal_style='nature',
    ...     significance='Demonstrates novel neural dynamics in layer 2/3 pyramidal cells.'
    ... )
    >>> scitex.io.save(fig, 'neural_recording.png')  # YAML metadata auto-saved
    """
    
    # Build comprehensive metadata dictionary
    metadata = {}
    
    if caption is not None:
        metadata['caption'] = caption
    if methods is not None:
        metadata['methods'] = methods
    if stats is not None:
        metadata['statistical_analysis'] = stats
    if keywords is not None:
        metadata['keywords'] = keywords if isinstance(keywords, list) else [keywords]
    if experimental_details is not None:
        metadata['experimental_details'] = experimental_details
    if journal_style is not None:
        metadata['journal_style'] = journal_style
    if significance is not None:
        metadata['significance'] = significance
    
    # Add any additional metadata
    for key, value in kwargs.items():
        if value is not None:
            metadata[key] = value
    
    # Add automatic metadata
    import datetime
    metadata['created_timestamp'] = datetime.datetime.now().isoformat()
    
    # Get version dynamically
    try:
        import scitex
        metadata['scitex_version'] = getattr(scitex, '__version__', 'unknown')
    except ImportError:
        metadata['scitex_version'] = 'unknown'
    
    # Store metadata in figure for automatic saving
    fig = ax.get_figure()
    if not hasattr(fig, '_scitex_metadata'):
        fig._scitex_metadata = {}
    
    # Use axis as key for panel-specific metadata
    fig._scitex_metadata[ax] = metadata
    
    # Also store as YAML-ready structure
    if not hasattr(fig, '_scitex_yaml_metadata'):
        fig._scitex_yaml_metadata = {}
    fig._scitex_yaml_metadata[ax] = metadata
    
    # Backward compatibility - store simple caption
    if caption is not None:
        if not hasattr(fig, '_scitex_captions'):
            fig._scitex_captions = {}
        fig._scitex_captions[ax] = caption
    
    return ax


def set_figure_meta(ax, caption=None, methods=None, stats=None, significance=None,
                   funding=None, conflicts=None, data_availability=None, **kwargs):
    """Set figure-level metadata for multi-panel figures
    
    Parameters
    ----------
    ax : matplotlib.axes.Axes or scitex AxisWrapper
        Any axis in the figure (figure accessed via ax.get_figure())
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
        
    Returns
    -------
    ax : matplotlib.axes.Axes or scitex AxisWrapper
        The modified axes
        
    Examples
    --------
    >>> fig, ((ax1, ax2), (ax3, ax4)) = scitex.plt.subplots(2, 2)
    >>> # Set individual panel metadata...
    >>> ax1.set_meta(caption='Panel A analysis...')
    >>> ax2.set_meta(caption='Panel B comparison...')
    >>> 
    >>> # Set figure-level metadata
    >>> ax1.set_figure_meta(
    ...     caption='Comprehensive analysis of neural dynamics...',
    ...     significance='This work demonstrates novel therapeutic targets.',
    ...     funding='Supported by NIH grant R01-NS123456.',
    ...     data_availability='Data available at doi:10.5061/dryad.example'
    ... )
    """
    
    # Build figure-level metadata
    figure_metadata = {}
    
    if caption is not None:
        figure_metadata['main_caption'] = caption
    if methods is not None:
        figure_metadata['overall_methods'] = methods
    if stats is not None:
        figure_metadata['overall_statistics'] = stats
    if significance is not None:
        figure_metadata['significance'] = significance
    if funding is not None:
        figure_metadata['funding'] = funding
    if conflicts is not None:
        figure_metadata['conflicts_of_interest'] = conflicts
    if data_availability is not None:
        figure_metadata['data_availability'] = data_availability
    
    # Add any additional metadata
    for key, value in kwargs.items():
        if value is not None:
            figure_metadata[key] = value
    
    # Add automatic metadata
    import datetime
    figure_metadata['created_timestamp'] = datetime.datetime.now().isoformat()
    
    # Store in figure
    fig = ax.get_figure()
    fig._scitex_figure_metadata = figure_metadata
    
    # Backward compatibility
    if caption is not None:
        fig._scitex_main_caption = caption
    
    return ax


def export_metadata_yaml(fig, filepath):
    """Export all figure metadata to YAML file
    
    Parameters
    ----------
    fig : matplotlib.figure.Figure
        Figure with metadata
    filepath : str
        Output YAML file path
    """
    import datetime
    
    # Collect all metadata
    export_data = {
        'figure_metadata': {},
        'panel_metadata': {},
        'export_info': {
            'timestamp': datetime.datetime.now().isoformat(),
            'scitex_version': '1.11.0'
        }
    }
    
    # Figure-level metadata
    if hasattr(fig, '_scitex_figure_metadata'):
        export_data['figure_metadata'] = fig._scitex_figure_metadata
    
    # Panel-level metadata
    if hasattr(fig, '_scitex_yaml_metadata'):
        for i, (ax, metadata) in enumerate(fig._scitex_yaml_metadata.items()):
            panel_key = f'panel_{i+1}'
            export_data['panel_metadata'][panel_key] = metadata
    
    # Write YAML file
    with open(filepath, 'w') as f:
        yaml.dump(export_data, f, default_flow_style=False, sort_keys=False, indent=2)


if __name__ == "__main__":
    # Start
    import sys
    import matplotlib.pyplot as plt
    import scitex
    CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.session.start(sys, plt)

    # Example usage
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [1, 4, 2])
    
    set_meta(ax, 
             caption='Example figure showing data trends.',
             methods='Synthetic data generated for demonstration.',
             keywords=['example', 'demo', 'synthetic'],
             experimental_details={'n_samples': 3, 'data_type': 'synthetic'})
    
    export_metadata_yaml(fig, 'example_metadata.yaml')

    # Close
    scitex.session.close(CONFIG)

# EOF