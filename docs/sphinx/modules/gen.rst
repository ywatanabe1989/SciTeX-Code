scitex.gen - General Utilities Module
===================================

The ``scitex.gen`` module provides core utilities for environment management, session handling, and general-purpose helper functions.

For comprehensive documentation including examples and best practices, see:
``docs/scitex_guidelines/modules/gen/README.md``

Quick Overview
--------------

Key functions:

- ``start()``: Initialize a managed session with logging
- ``close()``: Clean up and save session logs  
- ``mk_spath()``: Create timestamped save directories
- ``title2path()``: Convert strings to valid paths
- ``run()``: Execute shell commands
- ``paste()``, ``copy()``: Clipboard operations

Example Usage
-------------

.. code-block:: python

    import scitex
    import sys
    import matplotlib.pyplot as plt
    
    # Start managed session
    CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.gen.start(sys, plt)
    
    # Your code here
    print("This is automatically logged")
    
    # Clean up
    scitex.gen.close(CONFIG)

API Reference
-------------

.. automodule:: scitex.gen
   :members:
   :undoc-members:
   :show-inheritance:
