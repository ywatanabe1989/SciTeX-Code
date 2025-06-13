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
    main()\n\n# --------------------------------------------------------------------------------\n# Start of Source Code from: /home/ywatanabe/proj/_scitex_repo/src/scitex/db/_SQLite3Mixins/_ConnectionMixin.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-29 04:33:58 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/db/_SQLite3Mixins/_ConnectionMixin.py
#
# THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/db/_SQLite3Mixins/_ConnectionMixin.py"
#
# """
# 1. Functionality:
#    - Manages SQLite database connections with thread-safe operations
#    - Handles database journal files and transaction states
# 2. Input:
#    - Database file path
# 3. Output:
#    - Managed SQLite connection and cursor objects
# 4. Prerequisites:
#    - sqlite3
#    - threading
# """
#
# import sqlite3
# import threading
# from typing import Optional
# import os
# import shutil
# import tempfile
# from .._BaseMixins._BaseConnectionMixin import _BaseConnectionMixin
# import contextlib
#
# class _ConnectionMixin:
#     """Connection management functionality"""
#
#     def __init__(self, db_path: str, use_temp_db: bool = False):
#         self.lock = threading.Lock()
#         self._maintenance_lock = threading.Lock()
#         self.db_path = db_path
#         self.conn = None
#         self.cursor = None
#         if db_path:
#             self.connect(db_path, use_temp_db)
#
#     def __enter__(self):
#         return self
#
#     def __exit__(self, exc_type, exc_val, exc_tb):
#         self.close()
#
#     def _create_temp_copy(self, db_path: str) -> str:
#         """Creates temporary copy of database."""
#         temp_dir = tempfile.gettempdir()
#         self.temp_path = os.path.join(
#             temp_dir, f"temp_{os.path.basename(db_path)}"
#         )
#         shutil.copy2(db_path, self.temp_path)
#         return self.temp_path
#
#     def connect(self, db_path: str, use_temp_db: bool = False) -> None:
#         if self.conn:
#             self.close()
#
#         path_to_connect = self._create_temp_copy(db_path) if use_temp_db else db_path
#
#         self.conn = sqlite3.connect(path_to_connect, timeout=60.0)
#         self.cursor = self.conn.cursor()
#
#         with self.lock:
#             # WAL mode settings
#             self.cursor.execute("PRAGMA journal_mode = WAL")
#             self.cursor.execute("PRAGMA synchronous = NORMAL")
#             self.cursor.execute("PRAGMA busy_timeout = 60000")
#             self.cursor.execute("PRAGMA mmap_size = 30000000000")
#             self.cursor.execute("PRAGMA temp_store = MEMORY")
#             self.cursor.execute("PRAGMA cache_size = -2000")
#             self.conn.commit()
#
#     def close(self) -> None:
#         if self.cursor:
#             self.cursor.close()
#         if self.conn:
#             try:
#                 self.conn.rollback()
#                 self.conn.close()
#             except sqlite3.Error:
#                 pass
#         self.cursor = None
#         self.conn = None
#
#         if self.temp_path and os.path.exists(self.temp_path):
#             try:
#                 os.remove(self.temp_path)
#                 self.temp_path = None
#             except OSError:
#                 pass
#
#     def reconnect(self, use_temp_db: bool = False) -> None:
#         if self.db_path:
#             self.connect(self.db_path, use_temp_db)
#         else:
#             raise ValueError("No database path specified for reconnection")
#
#
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/db/_SQLite3Mixins/_ConnectionMixin.py
# --------------------------------------------------------------------------------
