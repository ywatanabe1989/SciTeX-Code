#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-29 04:31:43 (ywatanabe)"
# File: ./scitex_repo/src/scitex/db/_SQLite3Mixins/_QueryMixin.py

THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/db/_SQLite3Mixins/_QueryMixin.py"

import sqlite3
from typing import List, Tuple

import pandas as pd
from .._BaseMixins._BaseQueryMixin import _BaseQueryMixin


class _QueryMixin:
    """Query execution functionality"""

    def _sanitize_parameters(self, parameters):
        """Convert pandas Timestamp objects to strings"""
        if isinstance(parameters, (list, tuple)):
            return [str(p) if isinstance(p, pd.Timestamp) else p for p in parameters]
        return parameters

    def execute(self, query: str, parameters: Tuple = ()) -> None:
        if not self.cursor:
            raise ConnectionError("Database not connected")

        if any(
            keyword in query.upper()
            for keyword in ["INSERT", "UPDATE", "DELETE", "DROP", "CREATE", "ALTER"]
        ):
            self._check_writable()

        try:
            parameters = self._sanitize_parameters(parameters)
            self.cursor.execute(query, parameters)
            self.conn.commit()
            return self.cursor
        except sqlite3.Error as err:
            raise sqlite3.Error(f"Query execution failed: {err}")

    def executemany(self, query: str, parameters: List[Tuple]) -> None:
        if not self.cursor:
            raise ConnectionError("Database not connected")

        if any(
            keyword in query.upper()
            for keyword in ["INSERT", "UPDATE", "DELETE", "DROP", "CREATE", "ALTER"]
        ):
            self._check_writable()

        try:
            parameters = [self._sanitize_parameters(p) for p in parameters]
            self.cursor.executemany(query, parameters)
            self.conn.commit()
        except sqlite3.Error as err:
            raise sqlite3.Error(f"Batch query execution failed: {err}")

    def executescript(self, script: str) -> None:
        if not self.cursor:
            raise ConnectionError("Database not connected")

        if any(
            keyword in script.upper()
            for keyword in [
                "INSERT",
                "UPDATE",
                "DELETE",
                "DROP",
                "CREATE",
                "ALTER",
            ]
        ):
            self._check_writable()

        try:
            self.cursor.executescript(script)
            self.conn.commit()
        except sqlite3.Error as err:
            raise sqlite3.Error(f"Script execution failed: {err}")


# EOF
