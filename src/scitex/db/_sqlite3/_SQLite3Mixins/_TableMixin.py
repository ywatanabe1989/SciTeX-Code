#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-11 05:47:57 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/db/_sqlite3/_SQLite3Mixins/_TableMixin.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/db/_sqlite3/_SQLite3Mixins/_TableMixin.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

# Time-stamp: "2024-11-25 01:38:47 (ywatanabe)"

THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/db/_SQLite3Mixins/_TableMixin.py"

# Time-stamp: "2024-11-11 19:13:19 (ywatanabe)"

import sqlite3
from typing import Any, Dict, List, Union

import pandas as pd

from ..._BaseMixins._BaseTableMixin import _BaseTableMixin


class _TableMixin:
    """Table management functionality"""

    def create_table(
        self,
        table_name: str,
        columns: Dict[str, str],
        foreign_keys: List[Dict[str, str]] = None,
        if_not_exists: bool = True,
    ) -> None:
        with self.transaction():
            try:
                exists_clause = "IF NOT EXISTS " if if_not_exists else ""
                column_defs = []

                for col_name, col_type in columns.items():
                    column_defs.append(f"{col_name} {col_type}")
                    if "BLOB" in col_type.upper():
                        column_defs.extend(
                            [
                                f"{col_name}_dtype TEXT DEFAULT 'unknown'",
                                f"{col_name}_shape TEXT DEFAULT 'unknown'",
                                f"{col_name}_is_compressed BOOLEAN DEFAULT FALSE",
                                f"{col_name}_hash TEXT DEFAULT NULL",
                            ]
                        )

                if foreign_keys:
                    for fk in foreign_keys:
                        column_defs.append(
                            f"FOREIGN KEY ({fk['tgt_column']}) REFERENCES {fk['src_table']}({fk['src_column']})"
                        )

                query = f"CREATE TABLE {exists_clause}{table_name} ({', '.join(column_defs)})"
                self.execute(query)

            except sqlite3.Error as err:
                raise ValueError(f"Failed to create table {table_name}: {err}")

    def drop_table(self, table_name: str, if_exists: bool = True) -> None:
        with self.transaction():
            try:
                exists_clause = "IF EXISTS " if if_exists else ""
                query = f"DROP TABLE {exists_clause}{table_name}"
                self.execute(query)
            except sqlite3.Error as err:
                raise ValueError(f"Failed to drop table: {err}")

    def rename_table(self, old_name: str, new_name: str) -> None:
        with self.transaction():
            try:
                query = f"ALTER TABLE {old_name} RENAME TO {new_name}"
                self.execute(query)
            except sqlite3.Error as err:
                raise ValueError(f"Failed to rename table: {err}")

    def add_columns(
        self,
        table_name: str,
        columns: Dict[str, str],
        default_values: Dict[str, Any] = None,
    ) -> None:
        with self.transaction():
            if default_values is None:
                default_values = {}

            for column_name, column_type in columns.items():
                self.add_column(
                    table_name,
                    column_name,
                    column_type,
                    default_values.get(column_name),
                )

    def add_column(
        self,
        table_name: str,
        column_name: str,
        column_type: str,
        default_value: Any = None,
    ) -> None:
        with self.transaction():
            schema = self.get_table_schema(table_name)
            if column_name in schema["name"].values:
                return

            try:
                query = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
                if default_value is not None:
                    query += f" DEFAULT {default_value}"
                self.execute(query)

                if "BLOB" in column_type.upper():
                    self.add_column(
                        table_name,
                        f"{column_name}_dtype",
                        "TEXT",
                        default_value="'unknown'",
                    )
                    self.add_column(
                        table_name,
                        f"{column_name}_shape",
                        "TEXT",
                        default_value="'unknown'",
                    )
                    self.add_column(
                        table_name,
                        f"{column_name}_is_compressed",
                        "BOOLEAN",
                        default_value="FALSE",
                    )
                    self.add_column(
                        table_name,
                        f"{column_name}_hash",
                        "TEXT",
                        default_value="NULL",
                    )

            except sqlite3.OperationalError as err:
                raise ValueError(f"Failed to add column: {err}")

    def drop_columns(
        self,
        table_name: str,
        columns: Union[str, List[str]],
        if_exists: bool = True,
    ) -> None:
        """
        DEPRECATED: Use the new drop_columns method from _DropMixin for better compatibility.
        This method will be removed in a future version.
        """
        import warnings
        warnings.warn(
            "TableMixin.drop_columns is deprecated. Use the enhanced drop_columns method "
            "from DropMixin which handles SQLite version compatibility automatically.",
            DeprecationWarning,
            stacklevel=2
        )
        
        # Delegate to the new implementation if available
        # Check all classes in MRO for the enhanced drop_columns method
        for cls in self.__class__.__mro__:
            if (hasattr(cls, 'drop_columns') and 
                hasattr(cls, '_supports_native_drop_column') and 
                cls.__name__ == '_DropMixin'):
                # Call DropMixin's drop_columns directly
                cls.drop_columns(self, table_name, columns, if_exists)
                return
            
        # Fallback to original implementation for compatibility
        with self.transaction():
            if isinstance(columns, str):
                columns = [columns]
            schema = self.get_table_schema(table_name)
            existing_columns = schema["name"].values
            columns_to_drop = (
                [col for col in columns if col in existing_columns]
                if if_exists
                else columns
            )

            if not columns_to_drop:
                return

            # Drop multiple columns in a single ALTER TABLE statement
            drop_clause = ", ".join(
                f"DROP COLUMN {col}" for col in columns_to_drop
            )
            self.execute(f"ALTER TABLE {table_name} {drop_clause}")

    def get_table_names(self) -> List[str]:
        self.ensure_connection()
        query = "SELECT name FROM sqlite_master WHERE type='table'"
        self.cursor.execute(query)
        return [table[0] for table in self.cursor.fetchall()]

    def get_table_schema(self, table_name: str) -> pd.DataFrame:
        self.ensure_connection()
        query = f"PRAGMA table_info({table_name})"
        self.cursor.execute(query)
        columns = ["cid", "name", "type", "notnull", "dflt_value", "pk"]
        return pd.DataFrame(self.cursor.fetchall(), columns=columns)

    def get_primary_key(self, table_name: str) -> str:
        schema = self.get_table_schema(table_name)
        pk_col = schema[schema["pk"] == 1]["name"].values
        return pk_col[0] if len(pk_col) > 0 else None

    def get_table_stats(self, table_name: str) -> Dict[str, int]:
        self.ensure_connection()
        try:
            pages = self.cursor.execute(f"PRAGMA page_count").fetchone()[0]
            page_size = self.cursor.execute(f"PRAGMA page_size").fetchone()[0]
            row_count = self.get_row_count(table_name)
            return {
                "pages": pages,
                "page_size": page_size,
                "total_size": pages * page_size,
                "row_count": row_count,
            }
        except sqlite3.Error as err:
            raise ValueError(f"Failed to get table size: {err}")

# EOF
