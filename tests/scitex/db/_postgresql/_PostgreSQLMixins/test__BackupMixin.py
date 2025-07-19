#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-12-01 10:40:00 (ywatanabe)"
# File: tests/scitex/db/_PostgreSQLMixins/test__BackupMixin.py

"""
Comprehensive tests for PostgreSQL BackupMixin.
Testing PostgreSQL-specific backup/restore functionality using pg_dump/pg_restore.
"""

import pytest
import subprocess
import os
from unittest.mock import MagicMock, patch, call
from scitex.db._PostgreSQLMixins import _BackupMixin


class TestPostgreSQLBackupMixin:
    """Test suite for PostgreSQL BackupMixin."""

    @pytest.fixture
    def mock_connection(self):
        """Mock PostgreSQL connection."""
        mock_conn = MagicMock()
        mock_conn.get_dsn_parameters.return_value = {
            "host": "localhost",
            "port": "5432",
            "user": "testuser",
            "password": "testpass",
            "dbname": "testdb"
        }
        return mock_conn

    @pytest.fixture
    def mixin(self, mock_connection):
        """Create BackupMixin instance with mocked connection."""
        mixin = _BackupMixin()
        mixin.conn = mock_connection
        mixin.cursor = MagicMock()
        mixin.execute = MagicMock()
        mixin._check_writable = MagicMock()
        return mixin

    def test_get_connection_params(self, mixin):
        """Test extraction of connection parameters."""
        params = mixin._get_connection_params()
        
        assert params == {
            "host": "localhost",
            "port": "5432",
            "user": "testuser",
            "password": "testpass",
            "database": "testdb"
        }

    def test_backup_table_success(self, mixin):
        """Test successful table backup using pg_dump."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            
            # Backup table
            mixin.backup_table("users", "/tmp/users_backup.sql")
            
            # Verify pg_dump command
            expected_cmd = [
                "pg_dump",
                "-h", "localhost",
                "-p", "5432",
                "-U", "testuser",
                "-d", "testdb",
                "-t", "users",
                "-f", "/tmp/users_backup.sql"
            ]
            
            mock_run.assert_called_once()
            actual_cmd = mock_run.call_args[0][0]
            assert actual_cmd == expected_cmd
            
            # Verify PGPASSWORD is set
            env = mock_run.call_args[1]['env']
            assert env['PGPASSWORD'] == 'testpass'

    def test_backup_table_failure(self, mixin):
        """Test table backup failure handling."""
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = subprocess.CalledProcessError(
                1, "pg_dump", stderr=b"Permission denied"
            )
            
            with pytest.raises(Exception, match="Backup failed: Permission denied"):
                mixin.backup_table("users", "/tmp/users_backup.sql")

    def test_restore_table_success(self, mixin):
        """Test successful table restore using psql."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            
            # Restore table
            mixin.restore_table("users", "/tmp/users_backup.sql")
            
            # Verify psql command
            expected_cmd = [
                "psql",
                "-h", "localhost",
                "-p", "5432",
                "-U", "testuser",
                "-d", "testdb",
                "-f", "/tmp/users_backup.sql"
            ]
            
            mock_run.assert_called_once()
            actual_cmd = mock_run.call_args[0][0]
            assert actual_cmd == expected_cmd
            
            # Verify _check_writable was called
            mixin._check_writable.assert_called_once()

    def test_restore_table_failure(self, mixin):
        """Test table restore failure handling."""
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = subprocess.CalledProcessError(
                1, "psql", stderr=b"Syntax error"
            )
            
            with pytest.raises(Exception, match="Restore failed: Syntax error"):
                mixin.restore_table("users", "/tmp/users_backup.sql")

    def test_backup_database_success(self, mixin):
        """Test successful database backup with custom format."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            
            # Backup database
            mixin.backup_database("/tmp/database_backup.dump")
            
            # Verify pg_dump command with custom format
            expected_cmd = [
                "pg_dump",
                "-h", "localhost",
                "-p", "5432",
                "-U", "testuser",
                "-d", "testdb",
                "-F", "c",  # Custom format
                "-f", "/tmp/database_backup.dump"
            ]
            
            mock_run.assert_called_once()
            actual_cmd = mock_run.call_args[0][0]
            assert actual_cmd == expected_cmd

    def test_backup_database_failure(self, mixin):
        """Test database backup failure handling."""
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = subprocess.CalledProcessError(
                1, "pg_dump", stderr=b"Out of disk space"
            )
            
            with pytest.raises(Exception, match="Database backup failed: Out of disk space"):
                mixin.backup_database("/tmp/database_backup.dump")

    def test_restore_database_success(self, mixin):
        """Test successful database restore with clean option."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            
            # Restore database
            mixin.restore_database("/tmp/database_backup.dump")
            
            # Verify pg_restore command with clean option
            expected_cmd = [
                "pg_restore",
                "-h", "localhost",
                "-p", "5432",
                "-U", "testuser",
                "-d", "testdb",
                "--clean",  # Clean before restore
                "/tmp/database_backup.dump"
            ]
            
            mock_run.assert_called_once()
            actual_cmd = mock_run.call_args[0][0]
            assert actual_cmd == expected_cmd
            
            # Verify _check_writable was called
            mixin._check_writable.assert_called_once()

    def test_restore_database_failure(self, mixin):
        """Test database restore failure handling."""
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = subprocess.CalledProcessError(
                1, "pg_restore", stderr=b"Invalid archive format"
            )
            
            with pytest.raises(Exception, match="Database restore failed: Invalid archive format"):
                mixin.restore_database("/tmp/database_backup.dump")

    def test_copy_table_success(self, mixin):
        """Test successful table copying."""
        # Mock column fetch
        mixin.cursor.fetchall.return_value = [
            ("id",), ("name",), ("email",), ("created_at",)
        ]
        
        # Copy table
        mixin.copy_table("users", "users_backup")
        
        # Verify column query
        column_query_call = mixin.execute.call_args_list[0]
        assert "information_schema.columns" in column_query_call[0][0]
        assert column_query_call[0][1] == ("users",)
        
        # Verify table creation
        create_call = mixin.execute.call_args_list[1]
        assert "CREATE TABLE IF NOT EXISTS users_backup" in create_call[0][0]
        assert "SELECT * FROM users WHERE 1=0" in create_call[0][0]
        
        # Verify data copy
        copy_call = mixin.execute.call_args_list[2]
        expected_query = (
            "INSERT INTO users_backup (id, name, email, created_at) "
            "SELECT id, name, email, created_at FROM users"
        )
        assert copy_call[0][0] == expected_query
        
        # Verify _check_writable was called
        mixin._check_writable.assert_called_once()

    def test_copy_table_with_where_clause(self, mixin):
        """Test table copying with WHERE clause."""
        # Mock column fetch
        mixin.cursor.fetchall.return_value = [("id",), ("status",)]
        
        # Copy table with condition
        mixin.copy_table("orders", "archived_orders", where="status = 'completed'")
        
        # Verify data copy with WHERE clause
        copy_call = mixin.execute.call_args_list[2]
        expected_query = (
            "INSERT INTO archived_orders (id, status) "
            "SELECT id, status FROM orders WHERE status = 'completed'"
        )
        assert copy_call[0][0] == expected_query

    def test_environment_password_handling(self, mixin):
        """Test that password is properly set in environment."""
        with patch('subprocess.run') as mock_run:
            with patch.dict(os.environ, {}, clear=True):
                mock_run.return_value = MagicMock(returncode=0)
                
                # Execute backup
                mixin.backup_table("test_table", "/tmp/test.sql")
                
                # Verify environment has PGPASSWORD
                env = mock_run.call_args[1]['env']
                assert 'PGPASSWORD' in env
                assert env['PGPASSWORD'] == 'testpass'

    def test_subprocess_parameters(self, mixin):
        """Test subprocess.run is called with correct parameters."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            
            # Execute backup
            mixin.backup_table("test_table", "/tmp/test.sql")
            
            # Verify subprocess parameters
            assert mock_run.call_args[1]['check'] is True
            assert mock_run.call_args[1]['capture_output'] is True

    def test_different_connection_parameters(self, mixin):
        """Test with different connection parameters."""
        # Change connection parameters
        mixin.conn.get_dsn_parameters.return_value = {
            "host": "remote.db.com",
            "port": "5433",
            "user": "admin",
            "password": "secret123",
            "dbname": "production"
        }
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            
            # Backup table
            mixin.backup_table("products", "/backup/products.sql")
            
            # Verify command uses new parameters
            expected_cmd = [
                "pg_dump",
                "-h", "remote.db.com",
                "-p", "5433",
                "-U", "admin",
                "-d", "production",
                "-t", "products",
                "-f", "/backup/products.sql"
            ]
            
            actual_cmd = mock_run.call_args[0][0]
            assert actual_cmd == expected_cmd
            
            # Verify password
            env = mock_run.call_args[1]['env']
            assert env['PGPASSWORD'] == 'secret123'

    def test_missing_connection_parameters(self, mixin):
        """Test handling of missing connection parameters."""
        # Return incomplete DSN parameters
        mixin.conn.get_dsn_parameters.return_value = {
            "dbname": "testdb"
        }
        
        params = mixin._get_connection_params()
        
        # Should use defaults
        assert params["host"] == "localhost"
        assert params["port"] == 5432
        assert params["user"] == ""
        assert params["password"] == ""
        assert params["database"] == "testdb"

    def test_stderr_decoding(self, mixin):
        """Test proper decoding of stderr messages."""
        with patch('subprocess.run') as mock_run:
            # Test with Unicode error message
            mock_run.side_effect = subprocess.CalledProcessError(
                1, "pg_dump", stderr="Erreur: accès refusé".encode('utf-8')
            )
            
            with pytest.raises(Exception, match="Backup failed: Erreur: accès refusé"):
                mixin.backup_table("test", "/tmp/test.sql")


# --------------------------------------------------------------------------------

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/_scitex_repo/src/scitex/db/_PostgreSQLMixins/_BackupMixin.py
# --------------------------------------------------------------------------------
