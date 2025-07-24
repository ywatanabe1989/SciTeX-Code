#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-12-01 10:30:00 (ywatanabe)"
# File: tests/scitex/db/_BaseMixins/test__BaseConnectionMixin.py

"""
Comprehensive tests for BaseConnectionMixin abstract base class.
Testing initialization, context manager, and abstract method definitions.
"""

import threading
from unittest.mock import MagicMock, patch
import pytest
from scitex.db._BaseMixins import _BaseConnectionMixin


class ConcreteConnectionMixin(_BaseConnectionMixin):
    """Concrete implementation for testing."""
    
    def connect(self):
        self.conn = MagicMock()
        self.cursor = MagicMock()
        
    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        self.cursor = None
        self.conn = None
        
    def reconnect(self):
        self.close()
        self.connect()
        
    def execute(self, query: str, parameters=()):
        return self.cursor.execute(query, parameters)
        
    def executemany(self, query: str, parameters):
        return self.cursor.executemany(query, parameters)


class TestBaseConnectionMixin:
    """Test suite for BaseConnectionMixin class."""

    def test_init(self):
        """Test initialization of BaseConnectionMixin."""
        mixin = ConcreteConnectionMixin()
        
        # Verify attributes
        assert isinstance(mixin.lock, threading.Lock)
        assert isinstance(mixin._maintenance_lock, threading.Lock)
        assert mixin.conn is None
        assert mixin.cursor is None

    def test_context_manager_enter(self):
        """Test context manager __enter__ method."""
        mixin = ConcreteConnectionMixin()
        
        # Enter context
        result = mixin.__enter__()
        
        # Should return self
        assert result is mixin

    def test_context_manager_exit(self):
        """Test context manager __exit__ method."""
        mixin = ConcreteConnectionMixin()
        mixin.connect()
        
        # Mock close method
        with patch.object(mixin, 'close') as mock_close:
            # Exit context
            mixin.__exit__(None, None, None)
            
            # Verify close was called
            mock_close.assert_called_once()

    def test_context_manager_usage(self):
        """Test using the mixin as a context manager."""
        with ConcreteConnectionMixin() as mixin:
            mixin.connect()
            assert mixin.conn is not None
            assert mixin.cursor is not None
        
        # After context, should be closed
        assert mixin.conn is None
        assert mixin.cursor is None

    def test_abstract_methods_not_implemented(self):
        """Test that abstract methods raise NotImplementedError."""
        # Create instance without implementing abstract methods
        mixin = _BaseConnectionMixin()
        
        # Test each abstract method
        with pytest.raises(NotImplementedError):
            mixin.connect()
            
        with pytest.raises(NotImplementedError):
            mixin.close()
            
        with pytest.raises(NotImplementedError):
            mixin.reconnect()
            
        with pytest.raises(NotImplementedError):
            mixin.execute("SELECT 1")
            
        with pytest.raises(NotImplementedError):
            mixin.executemany("INSERT INTO test VALUES (?)", [(1,), (2,)])

    def test_concrete_implementation(self):
        """Test concrete implementation of abstract methods."""
        mixin = ConcreteConnectionMixin()
        
        # Test connect
        mixin.connect()
        assert mixin.conn is not None
        assert mixin.cursor is not None
        
        # Test execute
        mixin.execute("SELECT * FROM users")
        mixin.cursor.execute.assert_called_once_with("SELECT * FROM users", ())
        
        # Test executemany
        params = [(1, "John"), (2, "Jane")]
        mixin.executemany("INSERT INTO users VALUES (?, ?)", params)
        mixin.cursor.executemany.assert_called_once_with(
            "INSERT INTO users VALUES (?, ?)", params
        )
        
        # Test reconnect
        old_conn = mixin.conn
        old_cursor = mixin.cursor
        mixin.reconnect()
        assert mixin.conn != old_conn
        assert mixin.cursor != old_cursor
        
        # Test close
        mixin.close()
        assert mixin.conn is None
        assert mixin.cursor is None

    def test_thread_safety_locks(self):
        """Test that threading locks are properly initialized."""
        mixin = ConcreteConnectionMixin()
        
        # Test acquiring locks
        assert mixin.lock.acquire(blocking=False)
        mixin.lock.release()
        
        assert mixin._maintenance_lock.acquire(blocking=False)
        mixin._maintenance_lock.release()

    def test_multiple_instances(self):
        """Test that multiple instances have separate locks."""
        mixin1 = ConcreteConnectionMixin()
        mixin2 = ConcreteConnectionMixin()
        
        # Locks should be different objects
        assert mixin1.lock is not mixin2.lock
        assert mixin1._maintenance_lock is not mixin2._maintenance_lock

    def test_exception_in_context_manager(self):
        """Test context manager handles exceptions properly."""
        class FailingMixin(ConcreteConnectionMixin):
            def connect(self):
                super().connect()
                raise ValueError("Connection failed")
        
        mixin = FailingMixin()
        
        # Close should still be called even with exception
        with patch.object(mixin, 'close') as mock_close:
            with pytest.raises(ValueError):
                with mixin:
                    mixin.connect()
            
            # Verify close was called
            mock_close.assert_called_once()

    def test_execute_with_parameters(self):
        """Test execute method with parameters."""
        mixin = ConcreteConnectionMixin()
        mixin.connect()
        
        # Execute with parameters
        query = "SELECT * FROM users WHERE id = ?"
        params = (123,)
        mixin.execute(query, params)
        
        # Verify call
        mixin.cursor.execute.assert_called_once_with(query, params)

    def test_executemany_with_empty_params(self):
        """Test executemany with empty parameter list."""
        mixin = ConcreteConnectionMixin()
        mixin.connect()
        
        # Execute with empty params
        mixin.executemany("INSERT INTO test VALUES (?)", [])
        
        # Verify call
        mixin.cursor.executemany.assert_called_once_with(
            "INSERT INTO test VALUES (?)", []
        )


# --------------------------------------------------------------------------------

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/db/_BaseMixins/_BaseConnectionMixin.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-25 06:02:43 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/db/_BaseMixins/_BaseConnectionMixin.py
# 
# THIS_FILE = (
#     "/home/ywatanabe/proj/scitex_repo/src/scitex/db/_BaseMixins/_BaseConnectionMixin.py"
# )
# 
# import threading
# from typing import Optional
# 
# 
# class _BaseConnectionMixin:
#     def __init__(self):
#         self.lock = threading.Lock()
#         self._maintenance_lock = threading.Lock()
#         self.conn = None
#         self.cursor = None
# 
#     def __enter__(self):
#         return self
# 
#     def __exit__(self, exc_type, exc_val, exc_tb):
#         self.close()
# 
#     def connect(self):
#         raise NotImplementedError
# 
#     def close(self):
#         raise NotImplementedError
# 
#     def reconnect(self):
#         raise NotImplementedError
# 
#     def execute(self, query: str, parameters=()) -> None:
#         raise NotImplementedError
# 
#     def executemany(self, query: str, parameters) -> None:
#         raise NotImplementedError
# 
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/db/_BaseMixins/_BaseConnectionMixin.py
# --------------------------------------------------------------------------------
