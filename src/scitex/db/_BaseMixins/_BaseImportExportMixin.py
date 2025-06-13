#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-24 22:20:15 (ywatanabe)"
# File: ./scitex_repo/src/scitex/db/_Basemodules/_BaseImportExportMixin.py

THIS_FILE = (
    "/home/ywatanabe/proj/scitex_repo/src/scitex/db/_Basemodules/_BaseImportExportMixin.py"
)


#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List


class _BaseImportExportMixin:
    def load_from_csv(
        self,
        table_name: str,
        csv_path: str,
        if_exists: str = "append",
        batch_size: int = 10_000,
        chunk_size: int = 100_000,
    ) -> None:
        raise NotImplementedError

    def save_to_csv(
        self,
        table_name: str,
        output_path: str,
        columns: List[str] = ["*"],
        where: str = None,
        batch_size: int = 10_000,
    ) -> None:
        raise NotImplementedError


# EOF
