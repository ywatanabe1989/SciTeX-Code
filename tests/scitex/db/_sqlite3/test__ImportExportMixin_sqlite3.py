#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 14:48:00 (ywatanabe)"
# File: ./tests/scitex/db/_SQLite3Mixins/test__ImportExportMixin.py

"""
Functionality:
    * Tests data import/export functionality for SQLite3
    * Validates CSV, JSON, and SQL dump operations
    * Tests backup and restore functionality
Input:
    * Test database and sample data files
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
import csv
import json
from unittest.mock import Mock, patch, mock_open


class TestImportExportMixin:
    """Test cases for _ImportExportMixin"""
    
    def test_export_to_csv(self):
        """Test CSV export functionality"""
        from scitex.db._SQLite3Mixins import _ImportExportMixin
        
        mixin = _ImportExportMixin()
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [(1, "test", 100), (2, "test2", 200)]
        mock_cursor.description = [("id",), ("name",), ("value",)]
        mixin.execute = Mock(return_value=mock_cursor)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp:
            csv_path = tmp.name
            
        try:
            mixin.export_to_csv("test_table", csv_path)
            
            # Verify CSV content
            with open(csv_path, 'r') as f:
                reader = csv.reader(f)
                rows = list(reader)
                assert len(rows) == 3  # header + 2 data rows
                assert rows[0] == ["id", "name", "value"]
        finally:
            os.unlink(csv_path)
            
    def test_import_from_csv(self):
        """Test CSV import functionality"""
        from scitex.db._SQLite3Mixins import _ImportExportMixin
        
        mixin = _ImportExportMixin()
        mixin.executemany = Mock()
        mixin.transaction = Mock(return_value=Mock(__enter__=Mock(), __exit__=Mock()))
        
        # Create test CSV
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp:
            csv_path = tmp.name
            writer = csv.writer(tmp)
            writer.writerow(["id", "name", "value"])
            writer.writerow([1, "test", 100])
            writer.writerow([2, "test2", 200])
            
        try:
            mixin.import_from_csv("test_table", csv_path)
            mixin.executemany.assert_called()
        finally:
            os.unlink(csv_path)
            
    def test_export_to_json(self):
        """Test JSON export functionality"""
        from scitex.db._SQLite3Mixins import _ImportExportMixin
        
        mixin = _ImportExportMixin()
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [(1, "test", 100), (2, "test2", 200)]
        mock_cursor.description = [("id",), ("name",), ("value",)]
        mixin.execute = Mock(return_value=mock_cursor)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
            json_path = tmp.name
            
        try:
            mixin.export_to_json("test_table", json_path)
            
            # Verify JSON content
            with open(json_path, 'r') as f:
                data = json.load(f)
                assert len(data) == 2
                assert data[0] == {"id": 1, "name": "test", "value": 100}
        finally:
            os.unlink(json_path)
            
    def test_import_from_json(self):
        """Test JSON import functionality"""
        from scitex.db._SQLite3Mixins import _ImportExportMixin
        
        mixin = _ImportExportMixin()
        mixin.insert_many = Mock()
        
        # Create test JSON
        test_data = [
            {"id": 1, "name": "test", "value": 100},
            {"id": 2, "name": "test2", "value": 200}
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
            json_path = tmp.name
            json.dump(test_data, tmp)
            
        try:
            mixin.import_from_json("test_table", json_path)
            mixin.insert_many.assert_called_with("test_table", test_data)
        finally:
            os.unlink(json_path)
            
    def test_dump_sql(self):
        """Test SQL dump functionality"""
        from scitex.db._SQLite3Mixins import _ImportExportMixin
        
        mixin = _ImportExportMixin()
        mixin._connection = Mock()
        mixin._connection.iterdump.return_value = [
            "CREATE TABLE test (id INTEGER PRIMARY KEY);",
            "INSERT INTO test VALUES (1);",
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as tmp:
            sql_path = tmp.name
            
        try:
            mixin.dump_to_sql(sql_path)
            
            with open(sql_path, 'r') as f:
                content = f.read()
                assert "CREATE TABLE" in content
                assert "INSERT INTO" in content
        finally:
            os.unlink(sql_path)
            
    def test_backup_database(self):
        """Test database backup functionality"""
        from scitex.db._SQLite3Mixins import _ImportExportMixin
        
        mixin = _ImportExportMixin()
        mixin._connection = Mock()
        mock_backup = Mock()
        mixin._connection.backup = mock_backup
        
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            backup_path = tmp.name
            
        try:
            with patch('sqlite3.connect') as mock_connect:
                mixin.backup_database(backup_path)
                mock_backup.assert_called()
        finally:
            os.unlink(backup_path)


def main():
    """Run the tests"""
    pytest.main([__file__, "-v"])


if __name__ == "__main__":
    main()
