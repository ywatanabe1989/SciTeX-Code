#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-25 01:43:41 (ywatanabe)"
# File: ./scitex_repo/src/scitex/db/_BaseMixins/_BaseBatchMixin.py

THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/db/_BaseMixins/_BaseBatchMixin.py"

from typing import List, Any, Optional, Dict, Union
import pandas as pd


class _BaseBatchMixin:
    def insert_many(
        self,
        table: str,
        records: List[Dict[str, Any]],
        batch_size: Optional[int] = None,
    ):
        raise NotImplementedError

    def _prepare_insert_query(self, table: str, record: Dict[str, Any]) -> str:
        raise NotImplementedError

    def _prepare_batch_parameters(self, records: List[Dict[str, Any]]) -> tuple:
        raise NotImplementedError

    def dataframe_to_sql(self, df: pd.DataFrame, table: str, if_exists: str = "fail"):
        raise NotImplementedError


# EOF
