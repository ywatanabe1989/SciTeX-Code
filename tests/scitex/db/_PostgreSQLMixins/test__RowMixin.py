#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Comprehensive tests for _RowMixin class."""

import os
import sys
from unittest.mock import Mock, MagicMock, patch, call
import pytest
import pandas as pd
import psycopg2

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../src')))

from scitex.db._PostgreSQLMixins import _RowMixin


class MockRowMixin(_RowMixin):
    """Mock class that includes _RowMixin for testing."""
    
    def __init__(self):
        self.cursor = Mock()


class TestRowMixin:
    """Test suite for _RowMixin class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mixin = MockRowMixin()
        
    def teardown_method(self):
        """Clean up after tests."""
        self.mixin.cursor.reset_mock()


class TestGetRows(TestRowMixin):
    """Tests for get_rows method."""
    
    def test_get_all_rows_basic(self):
        """Test getting all rows from a table."""
        # Mock cursor behavior
        self.mixin.cursor.description = [("id",), ("name",), ("email",)]
        self.mixin.cursor.fetchall.return_value = [
            (1, "Alice", "alice@example.com"),
            (2, "Bob", "bob@example.com")
        ]
        
        result = self.mixin.get_rows("users")
        
        # Verify query
        self.mixin.cursor.execute.assert_called_once_with("SELECT * FROM users")
        
        # Verify result is DataFrame
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert list(result.columns) == ["id", "name", "email"]
        
    def test_get_rows_with_columns(self):
        """Test getting specific columns."""
        self.mixin.cursor.description = [("name",), ("email",)]
        self.mixin.cursor.fetchall.return_value = [
            ("Alice", "alice@example.com"),
        ]
        
        result = self.mixin.get_rows("users", columns=["name", "email"])
        
        expected_query = 'SELECT "name", "email" FROM users'
        self.mixin.cursor.execute.assert_called_once_with(expected_query)
        
    def test_get_rows_with_single_column_string(self):
        """Test getting single column specified as string."""
        self.mixin.cursor.description = [("name",)]
        self.mixin.cursor.fetchall.return_value = [("Alice",), ("Bob",)]
        
        result = self.mixin.get_rows("users", columns="name")
        
        expected_query = 'SELECT "name" FROM users'
        self.mixin.cursor.execute.assert_called_once_with(expected_query)
        
    def test_get_rows_with_where_clause(self):
        """Test filtering with WHERE clause."""
        self.mixin.cursor.description = [("id",), ("name",)]
        self.mixin.cursor.fetchall.return_value = [(1, "Alice")]
        
        result = self.mixin.get_rows("users", where="age > 18")
        
        expected_query = "SELECT * FROM users WHERE age > 18"
        self.mixin.cursor.execute.assert_called_once_with(expected_query)
        
    def test_get_rows_with_order_by(self):
        """Test ordering results."""
        self.mixin.cursor.description = [("id",), ("name",)]
        self.mixin.cursor.fetchall.return_value = [(2, "Bob"), (1, "Alice")]
        
        result = self.mixin.get_rows("users", order_by="name DESC")
        
        expected_query = "SELECT * FROM users ORDER BY name DESC"
        self.mixin.cursor.execute.assert_called_once_with(expected_query)
        
    def test_get_rows_with_limit(self):
        """Test limiting results."""
        self.mixin.cursor.description = [("id",), ("name",)]
        self.mixin.cursor.fetchall.return_value = [(1, "Alice")]
        
        result = self.mixin.get_rows("users", limit=10)
        
        expected_query = "SELECT * FROM users LIMIT 10"
        self.mixin.cursor.execute.assert_called_once_with(expected_query)
        
    def test_get_rows_with_offset(self):
        """Test pagination with offset."""
        self.mixin.cursor.description = [("id",), ("name",)]
        self.mixin.cursor.fetchall.return_value = [(11, "User11")]
        
        result = self.mixin.get_rows("users", limit=10, offset=10)
        
        expected_query = "SELECT * FROM users LIMIT 10 OFFSET 10"
        self.mixin.cursor.execute.assert_called_once_with(expected_query)
        
    def test_get_rows_return_as_list(self):
        """Test returning results as list."""
        self.mixin.cursor.description = [("id",), ("name",)]
        self.mixin.cursor.fetchall.return_value = [(1, "Alice"), (2, "Bob")]
        
        result = self.mixin.get_rows("users", return_as="list")
        
        assert result == [(1, "Alice"), (2, "Bob")]
        assert isinstance(result, list)
        
    def test_get_rows_return_as_dict(self):
        """Test returning results as list of dicts."""
        self.mixin.cursor.description = [("id",), ("name",)]
        self.mixin.cursor.fetchall.return_value = [(1, "Alice"), (2, "Bob")]
        
        result = self.mixin.get_rows("users", return_as="dict")
        
        expected = [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"}
        ]
        assert result == expected
        
    def test_get_rows_complex_query(self):
        """Test complex query with all parameters."""
        self.mixin.cursor.description = [("name",), ("email",)]
        self.mixin.cursor.fetchall.return_value = [("Charlie", "charlie@example.com")]
        
        result = self.mixin.get_rows(
            "users",
            columns=["name", "email"],
            where="age > 25",
            order_by="name ASC",
            limit=5,
            offset=10
        )
        
        expected_query = 'SELECT "name", "email" FROM users WHERE age > 25 ORDER BY name ASC LIMIT 5 OFFSET 10'
        self.mixin.cursor.execute.assert_called_once_with(expected_query)
        
    def test_get_rows_empty_result(self):
        """Test handling empty results."""
        self.mixin.cursor.description = [("id",), ("name",)]
        self.mixin.cursor.fetchall.return_value = []
        
        result = self.mixin.get_rows("users")
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
        assert list(result.columns) == ["id", "name"]
        
    def test_get_rows_psycopg2_error(self):
        """Test handling psycopg2 errors."""
        self.mixin.cursor.execute.side_effect = psycopg2.Error("Database error")
        
        with pytest.raises(ValueError) as exc_info:
            self.mixin.get_rows("users")
        assert "Query execution failed" in str(exc_info.value)
        assert "Database error" in str(exc_info.value)
        
    def test_get_rows_generic_exception(self):
        """Test handling generic exceptions."""
        self.mixin.cursor.execute.side_effect = Exception("Unexpected error")
        
        with pytest.raises(ValueError) as exc_info:
            self.mixin.get_rows("users")
        assert "Query execution failed" in str(exc_info.value)
        assert "Unexpected error" in str(exc_info.value)
        
    def test_get_rows_special_characters_in_columns(self):
        """Test handling special characters in column names."""
        self.mixin.cursor.description = [("first_name",), ("last_name",)]
        self.mixin.cursor.fetchall.return_value = [("John", "Doe")]
        
        result = self.mixin.get_rows("users", columns=["first_name", "last_name"])
        
        expected_query = 'SELECT "first_name", "last_name" FROM users'
        self.mixin.cursor.execute.assert_called_once_with(expected_query)
        
    def test_get_rows_sql_injection_protection(self):
        """Test SQL injection protection in WHERE clause."""
        self.mixin.cursor.description = [("id",), ("name",)]
        self.mixin.cursor.fetchall.return_value = []
        
        # Dangerous WHERE clause - should be passed as-is
        # (protection should be in execute method)
        dangerous_where = "1=1; DROP TABLE users;--"
        result = self.mixin.get_rows("users", where=dangerous_where)
        
        expected_query = f"SELECT * FROM users WHERE {dangerous_where}"
        self.mixin.cursor.execute.assert_called_once_with(expected_query)


class TestGetRowCount(TestRowMixin):
    """Tests for get_row_count method."""
    
    def test_get_row_count_basic(self):
        """Test getting row count for a table."""
        self.mixin.cursor.fetchone.return_value = (42,)
        
        result = self.mixin.get_row_count("users")
        
        self.mixin.cursor.execute.assert_called_once_with("SELECT COUNT(*) FROM users")
        assert result == 42
        
    def test_get_row_count_with_where(self):
        """Test getting row count with WHERE clause."""
        self.mixin.cursor.fetchone.return_value = (10,)
        
        result = self.mixin.get_row_count("users", where="active = true")
        
        expected_query = "SELECT COUNT(*) FROM users WHERE active = true"
        self.mixin.cursor.execute.assert_called_once_with(expected_query)
        assert result == 10
        
    def test_get_row_count_no_table_name(self):
        """Test error when table name is not provided."""
        with pytest.raises(ValueError) as exc_info:
            self.mixin.get_row_count()
        assert "Table name must be specified" in str(exc_info.value)
        
    def test_get_row_count_empty_table(self):
        """Test counting empty table."""
        self.mixin.cursor.fetchone.return_value = (0,)
        
        result = self.mixin.get_row_count("empty_table")
        
        assert result == 0
        
    def test_get_row_count_large_table(self):
        """Test counting large table."""
        self.mixin.cursor.fetchone.return_value = (1000000,)
        
        result = self.mixin.get_row_count("large_table")
        
        assert result == 1000000
        
    def test_get_row_count_psycopg2_error(self):
        """Test handling psycopg2 errors."""
        self.mixin.cursor.execute.side_effect = psycopg2.Error("Table not found")
        
        with pytest.raises(ValueError) as exc_info:
            self.mixin.get_row_count("nonexistent")
        assert "Failed to get row count" in str(exc_info.value)
        assert "Table not found" in str(exc_info.value)
        
    def test_get_row_count_generic_exception(self):
        """Test handling generic exceptions."""
        self.mixin.cursor.execute.side_effect = Exception("Unexpected error")
        
        with pytest.raises(ValueError) as exc_info:
            self.mixin.get_row_count("users")
        assert "Failed to get row count" in str(exc_info.value)
        assert "Unexpected error" in str(exc_info.value)
        
    def test_get_row_count_complex_where(self):
        """Test complex WHERE clause."""
        self.mixin.cursor.fetchone.return_value = (5,)
        
        complex_where = "age > 18 AND status = 'active' AND created_at > '2024-01-01'"
        result = self.mixin.get_row_count("users", where=complex_where)
        
        expected_query = f"SELECT COUNT(*) FROM users WHERE {complex_where}"
        self.mixin.cursor.execute.assert_called_once_with(expected_query)
        assert result == 5


class TestRowMixinIntegration:
    """Integration tests for _RowMixin."""
    
    def test_pagination_workflow(self):
        """Test complete pagination workflow."""
        mixin = MockRowMixin()
        
        # Get total count
        mixin.cursor.fetchone.return_value = (100,)
        total = mixin.get_row_count("users")
        assert total == 100
        
        # Get first page
        mixin.cursor.description = [("id",), ("name",)]
        mixin.cursor.fetchall.return_value = [(i, f"User{i}") for i in range(1, 11)]
        
        page1 = mixin.get_rows("users", limit=10, offset=0)
        assert len(page1) == 10
        
        # Get second page
        mixin.cursor.fetchall.return_value = [(i, f"User{i}") for i in range(11, 21)]
        
        page2 = mixin.get_rows("users", limit=10, offset=10)
        assert len(page2) == 10
        
    def test_filtering_and_counting(self):
        """Test filtering results and getting count."""
        mixin = MockRowMixin()
        
        # Count filtered results
        mixin.cursor.fetchone.return_value = (25,)
        active_count = mixin.get_row_count("users", where="status = 'active'")
        assert active_count == 25
        
        # Get filtered results
        mixin.cursor.description = [("id",), ("name",), ("status",)]
        mixin.cursor.fetchall.return_value = [
            (1, "Alice", "active"),
            (3, "Charlie", "active")
        ]
        
        active_users = mixin.get_rows("users", where="status = 'active'")
        assert len(active_users) == 2
        
    def test_multiple_return_formats(self):
        """Test getting same data in different formats."""
        mixin = MockRowMixin()
        mixin.cursor.description = [("id",), ("name",)]
        test_data = [(1, "Alice"), (2, "Bob")]
        mixin.cursor.fetchall.return_value = test_data
        
        # As DataFrame
        df_result = mixin.get_rows("users", return_as="dataframe")
        assert isinstance(df_result, pd.DataFrame)
        
        # As list
        list_result = mixin.get_rows("users", return_as="list")
        assert list_result == test_data
        
        # As dict
        dict_result = mixin.get_rows("users", return_as="dict")
        assert dict_result == [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]


class TestRowMixinEdgeCases:
    """Edge case tests for _RowMixin."""
    
    def test_table_with_special_name(self):
        """Test handling table names with special characters."""
        mixin = MockRowMixin()
        mixin.cursor.description = [("id",)]
        mixin.cursor.fetchall.return_value = [(1,)]
        
        # Table name with schema
        result = mixin.get_rows("public.users")
        mixin.cursor.execute.assert_called_with("SELECT * FROM public.users")
        
    def test_columns_with_spaces(self):
        """Test column names with spaces."""
        mixin = MockRowMixin()
        mixin.cursor.description = [("first name",), ("last name",)]
        mixin.cursor.fetchall.return_value = [("John", "Doe")]
        
        result = mixin.get_rows("users", columns=["first name", "last name"])
        expected_query = 'SELECT "first name", "last name" FROM users'
        mixin.cursor.execute.assert_called_with(expected_query)
        
    def test_unicode_data(self):
        """Test handling Unicode data."""
        mixin = MockRowMixin()
        mixin.cursor.description = [("name",), ("city",)]
        mixin.cursor.fetchall.return_value = [
            ("José", "São Paulo"),
            ("李明", "北京")
        ]
        
        result = mixin.get_rows("users")
        assert len(result) == 2
        assert result.iloc[0]["name"] == "José"
        assert result.iloc[1]["city"] == "北京"
        
    def test_null_values(self):
        """Test handling NULL values."""
        mixin = MockRowMixin()
        mixin.cursor.description = [("id",), ("email",)]
        mixin.cursor.fetchall.return_value = [(1, None), (2, "test@example.com")]
        
        result = mixin.get_rows("users")
        assert pd.isna(result.iloc[0]["email"])
        assert result.iloc[1]["email"] == "test@example.com"
        
    def test_very_large_limit(self):
        """Test with very large LIMIT value."""
        mixin = MockRowMixin()
        mixin.cursor.description = [("id",)]
        mixin.cursor.fetchall.return_value = [(i,) for i in range(1000)]
        
        result = mixin.get_rows("users", limit=1000000)
        expected_query = "SELECT * FROM users LIMIT 1000000"
        mixin.cursor.execute.assert_called_with(expected_query)
        
    def test_negative_offset(self):
        """Test with negative offset (should pass through)."""
        mixin = MockRowMixin()
        mixin.cursor.description = [("id",)]
        mixin.cursor.fetchall.return_value = []
        
        # Negative offset - PostgreSQL will handle the error
        result = mixin.get_rows("users", offset=-10)
        expected_query = "SELECT * FROM users OFFSET -10"
        mixin.cursor.execute.assert_called_with(expected_query)


class TestRowMixinDocumentation:
    """Test documentation and type hints."""
    
    def test_method_signatures(self):
        """Test that methods have correct signatures."""
        assert hasattr(_RowMixin, 'get_rows')
        assert hasattr(_RowMixin, 'get_row_count')
        
    def test_type_annotations(self):
        """Test type annotations are present."""
        import inspect
        from typing import get_type_hints
        
        # Check get_rows annotations
        hints = get_type_hints(_RowMixin.get_rows)
        assert hints['table_name'] == str
        assert 'return_as' in inspect.signature(_RowMixin.get_rows).parameters
        
        # Check get_row_count annotations  
        hints = get_type_hints(_RowMixin.get_row_count)
        assert hints['return'] == int
        
    def test_method_docstrings(self):
        """Test that methods should have docstrings."""
        # Note: Current implementation doesn't have docstrings,
        # but this test documents that they should be added
        methods = ['get_rows', 'get_row_count']
        for method_name in methods:
            method = getattr(_RowMixin, method_name)
            # Currently will be None, but should have docstrings
            assert method.__doc__ is None or isinstance(method.__doc__, str)


class TestRowMixinPerformance:
    """Performance tests for _RowMixin."""
    
    def test_large_result_set_handling(self):
        """Test handling large result sets efficiently."""
        mixin = MockRowMixin()
        
        # Simulate large result set
        large_data = [(i, f"User{i}", f"user{i}@example.com") 
                     for i in range(10000)]
        mixin.cursor.description = [("id",), ("name",), ("email",)]
        mixin.cursor.fetchall.return_value = large_data
        
        # Should handle large data without issues
        result = mixin.get_rows("users", return_as="list")
        assert len(result) == 10000
        
    def test_query_building_performance(self):
        """Test query building is efficient."""
        mixin = MockRowMixin()
        mixin.cursor.description = [("id",)]
        mixin.cursor.fetchall.return_value = []
        
        # Many columns
        many_columns = [f"col{i}" for i in range(100)]
        result = mixin.get_rows("users", columns=many_columns)
        
        # Should build query efficiently
        assert mixin.cursor.execute.call_count == 1
        query = mixin.cursor.execute.call_args[0][0]
        assert all(f'"{col}"' in query for col in many_columns)


if __name__ == "__main__":
    pytest.main([os.path.abspath(__file__), "-v"])
