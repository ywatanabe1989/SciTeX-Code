#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 14:48:00 (ywatanabe)"
# File: ./tests/scitex/db/_SQLite3Mixins/test__MaintenanceMixin.py

"""
Functionality:
    * Tests database maintenance operations for SQLite3
    * Validates vacuum, analyze, and integrity checks
    * Tests database optimization
Input:
    * Test database
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


class TestMaintenanceMixin:
    """Test cases for _MaintenanceMixin"""
    
    def test_vacuum_database(self):
        """Test database vacuum operation"""
        from scitex.db._SQLite3Mixins import _MaintenanceMixin
        
        mixin = _MaintenanceMixin()
        mixin.execute = Mock()
        
        mixin.vacuum()
        mixin.execute.assert_called_with("VACUUM")
        
    def test_analyze_database(self):
        """Test database analysis"""
        from scitex.db._SQLite3Mixins import _MaintenanceMixin
        
        mixin = _MaintenanceMixin()
        mixin.execute = Mock()
        
        mixin.analyze()
        mixin.execute.assert_called_with("ANALYZE")
        
    def test_integrity_check(self):
        """Test database integrity check"""
        from scitex.db._SQLite3Mixins import _MaintenanceMixin
        
        mixin = _MaintenanceMixin()
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [("ok",)]
        mixin.execute = Mock(return_value=mock_cursor)
        
        result = mixin.integrity_check()
        assert result["status"] == "ok"
        mixin.execute.assert_called_with("PRAGMA integrity_check")
        
    def test_integrity_check_with_errors(self):
        """Test integrity check with errors"""
        from scitex.db._SQLite3Mixins import _MaintenanceMixin
        
        mixin = _MaintenanceMixin()
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [
            ("*** in database main ***",),
            ("Page 5 is never used",)
        ]
        mixin.execute = Mock(return_value=mock_cursor)
        
        result = mixin.integrity_check()
        assert result["status"] == "error"
        assert len(result["errors"]) == 2
        
    def test_optimize_database(self):
        """Test database optimization"""
        from scitex.db._SQLite3Mixins import _MaintenanceMixin
        
        mixin = _MaintenanceMixin()
        mixin.execute = Mock()
        
        mixin.optimize()
        mixin.execute.assert_called_with("PRAGMA optimize")
        
    def test_get_database_stats(self):
        """Test retrieving database statistics"""
        from scitex.db._SQLite3Mixins import _MaintenanceMixin
        
        mixin = _MaintenanceMixin()
        mock_cursor = Mock()
        
        # Mock various PRAGMA results
        mixin.execute = Mock()
        mixin.execute.side_effect = [
            Mock(fetchone=Mock(return_value=(4096,))),  # page_size
            Mock(fetchone=Mock(return_value=(1000,))),  # page_count
            Mock(fetchone=Mock(return_value=(50,))),    # freelist_count
            Mock(fetchall=Mock(return_value=[("table1",), ("table2",)])),  # tables
        ]
        
        stats = mixin.get_database_stats()
        assert stats["page_size"] == 4096
        assert stats["total_pages"] == 1000
        assert stats["free_pages"] == 50
        assert stats["table_count"] == 2
        
    def test_compact_database(self):
        """Test database compaction"""
        from scitex.db._SQLite3Mixins import _MaintenanceMixin
        
        mixin = _MaintenanceMixin()
        mixin.vacuum = Mock()
        mixin.analyze = Mock()
        mixin.optimize = Mock()
        
        mixin.compact_database()
        mixin.vacuum.assert_called_once()
        mixin.analyze.assert_called_once()
        mixin.optimize.assert_called_once()
        
    def test_auto_vacuum_settings(self):
        """Test auto-vacuum configuration"""
        from scitex.db._SQLite3Mixins import _MaintenanceMixin
        
        mixin = _MaintenanceMixin()
        mixin.execute = Mock()
        
        # Enable auto-vacuum
        mixin.set_auto_vacuum(1)
        mixin.execute.assert_called_with("PRAGMA auto_vacuum = 1")
        
    def test_checkpoint_wal(self):
        """Test WAL checkpoint operation"""
        from scitex.db._SQLite3Mixins import _MaintenanceMixin
        
        mixin = _MaintenanceMixin()
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = (0, 10, 10)  # busy, log, checkpointed
        mixin.execute = Mock(return_value=mock_cursor)
        
        result = mixin.checkpoint_wal()
        assert result["busy"] == 0
        assert result["checkpointed"] == 10
        mixin.execute.assert_called_with("PRAGMA wal_checkpoint(TRUNCATE)")


def main():
    """Run the tests"""
    pytest.main([__file__, "-v"])


if __name__ == "__main__":
    main()
