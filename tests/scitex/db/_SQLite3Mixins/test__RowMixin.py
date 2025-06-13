#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 14:48:00 (ywatanabe)"
# File: ./tests/scitex/db/_SQLite3Mixins/test__RowMixin.py

"""
Functionality:
    * Tests row-level operations for SQLite3
    * Validates insert, update, delete operations
    * Tests row retrieval and manipulation
Input:
    * Test database and row data
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


class TestRowMixin:
    """Test cases for _RowMixin"""
    
    def test_insert_row_basic(self):
        """Test basic row insertion"""
from scitex.db._SQLite3Mixins import _RowMixin
        
        mixin = _RowMixin()
        mixin.execute = Mock()
        mixin.transaction = Mock(return_value=Mock(__enter__=Mock(), __exit__=Mock()))
        
        row_data = {"name": "test", "value": 100}
        mixin.insert_row("test_table", row_data)
        
        # Verify SQL construction
        call_args = mixin.execute.call_args[0]
        assert "INSERT INTO test_table" in call_args[0]
        assert call_args[1] == ("test", 100)
        
    def test_insert_row_with_returning(self):
        """Test row insertion with RETURNING clause"""
from scitex.db._SQLite3Mixins import _RowMixin
        
        mixin = _RowMixin()
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = (1,)
        mixin.execute = Mock(return_value=mock_cursor)
        mixin.transaction = Mock(return_value=Mock(__enter__=Mock(), __exit__=Mock()))
        
        row_data = {"name": "test", "value": 100}
        row_id = mixin.insert_row("test_table", row_data, returning="id")
        assert row_id == 1
        
    def test_update_row(self):
        """Test row update"""
from scitex.db._SQLite3Mixins import _RowMixin
        
        mixin = _RowMixin()
        mixin.execute = Mock()
        mixin.transaction = Mock(return_value=Mock(__enter__=Mock(), __exit__=Mock()))
        
        updates = {"name": "updated", "value": 200}
        mixin.update_row("test_table", updates, {"id": 1})
        
        # Verify SQL construction
        call_args = mixin.execute.call_args[0]
        assert "UPDATE test_table SET" in call_args[0]
        assert "WHERE id = ?" in call_args[0]
        
    def test_delete_row(self):
        """Test row deletion"""
from scitex.db._SQLite3Mixins import _RowMixin
        
        mixin = _RowMixin()
        mixin.execute = Mock()
        mixin.transaction = Mock(return_value=Mock(__enter__=Mock(), __exit__=Mock()))
        
        mixin.delete_row("test_table", {"id": 1})
        
        # Verify SQL construction
        call_args = mixin.execute.call_args[0]
        assert "DELETE FROM test_table WHERE id = ?" in call_args[0]
        assert call_args[1] == (1,)
        
    def test_get_row(self):
        """Test single row retrieval"""
from scitex.db._SQLite3Mixins import _RowMixin
        
        mixin = _RowMixin()
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = (1, "test", 100)
        mock_cursor.description = [("id",), ("name",), ("value",)]
        mixin.execute = Mock(return_value=mock_cursor)
        
        row = mixin.get_row("test_table", {"id": 1})
        assert row == {"id": 1, "name": "test", "value": 100}
        
    def test_get_row_not_found(self):
        """Test row retrieval when not found"""
from scitex.db._SQLite3Mixins import _RowMixin
        
        mixin = _RowMixin()
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = None
        mixin.execute = Mock(return_value=mock_cursor)
        
        row = mixin.get_row("test_table", {"id": 999})
        assert row is None
        
    def test_upsert_row(self):
        """Test row upsert (INSERT OR REPLACE)"""
from scitex.db._SQLite3Mixins import _RowMixin
        
        mixin = _RowMixin()
        mixin.execute = Mock()
        mixin.transaction = Mock(return_value=Mock(__enter__=Mock(), __exit__=Mock()))
        
        row_data = {"id": 1, "name": "test", "value": 100}
        mixin.upsert_row("test_table", row_data)
        
        # Verify SQL construction
        call_args = mixin.execute.call_args[0]
        assert "INSERT OR REPLACE INTO test_table" in call_args[0]
        
    def test_row_exists(self):
        """Test checking if row exists"""
from scitex.db._SQLite3Mixins import _RowMixin
        
        mixin = _RowMixin()
        mock_cursor = Mock()
        
        # Row exists
        mock_cursor.fetchone.return_value = (1,)
        mixin.execute = Mock(return_value=mock_cursor)
        assert mixin.row_exists("test_table", {"id": 1}) is True
        
        # Row doesn't exist
        mock_cursor.fetchone.return_value = (0,)
        assert mixin.row_exists("test_table", {"id": 999}) is False
        
    def test_get_last_insert_rowid(self):
        """Test getting last inserted row ID"""
from scitex.db._SQLite3Mixins import _RowMixin
        
        mixin = _RowMixin()
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = (42,)
        mixin.execute = Mock(return_value=mock_cursor)
        
        rowid = mixin.get_last_insert_rowid()
        assert rowid == 42
        mixin.execute.assert_called_with("SELECT last_insert_rowid()")
        
    def test_duplicate_row(self):
        """Test row duplication"""
from scitex.db._SQLite3Mixins import _RowMixin
        
        mixin = _RowMixin()
        mixin.get_row = Mock(return_value={"id": 1, "name": "test", "value": 100})
        mixin.insert_row = Mock(return_value=2)
        
        new_id = mixin.duplicate_row("test_table", {"id": 1}, exclude_columns=["id"])
        assert new_id == 2
        
        # Verify insert was called without id
        insert_data = mixin.insert_row.call_args[0][1]
        assert "id" not in insert_data
        assert insert_data["name"] == "test"
        assert insert_data["value"] == 100


def main():
    """Run the tests"""
    pytest.main([__file__, "-v"])


if __name__ == "__main__":
    main()\n\n# --------------------------------------------------------------------------------\n# Start of Source Code from: /home/ywatanabe/proj/_scitex_repo/src/scitex/db/_SQLite3Mixins/_RowMixin.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-25 01:38:17 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/db/_SQLite3Mixins/_RowMixin.py
#
# THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/db/_SQLite3Mixins/_RowMixin.py"
#
# import sqlite3
# from typing import List
# from typing import Optional
# import pandas as pd
# from .._BaseMixins._BaseRowMixin import _BaseRowMixin
#
# class _RowMixin:
#     """Row operations functionality"""
#
#     def get_rows(
#         self,
#         table_name: str,
#         columns: List[str] = None,
#         where: str = None,
#         order_by: str = None,
#         limit: Optional[int] = None,
#         offset: Optional[int] = None,
#         return_as: str = "dataframe",
#     ):
#         if columns is None:
#             columns_str = "*"
#         elif isinstance(columns, str):
#             columns_str = f'"{columns}"'
#         else:
#             columns_str = ", ".join(f'"{col}"' for col in columns)
#
#         try:
#             query_parts = [f"SELECT {columns_str} FROM {table_name}"]
#
#             if where:
#                 query_parts.append(f"WHERE {where}")
#             if order_by:
#                 query_parts.append(f"ORDER BY {order_by}")
#             if limit is not None:
#                 query_parts.append(f"LIMIT {limit}")
#             if offset is not None:
#                 query_parts.append(f"OFFSET {offset}")
#
#             query = " ".join(query_parts)
#             self.cursor.execute(query)
#
#             column_names = [
#                 description[0] for description in self.cursor.description
#             ]
#             data = self.cursor.fetchall()
#
#             if return_as == "list":
#                 return data
#             elif return_as == "dict":
#                 return [dict(zip(column_names, row)) for row in data]
#             else:
#                 return pd.DataFrame(data, columns=column_names)
#
#         except sqlite3.Error as error:
#             raise sqlite3.Error(f"Query execution failed: {str(error)}")
#
#     def get_row_count(self, table_name: str = None, where: str = None) -> int:
#         if table_name is None:
#             raise ValueError("Table name must be specified")
#
#         query = f"SELECT COUNT(*) FROM {table_name}"
#         if where:
#             query += f" WHERE {where}"
#
#         self.cursor.execute(query)
#         return self.cursor.fetchone()[0]
#
#
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/db/_SQLite3Mixins/_RowMixin.py
# --------------------------------------------------------------------------------
