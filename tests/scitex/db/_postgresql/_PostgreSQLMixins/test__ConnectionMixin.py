#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-12-01 10:35:00 (ywatanabe)"
# File: tests/scitex/db/_PostgreSQLMixins/test__ConnectionMixin.py

"""
Comprehensive tests for PostgreSQL ConnectionMixin.
Testing PostgreSQL-specific connection handling, transactions, and error cases.
"""

import pytest
from unittest.mock import MagicMock, patch, PropertyMock
import psycopg2
from scitex.db._PostgreSQLMixins import _ConnectionMixin


class TestPostgreSQLConnectionMixin:
    """Test suite for PostgreSQL ConnectionMixin."""

    @pytest.fixture
    def mock_psycopg2(self):
        """Mock psycopg2 module."""
        with patch('scitex.db._PostgreSQLMixins._ConnectionMixin.psycopg2') as mock:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_conn.cursor.return_value = mock_cursor
            mock.connect.return_value = mock_conn
            mock.Error = psycopg2.Error
            yield mock

    @pytest.fixture
    def mixin(self, mock_psycopg2):
        """Create a ConnectionMixin instance with mocked connection."""
        return _ConnectionMixin(
            dbname="test_db",
            user="test_user",
            password="test_pass",
            host="localhost",
            port=5432
        )

    def test_init_with_connection(self, mock_psycopg2):
        """Test initialization with automatic connection."""
        mixin = _ConnectionMixin(
            dbname="test_db",
            user="test_user",
            password="test_pass",
            host="testhost",
            port=5433
        )
        
        # Verify db_config is set correctly
        assert mixin.db_config == {
            "dbname": "test_db",
            "user": "test_user",
            "password": "test_pass",
            "host": "testhost",
            "port": 5433
        }
        
        # Verify connect was called
        mock_psycopg2.connect.assert_called_once_with(
            dbname="test_db",
            user="test_user",
            password="test_pass",
            host="testhost",
            port=5433
        )

    def test_init_without_dbname(self, mock_psycopg2):
        """Test initialization without dbname doesn't connect."""
        mixin = _ConnectionMixin(
            dbname="",
            user="test_user",
            password="test_pass"
        )
        
        # Should not connect
        mock_psycopg2.connect.assert_not_called()
        assert mixin.conn is None
        assert mixin.cursor is None

    def test_connect_success(self, mixin, mock_psycopg2):
        """Test successful connection to PostgreSQL."""
        # Connection should already be established
        assert mixin.conn is not None
        assert mixin.cursor is not None
        
        # Verify autocommit and isolation level
        mixin.conn.autocommit = False
        mixin.cursor.execute.assert_called_with(
            "SET SESSION CHARACTERISTICS AS TRANSACTION ISOLATION LEVEL READ COMMITTED"
        )

    def test_connect_closes_existing(self, mixin, mock_psycopg2):
        """Test connect closes existing connection."""
        old_conn = mixin.conn
        old_cursor = mixin.cursor
        
        # Connect again
        mixin.connect()
        
        # Old connection should be closed
        old_cursor.close.assert_called()
        old_conn.close.assert_called()
        
        # New connection should be different
        assert mixin.conn != old_conn
        assert mixin.cursor != old_cursor

    def test_close(self, mixin):
        """Test closing connection."""
        conn = mixin.conn
        cursor = mixin.cursor
        
        # Close connection
        mixin.close()
        
        # Verify close was called
        cursor.close.assert_called_once()
        conn.close.assert_called_once()
        
        # Verify attributes are cleared
        assert mixin.conn is None
        assert mixin.cursor is None

    def test_close_with_error(self, mixin):
        """Test close handles psycopg2 errors gracefully."""
        # Make close raise an error
        mixin.conn.close.side_effect = psycopg2.Error("Connection error")
        
        # Should not raise
        mixin.close()
        
        # Should still clear attributes
        assert mixin.conn is None
        assert mixin.cursor is None

    def test_reconnect(self, mixin, mock_psycopg2):
        """Test reconnection."""
        old_conn = mixin.conn
        
        # Reconnect
        mixin.reconnect()
        
        # Should have new connection
        assert mixin.conn != old_conn
        assert mock_psycopg2.connect.call_count >= 2

    def test_reconnect_without_config(self):
        """Test reconnect raises error without config."""
        mixin = _ConnectionMixin(
            dbname="",
            user="",
            password=""
        )
        mixin.db_config = None
        
        with pytest.raises(ValueError, match="No database configuration"):
            mixin.reconnect()

    def test_execute_success(self, mixin):
        """Test successful query execution."""
        query = "SELECT * FROM users WHERE id = %s"
        params = (123,)
        
        # Execute query
        result = mixin.execute(query, params)
        
        # Verify execution
        mixin.cursor.execute.assert_called_once_with(query, params)
        mixin.conn.commit.assert_called_once()
        assert result == mixin.cursor

    def test_execute_without_parameters(self, mixin):
        """Test execute without parameters."""
        query = "SELECT COUNT(*) FROM users"
        
        # Execute query
        result = mixin.execute(query)
        
        # Verify execution
        mixin.cursor.execute.assert_called_once_with(query, None)
        mixin.conn.commit.assert_called_once()

    def test_execute_not_connected(self):
        """Test execute raises error when not connected."""
        mixin = _ConnectionMixin(
            dbname="",
            user="test",
            password="test"
        )
        
        with pytest.raises(ConnectionError, match="Database not connected"):
            mixin.execute("SELECT 1")

    def test_execute_with_error(self, mixin):
        """Test execute handles psycopg2 errors."""
        # Make execute raise an error
        mixin.cursor.execute.side_effect = psycopg2.Error("Syntax error")
        
        with pytest.raises(psycopg2.Error, match="Query execution failed"):
            mixin.execute("INVALID SQL")
        
        # Should rollback
        mixin.conn.rollback.assert_called_once()

    def test_executemany_success(self, mixin):
        """Test successful batch execution."""
        query = "INSERT INTO users (id, name) VALUES (%s, %s)"
        params = [(1, "John"), (2, "Jane"), (3, "Bob")]
        
        # Execute batch
        mixin.executemany(query, params)
        
        # Verify execution
        mixin.cursor.executemany.assert_called_once_with(query, params)
        mixin.conn.commit.assert_called_once()

    def test_executemany_not_connected(self):
        """Test executemany raises error when not connected."""
        mixin = _ConnectionMixin(
            dbname="",
            user="test",
            password="test"
        )
        
        with pytest.raises(ConnectionError, match="Database not connected"):
            mixin.executemany("INSERT INTO test VALUES (%s)", [(1,), (2,)])

    def test_executemany_with_error(self, mixin):
        """Test executemany handles psycopg2 errors."""
        # Make executemany raise an error
        mixin.cursor.executemany.side_effect = psycopg2.Error("Constraint violation")
        
        with pytest.raises(psycopg2.Error, match="Batch query execution failed"):
            mixin.executemany("INSERT INTO test VALUES (%s)", [(1,)])
        
        # Should rollback
        mixin.conn.rollback.assert_called_once()

    def test_postgresql_specific_features(self, mixin):
        """Test PostgreSQL-specific features."""
        # Test autocommit is disabled
        assert mixin.conn.autocommit is False
        
        # Test isolation level was set
        mixin.cursor.execute.assert_any_call(
            "SET SESSION CHARACTERISTICS AS TRANSACTION ISOLATION LEVEL READ COMMITTED"
        )

    def test_connection_parameters(self, mock_psycopg2):
        """Test all connection parameters are passed correctly."""
        _ConnectionMixin(
            dbname="production",
            user="admin",
            password="secure123",
            host="db.example.com",
            port=5432
        )
        
        # Verify all parameters passed to psycopg2
        mock_psycopg2.connect.assert_called_with(
            dbname="production",
            user="admin",
            password="secure123",
            host="db.example.com",
            port=5432
        )

    def test_thread_safety(self, mixin):
        """Test thread safety with lock."""
        # Lock should be used when setting isolation level
        assert hasattr(mixin, 'lock')
        
        # Verify lock is acquired during connect
        with patch.object(mixin.lock, '__enter__') as mock_enter:
            with patch.object(mixin.lock, '__exit__') as mock_exit:
                mixin.connect()
                mock_enter.assert_called()
                mock_exit.assert_called()

    def test_context_manager_usage(self, mock_psycopg2):
        """Test using mixin as context manager."""
        with _ConnectionMixin(
            dbname="test",
            user="test",
            password="test"
        ) as mixin:
            # Should be connected
            assert mixin.conn is not None
            assert mixin.cursor is not None
        
        # Should be closed after context
        assert mixin.conn is None
        assert mixin.cursor is None

    def test_empty_parameter_list(self, mixin):
        """Test executemany with empty parameter list."""
        mixin.executemany("DELETE FROM temp_table", [])
        
        # Should still call executemany
        mixin.cursor.executemany.assert_called_once_with(
            "DELETE FROM temp_table", []
        )


# --------------------------------------------------------------------------------

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/db/_PostgreSQLMixins/_ConnectionMixin.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-02-27 22:14:52 (ywatanabe)"
# # File: /home/ywatanabe/proj/scitex_dev/src/scitex/db/_PostgreSQLMixins/_ConnectionMixin.py
#
# THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/db/_PostgreSQLMixins/_ConnectionMixin.py"
#
# from typing import Any, Tuple
# import psycopg2
#
# from ..._BaseMixins._BaseConnectionMixin import _BaseConnectionMixin
#
#
# class _ConnectionMixin(_BaseConnectionMixin):
#     def __init__(
#         self,
#         dbname: str,
#         user: str,
#         password: str,
#         host: str = "localhost",
#         port: int = 5432,
#     ):
#         super().__init__()
#         self.db_config = {
#             "dbname": dbname,
#             "user": user,
#             "password": password,
#             "host": host,
#             "port": port,
#         }
#         if dbname:
#             self.connect()
#
#     def connect(self) -> None:
#         if self.conn:
#             self.close()
#
#         self.conn = psycopg2.connect(**self.db_config)
#         self.cursor = self.conn.cursor()
#
#         with self.lock:
#             self.conn.autocommit = False
#             self.cursor.execute(
#                 "SET SESSION CHARACTERISTICS AS TRANSACTION ISOLATION LEVEL READ COMMITTED"
#             )
#
#     def close(self) -> None:
#         if self.cursor:
#             self.cursor.close()
#         if self.conn:
#             try:
#                 self.conn.close()
#             except psycopg2.Error:
#                 pass
#         self.cursor = None
#         self.conn = None
#
#     def reconnect(self) -> None:
#         if self.db_config:
#             self.connect()
#         else:
#             raise ValueError(
#                 "No database configuration specified for reconnection"
#             )
#
#     def execute(self, query: str, parameters: Tuple = None) -> Any:
#         """Execute a database query."""
#         if not self.cursor:
#             raise ConnectionError("Database not connected")
#
#         try:
#             self.cursor.execute(query, parameters)
#             self.conn.commit()
#             return self.cursor
#         except psycopg2.Error as err:
#             self.conn.rollback()
#             raise psycopg2.Error(f"Query execution failed: {err}")
#
#
#     def executemany(self, query: str, parameters: list) -> None:
#         """Execute multiple database queries."""
#         if not self.cursor:
#             raise ConnectionError("Database not connected")
#
#         try:
#             self.cursor.executemany(query, parameters)
#             self.conn.commit()
#         except psycopg2.Error as err:
#             self.conn.rollback()
#             raise psycopg2.Error(f"Batch query execution failed: {err}")
#
# # EOF
# --------------------------------------------------------------------------------
# End of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/db/_PostgreSQLMixins/_ConnectionMixin.py
# --------------------------------------------------------------------------------
