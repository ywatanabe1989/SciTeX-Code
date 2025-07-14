#!/usr/bin/env python3
"""
DEPRECATED: The 'reproduce' module has been renamed to 'repro'.

This module exists only for backward compatibility and will be removed in a
future version.
Please update your imports from:
    from scitex.reproduce import ...
to:
    from scitex.repro import ...
"""

import warnings

warnings.warn(
    "The 'reproduce' module is deprecated and has been renamed to 'repro'. "
    "Please update your imports to use 'scitex.repro' instead of "
    "'scitex.reproduce'. This compatibility layer will be removed in a "
    "future version.",
    DeprecationWarning,
    stacklevel=2
)

# Import everything from the new module for backward compatibility
from ..repro import *  # noqa: F403,F401,E402
