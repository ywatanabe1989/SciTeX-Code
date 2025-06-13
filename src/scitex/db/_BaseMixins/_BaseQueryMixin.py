#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-24 22:17:03 (ywatanabe)"
# File: ./scitex_repo/src/scitex/db/_Basemodules/_BaseQueryMixin.py

THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/db/_Basemodules/_BaseQueryMixin.py"

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List, Dict, Any, Optional, Union, Tuple


class _BaseQueryMixin:
    def select(
        self,
        table: str,
        columns: Optional[List[str]] = None,
        where: Optional[str] = None,
        params: Optional[tuple] = None,
        order_by: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        raise NotImplementedError

    def insert(self, table: str, data: Dict[str, Any]) -> None:
        raise NotImplementedError

    def update(
        self,
        table: str,
        data: Dict[str, Any],
        where: str,
        params: Optional[tuple] = None,
    ) -> int:
        raise NotImplementedError

    def delete(self, table: str, where: str, params: Optional[tuple] = None) -> int:
        raise NotImplementedError

    def execute_query(
        self, query: str, params: Optional[tuple] = None
    ) -> List[Dict[str, Any]]:
        raise NotImplementedError

    def count(
        self, table: str, where: Optional[str] = None, params: Optional[tuple] = None
    ) -> int:
        raise NotImplementedError


# EOF
