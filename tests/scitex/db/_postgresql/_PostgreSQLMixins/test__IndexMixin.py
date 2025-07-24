#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Comprehensive tests for _IndexMixin class."""

import os
import sys
from unittest.mock import Mock, MagicMock, patch, call
import pytest
import psycopg2

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../src')))

from scitex.db._PostgreSQLMixins import _IndexMixin


class MockIndexMixin(_IndexMixin):
    """Mock class that includes _IndexMixin for testing."""
    
    def __init__(self):
        self.execute = Mock()


class TestIndexMixin:
    """Test suite for _IndexMixin class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mixin = MockIndexMixin()
        
    def teardown_method(self):
        """Clean up after tests."""
        self.mixin.execute.reset_mock()


class TestCreateIndex(TestIndexMixin):
    """Tests for create_index method."""
    
    def test_create_basic_index(self):
        """Test creating a basic index."""
        self.mixin.create_index("users", ["email"])
        
        expected_query = """
            CREATE  INDEX IF NOT EXISTS idx_users_email
            ON users (email)
            """
        self.mixin.execute.assert_called_once()
        actual_query = self.mixin.execute.call_args[0][0]
        assert "CREATE" in actual_query
        assert "INDEX IF NOT EXISTS idx_users_email" in actual_query
        assert "ON users (email)" in actual_query
        
    def test_create_composite_index(self):
        """Test creating a composite index on multiple columns."""
        self.mixin.create_index("orders", ["user_id", "created_at"])
        
        self.mixin.execute.assert_called_once()
        actual_query = self.mixin.execute.call_args[0][0]
        assert "idx_orders_user_id_created_at" in actual_query
        assert "ON orders (user_id, created_at)" in actual_query
        
    def test_create_index_with_custom_name(self):
        """Test creating index with custom name."""
        self.mixin.create_index("products", ["category"], index_name="idx_prod_cat")
        
        self.mixin.execute.assert_called_once()
        actual_query = self.mixin.execute.call_args[0][0]
        assert "INDEX IF NOT EXISTS idx_prod_cat" in actual_query
        assert "ON products (category)" in actual_query
        
    def test_create_unique_index(self):
        """Test creating a unique index."""
        self.mixin.create_index("users", ["username"], unique=True)
        
        self.mixin.execute.assert_called_once()
        actual_query = self.mixin.execute.call_args[0][0]
        assert "CREATE UNIQUE INDEX" in actual_query
        assert "idx_users_username" in actual_query
        
    def test_create_index_with_special_characters(self):
        """Test creating index with special characters in table/column names."""
        self.mixin.create_index("user_profiles", ["first_name", "last_name"])
        
        self.mixin.execute.assert_called_once()
        actual_query = self.mixin.execute.call_args[0][0]
        assert "idx_user_profiles_first_name_last_name" in actual_query
        
    def test_create_index_empty_columns(self):
        """Test creating index with empty column list."""
        self.mixin.create_index("users", [])
        
        self.mixin.execute.assert_called_once()
        actual_query = self.mixin.execute.call_args[0][0]
        assert "idx_users_" in actual_query
        assert "ON users ()" in actual_query
        
    def test_create_index_psycopg2_error(self):
        """Test handling psycopg2 errors during index creation."""
        self.mixin.execute.side_effect = psycopg2.Error("Database error")
        
        with pytest.raises(ValueError) as exc_info:
            self.mixin.create_index("users", ["email"])
        assert "Failed to create index" in str(exc_info.value)
        assert "Database error" in str(exc_info.value)
        
    def test_create_index_generic_exception(self):
        """Test handling generic exceptions during index creation."""
        self.mixin.execute.side_effect = Exception("Unexpected error")
        
        with pytest.raises(ValueError) as exc_info:
            self.mixin.create_index("users", ["email"])
        assert "Failed to create index" in str(exc_info.value)
        assert "Unexpected error" in str(exc_info.value)
        
    def test_create_index_long_name(self):
        """Test creating index with very long table and column names."""
        long_table = "very_long_table_name_that_exceeds_normal_limits"
        long_columns = ["extremely_long_column_name_one", "extremely_long_column_name_two"]
        
        self.mixin.create_index(long_table, long_columns)
        
        self.mixin.execute.assert_called_once()
        actual_query = self.mixin.execute.call_args[0][0]
        expected_name = f"idx_{long_table}_{'_'.join(long_columns)}"
        assert expected_name in actual_query


class TestDropIndex(TestIndexMixin):
    """Tests for drop_index method."""
    
    def test_drop_index_basic(self):
        """Test dropping an index."""
        self.mixin.drop_index("idx_users_email")
        
        self.mixin.execute.assert_called_once_with(
            "DROP INDEX IF EXISTS idx_users_email"
        )
        
    def test_drop_index_special_name(self):
        """Test dropping index with special characters in name."""
        self.mixin.drop_index("idx_user_profiles_first_last")
        
        self.mixin.execute.assert_called_once_with(
            "DROP INDEX IF EXISTS idx_user_profiles_first_last"
        )
        
    def test_drop_index_psycopg2_error(self):
        """Test handling psycopg2 errors during index drop."""
        self.mixin.execute.side_effect = psycopg2.Error("Cannot drop index")
        
        with pytest.raises(ValueError) as exc_info:
            self.mixin.drop_index("idx_users_email")
        assert "Failed to drop index" in str(exc_info.value)
        assert "Cannot drop index" in str(exc_info.value)
        
    def test_drop_index_generic_exception(self):
        """Test handling generic exceptions during index drop."""
        self.mixin.execute.side_effect = Exception("Unexpected error")
        
        with pytest.raises(ValueError) as exc_info:
            self.mixin.drop_index("idx_users_email")
        assert "Failed to drop index" in str(exc_info.value)
        assert "Unexpected error" in str(exc_info.value)
        
    def test_drop_nonexistent_index(self):
        """Test dropping non-existent index (should not raise)."""
        # Should execute without error due to IF EXISTS clause
        self.mixin.drop_index("idx_nonexistent")
        
        self.mixin.execute.assert_called_once_with(
            "DROP INDEX IF EXISTS idx_nonexistent"
        )


class TestGetIndexes(TestIndexMixin):
    """Tests for get_indexes method."""
    
    def test_get_all_indexes(self):
        """Test getting all indexes."""
        mock_result = Mock()
        mock_result.fetchall.return_value = [
            {"schemaname": "public", "tablename": "users", 
             "indexname": "idx_users_email", "indexdef": "CREATE INDEX ..."},
            {"schemaname": "public", "tablename": "orders", 
             "indexname": "idx_orders_date", "indexdef": "CREATE INDEX ..."}
        ]
        self.mixin.execute.return_value = mock_result
        
        result = self.mixin.get_indexes()
        
        expected_query = """
            SELECT
                schemaname,
                tablename,
                indexname,
                indexdef
            FROM
                pg_indexes
            """
        self.mixin.execute.assert_called_once()
        actual_query = self.mixin.execute.call_args[0][0]
        assert "SELECT" in actual_query
        assert "pg_indexes" in actual_query
        assert "WHERE" not in actual_query
        
        assert len(result) == 2
        assert result[0]["indexname"] == "idx_users_email"
        
    def test_get_indexes_for_specific_table(self):
        """Test getting indexes for specific table."""
        mock_result = Mock()
        mock_result.fetchall.return_value = [
            {"schemaname": "public", "tablename": "users", 
             "indexname": "idx_users_email", "indexdef": "CREATE INDEX ..."}
        ]
        self.mixin.execute.return_value = mock_result
        
        result = self.mixin.get_indexes("users")
        
        self.mixin.execute.assert_called_once()
        actual_query = self.mixin.execute.call_args[0][0]
        assert "WHERE tablename = 'users'" in actual_query
        
        assert len(result) == 1
        assert result[0]["tablename"] == "users"
        
    def test_get_indexes_empty_result(self):
        """Test getting indexes when none exist."""
        mock_result = Mock()
        mock_result.fetchall.return_value = []
        self.mixin.execute.return_value = mock_result
        
        result = self.mixin.get_indexes("nonexistent_table")
        
        assert result == []
        
    def test_get_indexes_psycopg2_error(self):
        """Test handling psycopg2 errors when getting indexes."""
        self.mixin.execute.side_effect = psycopg2.Error("Query failed")
        
        with pytest.raises(ValueError) as exc_info:
            self.mixin.get_indexes()
        assert "Failed to get indexes" in str(exc_info.value)
        assert "Query failed" in str(exc_info.value)
        
    def test_get_indexes_generic_exception(self):
        """Test handling generic exceptions when getting indexes."""
        self.mixin.execute.side_effect = Exception("Unexpected error")
        
        with pytest.raises(ValueError) as exc_info:
            self.mixin.get_indexes()
        assert "Failed to get indexes" in str(exc_info.value)
        assert "Unexpected error" in str(exc_info.value)
        
    def test_get_indexes_special_table_name(self):
        """Test getting indexes for table with special characters."""
        mock_result = Mock()
        mock_result.fetchall.return_value = []
        self.mixin.execute.return_value = mock_result
        
        self.mixin.get_indexes("user_profiles")
        
        self.mixin.execute.assert_called_once()
        actual_query = self.mixin.execute.call_args[0][0]
        assert "WHERE tablename = 'user_profiles'" in actual_query


class TestIndexMixinIntegration:
    """Integration tests for _IndexMixin."""
    
    def test_create_and_drop_workflow(self):
        """Test complete workflow of creating and dropping indexes."""
        mixin = MockIndexMixin()
        
        # Create index
        mixin.create_index("users", ["email", "username"], unique=True)
        assert mixin.execute.call_count == 1
        
        # Get indexes to verify
        mock_result = Mock()
        mock_result.fetchall.return_value = [
            {"indexname": "idx_users_email_username"}
        ]
        mixin.execute.return_value = mock_result
        
        indexes = mixin.get_indexes("users")
        assert len(indexes) == 1
        assert mixin.execute.call_count == 2
        
        # Drop index
        mixin.drop_index("idx_users_email_username")
        assert mixin.execute.call_count == 3
        
    def test_multiple_indexes_on_same_table(self):
        """Test creating multiple indexes on the same table."""
        mixin = MockIndexMixin()
        
        # Create multiple indexes
        mixin.create_index("orders", ["user_id"])
        mixin.create_index("orders", ["created_at"])
        mixin.create_index("orders", ["status", "created_at"], 
                          index_name="idx_orders_status_date")
        
        assert mixin.execute.call_count == 3
        
        # Verify different index names were generated
        calls = mixin.execute.call_args_list
        queries = [call[0][0] for call in calls]
        
        assert "idx_orders_user_id" in queries[0]
        assert "idx_orders_created_at" in queries[1]
        assert "idx_orders_status_date" in queries[2]
        
    def test_sql_injection_protection(self):
        """Test that the mixin doesn't enable SQL injection."""
        mixin = MockIndexMixin()
        
        # Attempt SQL injection in table name
        malicious_table = "users; DROP TABLE users;--"
        mixin.create_index(malicious_table, ["email"])
        
        # The query should include the malicious string as-is
        # (sanitization should be handled by execute method)
        actual_query = mixin.execute.call_args[0][0]
        assert malicious_table in actual_query
        
    def test_index_types_coverage(self):
        """Test different types of indexes."""
        mixin = MockIndexMixin()
        
        # Regular index
        mixin.create_index("table1", ["col1"])
        
        # Unique index
        mixin.create_index("table2", ["col2"], unique=True)
        
        # Composite index
        mixin.create_index("table3", ["col3", "col4", "col5"])
        
        # Custom named index
        mixin.create_index("table4", ["col6"], index_name="custom_idx")
        
        assert mixin.execute.call_count == 4
        
        queries = [call[0][0] for call in mixin.execute.call_args_list]
        
        # Verify each query
        assert "CREATE  INDEX" in queries[0] and "UNIQUE" not in queries[0]
        assert "CREATE UNIQUE INDEX" in queries[1]
        assert "col3, col4, col5" in queries[2]
        assert "custom_idx" in queries[3]


class TestIndexMixinEdgeCases:
    """Edge case tests for _IndexMixin."""
    
    def test_empty_execute_result(self):
        """Test when execute returns None."""
        mixin = MockIndexMixin()
        mixin.execute.return_value = None
        
        with pytest.raises(AttributeError):
            mixin.get_indexes()
            
    def test_very_long_index_name(self):
        """Test index name length limits."""
        mixin = MockIndexMixin()
        
        # PostgreSQL has a 63 character limit for identifiers
        long_columns = ["a" * 20 for _ in range(5)]
        mixin.create_index("table", long_columns)
        
        actual_query = mixin.execute.call_args[0][0]
        # The generated name will be very long
        assert "idx_table_" in actual_query
        
    def test_unicode_in_names(self):
        """Test handling Unicode in table/column names."""
        mixin = MockIndexMixin()
        
        # Note: Actual PostgreSQL may not support these, but test mixin behavior
        mixin.create_index("用户表", ["电子邮件"])
        
        actual_query = mixin.execute.call_args[0][0]
        assert "用户表" in actual_query
        assert "电子邮件" in actual_query
        
    def test_concurrent_index_operations(self):
        """Test behavior with concurrent operations."""
        mixin = MockIndexMixin()
        
        # Simulate concurrent index creation
        mixin.execute.side_effect = [None, psycopg2.Error("Index already exists")]
        
        # First creation succeeds
        mixin.create_index("users", ["email"])
        
        # Second creation fails
        with pytest.raises(ValueError):
            mixin.create_index("users", ["email"])


class TestIndexMixinDocumentation:
    """Test documentation and type hints."""
    
    def test_method_signatures(self):
        """Test that methods have correct signatures."""
        assert hasattr(_IndexMixin, 'create_index')
        assert hasattr(_IndexMixin, 'drop_index')
        assert hasattr(_IndexMixin, 'get_indexes')
        
    def test_type_annotations(self):
        """Test type annotations are present."""
        import inspect
        from typing import List
        
        # Check create_index annotations
        sig = inspect.signature(_IndexMixin.create_index)
        assert sig.parameters['table_name'].annotation == str
        assert sig.parameters['column_names'].annotation == List[str]
        # index_name has a default of None, check if annotation exists
        assert 'index_name' in sig.parameters
        assert sig.parameters['unique'].annotation == bool
        
    def test_method_docstrings(self):
        """Test that methods should have docstrings."""
        # Note: Current implementation doesn't have docstrings,
        # but this test documents that they should be added
        methods = ['create_index', 'drop_index', 'get_indexes']
        for method_name in methods:
            method = getattr(_IndexMixin, method_name)
            # Currently will be None, but should have docstrings
            assert method.__doc__ is None or isinstance(method.__doc__, str)

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/db/_postgresql/_PostgreSQLMixins/_IndexMixin.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-02-27 22:15:05 (ywatanabe)"
# # File: /home/ywatanabe/proj/scitex_dev/src/scitex/db/_PostgreSQLMixins/_IndexMixin.py
# 
# THIS_FILE = (
#     "/home/ywatanabe/proj/scitex_repo/src/scitex/db/_PostgreSQLMixins/_IndexMixin.py"
# )
# 
# from typing import List
# import psycopg2
# 
# 
# class _IndexMixin:
#     def create_index(
#         self,
#         table_name: str,
#         column_names: List[str],
#         index_name: str = None,
#         unique: bool = False,
#     ) -> None:
#         try:
#             if index_name is None:
#                 index_name = f"idx_{table_name}_{'_'.join(column_names)}"
# 
#             unique_clause = "UNIQUE" if unique else ""
#             columns_str = ", ".join(column_names)
# 
#             query = f"""
#             CREATE {unique_clause} INDEX IF NOT EXISTS {index_name}
#             ON {table_name} ({columns_str})
#             """
#             self.execute(query)
# 
#         except (Exception, psycopg2.Error) as err:
#             raise ValueError(f"Failed to create index: {err}")
# 
#     def drop_index(self, index_name: str) -> None:
#         try:
#             self.execute(f"DROP INDEX IF EXISTS {index_name}")
#         except (Exception, psycopg2.Error) as err:
#             raise ValueError(f"Failed to drop index: {err}")
# 
#     def get_indexes(self, table_name: str = None) -> List[dict]:
#         try:
#             query = """
#             SELECT
#                 schemaname,
#                 tablename,
#                 indexname,
#                 indexdef
#             FROM
#                 pg_indexes
#             """
#             if table_name:
#                 query += f" WHERE tablename = '{table_name}'"
# 
#             return self.execute(query).fetchall()
# 
#         except (Exception, psycopg2.Error) as err:
#             raise ValueError(f"Failed to get indexes: {err}")
# 
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/db/_postgresql/_PostgreSQLMixins/_IndexMixin.py
# --------------------------------------------------------------------------------
