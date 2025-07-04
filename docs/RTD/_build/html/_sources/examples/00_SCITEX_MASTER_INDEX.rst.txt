SciTeX Master Tutorial Index
============================

.. note::
   This page is generated from the Jupyter notebook `00_SCITEX_MASTER_INDEX.ipynb <https://github.com/scitex/scitex/blob/main/examples/00_SCITEX_MASTER_INDEX.ipynb>`_
   
   To run this notebook interactively:
   
   .. code-block:: bash
   
      cd examples/
      jupyter notebook 00_SCITEX_MASTER_INDEX.ipynb


**Welcome to the SciTeX Scientific Computing Library!**

| **Version:** 2.0 (Updated 2025-07-04)
| **Framework:** SciTeX - A Python utility package for scientific
  analysis
| **Total Notebooks:** 25+ comprehensive tutorials and examples

This master index provides organized access to all SciTeX tutorials and
examples. Choose your learning path based on your needs and experience
level.

--------------

🎯 Quick Navigation
-------------------

+-----------------+-----------------+-----------------+-----------------+
| **Getting       | **Core          | **Specialized** | **Research      |
| Started**       | Modules**       |                 | Tools**         |
+=================+=================+=================+=================+
| `Quick          | `I/O            | `Neural         | `Literature     |
| Start <#        | Operations <#io | Networks <#neur | Manageme        |
| quick-start>`__ | -operations>`__ | al-networks>`__ | nt <#literature |
|                 |                 |                 | -management>`__ |
+-----------------+-----------------+-----------------+-----------------+
| `Learning       | `Data           | `Signal         | `Reprodu        |
| Paths <#lea     | Visualiz        | Proc            | cibility <#repr |
| rning-paths>`__ | ation <#data-vi | essing <#signal | oducibility>`__ |
|                 | sualization>`__ | -processing>`__ |                 |
+-----------------+-----------------+-----------------+-----------------+
| `By Skill       | `Statistical    | `Linear         | `Web &          |
| Level <#by-     | Analy           | Algebra <#lin   | Databases <#we  |
| skill-level>`__ | sis <#statistic | ear-algebra>`__ | b-databases>`__ |
|                 | al-analysis>`__ |                 |                 |
+-----------------+-----------------+-----------------+-----------------+
|                 | `AI & Machine   | `System         | `LaTeX          |
|                 | Lear            | Ut              | Integ           |
|                 | ning <#ai-machi | ilities <#syste | ration <#latex- |
|                 | ne-learning>`__ | m-utilities>`__ | integration>`__ |
+-----------------+-----------------+-----------------+-----------------+

--------------

🌟 Quick Start
--------------

First-Time Users
~~~~~~~~~~~~~~~~

**⚡ Start Here →** `01_scitex_io.ipynb <01_scitex_io.ipynb>`__ -
Universal file I/O for 20+ formats - Configuration management with YAML
- Essential for any data workflow

Popular Starting Points
~~~~~~~~~~~~~~~~~~~~~~~

+---------------+-----------------------------+-------------------------+
| For…          | Start with…                 | Description             |
+===============+=============================+=========================+
| **Data        | `11_scitex_stats.ipynb      | Research-grade          |
| Scientists**  |  <11_scitex_stats.ipynb>`__ | statistical analysis    |
+---------------+-----------------------------+-------------------------+
| **ML          | `16_scitex_ai.ip            | Complete AI/ML toolkit  |
| Engineers**   | ynb <16_scitex_ai.ipynb>`__ | with GenAI              |
+---------------+-----------------------------+-------------------------+
| **            | `16_scitex_scholar.ipynb <  | Literature management   |
| Researchers** | 16_scitex_scholar.ipynb>`__ | with impact factors     |
+---------------+-----------------------------+-------------------------+
| **Vi          | `14_scitex_plt.ipy          | Publication-ready       |
| sualization** | nb <14_scitex_plt.ipynb>`__ | plotting                |
+---------------+-----------------------------+-------------------------+

📚 Core Modules
---------------

Essential SciTeX functionality organized by module number:

I/O Operations
~~~~~~~~~~~~~~

**📁** `01_scitex_io.ipynb <01_scitex_io.ipynb>`__ - *Most Essential* -
Universal load/save for CSV, JSON, HDF5, YAML, NPY, PKL, etc. -
Automatic format detection and path management - Configuration
management with ``load_configs()`` - Symlink creation and batch
operations

Core Utilities
~~~~~~~~~~~~~~

**🔧** `02_scitex_gen.ipynb <02_scitex_gen.ipynb>`__ - *General
Utilities* - Environment management with ``start()`` and ``close()`` -
Path utilities, system information, and helpers - Essential workflow
functions

**🛠️** `03_scitex_utils.ipynb <03_scitex_utils.ipynb>`__ - *Utility
Functions* - Grid operations and array utilities - HDF5 compression and
email notifications - Scientific computing helpers

Text & Path Management
~~~~~~~~~~~~~~~~~~~~~~

**🔤** `04_scitex_str.ipynb <04_scitex_str.ipynb>`__ - *String
Processing* - Advanced text formatting and color output - LaTeX
rendering and scientific notation - API key masking and text cleaning

**📂** `05_scitex_path.ipynb <05_scitex_path.ipynb>`__ - *Path
Operations* - Cross-platform path handling - Smart path creation and
version management - Module path resolution

Data Structures
~~~~~~~~~~~~~~~

**🔄** `06_scitex_context.ipynb <06_scitex_context.ipynb>`__ - *Context
Management* - Output suppression and resource management - Context
decorators for clean workflows

**📖** `07_scitex_dict.ipynb <07_scitex_dict.ipynb>`__ - *Dictionary
Utilities* - DotDict for attribute-style access - Safe merging and key
manipulation - Listed dictionaries for complex data

**🏷️** `08_scitex_types.ipynb <08_scitex_types.ipynb>`__ - *Type System*
- ArrayLike and ColorLike definitions - Cross-library type validation -
Type checking utilities

🔬 Scientific Computing
-----------------------

System & Parallel Computing
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**💻** `09_scitex_os.ipynb <09_scitex_os.ipynb>`__ - *OS Operations* -
Safe file movement with ``mv()`` - System-level operations

**⚡** `10_scitex_parallel.ipynb <10_scitex_parallel.ipynb>`__ -
*Parallel Processing* - Thread-based parallel execution - Performance
optimization for scientific computing

Analysis & Visualization
~~~~~~~~~~~~~~~~~~~~~~~~

**📊** `11_scitex_stats.ipynb <11_scitex_stats.ipynb>`__ - *Statistical
Analysis* - Hypothesis testing with multiple corrections - Correlation
analysis and bootstrap methods - Publication-ready statistical reporting

**🔢** `12_scitex_linalg.ipynb <12_scitex_linalg.ipynb>`__ - *Linear
Algebra* - Distance calculations and geometric operations -
Multi-framework support (NumPy, PyTorch, TensorFlow)

**🌊** `13_scitex_dsp.ipynb <13_scitex_dsp.ipynb>`__ - *Signal
Processing* - Time-frequency analysis and filtering - Spectral analysis
and wavelets - Biomedical signal processing

Data Visualization
~~~~~~~~~~~~~~~~~~

**📈** `14_scitex_plt.ipynb <14_scitex_plt.ipynb>`__ - *Plotting &
Visualization* - Enhanced matplotlib with automatic data export -
Publication-ready styling and themes - Multi-panel figures and color
management

Data Processing
~~~~~~~~~~~~~~~

**🐼** `15_scitex_pd.ipynb <15_scitex_pd.ipynb>`__ - *Pandas
Integration* - Enhanced DataFrame operations - Statistical summaries and
transformations - Matrix conversions and data reshaping

🤖 AI & Machine Learning
------------------------

.. _ai-machine-learning-1:

AI & Machine Learning
~~~~~~~~~~~~~~~~~~~~~

**🎯** `16_scitex_ai.ipynb <16_scitex_ai.ipynb>`__ - *Complete AI
Toolkit* - Generative AI integration (OpenAI, Anthropic, Google, Groq) -
Classification with comprehensive reporting - Clustering and
dimensionality reduction - Early stopping and training utilities

Neural Networks
~~~~~~~~~~~~~~~

**🧠** `17_scitex_nn.ipynb <17_scitex_nn.ipynb>`__ - *Neural Network
Layers* - Custom layers for scientific computing - Signal processing
layers (Hilbert, Wavelet, PSD) - Specialized architectures (BNet,
ResNet1D)

PyTorch Integration
~~~~~~~~~~~~~~~~~~~

**🔥** `18_scitex_torch.ipynb <18_scitex_torch.ipynb>`__ - *PyTorch
Utilities* - Tensor operations and type conversions - NaN-aware
functions - GPU acceleration utilities

📚 Research Tools
-----------------

Literature Management
~~~~~~~~~~~~~~~~~~~~~

**📖** `16_scitex_scholar.ipynb <16_scitex_scholar.ipynb>`__ - *Scholar
Module* - Literature search with impact factor integration - Semantic
Scholar and PubMed integration - PDF downloads and bibliography
management - BibTeX generation with enriched metadata

Database Operations
~~~~~~~~~~~~~~~~~~~

**🗄️** `19_scitex_db.ipynb <19_scitex_db.ipynb>`__ - *Database
Integration* - PostgreSQL and SQLite support - SQL operations with
pandas integration - Data persistence workflows

Documentation & LaTeX
~~~~~~~~~~~~~~~~~~~~~

**📝** `20_scitex_tex.ipynb <20_scitex_tex.ipynb>`__ - *LaTeX
Integration* - LaTeX rendering and preview - Mathematical notation
support - Document generation utilities

Development Tools
~~~~~~~~~~~~~~~~~

**🎭** `21_scitex_decorators.ipynb <21_scitex_decorators.ipynb>`__ -
*Function Decorators* - Type conversion decorators (@numpy_fn,
@torch_fn) - Performance optimization (@cache_mem, @batch_fn) - Error
handling and deprecation

Reproducibility
~~~~~~~~~~~~~~~

**🔄** `22_scitex_repro.ipynb <22_scitex_repro.ipynb>`__ - *Reproducible
Research* - Seed management and ID generation - Timestamp utilities -
Reproducible workflows

Web Integration
~~~~~~~~~~~~~~~

**🌐** `23_scitex_web.ipynb <23_scitex_web.ipynb>`__ - *Web Utilities* -
PubMed search integration - URL summarization - Web data collection

🎓 Learning Paths
-----------------

By Skill Level
~~~~~~~~~~~~~~

🟢 **Beginner Path**
^^^^^^^^^^^^^^^^^^^^

1. `01_scitex_io.ipynb <01_scitex_io.ipynb>`__ - File I/O basics
2. `14_scitex_plt.ipynb <14_scitex_plt.ipynb>`__ - Basic plotting
3. `11_scitex_stats.ipynb <11_scitex_stats.ipynb>`__ - Simple statistics
4. `15_scitex_pd.ipynb <15_scitex_pd.ipynb>`__ - Data manipulation

🟡 **Intermediate Path**
^^^^^^^^^^^^^^^^^^^^^^^^

1. `02_scitex_gen.ipynb <02_scitex_gen.ipynb>`__ - Environment
   management
2. `07_scitex_dict.ipynb <07_scitex_dict.ipynb>`__ - Advanced data
   structures
3. `13_scitex_dsp.ipynb <13_scitex_dsp.ipynb>`__ - Signal processing
4. `21_scitex_decorators.ipynb <21_scitex_decorators.ipynb>`__ - Code
   optimization

🔴 **Advanced Path**
^^^^^^^^^^^^^^^^^^^^

1. `16_scitex_ai.ipynb <16_scitex_ai.ipynb>`__ - AI/ML integration
2. `17_scitex_nn.ipynb <17_scitex_nn.ipynb>`__ - Neural networks
3. `10_scitex_parallel.ipynb <10_scitex_parallel.ipynb>`__ - Parallel
   computing
4. `22_scitex_repro.ipynb <22_scitex_repro.ipynb>`__ - Reproducible
   research

By Domain
~~~~~~~~~

📊 **For Data Scientists**
^^^^^^^^^^^^^^^^^^^^^^^^^^

→ 01 (I/O) → 11 (Stats) → 14 (Plotting) → 15 (Pandas) → 16 (AI/ML)

🤖 **For ML Engineers**
^^^^^^^^^^^^^^^^^^^^^^^

→ 01 (I/O) → 16 (AI) → 17 (NN) → 18 (PyTorch) → 21 (Decorators)

🔬 **For Researchers**
^^^^^^^^^^^^^^^^^^^^^^

→ 16_scholar → 01 (I/O) → 11 (Stats) → 14 (Plotting) → 22
(Reproducibility)

🧮 **For Scientific Computing**
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

→ 01 (I/O) → 12 (LinAlg) → 13 (DSP) → 10 (Parallel) → 03 (Utils)

📋 Module Reference
-------------------

Core Infrastructure
~~~~~~~~~~~~~~~~~~~

-  **scitex.io** → `01_scitex_io.ipynb <01_scitex_io.ipynb>`__
-  **scitex.gen** → `02_scitex_gen.ipynb <02_scitex_gen.ipynb>`__
-  **scitex.utils** → `03_scitex_utils.ipynb <03_scitex_utils.ipynb>`__
-  **scitex.str** → `04_scitex_str.ipynb <04_scitex_str.ipynb>`__
-  **scitex.path** → `05_scitex_path.ipynb <05_scitex_path.ipynb>`__

Data Structures
~~~~~~~~~~~~~~~

-  **scitex.context** →
   `06_scitex_context.ipynb <06_scitex_context.ipynb>`__
-  **scitex.dict** → `07_scitex_dict.ipynb <07_scitex_dict.ipynb>`__
-  **scitex.types** → `08_scitex_types.ipynb <08_scitex_types.ipynb>`__

Computing & Analysis
~~~~~~~~~~~~~~~~~~~~

-  **scitex.os** → `09_scitex_os.ipynb <09_scitex_os.ipynb>`__
-  **scitex.parallel** →
   `10_scitex_parallel.ipynb <10_scitex_parallel.ipynb>`__
-  **scitex.stats** → `11_scitex_stats.ipynb <11_scitex_stats.ipynb>`__
-  **scitex.linalg** →
   `12_scitex_linalg.ipynb <12_scitex_linalg.ipynb>`__
-  **scitex.dsp** → `13_scitex_dsp.ipynb <13_scitex_dsp.ipynb>`__

Visualization & Data
~~~~~~~~~~~~~~~~~~~~

-  **scitex.plt** → `14_scitex_plt.ipynb <14_scitex_plt.ipynb>`__
-  **scitex.pd** → `15_scitex_pd.ipynb <15_scitex_pd.ipynb>`__

AI & Neural Networks
~~~~~~~~~~~~~~~~~~~~

-  **scitex.ai** → `16_scitex_ai.ipynb <16_scitex_ai.ipynb>`__
-  **scitex.nn** → `17_scitex_nn.ipynb <17_scitex_nn.ipynb>`__
-  **scitex.torch** → `18_scitex_torch.ipynb <18_scitex_torch.ipynb>`__

Research Tools
~~~~~~~~~~~~~~

-  **scitex.scholar** →
   `16_scitex_scholar.ipynb <16_scitex_scholar.ipynb>`__
-  **scitex.db** → `19_scitex_db.ipynb <19_scitex_db.ipynb>`__
-  **scitex.tex** → `20_scitex_tex.ipynb <20_scitex_tex.ipynb>`__
-  **scitex.decorators** →
   `21_scitex_decorators.ipynb <21_scitex_decorators.ipynb>`__
-  **scitex.repro** → `22_scitex_repro.ipynb <22_scitex_repro.ipynb>`__
-  **scitex.web** → `23_scitex_web.ipynb <23_scitex_web.ipynb>`__

💡 Tips for Success
-------------------

Getting Started
~~~~~~~~~~~~~~~

1. **Install SciTeX**: ``pip install -e /path/to/scitex``
2. **Start with I/O**: Master
   `01_scitex_io.ipynb <01_scitex_io.ipynb>`__ first
3. **Run examples**: Each notebook has executable examples
4. **Check outputs**: Look for generated files and plots

Best Practices
~~~~~~~~~~~~~~

-  **Use relative paths**: Start with ``./`` for all file paths
-  **Leverage symlinks**: Use ``symlink_from_cwd=True`` in save
   operations
-  **Track data**: Use ``scitex.plt`` for automatic CSV export with
   plots
-  **Configuration**: Store settings in ``./config/*.yaml``

Common Patterns
~~~~~~~~~~~~~~~

.. code:: python

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

Getting Help
~~~~~~~~~~~~

-  **In notebooks**: Each tutorial has detailed explanations
-  **Error handling**: Examples include fallback patterns
-  **Bug reports**: Create at
   ``~/proj/scitex_repo/project_management/bug-reports/``

--------------

🚀 Ready to Start?
------------------

**Open** `01_scitex_io.ipynb <01_scitex_io.ipynb>`__ **and begin your
SciTeX journey!**

*Happy Scientific Computing with SciTeX!* 🎉
