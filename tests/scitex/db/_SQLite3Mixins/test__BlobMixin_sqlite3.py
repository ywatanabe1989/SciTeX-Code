#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 14:48:00 (ywatanabe)"
# File: ./tests/scitex/db/_SQLite3Mixins/test__BlobMixin.py

"""
Functionality:
    * Tests BLOB data handling for SQLite3
    * Validates binary data storage and retrieval
    * Tests large object operations
Input:
    * Test database and binary data
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


class TestBlobMixin:
    """Test cases for _BlobMixin"""
    
    def setup_method(self):
        """Set up test database"""
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.db_path = self.temp_db.name
        
    def teardown_method(self):
        """Clean up test database"""
        os.unlink(self.db_path)
        
    def test_insert_blob_basic(self):
        """Test basic BLOB insertion"""
        from scitex.db._SQLite3Mixins import _BlobMixin
        
        mixin = _BlobMixin()
        mixin.execute = Mock()
        mixin.transaction = Mock(return_value=Mock(__enter__=Mock(), __exit__=Mock()))
        
        # Test binary data
        blob_data = b"\x00\x01\x02\x03\x04"
        
        mixin.insert_blob("test_table", "data", blob_data, {"id": 1})
        mixin.execute.assert_called()
        
    def test_read_blob_basic(self):
        """Test BLOB reading"""
        from scitex.db._SQLite3Mixins import _BlobMixin
        
        mixin = _BlobMixin()
        mock_result = Mock(fetchone=Mock(return_value=(b"test_data",)))
        mixin.execute = Mock(return_value=mock_result)
        
        result = mixin.read_blob("test_table", "data", {"id": 1})
        assert result == b"test_data"
        
    def test_update_blob(self):
        """Test BLOB update"""
        from scitex.db._SQLite3Mixins import _BlobMixin
        
        mixin = _BlobMixin()
        mixin.execute = Mock()
        mixin.transaction = Mock(return_value=Mock(__enter__=Mock(), __exit__=Mock()))
        
        new_data = b"updated_blob_data"
        mixin.update_blob("test_table", "data", new_data, {"id": 1})
        mixin.execute.assert_called()
        
    def test_blob_size(self):
        """Test getting BLOB size"""
        from scitex.db._SQLite3Mixins import _BlobMixin
        
        mixin = _BlobMixin()
        mock_result = Mock(fetchone=Mock(return_value=(1024,)))
        mixin.execute = Mock(return_value=mock_result)
        
        size = mixin.get_blob_size("test_table", "data", {"id": 1})
        assert size == 1024
        
    def test_large_blob_handling(self):
        """Test handling of large BLOBs"""
        from scitex.db._SQLite3Mixins import _BlobMixin
        
        mixin = _BlobMixin()
        mixin.execute = Mock()
        mixin.transaction = Mock(return_value=Mock(__enter__=Mock(), __exit__=Mock()))
        
        # 1MB of data
        large_data = b"x" * (1024 * 1024)
        
        # Should handle without error
        mixin.insert_blob("test_table", "data", large_data, {"id": 1})
        mixin.execute.assert_called()
        
    def test_null_blob_handling(self):
        """Test NULL BLOB handling"""
        from scitex.db._SQLite3Mixins import _BlobMixin
        
        mixin = _BlobMixin()
        mock_result = Mock(fetchone=Mock(return_value=(None,)))
        mixin.execute = Mock(return_value=mock_result)
        
        result = mixin.read_blob("test_table", "data", {"id": 1})
        assert result is None


def main():
    """Run the tests"""
    pytest.main([__file__, "-v"])


if __name__ == "__main__":
    main()
