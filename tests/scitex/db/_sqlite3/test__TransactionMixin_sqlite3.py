#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 14:48:00 (ywatanabe)"
# File: ./tests/scitex/db/_SQLite3Mixins/test__TransactionMixin.py

"""
Functionality:
    * Tests transaction management for SQLite3
    * Validates commit, rollback, and savepoint operations
    * Tests transaction isolation levels
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
from unittest.mock import Mock, patch, call


class TestTransactionMixin:
    """Test cases for _TransactionMixin"""
    
    def test_begin_transaction(self):
        """Test transaction beginning"""
        from scitex.db._SQLite3Mixins import _TransactionMixin
        
        mixin = _TransactionMixin()
        mixin.execute = Mock()
        
        mixin.begin()
        mixin.execute.assert_called_with("BEGIN")
        
    def test_commit_transaction(self):
        """Test transaction commit"""
        from scitex.db._SQLite3Mixins import _TransactionMixin
        
        mixin = _TransactionMixin()
        mixin._connection = Mock()
        
        mixin.commit()
        mixin._connection.commit.assert_called_once()
        
    def test_rollback_transaction(self):
        """Test transaction rollback"""
        from scitex.db._SQLite3Mixins import _TransactionMixin
        
        mixin = _TransactionMixin()
        mixin._connection = Mock()
        
        mixin.rollback()
        mixin._connection.rollback.assert_called_once()
        
    def test_transaction_context_manager(self):
        """Test transaction context manager"""
        from scitex.db._SQLite3Mixins import _TransactionMixin
        
        mixin = _TransactionMixin()
        mixin.begin = Mock()
        mixin.commit = Mock()
        mixin.rollback = Mock()
        
        # Successful transaction
        with mixin.transaction():
            pass
            
        mixin.begin.assert_called_once()
        mixin.commit.assert_called_once()
        mixin.rollback.assert_not_called()
        
    def test_transaction_rollback_on_error(self):
        """Test transaction rollback on error"""
        from scitex.db._SQLite3Mixins import _TransactionMixin
        
        mixin = _TransactionMixin()
        mixin.begin = Mock()
        mixin.commit = Mock()
        mixin.rollback = Mock()
        
        # Transaction with error
        with pytest.raises(ValueError):
            with mixin.transaction():
                raise ValueError("Test error")
                
        mixin.begin.assert_called_once()
        mixin.commit.assert_not_called()
        mixin.rollback.assert_called_once()
        
    def test_savepoint_operations(self):
        """Test savepoint creation and management"""
        from scitex.db._SQLite3Mixins import _TransactionMixin
        
        mixin = _TransactionMixin()
        mixin.execute = Mock()
        
        # Create savepoint
        mixin.savepoint("sp1")
        mixin.execute.assert_called_with("SAVEPOINT sp1")
        
        # Release savepoint
        mixin.release_savepoint("sp1")
        mixin.execute.assert_called_with("RELEASE SAVEPOINT sp1")
        
        # Rollback to savepoint
        mixin.rollback_to_savepoint("sp1")
        mixin.execute.assert_called_with("ROLLBACK TO SAVEPOINT sp1")
        
    def test_nested_transactions(self):
        """Test nested transaction handling"""
        from scitex.db._SQLite3Mixins import _TransactionMixin
        
        mixin = _TransactionMixin()
        mixin.execute = Mock()
        mixin.commit = Mock()
        mixin._transaction_depth = 0
        
        # Nested transactions using savepoints
        with mixin.transaction():
            mixin._transaction_depth = 1
            with mixin.transaction():
                pass
                
        # Should create savepoint for nested transaction
        calls = mixin.execute.call_args_list
        savepoint_calls = [c for c in calls if "SAVEPOINT" in str(c)]
        assert len(savepoint_calls) > 0
        
    def test_isolation_level_setting(self):
        """Test setting transaction isolation level"""
        from scitex.db._SQLite3Mixins import _TransactionMixin
        
        mixin = _TransactionMixin()
        mixin._connection = Mock()
        
        # Set isolation level
        mixin.set_isolation_level("IMMEDIATE")
        assert mixin._connection.isolation_level == "IMMEDIATE"
        
    def test_deferred_transaction(self):
        """Test deferred transaction mode"""
        from scitex.db._SQLite3Mixins import _TransactionMixin
        
        mixin = _TransactionMixin()
        mixin.execute = Mock()
        
        mixin.begin_deferred()
        mixin.execute.assert_called_with("BEGIN DEFERRED")
        
    def test_immediate_transaction(self):
        """Test immediate transaction mode"""
        from scitex.db._SQLite3Mixins import _TransactionMixin
        
        mixin = _TransactionMixin()
        mixin.execute = Mock()
        
        mixin.begin_immediate()
        mixin.execute.assert_called_with("BEGIN IMMEDIATE")
        
    def test_exclusive_transaction(self):
        """Test exclusive transaction mode"""
        from scitex.db._SQLite3Mixins import _TransactionMixin
        
        mixin = _TransactionMixin()
        mixin.execute = Mock()
        
        mixin.begin_exclusive()
        mixin.execute.assert_called_with("BEGIN EXCLUSIVE")
        
    def test_transaction_state(self):
        """Test checking transaction state"""
        from scitex.db._SQLite3Mixins import _TransactionMixin
        
        mixin = _TransactionMixin()
        mixin._connection = Mock()
        
        # Not in transaction
        mixin._connection.in_transaction = False
        assert mixin.in_transaction() is False
        
        # In transaction
        mixin._connection.in_transaction = True
        assert mixin.in_transaction() is True


def main():
    """Run the tests"""
    pytest.main([__file__, "-v"])


if __name__ == "__main__":
    main()
