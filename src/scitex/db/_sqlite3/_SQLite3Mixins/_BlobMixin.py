#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-11 05:50:10 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/db/_sqlite3/_SQLite3Mixins/_BlobMixin.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/db/_sqlite3/_SQLite3Mixins/_BlobMixin.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import pickle
import zlib
from typing import Any as _Any
from typing import Dict, List, Optional, Union

import numpy as np


class _BlobMixin:
    """BLOB data handling functionality"""

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

        self.ensure_connection()

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

    # def load_blob(
    #     self,
    #     table_name: str,
    #     key: Optional[str] = None,
    #     where: Optional[str] = None,
    # ) -> Union[_Any, Dict[str, _Any]]:
    #     """Load compressed blob data.

    #     Parameters
    #     ----------
    #     table_name : str
    #         Table name
    #     key : str, optional
    #         Specific key to load. If None, loads all.
    #     where : str, optional
    #         SQL WHERE clause

    #     Returns
    #     -------
    #     Loaded object(s)
    #     """
    #     if key:
    #         # Load specific key
    #         result = self.execute(
    #             f"""
    #             SELECT data, compressed, data_type
    #             FROM {table_name}
    #             WHERE key = ?
    #         """,
    #             (key,),
    #         ).fetchone()

    #         if result is None:
    #             raise KeyError(f"Key '{key}' not found")

    #         data_bytes, is_compressed, data_type = result

    #         # Decompress if needed
    #         if is_compressed:
    #             data_bytes = zlib.decompress(data_bytes)

    #         # Deserialize
    #         if data_type.startswith("ndarray:"):
    #             _, dtype_str, shape_str = data_type.split(":", 2)
    #             arr = np.frombuffer(data_bytes, dtype=np.dtype(dtype_str))
    #             return arr.reshape(eval(shape_str))
    #         else:
    #             return pickle.loads(data_bytes)

    #     else:
    #         # Load all or filtered
    #         query = (
    #             f"SELECT key, data, compressed, data_type FROM {table_name}"
    #         )
    #         if where:
    #             query += f" WHERE {where}"

    #         results = {}
    #         for key, data_bytes, is_compressed, data_type in self.execute(
    #             query
    #         ):
    #             if is_compressed:
    #                 data_bytes = zlib.decompress(data_bytes)

    #             if data_type.startswith("ndarray:"):
    #                 _, dtype_str, shape_str = data_type.split(":", 2)
    #                 arr = np.frombuffer(data_bytes, dtype=np.dtype(dtype_str))
    #                 results[key] = arr.reshape(eval(shape_str))
    #             else:
    #                 results[key] = pickle.loads(data_bytes)

    #         return results

    def load_blob(
        self,
        table_name: str,
        key: Optional[str] = None,
        ids: Union[int, List[int], str] = "all",
        where: Optional[str] = None,
    ) -> Union[_Any, Dict[str, _Any]]:
        """Load compressed blob data.

        Parameters
        ----------
        table_name : str
            Table name
        key : str, optional
            Specific key to load. If None, loads all.
        ids : int, list of int, or "all", default "all"
            Row IDs to load. "all" loads all rows
        where : str, optional
            SQL WHERE clause

        Returns
        -------
        Loaded object(s)
        """
        self.ensure_connection()

        # Handle ids parameter
        if ids != "all":
            if isinstance(ids, int):
                id_where = f"id = {ids}"
            else:
                id_list = ",".join(map(str, ids))
                id_where = f"id IN ({id_list})"

            if where:
                where = f"({where}) AND ({id_where})"
            else:
                where = id_where

        if key:
            # Load specific key
            query = f"SELECT data, compressed, data_type FROM {table_name} WHERE key = ?"
            params = (key,)

            if where:
                query += f" AND {where}"

            result = self.execute(query, params).fetchone()

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
