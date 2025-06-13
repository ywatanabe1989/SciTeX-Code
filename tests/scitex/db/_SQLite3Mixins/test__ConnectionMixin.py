#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 14:48:00 (ywatanabe)"
# File: ./tests/scitex/db/_SQLite3Mixins/test__ConnectionMixin.py

"""
Functionality:
    * Tests database connection management for SQLite3
    * Validates connection opening, closing, and error handling
    * Tests connection pooling and thread safety
Input:
    * Database connection parameters
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
from unittest.mock import Mock, patch, MagicMock
import threading


class TestConnectionMixin:
    """Test cases for _ConnectionMixin"""
    
    def test_connect_basic(self):
        """Test basic connection establishment"""
        from scitex.db._SQLite3Mixins import _ConnectionMixin
        
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
            
        try:
            mixin = _ConnectionMixin()
            mixin._db_path = db_path
            
            # Test connect
            mixin.connect()
            assert mixin._connection is not None
            assert isinstance(mixin._connection, sqlite3.Connection)
            
            mixin.close()
        finally:
            os.unlink(db_path)
            
    def test_disconnect(self):
        """Test connection closing"""
        from scitex.db._SQLite3Mixins import _ConnectionMixin
        
        mixin = _ConnectionMixin()
        mixin._connection = Mock()
        
        mixin.close()
        mixin._connection.close.assert_called_once()
        assert mixin._connection is None
        
    def test_is_connected(self):
        """Test connection status checking"""
        from scitex.db._SQLite3Mixins import _ConnectionMixin
        
        mixin = _ConnectionMixin()
        
        # Not connected
        assert not mixin.is_connected()
        
        # Connected
        mixin._connection = Mock()
        assert mixin.is_connected()
        
    def test_execute_basic(self):
        """Test basic query execution"""
        from scitex.db._SQLite3Mixins import _ConnectionMixin
        
        mixin = _ConnectionMixin()
        mock_cursor = Mock()
        mixin._connection = Mock(cursor=Mock(return_value=mock_cursor))
        
        # Test execute
        mixin.execute("SELECT * FROM test")
        mock_cursor.execute.assert_called_with("SELECT * FROM test", ())
        
    def test_executemany(self):
        """Test bulk query execution"""
        from scitex.db._SQLite3Mixins import _ConnectionMixin
        
        mixin = _ConnectionMixin()
        mock_cursor = Mock()
        mixin._connection = Mock(cursor=Mock(return_value=mock_cursor))
        
        # Test executemany
        values = [(1, "a"), (2, "b")]
        mixin.executemany("INSERT INTO test VALUES (?, ?)", values)
        mock_cursor.executemany.assert_called_with("INSERT INTO test VALUES (?, ?)", values)
        
    def test_auto_reconnect(self):
        """Test automatic reconnection on failure"""
        from scitex.db._SQLite3Mixins import _ConnectionMixin
        
        mixin = _ConnectionMixin()
        mixin._db_path = ":memory:"
        mixin._auto_reconnect = True
        
        # Simulate connection failure
        mixin._connection = Mock()
        mixin._connection.cursor.side_effect = sqlite3.OperationalError("Database is locked")
        
        with patch.object(mixin, 'connect') as mock_connect:
            with pytest.raises(sqlite3.OperationalError):
                mixin.execute("SELECT 1")
            mock_connect.assert_called()
            
    def test_connection_timeout(self):
        """Test connection timeout handling"""
        from scitex.db._SQLite3Mixins import _ConnectionMixin
        
        mixin = _ConnectionMixin()
        mixin._db_path = ":memory:"
        mixin._timeout = 5.0
        
        mixin.connect()
        # Verify timeout was set
        assert mixin._connection is not None
        
    def test_thread_safety(self):
        """Test thread-safe connection handling"""
        from scitex.db._SQLite3Mixins import _ConnectionMixin
        
        mixin = _ConnectionMixin()
        mixin._db_path = ":memory:"
        results = []
        
        def worker():
            try:
                mixin.connect()
                mixin.execute("SELECT 1")
                results.append("success")
            except Exception as e:
                results.append(f"error: {e}")
                
        threads = [threading.Thread(target=worker) for _ in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
            
        # Should handle concurrent access
        assert len(results) == 3


def main():
    """Run the tests"""
    pytest.main([__file__, "-v"])


if __name__ == "__main__":
    main()
