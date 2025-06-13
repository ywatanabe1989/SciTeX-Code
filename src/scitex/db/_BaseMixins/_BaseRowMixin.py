#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-24 22:21:03 (ywatanabe)"
# File: ./scitex_repo/src/scitex/db/_Basemodules/_BaseRowMixin.py

THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/db/_Basemodules/_BaseRowMixin.py"


#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List, Optional


class _BaseRowMixin:
    def get_rows(
        self,
        table_name: str,
        columns: List[str] = None,
        where: str = None,
        order_by: str = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        return_as: str = "dataframe",
    ):
        raise NotImplementedError

    def get_row_count(self, table_name: str = None, where: str = None) -> int:
        raise NotImplementedError


# EOF
