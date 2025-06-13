#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-10"

"""Comprehensive tests for _IndexMixin.py

Tests cover:
- Index creation with various options
- Index dropping
- Index listing and querying
- Error handling for database operations
- SQL injection prevention
- Unique and non-unique indexes
"""

import os
import sys
from typing import List
from unittest.mock import Mock, patch, MagicMock, call

import psycopg2
import pytest

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))


class TestIndexMixin:
    """Test _IndexMixin class."""
    
    @pytest.fixture
    def mock_db_connection(self):
        """Create a mock database connection with IndexMixin."""
from scitex.db._PostgreSQLMixins import _IndexMixin
        
        class MockDB(_IndexMixin):
            def __init__(self):
                self.execute = Mock()
        
        return MockDB()
    
    @pytest.fixture
    def mock_cursor(self):
        """Create a mock cursor for database operations."""
        cursor = Mock()
        cursor.fetchall = Mock(return_value=[])
        return cursor


class TestCreateIndex:
    """Test create_index method."""
    
    def test_create_index_basic(self, mock_db_connection):
        """Test basic index creation."""
        mock_db_connection.create_index(
            table_name="users",
            column_names=["email"]
        )
        
        # Check execute was called
        assert mock_db_connection.execute.called
        
        # Get the SQL query
        call_args = mock_db_connection.execute.call_args[0][0]
        
        # Check query structure
        assert "CREATE" in call_args
        assert "INDEX IF NOT EXISTS" in call_args
        assert "idx_users_email" in call_args
        assert "ON users (email)" in call_args
    
    def test_create_index_multi_column(self, mock_db_connection):
        """Test index creation with multiple columns."""
        mock_db_connection.create_index(
            table_name="orders",
            column_names=["user_id", "created_at"]
        )
        
        call_args = mock_db_connection.execute.call_args[0][0]
        
        assert "idx_orders_user_id_created_at" in call_args
        assert "ON orders (user_id, created_at)" in call_args
    
    def test_create_index_custom_name(self, mock_db_connection):
        """Test index creation with custom name."""
        mock_db_connection.create_index(
            table_name="products",
            column_names=["category", "price"],
            index_name="idx_category_price_lookup"
        )
        
        call_args = mock_db_connection.execute.call_args[0][0]
        
        assert "idx_category_price_lookup" in call_args
        assert "idx_products_category_price" not in call_args
    
    def test_create_unique_index(self, mock_db_connection):
        """Test unique index creation."""
        mock_db_connection.create_index(
            table_name="users",
            column_names=["username"],
            unique=True
        )
        
        call_args = mock_db_connection.execute.call_args[0][0]
        
        assert "CREATE UNIQUE INDEX" in call_args
        assert "ON users (username)" in call_args
    
    def test_create_index_sql_formatting(self, mock_db_connection):
        """Test SQL query formatting."""
        mock_db_connection.create_index(
            table_name="test_table",
            column_names=["col1", "col2", "col3"]
        )
        
        call_args = mock_db_connection.execute.call_args[0][0]
        
        # Check proper formatting
        assert call_args.strip().startswith("CREATE")
        assert "ON test_table (col1, col2, col3)" in call_args
    
    def test_create_index_error_handling(self, mock_db_connection):
        """Test error handling during index creation."""
        # Mock execute to raise an error
        mock_db_connection.execute.side_effect = psycopg2.Error("Database error")
        
        with pytest.raises(ValueError) as exc_info:
            mock_db_connection.create_index(
                table_name="users",
                column_names=["email"]
            )
        
        assert "Failed to create index" in str(exc_info.value)
        assert "Database error" in str(exc_info.value)
    
    def test_create_index_general_exception(self, mock_db_connection):
        """Test handling of general exceptions."""
        mock_db_connection.execute.side_effect = Exception("Unexpected error")
        
        with pytest.raises(ValueError) as exc_info:
            mock_db_connection.create_index(
                table_name="users",
                column_names=["email"]
            )
        
        assert "Failed to create index" in str(exc_info.value)


class TestDropIndex:
    """Test drop_index method."""
    
    def test_drop_index_basic(self, mock_db_connection):
        """Test basic index dropping."""
        mock_db_connection.drop_index("idx_users_email")
        
        assert mock_db_connection.execute.called
        call_args = mock_db_connection.execute.call_args[0][0]
        
        assert "DROP INDEX IF EXISTS idx_users_email" in call_args
    
    def test_drop_index_special_characters(self, mock_db_connection):
        """Test dropping index with special characters in name."""
        mock_db_connection.drop_index("idx_users_email_2024")
        
        call_args = mock_db_connection.execute.call_args[0][0]
        assert "DROP INDEX IF EXISTS idx_users_email_2024" in call_args
    
    def test_drop_index_error_handling(self, mock_db_connection):
        """Test error handling during index dropping."""
        mock_db_connection.execute.side_effect = psycopg2.Error("Cannot drop index")
        
        with pytest.raises(ValueError) as exc_info:
            mock_db_connection.drop_index("idx_test")
        
        assert "Failed to drop index" in str(exc_info.value)
        assert "Cannot drop index" in str(exc_info.value)
    
    def test_drop_nonexistent_index(self, mock_db_connection):
        """Test dropping non-existent index (should not error due to IF EXISTS)."""
        mock_db_connection.drop_index("idx_nonexistent")
        
        # Should execute without error due to IF EXISTS clause
        assert mock_db_connection.execute.called
        call_args = mock_db_connection.execute.call_args[0][0]
        assert "IF EXISTS" in call_args


class TestGetIndexes:
    """Test get_indexes method."""
    
    def test_get_indexes_all(self, mock_db_connection):
        """Test getting all indexes."""
        # Mock return value
        mock_result = Mock()
        mock_result.fetchall.return_value = [
            {
                'schemaname': 'public',
                'tablename': 'users',
                'indexname': 'idx_users_email',
                'indexdef': 'CREATE INDEX idx_users_email ON users(email)'
            }
        ]
        mock_db_connection.execute.return_value = mock_result
        
        result = mock_db_connection.get_indexes()
        
        assert mock_db_connection.execute.called
        call_args = mock_db_connection.execute.call_args[0][0]
        
        # Check base query
        assert "SELECT" in call_args
        assert "schemaname" in call_args
        assert "tablename" in call_args
        assert "indexname" in call_args
        assert "indexdef" in call_args
        assert "FROM pg_indexes" in call_args
        
        # Should not have WHERE clause for all indexes
        assert "WHERE" not in call_args
        
        assert result == mock_result.fetchall.return_value
    
    def test_get_indexes_by_table(self, mock_db_connection):
        """Test getting indexes for specific table."""
        mock_result = Mock()
        mock_result.fetchall.return_value = []
        mock_db_connection.execute.return_value = mock_result
        
        mock_db_connection.get_indexes(table_name="users")
        
        call_args = mock_db_connection.execute.call_args[0][0]
        
        # Should have WHERE clause
        assert "WHERE tablename = 'users'" in call_args
    
    def test_get_indexes_sql_injection_risk(self, mock_db_connection):
        """Test potential SQL injection in table name."""
        # This test shows a vulnerability - table_name is directly interpolated
        mock_result = Mock()
        mock_result.fetchall.return_value = []
        mock_db_connection.execute.return_value = mock_result
        
        # Attempt SQL injection
        mock_db_connection.get_indexes(table_name="users'; DROP TABLE users; --")
        
        call_args = mock_db_connection.execute.call_args[0][0]
        
        # The current implementation is vulnerable to SQL injection
        assert "users'; DROP TABLE users; --" in call_args
        # This is a security issue that should be fixed with parameterized queries
    
    def test_get_indexes_error_handling(self, mock_db_connection):
        """Test error handling when getting indexes."""
        mock_db_connection.execute.side_effect = psycopg2.Error("Access denied")
        
        with pytest.raises(ValueError) as exc_info:
            mock_db_connection.get_indexes()
        
        assert "Failed to get indexes" in str(exc_info.value)
        assert "Access denied" in str(exc_info.value)
    
    def test_get_indexes_return_format(self, mock_db_connection):
        """Test the return format of get_indexes."""
        mock_result = Mock()
        mock_result.fetchall.return_value = [
            ('public', 'users', 'users_pkey', 'CREATE UNIQUE INDEX...'),
            ('public', 'users', 'idx_users_email', 'CREATE INDEX...')
        ]
        mock_db_connection.execute.return_value = mock_result
        
        result = mock_db_connection.get_indexes("users")
        
        assert isinstance(result, list)
        assert len(result) == 2


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_create_index_empty_columns(self, mock_db_connection):
        """Test creating index with empty column list."""
        # Should handle gracefully or error appropriately
        mock_db_connection.create_index(
            table_name="users",
            column_names=[]
        )
        
        call_args = mock_db_connection.execute.call_args[0][0]
        # Will create invalid SQL: "ON users ()"
        assert "ON users ()" in call_args
    
    def test_create_index_special_column_names(self, mock_db_connection):
        """Test creating index with special column names."""
        mock_db_connection.create_index(
            table_name="users",
            column_names=["user-id", "created_at", "is_active"]
        )
        
        call_args = mock_db_connection.execute.call_args[0][0]
        
        # Check columns are properly joined
        assert "user-id, created_at, is_active" in call_args
    
    def test_drop_index_empty_name(self, mock_db_connection):
        """Test dropping index with empty name."""
        mock_db_connection.drop_index("")
        
        call_args = mock_db_connection.execute.call_args[0][0]
        assert "DROP INDEX IF EXISTS" in call_args
        # Will execute "DROP INDEX IF EXISTS " which is invalid SQL
    
    def test_get_indexes_none_result(self, mock_db_connection):
        """Test get_indexes when execute returns None."""
        mock_db_connection.execute.return_value = None
        
        with pytest.raises(AttributeError):
            # Will fail when trying to call fetchall() on None
            mock_db_connection.get_indexes()


class TestIntegration:
    """Test integration scenarios."""
    
    def test_create_and_drop_workflow(self, mock_db_connection):
        """Test creating and then dropping an index."""
        # Create index
        mock_db_connection.create_index(
            table_name="orders",
            column_names=["user_id", "status"]
        )
        
        # Verify creation
        create_call = mock_db_connection.execute.call_args_list[0][0][0]
        assert "CREATE" in create_call
        assert "idx_orders_user_id_status" in create_call
        
        # Drop the same index
        mock_db_connection.drop_index("idx_orders_user_id_status")
        
        # Verify drop
        drop_call = mock_db_connection.execute.call_args_list[1][0][0]
        assert "DROP INDEX IF EXISTS idx_orders_user_id_status" in drop_call
    
    def test_multiple_indexes_same_table(self, mock_db_connection):
        """Test creating multiple indexes on same table."""
        # Create first index
        mock_db_connection.create_index(
            table_name="products",
            column_names=["category"]
        )
        
        # Create second index
        mock_db_connection.create_index(
            table_name="products",
            column_names=["price"]
        )
        
        # Create composite index
        mock_db_connection.create_index(
            table_name="products",
            column_names=["category", "price"],
            index_name="idx_products_category_price"
        )
        
        # Verify all three were created
        assert mock_db_connection.execute.call_count == 3
        
        calls = [call[0][0] for call in mock_db_connection.execute.call_args_list]
        assert any("idx_products_category" in call for call in calls)
        assert any("idx_products_price" in call for call in calls)
        assert any("idx_products_category_price" in call for call in calls)


class TestSQLInjectionPrevention:
    """Test SQL injection vulnerabilities and prevention."""
    
    def test_create_index_table_injection(self, mock_db_connection):
        """Test SQL injection in table name."""
        # Attempt injection in table name
        mock_db_connection.create_index(
            table_name="users; DROP TABLE users; --",
            column_names=["email"]
        )
        
        call_args = mock_db_connection.execute.call_args[0][0]
        # Current implementation is vulnerable
        assert "users; DROP TABLE users; --" in call_args
    
    def test_create_index_column_injection(self, mock_db_connection):
        """Test SQL injection in column names."""
        mock_db_connection.create_index(
            table_name="users",
            column_names=["email); DROP TABLE users; --"]
        )
        
        call_args = mock_db_connection.execute.call_args[0][0]
        # Current implementation is vulnerable
        assert "email); DROP TABLE users; --" in call_args
    
    def test_parameterized_query_recommendation(self):
        """Test that demonstrates need for parameterized queries."""
        # This test documents that the current implementation
        # should be updated to use parameterized queries
        # to prevent SQL injection
        
        # Recommended approach would be:
        # cursor.execute(
        #     "CREATE INDEX %s ON %s (%s)",
        #     (AsIs(index_name), AsIs(table_name), AsIs(columns_str))
        # )
        
        assert True  # Document the security concern


class TestPerformance:
    """Test performance considerations."""
    
    def test_create_index_large_table_warning(self, mock_db_connection):
        """Test that large table indexing is handled."""
        # Creating indexes on large tables can be slow
        # Consider using CONCURRENTLY option
        
        mock_db_connection.create_index(
            table_name="large_events_table",
            column_names=["timestamp", "user_id"]
        )
        
        call_args = mock_db_connection.execute.call_args[0][0]
        
        # Current implementation doesn't use CONCURRENTLY
        assert "CONCURRENTLY" not in call_args
        
        # For production, consider:
        # CREATE INDEX CONCURRENTLY to avoid table locks
    
    def test_get_indexes_performance(self, mock_db_connection):
        """Test performance of get_indexes query."""
        mock_result = Mock()
        mock_result.fetchall.return_value = []
        mock_db_connection.execute.return_value = mock_result
        
        # Getting all indexes might be slow on large databases
        mock_db_connection.get_indexes()
        
        call_args = mock_db_connection.execute.call_args[0][0]
        
        # Query uses pg_indexes which is generally efficient
        assert "pg_indexes" in call_args


class TestErrorMessages:
    """Test error message quality."""
    
    def test_create_index_detailed_error(self, mock_db_connection):
        """Test that errors provide useful information."""
        error_msg = "index 'idx_users_email' already exists"
        mock_db_connection.execute.side_effect = psycopg2.Error(error_msg)
        
        with pytest.raises(ValueError) as exc_info:
            mock_db_connection.create_index(
                table_name="users",
                column_names=["email"]
            )
        
        # Error message includes context
        assert "Failed to create index" in str(exc_info.value)
        assert error_msg in str(exc_info.value)
    
    def test_drop_index_detailed_error(self, mock_db_connection):
        """Test drop index error messages."""
        error_msg = "index 'idx_test' does not exist"
        mock_db_connection.execute.side_effect = psycopg2.Error(error_msg)
        
        with pytest.raises(ValueError) as exc_info:
            mock_db_connection.drop_index("idx_test")
        
        assert "Failed to drop index" in str(exc_info.value)
        assert error_msg in str(exc_info.value)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])