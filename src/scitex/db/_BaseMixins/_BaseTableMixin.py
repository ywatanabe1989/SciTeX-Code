#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-24 22:21:17 (ywatanabe)"
# File: ./scitex_repo/src/scitex/db/_Basemodules/_BaseTableMixin.py

THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/db/_Basemodules/_BaseTableMixin.py"


#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Any, Dict, List, Union


class _BaseTableMixin:
    def create_table(
        self,
        table_name: str,
        columns: Dict[str, str],
        foreign_keys: List[Dict[str, str]] = None,
        if_not_exists: bool = True,
    ) -> None:
        raise NotImplementedError

    def drop_table(self, table_name: str, if_exists: bool = True) -> None:
        raise NotImplementedError

    def rename_table(self, old_name: str, new_name: str) -> None:
        raise NotImplementedError

    def add_columns(
        self,
        table_name: str,
        columns: Dict[str, str],
        default_values: Dict[str, Any] = None,
    ) -> None:
        raise NotImplementedError

    def add_column(
        self,
        table_name: str,
        column_name: str,
        column_type: str,
        default_value: Any = None,
    ) -> None:
        raise NotImplementedError

    def drop_columns(
        self, table_name: str, columns: Union[str, List[str]], if_exists: bool = True
    ) -> None:
        raise NotImplementedError

    def get_table_names(self) -> List[str]:
        raise NotImplementedError

    def get_table_schema(self, table_name: str):
        raise NotImplementedError

    def get_primary_key(self, table_name: str) -> str:
        raise NotImplementedError

    def get_table_stats(self, table_name: str) -> Dict[str, int]:
        raise NotImplementedError


# EOF
