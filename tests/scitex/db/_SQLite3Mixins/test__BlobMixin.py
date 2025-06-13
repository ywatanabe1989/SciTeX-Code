#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 14:48:00 (ywatanabe)"
# File: ./tests/scitex/db/_SQLite3Mixins/test__BlobMixin.py

"""
Functionality:
    * Tests BLOB data handling for SQLite3
    * Validates binary data storage and retrieval
    * Tests large object operations
Input:
    * Test database and binary data
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
from unittest.mock import Mock, patch


class TestBlobMixin:
    """Test cases for _BlobMixin"""
    
    def setup_method(self):
        """Set up test database"""
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.db_path = self.temp_db.name
        
    def teardown_method(self):
        """Clean up test database"""
        os.unlink(self.db_path)
        
    def test_insert_blob_basic(self):
        """Test basic BLOB insertion"""
from scitex.db._SQLite3Mixins import _BlobMixin
        
        mixin = _BlobMixin()
        mixin.execute = Mock()
        mixin.transaction = Mock(return_value=Mock(__enter__=Mock(), __exit__=Mock()))
        
        # Test binary data
        blob_data = b"\x00\x01\x02\x03\x04"
        
        mixin.insert_blob("test_table", "data", blob_data, {"id": 1})
        mixin.execute.assert_called()
        
    def test_read_blob_basic(self):
        """Test BLOB reading"""
from scitex.db._SQLite3Mixins import _BlobMixin
        
        mixin = _BlobMixin()
        mock_result = Mock(fetchone=Mock(return_value=(b"test_data",)))
        mixin.execute = Mock(return_value=mock_result)
        
        result = mixin.read_blob("test_table", "data", {"id": 1})
        assert result == b"test_data"
        
    def test_update_blob(self):
        """Test BLOB update"""
from scitex.db._SQLite3Mixins import _BlobMixin
        
        mixin = _BlobMixin()
        mixin.execute = Mock()
        mixin.transaction = Mock(return_value=Mock(__enter__=Mock(), __exit__=Mock()))
        
        new_data = b"updated_blob_data"
        mixin.update_blob("test_table", "data", new_data, {"id": 1})
        mixin.execute.assert_called()
        
    def test_blob_size(self):
        """Test getting BLOB size"""
from scitex.db._SQLite3Mixins import _BlobMixin
        
        mixin = _BlobMixin()
        mock_result = Mock(fetchone=Mock(return_value=(1024,)))
        mixin.execute = Mock(return_value=mock_result)
        
        size = mixin.get_blob_size("test_table", "data", {"id": 1})
        assert size == 1024
        
    def test_large_blob_handling(self):
        """Test handling of large BLOBs"""
from scitex.db._SQLite3Mixins import _BlobMixin
        
        mixin = _BlobMixin()
        mixin.execute = Mock()
        mixin.transaction = Mock(return_value=Mock(__enter__=Mock(), __exit__=Mock()))
        
        # 1MB of data
        large_data = b"x" * (1024 * 1024)
        
        # Should handle without error
        mixin.insert_blob("test_table", "data", large_data, {"id": 1})
        mixin.execute.assert_called()
        
    def test_null_blob_handling(self):
        """Test NULL BLOB handling"""
from scitex.db._SQLite3Mixins import _BlobMixin
        
        mixin = _BlobMixin()
        mock_result = Mock(fetchone=Mock(return_value=(None,)))
        mixin.execute = Mock(return_value=mock_result)
        
        result = mixin.read_blob("test_table", "data", {"id": 1})
        assert result is None


def main():
    """Run the tests"""
    pytest.main([__file__, "-v"])


if __name__ == "__main__":
    main()\n\n# --------------------------------------------------------------------------------\n# Start of Source Code from: /home/ywatanabe/proj/_scitex_repo/src/scitex/db/_SQLite3Mixins/_BlobMixin.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-12-01 05:13:49 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/db/_SQLite3Mixins/_BlobMixin.py
#
# THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/db/_SQLite3Mixins/_BlobMixin.py"
#
# import sqlite3
# from typing import Any as _Any
# from typing import Dict, List, Optional, Tuple, Union
#
# import numpy as np
# from .._BaseMixins._BaseBlobMixin import _BaseBlobMixin
#
# class _BlobMixin:
#     """BLOB data handling functionality"""
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
#         with self.lock:
#             if not isinstance(data, (np.ndarray, list)):
#                 raise ValueError(
#                     "Input must be a NumPy array or list of arrays"
#                 )
#
#             try:
#                 if ids is not None:
#                     if isinstance(ids, int):
#                         ids = [ids]
#                         data = [data]
#                     if len(ids) != len(data):
#                         raise ValueError(
#                             "Length of ids must match number of arrays"
#                         )
#
#                     for id_, arr in zip(ids, data):
#                         if not isinstance(arr, np.ndarray):
#                             raise ValueError(
#                                 f"Element for id {id_} must be a NumPy array"
#                             )
#
#                         binary = arr.tobytes()
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
#                         update_cols = [f"{col}=?" for col in columns]
#                         query = f"UPDATE {table_name} SET {','.join(update_cols)} WHERE id=?"
#                         values.append(id_)
#                         self.execute(query, tuple(values))
#
#                 else:
#                     if not isinstance(data, np.ndarray):
#                         raise ValueError("Single input must be a NumPy array")
#
#                     binary = data.tobytes()
#                     columns = [column, f"{column}_dtype", f"{column}_shape"]
#                     values = [binary, str(data.dtype), str(data.shape)]
#
#                     if additional_columns:
#                         columns = list(additional_columns.keys()) + columns
#                         values = list(additional_columns.values()) + values
#
#                     if where is not None:
#                         update_cols = [f"{col}=?" for col in columns]
#                         query = f"UPDATE {table_name} SET {','.join(update_cols)} WHERE {where}"
#                         self.execute(query, tuple(values))
#                     else:
#                         placeholders = ",".join(["?" for _ in columns])
#                         columns_str = ",".join(columns)
#                         query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
#                         self.execute(query, tuple(values))
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
#                 self.cursor.execute(query)
#                 ids = [row[0] for row in self.cursor.fetchall()]
#             elif isinstance(ids, int):
#                 ids = [ids]
#
#             id_to_data = {}
#             unique_ids = list(set(ids))
#
#             for idx in range(0, len(unique_ids), batch_size):
#                 batch_ids = unique_ids[idx : idx + batch_size]
#                 placeholders = ",".join("?" for _ in batch_ids)
#
#                 try:
#                     query = f"""
#                         SELECT id, {column},
#                                {column}_dtype,
#                                {column}_shape
#                         FROM {table_name}
#                         WHERE id IN ({placeholders})
#                     """
#                     self.cursor.execute(query, tuple(batch_ids))
#                     has_metadata = True
#                 except sqlite3.OperationalError:
#                     query = f"SELECT id, {column} FROM {table_name} WHERE id IN ({placeholders})"
#                     self.cursor.execute(query, tuple(batch_ids))
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
#                                 blob, dtype=np.dtype(dtype_str)
#                             ).reshape(eval(shape_str))
#                         else:
#                             id_val, blob = result
#                             data = (
#                                 np.frombuffer(blob, dtype=dtype)
#                                 if dtype
#                                 else np.frombuffer(blob)
#                             )
#                             if shape:
#                                 data = data.reshape(shape)
#                         id_to_data[id_val] = data
#
#             all_data = [
#                 id_to_data[id_val] for id_val in ids if id_val in id_to_data
#             ]
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
#         if dtype_str and shape_str:
#             return np.frombuffer(
#                 binary_data, dtype=np.dtype(dtype_str)
#             ).reshape(eval(shape_str))
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
#                     self.binary_to_array(x, dtype=dtype, shape=shape)
#                     for x in df[col]
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
# End of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/db/_SQLite3Mixins/_BlobMixin.py
# --------------------------------------------------------------------------------
