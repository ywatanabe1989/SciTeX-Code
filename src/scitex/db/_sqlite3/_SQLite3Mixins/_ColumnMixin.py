#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-11 08:00:00 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/SciTeX-Code/src/scitex/db/_sqlite3/_SQLite3Mixins/_ColumnMixin.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import time
from scitex import logging
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class _ColumnMixin:
    """Efficient column operations for SQLite3 databases.
    
    Handles drop, rename, reorder, add, and modify operations
    with automatic version detection and optimization.
    """
    
    def get_sqlite_version(self) -> Tuple[int, int, int]:
        """Get SQLite version as tuple (major, minor, patch)."""
        cursor = self.cursor
        cursor.execute("SELECT sqlite_version()")
        version_str = cursor.fetchone()[0]
        parts = version_str.split(".")
        return tuple(int(p) for p in parts[:3])
    
    def supports_drop_column(self) -> bool:
        """Check if SQLite supports DROP COLUMN (3.35.0+)."""
        version = self.get_sqlite_version()
        return version >= (3, 35, 0)
    
    def supports_rename_column(self) -> bool:
        """Check if SQLite supports RENAME COLUMN (3.25.0+)."""
        version = self.get_sqlite_version()
        return version >= (3, 25, 0)
    
    def get_column_info(self, table_name: str) -> List[Dict[str, Any]]:
        """Get detailed information about table columns."""
        cursor = self.cursor
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = []
        for row in cursor.fetchall():
            columns.append({
                "cid": row[0],
                "name": row[1],
                "type": row[2],
                "notnull": row[3],
                "default": row[4],
                "pk": row[5],
            })
        return columns
    
    def column_exists(self, table_name: str, column_name: str) -> bool:
        """Check if a column exists in the table."""
        columns = self.get_column_info(table_name)
        return any(col["name"] == column_name for col in columns)
    
    # ----------------------------------------
    # DROP Operations
    # ----------------------------------------
    
    def drop_column(
        self,
        table_name: str,
        column_name: str,
        force_recreate: bool = False,
        progress_callback: Optional[callable] = None,
    ) -> bool:
        """Drop a column from table, using native or recreation method.
        
        Args:
            table_name: Name of the table
            column_name: Name of column to drop
            force_recreate: Force table recreation even if native DROP is available
            progress_callback: Function to call with progress updates
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if column exists
            if not self.column_exists(table_name, column_name):
                logger.warning(f"Column {column_name} does not exist in {table_name}")
                return False
            
            # Use native DROP if available and not forced to recreate
            if self.supports_drop_column() and not force_recreate:
                return self._drop_column_native(table_name, column_name)
            else:
                return self._drop_column_recreate(table_name, column_name, progress_callback)
                
        except Exception as e:
            logger.error(f"Failed to drop column {column_name} from {table_name}: {e}")
            return False
    
    def _drop_column_native(self, table_name: str, column_name: str) -> bool:
        """Drop column using native SQLite ALTER TABLE DROP COLUMN."""
        try:
            cursor = self.cursor
            cursor.execute(f"ALTER TABLE {table_name} DROP COLUMN {column_name}")
            self.conn.commit()
            logger.info(f"Dropped column {column_name} from {table_name} (native)")
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Native drop failed: {e}")
            return False
    
    def _drop_column_recreate(
        self,
        table_name: str,
        column_name: str,
        progress_callback: Optional[callable] = None,
    ) -> bool:
        """Drop column by recreating the table (for older SQLite versions)."""
        try:
            cursor = self.cursor
            # Start transaction
            cursor.execute("BEGIN EXCLUSIVE TRANSACTION")
            
            # Get columns to keep
            columns = self.get_column_info(table_name)
            keep_columns = [col for col in columns if col["name"] != column_name]
            
            if not keep_columns:
                raise ValueError("Cannot drop all columns from table")
            
            # Create column list for new table
            column_names = [col["name"] for col in keep_columns]
            column_defs = []
            for col in keep_columns:
                col_def = f"{col['name']} {col['type']}"
                if col["notnull"]:
                    col_def += " NOT NULL"
                if col["default"] is not None:
                    col_def += f" DEFAULT {col['default']}"
                if col["pk"]:
                    col_def += " PRIMARY KEY"
                column_defs.append(col_def)
            
            # Get row count for progress
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            total_rows = cursor.fetchone()[0]
            
            if progress_callback:
                progress_callback(0, total_rows, "Creating temporary table")
            
            # Create temporary table
            temp_table = f"{table_name}_temp_{int(time.time())}"
            cursor.execute(f"""
                CREATE TABLE {temp_table} (
                    {', '.join(column_defs)}
                )
            """)
            
            # Copy data in batches for progress reporting
            batch_size = 10000
            offset = 0
            
            while offset < total_rows:
                cursor.execute(f"""
                    INSERT INTO {temp_table} ({', '.join(column_names)})
                    SELECT {', '.join(column_names)}
                    FROM {table_name}
                    LIMIT {batch_size} OFFSET {offset}
                """)
                
                offset += batch_size
                if progress_callback:
                    progress_callback(min(offset, total_rows), total_rows, "Copying data")
            
            # Get indexes, triggers, and views
            cursor.execute(f"""
                SELECT sql FROM sqlite_master
                WHERE type IN ('index', 'trigger', 'view')
                AND tbl_name = '{table_name}'
                AND sql IS NOT NULL
            """)
            dependencies = cursor.fetchall()
            
            # Drop old table
            cursor.execute(f"DROP TABLE {table_name}")
            
            # Rename temp table
            cursor.execute(f"ALTER TABLE {temp_table} RENAME TO {table_name}")
            
            # Recreate indexes, triggers, and views
            for dep in dependencies:
                sql = dep[0]
                # Skip if it references the dropped column
                if column_name not in sql:
                    try:
                        cursor.execute(sql)
                    except Exception as e:
                        logger.warning(f"Could not recreate dependency: {e}")
            
            # Commit transaction
            self.conn.commit()
            
            if progress_callback:
                progress_callback(total_rows, total_rows, "Complete")
            
            logger.info(f"Dropped column {column_name} from {table_name} (recreate)")
            return True
            
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Table recreation failed: {e}")
            return False
    
    # ----------------------------------------
    # RENAME Operations
    # ----------------------------------------
    
    def rename_column(self, table_name: str, old_name: str, new_name: str) -> bool:
        """Rename a column in the table.
        
        Args:
            table_name: Name of the table
            old_name: Current column name
            new_name: New column name
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.column_exists(table_name, old_name):
                logger.error(f"Column {old_name} does not exist in {table_name}")
                return False
            
            if self.column_exists(table_name, new_name):
                logger.error(f"Column {new_name} already exists in {table_name}")
                return False
            
            if self.supports_rename_column():
                # Use native RENAME COLUMN
                cursor = self.cursor
                cursor.execute(f"""
                    ALTER TABLE {table_name}
                    RENAME COLUMN {old_name} TO {new_name}
                """)
                self.conn.commit()
                logger.info(f"Renamed column {old_name} to {new_name} in {table_name}")
                return True
            else:
                # Use table recreation for older versions
                return self._rename_column_recreate(table_name, old_name, new_name)
                
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Failed to rename column: {e}")
            return False
    
    def _rename_column_recreate(self, table_name: str, old_name: str, new_name: str) -> bool:
        """Rename column by recreating the table."""
        # Similar to drop_column_recreate but with renamed column
        # Implementation would be similar to _drop_column_recreate
        # but keeping all columns with one renamed
        logger.warning("Column rename via recreation not yet implemented")
        return False
    
    # ----------------------------------------
    # REORDER/SORT Operations
    # ----------------------------------------
    
    def reorder_columns(
        self,
        table_name: str,
        column_order: List[str],
        progress_callback: Optional[callable] = None,
    ) -> bool:
        """Reorder columns in a table to match the specified order.
        
        Similar to pandas: df = df[['col3', 'col1', 'col2']]
        
        SQLite doesn't support column reordering directly, so this always
        requires table recreation.
        
        Args:
            table_name: Name of the table
            column_order: List of column names in desired order
            progress_callback: Function for progress updates
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate all columns exist
            current_columns = self.get_column_info(table_name)
            current_names = {col["name"] for col in current_columns}
            
            if set(column_order) != current_names:
                missing = current_names - set(column_order)
                extra = set(column_order) - current_names
                if missing:
                    logger.error(f"Missing columns in order: {missing}")
                if extra:
                    logger.error(f"Unknown columns in order: {extra}")
                return False
            
            # Create column map
            column_map = {col["name"]: col for col in current_columns}
            
            cursor = self.cursor
            cursor.execute("BEGIN EXCLUSIVE TRANSACTION")
            
            # Build new table definition with reordered columns
            column_defs = []
            for col_name in column_order:
                col = column_map[col_name]
                col_def = f"{col['name']} {col['type']}"
                if col["notnull"]:
                    col_def += " NOT NULL"
                if col["default"] is not None:
                    col_def += f" DEFAULT {col['default']}"
                if col["pk"]:
                    col_def += " PRIMARY KEY"
                column_defs.append(col_def)
            
            # Create temp table with new column order
            temp_table = f"{table_name}_reorder_{int(time.time())}"
            cursor.execute(f"""
                CREATE TABLE {temp_table} (
                    {', '.join(column_defs)}
                )
            """)
            
            # Copy data
            cursor.execute(f"""
                INSERT INTO {temp_table} ({', '.join(column_order)})
                SELECT {', '.join(column_order)} FROM {table_name}
            """)
            
            # Swap tables
            cursor.execute(f"DROP TABLE {table_name}")
            cursor.execute(f"ALTER TABLE {temp_table} RENAME TO {table_name}")
            
            self.conn.commit()
            logger.info(f"Reordered columns in {table_name}")
            return True
            
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Failed to reorder columns: {e}")
            return False
    
    def sort_columns(
        self,
        table_name: str,
        alphabetical: bool = True,
        reverse: bool = False,
        key_columns_first: Optional[List[str]] = None,
        progress_callback: Optional[callable] = None,
    ) -> bool:
        """Sort columns in a table alphabetically or by custom criteria.
        
        Similar to organizing DataFrame columns systematically.
        
        Args:
            table_name: Name of the table
            alphabetical: Sort columns alphabetically
            reverse: Reverse sort order
            key_columns_first: List of columns to place first (like 'id', 'created_at')
            progress_callback: Function for progress updates
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get current columns
            columns = self.get_column_info(table_name)
            column_names = [col["name"] for col in columns]
            
            # Determine new order
            if key_columns_first:
                # Put key columns first, then sort the rest
                key_cols = [c for c in key_columns_first if c in column_names]
                other_cols = [c for c in column_names if c not in key_cols]
                if alphabetical:
                    other_cols.sort(reverse=reverse)
                new_order = key_cols + other_cols
            else:
                # Just sort all columns
                new_order = (
                    sorted(column_names, reverse=reverse)
                    if alphabetical
                    else column_names
                )
            
            # Use reorder_columns to apply the new order
            return self.reorder_columns(table_name, new_order, progress_callback)
            
        except Exception as e:
            logger.error(f"Failed to sort columns: {e}")
            return False
    
    # ----------------------------------------
    # ADD Operations
    # ----------------------------------------
    
    def add_column(
        self,
        table_name: str,
        column_name: str,
        column_type: str,
        default: Any = None,
        not_null: bool = False,
    ) -> bool:
        """Add a new column to the table.
        
        Args:
            table_name: Name of the table
            column_name: Name of new column
            column_type: SQLite type (TEXT, INTEGER, REAL, BLOB)
            default: Default value for the column
            not_null: Whether column should be NOT NULL
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.column_exists(table_name, column_name):
                logger.warning(f"Column {column_name} already exists in {table_name}")
                return False
            
            cursor = self.cursor
            col_def = f"{column_name} {column_type}"
            
            if not_null and default is None:
                logger.error("Cannot add NOT NULL column without default value")
                return False
            
            if default is not None:
                if isinstance(default, str):
                    col_def += f" DEFAULT '{default}'"
                else:
                    col_def += f" DEFAULT {default}"
            
            if not_null:
                col_def += " NOT NULL"
            
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {col_def}")
            self.conn.commit()
            
            logger.info(f"Added column {column_name} to {table_name}")
            return True
            
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Failed to add column: {e}")
            return False
    
    # ----------------------------------------
    # Batch Operations
    # ----------------------------------------
    
    def drop_columns(
        self,
        table_name: str,
        column_names: List[str],
        progress_callback: Optional[callable] = None,
    ) -> bool:
        """Drop multiple columns efficiently in one operation.
        
        More efficient than dropping columns one by one as it only
        recreates the table once.
        
        Args:
            table_name: Name of the table
            column_names: List of columns to drop
            progress_callback: Function for progress updates
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check all columns exist
            for col_name in column_names:
                if not self.column_exists(table_name, col_name):
                    logger.error(f"Column {col_name} does not exist in {table_name}")
                    return False
            
            # If native DROP is supported and only one column, use it
            if len(column_names) == 1 and self.supports_drop_column():
                return self.drop_column(table_name, column_names[0])
            
            # Otherwise recreate table without the columns
            cursor = self.cursor
            cursor.execute("BEGIN EXCLUSIVE TRANSACTION")
            
            # Get columns to keep
            columns = self.get_column_info(table_name)
            keep_columns = [
                col for col in columns if col["name"] not in column_names
            ]
            
            if not keep_columns:
                raise ValueError("Cannot drop all columns from table")
            
            # Create column definitions
            column_names_keep = [col["name"] for col in keep_columns]
            column_defs = []
            for col in keep_columns:
                col_def = f"{col['name']} {col['type']}"
                if col["notnull"]:
                    col_def += " NOT NULL"
                if col["default"] is not None:
                    col_def += f" DEFAULT {col['default']}"
                if col["pk"]:
                    col_def += " PRIMARY KEY"
                column_defs.append(col_def)
            
            # Create temp table
            temp_table = f"{table_name}_drop_{int(time.time())}"
            cursor.execute(f"""
                CREATE TABLE {temp_table} (
                    {', '.join(column_defs)}
                )
            """)
            
            # Copy data
            cursor.execute(f"""
                INSERT INTO {temp_table} ({', '.join(column_names_keep)})
                SELECT {', '.join(column_names_keep)} FROM {table_name}
            """)
            
            # Swap tables
            cursor.execute(f"DROP TABLE {table_name}")
            cursor.execute(f"ALTER TABLE {temp_table} RENAME TO {table_name}")
            
            self.conn.commit()
            logger.info(f"Dropped {len(column_names)} columns from {table_name}")
            return True
            
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Failed to drop multiple columns: {e}")
            return False


# EOF