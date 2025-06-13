#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-02-27 22:14:45 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_dev/src/scitex/db/_PostgreSQLMixins/_BlobMixin.py

THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/db/_PostgreSQLMixins/_BlobMixin.py"

import psycopg2
import numpy as np
from typing import Any as _Any
from typing import Dict, List, Optional, Tuple, Union
from .._BaseMixins._BaseBlobMixin import _BaseBlobMixin


class _BlobMixin(_BaseBlobMixin):
    """BLOB data handling functionality for PostgreSQL"""

    def save_array(
        self,
        table_name: str,
        data: np.ndarray,
        column: str = "data",
        ids: Optional[Union[int, List[int]]] = None,
        where: str = None,
        additional_columns: Dict[str, _Any] = None,
        batch_size: int = 1000,
    ) -> None:
        with self.transaction():
            if not isinstance(data, (np.ndarray, list)):
                raise ValueError("Input must be a NumPy array or list of arrays")

            try:
                if ids is not None:
                    if isinstance(ids, int):
                        ids = [ids]
                        data = [data]
                    if len(ids) != len(data):
                        raise ValueError("Length of ids must match number of arrays")

                    for id_, arr in zip(ids, data):
                        if not isinstance(arr, np.ndarray):
                            raise ValueError(
                                f"Element for id {id_} must be a NumPy array"
                            )

                        binary = psycopg2.Binary(arr.tobytes())
                        # binary = Binary(arr.tobytes())
                        columns = [
                            column,
                            f"{column}_dtype",
                            f"{column}_shape",
                        ]
                        values = [binary, str(arr.dtype), str(arr.shape)]

                        if additional_columns:
                            columns = list(additional_columns.keys()) + columns
                            values = list(additional_columns.values()) + values

                        update_cols = [f"{col}=%s" for col in columns]
                        query = f"UPDATE {table_name} SET {','.join(update_cols)} WHERE id=%s"
                        values.append(id_)
                        self.execute(query, values)

                else:
                    if not isinstance(data, np.ndarray):
                        raise ValueError("Single input must be a NumPy array")

                    binary = psycopg2.Binary(arr.tobytes())
                    # binary = Binary(data.tobytes())
                    columns = [column, f"{column}_dtype", f"{column}_shape"]
                    values = [binary, str(data.dtype), str(data.shape)]

                    if additional_columns:
                        columns = list(additional_columns.keys()) + columns
                        values = list(additional_columns.values()) + values

                    if where is not None:
                        update_cols = [f"{col}=%s" for col in columns]
                        query = f"UPDATE {table_name} SET {','.join(update_cols)} WHERE {where}"
                        self.execute(query, values)
                    else:
                        placeholders = ",".join(["%s" for _ in columns])
                        columns_str = ",".join(columns)
                        query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
                        self.execute(query, values)

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
                self.execute(query)
                ids = [row[0] for row in self.cursor.fetchall()]
            elif isinstance(ids, int):
                ids = [ids]

            id_to_data = {}
            unique_ids = list(set(ids))

            for idx in range(0, len(unique_ids), batch_size):
                batch_ids = unique_ids[idx : idx + batch_size]
                placeholders = ",".join(["%s" for _ in batch_ids])

                try:
                    query = f"""
                        SELECT id, {column},
                               {column}_dtype,
                               {column}_shape
                        FROM {table_name}
                        WHERE id IN ({placeholders})
                    """
                    self.execute(query, batch_ids)
                    has_metadata = True
                except psycopg2.Error:
                    query = f"SELECT id, {column} FROM {table_name} WHERE id IN ({placeholders})"
                    self.execute(query, batch_ids)
                    has_metadata = False

                if where:
                    query += f" AND {where}"
                if order_by:
                    query += f" ORDER BY {order_by}"

                results = self.cursor.fetchall()
                if results:
                    for result in results:
                        if has_metadata:
                            id_val, blob, dtype_str, shape_str = result
                            data = np.frombuffer(
                                bytes(blob), dtype=np.dtype(dtype_str)
                            ).reshape(eval(shape_str))
                        else:
                            id_val, blob = result
                            data = (
                                np.frombuffer(bytes(blob), dtype=dtype)
                                if dtype
                                else np.frombuffer(bytes(blob))
                            )
                            if shape:
                                data = data.reshape(shape)
                        id_to_data[id_val] = data

            all_data = [id_to_data[id_val] for id_val in ids if id_val in id_to_data]
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

        binary_data = bytes(binary_data)
        if dtype_str and shape_str:
            return np.frombuffer(binary_data, dtype=np.dtype(dtype_str)).reshape(
                eval(shape_str)
            )
        elif dtype and shape:
            return np.frombuffer(binary_data, dtype=dtype).reshape(shape)
        return binary_data

    def get_array_dict(self, df, columns=None, dtype=None, shape=None):
        result = {}
        if columns is None:
            columns = [
                col
                for col in df.columns
                if not (col.endswith("_dtype") or col.endswith("_shape"))
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
                    self.binary_to_array(x, dtype=dtype, shape=shape) for x in df[col]
                ]
            result[col] = np.stack(arrays)

        return result

    def decode_array_columns(self, df, columns=None, dtype=None, shape=None):
        if columns is None:
            columns = [
                col
                for col in df.columns
                if not (col.endswith("_dtype") or col.endswith("_shape"))
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


# EOF
