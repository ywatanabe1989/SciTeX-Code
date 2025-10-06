#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-11 05:43:10 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/db/_sqlite3/_SQLite3Mixins/_ConnectionMixin.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

# Time-stamp: "2024-11-29 04:33:58 (ywatanabe)"

THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/db/_SQLite3Mixins/_ConnectionMixin.py"

"""
1. Functionality:
   - Manages SQLite database connections with thread-safe operations
   - Handles database journal files and transaction states
2. Input:
   - Database file path
3. Output:
   - Managed SQLite connection and cursor objects
4. Prerequisites:
   - sqlite3
   - threading
"""

import shutil
import sqlite3
import tempfile
import threading


class _ConnectionMixin:
    """Connection management functionality"""

    def __init__(self, db_path: str, use_temp_db: bool = False):
        self.lock = threading.Lock()
        self._maintenance_lock = threading.Lock()
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.temp_path = None  # Initialize temp_path attribute
        if db_path:
            self.connect(db_path, use_temp_db)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def _create_temp_copy(self, db_path: str) -> str:
        """Creates temporary copy of database."""
        temp_dir = tempfile.gettempdir()
        self.temp_path = os.path.join(
            temp_dir, f"temp_{os.path.basename(db_path)}"
        )
        shutil.copy2(db_path, self.temp_path)
        return self.temp_path

    def connect(self, db_path: str, use_temp_db: bool = False) -> None:
        if self.conn:
            self.close()

        path_to_connect = (
            self._create_temp_copy(db_path) if use_temp_db else db_path
        )

        self.conn = sqlite3.connect(path_to_connect, timeout=60.0)
        self.cursor = self.conn.cursor()

        with self.lock:
            # WAL mode settings
            self.cursor.execute("PRAGMA journal_mode = WAL")
            self.cursor.execute("PRAGMA synchronous = NORMAL")
            self.cursor.execute("PRAGMA busy_timeout = 300000")  # 5 minutes
            self.cursor.execute("PRAGMA mmap_size = 30000000000")
            self.cursor.execute("PRAGMA temp_store = MEMORY")
            self.cursor.execute("PRAGMA cache_size = -2000")
            self.cursor.execute(
                "PRAGMA wal_autocheckpoint = 1000"
            )  # Auto-checkpoint
            self.conn.commit()

    def close(self) -> None:
        if self.cursor:
            self.cursor.close()
        if self.conn:
            try:
                self.conn.rollback()
                self.conn.close()
            except sqlite3.Error:
                pass
        self.cursor = None
        self.conn = None

        if (
            hasattr(self, "temp_path")
            and self.temp_path
            and os.path.exists(self.temp_path)
        ):
            try:
                os.remove(self.temp_path)
                self.temp_path = None
            except OSError:
                pass

    def reconnect(self, use_temp_db: bool = False) -> None:
        if self.db_path:
            self.connect(self.db_path, use_temp_db)
        else:
            raise ValueError("No database path specified for reconnection")

    def ensure_connection(self):
        """
        Ensure connection when used in context manager (with statement).
        All methods that use `self.cursor` or `self.conn` should call this first.
        """
        if not self.cursor or not self.conn:
            self.reconnect()

# EOF
