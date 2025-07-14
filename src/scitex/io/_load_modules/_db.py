#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-25 11:50:05 (ywatanabe)"
# File: ./scitex_repo/src/scitex/io/_load_modules/_db.py

THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/io/_load_modules/_db.py"

from typing import Any

from ...db import SQLite3


def _load_sqlite3db(lpath: str, use_temp=False) -> Any:
    if not lpath.endswith(".db"):
        raise ValueError("File must have .db extension")
    try:
        obj = SQLite3(lpath, use_temp=use_temp)

        return obj
    except Exception as e:
        raise ValueError(str(e))


# EOF
