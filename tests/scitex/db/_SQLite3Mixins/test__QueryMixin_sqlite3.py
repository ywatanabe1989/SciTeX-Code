#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 14:48:00 (ywatanabe)"
# File: ./tests/scitex/db/_SQLite3Mixins/test__QueryMixin.py

"""
Functionality:
    * Tests query operations for SQLite3
    * Validates SELECT, JOIN, and complex query handling
    * Tests query optimization and caching
Input:
    * Test database and query parameters
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


class TestQueryMixin:
    """Test cases for _QueryMixin"""
    
    def test_select_basic(self):
        """Test basic SELECT query"""
        from scitex.db._SQLite3Mixins import _QueryMixin
        
        mixin = _QueryMixin()
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [(1, "test"), (2, "test2")]
        mixin.execute = Mock(return_value=mock_cursor)
        
        results = mixin.select("test_table")
        assert len(results) == 2
        mixin.execute.assert_called_with("SELECT * FROM test_table", ())
        
    def test_select_with_columns(self):
        """Test SELECT with specific columns"""
        from scitex.db._SQLite3Mixins import _QueryMixin
        
        mixin = _QueryMixin()
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [(1,), (2,)]
        mixin.execute = Mock(return_value=mock_cursor)
        
        results = mixin.select("test_table", columns=["id"])
        assert len(results) == 2
        mixin.execute.assert_called_with("SELECT id FROM test_table", ())
        
    def test_select_with_where(self):
        """Test SELECT with WHERE clause"""
        from scitex.db._SQLite3Mixins import _QueryMixin
        
        mixin = _QueryMixin()
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [(1, "test")]
        mixin.execute = Mock(return_value=mock_cursor)
        
        results = mixin.select("test_table", where="id = ?", params=(1,))
        assert len(results) == 1
        mixin.execute.assert_called_with("SELECT * FROM test_table WHERE id = ?", (1,))
        
    def test_select_with_order_by(self):
        """Test SELECT with ORDER BY"""
        from scitex.db._SQLite3Mixins import _QueryMixin
        
        mixin = _QueryMixin()
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [(2, "b"), (1, "a")]
        mixin.execute = Mock(return_value=mock_cursor)
        
        results = mixin.select("test_table", order_by="name DESC")
        mixin.execute.assert_called_with("SELECT * FROM test_table ORDER BY name DESC", ())
        
    def test_select_with_limit(self):
        """Test SELECT with LIMIT"""
        from scitex.db._SQLite3Mixins import _QueryMixin
        
        mixin = _QueryMixin()
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [(1, "test")]
        mixin.execute = Mock(return_value=mock_cursor)
        
        results = mixin.select("test_table", limit=1)
        mixin.execute.assert_called_with("SELECT * FROM test_table LIMIT 1", ())
        
    def test_join_query(self):
        """Test JOIN queries"""
        from scitex.db._SQLite3Mixins import _QueryMixin
        
        mixin = _QueryMixin()
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [(1, "test", "data")]
        mixin.execute = Mock(return_value=mock_cursor)
        
        results = mixin.join(
            "table1", 
            "table2", 
            "table1.id = table2.table1_id",
            join_type="INNER"
        )
        assert len(results) == 1
        assert "INNER JOIN" in mixin.execute.call_args[0][0]
        
    def test_count_rows(self):
        """Test row counting"""
        from scitex.db._SQLite3Mixins import _QueryMixin
        
        mixin = _QueryMixin()
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = (42,)
        mixin.execute = Mock(return_value=mock_cursor)
        
        count = mixin.count("test_table")
        assert count == 42
        mixin.execute.assert_called_with("SELECT COUNT(*) FROM test_table", ())
        
    def test_exists_query(self):
        """Test existence check"""
        from scitex.db._SQLite3Mixins import _QueryMixin
        
        mixin = _QueryMixin()
        mock_cursor = Mock()
        
        # Record exists
        mock_cursor.fetchone.return_value = (1,)
        mixin.execute = Mock(return_value=mock_cursor)
        assert mixin.exists("test_table", "id = ?", (1,)) is True
        
        # Record doesn't exist
        mock_cursor.fetchone.return_value = None
        assert mixin.exists("test_table", "id = ?", (999,)) is False
        
    def test_aggregate_functions(self):
        """Test aggregate function queries"""
        from scitex.db._SQLite3Mixins import _QueryMixin
        
        mixin = _QueryMixin()
        mock_cursor = Mock()
        
        # Test SUM
        mock_cursor.fetchone.return_value = (1000,)
        mixin.execute = Mock(return_value=mock_cursor)
        result = mixin.aggregate("test_table", "SUM", "value")
        assert result == 1000
        
        # Test AVG
        mock_cursor.fetchone.return_value = (50.5,)
        result = mixin.aggregate("test_table", "AVG", "value")
        assert result == 50.5
        
    def test_group_by_query(self):
        """Test GROUP BY queries"""
        from scitex.db._SQLite3Mixins import _QueryMixin
        
        mixin = _QueryMixin()
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [
            ("category1", 10),
            ("category2", 20)
        ]
        mixin.execute = Mock(return_value=mock_cursor)
        
        results = mixin.select(
            "test_table",
            columns=["category", "COUNT(*)"],
            group_by="category"
        )
        assert len(results) == 2
        assert "GROUP BY category" in mixin.execute.call_args[0][0]


def main():
    """Run the tests"""
    pytest.main([__file__, "-v"])


if __name__ == "__main__":
    main()
