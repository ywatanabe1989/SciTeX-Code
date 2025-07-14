#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-25 01:36:45 (ywatanabe)"
# File: ./scitex_repo/src/scitex/db/_SQLite3Mixins/_IndexMixin.py

THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/db/_SQLite3Mixins/_IndexMixin.py"

from typing import List
from ..._BaseMixins._BaseIndexMixin import _BaseIndexMixin


class _IndexMixin:
    """Index management functionality"""

    def create_index(
        self,
        table_name: str,
        column_names: List[str],
        index_name: str = None,
        unique: bool = False,
    ) -> None:
        if index_name is None:
            index_name = f"idx_{table_name}_{'_'.join(column_names)}"
        unique_clause = "UNIQUE" if unique else ""
        query = f"CREATE {unique_clause} INDEX IF NOT EXISTS {index_name} ON {table_name} ({','.join(column_names)})"
        self.execute(query)

    def drop_index(self, index_name: str) -> None:
        self.execute(f"DROP INDEX IF EXISTS {index_name}")


# EOF
