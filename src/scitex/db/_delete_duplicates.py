#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-12 12:00:00 (ywatanabe)"
# File: ./src/scitex/db/_delete_duplicates.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/db/_delete_duplicates.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Backward compatibility wrapper for delete_duplicates function.
The actual implementation has been moved to _sqlite3._delete_duplicates
as it is SQLite3-specific.
"""

from ..errors import warn_deprecated
from ._sqlite3._delete_duplicates import delete_sqlite3_duplicates

def delete_duplicates(*args, **kwargs):
    """
    Delete duplicate entries from an SQLite database table.
    
    .. deprecated:: 
        This function is deprecated as it's SQLite3-specific.
        Use scitex.db._sqlite3.delete_sqlite3_duplicates() instead.
    """
    warn_deprecated(
        old_function="scitex.db.delete_duplicates",
        new_function="scitex.db._sqlite3.delete_sqlite3_duplicates",
        version="3.0.0"
    )
    return delete_sqlite3_duplicates(*args, **kwargs)

# Export for backward compatibility
__all__ = ["delete_duplicates"]