.. MNGS documentation master file

MNGS - Python Utilities for Scientific Computing
=================================================

**MNGS** (pronounced "monogusa", meaning "lazy" in Japanese) is a comprehensive Python package designed to streamline scientific computing workflows. It provides a unified interface for common tasks in data science, machine learning, and signal processing.

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   installation
   quickstart
   core_concepts

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   modules/index
   workflows/index
   best_practices

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/mngs.gen
   api/mngs.io
   api/mngs.plt
   api/mngs.dsp
   api/mngs.stats
   api/mngs.pd
   api/mngs.ai
   api/mngs.nn
   api/mngs.db

.. toctree::
   :maxdepth: 2
   :caption: Examples

   examples/basic_usage
   examples/data_analysis
   examples/signal_processing
   examples/machine_learning

.. toctree::
   :maxdepth: 1
   :caption: Development

   contributing
   changelog
   license

Key Features
------------

- **Unified Interface**: Consistent API across all modules
- **Scientific Focus**: Tools optimized for research workflows
- **GPU Acceleration**: PyTorch-based implementations where applicable
- **Data Preservation**: Automatic logging and data export
- **Robust Error Handling**: Graceful handling of edge cases and NaN values

Quick Example
-------------

.. code-block:: python

    import mngs
    
    # Start a managed session with automatic logging
    CONFIG, sys.stdout, sys.stderr, plt, CC = mngs.gen.start(sys, plt)
    
    # Load and process data
    data = mngs.io.load("data.pkl")
    
    # Create enhanced plots with automatic data export
    fig, axes = mngs.plt.subplots(2, 2)
    axes[0, 0].plot(data['time'], data['signal'])
    
    # Perform signal processing
    filtered = mngs.dsp.filt.bandpass(data['signal'], fs=1000, low=1, high=50)
    
    # Statistical analysis
    results = mngs.stats.corr_test(data['x'], data['y'])
    
    # Clean up and save logs
    mngs.gen.close(CONFIG)

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`