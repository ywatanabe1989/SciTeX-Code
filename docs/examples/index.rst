Examples & Tutorials
====================

SciTeX provides 44+ comprehensive Jupyter notebook examples covering all major modules and use cases. These examples demonstrate practical applications and best practices for scientific computing workflows.

.. note::
   All example notebooks are available in the `examples/ directory <https://github.com/ywatanabe1989/SciTeX-Code/tree/develop/examples>`_ 
   of the GitHub repository and can be run interactively.

Core Module Examples
--------------------

**Getting Started**

* :doc:`../examples/01_getting_started_with_scitex` - Basic SciTeX workflow and setup
* :doc:`../examples/scitex_quickstart` - Quick start guide with common operations

**I/O Operations** 

* :doc:`../examples/comprehensive_scitex_io` - Complete I/O operations guide
* :doc:`../examples/02_scitex_io_advanced` - Advanced file format handling
* :doc:`../examples/15_scitex_io_operations` - Specialized I/O utilities

**Plotting & Visualization**

* :doc:`../examples/comprehensive_scitex_plt` - Complete plotting capabilities
* :doc:`../examples/03_scitex_plotting` - Basic plotting workflows
* :doc:`../examples/16_scitex_plt_plotting_utilities` - Advanced plotting features
* :doc:`../examples/scitex_plt_tutorial` - Step-by-step plotting tutorial

**Statistics & Analysis**

* :doc:`../examples/comprehensive_scitex_stats` - Statistical analysis toolkit
* :doc:`../examples/04_scitex_statistics` - Basic statistical operations
* :doc:`../examples/05_scitex_stats_analysis` - Advanced statistical methods
* :doc:`../examples/scitex_stats_tutorial` - Statistics workflow examples

**Signal Processing**

* :doc:`../examples/comprehensive_scitex_dsp` - Complete DSP capabilities
* :doc:`../examples/04_scitex_dsp` - Basic signal processing
* :doc:`../examples/04_scitex_dsp_signal_processing` - Advanced DSP techniques
* :doc:`../examples/05_scitex_dsp` - Real-world DSP applications

Advanced Module Examples
-------------------------

**Artificial Intelligence & Machine Learning**

* :doc:`../examples/comprehensive_scitex_ai` - Complete AI/ML toolkit
* :doc:`../examples/06_scitex_ai` - Basic machine learning workflows
* :doc:`../examples/06_scitex_ai_machine_learning` - Advanced ML techniques
* :doc:`../examples/06_scitex_ai_v02` - Updated AI examples

**Data Processing & Pandas Integration**

* :doc:`../examples/comprehensive_scitex_pd` - Complete pandas integration
* :doc:`../examples/08_scitex_pd_pandas_utilities` - Pandas utility functions
* :doc:`../examples/10_scitex_pd` - Advanced data manipulation

**Neural Networks**

* :doc:`../examples/07_scitex_nn` - Neural network implementations
* :doc:`../examples/08_scitex_torch` - PyTorch integration
* :doc:`../examples/14_scitex_nn_neural_networks` - Advanced neural architectures

**Development & Utilities**

* :doc:`../examples/comprehensive_scitex_decorators` - Function decorators
* :doc:`../examples/11_scitex_decorators` - Decorator examples
* :doc:`../examples/12_scitex_decorators` - Advanced decorator patterns

Specialized Examples
--------------------

**Database Operations**

* :doc:`../examples/14_scitex_db` - Database connectivity and operations
* :doc:`../examples/09_scitex_db_database_operations` - Advanced DB workflows

**Path & File Management**

* :doc:`../examples/10_scitex_path_management` - File system utilities
* :doc:`../examples/13_scitex_path` - Path manipulation examples

**String Processing**

* :doc:`../examples/09_scitex_str` - String processing utilities
* :doc:`../examples/12_scitex_str_string_utilities` - Advanced string operations

**Scientific Computing**

* :doc:`../examples/06_scitex_linalg` - Linear algebra operations
* :doc:`../examples/13_scitex_linalg_linear_algebra` - Advanced linear algebra
* :doc:`../examples/05_scitex_gen` - General utilities
* :doc:`../examples/07_scitex_gen_utilities` - Extended utility functions

**Research & Academia**

* :doc:`../examples/16_scitex_scholar` - Academic research tools
* :doc:`../examples/scholar/scholar_tutorial` - Scholar module tutorial
* :doc:`../examples/scholar/scholar_tutorial_new` - Updated scholar examples

**System & Performance**

* :doc:`../examples/07_scitex_os` - Operating system utilities
* :doc:`../examples/08_scitex_parallel` - Parallel processing
* :doc:`../examples/11_scitex_repro` - Reproducibility tools

**Web & Networking**

* :doc:`../examples/11_scitex_web` - Web scraping and APIs
* :doc:`../examples/09_scitex_context` - Context management

**Document & LaTeX**

* :doc:`../examples/10_scitex_tex` - LaTeX integration and document generation

Integration Examples
--------------------

**MCP (Model Context Protocol) Integration**

* :doc:`../examples/scitex_mcp_integration_tutorial` - MCP server integration guide

**Master Index & Navigation**

* :doc:`../examples/00_scitex_master_index` - Complete example overview and navigation

Running the Examples
--------------------

All examples can be run in several ways:

**Local Jupyter Environment:**

.. code-block:: bash

   # Clone the repository
   git clone https://github.com/ywatanabe1989/SciTeX-Code.git
   cd SciTeX-Code
   
   # Install dependencies
   pip install -r requirements.txt
   pip install -e .
   
   # Launch Jupyter
   jupyter notebook examples/

**Google Colab:**

Most examples include Colab-compatible installation cells:

.. code-block:: python

   # First cell in notebook
   !pip install scitex
   import scitex

**Binder (Interactive Online):**

Click the Binder badge in any notebook to run it online without installation.

Legacy Examples
---------------

Historical examples and alternative implementations are preserved in:

* `examples/legacy_notebooks/ <https://github.com/ywatanabe1989/SciTeX-Code/tree/develop/examples/legacy_notebooks>`_ - Previous notebook versions
* `examples/scitex_examples_legacy/ <https://github.com/ywatanabe1989/SciTeX-Code/tree/develop/examples/scitex_examples_legacy>`_ - Python script examples

These provide additional reference implementations and migration guides.

Contributing Examples
---------------------

We welcome contributions of new examples! Please see our `Contributing Guide <../contributing.html>`_ 
for guidelines on creating high-quality example notebooks.

**Example Requirements:**

* Clear documentation and comments
* Reproducible results with seed setting
* Error handling and graceful degradation
* Performance considerations noted
* Real-world applicability demonstrated