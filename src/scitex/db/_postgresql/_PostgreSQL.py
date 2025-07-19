#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-25 02:00:06 (ywatanabe)"
# File: ./scitex_repo/src/scitex/db/_postgresql/_PostgreSQL.py

THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/db/_postgresql/_PostgreSQL.py"

from typing import List, Optional

from ...str import printc as _printc
from typing import Optional
import psycopg2
from ._PostgreSQLMixins._BackupMixin import _BackupMixin
from ._PostgreSQLMixins._BatchMixin import _BatchMixin
from ._PostgreSQLMixins._ConnectionMixin import _ConnectionMixin
from ._PostgreSQLMixins._ImportExportMixin import _ImportExportMixin
from ._PostgreSQLMixins._IndexMixin import _IndexMixin
from ._PostgreSQLMixins._MaintenanceMixin import _MaintenanceMixin
from ._PostgreSQLMixins._QueryMixin import _QueryMixin
from ._PostgreSQLMixins._RowMixin import _RowMixin
from ._PostgreSQLMixins._SchemaMixin import _SchemaMixin
from ._PostgreSQLMixins._TableMixin import _TableMixin
from ._PostgreSQLMixins._TransactionMixin import _TransactionMixin
from ._PostgreSQLMixins._BlobMixin import _BlobMixin


class PostgreSQL(
    _BackupMixin,
    _BatchMixin,
    _ConnectionMixin,
    _ImportExportMixin,
    _IndexMixin,
    _MaintenanceMixin,
    _QueryMixin,
    _RowMixin,
    _SchemaMixin,
    _TableMixin,
    _TransactionMixin,
    _BlobMixin,
):

    def __init__(
        self,
        dbname: Optional[str] = None,
        user: str = None,
        password: str = None,
        host: str = "localhost",
        port: int = 5432,
    ):
        super().__init__(
            dbname=dbname, user=user, password=password, host=host, port=port
        )

    def __call__(
        self,
        return_summary=False,
        print_summary=True,
        table_names: Optional[List[str]] = None,
        verbose: bool = True,
        limit: int = 5,
    ):
        """Display or return database summary."""
        summary = self.get_summaries(
            table_names=table_names,
            verbose=verbose,
            limit=limit,
        )

        if print_summary:
            for k, v in summary.items():
                _printc(f"{k}\n{v}")

        if return_summary:
            return summary

    @property
    def summary(self):
        """Property to quickly access database summary."""
        self()


# class BaseSQLiteDB(
#     _ConnectionMixin,
#     _QueryMixin,
#     _TransactionMixin,
#     _TableMixin,
#     _IndexMixin,
#     _RowMixin,
#     _BatchMixin,
#     _BlobMixin,
#     _ImportExportMixin,
#     _MaintenanceMixin,
# ):
#     """Comprehensive SQLite database management class."""

#     def __init__(self, db_path: str, use_temp: bool = False):
#         """Initializes database with option for temporary copy."""
#         _ConnectionMixin.__init__(self, db_path, use_temp)

#     def __call__(
#         self,
#         return_summary=False,
#         print_summary=True,
#         table_names: Optional[List[str]] = None,
#         verbose: bool = True,
#         limit: int = 5,
#     ):
#         summary = self.get_summaries(
#             table_names=table_names,
#             verbose=verbose,
#             limit=limit,
#         )

#         if print_summary:
#             for k, v in summary.items():
#                 _printc(f"{k}\n{v}")

#         if return_summary:
#             return summary

#     @property
#     def summary(self):
#         self()


# EOF
