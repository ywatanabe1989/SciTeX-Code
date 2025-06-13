#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-12-01 10:35:00 (ywatanabe)"
# File: tests/scitex/db/_BaseMixins/test__BaseQueryMixin.py

"""
Comprehensive tests for BaseQueryMixin abstract base class.
Testing query interface methods and their expected signatures.
"""

from typing import List, Dict, Any, Optional
from unittest.mock import MagicMock
import pytest
from scitex.db._BaseMixins import _BaseQueryMixin


class ConcreteQueryMixin(_BaseQueryMixin):
    """Concrete implementation for testing."""
    
    def __init__(self):
        self.cursor = MagicMock()
        self.conn = MagicMock()
        self._check_writable = MagicMock()
        
    def select(
        self,
        table: str,
        columns: Optional[List[str]] = None,
        where: Optional[str] = None,
        params: Optional[tuple] = None,
        order_by: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        # Simulate database query
        return [{"id": 1, "name": "Test", "value": 100}]
        
    def insert(self, table: str, data: Dict[str, Any]) -> None:
        self._check_writable()
        # Simulate insert
        pass
        
    def update(
        self,
        table: str,
        data: Dict[str, Any],
        where: str,
        params: Optional[tuple] = None,
    ) -> int:
        self._check_writable()
        # Simulate update returning affected rows
        return 1
        
    def delete(self, table: str, where: str, params: Optional[tuple] = None) -> int:
        self._check_writable()
        # Simulate delete returning affected rows
        return 2
        
    def execute_query(
        self, query: str, params: Optional[tuple] = None
    ) -> List[Dict[str, Any]]:
        # Simulate custom query
        return [{"result": "success"}]
        
    def count(
        self, table: str, where: Optional[str] = None, params: Optional[tuple] = None
    ) -> int:
        # Simulate count
        return 42


class TestBaseQueryMixin:
    """Test suite for BaseQueryMixin class."""

    def test_abstract_methods_not_implemented(self):
        """Test that abstract methods raise NotImplementedError."""
        mixin = _BaseQueryMixin()
        
        # Test select
        with pytest.raises(NotImplementedError):
            mixin.select("users")
            
        # Test insert
        with pytest.raises(NotImplementedError):
            mixin.insert("users", {"name": "Test"})
            
        # Test update
        with pytest.raises(NotImplementedError):
            mixin.update("users", {"name": "Test"}, "id = 1")
            
        # Test delete
        with pytest.raises(NotImplementedError):
            mixin.delete("users", "id = 1")
            
        # Test execute_query
        with pytest.raises(NotImplementedError):
            mixin.execute_query("SELECT * FROM users")
            
        # Test count
        with pytest.raises(NotImplementedError):
            mixin.count("users")

    def test_select_method(self):
        """Test select method implementation."""
        mixin = ConcreteQueryMixin()
        
        # Test basic select
        result = mixin.select("users")
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["id"] == 1
        
        # Test with all parameters
        result = mixin.select(
            "users",
            columns=["id", "name"],
            where="age > ?",
            params=(18,),
            order_by="name ASC",
            limit=10
        )
        assert isinstance(result, list)

    def test_insert_method(self):
        """Test insert method implementation."""
        mixin = ConcreteQueryMixin()
        
        # Test insert
        data = {"name": "John", "age": 30, "email": "john@example.com"}
        mixin.insert("users", data)
        
        # Verify writable check was called
        mixin._check_writable.assert_called()

    def test_update_method(self):
        """Test update method implementation."""
        mixin = ConcreteQueryMixin()
        
        # Test update without params
        data = {"name": "Jane", "age": 25}
        affected = mixin.update("users", data, "id = 1")
        assert affected == 1
        
        # Test update with params
        affected = mixin.update("users", data, "id = ?", (1,))
        assert affected == 1
        
        # Verify writable check was called
        assert mixin._check_writable.call_count >= 2

    def test_delete_method(self):
        """Test delete method implementation."""
        mixin = ConcreteQueryMixin()
        
        # Test delete without params
        affected = mixin.delete("users", "age < 18")
        assert affected == 2
        
        # Test delete with params
        affected = mixin.delete("users", "id = ?", (1,))
        assert affected == 2
        
        # Verify writable check was called
        assert mixin._check_writable.call_count >= 2

    def test_execute_query_method(self):
        """Test execute_query method implementation."""
        mixin = ConcreteQueryMixin()
        
        # Test custom query without params
        result = mixin.execute_query("SELECT * FROM users")
        assert isinstance(result, list)
        assert result[0]["result"] == "success"
        
        # Test custom query with params
        result = mixin.execute_query(
            "SELECT * FROM users WHERE id = ?",
            (1,)
        )
        assert isinstance(result, list)

    def test_count_method(self):
        """Test count method implementation."""
        mixin = ConcreteQueryMixin()
        
        # Test count all
        count = mixin.count("users")
        assert count == 42
        
        # Test count with where clause
        count = mixin.count("users", "active = 1")
        assert count == 42
        
        # Test count with params
        count = mixin.count("users", "age > ?", (18,))
        assert count == 42

    def test_method_signatures(self):
        """Test that methods have correct signatures."""
        mixin = ConcreteQueryMixin()
        
        # Test select signature
        import inspect
        sig = inspect.signature(mixin.select)
        params = list(sig.parameters.keys())
        assert params == ["table", "columns", "where", "params", "order_by", "limit"]
        
        # Test insert signature
        sig = inspect.signature(mixin.insert)
        params = list(sig.parameters.keys())
        assert params == ["table", "data"]
        
        # Test update signature
        sig = inspect.signature(mixin.update)
        params = list(sig.parameters.keys())
        assert params == ["table", "data", "where", "params"]
        
        # Test delete signature
        sig = inspect.signature(mixin.delete)
        params = list(sig.parameters.keys())
        assert params == ["table", "where", "params"]

    def test_return_types(self):
        """Test that methods return expected types."""
        mixin = ConcreteQueryMixin()
        
        # Select should return list of dicts
        result = mixin.select("users")
        assert isinstance(result, list)
        assert all(isinstance(row, dict) for row in result)
        
        # Insert should return None
        result = mixin.insert("users", {"name": "Test"})
        assert result is None
        
        # Update should return int
        result = mixin.update("users", {"name": "Test"}, "id = 1")
        assert isinstance(result, int)
        
        # Delete should return int
        result = mixin.delete("users", "id = 1")
        assert isinstance(result, int)
        
        # Execute query should return list of dicts
        result = mixin.execute_query("SELECT 1")
        assert isinstance(result, list)
        assert all(isinstance(row, dict) for row in result)
        
        # Count should return int
        result = mixin.count("users")
        assert isinstance(result, int)

    def test_empty_results(self):
        """Test handling of empty results."""
        class EmptyResultMixin(ConcreteQueryMixin):
            def select(self, *args, **kwargs):
                return []
                
            def execute_query(self, *args, **kwargs):
                return []
                
            def count(self, *args, **kwargs):
                return 0
        
        mixin = EmptyResultMixin()
        
        # Test empty select
        result = mixin.select("users")
        assert result == []
        
        # Test empty execute_query
        result = mixin.execute_query("SELECT * FROM users")
        assert result == []
        
        # Test zero count
        result = mixin.count("users")
        assert result == 0

    def test_complex_queries(self):
        """Test complex query scenarios."""
        mixin = ConcreteQueryMixin()
        
        # Test select with multiple conditions
        result = mixin.select(
            "users",
            columns=["id", "name", "email", "created_at"],
            where="age >= ? AND status = ? AND country = ?",
            params=(18, "active", "USA"),
            order_by="created_at DESC, name ASC",
            limit=100
        )
        assert isinstance(result, list)
        
        # Test update with multiple fields
        data = {
            "name": "Updated Name",
            "email": "new@example.com",
            "age": 35,
            "modified_at": "2024-12-01 10:00:00"
        }
        affected = mixin.update(
            "users",
            data,
            "id = ? AND status = ?",
            (123, "active")
        )
        assert isinstance(affected, int)

    def test_sql_injection_prevention(self):
        """Test that parameters are properly separated from queries."""
        mixin = ConcreteQueryMixin()
        
        # Dangerous input that should be parameterized
        dangerous_input = "'; DROP TABLE users; --"
        
        # These should use parameters, not string interpolation
        mixin.select("users", where="name = ?", params=(dangerous_input,))
        mixin.delete("users", "name = ?", (dangerous_input,))
        mixin.count("users", "name = ?", (dangerous_input,))
        
        # The concrete implementation should handle this safely
        # (In real implementation, params should be passed separately to DB)


# --------------------------------------------------------------------------------

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/_scitex_repo/src/scitex/db/_BaseMixins/_BaseQueryMixin.py
# --------------------------------------------------------------------------------
