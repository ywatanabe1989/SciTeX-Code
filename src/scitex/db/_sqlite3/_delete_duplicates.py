#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-16 14:00:04 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/db/_sqlite3/_delete_duplicates.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/db/_sqlite3/_delete_duplicates.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
# Time-stamp: "2024-11-11 14:16:58 (ywatanabe)"

import sqlite3
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

import pandas as pd

"""
Functionality:
    - Deletes duplicate entries from an SQLite database table
Input:
    - SQLite database file path, table name, columns to consider for duplicates
Output:
    - Updated SQLite database with duplicates removed
Prerequisites:
    - sqlite3, pandas, tqdm, scitex
"""


def _sort_db(
    cursor: sqlite3.Cursor, table_name: str, columns: List[str]
) -> None:
    """
    Sorts the database table based on the specified columns.

    Parameters
    ----------
    cursor : sqlite3.Cursor
        The cursor object for executing SQL commands.
    table_name : str
        The name of the table to be sorted.
    columns : List[str]
        The list of column names to sort by, in order of priority.

    Example
    -------
    >>> conn = sqlite3.connect('example.db')
    >>> cursor = conn.cursor()
    >>> _sort_db(cursor, 'my_table', ['column1', 'column2'])
    >>> conn.commit()
    >>> conn.close()
    """
    columns_str = ", ".join(columns)
    temp_table = f"{table_name}_temp"

    cursor.execute(
        f"CREATE TABLE {temp_table} AS SELECT * FROM {table_name} ORDER BY {columns_str}"
    )
    cursor.execute(f"DROP TABLE {table_name}")
    cursor.execute(f"ALTER TABLE {temp_table} RENAME TO {table_name}")


# def _determine_columns(
#     cursor: sqlite3.Cursor,
#     table_name: str,
#     columns: Union[str, List[str]],
#     include_blob: bool,
# ) -> List[str]:
#     cursor.execute(f"PRAGMA table_info({table_name})")
#     table_info = cursor.fetchall()
#     all_columns = [col[1] for col in table_info]
#     column_types = {col[1]: col[2] for col in table_info}

#     if columns == "all":
#         columns = (
#             all_columns
#             if include_blob
#             else [
#                 col
#                 for col in all_columns
#                 if column_types[col].lower() != "blob"
#             ]
#         )
#     elif isinstance(columns, str):
#         columns = [columns]

#     columns_str = ", ".join(columns)
#     print(f"Columns considered for duplicates: {columns_str}")

#     return columns

def _determine_columns(
    cursor: sqlite3.Cursor,
    table_name: str,
    columns: Union[str, List[str]],
    include_blob: bool,
) -> List[str]:
    cursor.execute(f"PRAGMA table_info({table_name})")
    table_info = cursor.fetchall()
    all_columns = [col[1] for col in table_info]
    column_types = {col[1]: col[2] for col in table_info}

    if columns == "all":
        columns = all_columns
        # Exclude blob columns
        if not include_blob:
            columns = [col for col in columns if column_types[col].lower() != "blob"]
        # Exclude timestamp columns
        columns = [col for col in columns if not col.endswith("_at")]
    elif isinstance(columns, str):
        columns = [columns]

    columns_str = ", ".join(columns)
    print(f"Columns considered for duplicates: {columns_str}")

    return columns

def _fetch_as_df(
    cursor: sqlite3.Cursor, columns: List[str], table_name: str
) -> pd.DataFrame:
    print("\nFetching all database entries...")
    columns_str = ", ".join(columns)
    query = f"SELECT {columns_str} FROM {table_name}"
    cursor.execute(query)
    df_entries = cursor.fetchall()
    return pd.DataFrame(df_entries, columns=columns)


def _find_duplicated(df: pd.DataFrame) -> pd.DataFrame:
    df_duplicated = df[df.duplicated(keep="first")].copy()
    duplication_rate = len(df_duplicated) / (len(df) - len(df_duplicated))
    print(
        f"\n{100*duplication_rate:.2f}% of data was duplicated. Cleaning up..."
    )
    print(f"\nOriginal entries:\n{df.head()}")
    print(f"\nDuplicated entries:\n{df_duplicated.head()}")
    return df_duplicated


def verify_duplicated_index(
    cursor: sqlite3.Cursor,
    duplicated_row: pd.Series,
    table_name: str,
    dry_run: bool,
) -> Tuple[str, bool]:
    """Check if entry to delete is the one intended"""
    columns = list(duplicated_row.index)
    columns_str = ", ".join(columns)

    where_conditions = " AND ".join([f"{col} = ?" for col in columns])
    select_query = f"""
        SELECT {columns_str}
        FROM {table_name}
        WHERE {where_conditions}
    """
    cursor.execute(select_query, tuple(duplicated_row))
    entries = cursor.fetchall()

    is_verified = len(entries) >= 1

    if dry_run:
        print(f"Expected duplicate entry: {tuple(duplicated_row)}")
        print(f"Found entries: {entries}")
        print(f"Verification {'succeeded' if is_verified else 'failed'}")

    return select_query, is_verified


def _delete_entry(
    cursor: sqlite3.Cursor,
    duplicated_row: pd.Series,
    table_name: str,
    dry_run: bool = True,
) -> None:
    select_query, is_verified = verify_duplicated_index(
        cursor, duplicated_row, table_name, dry_run
    )
    if is_verified:
        delete_query = select_query.replace("SELECT", "DELETE")
        if dry_run:
            print(f"[DRY RUN] Would delete entry:\n{duplicated_row}")
        else:
            cursor.execute(delete_query, tuple(duplicated_row))
            print(f"Deleted entry:\n{duplicated_row}")
    else:
        print(
            f"Skipping entry (not found or already deleted):\n{duplicated_row}"
        )


def delete_sqlite3_duplicates(
    lpath_db: str,
    table_name: str,
    columns: Union[str, List[str]] = "all",
    include_blob: bool = False,
    chunk_size: int = 10_000,
    dry_run: bool = True,
) -> Tuple[Optional[int], Optional[int]]:
    try:
        conn = sqlite3.connect(lpath_db)
        cursor = conn.cursor()

        # Vacuum the database to free up space
        if not dry_run:
            cursor.execute("VACUUM")
            conn.commit()

        columns = _determine_columns(cursor, table_name, columns, include_blob)
        columns_str = ", ".join(columns)

        # Drop temp table if exists from previous run
        temp_table = f"{table_name}_temp"
        cursor.execute(f"DROP TABLE IF EXISTS {temp_table}")

        # Get all columns for creating temp table with same structure
        cursor.execute(f"PRAGMA table_info({table_name})")
        all_cols_info = cursor.fetchall()
        all_cols = [col[1] for col in all_cols_info]
        all_cols_str = ", ".join(all_cols)

        # Create temp table with same structure
        cursor.execute(f"CREATE TABLE {temp_table} AS SELECT {all_cols_str} FROM {table_name} LIMIT 0")

        # Get total row count
        total_rows = cursor.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        print(f"Total rows in table: {total_rows}")

        # Insert unique rows based on specified columns
        insert_query = f"""
            INSERT INTO {temp_table}
            SELECT {all_cols_str}
            FROM (
                SELECT *, ROW_NUMBER() OVER (PARTITION BY {columns_str} ORDER BY rowid) as rn
                FROM {table_name}
            )
            WHERE rn = 1
        """

        if dry_run:
            print(f"[DRY RUN] Would execute deduplication based on: {columns_str}")
        else:
            cursor.execute(insert_query)
            conn.commit()

        # Count unique rows
        total_unique = cursor.execute(f"SELECT COUNT(*) FROM {temp_table}").fetchone()[0]
        total_duplicates = total_rows - total_unique

        if not dry_run:
            # Replace original table with deduplicated one
            cursor.execute(f"DROP TABLE {table_name}")
            cursor.execute(f"ALTER TABLE {temp_table} RENAME TO {table_name}")
            cursor.execute("VACUUM")
            conn.commit()
        else:
            # Clean up temp table in dry run
            cursor.execute(f"DROP TABLE IF EXISTS {temp_table}")

        print(f"Total rows processed: {total_rows}")
        print(f"Total unique rows: {total_unique}")
        print(f"Total duplicates removed: {total_duplicates}")

        return total_rows, total_duplicates

    except Exception as error:
        print(f"An error occurred: {error}")
        return None, None

    finally:
        conn.close()

# EOF
