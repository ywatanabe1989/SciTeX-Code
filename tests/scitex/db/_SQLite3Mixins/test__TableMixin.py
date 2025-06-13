#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 14:48:00 (ywatanabe)"
# File: ./tests/scitex/db/_SQLite3Mixins/test__TableMixin.py

"""
Functionality:
    * Tests table operations for SQLite3
    * Validates table creation, alteration, and deletion
    * Tests schema management
Input:
    * Test database and table schemas
Output:
    * Test results
Prerequisites:
    * pytest
    * sqlite3
"""

import pytest
import sqlite3
import tempfile
import os
from unittest.mock import Mock, patch


class TestTableMixin:
    """Test cases for _TableMixin"""
    
    def test_create_table_basic(self):
        """Test basic table creation"""
from scitex.db._SQLite3Mixins import _TableMixin
        
        mixin = _TableMixin()
        mixin.execute = Mock()
        
        schema = {
            "id": "INTEGER PRIMARY KEY",
            "name": "TEXT NOT NULL",
            "value": "INTEGER DEFAULT 0"
        }
        
        mixin.create_table("test_table", schema)
        
        # Verify SQL construction
        call_args = mixin.execute.call_args[0][0]
        assert "CREATE TABLE test_table" in call_args
        assert "id INTEGER PRIMARY KEY" in call_args
        assert "name TEXT NOT NULL" in call_args
        
    def test_create_table_if_not_exists(self):
        """Test conditional table creation"""
from scitex.db._SQLite3Mixins import _TableMixin
        
        mixin = _TableMixin()
        mixin.execute = Mock()
        
        schema = {"id": "INTEGER PRIMARY KEY"}
        mixin.create_table("test_table", schema, if_not_exists=True)
        
        call_args = mixin.execute.call_args[0][0]
        assert "CREATE TABLE IF NOT EXISTS" in call_args
        
    def test_drop_table(self):
        """Test table deletion"""
from scitex.db._SQLite3Mixins import _TableMixin
        
        mixin = _TableMixin()
        mixin.execute = Mock()
        
        mixin.drop_table("test_table")
        mixin.execute.assert_called_with("DROP TABLE test_table")
        
    def test_drop_table_if_exists(self):
        """Test conditional table deletion"""
from scitex.db._SQLite3Mixins import _TableMixin
        
        mixin = _TableMixin()
        mixin.execute = Mock()
        
        mixin.drop_table("test_table", if_exists=True)
        mixin.execute.assert_called_with("DROP TABLE IF EXISTS test_table")
        
    def test_table_exists(self):
        """Test checking if table exists"""
from scitex.db._SQLite3Mixins import _TableMixin
        
        mixin = _TableMixin()
        mock_cursor = Mock()
        
        # Table exists
        mock_cursor.fetchone.return_value = ("test_table",)
        mixin.execute = Mock(return_value=mock_cursor)
        assert mixin.table_exists("test_table") is True
        
        # Table doesn't exist
        mock_cursor.fetchone.return_value = None
        assert mixin.table_exists("nonexistent") is False
        
    def test_list_tables(self):
        """Test listing all tables"""
from scitex.db._SQLite3Mixins import _TableMixin
        
        mixin = _TableMixin()
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [
            ("table1",), ("table2",), ("table3",)
        ]
        mixin.execute = Mock(return_value=mock_cursor)
        
        tables = mixin.list_tables()
        assert len(tables) == 3
        assert "table1" in tables
        
    def test_get_table_schema(self):
        """Test retrieving table schema"""
from scitex.db._SQLite3Mixins import _TableMixin
        
        mixin = _TableMixin()
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [
            (0, "id", "INTEGER", 1, None, 1),
            (1, "name", "TEXT", 0, None, 0),
            (2, "value", "INTEGER", 0, "0", 0)
        ]
        mixin.execute = Mock(return_value=mock_cursor)
        
        schema = mixin.get_table_schema("test_table")
        assert len(schema) == 3
        assert schema[0]["name"] == "id"
        assert schema[0]["type"] == "INTEGER"
        assert schema[0]["primary_key"] == 1
        
    def test_rename_table(self):
        """Test table renaming"""
from scitex.db._SQLite3Mixins import _TableMixin
        
        mixin = _TableMixin()
        mixin.execute = Mock()
        
        mixin.rename_table("old_table", "new_table")
        mixin.execute.assert_called_with("ALTER TABLE old_table RENAME TO new_table")
        
    def test_add_column(self):
        """Test adding column to table"""
from scitex.db._SQLite3Mixins import _TableMixin
        
        mixin = _TableMixin()
        mixin.execute = Mock()
        
        mixin.add_column("test_table", "new_column", "TEXT DEFAULT ''")
        mixin.execute.assert_called_with(
            "ALTER TABLE test_table ADD COLUMN new_column TEXT DEFAULT ''"
        )
        
    def test_copy_table(self):
        """Test table copying"""
from scitex.db._SQLite3Mixins import _TableMixin
        
        mixin = _TableMixin()
        mixin.execute = Mock()
        
        # Copy structure and data
        mixin.copy_table("source_table", "dest_table", include_data=True)
        
        # Should execute CREATE TABLE and INSERT
        assert mixin.execute.call_count == 2
        create_call = mixin.execute.call_args_list[0][0][0]
        insert_call = mixin.execute.call_args_list[1][0][0]
        
        assert "CREATE TABLE dest_table AS SELECT" in create_call
        assert "INSERT INTO dest_table SELECT" in insert_call
        
    def test_truncate_table(self):
        """Test table truncation"""
from scitex.db._SQLite3Mixins import _TableMixin
        
        mixin = _TableMixin()
        mixin.execute = Mock()
        mixin.transaction = Mock(return_value=Mock(__enter__=Mock(), __exit__=Mock()))
        
        mixin.truncate_table("test_table")
        mixin.execute.assert_called_with("DELETE FROM test_table")


def main():
    """Run the tests"""
    pytest.main([__file__, "-v"])


if __name__ == "__main__":
    main()\n\n# --------------------------------------------------------------------------------\n# Start of Source Code from: /home/ywatanabe/proj/_scitex_repo/src/scitex/db/_SQLite3Mixins/_TableMixin.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-25 01:38:47 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/db/_SQLite3Mixins/_TableMixin.py
#
# THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/db/_SQLite3Mixins/_TableMixin.py"
#
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-11 19:13:19 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/db/_BaseSQLiteDB_modules/_TableMixin.py
#
# import sqlite3
# from typing import Any, Dict, List, Union
# import pandas as pd
# from .._BaseMixins._BaseTableMixin import _BaseTableMixin
#
# class _TableMixin:
#     """Table management functionality"""
#
#     def create_table(
#         self,
#         table_name: str,
#         columns: Dict[str, str],
#         foreign_keys: List[Dict[str, str]] = None,
#         if_not_exists: bool = True,
#     ) -> None:
#         with self.transaction():
#             try:
#                 exists_clause = "IF NOT EXISTS " if if_not_exists else ""
#                 column_defs = []
#
#                 for col_name, col_type in columns.items():
#                     column_defs.append(f"{col_name} {col_type}")
#                     if "BLOB" in col_type.upper():
#                         column_defs.extend([
#                             f"{col_name}_dtype TEXT DEFAULT 'unknown'",
#                             f"{col_name}_shape TEXT DEFAULT 'unknown'",
#                         ])
#
#                 if foreign_keys:
#                     for fk in foreign_keys:
#                         column_defs.append(
#                             f"FOREIGN KEY ({fk['tgt_column']}) REFERENCES {fk['src_table']}({fk['src_column']})"
#                         )
#
#                 query = f"CREATE TABLE {exists_clause}{table_name} ({', '.join(column_defs)})"
#                 self.execute(query)
#
#             except sqlite3.Error as err:
#                 raise ValueError(f"Failed to create table {table_name}: {err}")
#
#     def drop_table(self, table_name: str, if_exists: bool = True) -> None:
#         with self.transaction():
#             try:
#                 exists_clause = "IF EXISTS " if if_exists else ""
#                 query = f"DROP TABLE {exists_clause}{table_name}"
#                 self.execute(query)
#             except sqlite3.Error as err:
#                 raise ValueError(f"Failed to drop table: {err}")
#
#     def rename_table(self, old_name: str, new_name: str) -> None:
#         with self.transaction():
#             try:
#                 query = f"ALTER TABLE {old_name} RENAME TO {new_name}"
#                 self.execute(query)
#             except sqlite3.Error as err:
#                 raise ValueError(f"Failed to rename table: {err}")
#
#     def add_columns(
#         self,
#         table_name: str,
#         columns: Dict[str, str],
#         default_values: Dict[str, Any] = None,
#     ) -> None:
#         with self.transaction():
#             if default_values is None:
#                 default_values = {}
#
#             for column_name, column_type in columns.items():
#                 self.add_column(
#                     table_name,
#                     column_name,
#                     column_type,
#                     default_values.get(column_name),
#                 )
#
#     def add_column(
#         self,
#         table_name: str,
#         column_name: str,
#         column_type: str,
#         default_value: Any = None,
#     ) -> None:
#         with self.transaction():
#             schema = self.get_table_schema(table_name)
#             if column_name in schema["name"].values:
#                 return
#
#             try:
#                 query = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
#                 if default_value is not None:
#                     query += f" DEFAULT {default_value}"
#                 self.execute(query)
#
#                 if "BLOB" in column_type.upper():
#                     self.add_column(
#                         table_name,
#                         f"{column_name}_dtype",
#                         "TEXT",
#                         default_value="'unknown'",
#                     )
#                     self.add_column(
#                         table_name,
#                         f"{column_name}_shape",
#                         "TEXT",
#                         default_value="'unknown'",
#                     )
#
#             except sqlite3.OperationalError as err:
#                 raise ValueError(f"Failed to add column: {err}")
#
#     def drop_columns(
#         self,
#         table_name: str,
#         columns: Union[str, List[str]],
#         if_exists: bool = True,
#     ) -> None:
#         with self.transaction():
#             if isinstance(columns, str):
#                 columns = [columns]
#             schema = self.get_table_schema(table_name)
#             existing_columns = schema["name"].values
#             columns_to_drop = (
#                 [col for col in columns if col in existing_columns]
#                 if if_exists
#                 else columns
#             )
#
#             if not columns_to_drop:
#                 return
#
#             # Drop multiple columns in a single ALTER TABLE statement
#             drop_clause = ", ".join(f"DROP COLUMN {col}" for col in columns_to_drop)
#             self.execute(f"ALTER TABLE {table_name} {drop_clause}")
#
#     def get_table_names(self) -> List[str]:
#         query = "SELECT name FROM sqlite_master WHERE type='table'"
#         self.cursor.execute(query)
#         return [table[0] for table in self.cursor.fetchall()]
#
#     def get_table_schema(self, table_name: str) -> pd.DataFrame:
#         query = f"PRAGMA table_info({table_name})"
#         self.cursor.execute(query)
#         columns = ["cid", "name", "type", "notnull", "dflt_value", "pk"]
#         return pd.DataFrame(self.cursor.fetchall(), columns=columns)
#
#     def get_primary_key(self, table_name: str) -> str:
#         schema = self.get_table_schema(table_name)
#         pk_col = schema[schema["pk"] == 1]["name"].values
#         return pk_col[0] if len(pk_col) > 0 else None
#
#     def get_table_stats(self, table_name: str) -> Dict[str, int]:
#         try:
#             pages = self.cursor.execute(f"PRAGMA page_count").fetchone()[0]
#             page_size = self.cursor.execute(f"PRAGMA page_size").fetchone()[0]
#             row_count = self.get_row_count(table_name)
#             return {
#                 "pages": pages,
#                 "page_size": page_size,
#                 "total_size": pages * page_size,
#                 "row_count": row_count,
#             }
#         except sqlite3.Error as err:
#             raise ValueError(f"Failed to get table size: {err}")
#
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/db/_SQLite3Mixins/_TableMixin.py
# --------------------------------------------------------------------------------
