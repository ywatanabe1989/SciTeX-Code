#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-10 19:15:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/db/_PostgreSQLMixins/test__MaintenanceMixin_comprehensive.py

"""Comprehensive tests for PostgreSQL MaintenanceMixin functionality."""

import contextlib
import os
import threading
from unittest.mock import MagicMock, Mock, call, patch

import pandas as pd
import psycopg2
import pytest


class MockMaintenanceMixin:
    """Mock class that includes MaintenanceMixin for testing."""
    
    def __init__(self):
        from scitex.db._PostgreSQLMixins import _MaintenanceMixin
        # Mock the required attributes
        self._maintenance_lock = threading.Lock()
        self.cursor = MagicMock()
        self.execute = MagicMock()
        self._check_writable = MagicMock()
        self.get_table_names = MagicMock(return_value=['table1', 'table2'])
        
        # Mix in the MaintenanceMixin
        for attr_name in dir(_MaintenanceMixin):
            if not attr_name.startswith('_'):
                setattr(self, attr_name, getattr(_MaintenanceMixin, attr_name).__get__(self, MockMaintenanceMixin))


class TestMaintenanceMixinBasic:
    """Basic functionality tests for MaintenanceMixin."""
    
    def test_import(self):
        """Test that MaintenanceMixin can be imported."""
        from scitex.db._PostgreSQLMixins import _MaintenanceMixin
        assert _MaintenanceMixin is not None
    
    def test_mixin_methods_exist(self):
        """Test that all expected methods exist."""
        mixin = MockMaintenanceMixin()
        
        expected_methods = [
            'maintenance_lock',
            'vacuum',
            'analyze',
            'reindex',
            'get_table_size',
            'get_database_size',
            'get_table_info',
            'optimize',
            'get_summaries'
        ]
        
        for method in expected_methods:
            assert hasattr(mixin, method)
            assert callable(getattr(mixin, method))


class TestMaintenanceLock:
    """Test cases for maintenance_lock context manager."""
    
    def test_maintenance_lock_acquisition(self):
        """Test basic lock acquisition and release."""
        mixin = MockMaintenanceMixin()
        
        with mixin.maintenance_lock():
            # Lock should be held
            assert not mixin._maintenance_lock.acquire(blocking=False)
        
        # Lock should be released
        assert mixin._maintenance_lock.acquire(blocking=False)
        mixin._maintenance_lock.release()
    
    def test_maintenance_lock_timeout(self):
        """Test lock timeout behavior."""
        mixin = MockMaintenanceMixin()
        
        # Mock the lock to simulate timeout
        mock_lock = MagicMock()
        mock_lock.acquire.return_value = False
        mixin._maintenance_lock = mock_lock
        
        with pytest.raises(TimeoutError, match="Could not acquire maintenance lock"):
            with mixin.maintenance_lock():
                pass
    
    def test_maintenance_lock_exception_handling(self):
        """Test that lock is released even on exception."""
        mixin = MockMaintenanceMixin()
        
        try:
            with mixin.maintenance_lock():
                raise ValueError("Test exception")
        except ValueError:
            pass
        
        # Lock should still be released
        assert mixin._maintenance_lock.acquire(blocking=False)
        mixin._maintenance_lock.release()


class TestVacuumMethod:
    """Test cases for vacuum method."""
    
    def test_vacuum_basic(self):
        """Test basic vacuum operation."""
        mixin = MockMaintenanceMixin()
        
        mixin.vacuum()
        
        mixin._check_writable.assert_called_once()
        mixin.execute.assert_called_once_with("VACUUM")
    
    def test_vacuum_with_table(self):
        """Test vacuum on specific table."""
        mixin = MockMaintenanceMixin()
        
        mixin.vacuum(table="test_table")
        
        mixin.execute.assert_called_once_with("VACUUM test_table")
    
    def test_vacuum_full(self):
        """Test full vacuum operation."""
        mixin = MockMaintenanceMixin()
        
        mixin.vacuum(full=True)
        
        mixin.execute.assert_called_once_with("VACUUM FULL")
    
    def test_vacuum_full_with_table(self):
        """Test full vacuum on specific table."""
        mixin = MockMaintenanceMixin()
        
        mixin.vacuum(table="test_table", full=True)
        
        mixin.execute.assert_called_once_with("VACUUM FULL test_table")
    
    def test_vacuum_error_handling(self):
        """Test vacuum error handling."""
        mixin = MockMaintenanceMixin()
        mixin.execute.side_effect = psycopg2.Error("Database error")
        
        with pytest.raises(ValueError, match="Vacuum operation failed"):
            mixin.vacuum()
    
    def test_vacuum_uses_lock(self):
        """Test that vacuum uses maintenance lock."""
        mixin = MockMaintenanceMixin()
        
        # Track lock acquisition
        original_acquire = mixin._maintenance_lock.acquire
        acquire_called = False
        
        def track_acquire(*args, **kwargs):
            nonlocal acquire_called
            acquire_called = True
            return original_acquire(*args, **kwargs)
        
        mixin._maintenance_lock.acquire = track_acquire
        
        mixin.vacuum()
        
        assert acquire_called


class TestAnalyzeMethod:
    """Test cases for analyze method."""
    
    def test_analyze_basic(self):
        """Test basic analyze operation."""
        mixin = MockMaintenanceMixin()
        
        mixin.analyze()
        
        mixin._check_writable.assert_called_once()
        mixin.execute.assert_called_once_with("ANALYZE")
    
    def test_analyze_with_table(self):
        """Test analyze on specific table."""
        mixin = MockMaintenanceMixin()
        
        mixin.analyze(table="test_table")
        
        mixin.execute.assert_called_once_with("ANALYZE test_table")
    
    def test_analyze_error_handling(self):
        """Test analyze error handling."""
        mixin = MockMaintenanceMixin()
        mixin.execute.side_effect = psycopg2.Error("Database error")
        
        with pytest.raises(ValueError, match="Analyze operation failed"):
            mixin.analyze()


class TestReindexMethod:
    """Test cases for reindex method."""
    
    def test_reindex_database(self):
        """Test reindex entire database."""
        mixin = MockMaintenanceMixin()
        
        mixin.reindex()
        
        mixin._check_writable.assert_called_once()
        mixin.execute.assert_called_once_with("REINDEX DATABASE CURRENT_DATABASE()")
    
    def test_reindex_table(self):
        """Test reindex specific table."""
        mixin = MockMaintenanceMixin()
        
        mixin.reindex(table="test_table")
        
        mixin.execute.assert_called_once_with("REINDEX TABLE test_table")
    
    def test_reindex_error_handling(self):
        """Test reindex error handling."""
        mixin = MockMaintenanceMixin()
        mixin.execute.side_effect = psycopg2.Error("Database error")
        
        with pytest.raises(ValueError, match="Reindex operation failed"):
            mixin.reindex()


class TestSizeMethods:
    """Test cases for size-related methods."""
    
    def test_get_table_size(self):
        """Test getting table size."""
        mixin = MockMaintenanceMixin()
        mixin.cursor.fetchone.return_value = ["1.5 MB"]
        
        result = mixin.get_table_size("test_table")
        
        assert result == "1.5 MB"
        mixin.execute.assert_called_once()
        # Check that parameterized query is used
        args = mixin.execute.call_args
        assert "pg_size_pretty" in args[0][0]
        assert args[0][1] == ("test_table",)
    
    def test_get_table_size_error(self):
        """Test table size error handling."""
        mixin = MockMaintenanceMixin()
        mixin.execute.side_effect = psycopg2.Error("Database error")
        
        with pytest.raises(ValueError, match="Failed to get table size"):
            mixin.get_table_size("test_table")
    
    def test_get_database_size(self):
        """Test getting database size."""
        mixin = MockMaintenanceMixin()
        mixin.cursor.fetchone.return_value = ["100 MB"]
        
        result = mixin.get_database_size()
        
        assert result == "100 MB"
        mixin.execute.assert_called_once()
        assert "pg_database_size" in mixin.execute.call_args[0][0]
    
    def test_get_database_size_error(self):
        """Test database size error handling."""
        mixin = MockMaintenanceMixin()
        mixin.execute.side_effect = psycopg2.Error("Database error")
        
        with pytest.raises(ValueError, match="Failed to get database size"):
            mixin.get_database_size()


class TestTableInfo:
    """Test cases for get_table_info method."""
    
    def test_get_table_info(self):
        """Test getting table information."""
        mixin = MockMaintenanceMixin()
        
        # Mock cursor description and results
        mixin.cursor.description = [
            ('table_name',), ('size',), ('columns',), ('has_pk',)
        ]
        mixin.cursor.fetchall.return_value = [
            ('users', '5 MB', 10, 1),
            ('orders', '20 MB', 15, 1),
        ]
        
        result = mixin.get_table_info()
        
        assert len(result) == 2
        assert result[0]['table_name'] == 'users'
        assert result[0]['size'] == '5 MB'
        assert result[0]['columns'] == 10
        assert result[0]['has_pk'] == 1
        
        # Check query contains expected elements
        query = mixin.execute.call_args[0][0]
        assert 'information_schema.tables' in query
        assert 'pg_size_pretty' in query
    
    def test_get_table_info_error(self):
        """Test table info error handling."""
        mixin = MockMaintenanceMixin()
        mixin.execute.side_effect = psycopg2.Error("Database error")
        
        with pytest.raises(ValueError, match="Failed to get table information"):
            mixin.get_table_info()


class TestOptimizeMethod:
    """Test cases for optimize method."""
    
    def test_optimize_all(self):
        """Test full database optimization."""
        mixin = MockMaintenanceMixin()
        
        # Mock the individual methods
        mixin.vacuum = MagicMock()
        mixin.analyze = MagicMock()
        mixin.reindex = MagicMock()
        
        mixin.optimize()
        
        mixin.vacuum.assert_called_once_with(None, full=True)
        mixin.analyze.assert_called_once_with(None)
        mixin.reindex.assert_called_once_with(None)
    
    def test_optimize_table(self):
        """Test table optimization."""
        mixin = MockMaintenanceMixin()
        
        # Mock the individual methods
        mixin.vacuum = MagicMock()
        mixin.analyze = MagicMock()
        mixin.reindex = MagicMock()
        
        mixin.optimize(table="test_table")
        
        mixin.vacuum.assert_called_once_with("test_table", full=True)
        mixin.analyze.assert_called_once_with("test_table")
        mixin.reindex.assert_called_once_with("test_table")
    
    def test_optimize_error_propagation(self):
        """Test that optimize propagates errors."""
        mixin = MockMaintenanceMixin()
        
        # Mock vacuum to raise error
        mixin.vacuum = MagicMock(side_effect=ValueError("Vacuum failed"))
        mixin.analyze = MagicMock()
        mixin.reindex = MagicMock()
        
        with pytest.raises(ValueError, match="Optimization failed"):
            mixin.optimize()


class TestGetSummaries:
    """Test cases for get_summaries method."""
    
    def test_get_summaries_basic(self):
        """Test basic get_summaries functionality."""
        mixin = MockMaintenanceMixin()
        
        # Mock cursor and results
        mixin.cursor.description = [('id',), ('name',), ('created_at',)]
        mixin.cursor.fetchall.return_value = [
            (1, 'John', '2023-01-01'),
            (2, 'Jane', '2023-01-02'),
        ]
        
        result = mixin.get_summaries(limit=2)
        
        assert isinstance(result, dict)
        assert 'table1' in result
        assert 'table2' in result
        assert isinstance(result['table1'], pd.DataFrame)
        assert len(result['table1']) == 2
    
    def test_get_summaries_single_table(self):
        """Test get_summaries with single table."""
        mixin = MockMaintenanceMixin()
        
        mixin.cursor.description = [('id',), ('value',)]
        mixin.cursor.fetchall.return_value = [(1, 100), (2, 200)]
        
        result = mixin.get_summaries(table_names="test_table", limit=2)
        
        assert 'test_table' in result
        assert len(result) == 1
        assert len(result['test_table']) == 2
    
    def test_get_summaries_datetime_detection(self):
        """Test datetime column detection."""
        mixin = MockMaintenanceMixin()
        
        mixin.cursor.description = [('id',), ('timestamp',), ('text',)]
        mixin.cursor.fetchall.return_value = [
            (1, '2023-01-01 12:00:00', 'test'),
            (2, '2023-01-02 13:00:00', 'data'),
        ]
        
        with patch('pandas.to_datetime') as mock_to_datetime:
            # First call succeeds (datetime column)
            # Second call fails (non-datetime column)
            mock_to_datetime.side_effect = [None, ValueError("Not a datetime")]
            
            result = mixin.get_summaries(table_names=['table1'], limit=2)
            
            # Should attempt datetime conversion
            assert mock_to_datetime.called
    
    def test_get_summaries_error_handling(self):
        """Test get_summaries error handling."""
        mixin = MockMaintenanceMixin()
        mixin.execute.side_effect = psycopg2.Error("Database error")
        
        with pytest.raises(ValueError, match="Failed to get summaries"):
            mixin.get_summaries()
    
    def test_get_summaries_limit(self):
        """Test that limit parameter is used."""
        mixin = MockMaintenanceMixin()
        
        mixin.cursor.description = [('id',)]
        mixin.cursor.fetchall.return_value = [(i,) for i in range(10)]
        
        mixin.get_summaries(table_names=['test'], limit=10)
        
        # Check that LIMIT is in the query
        query = mixin.execute.call_args[0][0]
        assert 'LIMIT 10' in query


class TestIntegration:
    """Integration tests for MaintenanceMixin."""
    
    def test_full_workflow(self):
        """Test a complete maintenance workflow."""
        mixin = MockMaintenanceMixin()
        
        # Setup mocks
        mixin.cursor.fetchone.return_value = ["10 MB"]
        mixin.cursor.description = [('table_name',), ('size',)]
        mixin.cursor.fetchall.return_value = [('test_table', '10 MB')]
        
        # Get database size
        db_size = mixin.get_database_size()
        assert db_size == "10 MB"
        
        # Get table info
        tables = mixin.get_table_info()
        assert len(tables) > 0
        
        # Perform maintenance
        mixin.vacuum = MagicMock()
        mixin.analyze = MagicMock()
        mixin.reindex = MagicMock()
        
        mixin.optimize()
        
        assert mixin.vacuum.called
        assert mixin.analyze.called
        assert mixin.reindex.called
    
    def test_concurrent_maintenance_operations(self):
        """Test that concurrent maintenance operations are serialized."""
        mixin = MockMaintenanceMixin()
        
        results = []
        
        def slow_vacuum():
            with mixin.maintenance_lock():
                results.append('start_vacuum')
                import time
                time.sleep(0.1)
                results.append('end_vacuum')
        
        def slow_analyze():
            with mixin.maintenance_lock():
                results.append('start_analyze')
                import time
                time.sleep(0.1)
                results.append('end_analyze')
        
        # Start both operations
        import threading
        t1 = threading.Thread(target=slow_vacuum)
        t2 = threading.Thread(target=slow_analyze)
        
        t1.start()
        t2.start()
        
        t1.join()
        t2.join()
        
        # Operations should not overlap
        assert results.index('end_vacuum') < results.index('start_analyze') or \
               results.index('end_analyze') < results.index('start_vacuum')


class TestErrorScenarios:
    """Test various error scenarios."""
    
    def test_writable_check_failure(self):
        """Test operations when database is not writable."""
        mixin = MockMaintenanceMixin()
        mixin._check_writable.side_effect = Exception("Database is read-only")
        
        with pytest.raises(Exception, match="Database is read-only"):
            mixin.vacuum()
    
    def test_lock_acquisition_failure(self):
        """Test handling of lock acquisition failures."""
        mixin = MockMaintenanceMixin()
        
        # Hold the lock in another "thread"
        mixin._maintenance_lock.acquire()
        
        # Mock timeout behavior
        original_acquire = mixin._maintenance_lock.acquire
        mixin._maintenance_lock.acquire = lambda timeout: False
        
        try:
            with pytest.raises(TimeoutError):
                mixin.vacuum()
        finally:
            # Restore and release
            mixin._maintenance_lock.acquire = original_acquire
            mixin._maintenance_lock.release()
    
    def test_invalid_table_name(self):
        """Test operations with invalid table names."""
        mixin = MockMaintenanceMixin()
        mixin.execute.side_effect = psycopg2.Error("relation does not exist")
        
        with pytest.raises(ValueError, match="Vacuum operation failed"):
            mixin.vacuum(table="nonexistent_table")


class TestDocumentation:
    """Test documentation aspects."""
    
    def test_method_docstrings(self):
        """Test that methods have docstrings."""
        from scitex.db._PostgreSQLMixins import _MaintenanceMixin
        
        methods_to_check = ['vacuum', 'analyze', 'reindex', 
                           'get_table_size', 'get_database_size']
        
        for method_name in methods_to_check:
            method = getattr(_MaintenanceMixin, method_name)
            assert method.__doc__ is not None
            assert len(method.__doc__) > 0


if __name__ == "__main__":
    pytest.main([os.path.abspath(__file__), "-v"])