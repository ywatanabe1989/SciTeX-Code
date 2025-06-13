#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 14:48:00 (ywatanabe)"
# File: ./tests/scitex/db/_SQLite3Mixins/test__BatchMixin.py

"""
Functionality:
    * Tests batch database operations for SQLite3
    * Validates batch inserts, updates, and replacements
    * Tests transaction safety and error handling
Input:
    * Test database and sample data
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
from unittest.mock import Mock, patch, MagicMock


class TestBatchMixin:
    """Test cases for _BatchMixin"""
    
    def setup_method(self):
        """Set up test database"""
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.db_path = self.temp_db.name
        self.conn = sqlite3.connect(self.db_path)
        
        # Create test table
        self.conn.execute("""
            CREATE TABLE test_table (
                id INTEGER PRIMARY KEY,
                name TEXT,
                value INTEGER
            )
        """)
        self.conn.commit()
        
    def teardown_method(self):
        """Clean up test database"""
        self.conn.close()
        os.unlink(self.db_path)
        
    def test_insert_many_basic(self):
        """Test basic batch insert operation"""
from scitex.db._SQLite3Mixins import _BatchMixin
        
        # Create mock instance
        mixin = _BatchMixin()
        mixin.execute = Mock(return_value=Mock(fetchone=Mock(return_value=None)))
        mixin.executemany = Mock()
        mixin.get_table_schema = Mock(return_value={"name": ["id", "name", "value"]})
        mixin.transaction = Mock(return_value=MagicMock())
        mixin.rollback = Mock()
        
        rows = [
            {"name": "test1", "value": 10},
            {"name": "test2", "value": 20}
        ]
        
        # Test insert_many
        mixin.insert_many("test_table", rows)
        assert mixin.executemany.called
        
    def test_update_many_basic(self):
        """Test batch update operation"""
from scitex.db._SQLite3Mixins import _BatchMixin
        
        mixin = _BatchMixin()
        mixin.execute = Mock()
        mixin.executemany = Mock()
        mixin.get_table_schema = Mock(return_value={"name": ["id", "name", "value"]})
        mixin.transaction = Mock(return_value=MagicMock())
        
        rows = [{"name": "updated", "value": 100}]
        
        # Test update_many
        mixin.update_many("test_table", rows, where="id=1")
        assert mixin.executemany.called
        
    def test_replace_many_basic(self):
        """Test batch replace operation"""
from scitex.db._SQLite3Mixins import _BatchMixin
        
        mixin = _BatchMixin()
        mixin.execute = Mock(return_value=Mock(fetchone=Mock(return_value=None)))
        mixin.executemany = Mock()
        mixin.get_table_schema = Mock(return_value={"name": ["id", "name", "value"]})
        mixin.transaction = Mock(return_value=MagicMock())
        
        rows = [{"id": 1, "name": "replaced", "value": 200}]
        
        # Test replace_many
        mixin.replace_many("test_table", rows)
        assert mixin.executemany.called
        
    def test_delete_where(self):
        """Test conditional delete operation"""
from scitex.db._SQLite3Mixins import _BatchMixin
        
        mixin = _BatchMixin()
        mixin.execute = Mock()
        mixin.transaction = Mock(return_value=MagicMock())
        
        # Test delete_where
        mixin.delete_where("test_table", "value > 50")
        mixin.execute.assert_called()
        
    def test_batch_size_validation(self):
        """Test batch size validation"""
from scitex.db._SQLite3Mixins import _BatchMixin
        
        mixin = _BatchMixin()
        mixin.transaction = Mock(return_value=MagicMock())
        
        with pytest.raises(ValueError):
            mixin._run_many("INSERT", "test_table", [], batch_size=-1)
            
    def test_empty_rows(self):
        """Test handling of empty row list"""
from scitex.db._SQLite3Mixins import _BatchMixin
        
        mixin = _BatchMixin()
        mixin.transaction = Mock(return_value=MagicMock())
        mixin.execute = Mock()
        
        # Should not raise error
        mixin.insert_many("test_table", [])
        

def main():
    """Run the tests"""
    pytest.main([__file__, "-v"])


if __name__ == "__main__":
    main()\n\n# --------------------------------------------------------------------------------\n# Start of Source Code from: /home/ywatanabe/proj/_scitex_repo/src/scitex/db/_SQLite3Mixins/_BatchMixin.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-29 04:36:14 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/db/_SQLite3Mixins/_BatchMixin.py
#
# THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/db/_SQLite3Mixins/_BatchMixin.py"
#
# """
# Functionality:
#     * Provides batch database operations for SQLite3
#     * Handles batch inserts, updates, replacements with transaction safety
#     * Supports foreign key inheritance and where clause filtering
#
# Input:
#     * Table name, row data as dictionaries, and operation parameters
#     * Support for batch size control and conditional operations
#
# Output:
#     * None, but executes database operations with transaction safety
#
# Prerequisites:
#     * SQLite3 database connection
#     * Table schema must exist
#     * Foreign key constraints must be enabled if using inherit_foreign
# """
#
# from typing import Any as _Any
# from typing import Dict, List, Optional
# from .._BaseMixins._BaseBatchMixin import _BaseBatchMixin
# import sqlite3
#
# class _BatchMixin:
#     """Batch operations functionality"""
#
#     def _run_many(
#         self,
#         sql_command,
#         table_name: str,
#         rows: List[Dict[str, _Any]],
#         batch_size: int = 1000,
#         inherit_foreign: bool = True,
#         where: Optional[str] = None,
#         columns: Optional[List[str]] = None,
#     ) -> None:
#         try:
#             if batch_size <= 0:
#                 raise ValueError("Batch size must be positive")
#
#             table_name = f'"{table_name.replace("`", "``")}"'
#
#             # Validate table exists and get schema
#             schema = self.get_table_schema(table_name)
#             table_columns = set(schema["name"])
#
#             # Replace the problematic code block with:
#             if columns:
#                 valid_columns = [
#                     col for col in columns
#                     if col in table_columns and col.isidentifier()
#                 ]
#             else:
#                 valid_columns = [
#                     col for col in rows[0].keys()
#                     if col in table_columns and col.isidentifier()
#                 ]
#
#             if not valid_columns:
#                 raise ValueError("No valid columns found")
#
#             if not table_name or not isinstance(table_name, str):
#                 raise ValueError("Invalid table name")
#             if not isinstance(rows, list):
#                 raise ValueError("Rows must be a list of dictionaries")
#             if rows and not all(isinstance(row, dict) for row in rows):
#                 raise ValueError("All rows must be dictionaries")
#
#             # Validate table exists
#             self.execute(f"SELECT 1 FROM {table_name} LIMIT 1")
#
#             assert sql_command.upper() in [
#                 "INSERT",
#                 "REPLACE",
#                 "INSERT OR REPLACE",
#                 "UPDATE",
#             ]
#
#             if not rows:
#                 return
#
#             if sql_command.upper() == "UPDATE":
#                 valid_columns = columns if columns else [col for col in rows[0].keys()]
#                 set_clause = ",".join([f"{col}=?" for col in valid_columns])
#                 where_clause = where if where else "1=1"
#
#                 # Modified query construction
#                 query = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}"
#                 params = []
#
#                 for row in rows:
#                     row_params = [row[col] for col in valid_columns]
#                     if where:
#                         # Add any parameters needed for WHERE clause
#                         row_params.extend([row[col] for col in where.split() if col in row])
#                     params.append(tuple(row_params))
#
#                 self.executemany(query, params)
#                 return
#
#             if where:
#                 filtered_rows = []
#                 for row in rows:
#                     try:
#                         test_query = f"SELECT 1 FROM (SELECT {','.join('? as ' + k for k in row.keys())}) WHERE {where}"
#                         values = tuple(row.values())
#                         result = self.execute(test_query, values).fetchone()
#                         if result:
#                             filtered_rows.append(row)
#                     except Exception as e:
#                         print(
#                             f"Warning: Where clause evaluation failed for row: {e}"
#                         )
#             rows = filtered_rows
#             schema = self.get_table_schema(table_name)
#             table_columns = set(schema["name"])
#             valid_columns = [col for col in rows[0].keys()]
#
#             if inherit_foreign:
#                 fk_query = f"PRAGMA foreign_key_list({table_name})"
#                 foreign_keys = self.execute(fk_query).fetchall()
#
#                 for row in rows:
#                     for fk in foreign_keys:
#                         ref_table, from_col, to_col = fk[2], fk[3], fk[4]
#                         if from_col not in row or row[from_col] is None:
#                             if to_col in row:
#                                 query = f"SELECT {from_col} FROM {ref_table} WHERE {to_col} = ?"
#                                 result = self.execute(
#                                     query, (row[to_col],)
#                                 ).fetchone()
#                                 if result:
#                                     row[from_col] = result[0]
#
#             columns = valid_columns
#             placeholders = ",".join(["?" for _ in columns])
#             query = f"{sql_command} INTO {table_name} ({','.join(columns)}) VALUES ({placeholders})"
#
#             for idx in range(0, len(rows), batch_size):
#                 batch = rows[idx : idx + batch_size]
#                 values = [[row.get(col) for col in valid_columns] for row in batch]
#                 self.executemany(query, values)
#
#         except sqlite3.Error as e:
#             self.rollback()
#             raise ValueError(f"Batch operation failed: {e}")
#
#     def update_many(
#         self,
#         table_name: str,
#         rows: List[Dict[str, _Any]],
#         batch_size: int = 1000,
#         where: Optional[str] = None,
#         columns: Optional[List[str]] = None,
#     ) -> None:
#         with self.transaction():
#             self._run_many(
#                 sql_command="UPDATE",
#                 table_name=table_name,
#                 rows=rows,
#                 batch_size=batch_size,
#                 inherit_foreign=False,
#                 where=where,
#                 columns=columns,
#             )
#
#     def insert_many(
#         self,
#         table_name: str,
#         rows: List[Dict[str, _Any]],
#         batch_size: int = 1000,
#         inherit_foreign: bool = True,
#         where: Optional[str] = None,
#     ) -> None:
#         with self.transaction():
#             self._run_many(
#                 sql_command="INSERT",
#                 table_name=table_name,
#                 rows=rows,
#                 batch_size=batch_size,
#                 inherit_foreign=inherit_foreign,
#                 where=where,
#             )
#
#     def replace_many(
#         self,
#         table_name: str,
#         rows: List[Dict[str, _Any]],
#         batch_size: int = 1000,
#         inherit_foreign: bool = True,
#         where: Optional[str] = None,
#     ) -> None:
#         with self.transaction():
#             self._run_many(
#                 sql_command="REPLACE",
#                 table_name=table_name,
#                 rows=rows,
#                 batch_size=batch_size,
#                 inherit_foreign=inherit_foreign,
#                 where=where,
#             )
#
#     def delete_where(self, table_name: str, where: str, limit: Optional[int] = None) -> None:
#         with self.transaction():
#             if not where or not isinstance(where, str):
#                 raise ValueError("Invalid where clause")
#             params = []
#             query = f"DELETE FROM {table_name} WHERE {where}"
#             if limit is not None:
#                 if not isinstance(limit, int) or limit <= 0:
#                     raise ValueError("Limit must be a positive integer")
#                 query += f" LIMIT {limit}"
#             self.execute(query, params)
#
#     def update_where(
#         self,
#         table_name: str,
#         updates: Dict[str, _Any],
#         where: str,
#         limit: Optional[int] = None,
#     ) -> None:
#         with self.transaction():
#             if not updates:
#                 raise ValueError("Updates dictionary cannot be empty")
#             set_clause = ", ".join([f"{col} = ?" for col in updates.keys()])
#             query = f"UPDATE {table_name} SET {set_clause} WHERE {where}"
#             if limit is not None:
#                 query += f" LIMIT {limit}"
#             self.execute(query, tuple(updates.values()))
#
#
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/db/_SQLite3Mixins/_BatchMixin.py
# --------------------------------------------------------------------------------
