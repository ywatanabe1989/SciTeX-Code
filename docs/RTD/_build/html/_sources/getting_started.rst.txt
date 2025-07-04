Getting Started with SciTeX
===========================

Welcome to SciTeX! This guide will help you get up and running quickly.

What is SciTeX?
--------------

SciTeX (Scientific tools from literature to LaTeX Manuscript) is a comprehensive Python package designed to streamline the entire scientific research workflow. It provides standardized tools for:

* **Data I/O**: Universal file operations for 20+ formats
* **Visualization**: Publication-ready plotting with automatic data export
* **Statistical Analysis**: Research-grade statistical tools
* **Machine Learning**: Integrated AI/ML toolkit with GenAI support
* **Signal Processing**: Advanced DSP tools for scientific data
* **Literature Management**: Scholar module with impact factor integration

Installation
-----------

Install SciTeX using pip:

.. code-block:: bash

   pip install scitex

Or install from source for development:

.. code-block:: bash

   git clone https://github.com/scitex/scitex.git
   cd scitex
   pip install -e .

First Steps
----------

1. **Start with the Master Index**

   Open the :doc:`examples/00_SCITEX_MASTER_INDEX` to get an overview of all available tutorials and choose your learning path.

2. **Essential First Tutorial**

   Begin with :doc:`examples/01_scitex_io` - the I/O module is fundamental to all SciTeX workflows.

3. **Quick Example**

   Here's a minimal example to get you started:

   .. code-block:: python

      import scitex as stx

      # Load data
      data = stx.io.load('./data.csv')

      # Create a plot
      fig, ax = stx.plt.subplots()
      ax.plot(data['x'], data['y'])
      ax.set_xlabel('X Label')
      ax.set_ylabel('Y Label')

      # Save with automatic data export
      stx.io.save(fig, './results/plot.png')

Key Concepts
-----------

**Unified I/O Interface**
   All file operations use the same ``load()`` and ``save()`` functions, with automatic format detection.

**Automatic Data Tracking**
   When you save plots, SciTeX automatically exports the underlying data to CSV for reproducibility.

**Configuration Management**
   Store your settings in YAML files and load them with ``load_configs()``.

**Cross-Library Support**
   SciTeX works seamlessly with NumPy, PyTorch, TensorFlow, and pandas data structures.

Next Steps
---------

Based on your needs, explore these learning paths:

**For Data Scientists**
   → :doc:`examples/11_scitex_stats` → :doc:`examples/14_scitex_plt` → :doc:`examples/15_scitex_pd`

**For ML Engineers**
   → :doc:`examples/16_scitex_ai` → :doc:`examples/17_scitex_nn` → :doc:`examples/18_scitex_torch`

**For Researchers**
   → :doc:`examples/16_scitex_scholar` → :doc:`examples/22_scitex_repro` → :doc:`examples/20_scitex_tex`

Getting Help
-----------

* **Documentation**: You're here! Browse the full documentation.
* **Examples**: Check the ``examples/`` directory for hands-on tutorials.
* **GitHub Issues**: Report bugs or request features on our GitHub page.
* **Community**: Join our discussions on GitHub.

Happy scientific computing with SciTeX! 🚀