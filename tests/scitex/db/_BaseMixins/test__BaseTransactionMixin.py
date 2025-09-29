#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-12-01 10:40:00 (ywatanabe)"
# File: tests/scitex/db/_BaseMixins/test__BaseTransactionMixin.py

"""
Comprehensive tests for BaseTransactionMixin abstract base class.
Testing transaction management, context managers, and writable state.
"""

import contextlib
from unittest.mock import MagicMock, patch, call
import pytest
from scitex.db._BaseMixins import _BaseTransactionMixin


class ConcreteTransactionMixin(_BaseTransactionMixin):
    """Concrete implementation for testing."""
    
    def __init__(self):
        self._writable = True
        self._in_transaction = False
        self.begin_count = 0
        self.commit_count = 0
        self.rollback_count = 0
        self.foreign_keys_enabled = True
        
    def begin(self):
        if self._in_transaction:
            raise RuntimeError("Already in transaction")
        self._in_transaction = True
        self.begin_count += 1
        
    def commit(self):
        if not self._in_transaction:
            raise RuntimeError("Not in transaction")
        self._in_transaction = False
        self.commit_count += 1
        
    def rollback(self):
        if not self._in_transaction:
            raise RuntimeError("Not in transaction")
        self._in_transaction = False
        self.rollback_count += 1
        
    def enable_foreign_keys(self):
        self.foreign_keys_enabled = True
        
    def disable_foreign_keys(self):
        self.foreign_keys_enabled = False
        
    @property
    def writable(self):
        return self._writable
        
    @writable.setter
    def writable(self, state: bool):
        self._writable = state


class TestBaseTransactionMixin:
    """Test suite for BaseTransactionMixin class."""

    def test_abstract_methods_not_implemented(self):
        """Test that abstract methods raise NotImplementedError."""
        mixin = _BaseTransactionMixin()
        
        # Test each abstract method
        with pytest.raises(NotImplementedError):
            mixin.begin()
            
        with pytest.raises(NotImplementedError):
            mixin.commit()
            
        with pytest.raises(NotImplementedError):
            mixin.rollback()
            
        with pytest.raises(NotImplementedError):
            mixin.enable_foreign_keys()
            
        with pytest.raises(NotImplementedError):
            mixin.disable_foreign_keys()
            
        with pytest.raises(NotImplementedError):
            _ = mixin.writable
            
        with pytest.raises(NotImplementedError):
            mixin.writable = True

    def test_transaction_context_manager_success(self):
        """Test successful transaction using context manager."""
        mixin = ConcreteTransactionMixin()
        
        # Use transaction context
        with mixin.transaction():
            assert mixin._in_transaction is True
            assert mixin.begin_count == 1
            # Do some work here
            
        # After context, transaction should be committed
        assert mixin._in_transaction is False
        assert mixin.commit_count == 1
        assert mixin.rollback_count == 0

    def test_transaction_context_manager_failure(self):
        """Test transaction rollback on exception."""
        mixin = ConcreteTransactionMixin()
        
        # Use transaction context with exception
        with pytest.raises(ValueError):
            with mixin.transaction():
                assert mixin._in_transaction is True
                assert mixin.begin_count == 1
                # Simulate error
                raise ValueError("Test error")
                
        # After context, transaction should be rolled back
        assert mixin._in_transaction is False
        assert mixin.commit_count == 0
        assert mixin.rollback_count == 1

    def test_nested_transactions_error(self):
        """Test that nested transactions raise error."""
        mixin = ConcreteTransactionMixin()
        
        with pytest.raises(RuntimeError, match="Already in transaction"):
            with mixin.transaction():
                # Try to start another transaction
                with mixin.transaction():
                    pass

    def test_manual_transaction_control(self):
        """Test manual begin/commit/rollback."""
        mixin = ConcreteTransactionMixin()
        
        # Begin transaction
        mixin.begin()
        assert mixin._in_transaction is True
        
        # Commit transaction
        mixin.commit()
        assert mixin._in_transaction is False
        
        # Begin another transaction
        mixin.begin()
        assert mixin._in_transaction is True
        
        # Rollback transaction
        mixin.rollback()
        assert mixin._in_transaction is False

    def test_commit_without_begin(self):
        """Test committing without beginning transaction."""
        mixin = ConcreteTransactionMixin()
        
        with pytest.raises(RuntimeError, match="Not in transaction"):
            mixin.commit()

    def test_rollback_without_begin(self):
        """Test rolling back without beginning transaction."""
        mixin = ConcreteTransactionMixin()
        
        with pytest.raises(RuntimeError, match="Not in transaction"):
            mixin.rollback()

    def test_foreign_key_control(self):
        """Test enabling/disabling foreign keys."""
        mixin = ConcreteTransactionMixin()
        
        # Initially enabled
        assert mixin.foreign_keys_enabled is True
        
        # Disable foreign keys
        mixin.disable_foreign_keys()
        assert mixin.foreign_keys_enabled is False
        
        # Enable foreign keys
        mixin.enable_foreign_keys()
        assert mixin.foreign_keys_enabled is True

    def test_writable_property(self):
        """Test writable property getter and setter."""
        mixin = ConcreteTransactionMixin()
        
        # Initially writable
        assert mixin.writable is True
        
        # Set to read-only
        mixin.writable = False
        assert mixin.writable is False
        
        # Set back to writable
        mixin.writable = True
        assert mixin.writable is True

    def test_multiple_transactions(self):
        """Test multiple sequential transactions."""
        mixin = ConcreteTransactionMixin()
        
        # First transaction
        with mixin.transaction():
            pass
        assert mixin.begin_count == 1
        assert mixin.commit_count == 1
        
        # Second transaction
        with mixin.transaction():
            pass
        assert mixin.begin_count == 2
        assert mixin.commit_count == 2
        
        # Third transaction with error
        with pytest.raises(RuntimeError):
            with mixin.transaction():
                raise RuntimeError("Test error")
        assert mixin.begin_count == 3
        assert mixin.commit_count == 2  # No new commit
        assert mixin.rollback_count == 1

    def test_transaction_preserves_exception(self):
        """Test that transaction context preserves original exception."""
        mixin = ConcreteTransactionMixin()
        
        class CustomError(Exception):
            pass
        
        # Verify the original exception is raised
        with pytest.raises(CustomError, match="Original error"):
            with mixin.transaction():
                raise CustomError("Original error")

    def test_transaction_with_mock(self):
        """Test transaction using mocks."""
        mixin = ConcreteTransactionMixin()
        
        # Mock the methods
        mixin.begin = MagicMock()
        mixin.commit = MagicMock()
        mixin.rollback = MagicMock()
        
        # Successful transaction
        with mixin.transaction():
            pass
            
        mixin.begin.assert_called_once()
        mixin.commit.assert_called_once()
        mixin.rollback.assert_not_called()
        
        # Reset mocks
        mixin.begin.reset_mock()
        mixin.commit.reset_mock()
        mixin.rollback.reset_mock()
        
        # Failed transaction
        with pytest.raises(Exception):
            with mixin.transaction():
                raise Exception("Test")
                
        mixin.begin.assert_called_once()
        mixin.commit.assert_not_called()
        mixin.rollback.assert_called_once()

    def test_complex_transaction_scenario(self):
        """Test complex transaction scenario with multiple operations."""
        mixin = ConcreteTransactionMixin()
        
        # Simulate database operations
        operations_performed = []
        
        try:
            with mixin.transaction():
                operations_performed.append("insert_user")
                operations_performed.append("update_profile")
                operations_performed.append("add_permissions")
                # All operations successful
        except Exception:
            operations_performed.append("rollback_all")
            
        # Verify all operations were performed and committed
        assert len(operations_performed) == 3
        assert mixin.commit_count == 1
        assert mixin.rollback_count == 0

    def test_transaction_state_consistency(self):
        """Test that transaction state remains consistent."""
        mixin = ConcreteTransactionMixin()
        
        # Multiple successful transactions
        for i in range(5):
            with mixin.transaction():
                assert mixin._in_transaction is True
            assert mixin._in_transaction is False
            
        # Multiple failed transactions
        for i in range(5):
            with pytest.raises(ValueError):
                with mixin.transaction():
                    assert mixin._in_transaction is True
                    raise ValueError("Test")
            assert mixin._in_transaction is False
            
        # Verify counts
        assert mixin.begin_count == 10
        assert mixin.commit_count == 5
        assert mixin.rollback_count == 5


# --------------------------------------------------------------------------------

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/db/_BaseMixins/_BaseTransactionMixin.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-24 22:08:33 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/db/_Basemodules/_BaseTransactionMixin.py
# 
# THIS_FILE = (
#     "/home/ywatanabe/proj/scitex_repo/src/scitex/db/_Basemodules/_BaseTransactionMixin.py"
# )
# 
# 
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# 
# import contextlib
# 
# 
# class _BaseTransactionMixin:
#     @contextlib.contextmanager
#     def transaction(self):
#         try:
#             self.begin()
#             yield
#             self.commit()
#         except Exception as e:
#             self.rollback()
#             raise e
# 
#     def begin(self):
#         raise NotImplementedError
# 
#     def commit(self):
#         raise NotImplementedError
# 
#     def rollback(self):
#         raise NotImplementedError
# 
#     def enable_foreign_keys(self):
#         raise NotImplementedError
# 
#     def disable_foreign_keys(self):
#         raise NotImplementedError
# 
#     @property
#     def writable(self):
#         raise NotImplementedError
# 
#     @writable.setter
#     def writable(self, state: bool):
#         raise NotImplementedError
# 
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/db/_BaseMixins/_BaseTransactionMixin.py
# --------------------------------------------------------------------------------
