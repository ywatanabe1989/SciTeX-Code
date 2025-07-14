#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-25 01:37:20 (ywatanabe)"
# File: ./scitex_repo/src/scitex/db/_SQLite3Mixins/_MaintenanceMixin.py

THIS_FILE = (
    "/home/ywatanabe/proj/scitex_repo/src/scitex/db/_SQLite3Mixins/_MaintenanceMixin.py"
)

import contextlib
import os
import sqlite3
from typing import Callable
from typing import ContextManager, Dict, List, Optional
import pandas as pd

from ..._BaseMixins._BaseMaintenanceMixin import _BaseMaintenanceMixin


class _MaintenanceMixin:
    """Database maintenance functionality"""

    @contextlib.contextmanager
    def maintenance_lock(self) -> ContextManager[None]:
        if not self._maintenance_lock.acquire(timeout=300):
            raise TimeoutError("Could not acquire maintenance lock")
        try:
            yield
        finally:
            self._maintenance_lock.release()

    def backup(
        self,
        backup_path: str,
        pages: int = -1,
        progress: Optional[Callable[[sqlite3.Connection, int, int], None]] = None,
    ) -> None:
        with self.maintenance_lock():
            try:

                def _progress(
                    status: sqlite3.Connection, remaining: int, total: int
                ) -> None:
                    if progress:
                        progress(total - remaining, total)

                backup_conn = sqlite3.connect(backup_path)
                with backup_conn:
                    self.conn.backup(backup_conn, pages=pages, progress=_progress)
                backup_conn.close()
            except (sqlite3.Error, Exception) as err:
                raise ValueError(f"Failed to create backup: {err}")

    def vacuum(self, into: Optional[str] = None) -> None:
        with self.maintenance_lock():
            try:
                if into:
                    self.execute(f"VACUUM INTO '{into}'")
                else:
                    self.execute("VACUUM")
            except sqlite3.Error as err:
                raise ValueError(f"Vacuum operation failed: {err}")

    def optimize(self, analyze: bool = True) -> None:
        with self.maintenance_lock():
            try:
                self.execute("PRAGMA optimize")
                self.vacuum()
                if analyze:
                    self.execute("ANALYZE")
            except sqlite3.Error as err:
                raise ValueError(f"Failed to optimize database: {err}")

    def get_summaries(
        self,
        table_names: Optional[List[str]] = None,
        verbose: bool = True,
        limit: int = 5,
    ) -> Dict[str, pd.DataFrame]:
        if table_names is None:
            table_names = self.get_table_names()
        if isinstance(table_names, str):
            table_names = [table_names]

        sample_tables = {}
        for table_name in table_names:
            columns = self.get_table_schema(table_name)
            table_sample = self.get_rows(table_name=table_name, limit=limit)

            for column in table_sample.columns:
                if table_sample[column].dtype == object:
                    try:
                        pd.to_datetime(table_sample[column])
                        continue
                    except:
                        pass

                    if table_sample[column].apply(lambda x: isinstance(x, str)).all():
                        continue

            sample_tables[table_name] = table_sample

        return sample_tables

    def fix_corruption(self) -> bool:
        """Attempts to fix database corruption"""
        with self.maintenance_lock():
            try:
                # Integrity check
                integrity_check = self.execute("PRAGMA integrity_check").fetchall()
                if integrity_check[0][0] == "ok":
                    return True

                # Backup good data
                temp_db = f"{self.db_path}_temp"
                self.execute("PRAGMA writable_schema = ON")
                self.execute(".dump", output_file=temp_db)

                # Recreate database
                self.close()
                os.remove(self.db_path)
                self.connect(self.db_path)

                # Restore from dump
                self.execute(f".read {temp_db}")
                os.remove(temp_db)
                return True

            except sqlite3.Error as error:
                raise ValueError(f"Failed to fix corruption: {error}")

    def fix_journal(self) -> bool:
        """Removes stale journal files and resets journal mode"""
        with self.maintenance_lock():
            try:
                self.close()

                # Remove journal files
                journal_file = f"{self.db_path}-journal"
                wal_file = f"{self.db_path}-wal"
                shm_file = f"{self.db_path}-shm"

                for file in [journal_file, wal_file, shm_file]:
                    if os.path.exists(file):
                        os.remove(file)

                # Reconnect and reset journal mode
                self.connect(self.db_path)
                self.execute("PRAGMA journal_mode = DELETE")
                self.execute("PRAGMA synchronous = NORMAL")
                return True

            except (sqlite3.Error, OSError) as error:
                raise ValueError(f"Failed to fix journal: {error}")

    def fix_indexes(self) -> bool:
        """Rebuilds all indexes"""
        with self.maintenance_lock():
            try:
                # Get all indexes
                indexes = self.execute(
                    "SELECT name, tbl_name, sql FROM sqlite_master WHERE type='index'"
                ).fetchall()

                # Drop and recreate each index
                for name, table, sql in indexes:
                    if sql:  # Skip internal indexes
                        self.execute(f"DROP INDEX IF EXISTS {name}")
                        self.execute(sql)

                return True

            except sqlite3.Error as error:
                raise ValueError(f"Failed to fix indexes: {error}")


# EOF
