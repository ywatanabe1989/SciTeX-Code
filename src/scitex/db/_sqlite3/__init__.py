#!/usr/bin/env python3
"""SQLite3 database module."""

from ._SQLite3 import SQLite3
from ._delete_duplicates import delete_sqlite3_duplicates

__all__ = ["SQLite3", "delete_sqlite3_duplicates"]