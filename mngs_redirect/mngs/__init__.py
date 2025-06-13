#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEPRECATED: mngs has been renamed to scitex.

This package exists only for backward compatibility.
Please update your code to use scitex instead:

    pip install scitex

Then update your imports:
    from scitex import io, plt, gen  # etc.
"""

import warnings
import sys

# Show deprecation warning
warnings.warn(
    "\n" + "="*60 + "\n"
    "DEPRECATION WARNING:\n"
    "The 'mngs' package has been renamed to 'scitex'.\n"
    "\n"
    "Please update your installation:\n"
    "    pip uninstall mngs\n"
    "    pip install scitex\n"
    "\n"
    "Then update your imports:\n"
    "    # Old: import mngs\n"
    "    # New: import scitex\n"
    "="*60 + "\n",
    DeprecationWarning,
    stacklevel=2
)

# Try to import scitex and make mngs behave exactly like it
try:
    import scitex
    
    # Re-export everything from scitex
    from scitex import *
    
    # Make this module behave exactly like scitex
    # This allows all mngs.X.Y references to work
    _original_module = sys.modules[__name__]
    _scitex_module = sys.modules['scitex']
    
    # Copy all attributes from scitex to mngs
    for attr_name in dir(_scitex_module):
        if not attr_name.startswith('_'):
            setattr(_original_module, attr_name, getattr(_scitex_module, attr_name))
    
    # Also ensure submodules work (e.g., mngs.io, mngs.plt, etc.)
    for name, module in sys.modules.items():
        if name.startswith('scitex.'):
            # Create corresponding mngs.X module
            mngs_name = name.replace('scitex.', 'mngs.')
            sys.modules[mngs_name] = module
    
    # Set version to match scitex
    __version__ = scitex.__version__
    
except ImportError as e:
    raise ImportError(
        "\n" + "="*60 + "\n"
        "ERROR: The 'mngs' package requires 'scitex' to be installed.\n"
        "\n"
        "The 'mngs' package has been renamed to 'scitex'.\n"
        "Please install it with:\n"
        "    pip install scitex\n"
        "\n"
        "Then update your code to import scitex instead of mngs.\n"
        "="*60
    ) from e