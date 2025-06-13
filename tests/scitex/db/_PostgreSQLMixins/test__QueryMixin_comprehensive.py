#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-10"

"""Comprehensive tests for _QueryMixin.py

Tests cover:
- SELECT queries with various options
- INSERT operations
- UPDATE operations  
- DELETE operations
- Custom query execution
- COUNT queries
- Error handling and writability checks
- SQL injection concerns
- Edge cases and boundary conditions
"""

import os
import sys
from typing import List, Dict, Any, Optional
from unittest.mock import Mock, patch, MagicMock, call

import pytest

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))


class TestQueryMixin:
    """Test _QueryMixin class."""
    
    @pytest.fixture
    def mock_db_connection(self):
        """Create a mock database connection with QueryMixin."""
from scitex.db._PostgreSQLMixins import _QueryMixin
        
        class MockDB(_QueryMixin):
            def __init__(self):
                self.execute = Mock()
                self.cursor = Mock()
                self._check_writable = Mock()
        
        return MockDB()


class TestSelectQueries:
    """Test select method."""
    
    def test_select_all_columns(self, mock_db_connection):
        """Test SELECT * query."""
        # Mock cursor description and results
        mock_db_connection.cursor.description = [
            ('id',), ('name',), ('email',)
        ]
        mock_db_connection.cursor.fetchall.return_value = [
            (1, 'Alice', 'alice@example.com'),
            (2, 'Bob', 'bob@example.com')
        ]
        
        result = mock_db_connection.select('users')
        
        # Check query
        assert mock_db_connection.execute.called
        query = mock_db_connection.execute.call_args[0][0]
        assert query == "SELECT * FROM users"
        
        # Check result format
        assert len(result) == 2
        assert result[0] == {'id': 1, 'name': 'Alice', 'email': 'alice@example.com'}
        assert result[1] == {'id': 2, 'name': 'Bob', 'email': 'bob@example.com'}
    
    def test_select_specific_columns(self, mock_db_connection):
        """Test SELECT with specific columns."""
        mock_db_connection.cursor.description = [('name',), ('email',)]
        mock_db_connection.cursor.fetchall.return_value = [
            ('Alice', 'alice@example.com'),
        ]
        
        result = mock_db_connection.select(
            'users',
            columns=['name', 'email']
        )
        
        query = mock_db_connection.execute.call_args[0][0]
        assert query == "SELECT name, email FROM users"
        
        assert result[0] == {'name': 'Alice', 'email': 'alice@example.com'}
    
    def test_select_with_where_clause(self, mock_db_connection):
        """Test SELECT with WHERE clause."""
        mock_db_connection.cursor.description = [('id',), ('name',)]
        mock_db_connection.cursor.fetchall.return_value = [(1, 'Alice')]
        
        result = mock_db_connection.select(
            'users',
            where='active = %s',
            params=(True,)
        )
        
        query = mock_db_connection.execute.call_args[0][0]
        params = mock_db_connection.execute.call_args[0][1]
        
        assert "WHERE active = %s" in query
        assert params == (True,)
    
    def test_select_with_order_by(self, mock_db_connection):
        """Test SELECT with ORDER BY."""
        mock_db_connection.cursor.description = [('id',), ('name',)]
        mock_db_connection.cursor.fetchall.return_value = []
        
        mock_db_connection.select(
            'users',
            order_by='created_at DESC'
        )
        
        query = mock_db_connection.execute.call_args[0][0]
        assert "ORDER BY created_at DESC" in query
    
    def test_select_with_limit(self, mock_db_connection):
        """Test SELECT with LIMIT."""
        mock_db_connection.cursor.description = [('id',)]
        mock_db_connection.cursor.fetchall.return_value = [(1,), (2,)]
        
        mock_db_connection.select(
            'users',
            limit=10
        )
        
        query = mock_db_connection.execute.call_args[0][0]
        assert "LIMIT 10" in query
    
    def test_select_with_all_options(self, mock_db_connection):
        """Test SELECT with all options combined."""
        mock_db_connection.cursor.description = [('id',), ('email',)]
        mock_db_connection.cursor.fetchall.return_value = []
        
        mock_db_connection.select(
            'users',
            columns=['id', 'email'],
            where='status = %s AND created_at > %s',
            params=('active', '2024-01-01'),
            order_by='id DESC',
            limit=50
        )
        
        query = mock_db_connection.execute.call_args[0][0]
        params = mock_db_connection.execute.call_args[0][1]
        
        assert "SELECT id, email FROM users" in query
        assert "WHERE status = %s AND created_at > %s" in query
        assert "ORDER BY id DESC" in query
        assert "LIMIT 50" in query
        assert params == ('active', '2024-01-01')
    
    def test_select_empty_result(self, mock_db_connection):
        """Test SELECT with no results."""
        mock_db_connection.cursor.description = [('id',), ('name',)]
        mock_db_connection.cursor.fetchall.return_value = []
        
        result = mock_db_connection.select('users')
        
        assert result == []
    
    def test_select_sql_injection_table(self, mock_db_connection):
        """Test SQL injection vulnerability in table name."""
        mock_db_connection.cursor.description = [('id',)]
        mock_db_connection.cursor.fetchall.return_value = []
        
        # Attempt SQL injection in table name
        mock_db_connection.select("users; DROP TABLE users; --")
        
        query = mock_db_connection.execute.call_args[0][0]
        # Current implementation is vulnerable
        assert "users; DROP TABLE users; --" in query


class TestInsertOperations:
    """Test insert method."""
    
    def test_insert_basic(self, mock_db_connection):
        """Test basic INSERT operation."""
        data = {
            'name': 'Alice',
            'email': 'alice@example.com',
            'active': True
        }
        
        mock_db_connection.insert('users', data)
        
        # Check writability was verified
        assert mock_db_connection._check_writable.called
        
        # Check query
        query = mock_db_connection.execute.call_args[0][0]
        params = mock_db_connection.execute.call_args[0][1]
        
        # Query should contain column names and placeholders
        assert "INSERT INTO users" in query
        assert "name, email, active" in query or "name, active, email" in query
        assert "VALUES (%s, %s, %s)" in query
        
        # Check parameters (order might vary due to dict)
        assert len(params) == 3
        assert 'Alice' in params
        assert 'alice@example.com' in params
        assert True in params
    
    def test_insert_empty_data(self, mock_db_connection):
        """Test INSERT with empty data."""
        mock_db_connection.insert('users', {})
        
        query = mock_db_connection.execute.call_args[0][0]
        params = mock_db_connection.execute.call_args[0][1]
        
        assert "INSERT INTO users" in query
        assert "VALUES ()" in query
        assert params == ()
    
    def test_insert_special_values(self, mock_db_connection):
        """Test INSERT with special values."""
        data = {
            'name': None,
            'count': 0,
            'data': {'key': 'value'},  # JSON data
            'tags': ['tag1', 'tag2']   # Array data
        }
        
        mock_db_connection.insert('records', data)
        
        params = mock_db_connection.execute.call_args[0][1]
        assert None in params
        assert 0 in params
        assert {'key': 'value'} in params
        assert ['tag1', 'tag2'] in params
    
    def test_insert_column_order(self, mock_db_connection):
        """Test that column order is preserved."""
        from collections import OrderedDict
        
        # Use OrderedDict to ensure order
        data = OrderedDict([
            ('col1', 'val1'),
            ('col2', 'val2'),
            ('col3', 'val3')
        ])
        
        mock_db_connection.insert('test_table', data)
        
        query = mock_db_connection.execute.call_args[0][0]
        # Should maintain order
        assert "(col1, col2, col3)" in query


class TestUpdateOperations:
    """Test update method."""
    
    def test_update_basic(self, mock_db_connection):
        """Test basic UPDATE operation."""
        mock_db_connection.cursor.rowcount = 5
        
        data = {
            'name': 'Alice Updated',
            'email': 'alice.new@example.com'
        }
        
        count = mock_db_connection.update(
            'users',
            data,
            where='id = %s',
            params=(1,)
        )
        
        # Check writability was verified
        assert mock_db_connection._check_writable.called
        
        # Check query
        query = mock_db_connection.execute.call_args[0][0]
        params = mock_db_connection.execute.call_args[0][1]
        
        assert "UPDATE users" in query
        assert "SET" in query
        assert "name = %s" in query
        assert "email = %s" in query
        assert "WHERE id = %s" in query
        
        # Check parameters
        assert len(params) == 3
        assert 'Alice Updated' in params
        assert 'alice.new@example.com' in params
        assert 1 in params
        
        # Check return value
        assert count == 5
    
    def test_update_no_where_params(self, mock_db_connection):
        """Test UPDATE without WHERE parameters."""
        mock_db_connection.cursor.rowcount = 10
        
        data = {'status': 'inactive'}
        
        count = mock_db_connection.update(
            'users',
            data,
            where='last_login < NOW() - INTERVAL \'1 year\''
        )
        
        params = mock_db_connection.execute.call_args[0][1]
        assert params == ('inactive',)
        assert count == 10
    
    def test_update_multiple_conditions(self, mock_db_connection):
        """Test UPDATE with multiple WHERE conditions."""
        mock_db_connection.cursor.rowcount = 2
        
        data = {'verified': True}
        
        count = mock_db_connection.update(
            'users',
            data,
            where='email = %s AND status = %s',
            params=('test@example.com', 'pending')
        )
        
        params = mock_db_connection.execute.call_args[0][1]
        assert len(params) == 3
        assert params == (True, 'test@example.com', 'pending')
    
    def test_update_empty_data(self, mock_db_connection):
        """Test UPDATE with empty data."""
        mock_db_connection.cursor.rowcount = 0
        
        # This would create invalid SQL
        count = mock_db_connection.update(
            'users',
            {},
            where='id = %s',
            params=(1,)
        )
        
        query = mock_db_connection.execute.call_args[0][0]
        assert "SET" in query
        # Would be "SET WHERE id = %s" which is invalid SQL


class TestDeleteOperations:
    """Test delete method."""
    
    def test_delete_basic(self, mock_db_connection):
        """Test basic DELETE operation."""
        mock_db_connection.cursor.rowcount = 3
        
        count = mock_db_connection.delete(
            'users',
            where='status = %s',
            params=('deleted',)
        )
        
        # Check writability was verified
        assert mock_db_connection._check_writable.called
        
        # Check query
        query = mock_db_connection.execute.call_args[0][0]
        params = mock_db_connection.execute.call_args[0][1]
        
        assert query == "DELETE FROM users WHERE status = %s"
        assert params == ('deleted',)
        assert count == 3
    
    def test_delete_multiple_conditions(self, mock_db_connection):
        """Test DELETE with multiple conditions."""
        mock_db_connection.cursor.rowcount = 1
        
        count = mock_db_connection.delete(
            'sessions',
            where='user_id = %s AND created_at < %s',
            params=(123, '2024-01-01')
        )
        
        query = mock_db_connection.execute.call_args[0][0]
        assert "WHERE user_id = %s AND created_at < %s" in query
        assert count == 1
    
    def test_delete_no_params(self, mock_db_connection):
        """Test DELETE without parameters."""
        mock_db_connection.cursor.rowcount = 100
        
        count = mock_db_connection.delete(
            'temp_data',
            where='created_at < NOW() - INTERVAL \'7 days\''
        )
        
        params = mock_db_connection.execute.call_args[0][1]
        assert params is None
        assert count == 100
    
    def test_delete_sql_injection(self, mock_db_connection):
        """Test SQL injection in DELETE."""
        mock_db_connection.cursor.rowcount = 0
        
        # Attempt injection in table name
        mock_db_connection.delete(
            'users; DROP TABLE users; --',
            where='1=1'
        )
        
        query = mock_db_connection.execute.call_args[0][0]
        # Current implementation is vulnerable
        assert "users; DROP TABLE users; --" in query


class TestExecuteQuery:
    """Test execute_query method."""
    
    def test_execute_query_select(self, mock_db_connection):
        """Test custom SELECT query."""
        mock_db_connection.cursor.description = [
            ('total',), ('category',)
        ]
        mock_db_connection.cursor.fetchall.return_value = [
            (100, 'A'),
            (200, 'B')
        ]
        
        result = mock_db_connection.execute_query(
            "SELECT SUM(amount) as total, category FROM sales GROUP BY category"
        )
        
        assert len(result) == 2
        assert result[0] == {'total': 100, 'category': 'A'}
        assert result[1] == {'total': 200, 'category': 'B'}
    
    def test_execute_query_with_params(self, mock_db_connection):
        """Test custom query with parameters."""
        mock_db_connection.cursor.description = [('count',)]
        mock_db_connection.cursor.fetchall.return_value = [(42,)]
        
        result = mock_db_connection.execute_query(
            "SELECT COUNT(*) as count FROM users WHERE age > %s",
            params=(18,)
        )
        
        assert result[0]['count'] == 42
    
    def test_execute_query_no_results(self, mock_db_connection):
        """Test query that returns no results."""
        mock_db_connection.cursor.description = None
        
        result = mock_db_connection.execute_query(
            "UPDATE users SET last_seen = NOW()"
        )
        
        assert result == []
    
    def test_execute_query_complex(self, mock_db_connection):
        """Test complex query execution."""
        mock_db_connection.cursor.description = [
            ('user_id',), ('username',), ('post_count',)
        ]
        mock_db_connection.cursor.fetchall.return_value = [
            (1, 'alice', 10),
            (2, 'bob', 5)
        ]
        
        result = mock_db_connection.execute_query("""
            SELECT u.id as user_id, u.username, COUNT(p.id) as post_count
            FROM users u
            LEFT JOIN posts p ON u.id = p.user_id
            WHERE u.active = %s
            GROUP BY u.id, u.username
            HAVING COUNT(p.id) > %s
        """, params=(True, 0))
        
        assert len(result) == 2
        assert all('user_id' in r and 'username' in r and 'post_count' in r 
                  for r in result)


class TestCountQueries:
    """Test count method."""
    
    def test_count_all(self, mock_db_connection):
        """Test counting all records."""
        mock_db_connection.cursor.fetchone.return_value = (42,)
        
        count = mock_db_connection.count('users')
        
        query = mock_db_connection.execute.call_args[0][0]
        assert query == "SELECT COUNT(*) FROM users"
        assert count == 42
    
    def test_count_with_where(self, mock_db_connection):
        """Test counting with WHERE clause."""
        mock_db_connection.cursor.fetchone.return_value = (10,)
        
        count = mock_db_connection.count(
            'users',
            where='active = %s',
            params=(True,)
        )
        
        query = mock_db_connection.execute.call_args[0][0]
        params = mock_db_connection.execute.call_args[0][1]
        
        assert query == "SELECT COUNT(*) FROM users WHERE active = %s"
        assert params == (True,)
        assert count == 10
    
    def test_count_zero_results(self, mock_db_connection):
        """Test count returning zero."""
        mock_db_connection.cursor.fetchone.return_value = (0,)
        
        count = mock_db_connection.count(
            'users',
            where='1 = 0'  # Always false
        )
        
        assert count == 0
    
    def test_count_complex_where(self, mock_db_connection):
        """Test count with complex WHERE clause."""
        mock_db_connection.cursor.fetchone.return_value = (25,)
        
        count = mock_db_connection.count(
            'orders',
            where='status IN (%s, %s) AND created_at > %s',
            params=('pending', 'processing', '2024-01-01')
        )
        
        query = mock_db_connection.execute.call_args[0][0]
        assert "WHERE status IN (%s, %s) AND created_at > %s" in query


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_select_cursor_none(self, mock_db_connection):
        """Test SELECT when cursor is None."""
        mock_db_connection.cursor = None
        
        with pytest.raises(AttributeError):
            mock_db_connection.select('users')
    
    def test_insert_check_writable_fails(self, mock_db_connection):
        """Test INSERT when _check_writable raises."""
        mock_db_connection._check_writable.side_effect = Exception("Read-only mode")
        
        with pytest.raises(Exception, match="Read-only mode"):
            mock_db_connection.insert('users', {'name': 'test'})
    
    def test_update_check_writable_fails(self, mock_db_connection):
        """Test UPDATE when _check_writable raises."""
        mock_db_connection._check_writable.side_effect = Exception("Read-only mode")
        
        with pytest.raises(Exception, match="Read-only mode"):
            mock_db_connection.update('users', {'name': 'test'}, where='id=1')
    
    def test_delete_check_writable_fails(self, mock_db_connection):
        """Test DELETE when _check_writable raises."""
        mock_db_connection._check_writable.side_effect = Exception("Read-only mode")
        
        with pytest.raises(Exception, match="Read-only mode"):
            mock_db_connection.delete('users', where='id=1')


class TestSQLInjectionVulnerabilities:
    """Test SQL injection vulnerabilities."""
    
    def test_select_column_injection(self, mock_db_connection):
        """Test SQL injection in column names."""
        mock_db_connection.cursor.description = []
        mock_db_connection.cursor.fetchall.return_value = []
        
        # Attempt injection in columns
        mock_db_connection.select(
            'users',
            columns=['id', 'name; DROP TABLE users; --']
        )
        
        query = mock_db_connection.execute.call_args[0][0]
        # Current implementation is vulnerable
        assert "name; DROP TABLE users; --" in query
    
    def test_update_column_injection(self, mock_db_connection):
        """Test SQL injection in UPDATE column names."""
        mock_db_connection.cursor.rowcount = 0
        
        # Attempt injection in column name
        data = {'name; DROP TABLE users; --': 'value'}
        
        mock_db_connection.update(
            'users',
            data,
            where='id = 1'
        )
        
        query = mock_db_connection.execute.call_args[0][0]
        # Current implementation is vulnerable
        assert "name; DROP TABLE users; --" in query
    
    def test_order_by_injection(self, mock_db_connection):
        """Test SQL injection in ORDER BY."""
        mock_db_connection.cursor.description = []
        mock_db_connection.cursor.fetchall.return_value = []
        
        # Attempt injection in order_by
        mock_db_connection.select(
            'users',
            order_by='id; DROP TABLE users; --'
        )
        
        query = mock_db_connection.execute.call_args[0][0]
        assert "id; DROP TABLE users; --" in query


class TestPerformance:
    """Test performance considerations."""
    
    def test_select_large_result_set(self, mock_db_connection):
        """Test SELECT with large result set."""
        # Simulate large result
        mock_db_connection.cursor.description = [('id',), ('data',)]
        mock_db_connection.cursor.fetchall.return_value = [
            (i, f'data_{i}') for i in range(10000)
        ]
        
        result = mock_db_connection.select('large_table')
        
        # Should handle large results
        assert len(result) == 10000
        
        # Note: In production, consider using LIMIT or cursor iteration
    
    def test_insert_batch_not_supported(self, mock_db_connection):
        """Test that batch insert is not directly supported."""
        # Current implementation only supports single record insert
        data = {'name': 'test', 'value': 123}
        
        mock_db_connection.insert('records', data)
        
        # Only one execute call for single insert
        assert mock_db_connection.execute.call_count == 1
        
        # For batch inserts, would need to call insert multiple times
        # or implement a batch_insert method


if __name__ == "__main__":
    pytest.main([__file__, "-v"])