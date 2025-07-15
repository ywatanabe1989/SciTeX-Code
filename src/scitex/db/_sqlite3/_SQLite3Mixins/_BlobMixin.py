#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-15 09:03:30 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/db/_sqlite3/_SQLite3Mixins/_BlobMixin.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/db/_sqlite3/_SQLite3Mixins/_BlobMixin.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

# Time-stamp: "2024-12-01 05:13:49 (ywatanabe)"

THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/db/_SQLite3Mixins/_BlobMixin.py"

import pickle
import sqlite3
import zlib
from typing import Any as _Any
from typing import Dict, List, Optional, Tuple, Union

import numpy as np


class _BlobMixin:
    """BLOB data handling functionality"""

    # def save_array(
    #     self,
    #     table_name: str,
    #     data: np.ndarray,
    #     column: str = "data",
    #     ids: Optional[Union[int, List[int]]] = None,
    #     where: str = None,
    #     additional_columns: Dict[str, _Any] = None,
    #     batch_size: int = 1000,
    #     compress: Optional[bool] = None,  # None means use database default
    #     compress_level: int = 6,
    # ) -> None:
    #     with self.lock:
    #         if not isinstance(data, (np.ndarray, list)):
    #             raise ValueError(
    #                 "Input must be a NumPy array or list of arrays"
    #             )

    #         # Use database default if compress not explicitly specified
    #         if compress is None:
    #             compress = getattr(self, "compress_by_default", False)

    #         try:
    #             if ids is not None:
    #                 if isinstance(ids, int):
    #                     ids = [ids]
    #                     data = [data]
    #                 if len(ids) != len(data):
    #                     raise ValueError(
    #                         "Length of ids must match number of arrays"
    #                     )

    #                 for id_, arr in zip(ids, data):
    #                     if not isinstance(arr, np.ndarray):
    #                         raise ValueError(
    #                             f"Element for id {id_} must be a NumPy array"
    #                         )

    #                     binary = arr.tobytes()
    #                     if (
    #                         compress and len(binary) > 1024
    #                     ):  # Compress if > 1KB
    #                         binary = zlib.compress(
    #                             binary, level=compress_level
    #                         )
    #                         is_compressed = 1
    #                     else:
    #                         is_compressed = 0

    #                     columns = [
    #                         column,
    #                         f"{column}_dtype",
    #                         f"{column}_shape",
    #                         f"{column}_compressed",
    #                     ]
    #                     values = [
    #                         binary,
    #                         str(arr.dtype),
    #                         str(arr.shape),
    #                         is_compressed,
    #                     ]

    #                     if additional_columns:
    #                         columns = list(additional_columns.keys()) + columns
    #                         values = list(additional_columns.values()) + values

    #                     update_cols = [f"{col}=?" for col in columns]
    #                     query = f"UPDATE {table_name} SET {','.join(update_cols)} WHERE id=?"
    #                     values.append(id_)
    #                     self.execute(query, tuple(values))

    #             else:
    #                 if not isinstance(data, np.ndarray):
    #                     raise ValueError("Single input must be a NumPy array")

    #                 binary = data.tobytes()
    #                 if compress and len(binary) > 1024:  # Compress if > 1KB
    #                     binary = zlib.compress(binary, level=compress_level)
    #                     is_compressed = 1
    #                 else:
    #                     is_compressed = 0

    #                 columns = [
    #                     column,
    #                     f"{column}_dtype",
    #                     f"{column}_shape",
    #                     f"{column}_compressed",
    #                 ]
    #                 values = [
    #                     binary,
    #                     str(data.dtype),
    #                     str(data.shape),
    #                     is_compressed,
    #                 ]

    #                 if additional_columns:
    #                     columns = list(additional_columns.keys()) + columns
    #                     values = list(additional_columns.values()) + values

    #                 if where is not None:
    #                     update_cols = [f"{col}=?" for col in columns]
    #                     query = f"UPDATE {table_name} SET {','.join(update_cols)} WHERE {where}"
    #                     self.execute(query, tuple(values))
    #                 else:
    #                     placeholders = ",".join(["?" for _ in columns])
    #                     columns_str = ",".join(columns)
    #                     query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
    #                     self.execute(query, tuple(values))

    #         except Exception as err:
    #             raise ValueError(f"Failed to save array: {err}")

    def save_array(
        self,
        table_name: str,
        data: np.ndarray,
        column: str = "data",
        ids: Optional[Union[int, List[int]]] = None,
        where: str = None,
        additional_columns: Dict[str, _Any] = None,
        batch_size: int = 1000,
        compress: Optional[bool] = None,
        compress_level: int = 6,
    ) -> None:
        with self.lock:
            if not isinstance(data, (np.ndarray, list)):
                raise ValueError(
                    "Input must be a NumPy array or list of arrays"
                )

            if compress is None:
                compress = getattr(self, "compress_by_default", False)

            # Auto-add missing columns
            required_columns = [
                f"{column}_dtype",
                f"{column}_shape",
                f"{column}_compressed",
            ]

            for col in required_columns:
                try:
                    self.execute(
                        f"ALTER TABLE {table_name} ADD COLUMN {col} TEXT"
                    )
                except:
                    pass

            try:
                if ids is not None:
                    if isinstance(ids, int):
                        ids = [ids]
                        data = [data]
                    if len(ids) != len(data):
                        raise ValueError(
                            "Length of ids must match number of arrays"
                        )

                    for id_, arr in zip(ids, data):
                        if not isinstance(arr, np.ndarray):
                            raise ValueError(
                                f"Element for id {id_} must be a NumPy array"
                            )

                        binary = arr.tobytes()
                        if compress and len(binary) > 1024:
                            binary = zlib.compress(
                                binary, level=compress_level
                            )
                            is_compressed = 1
                        else:
                            is_compressed = 0

                        columns = [
                            column,
                            f"{column}_dtype",
                            f"{column}_shape",
                            f"{column}_compressed",
                        ]
                        values = [
                            binary,
                            str(arr.dtype),
                            str(arr.shape),
                            is_compressed,
                        ]

                        if additional_columns:
                            columns = list(additional_columns.keys()) + columns
                            values = list(additional_columns.values()) + values

                        update_cols = [f"{col}=?" for col in columns]
                        query = f"UPDATE {table_name} SET {','.join(update_cols)} WHERE id=?"
                        values.append(id_)
                        self.execute(query, tuple(values))

                else:
                    if not isinstance(data, np.ndarray):
                        raise ValueError("Single input must be a NumPy array")

                    binary = data.tobytes()
                    if compress and len(binary) > 1024:
                        binary = zlib.compress(binary, level=compress_level)
                        is_compressed = 1
                    else:
                        is_compressed = 0

                    columns = [
                        column,
                        f"{column}_dtype",
                        f"{column}_shape",
                        f"{column}_compressed",
                    ]
                    values = [
                        binary,
                        str(data.dtype),
                        str(data.shape),
                        is_compressed,
                    ]

                    if additional_columns:
                        columns = list(additional_columns.keys()) + columns
                        values = list(additional_columns.values()) + values

                    if where is not None:
                        update_cols = [f"{col}=?" for col in columns]
                        query = f"UPDATE {table_name} SET {','.join(update_cols)} WHERE {where}"
                        self.execute(query, tuple(values))
                    else:
                        placeholders = ",".join(["?" for _ in columns])
                        columns_str = ",".join(columns)
                        query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
                        self.execute(query, tuple(values))

            except Exception as err:
                raise ValueError(f"Failed to save array: {err}")

    def load_array(
        self,
        table_name: str,
        column: str,
        ids: Union[int, List[int], str] = "all",
        where: str = None,
        order_by: str = None,
        batch_size: int = 128,
        dtype: np.dtype = None,
        shape: Optional[Tuple] = None,
    ) -> Optional[np.ndarray]:
        try:
            if ids == "all":
                query = f"SELECT id FROM {table_name}"
                if where:
                    query += f" WHERE {where}"
                self.cursor.execute(query)
                ids = [row[0] for row in self.cursor.fetchall()]
            elif isinstance(ids, int):
                ids = [ids]

            id_to_data = {}
            unique_ids = list(set(ids))

            for idx in range(0, len(unique_ids), batch_size):
                batch_ids = unique_ids[idx : idx + batch_size]
                placeholders = ",".join("?" for _ in batch_ids)

                try:
                    query = f"""
                        SELECT id, {column},
                               {column}_dtype,
                               {column}_shape,
                               {column}_compressed
                        FROM {table_name}
                        WHERE id IN ({placeholders})
                    """
                    self.cursor.execute(query, tuple(batch_ids))
                    has_metadata = True
                    has_compression = True
                except sqlite3.OperationalError:
                    try:
                        query = f"""
                            SELECT id, {column},
                                   {column}_dtype,
                                   {column}_shape
                            FROM {table_name}
                            WHERE id IN ({placeholders})
                        """
                        self.cursor.execute(query, tuple(batch_ids))
                        has_metadata = True
                        has_compression = False
                    except sqlite3.OperationalError:
                        query = f"SELECT id, {column} FROM {table_name} WHERE id IN ({placeholders})"
                        self.cursor.execute(query, tuple(batch_ids))
                        has_metadata = False
                        has_compression = False

                if where:
                    query += f" AND {where}"
                if order_by:
                    query += f" ORDER BY {order_by}"

                results = self.cursor.fetchall()
                if results:
                    for result in results:
                        if has_metadata and has_compression:
                            (
                                id_val,
                                blob,
                                dtype_str,
                                shape_str,
                                is_compressed,
                            ) = result
                            if is_compressed:
                                blob = zlib.decompress(blob)
                            data = np.frombuffer(
                                blob, dtype=np.dtype(dtype_str)
                            ).reshape(eval(shape_str))
                        elif has_metadata:
                            id_val, blob, dtype_str, shape_str = result
                            data = np.frombuffer(
                                blob, dtype=np.dtype(dtype_str)
                            ).reshape(eval(shape_str))
                        else:
                            id_val, blob = result
                            data = (
                                np.frombuffer(blob, dtype=dtype)
                                if dtype
                                else np.frombuffer(blob)
                            )
                            if shape:
                                data = data.reshape(shape)
                        id_to_data[id_val] = data

            all_data = [
                id_to_data[id_val] for id_val in ids if id_val in id_to_data
            ]
            return np.stack(all_data, axis=0) if all_data else None

        except Exception as err:
            raise ValueError(f"Failed to load array: {err}")

    def binary_to_array(
        self,
        binary_data,
        dtype_str=None,
        shape_str=None,
        dtype=None,
        shape=None,
    ):
        if binary_data is None:
            return None

        if dtype_str and shape_str:
            return np.frombuffer(
                binary_data, dtype=np.dtype(dtype_str)
            ).reshape(eval(shape_str))
        elif dtype and shape:
            return np.frombuffer(binary_data, dtype=dtype).reshape(shape)
        return binary_data

    # def get_array_dict(self, df, columns=None, dtype=None, shape=None):
    #     result = {}
    #     if columns is None:
    #         columns = [
    #             col
    #             for col in df.columns
    #             if not (col.endswith("_dtype") or col.endswith("_shape"))
    #         ]

    #     for col in columns:
    #         if f"{col}_dtype" in df.columns and f"{col}_shape" in df.columns:
    #             arrays = [
    #                 self.binary_to_array(
    #                     row[col], row[f"{col}_dtype"], row[f"{col}_shape"]
    #                 )
    #                 for _, row in df.iterrows()
    #             ]
    #         elif dtype and shape:
    #             arrays = [
    #                 self.binary_to_array(x, dtype=dtype, shape=shape)
    #                 for x in df[col]
    #             ]
    #         result[col] = np.stack(arrays)

    #     return result

    # def decode_array_columns(self, df, columns=None, dtype=None, shape=None):
    #     if columns is None:
    #         columns = [
    #             col
    #             for col in df.columns
    #             if not (col.endswith("_dtype") or col.endswith("_shape"))
    #         ]

    #     for col in columns:
    #         if f"{col}_dtype" in df.columns and f"{col}_shape" in df.columns:
    #             df[col] = df.apply(
    #                 lambda row: self.binary_to_array(
    #                     row[col], row[f"{col}_dtype"], row[f"{col}_shape"]
    #                 ),
    #                 axis=1,
    #             )
    #         elif dtype and shape:
    #             df[col] = df[col].apply(
    #                 lambda x: self.binary_to_array(x, dtype=dtype, shape=shape)
    #             )
    #     return df

    def get_array_dict(self, df, columns=None, dtype=None, shape=None):
        result = {}
        if columns is None:
            columns = [
                col
                for col in df.columns
                if not (
                    col.endswith("_dtype")
                    or col.endswith("_shape")
                    or col.endswith("_compressed")
                )
            ]

        for col in columns:
            if f"{col}_dtype" in df.columns and f"{col}_shape" in df.columns:
                arrays = [
                    self.binary_to_array(
                        row[col], row[f"{col}_dtype"], row[f"{col}_shape"]
                    )
                    for _, row in df.iterrows()
                ]
            elif dtype and shape:
                arrays = [
                    self.binary_to_array(x, dtype=dtype, shape=shape)
                    for x in df[col]
                ]
            result[col] = np.stack(arrays)

        return result

    def decode_array_columns(self, df, columns=None, dtype=None, shape=None):
        if columns is None:
            columns = [
                col
                for col in df.columns
                if not (
                    col.endswith("_dtype")
                    or col.endswith("_shape")
                    or col.endswith("_compressed")
                )
            ]

        for col in columns:
            if f"{col}_dtype" in df.columns and f"{col}_shape" in df.columns:
                df[col] = df.apply(
                    lambda row: self.binary_to_array(
                        row[col], row[f"{col}_dtype"], row[f"{col}_shape"]
                    ),
                    axis=1,
                )
            elif dtype and shape:
                df[col] = df[col].apply(
                    lambda x: self.binary_to_array(x, dtype=dtype, shape=shape)
                )
        return df

    def save_blob(
        self,
        table_name: str,
        data: _Any,
        key: str,
        compress: Optional[bool] = None,  # None means use database default
        compress_level: int = 6,
        metadata: Optional[Dict[str, _Any]] = None,
    ) -> None:
        """Save any Python object as compressed blob with automatic queueing.

        Perfect for HPC with dynamic parallelism - SQLite handles conflicts.

        Parameters
        ----------
        table_name : str
            Table name (created if not exists)
        data : Any
            Any Python object to save
        key : str
            Unique key for this data
        compress : bool
            Use compression (default: True)
        compress_level : int
            Compression level 1-9 (default: 6)
        metadata : dict, optional
            Additional metadata to store
        """
        import os
        import time

        # Use database default if compress not explicitly specified
        if compress is None:
            compress = getattr(self, "compress_by_default", False)

        # Create table if not exists
        self.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                key TEXT PRIMARY KEY,
                timestamp REAL,
                pid INTEGER,
                hostname TEXT,
                data BLOB,
                compressed INTEGER,
                data_type TEXT,
                metadata TEXT
            )
        """
        )

        # Serialize data
        if isinstance(data, np.ndarray):
            data_bytes = data.tobytes()
            data_type = f"ndarray:{data.dtype}:{data.shape}"
        else:
            data_bytes = pickle.dumps(data, protocol=pickle.HIGHEST_PROTOCOL)
            data_type = "pickle"

        # Compress if requested
        if compress and len(data_bytes) > 1024:
            original_size = len(data_bytes)
            data_bytes = zlib.compress(data_bytes, level=compress_level)
            is_compressed = 1
            if metadata is None:
                metadata = {}
            metadata["original_size"] = original_size
            metadata["compressed_size"] = len(data_bytes)
        else:
            is_compressed = 0

        # Save with automatic queueing (SQLite handles conflicts)
        import json

        self.execute(
            f"""
            INSERT OR REPLACE INTO {table_name}
            (key, timestamp, pid, hostname, data, compressed, data_type, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                key,
                time.time(),
                os.getpid(),
                os.uname().nodename,
                data_bytes,
                is_compressed,
                data_type,
                json.dumps(metadata) if metadata else None,
            ),
        )
        self.commit()

    def load_blob(
        self,
        table_name: str,
        key: Optional[str] = None,
        where: Optional[str] = None,
    ) -> Union[_Any, Dict[str, _Any]]:
        """Load compressed blob data.

        Parameters
        ----------
        table_name : str
            Table name
        key : str, optional
            Specific key to load. If None, loads all.
        where : str, optional
            SQL WHERE clause

        Returns
        -------
        Loaded object(s)
        """
        if key:
            # Load specific key
            result = self.execute(
                f"""
                SELECT data, compressed, data_type
                FROM {table_name}
                WHERE key = ?
            """,
                (key,),
            ).fetchone()

            if result is None:
                raise KeyError(f"Key '{key}' not found")

            data_bytes, is_compressed, data_type = result

            # Decompress if needed
            if is_compressed:
                data_bytes = zlib.decompress(data_bytes)

            # Deserialize
            if data_type.startswith("ndarray:"):
                _, dtype_str, shape_str = data_type.split(":", 2)
                arr = np.frombuffer(data_bytes, dtype=np.dtype(dtype_str))
                return arr.reshape(eval(shape_str))
            else:
                return pickle.loads(data_bytes)

        else:
            # Load all or filtered
            query = (
                f"SELECT key, data, compressed, data_type FROM {table_name}"
            )
            if where:
                query += f" WHERE {where}"

            results = {}
            for key, data_bytes, is_compressed, data_type in self.execute(
                query
            ):
                if is_compressed:
                    data_bytes = zlib.decompress(data_bytes)

                if data_type.startswith("ndarray:"):
                    _, dtype_str, shape_str = data_type.split(":", 2)
                    arr = np.frombuffer(data_bytes, dtype=np.dtype(dtype_str))
                    results[key] = arr.reshape(eval(shape_str))
                else:
                    results[key] = pickle.loads(data_bytes)

            return results

# EOF
