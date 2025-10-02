#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-16 12:49:57 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/db/__init__.py
# ----------------------------------------
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
"""Database operations module for scitex."""

from ._postgresql._PostgreSQL import PostgreSQL
from ._sqlite3._SQLite3 import SQLite3
from ._sqlite3._delete_duplicates import delete_sqlite3_duplicates
from ._delete_duplicates import delete_duplicates
from ._inspect import inspect
from ._check_health import check_health, batch_health_check

__all__ = [
    "PostgreSQL",
    "SQLite3",
    "delete_duplicates",
    "delete_sqlite3_duplicates",
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

# EOF
