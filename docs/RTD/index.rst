.. SciTeX documentation master file

SciTeX - Scientific Tools from Literature to LaTeX Manuscript
===========================================================

.. image:: https://img.shields.io/pypi/v/scitex.svg
   :target: https://pypi.org/project/scitex/
   :alt: PyPI version

.. image:: https://img.shields.io/pypi/pyversions/scitex.svg
   :target: https://pypi.org/project/scitex/
   :alt: Python versions

**SciTeX** (Scientific tools from literature to LaTeX Manuscript) is a comprehensive Python package designed to streamline the entire scientific research workflow - from literature search and data analysis to publication-ready LaTeX manuscripts. It provides standardized tools for I/O operations, signal processing, plotting, statistics, literature management, and more.

Key Features
------------

* **Comprehensive I/O**: Support for 20+ file formats with unified interface
* **Signal Processing**: Advanced DSP tools for filtering, spectral analysis, and more
* **Enhanced Plotting**: matplotlib wrapper with automatic data tracking and export
* **Statistical Analysis**: Common statistical tests and utilities
* **Reproducibility**: Built-in experiment tracking and seed management
* **GPU Support**: Seamless integration with PyTorch for GPU computing

Installation
------------

.. code-block:: bash

   pip install scitex

Quick Start
-----------

.. code-block:: python

   import sys
   import matplotlib.pyplot as plt
   import scitex

   # Initialize experiment environment
   CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.gen.start(
       sys, plt,
       file=__file__,
       verbose=False
   )

   # Your scientific code here
   data = scitex.io.load("data.pkl")
   results = process_data(data)
   scitex.io.save(results, "results.pkl")

   # Clean up and finalize
   scitex.gen.close(CONFIG)

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   getting_started
   installation
   quickstart
   examples/index

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/modules
   api/scitex.gen
   api/scitex.io
   api/scitex.plt
   api/scitex.dsp
   api/scitex.stats
   api/scitex.ai

.. toctree::
   :maxdepth: 2
   :caption: Agent Documentation

   scitex_guidelines/README
   scitex_guidelines/agent_guidelines/00_why_use_scitex
   scitex_guidelines/agent_guidelines/01_quick_start
   scitex_guidelines/agent_guidelines/02_core_concepts
   scitex_guidelines/agent_guidelines/03_module_overview
   scitex_guidelines/agent_guidelines/04_common_workflows

.. toctree::
   :maxdepth: 1
   :caption: Development

   contributing
   changelog
   license

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`