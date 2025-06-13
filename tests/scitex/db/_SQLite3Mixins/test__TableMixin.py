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
    main()
