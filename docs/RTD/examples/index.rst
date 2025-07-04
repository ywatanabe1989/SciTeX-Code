SciTeX Examples and Tutorials
=============================

Welcome to the SciTeX examples collection! This comprehensive guide provides hands-on tutorials and examples to help you master the SciTeX library.

.. note::
   All example notebooks are located in the ``examples/`` directory of the SciTeX repository.
   You can run them interactively in Jupyter or view them in the documentation.

Master Tutorial Index
--------------------

The master index notebook provides a comprehensive overview of all available tutorials:

.. toctree::
   :maxdepth: 1

   00_SCITEX_MASTER_INDEX

Quick Navigation
---------------

Choose your learning path based on your needs:

**Getting Started**
  * :doc:`01_scitex_io` - Universal file I/O (start here!)
  * :doc:`02_scitex_gen` - General utilities and environment management
  * :doc:`14_scitex_plt` - Data visualization basics

**By Domain**
  * **Data Scientists**: Start with I/O → Stats → Plotting → Pandas → AI/ML
  * **ML Engineers**: Start with I/O → AI → Neural Networks → PyTorch
  * **Researchers**: Start with Scholar → I/O → Stats → Plotting

Core Modules
-----------

Essential SciTeX functionality organized by module:

I/O and File Operations
~~~~~~~~~~~~~~~~~~~~~~~

.. toctree::
   :maxdepth: 1

   01_scitex_io
   05_scitex_path
   09_scitex_os

Utilities and Data Structures
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. toctree::
   :maxdepth: 1

   02_scitex_gen
   03_scitex_utils
   04_scitex_str
   06_scitex_context
   07_scitex_dict
   08_scitex_types

Scientific Computing
~~~~~~~~~~~~~~~~~~~

.. toctree::
   :maxdepth: 1

   10_scitex_parallel
   11_scitex_stats
   12_scitex_linalg
   13_scitex_dsp

Data Analysis and Visualization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. toctree::
   :maxdepth: 1

   14_scitex_plt
   15_scitex_pd

Machine Learning and AI
~~~~~~~~~~~~~~~~~~~~~~

.. toctree::
   :maxdepth: 1

   16_scitex_ai
   17_scitex_nn
   18_scitex_torch

Research Tools
~~~~~~~~~~~~~

.. toctree::
   :maxdepth: 1

   16_scitex_scholar
   19_scitex_db
   20_scitex_tex
   21_scitex_decorators
   22_scitex_repro
   23_scitex_web

Learning Paths
-------------

By Skill Level
~~~~~~~~~~~~~

**Beginner Path** 🟢
  1. :doc:`01_scitex_io` - File I/O basics
  2. :doc:`14_scitex_plt` - Basic plotting
  3. :doc:`11_scitex_stats` - Simple statistics
  4. :doc:`15_scitex_pd` - Data manipulation

**Intermediate Path** 🟡
  1. :doc:`02_scitex_gen` - Environment management
  2. :doc:`07_scitex_dict` - Advanced data structures
  3. :doc:`13_scitex_dsp` - Signal processing
  4. :doc:`21_scitex_decorators` - Code optimization

**Advanced Path** 🔴
  1. :doc:`16_scitex_ai` - AI/ML integration
  2. :doc:`17_scitex_nn` - Neural networks
  3. :doc:`10_scitex_parallel` - Parallel computing
  4. :doc:`22_scitex_repro` - Reproducible research

Common Patterns
--------------

Here's a typical SciTeX workflow:

.. code-block:: python

   import scitex as stx

   # Load configuration
   CONFIG = stx.io.load_configs()

   # Load data
   data = stx.io.load('./data/input.csv')

   # Process and visualize
   fig, ax = stx.plt.subplots()
   ax.plot(data['x'], data['y'])

   # Save with tracking
   stx.io.save(fig, './output/result.jpg', symlink_from_cwd=True)

Tips for Success
---------------

1. **Install SciTeX**: ``pip install -e /path/to/scitex``
2. **Start with I/O**: Master :doc:`01_scitex_io` first
3. **Run examples**: Each notebook has executable examples
4. **Check outputs**: Look for generated files and plots

Best Practices
~~~~~~~~~~~~~

* **Use relative paths**: Start with ``./`` for all file paths
* **Leverage symlinks**: Use ``symlink_from_cwd=True`` in save operations
* **Track data**: Use ``scitex.plt`` for automatic CSV export with plots
* **Configuration**: Store settings in ``./config/*.yaml``

Additional Resources
-------------------

* `SciTeX GitHub Repository <https://github.com/scitex/scitex>`_
* `API Documentation </api/modules.html>`_
* `Contributing Guide </contributing.html>`_

Getting Help
-----------

* **In notebooks**: Each tutorial has detailed explanations
* **Error handling**: Examples include fallback patterns
* **Bug reports**: Create at ``~/proj/scitex_repo/project_management/bug-reports/``

Ready to Start?
--------------

Open :doc:`01_scitex_io` and begin your SciTeX journey! 🚀

*Happy Scientific Computing with SciTeX!* 🎉