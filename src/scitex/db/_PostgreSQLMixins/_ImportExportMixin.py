#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-02-27 22:14:59 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_dev/src/scitex/db/_PostgreSQLMixins/_ImportExportMixin.py

THIS_FILE = (
    "/home/ywatanabe/proj/scitex_repo/src/scitex/db/_PostgreSQLMixins/_ImportExportMixin.py"
)

import pandas as pd
from typing import List
import psycopg2
from io import StringIO


class _ImportExportMixin:
    def load_from_csv(
        self,
        table_name: str,
        csv_path: str,
        if_exists: str = "append",
        batch_size: int = 10_000,
        chunk_size: int = 100_000,
    ) -> None:
        with self.transaction():
            try:
                if if_exists == "replace":
                    self.execute(f"TRUNCATE TABLE {table_name}")

                copy_sql = f"COPY {table_name} FROM STDIN WITH CSV HEADER"
                with open(csv_path, "r") as f:
                    self.cursor.copy_expert(sql=copy_sql, file=f)

            except (Exception, psycopg2.Error) as err:
                raise ValueError(f"Failed to import from CSV: {err}")

    def save_to_csv(
        self,
        table_name: str,
        output_path: str,
        columns: List[str] = ["*"],
        where: str = None,
        batch_size: int = 10_000,
    ) -> None:
        try:
            columns_str = ", ".join(columns) if columns != ["*"] else "*"
            query = f"COPY (SELECT {columns_str} FROM {table_name}"
            if where:
                query += f" WHERE {where}"
            query += ") TO STDOUT WITH CSV HEADER"

            with open(output_path, "w") as f:
                self.cursor.copy_expert(sql=query, file=f)

        except (Exception, psycopg2.Error) as err:
            raise ValueError(f"Failed to export to CSV: {err}")


# EOF
