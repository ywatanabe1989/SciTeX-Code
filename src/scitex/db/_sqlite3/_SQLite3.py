#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-11 07:57:49 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/db/_sqlite3/_SQLite3.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/db/_sqlite3/_SQLite3.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import warnings
from typing import List, Optional

from ...str import printc as _printc
from ._SQLite3Mixins._ArrayMixin import _ArrayMixin
from ._SQLite3Mixins._BatchMixin import _BatchMixin
from ._SQLite3Mixins._BlobMixin import _BlobMixin
from ._SQLite3Mixins._ColumnMixin import _ColumnMixin
from ._SQLite3Mixins._ConnectionMixin import _ConnectionMixin
from ._SQLite3Mixins._GitMixin import _GitMixin
from ._SQLite3Mixins._ImportExportMixin import _ImportExportMixin
from ._SQLite3Mixins._IndexMixin import _IndexMixin
from ._SQLite3Mixins._MaintenanceMixin import _MaintenanceMixin
from ._SQLite3Mixins._QueryMixin import _QueryMixin
from ._SQLite3Mixins._RowMixin import _RowMixin
from ._SQLite3Mixins._TableMixin import _TableMixin
from ._SQLite3Mixins._TransactionMixin import _TransactionMixin


class SQLite3(
    _ArrayMixin,
    _ConnectionMixin,
    _QueryMixin,
    _TransactionMixin,
    _ColumnMixin,
    _TableMixin,
    _IndexMixin,
    _RowMixin,
    _BatchMixin,
    _BlobMixin,
    _ImportExportMixin,
    _MaintenanceMixin,
    _GitMixin,
):
    """SQLite database manager with automatic metadata handling, numpy array storage, and compression.

    This class provides a comprehensive interface for SQLite database operations with
    automatic compression, thread-safe operations, and specialized numpy array handling.

    Features:
        - Automatic compression for BLOB data (70-90% reduction)
        - Thread-safe operations with proper connection management
        - Metadata handling for BLOB columns
        - Batch processing support
        - Context manager support for proper resource cleanup

    Examples:
        Basic usage with context manager (recommended):

        >>> with SQLite3("data.db", compress_by_default=True) as db:
        ...     db.create_table("experiments", {"id": "INTEGER PRIMARY KEY", "data": "BLOB"})
        ...     data = np.random.random((1000, 100))
        ...     db.save_array("experiments", data, column="data", additional_columns={"id": 1})

        Array storage and retrieval:

        >>> with SQLite3("data.db") as db:
        ...     # Save numpy array
        ...     db.save_array(
        ...         table_name="measurements",
        ...         data=np.random.random((1000, 100)),
        ...         column="data",
        ...         additional_columns={"name": "experiment_1", "timestamp": 1234567890}
        ...     )
        ...     # Load array
        ...     loaded = db.load_array("measurements", "data", where="name = 'experiment_1'")

        Generic object storage:

        >>> with SQLite3("data.db") as db:
        ...     db.save_blob(
        ...         table_name="objects",
        ...         data={"weights": array, "params": {"lr": 0.001}},
        ...         key="model_v1"
        ...     )
        ...     loaded_obj = db.load_blob("objects", key="model_v1")

    Notes:
        - Always use context manager (with statement) for proper resource cleanup
        - BLOB columns automatically get metadata columns: {column}_dtype, {column}_shape, {column}_compressed
        - Compression is enabled by default for arrays > 1KB
        - Thread-safe operations are supported
    """

    def __init__(
        self,
        db_path: str,
        use_temp: bool = False,
        compress_by_default: bool = False,
        autocommit: bool = False,
    ):
        """Initialize SQLite database manager.

        Parameters
        ----------
        db_path : str
            Path to the SQLite database file
        use_temp : bool, optional
            Whether to use a temporary copy of the database, by default False
        compress_by_default : bool, optional
            Whether to compress BLOB data by default when not explicitly specified, by default False
        autocommit : bool, optional
            Whether to automatically commit transactions, by default False

        Warnings
        --------
        UserWarning
            If not used with context manager, warns about potential resource leaks
        """

        if not os.path.exists(db_path):
            os.makedirs(os.path.dirname(db_path), exist_ok=True)

        _ConnectionMixin.__init__(self, db_path, use_temp)
        self.compress_by_default = compress_by_default
        self.autocommit = autocommit
        self._context_manager_used = False

    def __enter__(self):
        """Enter context manager."""
        self._context_manager_used = True
        return self

    def _check_context_manager(self):
        if not self._context_manager_used:
            raise RuntimeError(
                "SQLite3 must be used with context manager: 'with SQLite3(...) as db:'"
            )

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager and ensure proper cleanup."""
        self.close()

    def __del__(self):
        """Destructor with context manager usage warning."""
        if (
            hasattr(self, "_context_manager_used")
            and not self._context_manager_used
        ):
            warnings.warn(
                "SQLite3 instance was not used with context manager. "
                "Use 'with SQLite3(...) as db:' to ensure proper resource cleanup.",
                UserWarning,
                stacklevel=2,
            )
        if hasattr(self, "close"):
            self.close()

    def __call__(
        self,
        return_summary=False,
        print_summary=True,
        table_names: Optional[List[str]] = None,
        verbose: bool = True,
        limit: int = 5,
    ):
        """Display database summary information.

        Parameters
        ----------
        return_summary : bool, optional
            Whether to return summary dict, by default False
        print_summary : bool, optional
            Whether to print summary to console, by default True
        table_names : Optional[List[str]], optional
            Specific table names to summarize, by default None (all tables)
        verbose : bool, optional
            Whether to show detailed information, by default True
        limit : int, optional
            Maximum number of rows to display per table, by default 5

        Returns
        -------
        dict or None
            Summary dictionary if return_summary=True, else None
        """

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
        """Quick access to database summary."""
        self()


BaseSQLiteDB = SQLite3

# EOF
