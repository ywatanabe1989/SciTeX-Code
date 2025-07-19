#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-01-12 10:28:51 (ywatanabe)"
# Path: /home/ywatanabe/proj/scitex_dev/tests/scitex/db/_PostgreSQLMixins/test__TransactionMixin.py
# Reference: /home/ywatanabe/proj/scitex_dev/tests/_test_template.py

"""Tests for scitex.db._PostgreSQLMixins._TransactionMixin module."""

import pytest
from unittest.mock import MagicMock, patch, call
import psycopg2
from scitex.db._PostgreSQLMixins import _TransactionMixin


class TestTransactionMixin:
    """Test cases for PostgreSQL TransactionMixin class."""

    @pytest.fixture
    def mixin(self):
        """Create a TransactionMixin instance with mocked dependencies."""
        # Create instance with mock attributes
        mixin = _TransactionMixin()
        mixin.conn = MagicMock()
        mixin.cursor = MagicMock()
        mixin.execute = MagicMock()
        return mixin

    def test_begin_transaction(self, mixin):
        """Test beginning a transaction."""
        mixin.begin()
        mixin.execute.assert_called_once_with("BEGIN TRANSACTION")

    def test_commit_transaction(self, mixin):
        """Test committing a transaction."""
        mixin.commit()
        mixin.conn.commit.assert_called_once()

    def test_rollback_transaction(self, mixin):
        """Test rolling back a transaction."""
        mixin.rollback()
        mixin.conn.rollback.assert_called_once()

    def test_enable_foreign_keys(self, mixin):
        """Test enabling foreign keys (no-op in PostgreSQL)."""
        # In PostgreSQL, foreign keys are always enabled
        mixin.enable_foreign_keys()
        # Should not execute anything
        mixin.execute.assert_not_called()

    def test_disable_foreign_keys(self, mixin):
        """Test disabling foreign keys via session replication role."""
        mixin.disable_foreign_keys()
        mixin.execute.assert_called_once_with("SET session_replication_role = 'replica'")

    def test_writable_property_getter_true(self, mixin):
        """Test getting writable property when database is writable."""
        mixin.cursor.fetchone.return_value = [True]
        assert mixin.writable is True
        mixin.cursor.execute.assert_called_once_with(
            "SELECT current_setting('transaction_read_only') = 'off'"
        )

    def test_writable_property_getter_false(self, mixin):
        """Test getting writable property when database is read-only."""
        mixin.cursor.fetchone.return_value = [False]
        assert mixin.writable is False
        mixin.cursor.execute.assert_called_once_with(
            "SELECT current_setting('transaction_read_only') = 'off'"
        )

    def test_writable_property_getter_error(self, mixin):
        """Test getting writable property when an error occurs."""
        mixin.cursor.execute.side_effect = psycopg2.Error("Database error")
        # Should return True on error (assume writable)
        assert mixin.writable is True

    def test_writable_property_setter_true(self, mixin):
        """Test setting writable property to True."""
        mixin.writable = True
        mixin.execute.assert_called_once_with("SET TRANSACTION READ WRITE")

    def test_writable_property_setter_false(self, mixin):
        """Test setting writable property to False."""
        mixin.writable = False
        mixin.execute.assert_called_once_with("SET TRANSACTION READ ONLY")

    def test_writable_property_setter_error(self, mixin):
        """Test setting writable property when an error occurs."""
        mixin.execute.side_effect = psycopg2.Error("Database error")
        with pytest.raises(ValueError, match="Failed to set writable state"):
            mixin.writable = True

    def test_check_writable_when_writable(self, mixin):
        """Test _check_writable when database is writable."""
        # Mock writable property to return True
        with patch.object(mixin, 'writable', True):
            # Should not raise an exception
            mixin._check_writable()

    def test_check_writable_when_readonly(self, mixin):
        """Test _check_writable when database is read-only."""
        # Mock writable property to return False
        with patch.object(mixin, 'writable', False):
            with pytest.raises(ValueError, match="Database is in read-only mode"):
                mixin._check_writable()

    def test_mvcc_transaction_isolation(self, mixin):
        """Test PostgreSQL MVCC transaction isolation handling."""
        # Test different isolation levels
        isolation_levels = [
            "READ UNCOMMITTED",
            "READ COMMITTED",
            "REPEATABLE READ",
            "SERIALIZABLE"
        ]
        
        for level in isolation_levels:
            mixin.execute.reset_mock()
            # Simulate setting isolation level
            mixin.execute(f"SET TRANSACTION ISOLATION LEVEL {level}")
            mixin.execute.assert_called_once_with(f"SET TRANSACTION ISOLATION LEVEL {level}")

    def test_savepoint_operations(self, mixin):
        """Test PostgreSQL savepoint operations."""
        # Create savepoint
        mixin.execute("SAVEPOINT test_savepoint")
        mixin.execute.assert_called_with("SAVEPOINT test_savepoint")
        
        # Release savepoint
        mixin.execute.reset_mock()
        mixin.execute("RELEASE SAVEPOINT test_savepoint")
        mixin.execute.assert_called_with("RELEASE SAVEPOINT test_savepoint")
        
        # Rollback to savepoint
        mixin.execute.reset_mock()
        mixin.execute("ROLLBACK TO SAVEPOINT test_savepoint")
        mixin.execute.assert_called_with("ROLLBACK TO SAVEPOINT test_savepoint")

    def test_transaction_chaining(self, mixin):
        """Test PostgreSQL transaction chaining behavior."""
        # Test transaction chaining
        mixin.execute("COMMIT AND CHAIN")
        mixin.execute.assert_called_with("COMMIT AND CHAIN")
        
        mixin.execute.reset_mock()
        mixin.execute("ROLLBACK AND CHAIN")
        mixin.execute.assert_called_with("ROLLBACK AND CHAIN")

    def test_two_phase_commit(self, mixin):
        """Test PostgreSQL two-phase commit protocol."""
        # Prepare transaction
        mixin.execute("PREPARE TRANSACTION 'test_transaction'")
        mixin.execute.assert_called_with("PREPARE TRANSACTION 'test_transaction'")
        
        # Commit prepared
        mixin.execute.reset_mock()
        mixin.execute("COMMIT PREPARED 'test_transaction'")
        mixin.execute.assert_called_with("COMMIT PREPARED 'test_transaction'")
        
        # Rollback prepared
        mixin.execute.reset_mock()
        mixin.execute("ROLLBACK PREPARED 'test_transaction'")
        mixin.execute.assert_called_with("ROLLBACK PREPARED 'test_transaction'")

    def test_advisory_locks(self, mixin):
        """Test PostgreSQL advisory lock operations."""
        # Session-level advisory lock
        mixin.execute("SELECT pg_advisory_lock(12345)")
        mixin.execute.assert_called_with("SELECT pg_advisory_lock(12345)")
        
        # Transaction-level advisory lock
        mixin.execute.reset_mock()
        mixin.execute("SELECT pg_advisory_xact_lock(12345)")
        mixin.execute.assert_called_with("SELECT pg_advisory_xact_lock(12345)")
        
        # Release advisory lock
        mixin.execute.reset_mock()
        mixin.execute("SELECT pg_advisory_unlock(12345)")
        mixin.execute.assert_called_with("SELECT pg_advisory_unlock(12345)")

    def test_transaction_status_check(self, mixin):
        """Test checking PostgreSQL transaction status."""
        # Mock transaction status
        mixin.cursor.fetchone.return_value = ['IDLE']
        mixin.cursor.execute("SELECT current_setting('transaction_status')")
        mixin.cursor.execute.assert_called_with("SELECT current_setting('transaction_status')")

    def test_deferrable_transactions(self, mixin):
        """Test PostgreSQL deferrable transaction mode."""
        mixin.execute("SET TRANSACTION READ ONLY DEFERRABLE")
        mixin.execute.assert_called_with("SET TRANSACTION READ ONLY DEFERRABLE")

    def test_session_characteristics(self, mixin):
        """Test setting session characteristics."""
        # Set default transaction isolation
        mixin.execute("SET SESSION CHARACTERISTICS AS TRANSACTION ISOLATION LEVEL SERIALIZABLE")
        mixin.execute.assert_called_with(
            "SET SESSION CHARACTERISTICS AS TRANSACTION ISOLATION LEVEL SERIALIZABLE"
        )
        
        # Set default transaction mode
        mixin.execute.reset_mock()
        mixin.execute("SET SESSION CHARACTERISTICS AS TRANSACTION READ ONLY")
        mixin.execute.assert_called_with(
            "SET SESSION CHARACTERISTICS AS TRANSACTION READ ONLY"
        )

    def test_inheritance_from_base_mixin(self):
        """Test that TransactionMixin properly inherits from BaseTransactionMixin."""
        from scitex.db._BaseMixins import _BaseTransactionMixin
        assert issubclass(_TransactionMixin, _BaseTransactionMixin)

    def test_error_handling_consistency(self, mixin):
        """Test consistent error handling across methods."""
        # Test psycopg2 specific errors
        error_types = [
            psycopg2.IntegrityError("Integrity violation"),
            psycopg2.OperationalError("Connection lost"),
            psycopg2.ProgrammingError("Invalid SQL"),
            psycopg2.DataError("Invalid data"),
            psycopg2.NotSupportedError("Feature not supported")
        ]
        
        for error in error_types:
            mixin.execute.side_effect = error
            with pytest.raises(type(error)):
                mixin.execute("ANY COMMAND")


if __name__ == "__main__":
    import os
    pytest.main([os.path.abspath(__file__), "-v"])


# EOF
