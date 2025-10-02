#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-11 05:49:14 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/db/_sqlite3/_SQLite3Mixins/_QueryMixin.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import sqlite3
from typing import List, Tuple

import pandas as pd


class _QueryMixin:
    """Query execution functionality"""

    def _sanitize_parameters(self, parameters):
        """Convert pandas Timestamp objects to strings"""
        if isinstance(parameters, (list, tuple)):
            return [
                str(p) if isinstance(p, pd.Timestamp) else p
                for p in parameters
            ]
        return parameters

    def execute(self, query: str, parameters: Tuple = ()) -> None:
        self.ensure_connection()
        self._check_context_manager()

        if not self.cursor:
            raise ConnectionError("Database not connected")

        if any(
            keyword in query.upper()
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
            parameters = self._sanitize_parameters(parameters)
            self.cursor.execute(query, parameters)
            if self.autocommit:
                self.conn.commit()
                self.cursor.execute("PRAGMA wal_checkpoint(PASSIVE)")
                # self.cursor.execute("PRAGMA wal_checkpoint(FULL)")
            return self.cursor
        except sqlite3.Error as err:
            raise sqlite3.Error(f"Query execution failed: {err}")

    def executemany(self, query: str, parameters: List[Tuple]) -> None:
        self.ensure_connection()
        if not self.cursor:
            raise ConnectionError("Database not connected")

        if any(
            keyword in query.upper()
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
            parameters = [self._sanitize_parameters(p) for p in parameters]
            self.cursor.executemany(query, parameters)
            self.conn.commit()
        except sqlite3.Error as err:
            raise sqlite3.Error(f"Batch query execution failed: {err}")

    def executescript(self, script: str) -> None:
        self.ensure_connection()
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
