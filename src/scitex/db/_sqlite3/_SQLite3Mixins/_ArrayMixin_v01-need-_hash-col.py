#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-14 00:03:40 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/db/_sqlite3/_SQLite3Mixins/_ArrayMixin.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/db/_sqlite3/_SQLite3Mixins/_ArrayMixin.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import hashlib
import logging
import zlib
from typing import Any
from typing import Any as _Any
from typing import Dict, List, Optional, Tuple, Union

import numpy as np

logger = logging.getLogger(__name__)


class _ArrayMixin:
    """Array data handling functionality"""

    def save_arrays(
        self,
        table_name: str,
        data: Dict[str, np.ndarray],
        ids: Optional[Union[int, List[int]]] = None,
        additional_columns: Dict[str, Any] = None,
        compress: Optional[bool] = None,
        compress_level: int = 6,
        verbose: bool = True,
    ) -> None:
        """Save multiple arrays to multiple columns in one operation.

        Parameters
        ----------
        table_name : str
            Name of the table
        data : dict
            Dictionary mapping column names to numpy arrays
        ids : int, list of int, optional
            Row ID(s) to update. If None, inserts new row
        additional_columns : dict, optional
            Additional non-array columns to save
        compress : bool, optional
            Whether to compress arrays. If None, uses database default
        compress_level : int, default 6
            Compression level (1-9)
        verbose : bool, default True
            Whether to print status messages
        """
        self.ensure_connection()
        with self.lock:
            if compress is None:
                compress = getattr(self, "compress_by_default", False)

            # Auto-add columns for all arrays
            for column in data.keys():
                for suffix in ["_dtype", "_shape", "_is_compressed", "_hash"]:
                    try:
                        self.execute(
                            f"ALTER TABLE {table_name} ADD COLUMN {column}{suffix} TEXT"
                        )
                    except:
                        pass

            # Prepare all columns and values
            all_columns = []
            all_values = []

            for column, arr in data.items():
                if not isinstance(arr, np.ndarray):
                    raise ValueError(f"{column} must be a NumPy array")

                # Calculate hash from original array data
                array_hash = hashlib.sha256(arr.tobytes()).hexdigest()[:16]
                
                binary = arr.tobytes()
                if compress and len(binary) > 1024:
                    binary = zlib.compress(binary, level=compress_level)
                    is_compressed = True
                else:
                    is_compressed = False

                all_columns.extend(
                    [
                        column,
                        f"{column}_dtype",
                        f"{column}_shape",
                        f"{column}_is_compressed",
                        f"{column}_hash",
                    ]
                )
                all_values.extend(
                    [binary, str(arr.dtype), str(arr.shape), is_compressed, array_hash]
                )

            if additional_columns:
                all_columns = list(additional_columns.keys()) + all_columns
                all_values = list(additional_columns.values()) + all_values

            # Single insert/update
            if ids is not None:
                update_cols = [f"{col}=?" for col in all_columns]
                query = f"UPDATE {table_name} SET {','.join(update_cols)} WHERE id=?"
                all_values.append(ids if isinstance(ids, int) else ids[0])
            else:
                placeholders = ",".join(["?" for _ in all_columns])
                columns_str = ",".join(all_columns)
                query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"

            self.execute(query, tuple(all_values))

            if verbose:
                logger.info(
                    f"Saved {len(data)} arrays to `{table_name}` table in `{self.db_path}`"
                )

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
        verbose: bool = True,
    ) -> None:
        """Save numpy array to database column.

        Parameters
        ----------
        table_name : str
            Name of the table
        data : np.ndarray
            Numpy array to save
        column : str, default "data"
            Column name for the array
        ids : int, list of int, optional
            Row ID(s) to update. If None, inserts new row
        where : str, optional
            WHERE clause for update (ignored if ids provided)
        additional_columns : dict, optional
            Additional non-array columns to save
        batch_size : int, default 1000
            Batch size for operations (not used)
        compress : bool, optional
            Whether to compress. If None, uses database default
        compress_level : int, default 6
            Compression level (1-9)
        verbose : bool, default True
            Whether to print status messages
        """

        self.save_arrays(
            table_name=table_name,
            data={column: data},
            ids=ids,
            where=where,
            additional_columns=additional_columns,
            compress=compress,
            compress_level=compress_level,
            verbose=verbose,
        )

    def load_arrays(
        self,
        table_name: str,
        columns: Union[List[str], str] = "all",
        ids: Union[int, List[int], str] = "all",
        where: str = None,
        batch_size: int = 128,
        verbose: bool = True,
    ) -> Dict[str, np.ndarray]:
        """Load multiple array columns in one query.

        Parameters
        ----------
        table_name : str
            Name of the table
        columns : list of str or "all", default "all"
            Column names to load, default "all"
        ids : int, list of int, or "all", default "all"
            Row IDs to load. "all" loads all rows
        where : str, optional
            WHERE clause to filter rows
        batch_size : int, default 128
            Batch size for loading
        verbose : bool, default True
            Whether to print status messages

        Returns
        -------
        dict
            Dictionary mapping column names to stacked arrays
        """
        self.ensure_connection()
        self._check_context_manager()

        if columns == "all":
            all_table_columns = self.get_table_schema(table_name)[
                "name"
            ].tolist()
            array_columns = []
            for col in all_table_columns:
                if (
                    (f"{col}_dtype" in all_table_columns)
                    and (f"{col}_shape" in all_table_columns)
                    and (f"{col}_is_compressed" in all_table_columns)
                    # _hash might not exist in older databases, so make it optional
                ):
                    array_columns.append(col)
        else:
            array_columns = columns if isinstance(columns, list) else [columns]

        query_columns = ["id"]
        for col in array_columns:
            query_columns.extend(
                [col, f"{col}_dtype", f"{col}_shape", f"{col}_is_compressed", f"{col}_hash"]
            )

        df = self.get_rows(
            table_name=table_name,
            columns=query_columns,
            ids=ids,
            where=where,
            return_as="dataframe",
        )

        result = {}
        for array_col in array_columns:
            arrays = []
            valid_arrays = []

            for _, row in df.iterrows():
                blob = row[array_col]
                if blob is not None:
                    if row.get(f"{array_col}_is_compressed"):
                        blob = zlib.decompress(blob)
                    arr = np.frombuffer(
                        blob, dtype=np.dtype(row[f"{array_col}_dtype"])
                    ).reshape(eval(row[f"{array_col}_shape"]))
                    valid_arrays.append(arr)

            if valid_arrays:
                ref_shape = valid_arrays[0].shape
                ref_dtype = valid_arrays[0].dtype

                for _, row in df.iterrows():
                    blob = row[array_col]
                    if blob is None:
                        arr = np.full(ref_shape, np.nan, dtype=ref_dtype)
                    else:
                        if row.get(f"{array_col}_is_compressed"):
                            blob = zlib.decompress(blob)
                        arr = np.frombuffer(
                            blob, dtype=np.dtype(row[f"{array_col}_dtype"])
                        ).reshape(eval(row[f"{array_col}_shape"]))
                    arrays.append(arr)

                result[array_col] = np.stack(arrays) if arrays else None
            else:
                result[array_col] = None

        if verbose:
            print(
                f"Loaded {len(array_columns)} array columns from {table_name}"
            )

        return result

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
        verbose: bool = True,
    ) -> Optional[np.ndarray]:
        """Load numpy array from database column.

        Parameters
        ----------
        table_name : str
            Name of the table
        column : str
            Column name containing the array
        ids : int, list of int, or "all", default "all"
            Row IDs to load. "all" loads all rows
        where : str, optional
            WHERE clause to filter rows
        order_by : str, optional
            ORDER BY clause (not used)
        batch_size : int, default 128
            Batch size for loading
        dtype : np.dtype, optional
            Data type hint (not used)
        shape : tuple, optional
            Shape hint (not used)
        verbose : bool, default True
            Whether to print status messages

        Returns
        -------
        np.ndarray or None
            Stacked array or None if no data
        """

        result = self.load_arrays(
            table_name=table_name,
            columns=[column],
            ids=ids,
            where=where,
            batch_size=batch_size,
            verbose=verbose,
        )
        return result.get(column) if result else None

    # def binary_to_array(
    #     self,
    #     binary_data,
    #     dtype_str=None,
    #     shape_str=None,
    #     dtype=None,
    #     shape=None,
    # ):
    #     """Convert binary data to numpy array.

    #     Parameters
    #     ----------
    #     binary_data : bytes
    #         Binary array data
    #     dtype_str : str, optional
    #         String representation of dtype
    #     shape_str : str, optional
    #         String representation of shape
    #     dtype : np.dtype, optional
    #         Numpy dtype (used if dtype_str not provided)
    #     shape : tuple, optional
    #         Array shape (used if shape_str not provided)

    #     Returns
    #     -------
    #     np.ndarray or bytes
    #         Decoded array or original binary if no metadata
    #     """

    #     if binary_data is None:
    #         return None

    #     if dtype_str and shape_str:
    #         return np.frombuffer(
    #             binary_data, dtype=np.dtype(dtype_str)
    #         ).reshape(eval(shape_str))
    #     elif dtype and shape:
    #         return np.frombuffer(binary_data, dtype=dtype).reshape(shape)
    #     return binary_data

    def binary_to_array(
        self,
        binary_data,
        dtype_str=None,
        shape_str=None,
        dtype=None,
        shape=None,
        compressed=False,
    ):
        if binary_data is None:
            return None

        # Decompress if needed
        if compressed:
            binary_data = zlib.decompress(binary_data)

        if dtype_str and shape_str:
            return np.frombuffer(
                binary_data, dtype=np.dtype(dtype_str)
            ).reshape(eval(shape_str))
        elif dtype and shape:
            return np.frombuffer(binary_data, dtype=dtype).reshape(shape)
        return binary_data

    def get_array_dict(self, df, columns=None, dtype=None, shape=None):
        """Extract arrays from dataframe columns into dictionary.

        Parameters
        ----------
        df : pd.DataFrame
            Dataframe with binary array data
        columns : list of str, optional
            Columns to decode. If None, decodes all array columns
        dtype : np.dtype, optional
            Fallback dtype if metadata missing
        shape : tuple, optional
            Fallback shape if metadata missing

        Returns
        -------
        dict
            Dictionary mapping column names to stacked arrays
        """

        result = {}
        if columns is None:
            columns = [
                col
                for col in df.columns
                if not (
                    col.endswith("_dtype")
                    or col.endswith("_shape")
                    or col.endswith("_is_compressed")
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

    # def decode_array_columns(self, df, columns=None, dtype=None, shape=None):
    #     """Decode binary array columns in-place in dataframe.

    #     Parameters
    #     ----------
    #     df : pd.DataFrame
    #         Dataframe with binary array data
    #     columns : list of str, optional
    #         Columns to decode. If None, decodes all array columns
    #     dtype : np.dtype, optional
    #         Fallback dtype if metadata missing
    #     shape : tuple, optional
    #         Fallback shape if metadata missing

    #     Returns
    #     -------
    #     pd.DataFrame
    #         Same dataframe with decoded arrays
    #     """

    #     if columns is None:
    #         columns = [
    #             col
    #             for col in df.columns
    #             if not (
    #                 col.endswith("_dtype")
    #                 or col.endswith("_shape")
    #                 or col.endswith("_is_compressed")
    #             )
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

    def decode_array_columns(self, df, columns=None, dtype=None, shape=None):
        if columns is None:
            columns = [
                col
                for col in df.columns
                if not (
                    col.endswith("_dtype")
                    or col.endswith("_shape")
                    or col.endswith("_is_compressed")
                )
            ]

        for col in columns:
            if f"{col}_dtype" in df.columns and f"{col}_shape" in df.columns:
                df[col] = df.apply(
                    lambda row: self.binary_to_array(
                        row[col],
                        row[f"{col}_dtype"],
                        row[f"{col}_shape"],
                        compressed=row.get(f"{col}_is_compressed", False),
                    ),
                    axis=1,
                )
            elif dtype and shape:
                df[col] = df[col].apply(
                    lambda x: self.binary_to_array(x, dtype=dtype, shape=shape)
                )
        return df

# EOF
