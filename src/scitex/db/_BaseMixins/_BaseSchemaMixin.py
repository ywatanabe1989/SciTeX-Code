#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-24 22:14:24 (ywatanabe)"
# File: ./scitex_repo/src/scitex/db/_Basemodules/_BaseSchemaMixin.py

THIS_FILE = (
    "/home/ywatanabe/proj/scitex_repo/src/scitex/db/_Basemodules/_BaseSchemaMixin.py"
)

from typing import List, Dict, Any, Optional


class _BaseSchemaMixin:
    def get_tables(self) -> List[str]:
        raise NotImplementedError

    def get_columns(self, table: str) -> List[Dict[str, Any]]:
        raise NotImplementedError

    def get_primary_keys(self, table: str) -> List[str]:
        raise NotImplementedError

    def get_foreign_keys(self, table: str) -> List[Dict[str, Any]]:
        raise NotImplementedError

    def get_indexes(self, table: str) -> List[Dict[str, Any]]:
        raise NotImplementedError

    def table_exists(self, table: str) -> bool:
        raise NotImplementedError

    def column_exists(self, table: str, column: str) -> bool:
        raise NotImplementedError

    def create_index(
        self, table: str, columns: List[str], index_name: Optional[str] = None
    ) -> None:
        raise NotImplementedError

    def drop_index(self, index_name: str) -> None:
        raise NotImplementedError


# EOF
