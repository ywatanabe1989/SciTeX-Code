#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-02-27 22:14:16 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_dev/src/scitex/db/_PostgreSQLMixins/_BatchMixin.py

THIS_FILE = (
    "/home/ywatanabe/proj/scitex_repo/src/scitex/db/_PostgreSQLMixins/_BatchMixin.py"
)

from typing import List, Any, Optional, Dict, Union
import pandas as pd
from ..._BaseMixins._BaseBatchMixin import _BaseBatchMixin


class _BatchMixin(_BaseBatchMixin):
    def insert_many(
        self,
        table: str,
        records: List[Dict[str, Any]],
        batch_size: Optional[int] = None,
    ) -> None:
        if not records:
            return

        query = self._prepare_insert_query(table, records[0])
        if batch_size and batch_size > 0:
            for i in range(0, len(records), batch_size):
                batch = records[i : i + batch_size]
                parameters = self._prepare_batch_parameters(batch)
                self.executemany(query, parameters)
        else:
            parameters = self._prepare_batch_parameters(records)
            self.executemany(query, parameters)

    def _prepare_insert_query(self, table: str, record: Dict[str, Any]) -> str:
        columns = list(record.keys())
        placeholders = ["%s"] * len(columns)
        columns_str = ", ".join(columns)
        placeholders_str = ", ".join(placeholders)
        return f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders_str})"

    def _prepare_batch_parameters(self, records: List[Dict[str, Any]]) -> List[tuple]:
        if not records:
            return []

        columns = list(records[0].keys())
        return [tuple(record[col] for col in columns) for record in records]

    def dataframe_to_sql(
        self, df: pd.DataFrame, table: str, if_exists: str = "fail"
    ) -> None:
        if if_exists not in ["fail", "replace", "append"]:
            raise ValueError("if_exists must be one of 'fail', 'replace', or 'append'")

        if if_exists == "replace":
            self.execute(f"DROP TABLE IF EXISTS {table}")
            # Create table based on DataFrame schema
            columns = []
            for col, dtype in df.dtypes.items():
                pg_type = self._map_dtype_to_postgres(dtype)
                columns.append(f"{col} {pg_type}")
            columns_str = ", ".join(columns)
            self.execute(f"CREATE TABLE {table} ({columns_str})")

        records = df.to_dict("records")
        self.insert_many(table, records)

    def _map_dtype_to_postgres(self, dtype) -> str:
        dtype_str = str(dtype)
        if "int" in dtype_str:
            return "INTEGER"
        elif "float" in dtype_str:
            return "REAL"
        elif "datetime" in dtype_str:
            return "TIMESTAMP"
        elif "bool" in dtype_str:
            return "BOOLEAN"
        else:
            return "TEXT"


# EOF
