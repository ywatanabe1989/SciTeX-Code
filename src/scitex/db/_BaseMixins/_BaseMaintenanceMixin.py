#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-24 22:12:07 (ywatanabe)"
# File: ./scitex_repo/src/scitex/db/_Basemodules/_BaseMaintenanceMixin.py

THIS_FILE = (
    "/home/ywatanabe/proj/scitex_repo/src/scitex/db/_Basemodules/_BaseMaintenanceMixin.py"
)

from typing import Optional, List, Dict


class _BaseMaintenanceMixin:
    def vacuum(self, table: Optional[str] = None):
        raise NotImplementedError

    def analyze(self, table: Optional[str] = None):
        raise NotImplementedError

    def reindex(self, table: Optional[str] = None):
        raise NotImplementedError

    def get_table_size(self, table: str):
        raise NotImplementedError

    def get_database_size(self):
        raise NotImplementedError

    def get_table_info(self) -> List[Dict]:
        raise NotImplementedError


# EOF
