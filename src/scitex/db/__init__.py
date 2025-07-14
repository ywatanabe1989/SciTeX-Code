#!/usr/bin/env python3
"""Database operations module for scitex."""

from ._postgresql._PostgreSQL import PostgreSQL
from ._sqlite3._SQLite3 import SQLite3
from ._delete_duplicates import delete_duplicates
from ._inspect import inspect

__all__ = [
    "PostgreSQL",
    "SQLite3", 
    "delete_duplicates",
    "inspect",
]

# Clean up namespace - remove private modules from public access
def _cleanup_namespace():
    import sys
    current_module = sys.modules[__name__]
    names_to_remove = []
    for name in list(vars(current_module).keys()):
        if name.startswith('_') and not name.startswith('__') and name not in ['_cleanup_namespace']:
            names_to_remove.append(name)
    for name in names_to_remove:
        delattr(current_module, name)

_cleanup_namespace()
del _cleanup_namespace