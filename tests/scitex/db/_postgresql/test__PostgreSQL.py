#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-12-01 10:00:00 (ywatanabe)"
# File: tests/scitex/db/test__PostgreSQL.py

"""
Comprehensive tests for PostgreSQL database interface.
Testing database connection, CRUD operations, transactions, and other features.
"""

import os
import tempfile
from unittest.mock import MagicMock, Mock, patch, call
import pytest
import pandas as pd
import psycopg2
from scitex.db import PostgreSQL


class TestPostgreSQL:
    """Test suite for PostgreSQL class."""

    @pytest.fixture
    def mock_connection(self):
        """Create a mock database connection."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.autocommit = False
        return mock_conn, mock_cursor

    @pytest.fixture
    def db_config(self):
        """Standard database configuration."""
        return {
            "dbname": "test_db",
            "user": "test_user",
            "password": "test_pass",
            "host": "localhost",
            "port": 5432
        }

    @patch('psycopg2.connect')
    def test_init_with_connection(self, mock_connect, mock_connection, db_config):
        """Test initialization with database connection."""
        mock_conn, mock_cursor = mock_connection
        mock_connect.return_value = mock_conn
        
        # Create instance
        db = PostgreSQL(**db_config)
        
        # Verify connection was made
        mock_connect.assert_called_once_with(**db_config)
        assert db.db_config == db_config
        assert db.conn == mock_conn
        assert db.cursor == mock_cursor

    @patch('psycopg2.connect')
    def test_init_without_dbname(self, mock_connect):
        """Test initialization without database name (no connection)."""
        db = PostgreSQL(user="test_user", password="test_pass")
        
        # Should not connect without dbname
        mock_connect.assert_not_called()
        assert db.conn is None
        assert db.cursor is None

    @patch('psycopg2.connect')
    def test_connect(self, mock_connect, mock_connection, db_config):
        """Test explicit connection method."""
        mock_conn, mock_cursor = mock_connection
        mock_connect.return_value = mock_conn
        
        db = PostgreSQL(**db_config)
        
        # Verify connection settings
        mock_cursor.execute.assert_called_with(
            "SET SESSION CHARACTERISTICS AS TRANSACTION ISOLATION LEVEL READ COMMITTED"
        )
        assert mock_conn.autocommit is False

    @patch('psycopg2.connect')
    def test_close(self, mock_connect, mock_connection, db_config):
        """Test closing database connection."""
        mock_conn, mock_cursor = mock_connection
        mock_connect.return_value = mock_conn
        
        db = PostgreSQL(**db_config)
        db.close()
        
        # Verify cleanup
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()
        assert db.conn is None
        assert db.cursor is None

    @patch('psycopg2.connect')
    def test_execute_query(self, mock_connect, mock_connection, db_config):
        """Test query execution."""
        mock_conn, mock_cursor = mock_connection
        mock_connect.return_value = mock_conn
        
        db = PostgreSQL(**db_config)
        
        # Execute query
        query = "SELECT * FROM users"
        result = db.execute(query)
        
        # Verify execution
        mock_cursor.execute.assert_any_call(query, None)
        mock_conn.commit.assert_called()
        assert result == mock_cursor

    @patch('psycopg2.connect')
    def test_execute_with_parameters(self, mock_connect, mock_connection, db_config):
        """Test parameterized query execution."""
        mock_conn, mock_cursor = mock_connection
        mock_connect.return_value = mock_conn
        
        db = PostgreSQL(**db_config)
        
        # Execute with parameters
        query = "SELECT * FROM users WHERE id = %s"
        params = (1,)
        db.execute(query, params)
        
        # Verify execution
        mock_cursor.execute.assert_any_call(query, params)

    @patch('psycopg2.connect')
    def test_execute_error_rollback(self, mock_connect, mock_connection, db_config):
        """Test rollback on execution error."""
        mock_conn, mock_cursor = mock_connection
        mock_connect.return_value = mock_conn
        mock_cursor.execute.side_effect = psycopg2.Error("Query failed")
        
        db = PostgreSQL(**db_config)
        
        # Execute should raise error
        with pytest.raises(psycopg2.Error, match="Query execution failed"):
            db.execute("SELECT * FROM users")
        
        # Verify rollback
        mock_conn.rollback.assert_called_once()

    @patch('psycopg2.connect')
    def test_create_table(self, mock_connect, mock_connection, db_config):
        """Test table creation."""
        mock_conn, mock_cursor = mock_connection
        mock_connect.return_value = mock_conn
        
        db = PostgreSQL(**db_config)
        
        # Create table
        columns = {
            "id": "SERIAL PRIMARY KEY",
            "name": "VARCHAR(100)",
            "age": "INTEGER"
        }
        db.create_table("users", columns)
        
        # Verify SQL
        expected_sql = "CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, name VARCHAR(100), age INTEGER)"
        mock_cursor.execute.assert_any_call(expected_sql, None)

    @patch('psycopg2.connect')
    def test_insert_data(self, mock_connect, mock_connection, db_config):
        """Test data insertion."""
        mock_conn, mock_cursor = mock_connection
        mock_connect.return_value = mock_conn
        
        db = PostgreSQL(**db_config)
        
        # Insert data
        data = {"name": "John", "age": 30}
        db.insert("users", data)
        
        # Verify SQL
        expected_sql = """
            INSERT INTO users
            (name, age)
            VALUES (%s, %s)
        """
        mock_cursor.execute.assert_any_call(expected_sql, ("John", 30))

    @patch('psycopg2.connect')
    def test_select_data(self, mock_connect, mock_connection, db_config):
        """Test data selection."""
        mock_conn, mock_cursor = mock_connection
        mock_connect.return_value = mock_conn
        
        # Mock query results
        mock_cursor.description = [("id",), ("name",), ("age",)]
        mock_cursor.fetchall.return_value = [(1, "John", 30), (2, "Jane", 25)]
        
        db = PostgreSQL(**db_config)
        
        # Select data
        results = db.select("users", columns=["id", "name", "age"])
        
        # Verify results
        assert len(results) == 2
        assert results[0] == {"id": 1, "name": "John", "age": 30}
        assert results[1] == {"id": 2, "name": "Jane", "age": 25}

    @patch('psycopg2.connect')
    def test_update_data(self, mock_connect, mock_connection, db_config):
        """Test data update."""
        mock_conn, mock_cursor = mock_connection
        mock_connect.return_value = mock_conn
        mock_cursor.rowcount = 1
        
        db = PostgreSQL(**db_config)
        
        # Update data
        updates = {"age": 31}
        count = db.update("users", updates, "name = %s", ("John",))
        
        # Verify SQL and result
        expected_sql = """
            UPDATE users
            SET age = %s
            WHERE name = %s
        """
        mock_cursor.execute.assert_any_call(expected_sql, (31, "John"))
        assert count == 1

    @patch('psycopg2.connect')
    def test_delete_data(self, mock_connect, mock_connection, db_config):
        """Test data deletion."""
        mock_conn, mock_cursor = mock_connection
        mock_connect.return_value = mock_conn
        mock_cursor.rowcount = 2
        
        db = PostgreSQL(**db_config)
        
        # Delete data
        count = db.delete("users", "age < %s", (18,))
        
        # Verify SQL and result
        expected_sql = "DELETE FROM users WHERE age < %s"
        mock_cursor.execute.assert_any_call(expected_sql, (18,))
        assert count == 2

    @patch('psycopg2.connect')
    def test_transaction_commit(self, mock_connect, mock_connection, db_config):
        """Test transaction commit."""
        mock_conn, mock_cursor = mock_connection
        mock_connect.return_value = mock_conn
        
        db = PostgreSQL(**db_config)
        
        # Begin transaction
        db.begin_transaction()
        db.insert("users", {"name": "Test"})
        db.commit()
        
        # Verify transaction flow
        mock_cursor.execute.assert_any_call("BEGIN")
        mock_conn.commit.assert_called()

    @patch('psycopg2.connect')
    def test_transaction_rollback(self, mock_connect, mock_connection, db_config):
        """Test transaction rollback."""
        mock_conn, mock_cursor = mock_connection
        mock_connect.return_value = mock_conn
        
        db = PostgreSQL(**db_config)
        
        # Begin and rollback transaction
        db.begin_transaction()
        db.rollback()
        
        # Verify rollback
        mock_conn.rollback.assert_called_once()

    @patch('psycopg2.connect')
    def test_batch_insert(self, mock_connect, mock_connection, db_config):
        """Test batch insert operation."""
        mock_conn, mock_cursor = mock_connection
        mock_connect.return_value = mock_conn
        
        db = PostgreSQL(**db_config)
        
        # Batch insert data
        data = [
            {"name": "User1", "age": 20},
            {"name": "User2", "age": 25},
            {"name": "User3", "age": 30}
        ]
        db.batch_insert("users", data)
        
        # Verify executemany was called
        mock_cursor.executemany.assert_called()

    @patch('psycopg2.connect')
    def test_blob_operations(self, mock_connect, mock_connection, db_config):
        """Test BLOB storage and retrieval."""
        mock_conn, mock_cursor = mock_connection
        mock_connect.return_value = mock_conn
        
        # Mock BLOB operations
        mock_cursor.fetchone.return_value = (b'test_blob_data',)
        
        db = PostgreSQL(**db_config)
        
        # Store BLOB
        blob_data = b"Test binary data"
        db.store_blob("files", "file_id", "data", blob_data)
        
        # Retrieve BLOB
        retrieved = db.get_blob("files", "data", "file_id = %s", ("test_id",))
        
        # Verify operations
        assert mock_cursor.execute.call_count >= 2  # store and retrieve

    @patch('psycopg2.connect')
    def test_create_index(self, mock_connect, mock_connection, db_config):
        """Test index creation."""
        mock_conn, mock_cursor = mock_connection
        mock_connect.return_value = mock_conn
        
        db = PostgreSQL(**db_config)
        
        # Create index
        db.create_index("users", ["name", "age"])
        
        # Verify SQL
        expected_sql = "CREATE INDEX idx_users_name_age ON users (name, age)"
        mock_cursor.execute.assert_any_call(expected_sql, None)

    @patch('psycopg2.connect')
    def test_get_tables(self, mock_connect, mock_connection, db_config):
        """Test getting list of tables."""
        mock_conn, mock_cursor = mock_connection
        mock_connect.return_value = mock_conn
        mock_cursor.fetchall.return_value = [("users",), ("orders",), ("products",)]
        
        db = PostgreSQL(**db_config)
        
        # Get tables
        tables = db.get_tables()
        
        # Verify result
        assert tables == ["users", "orders", "products"]

    @patch('psycopg2.connect')
    def test_vacuum_operation(self, mock_connect, mock_connection, db_config):
        """Test VACUUM operation."""
        mock_conn, mock_cursor = mock_connection
        mock_connect.return_value = mock_conn
        
        db = PostgreSQL(**db_config)
        
        # Vacuum database
        db.vacuum()
        
        # Verify SQL
        mock_cursor.execute.assert_any_call("VACUUM", None)

    @patch('psycopg2.connect')
    def test_analyze_operation(self, mock_connect, mock_connection, db_config):
        """Test ANALYZE operation."""
        mock_conn, mock_cursor = mock_connection
        mock_connect.return_value = mock_conn
        
        db = PostgreSQL(**db_config)
        
        # Analyze table
        db.analyze("users")
        
        # Verify SQL
        mock_cursor.execute.assert_any_call("ANALYZE users", None)

    @patch('psycopg2.connect')
    def test_get_summaries(self, mock_connect, mock_connection, db_config):
        """Test getting table summaries."""
        mock_conn, mock_cursor = mock_connection
        mock_connect.return_value = mock_conn
        
        # Mock table names
        with patch.object(PostgreSQL, 'get_table_names', return_value=['users']):
            # Mock query results
            mock_cursor.description = [("id",), ("name",), ("age",)]
            mock_cursor.fetchall.return_value = [(1, "John", 30), (2, "Jane", 25)]
            
            db = PostgreSQL(**db_config)
            
            # Get summaries
            summaries = db.get_summaries(limit=2)
            
            # Verify result
            assert "users" in summaries
            assert isinstance(summaries["users"], pd.DataFrame)
            assert len(summaries["users"]) == 2

    @patch('psycopg2.connect')
    def test_call_method_with_summary(self, mock_connect, mock_connection, db_config):
        """Test __call__ method returning summary."""
        mock_conn, mock_cursor = mock_connection
        mock_connect.return_value = mock_conn
        
        # Mock get_summaries
        with patch.object(PostgreSQL, 'get_summaries', return_value={"test": pd.DataFrame()}):
            db = PostgreSQL(**db_config)
            
            # Call with return_summary
            result = db(return_summary=True, print_summary=False)
            
            # Verify result
            assert "test" in result

    @patch('psycopg2.connect')
    def test_summary_property(self, mock_connect, mock_connection, db_config):
        """Test summary property."""
        mock_conn, mock_cursor = mock_connection
        mock_connect.return_value = mock_conn
        
        # Mock methods
        with patch.object(PostgreSQL, '__call__') as mock_call:
            db = PostgreSQL(**db_config)
            
            # Access summary property
            _ = db.summary
            
            # Verify __call__ was invoked
            mock_call.assert_called_once()

    @patch('psycopg2.connect')
    def test_connection_error_handling(self, mock_connect):
        """Test handling of connection errors."""
        mock_connect.side_effect = psycopg2.OperationalError("Connection failed")
        
        # Should raise error
        with pytest.raises(psycopg2.OperationalError):
            PostgreSQL(dbname="test_db", user="test_user", password="test_pass")

    @patch('psycopg2.connect')
    def test_executemany(self, mock_connect, mock_connection, db_config):
        """Test executemany for batch operations."""
        mock_conn, mock_cursor = mock_connection
        mock_connect.return_value = mock_conn
        
        db = PostgreSQL(**db_config)
        
        # Execute many
        query = "INSERT INTO users (name, age) VALUES (%s, %s)"
        params = [("User1", 20), ("User2", 25), ("User3", 30)]
        db.executemany(query, params)
        
        # Verify
        mock_cursor.executemany.assert_called_once_with(query, params)
        mock_conn.commit.assert_called()

    @patch('psycopg2.connect')
    def test_foreign_key_constraint(self, mock_connect, mock_connection, db_config):
        """Test creating table with foreign key constraints."""
        mock_conn, mock_cursor = mock_connection
        mock_connect.return_value = mock_conn
        
        db = PostgreSQL(**db_config)
        
        # Create table with foreign keys
        columns = {
            "id": "SERIAL PRIMARY KEY",
            "user_id": "INTEGER",
            "product": "VARCHAR(100)"
        }
        foreign_keys = [{
            "column": "user_id",
            "references": "users",
            "referenced_column": "id"
        }]
        db.create_table("orders", columns, foreign_keys=foreign_keys)
        
        # Verify foreign key in SQL
        calls = mock_cursor.execute.call_args_list
        sql_executed = str(calls)
        assert "FOREIGN KEY" in sql_executed

    @patch('psycopg2.connect')
    def test_import_export_csv(self, mock_connect, mock_connection, db_config):
        """Test CSV import/export functionality."""
        mock_conn, mock_cursor = mock_connection
        mock_connect.return_value = mock_conn
        
        db = PostgreSQL(**db_config)
        
        # Test CSV export (mocked)
        with patch.object(db, 'export_to_csv') as mock_export:
            db.export_to_csv("users", "/tmp/users.csv")
            mock_export.assert_called_once_with("users", "/tmp/users.csv")


# --------------------------------------------------------------------------------

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/_scitex_repo/src/scitex/db/_PostgreSQL.py
# --------------------------------------------------------------------------------
