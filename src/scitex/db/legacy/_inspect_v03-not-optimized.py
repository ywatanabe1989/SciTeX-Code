#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-10 07:39:43 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/db/_inspect.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/db/_inspect.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import sqlite3
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


class Inspector:
    def __init__(self, db_path: str):
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"Database file not found: {db_path}")
        self.db_path = db_path

    def get_table_names(self) -> List[str]:
        """Retrieves all table names from the database.

        Returns:
            List[str]: List of table names
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table';"
            )
            return [table[0] for table in cursor.fetchall()]

    def get_table_info(
        self, table_name: str
    ) -> List[Tuple[int, str, str, int, Any, int, str]]:
        """Retrieves table structure information.

        Args:
            table_name (str): Name of the table

        Returns:
            List[Tuple[int, str, str, int, Any, int, str]]: List of column information tuples
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()

            cursor.execute(f"PRAGMA index_list({table_name})")
            indexes = cursor.fetchall()
            pk_columns = []
            for idx in indexes:
                if idx[2] == 1:  # Is primary key
                    cursor.execute(f"PRAGMA index_info({idx[1]})")
                    pk_columns.extend([info[2] for info in cursor.fetchall()])

            enhanced_columns = []
            for col in columns:
                constraints = []
                if col[1] in pk_columns:
                    constraints.append("PRIMARY KEY")
                if col[3] == 1:
                    constraints.append("NOT NULL")
                enhanced_columns.append(col + (" ".join(constraints),))

            return enhanced_columns

    def get_sample_data(
        self, table_name: str, limit: int = 5
    ) -> Tuple[List[str], List[Tuple], int]:
        """Retrieves sample data from the specified table.

        Args:
            table_name (str): Name of the table
            limit (int, optional): Number of rows to retrieve. Defaults to 5.

        Returns:
            Tuple[List[str], List[Tuple], int]: Column names, sample data rows, and total row count
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
            columns = [description[0] for description in cursor.description]
            sample_data = cursor.fetchall()

            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            total_rows = cursor.fetchone()[0]

            return columns, sample_data, total_rows

    def inspect(
        self,
        table_names: Optional[List[str]] = None,
        verbose=True,
    ) -> List[Dict[str, Any]]:
        import pandas as pd

        if table_names is None:
            table_names = self.get_table_names()

        data_table_dfs = []
        for table_name in table_names:
            columns = self.get_table_info(table_name)
            column_names, rows, total_rows = self.get_sample_data(table_name)

            meta = {}
            meta["table_name"] = table_name
            meta["n_total_rows"] = total_rows

            sample_data = pd.DataFrame(
                [
                    {
                        col: (
                            str(value)
                            if not isinstance(value, bytes)
                            else "<BLOB>"
                        )
                        for col, value in zip(column_names, row)
                    }
                    for row in rows
                ]
            )

            for k, v in meta.items():
                sample_data[k] = v

            sample_data = sample_data.set_index(["table_name", "n_total_rows"])
            data_table_dfs.append(sample_data)

        return data_table_dfs


def pop_array_metadata(columns):
    pop_suffixes = ["_dtype", "_shape", "_compressed"]
    clean_columns = []
    for col in columns:
        if not any(col.endswith(pop_suffix) for pop_suffix in pop_suffixes):
            clean_columns.append(col)
    return clean_columns


def inspect(
    lpath_db: str,
    table_names: Optional[List[str]] = None,
    verbose: bool = True,
) -> None:
    """
    Inspects the specified SQLite database.

    Example:
    >>> inspect('path/to/database.db')
    >>> inspect('path/to/database.db', ['table1', 'table2'])

    Args:
        lpath_db (str): Path to the SQLite database file
        table_names (Optional[List[str]], optional): List of table names to inspect.
            If None, inspects all tables. Defaults to None.
    """
    inspector = Inspector(lpath_db)
    overviews_table_dfs = inspector.inspect(table_names, verbose=verbose)
    if verbose:
        for table_df in overviews_table_dfs:
            clean_columns = pop_array_metadata(table_df.columns.tolist())
            clean_table_df = table_df[clean_columns]
            print(f"\n{clean_table_df}\n")
            print(clean_table_df.iloc[0])
    return overviews_table_dfs


# python -c "import scitex; scitex.db.inspect(\"./data/pac/pac_db/Patient_23_002.db\")"
# python -c "import scitex; scitex.db.inspect(\"./data/pac/pac_db/Patient_23_002.db\", table_names=[\"eeg_data_reindexed\"])"
# python -c "import scitex; scitex.db.inspect(\"./data/pac/pac_db/Patient_23_002.db\", table_names=[\"eeg_data\"])"
# python -c "import scitex; scitex.db.inspect(\"./data/pac/pac_db/Patient_23_002.db\", table_names=[\"sqlite_sequence\"])"

# EOF
