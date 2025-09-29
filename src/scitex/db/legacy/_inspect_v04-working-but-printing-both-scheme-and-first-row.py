#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-11 07:14:35 (ywatanabe)"
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
from contextlib import contextmanager
from typing import Any, Dict, List, Optional


class OptimizedInspector:
    """Optimized database inspector with connection reuse and efficient queries."""

    def __init__(self, db_path: str):
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"Database file not found: {db_path}")
        self.db_path = db_path
        self._conn = None
        self._cursor = None

    @contextmanager
    def connection(self):
        """Context manager for database connection reuse."""
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path)
            self._conn.row_factory = (
                sqlite3.Row
            )  # Enable column access by name
            self._cursor = self._conn.cursor()
        try:
            yield self._cursor
        except Exception:
            self._conn.rollback()
            raise

    def close(self):
        """Close the database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None
            self._cursor = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def get_table_names(self) -> List[str]:
        """Retrieves all table names from the database."""
        with self.connection() as cursor:
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"
            )
            return [row[0] for row in cursor.fetchall()]

    def get_table_info_batch(
        self, table_names: List[str]
    ) -> Dict[str, List[Dict]]:
        """Get table info for multiple tables in one go.

        Returns:
            Dict mapping table_name to list of column info dictionaries
        """
        table_info = {}

        with self.connection() as cursor:
            for table_name in table_names:
                # Get column info
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()

                # Get primary key info more efficiently
                cursor.execute(
                    f"""
                    SELECT name FROM pragma_table_info('{table_name}')
                    WHERE pk > 0
                """
                )
                pk_columns = {row[0] for row in cursor.fetchall()}

                # Build column info
                col_info = []
                for col in columns:
                    col_dict = {
                        "cid": col[0],
                        "name": col[1],
                        "type": col[2],
                        "notnull": col[3],
                        "default": col[4],
                        "pk": col[1] in pk_columns,
                    }
                    col_info.append(col_dict)

                table_info[table_name] = col_info

        return table_info

    def get_table_stats_batch(
        self,
        table_names: List[str],
        sample_size: int = 5,
        skip_count: bool = False,
    ) -> Dict[str, Dict]:
        """Get statistics for multiple tables efficiently.

        Args:
            table_names: List of table names to inspect
            sample_size: Number of sample rows to retrieve
            skip_count: If True, skip the COUNT(*) query for performance

        Returns:
            Dict mapping table_name to statistics dictionary
        """
        stats = {}

        with self.connection() as cursor:
            for table_name in table_names:
                table_stats = {}

                # Get sample data
                cursor.execute(
                    f"SELECT * FROM {table_name} LIMIT {sample_size}"
                )
                table_stats["columns"] = [
                    desc[0] for desc in cursor.description
                ]
                table_stats["sample_data"] = cursor.fetchall()

                # Get row count (can be slow for large tables)
                if not skip_count:
                    # Use approximate count if available
                    cursor.execute(
                        f"""
                        SELECT COUNT(*) FROM (
                            SELECT 1 FROM {table_name} LIMIT 100000
                        )
                    """
                    )
                    approx_count = cursor.fetchone()[0]

                    if approx_count < 100000:
                        # Small table, get exact count
                        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                        table_stats["row_count"] = cursor.fetchone()[0]
                        table_stats["is_approximate"] = False
                    else:
                        # Large table, use approximate count
                        table_stats["row_count"] = f">{approx_count:,}"
                        table_stats["is_approximate"] = True
                else:
                    table_stats["row_count"] = "Not counted"
                    table_stats["is_approximate"] = None

                stats[table_name] = table_stats

        return stats

    def inspect_fast(
        self,
        table_names: Optional[List[str]] = None,
        sample_size: int = 5,
        skip_count: bool = False,
        skip_blob_content: bool = True,
        verbose: bool = True,
    ) -> List[Dict[str, Any]]:
        """Fast inspection of database tables.

        Args:
            table_names: Tables to inspect (None for all)
            sample_size: Number of sample rows
            skip_count: Skip row counting for performance
            skip_blob_content: Don't load BLOB content
            verbose: Print results

        Returns:
            List of inspection results
        """
        if table_names is None:
            table_names = self.get_table_names()

        # Batch operations for efficiency
        table_info = self.get_table_info_batch(table_names)
        table_stats = self.get_table_stats_batch(
            table_names, sample_size, skip_count
        )

        results = []
        for table_name in table_names:
            result = {
                "table_name": table_name,
                "columns": table_info[table_name],
                "row_count": table_stats[table_name]["row_count"],
                "is_approximate": table_stats[table_name]["is_approximate"],
                "sample_data": [],
            }

            # Format sample data
            for row in table_stats[table_name]["sample_data"]:
                formatted_row = {}
                for i, col_name in enumerate(
                    table_stats[table_name]["columns"]
                ):
                    value = row[i]
                    if isinstance(value, bytes):
                        if skip_blob_content:
                            formatted_row[col_name] = (
                                f"<BLOB {len(value)} bytes>"
                            )
                        else:
                            formatted_row[col_name] = value
                    else:
                        formatted_row[col_name] = value
                result["sample_data"].append(formatted_row)

            results.append(result)

            if verbose:
                self._print_table_info(result)

        return results

    def _print_table_info(self, result: Dict):
        """Pretty print table information."""
        print(f"\n{'='*60}")
        print(f"Table: {result['table_name']}")
        print(
            f"Rows: {result['row_count']}"
            + (" (approximate)" if result["is_approximate"] else "")
        )
        print(f"-" * 60)

        # Print column info
        print("Columns:")
        for col in result["columns"]:
            pk_marker = " [PK]" if col["pk"] else ""
            nn_marker = " NOT NULL" if col["notnull"] else ""
            print(f"  {col['name']}: {col['type']}{pk_marker}{nn_marker}")

        # Print sample data
        if result["sample_data"]:
            print(f"\nSample data ({len(result['sample_data'])} rows):")
            # Get column names that aren't metadata columns
            data_cols = [
                c
                for c in result["sample_data"][0].keys()
                if not c.endswith(("_dtype", "_shape", "_compressed"))
            ]

            # First show table format for overview (limited columns)
            if len(data_cols) > 5:
                print(f"\nTable view (first 5 of {len(data_cols)} columns):")
            else:
                print("\nTable view:")
            
            # Print header
            header = " | ".join(f"{col[:15]:<15}" for col in data_cols[:5])
            print(f"  {header}")
            print(f"  {'-'*len(header)}")

            # Print rows
            for row in result["sample_data"][:3]:
                values = []
                for col in data_cols[:5]:
                    val = str(row.get(col, ""))
                    if len(val) > 15:
                        val = val[:12] + "..."
                    values.append(f"{val:<15}")
                print(f"  {' | '.join(values)}")
            
            # Then show first row in detail (like df.iloc[0])
            print(f"\nFirst row details:")
            first_row = result["sample_data"][0]
            max_key_len = max(len(str(k)) for k in first_row.keys())
            
            for key, value in first_row.items():
                # Skip metadata columns in detailed view too
                if key.endswith(("_dtype", "_shape", "_compressed")):
                    continue
                    
                # Format value for display
                if isinstance(value, str) and len(value) > 50:
                    display_value = value[:47] + "..."
                elif value is None:
                    display_value = "NULL"
                else:
                    display_value = str(value)
                
                # Find column type
                col_type = ""
                for col in result["columns"]:
                    if col["name"] == key:
                        col_type = f" ({col['type']})"
                        break
                
                print(f"  {key:<{max_key_len}}: {display_value}{col_type}")


def inspect(
    lpath_db: str,
    table_names: Optional[List[str]] = None,
    sample_size: int = 5,
    skip_count: bool = False,
    verbose: bool = True,
) -> List[Dict[str, Any]]:
    """
    Optimized database inspection.

    Example:
    >>> inspect('path/to/database.db')
    >>> inspect('path/to/database.db', ['table1'], skip_count=True)

    Args:
        lpath_db: Path to the SQLite database file
        table_names: List of table names to inspect (None for all)
        sample_size: Number of sample rows to retrieve
        skip_count: Skip row counting for large tables (much faster)
        verbose: Print inspection results

    Returns:
        List of inspection results
    """
    with OptimizedInspector(lpath_db) as inspector:
        return inspector.inspect_fast(
            table_names=table_names,
            sample_size=sample_size,
            skip_count=skip_count,
            verbose=verbose,
        )

# EOF
