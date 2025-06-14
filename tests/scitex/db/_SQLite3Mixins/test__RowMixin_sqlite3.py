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
    main()
