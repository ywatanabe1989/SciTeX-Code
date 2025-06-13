Module Overview
===============

MNGS is organized into specialized modules, each focusing on a specific domain of scientific computing.

Core Modules
------------

.. toctree::
   :maxdepth: 2

   gen
   io
   plt
   dsp
   stats
   pd

Machine Learning Modules
------------------------

.. toctree::
   :maxdepth: 2

   ai
   nn

Utility Modules
---------------

.. toctree::
   :maxdepth: 2

   db
   path
   str
   dict
   decorators

Module Categories
-----------------

Data I/O and Management
~~~~~~~~~~~~~~~~~~~~~~~

- **mngs.io**: File I/O operations with automatic format detection
- **mngs.path**: Advanced path manipulation utilities
- **mngs.db**: Database operations (SQLite3, PostgreSQL)

Visualization
~~~~~~~~~~~~~

- **mngs.plt**: Enhanced matplotlib wrapper with data tracking
- **mngs.plt.color**: Color management and palettes

Signal Processing
~~~~~~~~~~~~~~~~~

- **mngs.dsp**: Digital signal processing tools
- **mngs.dsp.filt**: Filtering operations
- **mngs.nn**: Neural network layers for signal processing

Data Analysis
~~~~~~~~~~~~~

- **mngs.stats**: Statistical analysis and tests
- **mngs.pd**: Pandas DataFrame utilities
- **mngs.ai**: Machine learning utilities

System Utilities
~~~~~~~~~~~~~~~~

- **mngs.gen**: General utilities and session management
- **mngs.decorators**: Function decorators
- **mngs.str**: String manipulation utilities
- **mngs.dict**: Dictionary utilities