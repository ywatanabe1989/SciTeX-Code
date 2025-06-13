#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-11 14:17:00 (ywatanabe)"
# File: ./scitex_repo/src/scitex/db/_inspect.py

import os
import sqlite3
from typing import Any, Dict, List, Optional, Tuple

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-10-24 13:13:33 (ywatanabe)"
# /mnt/ssd/scitex_repo/src/scitex/db/_inspect.py


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
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
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

        data_tables = []
        for table_name in table_names:
            columns = self.get_table_info(table_name)
            column_names, rows, total_rows = self.get_sample_data(table_name)

            meta = {}
            meta["table_name"] = table_name
            meta["n_total_rows"] = total_rows

            sample_data = pd.DataFrame(
                [
                    {
                        col: (str(value) if not isinstance(value, bytes) else "<BLOB>")
                        for col, value in zip(column_names, row)
                    }
                    for row in rows
                ]
            )

            for k, v in meta.items():
                sample_data[k] = v

            sample_data = sample_data.set_index(["table_name", "n_total_rows"])

            data_tables.append(sample_data)

        # if len(data_tables) == 1:
        #     return data_tables[0]
        # else:
        #     return tuple(data_tables)
        return data_tables


def inspect(
    lpath_db: str, table_names: Optional[List[str]] = None, verbose: bool = True
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
    overviews_tables = inspector.inspect(table_names, verbose=verbose)
    if verbose:
        for dd in overviews_tables:
            print(f"\n{dd}\n")
    return overviews_tables


# python -c "import scitex; scitex.db.inspect(\"./data/db_all/Patient_23_005.db\")"
# python -c "import scitex; scitex.db.inspect(\"./data/db_all/Patient_23_005.db\", table_names=[\"eeg_data_reindexed\"])"
# python -c "import scitex; scitex.db.inspect(\"./data/db_all/Patient_23_005.db\", table_names=[\"eeg_data\"])"
# python -c "import scitex; scitex.db.inspect(\"./data/db_all/Patient_23_005.db\", table_names=[\"sqlite_sequence\"])"


# EOF
