#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-12-01 10:50:00 (ywatanabe)"
# File: tests/scitex/db/_PostgreSQLMixins/test__BlobMixin.py

"""
Comprehensive tests for PostgreSQL BlobMixin.
Testing PostgreSQL-specific BLOB handling for NumPy arrays and binary data.
"""

import pytest
import numpy as np
import pandas as pd
import psycopg2
from unittest.mock import MagicMock, patch, call
from scitex.db._PostgreSQLMixins import _BlobMixin


class TestPostgreSQLBlobMixin:
    """Test suite for PostgreSQL BlobMixin."""

    @pytest.fixture
    def mixin(self):
        """Create BlobMixin instance with mocked methods."""
        mixin = _BlobMixin()
        mixin.execute = MagicMock()
        mixin.cursor = MagicMock()
        mixin.transaction = MagicMock()
        mixin.transaction().__enter__ = MagicMock()
        mixin.transaction().__exit__ = MagicMock()
        return mixin

    @pytest.fixture
    def sample_arrays(self):
        """Create sample NumPy arrays for testing."""
        return {
            "1d": np.array([1, 2, 3, 4, 5], dtype=np.float32),
            "2d": np.array([[1, 2], [3, 4], [5, 6]], dtype=np.int32),
            "3d": np.random.randn(2, 3, 4).astype(np.float64),
            "bool": np.array([True, False, True], dtype=bool),
            "complex": np.array([1+2j, 3+4j], dtype=np.complex128)
        }

    def test_save_array_single(self, mixin, sample_arrays):
        """Test saving a single array without ID."""
        arr = sample_arrays["2d"]
        
        with patch('psycopg2.Binary') as mock_binary:
            mock_binary.return_value = b"mock_binary_data"
            
            mixin.save_array("test_table", arr)
            
            # Verify Binary was called with array bytes
            mock_binary.assert_called_once_with(arr.tobytes())
            
            # Verify INSERT query
            expected_query = "INSERT INTO test_table (data,data_dtype,data_shape) VALUES (%s,%s,%s)"
            mixin.execute.assert_called_once_with(
                expected_query,
                [b"mock_binary_data", "int32", "(3, 2)"]
            )

    def test_save_array_with_id(self, mixin, sample_arrays):
        """Test saving array with specific ID."""
        arr = sample_arrays["1d"]
        
        with patch('psycopg2.Binary') as mock_binary:
            mock_binary.return_value = b"mock_binary"
            
            mixin.save_array("test_table", arr, ids=42)
            
            # Verify UPDATE query
            expected_query = "UPDATE test_table SET data=%s,data_dtype=%s,data_shape=%s WHERE id=%s"
            mixin.execute.assert_called_once_with(
                expected_query,
                [b"mock_binary", "float32", "(5,)", 42]
            )

    def test_save_array_multiple_with_ids(self, mixin, sample_arrays):
        """Test saving multiple arrays with IDs."""
        arrays = [sample_arrays["1d"], sample_arrays["2d"]]
        ids = [10, 20]
        
        with patch('psycopg2.Binary') as mock_binary:
            mock_binary.side_effect = [b"binary1", b"binary2"]
            
            mixin.save_array("test_table", arrays, ids=ids)
            
            # Should execute two UPDATE queries
            assert mixin.execute.call_count == 2
            
            # Check first call
            first_call = mixin.execute.call_args_list[0]
            assert "UPDATE test_table" in first_call[0][0]
            assert first_call[0][1][-1] == 10  # ID at end
            
            # Check second call
            second_call = mixin.execute.call_args_list[1]
            assert second_call[0][1][-1] == 20  # ID at end

    def test_save_array_with_where_clause(self, mixin, sample_arrays):
        """Test saving array with WHERE clause."""
        arr = sample_arrays["3d"]
        
        with patch('psycopg2.Binary') as mock_binary:
            mock_binary.return_value = b"binary_data"
            
            mixin.save_array("test_table", arr, where="status='active'")
            
            # Verify UPDATE with WHERE
            call_args = mixin.execute.call_args[0]
            assert "UPDATE test_table" in call_args[0]
            assert "WHERE status='active'" in call_args[0]

    def test_save_array_with_additional_columns(self, mixin, sample_arrays):
        """Test saving array with additional columns."""
        arr = sample_arrays["1d"]
        additional = {"name": "test_array", "created_by": "user123"}
        
        with patch('psycopg2.Binary') as mock_binary:
            mock_binary.return_value = b"binary"
            
            mixin.save_array("test_table", arr, additional_columns=additional)
            
            # Verify columns are included
            query = mixin.execute.call_args[0][0]
            assert "name" in query
            assert "created_by" in query
            
            # Verify values order
            values = mixin.execute.call_args[0][1]
            assert "test_array" in values
            assert "user123" in values

    def test_save_array_invalid_input(self, mixin):
        """Test save_array with invalid input."""
        with pytest.raises(ValueError, match="Input must be a NumPy array"):
            mixin.save_array("test_table", "not an array")
        
        with pytest.raises(ValueError, match="Single input must be a NumPy array"):
            mixin.save_array("test_table", [1, 2, 3])  # List but no IDs

    def test_save_array_mismatched_ids(self, mixin, sample_arrays):
        """Test save_array with mismatched IDs and arrays."""
        arrays = [sample_arrays["1d"], sample_arrays["2d"]]
        ids = [1, 2, 3]  # Too many IDs
        
        with pytest.raises(ValueError, match="Length of ids must match"):
            mixin.save_array("test_table", arrays, ids=ids)

    def test_load_array_single_id(self, mixin, sample_arrays):
        """Test loading array with single ID."""
        # Mock database response
        original_arr = sample_arrays["2d"]
        blob_data = original_arr.tobytes()
        
        mixin.cursor.fetchall.return_value = [
            (42, blob_data, "int32", "(3, 2)")
        ]
        
        result = mixin.load_array("test_table", "data", ids=42)
        
        # Verify query
        query = mixin.execute.call_args[0][0]
        assert "SELECT id, data, data_dtype, data_shape" in query
        assert "WHERE id IN (%s)" in query
        
        # Result should be stacked array
        assert result.shape == (1, 3, 2)  # Stacked with extra dimension

    def test_load_array_multiple_ids(self, mixin, sample_arrays):
        """Test loading arrays with multiple IDs."""
        # Create test data
        arr1 = np.array([1, 2, 3])
        arr2 = np.array([4, 5, 6])
        
        mixin.cursor.fetchall.return_value = [
            (1, arr1.tobytes(), "int64", "(3,)"),
            (2, arr2.tobytes(), "int64", "(3,)")
        ]
        
        result = mixin.load_array("test_table", "data", ids=[1, 2])
        
        # Should return stacked arrays
        assert result.shape == (2, 3)
        np.testing.assert_array_equal(result[0], arr1)
        np.testing.assert_array_equal(result[1], arr2)

    def test_load_array_all(self, mixin):
        """Test loading all arrays from table."""
        # First query returns IDs
        mixin.cursor.fetchall.side_effect = [
            [(1,), (2,), (3,)],  # ID query result
            [  # Data query result
                (1, b"data1", "float32", "(2,)"),
                (2, b"data2", "float32", "(2,)"),
                (3, b"data3", "float32", "(2,)")
            ]
        ]
        
        result = mixin.load_array("test_table", "data", ids="all")
        
        # Should execute two queries
        assert mixin.execute.call_count == 2
        
        # First query should get IDs
        first_query = mixin.execute.call_args_list[0][0][0]
        assert "SELECT id FROM test_table" in first_query

    def test_load_array_with_where(self, mixin):
        """Test loading arrays with WHERE clause."""
        mixin.cursor.fetchall.return_value = [(1,), (2,)]
        
        mixin.load_array("test_table", "data", ids="all", where="active=true")
        
        # Check WHERE clause in ID query
        query = mixin.execute.call_args_list[0][0][0]
        assert "WHERE active=true" in query

    def test_load_array_batch_processing(self, mixin):
        """Test batch processing for large ID lists."""
        # Create many IDs
        ids = list(range(500))
        
        # Mock responses for batches
        mixin.cursor.fetchall.return_value = []
        
        mixin.load_array("test_table", "data", ids=ids, batch_size=100)
        
        # Should process in 5 batches
        assert mixin.execute.call_count == 5

    def test_load_array_without_metadata(self, mixin):
        """Test loading arrays without dtype/shape metadata."""
        # Simulate missing metadata columns
        mixin.execute.side_effect = [
            psycopg2.Error("column does not exist"),  # First query fails
            None  # Second query succeeds
        ]
        
        blob = np.array([1.0, 2.0, 3.0], dtype=np.float64).tobytes()
        mixin.cursor.fetchall.return_value = [(1, blob)]
        
        result = mixin.load_array(
            "test_table", "data", ids=1, 
            dtype=np.float64, shape=(3,)
        )
        
        # Should fall back to simple query
        assert mixin.execute.call_count == 2
        second_query = mixin.execute.call_args_list[1][0][0]
        assert "data_dtype" not in second_query

    def test_binary_to_array_with_metadata(self, mixin):
        """Test binary_to_array with dtype and shape metadata."""
        arr = np.array([[1, 2], [3, 4]], dtype=np.int16)
        binary = arr.tobytes()
        
        result = mixin.binary_to_array(binary, "int16", "(2, 2)")
        
        np.testing.assert_array_equal(result, arr)

    def test_binary_to_array_without_metadata(self, mixin):
        """Test binary_to_array without metadata."""
        arr = np.array([1.1, 2.2, 3.3], dtype=np.float32)
        binary = arr.tobytes()
        
        result = mixin.binary_to_array(
            binary, dtype=np.float32, shape=(3,)
        )
        
        np.testing.assert_array_equal(result, arr)

    def test_binary_to_array_none(self, mixin):
        """Test binary_to_array with None input."""
        result = mixin.binary_to_array(None)
        assert result is None

    def test_get_array_dict(self, mixin):
        """Test converting DataFrame to array dictionary."""
        # Create test DataFrame
        df = pd.DataFrame({
            "id": [1, 2],
            "array1": [b"data1", b"data2"],
            "array1_dtype": ["float32", "float32"],
            "array1_shape": ["(2,)", "(2,)"],
            "array2": [b"data3", b"data4"],
            "array2_dtype": ["int32", "int32"],
            "array2_shape": ["(3,)", "(3,)"]
        })
        
        # Mock binary_to_array
        mixin.binary_to_array = MagicMock(side_effect=[
            np.array([1, 2]), np.array([3, 4]),  # array1
            np.array([5, 6, 7]), np.array([8, 9, 10])  # array2
        ])
        
        result = mixin.get_array_dict(df)
        
        assert "array1" in result
        assert "array2" in result
        assert result["array1"].shape == (2, 2)
        assert result["array2"].shape == (2, 3)

    def test_decode_array_columns(self, mixin):
        """Test decoding array columns in DataFrame."""
        # Create test DataFrame
        df = pd.DataFrame({
            "id": [1, 2],
            "data": [b"binary1", b"binary2"],
            "data_dtype": ["float64", "float64"],
            "data_shape": ["(4,)", "(4,)"],
            "other_col": ["a", "b"]
        })
        
        # Mock binary_to_array
        arr1 = np.array([1, 2, 3, 4])
        arr2 = np.array([5, 6, 7, 8])
        mixin.binary_to_array = MagicMock(side_effect=[arr1, arr2])
        
        result = mixin.decode_array_columns(df)
        
        # Check arrays were decoded
        assert isinstance(result.loc[0, "data"], np.ndarray)
        assert isinstance(result.loc[1, "data"], np.ndarray)
        np.testing.assert_array_equal(result.loc[0, "data"], arr1)
        np.testing.assert_array_equal(result.loc[1, "data"], arr2)

    def test_transaction_context(self, mixin, sample_arrays):
        """Test that save operations use transaction context."""
        arr = sample_arrays["1d"]
        
        with patch('psycopg2.Binary'):
            mixin.save_array("test_table", arr)
        
        # Verify transaction was used
        mixin.transaction.assert_called_once()
        mixin.transaction().__enter__.assert_called_once()
        mixin.transaction().__exit__.assert_called_once()

    def test_save_array_error_handling(self, mixin, sample_arrays):
        """Test error handling in save_array."""
        arr = sample_arrays["1d"]
        
        # Make execute raise an error
        mixin.execute.side_effect = Exception("Database error")
        
        with patch('psycopg2.Binary'):
            with pytest.raises(ValueError, match="Failed to save array"):
                mixin.save_array("test_table", arr)

    def test_load_array_error_handling(self, mixin):
        """Test error handling in load_array."""
        # Make execute raise an error
        mixin.execute.side_effect = Exception("Database error")
        
        with pytest.raises(ValueError, match="Failed to load array"):
            mixin.load_array("test_table", "data", ids=1)

    def test_complex_dtype_handling(self, mixin, sample_arrays):
        """Test handling of complex data types."""
        arr = sample_arrays["complex"]
        
        with patch('psycopg2.Binary') as mock_binary:
            mock_binary.return_value = b"complex_binary"
            
            mixin.save_array("test_table", arr, column="complex_data")
            
            # Verify complex dtype is preserved
            values = mixin.execute.call_args[0][1]
            assert "complex128" in values
            assert "(2,)" in values

    def test_custom_column_name(self, mixin, sample_arrays):
        """Test using custom column names."""
        arr = sample_arrays["2d"]
        
        with patch('psycopg2.Binary'):
            mixin.save_array("test_table", arr, column="custom_array")
        
        # Verify custom column name used
        query = mixin.execute.call_args[0][0]
        assert "custom_array" in query
        assert "custom_array_dtype" in query
        assert "custom_array_shape" in query


# --------------------------------------------------------------------------------

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/db/_postgresql/_PostgreSQLMixins/_BlobMixin.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-02-27 22:14:45 (ywatanabe)"
# # File: /home/ywatanabe/proj/scitex_dev/src/scitex/db/_PostgreSQLMixins/_BlobMixin.py
# 
# THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/db/_PostgreSQLMixins/_BlobMixin.py"
# 
# import psycopg2
# import numpy as np
# from typing import Any as _Any
# from typing import Dict, List, Optional, Tuple, Union
# from ..._BaseMixins._BaseBlobMixin import _BaseBlobMixin
# 
# 
# class _BlobMixin(_BaseBlobMixin):
#     """BLOB data handling functionality for PostgreSQL"""
# 
#     def save_array(
#         self,
#         table_name: str,
#         data: np.ndarray,
#         column: str = "data",
#         ids: Optional[Union[int, List[int]]] = None,
#         where: str = None,
#         additional_columns: Dict[str, _Any] = None,
#         batch_size: int = 1000,
#     ) -> None:
#         with self.transaction():
#             if not isinstance(data, (np.ndarray, list)):
#                 raise ValueError("Input must be a NumPy array or list of arrays")
# 
#             try:
#                 if ids is not None:
#                     if isinstance(ids, int):
#                         ids = [ids]
#                         data = [data]
#                     if len(ids) != len(data):
#                         raise ValueError("Length of ids must match number of arrays")
# 
#                     for id_, arr in zip(ids, data):
#                         if not isinstance(arr, np.ndarray):
#                             raise ValueError(
#                                 f"Element for id {id_} must be a NumPy array"
#                             )
# 
#                         binary = psycopg2.Binary(arr.tobytes())
#                         # binary = Binary(arr.tobytes())
#                         columns = [
#                             column,
#                             f"{column}_dtype",
#                             f"{column}_shape",
#                         ]
#                         values = [binary, str(arr.dtype), str(arr.shape)]
# 
#                         if additional_columns:
#                             columns = list(additional_columns.keys()) + columns
#                             values = list(additional_columns.values()) + values
# 
#                         update_cols = [f"{col}=%s" for col in columns]
#                         query = f"UPDATE {table_name} SET {','.join(update_cols)} WHERE id=%s"
#                         values.append(id_)
#                         self.execute(query, values)
# 
#                 else:
#                     if not isinstance(data, np.ndarray):
#                         raise ValueError("Single input must be a NumPy array")
# 
#                     binary = psycopg2.Binary(arr.tobytes())
#                     # binary = Binary(data.tobytes())
#                     columns = [column, f"{column}_dtype", f"{column}_shape"]
#                     values = [binary, str(data.dtype), str(data.shape)]
# 
#                     if additional_columns:
#                         columns = list(additional_columns.keys()) + columns
#                         values = list(additional_columns.values()) + values
# 
#                     if where is not None:
#                         update_cols = [f"{col}=%s" for col in columns]
#                         query = f"UPDATE {table_name} SET {','.join(update_cols)} WHERE {where}"
#                         self.execute(query, values)
#                     else:
#                         placeholders = ",".join(["%s" for _ in columns])
#                         columns_str = ",".join(columns)
#                         query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
#                         self.execute(query, values)
# 
#             except Exception as err:
#                 raise ValueError(f"Failed to save array: {err}")
# 
#     def load_array(
#         self,
#         table_name: str,
#         column: str,
#         ids: Union[int, List[int], str] = "all",
#         where: str = None,
#         order_by: str = None,
#         batch_size: int = 128,
#         dtype: np.dtype = None,
#         shape: Optional[Tuple] = None,
#     ) -> Optional[np.ndarray]:
#         try:
#             if ids == "all":
#                 query = f"SELECT id FROM {table_name}"
#                 if where:
#                     query += f" WHERE {where}"
#                 self.execute(query)
#                 ids = [row[0] for row in self.cursor.fetchall()]
#             elif isinstance(ids, int):
#                 ids = [ids]
# 
#             id_to_data = {}
#             unique_ids = list(set(ids))
# 
#             for idx in range(0, len(unique_ids), batch_size):
#                 batch_ids = unique_ids[idx : idx + batch_size]
#                 placeholders = ",".join(["%s" for _ in batch_ids])
# 
#                 try:
#                     query = f"""
#                         SELECT id, {column},
#                                {column}_dtype,
#                                {column}_shape
#                         FROM {table_name}
#                         WHERE id IN ({placeholders})
#                     """
#                     self.execute(query, batch_ids)
#                     has_metadata = True
#                 except psycopg2.Error:
#                     query = f"SELECT id, {column} FROM {table_name} WHERE id IN ({placeholders})"
#                     self.execute(query, batch_ids)
#                     has_metadata = False
# 
#                 if where:
#                     query += f" AND {where}"
#                 if order_by:
#                     query += f" ORDER BY {order_by}"
# 
#                 results = self.cursor.fetchall()
#                 if results:
#                     for result in results:
#                         if has_metadata:
#                             id_val, blob, dtype_str, shape_str = result
#                             data = np.frombuffer(
#                                 bytes(blob), dtype=np.dtype(dtype_str)
#                             ).reshape(eval(shape_str))
#                         else:
#                             id_val, blob = result
#                             data = (
#                                 np.frombuffer(bytes(blob), dtype=dtype)
#                                 if dtype
#                                 else np.frombuffer(bytes(blob))
#                             )
#                             if shape:
#                                 data = data.reshape(shape)
#                         id_to_data[id_val] = data
# 
#             all_data = [id_to_data[id_val] for id_val in ids if id_val in id_to_data]
#             return np.stack(all_data, axis=0) if all_data else None
# 
#         except Exception as err:
#             raise ValueError(f"Failed to load array: {err}")
# 
#     def binary_to_array(
#         self,
#         binary_data,
#         dtype_str=None,
#         shape_str=None,
#         dtype=None,
#         shape=None,
#     ):
#         if binary_data is None:
#             return None
# 
#         binary_data = bytes(binary_data)
#         if dtype_str and shape_str:
#             return np.frombuffer(binary_data, dtype=np.dtype(dtype_str)).reshape(
#                 eval(shape_str)
#             )
#         elif dtype and shape:
#             return np.frombuffer(binary_data, dtype=dtype).reshape(shape)
#         return binary_data
# 
#     def get_array_dict(self, df, columns=None, dtype=None, shape=None):
#         result = {}
#         if columns is None:
#             columns = [
#                 col
#                 for col in df.columns
#                 if not (col.endswith("_dtype") or col.endswith("_shape"))
#             ]
# 
#         for col in columns:
#             if f"{col}_dtype" in df.columns and f"{col}_shape" in df.columns:
#                 arrays = [
#                     self.binary_to_array(
#                         row[col], row[f"{col}_dtype"], row[f"{col}_shape"]
#                     )
#                     for _, row in df.iterrows()
#                 ]
#             elif dtype and shape:
#                 arrays = [
#                     self.binary_to_array(x, dtype=dtype, shape=shape) for x in df[col]
#                 ]
#             result[col] = np.stack(arrays)
# 
#         return result
# 
#     def decode_array_columns(self, df, columns=None, dtype=None, shape=None):
#         if columns is None:
#             columns = [
#                 col
#                 for col in df.columns
#                 if not (col.endswith("_dtype") or col.endswith("_shape"))
#             ]
# 
#         for col in columns:
#             if f"{col}_dtype" in df.columns and f"{col}_shape" in df.columns:
#                 df[col] = df.apply(
#                     lambda row: self.binary_to_array(
#                         row[col], row[f"{col}_dtype"], row[f"{col}_shape"]
#                     ),
#                     axis=1,
#                 )
#             elif dtype and shape:
#                 df[col] = df[col].apply(
#                     lambda x: self.binary_to_array(x, dtype=dtype, shape=shape)
#                 )
#         return df
# 
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/db/_postgresql/_PostgreSQLMixins/_BlobMixin.py
# --------------------------------------------------------------------------------
