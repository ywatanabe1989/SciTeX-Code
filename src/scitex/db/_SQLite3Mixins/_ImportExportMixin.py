#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-25 01:36:18 (ywatanabe)"
# File: ./scitex_repo/src/scitex/db/_SQLite3Mixins/_ImportExportMixin.py

THIS_FILE = (
    "/home/ywatanabe/proj/scitex_repo/src/scitex/db/_SQLite3Mixins/_ImportExportMixin.py"
)

from typing import List

import pandas as pd

from .._BaseMixins._BaseImportExportMixin import _BaseImportExportMixin


class _ImportExportMixin:
    """Import/Export functionality"""

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
                for chunk in pd.read_csv(csv_path, chunksize=chunk_size):
                    chunk.to_sql(
                        table_name,
                        self.conn,
                        if_exists=if_exists,
                        index=False,
                        chunksize=batch_size,
                    )
                    if_exists = "append"
            except FileNotFoundError:
                raise FileNotFoundError(f"CSV file not found: {csv_path}")
            except Exception as err:
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
            df = self.get_rows(
                columns=columns,
                table_name=table_name,
                where=where,
                limit=batch_size,
                offset=0,
            )
            df.to_csv(output_path, index=False, mode="w")

            offset = batch_size
            while len(df) == batch_size:
                df = self.get_rows(
                    columns=columns,
                    table_name=table_name,
                    where=where,
                    limit=batch_size,
                    offset=offset,
                )
                if len(df) > 0:
                    df.to_csv(output_path, index=False, mode="a", header=False)
                offset += batch_size
        except PermissionError:
            raise PermissionError(f"Cannot write to: {output_path}")
        except Exception as err:
            raise ValueError(f"Failed to export to CSV: {err}")


# EOF
