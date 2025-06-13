#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 17:00:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/io/_load_modules/test__db.py

"""Comprehensive tests for SQLite3 database loading functionality."""

import os
import tempfile
import pytest
import sqlite3
from unittest.mock import patch, MagicMock


class TestLoadSQLite3DB:
    """Test suite for _load_sqlite3db function"""
    
    def test_valid_extension_check(self):
        """Test that function validates .db extension"""
from scitex.io._load_modules import _load_sqlite3db
        
        # Test invalid extensions
        invalid_files = ["file.txt", "data.sql", "database.sqlite", "test.xlsx"]
        
        for invalid_file in invalid_files:
            with pytest.raises(ValueError, match="File must have .db extension"):
                _load_sqlite3db(invalid_file)
    
    @patch('scitex.io._load_modules._db.SQLite3')
    def test_sqlite3_object_creation_default_params(self, mock_sqlite3):
        """Test that SQLite3 object is created with correct default parameters"""
from scitex.io._load_modules import _load_sqlite3db
        
        mock_db = MagicMock()
        mock_sqlite3.return_value = mock_db
        
        # Call function with default parameters
        result = _load_sqlite3db('test_database.db')
        
        # Verify SQLite3 was called correctly
        mock_sqlite3.assert_called_once_with('test_database.db', use_temp=False)
        assert result == mock_db
    
    @patch('scitex.io._load_modules._db.SQLite3')
    def test_sqlite3_object_creation_with_use_temp(self, mock_sqlite3):
        """Test SQLite3 object creation with use_temp parameter"""
from scitex.io._load_modules import _load_sqlite3db
        
        mock_db = MagicMock()
        mock_sqlite3.return_value = mock_db
        
        # Test with use_temp=True
        result = _load_sqlite3db('temp_database.db', use_temp=True)
        
        mock_sqlite3.assert_called_once_with('temp_database.db', use_temp=True)
        assert result == mock_db
        
        # Reset mock and test with use_temp=False
        mock_sqlite3.reset_mock()
        result = _load_sqlite3db('persistent_database.db', use_temp=False)
        
        mock_sqlite3.assert_called_once_with('persistent_database.db', use_temp=False)
        assert result == mock_db
    
    @patch('scitex.io._load_modules._db.SQLite3')
    def test_sqlite3_exception_handling(self, mock_sqlite3):
        """Test that SQLite3 exceptions are caught and re-raised as ValueError"""
from scitex.io._load_modules import _load_sqlite3db
        
        # Test file not found error
        mock_sqlite3.side_effect = FileNotFoundError("Database file not found")
        
        with pytest.raises(ValueError, match="Database file not found"):
            _load_sqlite3db('nonexistent.db')
        
        # Test permission error
        mock_sqlite3.side_effect = PermissionError("Permission denied")
        
        with pytest.raises(ValueError, match="Permission denied"):
            _load_sqlite3db('protected.db')
        
        # Test database corruption error
        mock_sqlite3.side_effect = sqlite3.DatabaseError("Database is corrupted")
        
        with pytest.raises(ValueError, match="Database is corrupted"):
            _load_sqlite3db('corrupted.db')
    
    @patch('scitex.io._load_modules._db.SQLite3')
    def test_return_type_verification(self, mock_sqlite3):
        """Test that function returns the SQLite3 object"""
from scitex.io._load_modules import _load_sqlite3db
        
        mock_db = MagicMock()
        mock_db.__class__.__name__ = 'SQLite3'
        mock_sqlite3.return_value = mock_db
        
        result = _load_sqlite3db('test.db')
        
        assert result is mock_db
        assert result.__class__.__name__ == 'SQLite3'
    
    def test_function_signature(self):
        """Test function signature and type annotations"""
from scitex.io._load_modules import _load_sqlite3db
        import inspect
        
        sig = inspect.signature(_load_sqlite3db)
        
        # Check parameters
        assert 'lpath' in sig.parameters
        assert 'use_temp' in sig.parameters
        
        # Check default value for use_temp
        assert sig.parameters['use_temp'].default == False
        
        # Check return annotation
        assert sig.return_annotation != inspect.Signature.empty
    
    @patch('scitex.io._load_modules._db.SQLite3')
    def test_absolute_path_handling(self, mock_sqlite3):
        """Test handling of absolute paths"""
from scitex.io._load_modules import _load_sqlite3db
        
        mock_db = MagicMock()
        mock_sqlite3.return_value = mock_db
        
        # Test with absolute path
        abs_path = '/home/user/databases/my_database.db'
        result = _load_sqlite3db(abs_path)
        
        mock_sqlite3.assert_called_once_with(abs_path, use_temp=False)
        assert result == mock_db
    
    @patch('scitex.io._load_modules._db.SQLite3')
    def test_relative_path_handling(self, mock_sqlite3):
        """Test handling of relative paths"""
from scitex.io._load_modules import _load_sqlite3db
        
        mock_db = MagicMock()
        mock_sqlite3.return_value = mock_db
        
        # Test with relative path
        rel_path = './data/local_database.db'
        result = _load_sqlite3db(rel_path)
        
        mock_sqlite3.assert_called_once_with(rel_path, use_temp=False)
        assert result == mock_db
    
    @patch('scitex.io._load_modules._db.SQLite3')
    def test_special_database_names(self, mock_sqlite3):
        """Test handling of special database names"""
from scitex.io._load_modules import _load_sqlite3db
        
        mock_db = MagicMock()
        mock_sqlite3.return_value = mock_db
        
        # Test special database names
        special_names = [
            'database-with-hyphens.db',
            'database_with_underscores.db',
            'database with spaces.db',
            'database123.db',
            'UPPERCASE.db',
            'database.backup.db'
        ]
        
        for db_name in special_names:
            mock_sqlite3.reset_mock()
            result = _load_sqlite3db(db_name)
            
            mock_sqlite3.assert_called_once_with(db_name, use_temp=False)
            assert result == mock_db
    
    def test_real_world_database_scenario(self):
        """Test with actual temporary SQLite database"""
from scitex.io._load_modules import _load_sqlite3db
        
        # Create a temporary database file
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            temp_db_path = f.name
        
        try:
            # Create and populate the database
            conn = sqlite3.connect(temp_db_path)
            cursor = conn.cursor()
            
            # Create tables and insert test data
            cursor.execute('''
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL
                )
            ''')
            cursor.execute('''
                CREATE TABLE posts (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    title TEXT NOT NULL,
                    content TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Insert test data
            cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", 
                          ("John Doe", "john@example.com"))
            cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", 
                          ("Jane Smith", "jane@example.com"))
            cursor.execute("INSERT INTO posts (user_id, title, content) VALUES (?, ?, ?)", 
                          (1, "First Post", "This is my first post"))
            
            conn.commit()
            conn.close()
            
            # Test loading the database
            db_obj = _load_sqlite3db(temp_db_path)
            
            # Verify the object is returned (we can't test internal structure without knowing SQLite3 class)
            assert db_obj is not None
            
        finally:
            # Clean up
            if os.path.exists(temp_db_path):
                os.unlink(temp_db_path)
    
    @patch('scitex.io._load_modules._db.SQLite3')
    def test_use_temp_parameter_variations(self, mock_sqlite3):
        """Test various values for use_temp parameter"""
from scitex.io._load_modules import _load_sqlite3db
        
        mock_db = MagicMock()
        mock_sqlite3.return_value = mock_db
        
        # Test boolean values
        for use_temp_value in [True, False]:
            mock_sqlite3.reset_mock()
            result = _load_sqlite3db('test.db', use_temp=use_temp_value)
            
            mock_sqlite3.assert_called_once_with('test.db', use_temp=use_temp_value)
            assert result == mock_db
    
    @patch('scitex.io._load_modules._db.SQLite3')
    def test_memory_database_handling(self, mock_sqlite3):
        """Test handling of in-memory database paths"""
from scitex.io._load_modules import _load_sqlite3db
        
        # In-memory databases don't have .db extension, so should raise ValueError
        with pytest.raises(ValueError, match="File must have .db extension"):
            _load_sqlite3db(':memory:')
    
    @patch('scitex.io._load_modules._db.SQLite3')
    def test_concurrent_database_access(self, mock_sqlite3):
        """Test multiple simultaneous database connections"""
from scitex.io._load_modules import _load_sqlite3db
        
        # Create multiple mock database objects
        mock_db1 = MagicMock()
        mock_db2 = MagicMock()
        mock_sqlite3.side_effect = [mock_db1, mock_db2]
        
        # Load same database twice
        result1 = _load_sqlite3db('shared.db')
        result2 = _load_sqlite3db('shared.db')
        
        assert result1 is mock_db1
        assert result2 is mock_db2
        assert mock_sqlite3.call_count == 2
    
    @patch('scitex.io._load_modules._db.SQLite3')
    def test_exception_message_preservation(self, mock_sqlite3):
        """Test that original exception messages are preserved"""
from scitex.io._load_modules import _load_sqlite3db
        
        original_message = "Custom database initialization error"
        mock_sqlite3.side_effect = RuntimeError(original_message)
        
        with pytest.raises(ValueError, match=original_message):
            _load_sqlite3db('test.db')
    
    def test_case_sensitive_extension_check(self):
        """Test case sensitivity of .db extension"""
from scitex.io._load_modules import _load_sqlite3db
        
        # Test case variations that should fail
        case_variations = ["file.DB", "file.Db", "file.dB", "file.db.TXT"]
        
        for variant in case_variations:
            if not variant.endswith('.db'):  # Only test non-.db extensions
                with pytest.raises(ValueError, match="File must have .db extension"):
                    _load_sqlite3db(variant)
    
    @patch('scitex.io._load_modules._db.SQLite3')
    def test_empty_string_handling(self, mock_sqlite3):
        """Test handling of empty and invalid path strings"""
from scitex.io._load_modules import _load_sqlite3db
        
        # Test empty string
        with pytest.raises(ValueError, match="File must have .db extension"):
            _load_sqlite3db('')
        
        # Test None (should raise TypeError before our validation)
        with pytest.raises(AttributeError):
            _load_sqlite3db(None)
    
    @patch('scitex.io._load_modules._db.SQLite3')
    def test_long_path_handling(self, mock_sqlite3):
        """Test handling of very long file paths"""
from scitex.io._load_modules import _load_sqlite3db
        
        mock_db = MagicMock()
        mock_sqlite3.return_value = mock_db
        
        # Create a very long path that ends with .db
        long_path = '/'.join(['very_long_directory_name'] * 10) + '/database.db'
        
        result = _load_sqlite3db(long_path)
        
        mock_sqlite3.assert_called_once_with(long_path, use_temp=False)
        assert result == mock_db


if __name__ == "__main__":
    import os
    import pytest
    
    pytest.main([os.path.abspath(__file__), "-v"])
