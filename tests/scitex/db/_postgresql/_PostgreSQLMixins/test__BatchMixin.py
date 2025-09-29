#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-12-01 10:45:00 (ywatanabe)"
# File: tests/scitex/db/_PostgreSQLMixins/test__BatchMixin.py

"""
Comprehensive tests for PostgreSQL BatchMixin.
Testing PostgreSQL-specific batch operations and DataFrame integration.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime
from unittest.mock import MagicMock, patch, call
from scitex.db._PostgreSQLMixins import _BatchMixin


class TestPostgreSQLBatchMixin:
    """Test suite for PostgreSQL BatchMixin."""

    @pytest.fixture
    def mixin(self):
        """Create BatchMixin instance with mocked methods."""
        mixin = _BatchMixin()
        mixin.execute = MagicMock()
        mixin.executemany = MagicMock()
        return mixin

    def test_insert_many_simple(self, mixin):
        """Test simple batch insert."""
        records = [
            {"id": 1, "name": "John", "age": 25},
            {"id": 2, "name": "Jane", "age": 30},
            {"id": 3, "name": "Bob", "age": 35}
        ]
        
        mixin.insert_many("users", records)
        
        # Verify SQL query
        expected_query = "INSERT INTO users (id, name, age) VALUES (%s, %s, %s)"
        
        # Verify executemany called with correct parameters
        mixin.executemany.assert_called_once_with(
            expected_query,
            [(1, "John", 25), (2, "Jane", 30), (3, "Bob", 35)]
        )

    def test_insert_many_empty_records(self, mixin):
        """Test insert_many with empty records."""
        mixin.insert_many("users", [])
        
        # Should not execute anything
        mixin.executemany.assert_not_called()

    def test_insert_many_with_batch_size(self, mixin):
        """Test batch insert with specific batch size."""
        records = [
            {"id": i, "value": f"test{i}"} 
            for i in range(10)
        ]
        
        mixin.insert_many("test_table", records, batch_size=3)
        
        # Should be called 4 times (3+3+3+1)
        assert mixin.executemany.call_count == 4
        
        # Check first batch
        first_call = mixin.executemany.call_args_list[0]
        assert len(first_call[0][1]) == 3  # 3 records in first batch
        
        # Check last batch
        last_call = mixin.executemany.call_args_list[-1]
        assert len(last_call[0][1]) == 1  # 1 record in last batch

    def test_prepare_insert_query(self, mixin):
        """Test SQL query preparation."""
        record = {"col1": "val1", "col2": 123, "col3": True}
        
        query = mixin._prepare_insert_query("test_table", record)
        
        assert query == "INSERT INTO test_table (col1, col2, col3) VALUES (%s, %s, %s)"

    def test_prepare_batch_parameters(self, mixin):
        """Test batch parameter preparation."""
        records = [
            {"name": "Alice", "score": 90, "active": True},
            {"name": "Bob", "score": 85, "active": False},
            {"name": "Charlie", "score": 95, "active": True}
        ]
        
        params = mixin._prepare_batch_parameters(records)
        
        expected = [
            ("Alice", 90, True),
            ("Bob", 85, False),
            ("Charlie", 95, True)
        ]
        assert params == expected

    def test_prepare_batch_parameters_empty(self, mixin):
        """Test batch parameter preparation with empty list."""
        params = mixin._prepare_batch_parameters([])
        assert params == []

    def test_dataframe_to_sql_fail_mode(self, mixin):
        """Test DataFrame to SQL with fail mode."""
        df = pd.DataFrame({
            "id": [1, 2, 3],
            "name": ["A", "B", "C"],
            "value": [10.5, 20.3, 30.1]
        })
        
        mixin.dataframe_to_sql(df, "test_table", if_exists="fail")
        
        # Should not drop or create table
        assert not any("DROP TABLE" in str(call) for call in mixin.execute.call_args_list)
        assert not any("CREATE TABLE" in str(call) for call in mixin.execute.call_args_list)
        
        # Should insert data
        mixin.executemany.assert_called_once()

    def test_dataframe_to_sql_replace_mode(self, mixin):
        """Test DataFrame to SQL with replace mode."""
        df = pd.DataFrame({
            "id": [1, 2],
            "name": ["Test1", "Test2"],
            "score": [85.5, 92.3],
            "active": [True, False],
            "created": [datetime.now(), datetime.now()]
        })
        
        mixin.dataframe_to_sql(df, "scores", if_exists="replace")
        
        # Verify table dropped
        drop_call = mixin.execute.call_args_list[0]
        assert drop_call[0][0] == "DROP TABLE IF EXISTS scores"
        
        # Verify table created with correct schema
        create_call = mixin.execute.call_args_list[1]
        create_query = create_call[0][0]
        assert "CREATE TABLE scores" in create_query
        assert "id INTEGER" in create_query
        assert "name TEXT" in create_query
        assert "score REAL" in create_query
        assert "active BOOLEAN" in create_query
        assert "created TIMESTAMP" in create_query
        
        # Verify data inserted
        mixin.executemany.assert_called_once()

    def test_dataframe_to_sql_append_mode(self, mixin):
        """Test DataFrame to SQL with append mode."""
        df = pd.DataFrame({
            "col1": ["a", "b"],
            "col2": [1, 2]
        })
        
        mixin.dataframe_to_sql(df, "existing_table", if_exists="append")
        
        # Should not drop or create table
        assert not any("DROP TABLE" in str(call) for call in mixin.execute.call_args_list)
        assert not any("CREATE TABLE" in str(call) for call in mixin.execute.call_args_list)
        
        # Should insert data
        mixin.executemany.assert_called_once()

    def test_dataframe_to_sql_invalid_mode(self, mixin):
        """Test DataFrame to SQL with invalid mode."""
        df = pd.DataFrame({"col": [1, 2]})
        
        with pytest.raises(ValueError, match="if_exists must be one of"):
            mixin.dataframe_to_sql(df, "table", if_exists="invalid")

    def test_map_dtype_to_postgres(self, mixin):
        """Test dtype mapping to PostgreSQL types."""
        # Test integer types
        assert mixin._map_dtype_to_postgres(np.dtype('int32')) == "INTEGER"
        assert mixin._map_dtype_to_postgres(np.dtype('int64')) == "INTEGER"
        
        # Test float types
        assert mixin._map_dtype_to_postgres(np.dtype('float32')) == "REAL"
        assert mixin._map_dtype_to_postgres(np.dtype('float64')) == "REAL"
        
        # Test datetime
        assert mixin._map_dtype_to_postgres(np.dtype('datetime64')) == "TIMESTAMP"
        
        # Test boolean
        assert mixin._map_dtype_to_postgres(np.dtype('bool')) == "BOOLEAN"
        
        # Test object/string (default)
        assert mixin._map_dtype_to_postgres(np.dtype('object')) == "TEXT"
        assert mixin._map_dtype_to_postgres(np.dtype('U10')) == "TEXT"

    def test_complex_dataframe_conversion(self, mixin):
        """Test conversion of complex DataFrame with various types."""
        df = pd.DataFrame({
            "int_col": pd.Series([1, 2, 3], dtype='int32'),
            "float_col": pd.Series([1.1, 2.2, 3.3], dtype='float64'),
            "str_col": ["a", "b", "c"],
            "bool_col": [True, False, True],
            "datetime_col": pd.date_range('2024-01-01', periods=3),
            "nullable_int": pd.Series([1, None, 3], dtype='Int64'),
            "mixed_col": [1, "two", 3.0]
        })
        
        mixin.dataframe_to_sql(df, "complex_table", if_exists="replace")
        
        # Check create table query
        create_call = mixin.execute.call_args_list[1]
        create_query = create_call[0][0]
        
        assert "int_col INTEGER" in create_query
        assert "float_col REAL" in create_query
        assert "str_col TEXT" in create_query
        assert "bool_col BOOLEAN" in create_query
        assert "datetime_col TIMESTAMP" in create_query
        assert "nullable_int INTEGER" in create_query
        assert "mixed_col TEXT" in create_query

    def test_large_batch_processing(self, mixin):
        """Test processing of large batches."""
        # Create large dataset
        large_records = [
            {"id": i, "data": f"data_{i}", "value": i * 10}
            for i in range(1000)
        ]
        
        mixin.insert_many("large_table", large_records, batch_size=100)
        
        # Should be called 10 times
        assert mixin.executemany.call_count == 10
        
        # Each call should have 100 records
        for call in mixin.executemany.call_args_list:
            assert len(call[0][1]) == 100

    def test_records_with_null_values(self, mixin):
        """Test handling of records with null values."""
        records = [
            {"id": 1, "name": "Test", "optional": None},
            {"id": 2, "name": None, "optional": "Value"},
            {"id": 3, "name": "Another", "optional": None}
        ]
        
        mixin.insert_many("nullable_table", records)
        
        expected_params = [
            (1, "Test", None),
            (2, None, "Value"),
            (3, "Another", None)
        ]
        
        mixin.executemany.assert_called_once()
        assert mixin.executemany.call_args[0][1] == expected_params

    def test_consistent_column_order(self, mixin):
        """Test that column order is preserved across records."""
        # Records with different key orders
        records = [
            {"b": 2, "a": 1, "c": 3},
            {"c": 6, "a": 4, "b": 5},
            {"a": 7, "c": 9, "b": 8}
        ]
        
        mixin.insert_many("ordered_table", records)
        
        # All records should use the same column order (from first record)
        expected_params = [
            (2, 1, 3),  # b, a, c order
            (5, 4, 6),
            (8, 7, 9)
        ]
        
        assert mixin.executemany.call_args[0][1] == expected_params

    def test_special_characters_in_values(self, mixin):
        """Test handling of special characters in values."""
        records = [
            {"id": 1, "text": "Normal text"},
            {"id": 2, "text": "Text with 'quotes'"},
            {"id": 3, "text": "Text with \"double quotes\""},
            {"id": 4, "text": "Text with % and $ special chars"},
            {"id": 5, "text": "Text with\nnewline"}
        ]
        
        mixin.insert_many("special_chars", records)
        
        # Parameters should preserve special characters
        params = mixin.executemany.call_args[0][1]
        assert params[1][1] == "Text with 'quotes'"
        assert params[2][1] == 'Text with "double quotes"'
        assert params[3][1] == "Text with % and $ special chars"
        assert params[4][1] == "Text with\nnewline"

    def test_zero_batch_size(self, mixin):
        """Test handling of zero or negative batch size."""
        records = [{"id": i} for i in range(5)]
        
        # Zero batch size should process all at once
        mixin.insert_many("test", records, batch_size=0)
        assert mixin.executemany.call_count == 1
        
        # Negative batch size should process all at once
        mixin.executemany.reset_mock()
        mixin.insert_many("test", records, batch_size=-1)
        assert mixin.executemany.call_count == 1


# --------------------------------------------------------------------------------

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/db/_postgresql/_PostgreSQLMixins/_BatchMixin.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-02-27 22:14:16 (ywatanabe)"
# # File: /home/ywatanabe/proj/scitex_dev/src/scitex/db/_PostgreSQLMixins/_BatchMixin.py
# 
# THIS_FILE = (
#     "/home/ywatanabe/proj/scitex_repo/src/scitex/db/_PostgreSQLMixins/_BatchMixin.py"
# )
# 
# from typing import List, Any, Optional, Dict, Union
# import pandas as pd
# from ..._BaseMixins._BaseBatchMixin import _BaseBatchMixin
# 
# 
# class _BatchMixin(_BaseBatchMixin):
#     def insert_many(
#         self,
#         table: str,
#         records: List[Dict[str, Any]],
#         batch_size: Optional[int] = None,
#     ) -> None:
#         if not records:
#             return
# 
#         query = self._prepare_insert_query(table, records[0])
#         if batch_size and batch_size > 0:
#             for i in range(0, len(records), batch_size):
#                 batch = records[i : i + batch_size]
#                 parameters = self._prepare_batch_parameters(batch)
#                 self.executemany(query, parameters)
#         else:
#             parameters = self._prepare_batch_parameters(records)
#             self.executemany(query, parameters)
# 
#     def _prepare_insert_query(self, table: str, record: Dict[str, Any]) -> str:
#         columns = list(record.keys())
#         placeholders = ["%s"] * len(columns)
#         columns_str = ", ".join(columns)
#         placeholders_str = ", ".join(placeholders)
#         return f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders_str})"
# 
#     def _prepare_batch_parameters(self, records: List[Dict[str, Any]]) -> List[tuple]:
#         if not records:
#             return []
# 
#         columns = list(records[0].keys())
#         return [tuple(record[col] for col in columns) for record in records]
# 
#     def dataframe_to_sql(
#         self, df: pd.DataFrame, table: str, if_exists: str = "fail"
#     ) -> None:
#         if if_exists not in ["fail", "replace", "append"]:
#             raise ValueError("if_exists must be one of 'fail', 'replace', or 'append'")
# 
#         if if_exists == "replace":
#             self.execute(f"DROP TABLE IF EXISTS {table}")
#             # Create table based on DataFrame schema
#             columns = []
#             for col, dtype in df.dtypes.items():
#                 pg_type = self._map_dtype_to_postgres(dtype)
#                 columns.append(f"{col} {pg_type}")
#             columns_str = ", ".join(columns)
#             self.execute(f"CREATE TABLE {table} ({columns_str})")
# 
#         records = df.to_dict("records")
#         self.insert_many(table, records)
# 
#     def _map_dtype_to_postgres(self, dtype) -> str:
#         dtype_str = str(dtype)
#         if "int" in dtype_str:
#             return "INTEGER"
#         elif "float" in dtype_str:
#             return "REAL"
#         elif "datetime" in dtype_str:
#             return "TIMESTAMP"
#         elif "bool" in dtype_str:
#             return "BOOLEAN"
#         else:
#             return "TEXT"
# 
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/db/_postgresql/_PostgreSQLMixins/_BatchMixin.py
# --------------------------------------------------------------------------------
