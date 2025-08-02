#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-12-01 10:45:00 (ywatanabe)"
# File: tests/scitex/db/_BaseMixins/test__BaseTableMixin.py

"""
Comprehensive tests for BaseTableMixin abstract base class.
Testing table operations, schema management, and metadata retrieval.
"""

from typing import Any, Dict, List, Union
from unittest.mock import MagicMock
import pytest
from scitex.db._BaseMixins import _BaseTableMixin


class ConcreteTableMixin(_BaseTableMixin):
    """Concrete implementation for testing."""
    
    def __init__(self):
        self.tables = {}
        self.executed_operations = []
        
    def create_table(
        self,
        table_name: str,
        columns: Dict[str, str],
        foreign_keys: List[Dict[str, str]] = None,
        if_not_exists: bool = True,
    ) -> None:
        if table_name in self.tables and not if_not_exists:
            raise ValueError(f"Table {table_name} already exists")
        
        self.tables[table_name] = {
            "columns": columns,
            "foreign_keys": foreign_keys or [],
            "primary_key": None
        }
        
        # Set primary key if defined in columns
        for col_name, col_type in columns.items():
            if "PRIMARY KEY" in col_type.upper():
                self.tables[table_name]["primary_key"] = col_name
                
        self.executed_operations.append(f"CREATE TABLE {table_name}")
        
    def drop_table(self, table_name: str, if_exists: bool = True) -> None:
        if table_name not in self.tables and not if_exists:
            raise ValueError(f"Table {table_name} does not exist")
            
        if table_name in self.tables:
            del self.tables[table_name]
            
        self.executed_operations.append(f"DROP TABLE {table_name}")
        
    def rename_table(self, old_name: str, new_name: str) -> None:
        if old_name not in self.tables:
            raise ValueError(f"Table {old_name} does not exist")
        if new_name in self.tables:
            raise ValueError(f"Table {new_name} already exists")
            
        self.tables[new_name] = self.tables.pop(old_name)
        self.executed_operations.append(f"RENAME TABLE {old_name} TO {new_name}")
        
    def add_columns(
        self,
        table_name: str,
        columns: Dict[str, str],
        default_values: Dict[str, Any] = None,
    ) -> None:
        if table_name not in self.tables:
            raise ValueError(f"Table {table_name} does not exist")
            
        self.tables[table_name]["columns"].update(columns)
        self.executed_operations.append(f"ADD COLUMNS to {table_name}")
        
    def add_column(
        self,
        table_name: str,
        column_name: str,
        column_type: str,
        default_value: Any = None,
    ) -> None:
        if table_name not in self.tables:
            raise ValueError(f"Table {table_name} does not exist")
            
        self.tables[table_name]["columns"][column_name] = column_type
        self.executed_operations.append(f"ADD COLUMN {column_name} to {table_name}")
        
    def drop_columns(
        self, table_name: str, columns: Union[str, List[str]], if_exists: bool = True
    ) -> None:
        if table_name not in self.tables:
            raise ValueError(f"Table {table_name} does not exist")
            
        if isinstance(columns, str):
            columns = [columns]
            
        for col in columns:
            if col in self.tables[table_name]["columns"]:
                del self.tables[table_name]["columns"][col]
            elif not if_exists:
                raise ValueError(f"Column {col} does not exist")
                
        self.executed_operations.append(f"DROP COLUMNS from {table_name}")
        
    def get_table_names(self) -> List[str]:
        return list(self.tables.keys())
        
    def get_table_schema(self, table_name: str):
        if table_name not in self.tables:
            raise ValueError(f"Table {table_name} does not exist")
        return self.tables[table_name]["columns"]
        
    def get_primary_key(self, table_name: str) -> str:
        if table_name not in self.tables:
            raise ValueError(f"Table {table_name} does not exist")
        return self.tables[table_name]["primary_key"]
        
    def get_table_stats(self, table_name: str) -> Dict[str, int]:
        if table_name not in self.tables:
            raise ValueError(f"Table {table_name} does not exist")
        return {
            "row_count": 100,  # Mock data
            "table_size": 1024,
            "index_size": 256,
            "total_size": 1280
        }


class TestBaseTableMixin:
    """Test suite for BaseTableMixin class."""

    def test_abstract_methods_not_implemented(self):
        """Test that abstract methods raise NotImplementedError."""
        mixin = _BaseTableMixin()
        
        # Test create_table
        with pytest.raises(NotImplementedError):
            mixin.create_table("users", {"id": "INTEGER"})
            
        # Test drop_table
        with pytest.raises(NotImplementedError):
            mixin.drop_table("users")
            
        # Test rename_table
        with pytest.raises(NotImplementedError):
            mixin.rename_table("users", "customers")
            
        # Test add_columns
        with pytest.raises(NotImplementedError):
            mixin.add_columns("users", {"email": "VARCHAR(100)"})
            
        # Test add_column
        with pytest.raises(NotImplementedError):
            mixin.add_column("users", "email", "VARCHAR(100)")
            
        # Test drop_columns
        with pytest.raises(NotImplementedError):
            mixin.drop_columns("users", ["email"])
            
        # Test get_table_names
        with pytest.raises(NotImplementedError):
            mixin.get_table_names()
            
        # Test get_table_schema
        with pytest.raises(NotImplementedError):
            mixin.get_table_schema("users")
            
        # Test get_primary_key
        with pytest.raises(NotImplementedError):
            mixin.get_primary_key("users")
            
        # Test get_table_stats
        with pytest.raises(NotImplementedError):
            mixin.get_table_stats("users")

    def test_create_table_basic(self):
        """Test basic table creation."""
        mixin = ConcreteTableMixin()
        
        # Create table
        columns = {
            "id": "INTEGER PRIMARY KEY",
            "name": "VARCHAR(100)",
            "age": "INTEGER"
        }
        mixin.create_table("users", columns)
        
        # Verify table exists
        assert "users" in mixin.get_table_names()
        assert mixin.get_table_schema("users") == columns
        assert mixin.get_primary_key("users") == "id"

    def test_create_table_with_foreign_keys(self):
        """Test table creation with foreign key constraints."""
        mixin = ConcreteTableMixin()
        
        # Create parent table
        mixin.create_table("users", {"id": "INTEGER PRIMARY KEY", "name": "VARCHAR(100)"})
        
        # Create child table with foreign key
        columns = {
            "id": "INTEGER PRIMARY KEY",
            "user_id": "INTEGER",
            "product": "VARCHAR(100)"
        }
        foreign_keys = [{
            "column": "user_id",
            "references": "users",
            "referenced_column": "id"
        }]
        mixin.create_table("orders", columns, foreign_keys=foreign_keys)
        
        # Verify foreign keys stored
        assert mixin.tables["orders"]["foreign_keys"] == foreign_keys

    def test_create_table_if_not_exists(self):
        """Test creating table with if_not_exists flag."""
        mixin = ConcreteTableMixin()
        
        # Create table
        mixin.create_table("users", {"id": "INTEGER"})
        
        # Try to create again with if_not_exists=True (should succeed)
        mixin.create_table("users", {"id": "INTEGER"}, if_not_exists=True)
        
        # Try to create again with if_not_exists=False (should fail)
        with pytest.raises(ValueError, match="already exists"):
            mixin.create_table("users", {"id": "INTEGER"}, if_not_exists=False)

    def test_drop_table(self):
        """Test dropping tables."""
        mixin = ConcreteTableMixin()
        
        # Create and drop table
        mixin.create_table("users", {"id": "INTEGER"})
        assert "users" in mixin.get_table_names()
        
        mixin.drop_table("users")
        assert "users" not in mixin.get_table_names()

    def test_drop_table_if_exists(self):
        """Test dropping table with if_exists flag."""
        mixin = ConcreteTableMixin()
        
        # Drop non-existent table with if_exists=True (should succeed)
        mixin.drop_table("users", if_exists=True)
        
        # Drop non-existent table with if_exists=False (should fail)
        with pytest.raises(ValueError, match="does not exist"):
            mixin.drop_table("users", if_exists=False)

    def test_rename_table(self):
        """Test renaming tables."""
        mixin = ConcreteTableMixin()
        
        # Create and rename table
        mixin.create_table("users", {"id": "INTEGER"})
        mixin.rename_table("users", "customers")
        
        # Verify rename
        assert "users" not in mixin.get_table_names()
        assert "customers" in mixin.get_table_names()

    def test_rename_table_errors(self):
        """Test error cases for rename table."""
        mixin = ConcreteTableMixin()
        
        # Rename non-existent table
        with pytest.raises(ValueError, match="does not exist"):
            mixin.rename_table("users", "customers")
            
        # Rename to existing table
        mixin.create_table("users", {"id": "INTEGER"})
        mixin.create_table("customers", {"id": "INTEGER"})
        with pytest.raises(ValueError, match="already exists"):
            mixin.rename_table("users", "customers")

    def test_add_columns(self):
        """Test adding multiple columns."""
        mixin = ConcreteTableMixin()
        
        # Create table and add columns
        mixin.create_table("users", {"id": "INTEGER"})
        new_columns = {
            "email": "VARCHAR(100)",
            "phone": "VARCHAR(20)",
            "address": "TEXT"
        }
        mixin.add_columns("users", new_columns)
        
        # Verify columns added
        schema = mixin.get_table_schema("users")
        for col in new_columns:
            assert col in schema

    def test_add_column(self):
        """Test adding single column."""
        mixin = ConcreteTableMixin()
        
        # Create table and add column
        mixin.create_table("users", {"id": "INTEGER"})
        mixin.add_column("users", "email", "VARCHAR(100)", default_value="''")
        
        # Verify column added
        schema = mixin.get_table_schema("users")
        assert "email" in schema
        assert schema["email"] == "VARCHAR(100)"

    def test_drop_columns(self):
        """Test dropping columns."""
        mixin = ConcreteTableMixin()
        
        # Create table with multiple columns
        columns = {
            "id": "INTEGER",
            "name": "VARCHAR(100)",
            "email": "VARCHAR(100)",
            "phone": "VARCHAR(20)"
        }
        mixin.create_table("users", columns)
        
        # Drop single column (string)
        mixin.drop_columns("users", "phone")
        schema = mixin.get_table_schema("users")
        assert "phone" not in schema
        
        # Drop multiple columns (list)
        mixin.drop_columns("users", ["name", "email"])
        schema = mixin.get_table_schema("users")
        assert "name" not in schema
        assert "email" not in schema
        assert "id" in schema

    def test_drop_columns_if_exists(self):
        """Test dropping columns with if_exists flag."""
        mixin = ConcreteTableMixin()
        
        mixin.create_table("users", {"id": "INTEGER"})
        
        # Drop non-existent column with if_exists=True (should succeed)
        mixin.drop_columns("users", "email", if_exists=True)
        
        # Drop non-existent column with if_exists=False (should fail)
        with pytest.raises(ValueError, match="does not exist"):
            mixin.drop_columns("users", "email", if_exists=False)

    def test_get_table_names(self):
        """Test getting list of table names."""
        mixin = ConcreteTableMixin()
        
        # Initially empty
        assert mixin.get_table_names() == []
        
        # Create multiple tables
        mixin.create_table("users", {"id": "INTEGER"})
        mixin.create_table("orders", {"id": "INTEGER"})
        mixin.create_table("products", {"id": "INTEGER"})
        
        # Verify all tables listed
        table_names = mixin.get_table_names()
        assert len(table_names) == 3
        assert "users" in table_names
        assert "orders" in table_names
        assert "products" in table_names

    def test_get_table_schema(self):
        """Test getting table schema."""
        mixin = ConcreteTableMixin()
        
        # Create table with schema
        columns = {
            "id": "INTEGER PRIMARY KEY",
            "name": "VARCHAR(100) NOT NULL",
            "email": "VARCHAR(100) UNIQUE",
            "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
        }
        mixin.create_table("users", columns)
        
        # Get schema
        schema = mixin.get_table_schema("users")
        assert schema == columns

    def test_get_primary_key(self):
        """Test getting primary key."""
        mixin = ConcreteTableMixin()
        
        # Table with primary key
        mixin.create_table("users", {
            "id": "INTEGER PRIMARY KEY",
            "name": "VARCHAR(100)"
        })
        assert mixin.get_primary_key("users") == "id"
        
        # Table without primary key
        mixin.create_table("logs", {
            "message": "TEXT",
            "timestamp": "TIMESTAMP"
        })
        assert mixin.get_primary_key("logs") is None

    def test_get_table_stats(self):
        """Test getting table statistics."""
        mixin = ConcreteTableMixin()
        
        mixin.create_table("users", {"id": "INTEGER"})
        stats = mixin.get_table_stats("users")
        
        # Verify stats structure
        assert "row_count" in stats
        assert "table_size" in stats
        assert "index_size" in stats
        assert "total_size" in stats
        assert all(isinstance(v, int) for v in stats.values())

    def test_error_on_non_existent_table(self):
        """Test operations on non-existent tables raise errors."""
        mixin = ConcreteTableMixin()
        
        # Test various operations
        with pytest.raises(ValueError, match="does not exist"):
            mixin.add_columns("users", {"email": "VARCHAR(100)"})
            
        with pytest.raises(ValueError, match="does not exist"):
            mixin.add_column("users", "email", "VARCHAR(100)")
            
        with pytest.raises(ValueError, match="does not exist"):
            mixin.drop_columns("users", "email")
            
        with pytest.raises(ValueError, match="does not exist"):
            mixin.get_table_schema("users")
            
        with pytest.raises(ValueError, match="does not exist"):
            mixin.get_primary_key("users")
            
        with pytest.raises(ValueError, match="does not exist"):
            mixin.get_table_stats("users")

    def test_operation_tracking(self):
        """Test that operations are tracked."""
        mixin = ConcreteTableMixin()
        
        # Perform various operations
        mixin.create_table("users", {"id": "INTEGER"})
        mixin.add_column("users", "email", "VARCHAR(100)")
        mixin.drop_columns("users", "email")
        mixin.rename_table("users", "customers")
        mixin.drop_table("customers")
        
        # Verify operations tracked
        assert len(mixin.executed_operations) == 5
        assert "CREATE TABLE users" in mixin.executed_operations
        assert "ADD COLUMN email to users" in mixin.executed_operations
        assert "DROP COLUMNS from users" in mixin.executed_operations
        assert "RENAME TABLE users TO customers" in mixin.executed_operations
        assert "DROP TABLE customers" in mixin.executed_operations


# --------------------------------------------------------------------------------

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/db/_BaseMixins/_BaseTableMixin.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-24 22:21:17 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/db/_Basemodules/_BaseTableMixin.py
# 
# THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/db/_Basemodules/_BaseTableMixin.py"
# 
# 
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# 
# from typing import Any, Dict, List, Union
# 
# 
# class _BaseTableMixin:
#     def create_table(
#         self,
#         table_name: str,
#         columns: Dict[str, str],
#         foreign_keys: List[Dict[str, str]] = None,
#         if_not_exists: bool = True,
#     ) -> None:
#         raise NotImplementedError
# 
#     def drop_table(self, table_name: str, if_exists: bool = True) -> None:
#         raise NotImplementedError
# 
#     def rename_table(self, old_name: str, new_name: str) -> None:
#         raise NotImplementedError
# 
#     def add_columns(
#         self,
#         table_name: str,
#         columns: Dict[str, str],
#         default_values: Dict[str, Any] = None,
#     ) -> None:
#         raise NotImplementedError
# 
#     def add_column(
#         self,
#         table_name: str,
#         column_name: str,
#         column_type: str,
#         default_value: Any = None,
#     ) -> None:
#         raise NotImplementedError
# 
#     def drop_columns(
#         self, table_name: str, columns: Union[str, List[str]], if_exists: bool = True
#     ) -> None:
#         raise NotImplementedError
# 
#     def get_table_names(self) -> List[str]:
#         raise NotImplementedError
# 
#     def get_table_schema(self, table_name: str):
#         raise NotImplementedError
# 
#     def get_primary_key(self, table_name: str) -> str:
#         raise NotImplementedError
# 
#     def get_table_stats(self, table_name: str) -> Dict[str, int]:
#         raise NotImplementedError
# 
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/db/_BaseMixins/_BaseTableMixin.py
# --------------------------------------------------------------------------------
