#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-11 14:16:58 (ywatanabe)"
# File: ./scitex_repo/src/scitex/db/_delete_duplicates.py

import sqlite3
from typing import List, Optional, Tuple, Union
import pandas as pd

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-10-20 02:17:10 (ywatanabe)"
# /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/db/_delete_duplicates_clean.py


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


def _sort_db(cursor: sqlite3.Cursor, table_name: str, columns: List[str]) -> None:
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
        columns = (
            all_columns
            if include_blob
            else [col for col in all_columns if column_types[col].lower() != "blob"]
        )
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
    print(f"\n{100*duplication_rate:.2f}% of data was duplicated. Cleaning up...")
    print(f"\nOriginal entries:\n{df.head()}")
    print(f"\nDuplicated entries:\n{df_duplicated.head()}")
    return df_duplicated


def verify_duplicated_index(
    cursor: sqlite3.Cursor, duplicated_row: pd.Series, table_name: str, dry_run: bool
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
        print(f"Skipping entry (not found or already deleted):\n{duplicated_row}")


# def delete_duplicates(
#     lpath_db: str,
#     table_name: str,
#     columns: Union[str, List[str]] = "all",
#     include_blob: bool = False,
#     batch_size: int = 1000,
#     reindex: bool = False,
#     sort: bool = False,
#     dry_run: bool = True,
# ) -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame]]:
#     """
#     Delete duplicate entries from an SQLite database table.

#     Parameters
#     ----------
#     lpath_db : str
#         Path to the SQLite database file.
#     table_name : str
#         Name of the table to remove duplicates from.
#     columns : Union[str, List[str]], optional
#         Columns to consider when identifying duplicates. Default is "all".
#     include_blob : bool, optional
#         Whether to include BLOB columns when considering duplicates. Default is False.
#     batch_size : int, optional
#         Number of rows to process in each batch. Default is 1000.
#     reindex : bool, optional
#         Whether to reindex the table after deletion. Default is False.
#     dry_run : bool, optional
#         If True, simulates the deletion without actually modifying the database. Default is True.

#     Returns
#     -------
#     Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame]]
#         A tuple containing:
#         - DataFrame of all entries after deletion process
#         - DataFrame of remaining duplicates if any, None otherwise
#     """
#     try:
#         conn = sqlite3.connect(lpath_db)
#         cursor = conn.cursor()

#         columns = _determine_columns(cursor, table_name, columns, include_blob)

#         if sort:
#             _sort_db(cursor, table_name, columns)

#         df_orig = _fetch_as_df(cursor, columns, table_name)
#         duplicates = _find_duplicated(df_orig)

#         if duplicates.empty:
#             print("Congratulations. Database is clean.")
#             return df_orig, None

#         columns_str = ", ".join(columns)
#         where_conditions = " AND ".join([f"{col} = ?" for col in columns])
#         delete_query = f"""
#             DELETE FROM {table_name}
#             WHERE {where_conditions}
#         """

#         for start in tqdm(range(0, len(duplicates), batch_size)):
#             batch = duplicates.iloc[start:start+batch_size]
#             batch_values = batch.values.tolist()

#             if dry_run:
#                 print(f"[DRY RUN] Would delete {len(batch)} entries")
#             else:
#                 cursor.executemany(delete_query, batch_values)
#                 conn.commit()

#         if not dry_run:
#             conn.commit()

#             if reindex:
#                 print("Reindexing the table...")
#                 cursor.execute(f"REINDEX {table_name}")
#                 conn.commit()

#         df_after = _fetch_as_df(cursor, columns, table_name)
#         remaining_duplicates = _find_duplicated(df_after)

#         if remaining_duplicates.empty:
#             print("All duplicates successfully removed.")
#             return df_after, None
#         else:
#             print(f"Warning: {len(remaining_duplicates)} duplicates still remain.\n{remaining_duplicates}")
#             return df_after, remaining_duplicates

#     except Exception as error:
#         print(f"An error occurred: {error}")
#         return None, None

#     finally:
#         conn.close()

# def delete_duplicates(
#     lpath_db: str,
#     table_name: str,
#     columns: Union[str, List[str]] = "all",
#     include_blob: bool = False,
#     batch_size: int = 1000,
#     chunk_size: int = 100_000,
#     reindex: bool = False,
#     sort: bool = False,
#     dry_run: bool = True,
# ) -> Tuple[Optional[int], Optional[int]]:
#     try:
#         conn = sqlite3.connect(lpath_db)
#         cursor = conn.cursor()

#         columns = _determine_columns(cursor, table_name, columns, include_blob)

#         if sort:
#             _sort_db(cursor, table_name, columns)

#         columns_str = ", ".join(columns)
#         where_conditions = " AND ".join([f"{col} = ?" for col in columns])
#         delete_query = f"""
#             DELETE FROM {table_name}
#             WHERE {where_conditions}
#         """

#         total_rows = cursor.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
#         total_deleted = 0
#         total_duplicates = 0

#         for offset in tqdm(range(0, total_rows, chunk_size)):
#             chunk_query = f"""
#                 SELECT {columns_str}
#                 FROM {table_name}
#                 LIMIT {chunk_size} OFFSET {offset}
#             """
#             df_chunk = pd.read_sql_query(chunk_query, conn)
#             duplicates = _find_duplicated(df_chunk)
#             total_duplicates += len(duplicates)

#             if duplicates.empty:
#                 continue

#             for start in range(0, len(duplicates), batch_size):
#                 batch = duplicates.iloc[start:start+batch_size]
#                 batch_values = batch.values.tolist()

#                 if dry_run:
#                     print(f"[DRY RUN] Would delete {len(batch)} entries")
#                 else:
#                     cursor.executemany(delete_query, batch_values)
#                     conn.commit()
#                     total_deleted += len(batch)

#         if not dry_run:
#             if reindex:
#                 print("Reindexing the table...")
#                 cursor.execute(f"REINDEX {table_name}")
#                 conn.commit()

#         print(f"Total duplicates found: {total_duplicates}")
#         print(f"Total entries deleted: {total_deleted}")

#         return total_duplicates, total_deleted

#     except Exception as error:
#         print(f"An error occurred: {error}")
#         return None, None

#     finally:
#         conn.close()


def delete_duplicates(
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

        # Create a temporary table to store unique rows
        temp_table = f"{table_name}_temp"
        cursor.execute(
            f"CREATE TABLE {temp_table} AS SELECT DISTINCT {columns_str} FROM {table_name} LIMIT 0"
        )

        # Process in small chunks
        offset = 0
        total_processed = 0
        total_unique = 0

        while True:
            chunk_query = f"""
                INSERT OR IGNORE INTO {temp_table}
                SELECT DISTINCT {columns_str}
                FROM {table_name}
                LIMIT {chunk_size} OFFSET {offset}
            """

            if dry_run:
                print(f"[DRY RUN] Would execute: {chunk_query}")
            else:
                cursor.execute(chunk_query)
                conn.commit()

            rows_affected = cursor.rowcount
            if rows_affected == 0:
                break

            total_processed += chunk_size
            total_unique += rows_affected
            offset += chunk_size

            print(f"Processed {total_processed} rows, {total_unique} unique")

        total_duplicates = total_processed - total_unique

        if not dry_run:
            # Replace original table with the deduplicated one
            cursor.execute(f"DROP TABLE {table_name}")
            cursor.execute(f"ALTER TABLE {temp_table} RENAME TO {table_name}")
            conn.commit()

        print(f"Total rows processed: {total_processed}")
        print(f"Total unique rows: {total_unique}")
        print(f"Total duplicates removed: {total_duplicates}")

        return total_processed, total_duplicates

    except Exception as error:
        print(f"An error occurred: {error}")
        return None, None

    finally:
        conn.close()


# EOF
