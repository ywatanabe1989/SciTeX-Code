#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-25 06:08:26 (ywatanabe)"
# File: ./scitex_repo/src/scitex/db/_SQLite3.py

THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/db/_SQLite3.py"

from typing import List, Optional

from ..str import printc as _printc
from ._SQLite3Mixins._BatchMixin import _BatchMixin
from ._SQLite3Mixins._BlobMixin import _BlobMixin
from ._SQLite3Mixins._ConnectionMixin import _ConnectionMixin
from ._SQLite3Mixins._ImportExportMixin import _ImportExportMixin
from ._SQLite3Mixins._IndexMixin import _IndexMixin
from ._SQLite3Mixins._MaintenanceMixin import _MaintenanceMixin
from ._SQLite3Mixins._QueryMixin import _QueryMixin
from ._SQLite3Mixins._RowMixin import _RowMixin
from ._SQLite3Mixins._TableMixin import _TableMixin
from ._SQLite3Mixins._TransactionMixin import _TransactionMixin


class SQLite3(
    _ConnectionMixin,
    _QueryMixin,
    _TransactionMixin,
    _TableMixin,
    _IndexMixin,
    _RowMixin,
    _BatchMixin,
    _BlobMixin,
    _ImportExportMixin,
    _MaintenanceMixin,
):
    """Comprehensive SQLite database management class."""

    def __init__(self, db_path: str, use_temp: bool = False):
        """Initializes database with option for temporary copy."""
        _ConnectionMixin.__init__(self, db_path, use_temp)

    def __call__(
        self,
        return_summary=False,
        print_summary=True,
        table_names: Optional[List[str]] = None,
        verbose: bool = True,
        limit: int = 5,
    ):
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
        self()


BaseSQLiteDB = SQLite3

# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-11 13:48:57 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/db/_BaseSQLiteDB.py

# """
# BaseSQLiteDB: Comprehensive SQLite Database Management Class

# Features:
#     - Basic database operations (connect, execute, close)
#     - Transaction management
#     - Table operations (create, drop, modify)
#     - Index management
#     - Row operations (CRUD)
#     - BLOB data handling
#     - Batch operations
#     - Foreign key constraints
#     - Import/Export capabilities (CSV)
#     - Database maintenance and optimization

# Dependencies:
#     - sqlite3: Core database operations
#     - pandas: Data manipulation and CSV handling
#     - numpy: BLOB data processing
# """

# """Imports"""
# from typing import Any, Callable, Dict, List, Optional, Tuple, Union
# import contextlib
# import os
# import sqlite3
# import threading
# import numpy as np
# import pandas as pd
# from ..str.__printc import _printc

# """Parameters"""
# # CONFIG = scitex.gen.load_configs()

# """Functions & Classes"""

# class BaseSQLiteDB:
#     """Comprehensive SQLite database management class providing:
#     - Basic operations (connect, execute, close)
#     - Transaction and batch operations
#     - Table and index management
#     - Row operations (CRUD)
#     - BLOB data handling
#     - Import/Export capabilities
#     - Database maintenance
#     """

#     # ----------------------------------------
#     # Basic Database Operations
#     # ----------------------------------------
#     def __init__(self, db_path: str):
#         """Initializes SQLite database connection.

#         Parameters
#         ----------
#         db_path : str
#             Path to SQLite database file

#         Raises
#         ------
#         sqlite3.Error
#             If database connection fails
#         """
#         self.lock = threading.Lock()
#         self._maintenance_lock = threading.Lock()
#         self.conn: Optional[sqlite3.Connection] = None
#         self.cursor: Optional[sqlite3.Cursor] = None
#         self.db_path = db_path
#         if db_path:
#             self.connect(db_path)
#             # self._initialize_writable_state()

#         # if writable:
#         #     self.writable = True
#         # else:
#         #     self.writable = False

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

#     @contextlib.contextmanager
#     def transaction(self):
#         """Safe transaction context manager"""
#         try:
#             self.begin()
#             yield
#             self.commit()
#         except Exception as e:
#             self.rollback()
#             raise e

#     # ----------------------------------------
#     # Writable states
#     # ----------------------------------------
#     # def _initialize_writable_state(self) -> None:
#     #     """Initializes writable state table and protects it."""
#     #     try:
#     #         # Create state table without protection by default
#     #         self.execute(
#     #             """
#     #             CREATE TABLE IF NOT EXISTS _db_state (
#     #                 key TEXT PRIMARY KEY,
#     #                 value TEXT,
#     #                 protected INTEGER DEFAULT 0
#     #             )
#     #             """
#     #         )

#     #         # Initialize state
#     #         self.execute(
#     #             """
#     #             INSERT OR IGNORE INTO _db_state (key, value, protected)
#     #             VALUES ('writable', 'true', 0)
#     #             """
#     #         )
#     #     except sqlite3.Error as err:
#     #         raise ValueError(f"Failed to initialize writable state: {err}")

#     # def _initialize_writable_state(self) -> None:
#     #     """Initializes writable state table and protects it."""
#     #     try:
#     #         # Create state table
#     #         self.execute(
#     #             """
#     #             CREATE TABLE IF NOT EXISTS _db_state (
#     #                 key TEXT PRIMARY KEY,
#     #                 value TEXT,
#     #                 protected INTEGER DEFAULT 1
#     #             )
#     #             """
#     #         )

#     #         # Create trigger
#     #         self.execute(
#     #             """
#     #             CREATE TRIGGER IF NOT EXISTS protect_db_state
#     #             BEFORE UPDATE ON _db_state
#     #             BEGIN
#     #                 SELECT CASE
#     #                     WHEN OLD.protected = 1 THEN
#     #                         RAISE(ABORT, 'Cannot modify protected state')
#     #                 END;
#     #             END;
#     #             """
#     #         )

#     #         # Initialize state
#     #         self.execute(
#     #             """
#     #             INSERT OR IGNORE INTO _db_state (key, value, protected)
#     #             VALUES ('writable', 'true', 1)
#     #             """
#     #         )
#     #     except sqlite3.Error as err:
#     #         raise ValueError(f"Failed to initialize writable state: {err}")

#     @property
#     def writable(self) -> bool:
#         """Gets database writable state from internal table."""
#         try:
#             self.cursor.execute(
#                 "SELECT value FROM _db_state WHERE key = 'writable'"
#             )
#             result = self.cursor.fetchone()
#             return result[0].lower() == "true" if result else True
#         except sqlite3.Error:
#             return True

#     @writable.setter
#     def writable(self, state: bool) -> None:
#         """Sets database writable state with proper authorization."""
#         try:
#             # Temporarily disable protection
#             self.execute(
#                 "UPDATE _db_state SET protected = 0 WHERE key = 'writable'"
#             )
#             # Update state
#             self.execute(
#                 "UPDATE _db_state SET value = ? WHERE key = 'writable'",
#                 (str(state).lower(),),
#             )
#             # Re-enable protection
#             self.execute(
#                 "UPDATE _db_state SET protected = 1 WHERE key = 'writable'"
#             )
#             self.execute("PRAGMA query_only = ?", (not state,))
#         except sqlite3.Error as err:
#             raise ValueError(f"Failed to set writable state: {err}")

#     def _check_writable(self) -> None:
#         """Verifies database is writable before write operations."""
#         if not self.writable:
#             raise ValueError("Database is in read-only mode")

#     # ----------------------------------------
#     # Connection
#     # ----------------------------------------
#     def __enter__(self):
#         return self

#     def __exit__(self, exc_type, exc_val, exc_tb):
#         self.close()

#     def connect(self, db_path: str) -> None:
#         """Establishes connection to SQLite database.

#         Example
#         -------
#         >>> db = BaseSQLiteDB('example.db')
#         >>> db.connect('new_database.db')

#         Parameters
#         ----------
#         db_path : str
#             Path to SQLite database file

#         Raises
#         ------
#         sqlite3.Error
#             If connection fails
#         """

#         if self.conn:
#             self.close()
#         self.conn = sqlite3.connect(db_path)
#         self.cursor = self.conn.cursor()

#     def close(self) -> None:
#         """Closes database connection and cursor.

#         Example
#         -------
#         >>> db = BaseSQLiteDB('example.db')
#         >>> db.close()
#         """
#         if self.cursor:
#             self.cursor.close()
#         if self.conn:
#             self.conn.close()
#         self.cursor = None
#         self.conn = None

#     def reconnect(self) -> None:
#         """Reestablishes database connection.

#         Example
#         -------
#         >>> db = BaseSQLiteDB('example.db')
#         >>> db.close()
#         >>> db.reconnect()

#         Raises
#         ------
#         ValueError
#             If no database path was previously specified
#         sqlite3.Error
#             If connection fails
#         """
#         if self.db_path:
#             self.connect(self.db_path)
#         else:
#             raise ValueError("No database path specified for reconnection")

#     def execute(self, query: str, parameters: Tuple = ()) -> None:
#         """Executes single SQL query with optional parameters.

#         Example
#         -------
#         >>> db.execute("INSERT INTO users (name) VALUES (?)", ("John",))
#         >>> db.execute("SELECT * FROM users WHERE age > ?", (25,))
#         >>> db.execute("CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY)")

#         Parameters
#         ----------
#         query : str
#             SQL query to execute
#         parameters : Tuple, optional
#             Query parameters to substitute

#         Raises
#         ------
#         ConnectionError
#             If database is not connected
#         ValueError
#             If database is in read-only mode for write operations
#         sqlite3.Error
#             If query execution fails
#         """
#         if not self.cursor:
#             raise ConnectionError("Database not connected")

#         # Check if operation requires write permission
#         if any(
#             keyword in query.upper()
#             for keyword in [
#                 "INSERT",
#                 "UPDATE",
#                 "DELETE",
#                 "DROP",
#                 "CREATE",
#                 "ALTER",
#             ]
#         ):
#             self._check_writable()

#         try:
#             self.cursor.execute(query, parameters)
#             self.conn.commit()
#             return self.cursor
#         except sqlite3.Error as err:
#             raise sqlite3.Error(f"Query execution failed: {err}")

#     def executemany(self, query: str, parameters: List[Tuple]) -> None:
#         """Executes batch SQL query with multiple parameter sets.

#         Example
#         -------
#         >>> params = [("John", 30), ("Jane", 25)]
#         >>> db.executemany("INSERT INTO users (name, age) VALUES (?, ?)", params)

#         Parameters
#         ----------
#         query : str
#             SQL query to execute
#         parameters : List[Tuple]
#             List of parameter tuples for batch execution

#         Raises
#         ------
#         ConnectionError
#             If database is not connected
#         ValueError
#             If database is in read-only mode for write operations
#         sqlite3.Error
#             If batch execution fails
#         """
#         if not self.cursor:
#             raise ConnectionError("Database not connected")

#         if any(
#             keyword in query.upper()
#             for keyword in [
#                 "INSERT",
#                 "UPDATE",
#                 "DELETE",
#                 "DROP",
#                 "CREATE",
#                 "ALTER",
#             ]
#         ):
#             self._check_writable()

#         try:
#             self.cursor.executemany(query, parameters)
#             self.conn.commit()
#         except sqlite3.Error as err:
#             raise sqlite3.Error(f"Batch query execution failed: {err}")

#     def executescript(self, script: str) -> None:
#         """Executes multiple SQL statements at once.

#         Parameters
#         ----------
#         script : str
#             Multiple SQL statements separated by semicolons

#         Raises
#         ------
#         ConnectionError
#             If database is not connected
#         ValueError
#             If database is in read-only mode
#         sqlite3.Error
#             If script execution fails
#         """
#         if not self.cursor:
#             raise ConnectionError("Database not connected")

#         if any(
#             keyword in script.upper()
#             for keyword in [
#                 "INSERT",
#                 "UPDATE",
#                 "DELETE",
#                 "DROP",
#                 "CREATE",
#                 "ALTER",
#             ]
#         ):
#             self._check_writable()

#         try:
#             self.cursor.executescript(script)
#             self.conn.commit()
#         except sqlite3.Error as err:
#             raise sqlite3.Error(f"Script execution failed: {err}")

#     # ----------------------------------------
#     # Transaction Management
#     # ----------------------------------------
#     def begin(self) -> None:
#         """Starts a new database transaction.

#         Example
#         -------
#         >>> db.begin()
#         >>> try:
#         ...     db.execute("INSERT INTO users (name) VALUES (?)", ("John",))
#         ...     db.commit_transaction()
#         ... except:
#         ...     db.rollback_transaction()

#         Raises
#         ------
#         sqlite3.Error
#             If transaction start fails
#         """
#         self.execute("BEGIN TRANSACTION")

#     def commit(self) -> None:
#         """Commits pending transaction changes.

#         Example
#         -------
#         >>> db.begin()
#         >>> db.execute("INSERT INTO users (name) VALUES (?)", ("John",))
#         >>> db.commit()

#         Raises
#         ------
#         sqlite3.Error
#             If commit fails
#         """
#         self.conn.commit()

#     def rollback(self) -> None:
#         """Reverts changes from current transaction.

#         Example
#         -------
#         >>> db.begin()
#         >>> try:
#         ...     db.execute("Invalid SQL")
#         ... except:
#         ...     db.rollback()

#         Raises
#         ------
#         sqlite3.Error
#             If rollback fails
#         """
#         self.conn.rollback()

#     # ----------------------------------------
#     # Foreign Key Management
#     # ----------------------------------------
#     def enable_foreign_keys(self) -> None:
#         """Enables foreign key constraint checking.

#         Example
#         -------
#         >>> db.enable_foreign_keys()
#         >>> db.execute("CREATE TABLE users (id INTEGER PRIMARY KEY)")
#         >>> db.execute('''CREATE TABLE posts
#         ...              (id INTEGER PRIMARY KEY,
#         ...               user_id INTEGER,
#         ...               FOREIGN KEY(user_id) REFERENCES users(id))''')

#         Raises
#         ------
#         sqlite3.Error
#             If PRAGMA command fails
#         """
#         self.execute("PRAGMA foreign_keys = ON")

#     def disable_foreign_keys(self) -> None:
#         """Disables foreign key constraint checking.

#         Example
#         -------
#         >>> db.disable_foreign_keys()
#         >>> # Now foreign key constraints won't be enforced

#         Raises
#         ------
#         sqlite3.Error
#             If PRAGMA command fails
#         """
#         self.execute("PRAGMA foreign_keys = OFF")

#     # ----------------------------------------
#     # Index Management
#     # ----------------------------------------
#     def create_index(
#         self,
#         table_name: str,
#         column_names: List[str],
#         index_name: str = None,
#         unique: bool = False,
#     ) -> None:
#         """Creates an index on specified table columns for improved query performance.

#         Parameters
#         ----------
#         table_name : str
#             Name of table to create index on
#         column_names : List[str]
#             List of columns to include in index
#         index_name : str, optional
#             Custom name for index. If None, auto-generated from table and column names
#         unique : bool, optional
#             Whether to create a unique index (default False)

#         Example
#         -------
#         >>> db.create_index('users', ['email'], unique=True)
#         >>> db.create_index('posts', ['user_id', 'created_at'])

#         Raises
#         ------
#         sqlite3.Error
#             If index creation fails
#         """
#         if index_name is None:
#             index_name = f"idx_{table_name}_{'_'.join(column_names)}"
#         unique_clause = "UNIQUE" if unique else ""
#         query = f"CREATE {unique_clause} INDEX IF NOT EXISTS {index_name} ON {table_name} ({','.join(column_names)})"
#         self.execute(query)

#     def drop_index(self, index_name: str) -> None:
#         """Drops an existing database index.

#         Parameters
#         ----------
#         index_name : str
#             Name of index to drop

#         Raises
#         ------
#         sqlite3.Error
#             If index drop fails
#         """
#         self.execute(f"DROP INDEX IF EXISTS {index_name}")

#     # ----------------------------------------
#     # Table Management
#     # ----------------------------------------
#     def create_table(
#         self,
#         table_name: str,
#         columns: Dict[str, str],
#         foreign_keys: List[Dict[str, str]] = None,
#         if_not_exists: bool = True,
#     ) -> None:
#         with self.transaction():
#             try:
#                 exists_clause = "IF NOT EXISTS " if if_not_exists else ""
#                 column_defs = []

#                 for col_name, col_type in columns.items():
#                     column_defs.append(f"{col_name} {col_type}")
#                     if "BLOB" in col_type.upper():
#                         column_defs.extend(
#                             [
#                                 f"{col_name}_dtype TEXT DEFAULT 'unknown'",
#                                 f"{col_name}_shape TEXT DEFAULT 'unknown'",
#                             ]
#                         )

#                 # Add foreign key constraints
#                 if foreign_keys:
#                     for fk in foreign_keys:
#                         column_defs.append(
#                             f"FOREIGN KEY ({fk['tgt_column']}) REFERENCES {fk['src_table']}({fk['src_column']})"
#                         )

#                 query = f"CREATE TABLE {exists_clause}{table_name} ({', '.join(column_defs)})"
#                 self.execute(query)

#             except sqlite3.Error as err:
#                 raise ValueError(f"Failed to create table {table_name}: {err}")

#     # def create_table(
#     #     self,
#     #     table_name: str,
#     #     columns: Dict[str, str],
#     #     foreign_keys: Dict[str, Union[str, List[str]]] = None,
#     #     if_not_exists: bool = True,
#     # ) -> None:
#     #     """Creates new table with metadata columns for BLOB types and foreign keys.

#     #     Parameters
#     #     ----------
#     #     table_name : str
#     #         Name of table to create
#     #     columns : Dict[str, str]
#     #         Column definitions with names as keys and SQL types as values
#     #     foreign_keys : Dict[str, Union[str, List[str]]], optional
#     #         Foreign key definitions as {table_name: column_name(s)}
#     #     if_not_exists : bool, optional
#     #         Whether to use IF NOT EXISTS clause (default True)

#     #     Example
#     #     -------
#     #     >>> columns = {
#     #     ...     'id': 'INTEGER PRIMARY KEY',
#     #     ...     'name': 'TEXT',
#     #     ...     'data': 'BLOB'
#     #     ... }
#     #     >>> foreign_keys = {'parent_table': ['id', 'name']}
#     #     >>> db.create_table('measurements', columns, foreign_keys)
#     #     """
#     #     try:
#     #         # Create base table
#     #         exists_clause = "IF NOT EXISTS " if if_not_exists else ""
#     #         column_defs = []

#     #         for col_name, col_type in columns.items():
#     #             column_defs.append(f"{col_name} {col_type}")
#     #             if "BLOB" in col_type.upper():
#     #                 column_defs.extend([
#     #                     f"{col_name}_dtype TEXT DEFAULT 'unknown'",
#     #                     f"{col_name}_shape TEXT DEFAULT 'unknown'"
#     #                 ])

#     #         # Add foreign key constraints
#     #         if foreign_keys:
#     #             for src_table, columns in foreign_keys.items():
#     #                 if isinstance(columns, str):
#     #                     columns = [columns]
#     #                 for column in columns:
#     #                     column_defs.append(
#     #                         f"FOREIGN KEY ({column}) REFERENCES {src_table}({column})"
#     #                     )

#     #         query = f"CREATE TABLE {exists_clause}{table_name} ({', '.join(column_defs)})"
#     #         self.execute(query)

#     #     except sqlite3.Error as err:
#     #         raise ValueError(f"Failed to create table {table_name}: {err}")

#     def drop_table(self, table_name: str, if_exists: bool = True) -> None:
#         """Drops a table from the database.

#         Parameters
#         ----------
#         table_name : str
#             Name of table to drop
#         if_exists : bool, optional
#             Whether to ignore if table doesn't exist (default True)

#         Example
#         -------
#         >>> db.drop_table('temporary_table')
#         >>> db.drop_table('users', if_exists=False)  # Raises error if table doesn't exist

#         Raises
#         ------
#         ValueError
#             If table drop fails
#         sqlite3.Error
#             If SQL execution fails
#         """
#         with self.transaction():
#             try:
#                 exists_clause = "IF EXISTS " if if_exists else ""
#                 query = f"DROP TABLE {exists_clause}{table_name}"
#                 self.execute(query)
#             except sqlite3.Error as err:
#                 raise ValueError(f"Failed to drop table: {err}")

#     def rename_table(self, old_name: str, new_name: str) -> None:
#         """Renames a table in the database.

#         Parameters
#         ----------
#         old_name : str
#             Current name of the table
#         new_name : str
#             New name for the table

#         Raises
#         ------
#         ValueError
#             If table rename fails
#         sqlite3.Error
#             If SQL execution fails
#         """
#         with self.transaction():
#             try:
#                 query = f"ALTER TABLE {old_name} RENAME TO {new_name}"
#                 self.execute(query)
#             except sqlite3.Error as err:
#                 raise ValueError(f"Failed to rename table: {err}")

#     def add_columns(
#         self,
#         table_name: str,
#         columns: Dict[str, str],
#         default_values: Dict[str, Any] = None,
#     ) -> None:
#         """Adds multiple columns to an existing table.

#         Parameters
#         ----------
#         table_name : str
#             Name of table to modify
#         columns : Dict[str, str]
#             Dictionary mapping column names to their SQL types
#         default_values : Dict[str, Any], optional
#             Dictionary mapping column names to their default values

#         Example
#         -------
#         >>> columns = {"age": "INTEGER", "status": "TEXT"}
#         >>> default_values = {"age": 0, "status": "'draft'"}
#         >>> db.add_columns("users", columns, default_values)
#         """
#         with self.transaction():
#             if default_values is None:
#                 default_values = {}

#             for column_name, column_type in columns.items():
#                 self.add_column(
#                     table_name,
#                     column_name,
#                     column_type,
#                     default_values.get(column_name),
#                 )

#     def add_column(
#         self,
#         table_name: str,
#         column_name: str,
#         column_type: str,
#         default_value: Any = None,
#     ) -> None:
#         """Adds a new column to an existing table if it doesn't exist."""
#         # Check if column exists using get_table_schema
#         with self.transaction():
#             schema = self.get_table_schema(table_name)
#             if column_name in schema["name"].values:
#                 return

#             try:
#                 query = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
#                 if default_value is not None:
#                     query += f" DEFAULT {default_value}"
#                 self.execute(query)

#                 # Add metadata columns if BLOB type
#                 if "BLOB" in column_type.upper():
#                     self.add_column(
#                         table_name,
#                         f"{column_name}_dtype",
#                         "TEXT",
#                         default_value="'unknown'",
#                     )
#                     self.add_column(
#                         table_name,
#                         f"{column_name}_shape",
#                         "TEXT",
#                         default_value="'unknown'",
#                     )

#             except sqlite3.OperationalError as err:
#                 raise ValueError(f"Failed to add column: {err}")

#     # def drop_columns(self, table_name: str, columns: Union[str, List[str]], if_exists: bool = True) -> None:
#     #     """Drops columns more efficiently using SQLite's ALTER TABLE."""
#     #     if isinstance(columns, str):
#     #         columns = [columns]

#     #     # Get existing columns
#     #     schema = self.get_table_schema(table_name)
#     #     existing_columns = schema['name'].values

#     #     # Filter to only existing columns if if_exists=True
#     #     columns_to_drop = [col for col in columns if col in existing_columns] if if_exists else columns

#     #     if not columns_to_drop:
#     #         return

#     #     try:
#     #         for column in columns_to_drop:
#     #             self.execute(f"ALTER TABLE {table_name} DROP COLUMN {column}")
#     #     except sqlite3.Error as err:
#     #         raise ValueError(f"Failed to drop columns: {err}")

#     def drop_columns(
#         self,
#         table_name: str,
#         columns: Union[str, List[str]],
#         if_exists: bool = True,
#     ) -> None:
#         with self.transaction():
#             if isinstance(columns, str):
#                 columns = [columns]
#             schema = self.get_table_schema(table_name)
#             existing_columns = schema["name"].values
#             columns_to_drop = (
#                 [col for col in columns if col in existing_columns]
#                 if if_exists
#                 else columns
#             )

#             if not columns_to_drop:
#                 return

#             for column in columns_to_drop:
#                 self.execute(f"ALTER TABLE {table_name} DROP COLUMN {column}")

#     def add_foreign_columns(
#         self,
#         tgt_table: str,
#         foreign_keys: Dict[str, Union[str, List[str]]],
#         default_value: Any = None,
#     ) -> None:
#         """Adds new foreign key columns to an existing table.

#         Parameters
#         ----------
#         tgt_table : str
#             Name of target table to modify
#         foreign_keys : Dict[str, Union[str, List[str]]]
#             Dictionary mapping source tables to their column(s)
#             Format: {source_table: column_name or [column_names]}
#         default_value : Any, optional
#             Default value for existing rows

#         Example
#         -------
#         >>> foreign_keys = {"id_manager": ["id", "patient_id"]}
#         >>> db.add_foreign_column("time_table", foreign_keys)
#         """
#         with self.transaction():
#             for src_table, columns in foreign_keys.items():
#                 if isinstance(columns, str):
#                     columns = [columns]

#                 for column in columns:
#                     temp_table = f"{tgt_table}_temp"
#                     self._add_single_foreign_column(
#                         tgt_table, temp_table, src_table, column, default_value
#                     )

#     # def add_foreign_columns(
#     #     self,
#     #     tgt_table: str,
#     #     foreign_keys: Dict[str, Union[str, List[str]]],
#     #     default_value: Any = None,
#     # ) -> None:
#     #     """Adds new foreign key columns to an existing table.

#     #     Parameters
#     #     ----------
#     #     tgt_table : str
#     #         Name of target table to modify
#     #     foreign_keys : Dict[str, Union[str, List[str]]]
#     #         Dictionary mapping source tables to their column(s)
#     #         Format: {source_table: column_name or [column_names]}
#     #     default_value : Any, optional
#     #         Default value for existing rows

#     #     Example
#     #     -------
#     #     >>> foreign_keys = {"id_manager": ["id", "patient_id"]}
#     #     >>> db.add_foreign_column("time_table", foreign_keys)
#     #     """
#     #     try:
#     #         for src_table, columns in foreign_keys.items():
#     #             if isinstance(columns, str):
#     #                 columns = [columns]

#     #             for column in columns:
#     #                 # Verify tables and columns exist
#     #                 src_schema = self.get_table_schema(src_table)
#     #                 if column not in src_schema:
#     #                     raise ValueError(
#     #                         f"Column {column} not found in {src_table}"
#     #                     )

#     #                 current_schema = self.get_table_schema(tgt_table)
#     #                 if column in current_schema:
#     #                     raise ValueError(
#     #                         f"Column {column} already exists in {tgt_table}"
#     #                     )

#     #                 # Get column type from source table
#     #                 column_type = src_schema[column]

#     #                 # Create new table schema with foreign key
#     #                 new_columns = {column: column_type}
#     #                 new_columns.update(current_schema)

#     #                 # Enable foreign keys
#     #                 self.execute("PRAGMA foreign_keys=ON")

#     #                 # Create temp table and copy data
#     #                 temp_table = f"{tgt_table}_temp"
#     #                 self.create_table(temp_table, new_columns)

#     #                 # Copy existing data
#     #                 old_cols = ", ".join(current_schema.keys())
#     #                 self.execute(
#     #                     f"INSERT INTO {temp_table} ({old_cols}) SELECT {old_cols} FROM {tgt_table}"
#     #                 )

#     #                 # Drop old table and rename new one
#     #                 self.execute(f"DROP TABLE {tgt_table}")
#     #                 self.execute(
#     #                     f"ALTER TABLE {temp_table} RENAME TO {tgt_table}"
#     #                 )

#     #                 # Add foreign key constraint
#     #                 query = (
#     #                     f"ALTER TABLE {tgt_table} ADD FOREIGN KEY ({column}) "
#     #                     f"REFERENCES {src_table}({column})"
#     #                 )
#     #                 self.execute(query)

#     #                 # Update with default value if provided
#     #                 if default_value is not None:
#     #                     self.execute(
#     #                         f"UPDATE {tgt_table} SET {column} = ?",
#     #                         (default_value,),
#     #                     )

#     #     except sqlite3.Error as err:
#     #         raise ValueError(f"Failed to add foreign key column: {err}")

#     def get_table_names(self) -> List[str]:
#         """Lists all tables in the database.

#         Returns
#         -------
#         List[str]
#             Names of all tables in database

#         Example
#         -------
#         >>> tables = db.get_table_names()
#         >>> print(tables)  # ['users', 'posts', ...]
#         """
#         query = "SELECT name FROM sqlite_master WHERE type='table'"
#         self.cursor.execute(query)
#         return [table[0] for table in self.cursor.fetchall()]

#     def get_table_schema(self, table_name: str) -> pd.DataFrame:
#         """Retrieves schema information for specified table.

#         Example
#         -------
#         >>> db = BaseSQLiteDB('example.db')
#         >>> info = db.get_table_schema('users')
#         >>> print(info)  # Shows column details

#         Parameters
#         ----------
#         table_name : str
#             Name of table to analyze

#         Returns
#         -------
#         pd.DataFrame
#             DataFrame containing:
#             - cid: Column ID
#             - name: Column name
#             - type: Data type
#             - notnull: NOT NULL constraint
#             - dflt_value: Default value
#             - pk: Primary key flag
#         """
#         query = f"PRAGMA table_info({table_name})"
#         self.cursor.execute(query)
#         columns = ["cid", "name", "type", "notnull", "dflt_value", "pk"]
#         return pd.DataFrame(self.cursor.fetchall(), columns=columns)

#     def get_primary_key(self, table_name: str) -> str:
#         schema = self.get_table_schema(table_name)
#         pk_col = schema[schema["pk"] == 1]["name"].values
#         return pk_col[0] if len(pk_col) > 0 else None

#     def get_table_stats(self, table_name: str) -> Dict[str, int]:
#         """Retrieves size statistics for a specified database table.

#         Example
#         -------
#         >>> db = BaseSQLiteDB('example.db')
#         >>> stats = db.get_table_stats('users')
#         >>> print(stats)
#         {
#             'pages': 10,
#             'page_size': 4096,
#             'total_size': 40960,
#             'row_count': 1000
#         }

#         Parameters
#         ----------
#         table_name : str
#             Name of the table to analyze

#         Returns
#         -------
#         Dict[str, int]
#             Dictionary containing:
#             - pages: Number of pages used by table
#             - page_size: Size of each page in bytes
#             - total_size: Total size in bytes (pages * page_size)
#             - row_count: Total number of rows in table

#         Raises
#         ------
#         ValueError
#             If size statistics cannot be retrieved
#         sqlite3.Error
#             If database query fails
#         """
#         try:
#             pages = self.cursor.execute(f"PRAGMA page_count").fetchone()[0]
#             page_size = self.cursor.execute(f"PRAGMA page_size").fetchone()[0]
#             row_count = self.get_row_count(table_name)
#             return {
#                 "pages": pages,
#                 "page_size": page_size,
#                 "total_size": pages * page_size,
#                 "row_count": row_count,
#             }
#         except sqlite3.Error as err:
#             raise ValueError(f"Failed to get table size: {err}")

#     # ----------------------------------------
#     # Row Operations
#     # ----------------------------------------
#     def get_rows(
#         self,
#         table_name: str,
#         columns: List[str] = None,
#         where: str = None,
#         order_by: str = None,
#         limit: Optional[int] = None,
#         offset: Optional[int] = None,
#         return_as: str = "dataframe",
#     ):
#         """Retrieves rows from specified table."""

#         if columns is None:
#             columns_str = "*"
#         elif isinstance(columns, str):
#             columns_str = f'"{columns}"'
#         else:
#             columns_str = ", ".join(f'"{col}"' for col in columns)

#         try:
#             query_parts = [f"SELECT {columns_str} FROM {table_name}"]

#             if where:
#                 query_parts.append(f"WHERE {where}")
#             if order_by:
#                 query_parts.append(f"ORDER BY {order_by}")
#             if limit is not None:
#                 query_parts.append(f"LIMIT {limit}")
#             if offset is not None:
#                 query_parts.append(f"OFFSET {offset}")

#             query = " ".join(query_parts)
#             self.cursor.execute(query)

#             column_names = [
#                 description[0] for description in self.cursor.description
#             ]
#             data = self.cursor.fetchall()

#             if return_as == "list":
#                 return data
#             elif return_as == "dict":
#                 return [dict(zip(column_names, row)) for row in data]
#             else:
#                 return pd.DataFrame(data, columns=column_names)

#         except sqlite3.Error as error:
#             raise sqlite3.Error(
#                 f"Query execution failed: {str(error)}"
#             ) from error

#     def get_row_count(self, table_name: str = None, where: str = None) -> int:
#         """Counts total number of rows in specified table.

#         Example
#         -------
#         >>> db = BaseSQLiteDB('example.db')
#         >>> # Count all rows
#         >>> total = db.get_row_count('users')
#         >>> # Count with condition
#         >>> active_users = db.get_row_count('users', where='status="active"')

#         Parameters
#         ----------
#         table_name : str
#             Name of target table
#         where : str, optional
#             SQL WHERE clause for filtering rows

#         Returns
#         -------
#         int
#             Number of rows matching criteria

#         Raises
#         ------
#         ValueError
#             If table_name is not specified
#         sqlite3.Error
#             If query execution fails
#         """

#         if table_name is None:
#             raise ValueError("Table name must be specified")

#         query = f"SELECT COUNT(*) FROM {table_name}"
#         if where:
#             query += f" WHERE {where}"

#         self.cursor.execute(query)
#         return self.cursor.fetchone()[0]

#     # ----------------------------------------
#     # Batch Operations
#     # ----------------------------------------
#     def _run_many(
#         self,
#         sql_command,
#         table_name: str,
#         rows: List[Dict[str, Any]],
#         batch_size: int = 1000,
#         inherit_foreign: bool = True,
#         where: Optional[str] = None,
#         columns: Optional[List[str]] = None,
#     ) -> None:
#         assert sql_command.upper() in [
#             "INSERT",
#             "REPLACE",
#             "INSERT OR REPLACE",
#             "UPDATE",
#         ]

#         if not rows:
#             return

#         if sql_command.upper() == "UPDATE":
#             valid_columns = (
#                 columns if columns else [col for col in rows[0].keys()]
#             )
#             set_clause = ",".join([f"{col}=?" for col in valid_columns])
#             where_clause = where if where else "1=1"
#             query = (
#                 f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}"
#             )

#             for idx in range(0, len(rows), batch_size):
#                 batch = rows[idx : idx + batch_size]
#                 values = [
#                     tuple([row[col] for col in valid_columns]) for row in batch
#                 ]
#                 self.executemany(query, values)
#             return

#         # Filter rows based on where clause if provided
#         if where:
#             filtered_rows = []
#             for row in rows:
#                 try:
#                     # Create a temporary query to test the where clause
#                     test_query = f"SELECT 1 FROM (SELECT {','.join(f'{k} as {k}' for k in row.keys())}) WHERE {where}"
#                     values = tuple(row.values())
#                     result = self.execute(test_query, values).fetchone()
#                     if result:
#                         filtered_rows.append(row)
#                 except Exception as e:
#                     print(
#                         f"Warning: Where clause evaluation failed for row: {e}"
#                     )
#             rows = filtered_rows

#         # Rest of the original function...
#         schema = self.get_table_schema(table_name)
#         table_columns = set(schema["name"])
#         valid_columns = [col for col in rows[0].keys()]

#         if inherit_foreign:
#             fk_query = f"PRAGMA foreign_key_list({table_name})"
#             foreign_keys = self.execute(fk_query).fetchall()

#             for row in rows:
#                 for fk in foreign_keys:
#                     ref_table, from_col, to_col = fk[2], fk[3], fk[4]
#                     if from_col not in row or row[from_col] is None:
#                         if to_col in row:
#                             query = f"SELECT {from_col} FROM {ref_table} WHERE {to_col} = ?"
#                             result = self.execute(
#                                 query, (row[to_col],)
#                             ).fetchone()
#                             if result:
#                                 row[from_col] = result[0]

#         columns = valid_columns
#         placeholders = ",".join(["?" for _ in columns])
#         query = f"{sql_command} INTO {table_name} ({','.join(columns)}) VALUES ({placeholders})"

#         for idx in range(0, len(rows), batch_size):
#             batch = rows[idx : idx + batch_size]
#             values = [[row.get(col) for col in valid_columns] for row in batch]
#             self.executemany(query, values)

#     def update_many(
#         self,
#         table_name: str,
#         rows: List[Dict[str, Any]],
#         batch_size: int = 1000,
#         where: Optional[str] = None,
#         columns: Optional[List[str]] = None,
#     ) -> None:
#         with self.transaction():
#             self._run_many(
#                 sql_command="UPDATE",
#                 table_name=table_name,
#                 rows=rows,
#                 batch_size=batch_size,
#                 inherit_foreign=False,
#                 where=where,
#                 columns=columns,
#             )

#     def insert_many(
#         self,
#         table_name: str,
#         rows: List[Dict[str, Any]],
#         batch_size: int = 1000,
#         inherit_foreign: bool = True,
#         where: Optional[str] = None,
#     ) -> None:
#         with self.transaction():
#             self._run_many(
#                 sql_command="INSERT",
#                 table_name=table_name,
#                 rows=rows,
#                 batch_size=batch_size,
#                 inherit_foreign=inherit_foreign,
#                 where=where,
#             )

#     def replace_many(
#         self,
#         table_name: str,
#         rows: List[Dict[str, Any]],
#         batch_size: int = 1000,
#         inherit_foreign: bool = True,
#         where: Optional[str] = None,
#     ) -> None:
#         with self.transaction():
#             self._run_many(
#                 sql_command="REPLACE",
#                 table_name=table_name,
#                 rows=rows,
#                 batch_size=batch_size,
#                 inherit_foreign=inherit_foreign,
#                 where=where,
#             )

#     def delete_where(
#         self, table_name: str, where: str, limit: Optional[int] = None
#     ) -> None:
#         with self.transaction():
#             query = f"DELETE FROM {table_name} WHERE {where}"
#             if limit is not None:
#                 query += f" LIMIT {limit}"
#             self.execute(query)

#     def update_where(
#         self,
#         table_name: str,
#         updates: Dict[str, Any],
#         where: str,
#         limit: Optional[int] = None,
#     ) -> None:
#         with self.transaction():
#             set_clause = ", ".join([f"{col} = ?" for col in updates.keys()])
#             query = f"UPDATE {table_name} SET {set_clause} WHERE {where}"
#             if limit is not None:
#                 query += f" LIMIT {limit}"
#             self.execute(query, tuple(updates.values()))

#     # def update_many(
#     #     self,
#     #     table_name: str,
#     #     rows: List[Dict[str, Any]],
#     #     batch_size: int = 1000,
#     #     where: Optional[str] = None,
#     #     columns: Optional[List[str]] = None,
#     # ) -> None:
#     #     self._run_many(
#     #         sql_command="UPDATE",
#     #         table_name=table_name,
#     #         rows=rows,
#     #         batch_size=batch_size,
#     #         inherit_foreign=False,
#     #         where=where,
#     #         columns=columns,
#     #     )

#     # def insert_many(
#     #     self,
#     #     table_name: str,
#     #     rows: List[Dict[str, Any]],
#     #     batch_size: int = 1000,
#     #     inherit_foreign: bool = True,
#     #     where: Optional[str] = None,
#     # ) -> None:
#     #     self._run_many(
#     #         sql_command="INSERT",
#     #         table_name=table_name,
#     #         rows=rows,
#     #         batch_size=batch_size,
#     #         inherit_foreign=inherit_foreign,
#     #         where=where,
#     #     )

#     # def replace_many(
#     #     self,
#     #     table_name: str,
#     #     rows: List[Dict[str, Any]],
#     #     batch_size: int = 1000,
#     #     inherit_foreign: bool = True,
#     #     where: Optional[str] = None,
#     # ) -> None:
#     #     self._run_many(
#     #         sql_command="REPLACE",
#     #         table_name=table_name,
#     #         rows=rows,
#     #         batch_size=batch_size,
#     #         inherit_foreign=inherit_foreign,
#     #         where=where,
#     #     )

#     # def delete_where(
#     #     self, table_name: str, where: str, limit: Optional[int] = None
#     # ) -> None:
#     #     """Deletes rows matching condition with optional limit.

#     #     Example
#     #     -------
#     #     >>> db.delete_where('users', "age < 18")
#     #     >>> db.delete_where('logs', "timestamp < '2024-01-01'", limit=1000)

#     #     Parameters
#     #     ----------
#     #     table_name : str
#     #         Name of target table
#     #     where : str
#     #         SQL WHERE clause for filtering rows to delete
#     #     limit : Optional[int], optional
#     #         Maximum number of rows to delete in single operation

#     #     Raises
#     #     ------
#     #     ValueError
#     #         If deletion fails
#     #     sqlite3.Error
#     #         If SQL execution fails
#     #     """
#     #     try:
#     #         query = f"DELETE FROM {table_name} WHERE {where}"
#     #         if limit is not None:
#     #             query += f" LIMIT {limit}"
#     #         self.execute(query)
#     #     except sqlite3.Error as err:
#     #         raise ValueError(f"Failed to delete rows: {err}")

#     # def update_where(
#     #     self,
#     #     table_name: str,
#     #     updates: Dict[str, Any],
#     #     where: str,
#     #     limit: Optional[int] = None,
#     # ) -> None:
#     #     """Updates rows matching condition with optional limit.

#     #     Example
#     #     -------
#     #     >>> db.update_where(
#     #     ...     'users',
#     #     ...     {'status': 'active', 'last_login': '2024-01-01'},
#     #     ...     "age >= 18",
#     #     ...     limit=1000
#     #     ... )

#     #     Parameters
#     #     ----------
#     #     table_name : str
#     #         Name of target table
#     #     updates : Dict[str, Any]
#     #         Dictionary of column names and new values
#     #     where : str
#     #         SQL WHERE clause for filtering rows to update
#     #     limit : Optional[int], optional
#     #         Maximum number of rows to update in single operation

#     #     Raises
#     #     ------
#     #     ValueError
#     #         If update fails
#     #     sqlite3.Error
#     #         If SQL execution fails
#     #     """
#     #     try:
#     #         set_clause = ", ".join([f"{col} = ?" for col in updates.keys()])
#     #         query = f"UPDATE {table_name} SET {set_clause} WHERE {where}"
#     #         if limit is not None:
#     #             query += f" LIMIT {limit}"
#     #         self.execute(query, tuple(updates.values()))
#     #     except sqlite3.Error as err:
#     #         raise ValueError(f"Failed to update rows: {err}")

#     # ----------------------------------------
#     # BLOB Operations
#     # ----------------------------------------
#     def save_array(
#         self,
#         table_name: str,
#         data: np.ndarray,
#         column: str = "data",
#         ids: Optional[Union[int, List[int]]] = None,
#         where: str = None,
#         additional_columns: Dict[str, Any] = None,
#         batch_size: int = 1000,
#     ) -> None:
#         """Stores NumPy array as BLOB with metadata in SQLite database."""
#         with self.transaction():
#             if not isinstance(data, (np.ndarray, list)):
#                 raise ValueError("Input must be a NumPy array or list of arrays")

#             try:
#                 if ids is not None:
#                     if isinstance(ids, int):
#                         ids = [ids]
#                         data = [data]
#                     if len(ids) != len(data):
#                         raise ValueError(
#                             "Length of ids must match number of arrays"
#                         )

#                     for id_, arr in zip(ids, data):
#                         if not isinstance(arr, np.ndarray):
#                             raise ValueError(
#                                 f"Element for id {id_} must be a NumPy array"
#                             )

#                         binary = arr.tobytes()
#                         columns = [column, f"{column}_dtype", f"{column}_shape"]
#                         values = [binary, str(arr.dtype), str(arr.shape)]

#                         if additional_columns:
#                             columns = list(additional_columns.keys()) + columns
#                             values = list(additional_columns.values()) + values

#                         update_cols = [f"{col}=?" for col in columns]
#                         query = f"UPDATE {table_name} SET {','.join(update_cols)} WHERE id=?"
#                         values.append(id_)
#                         self.execute(query, tuple(values))

#                 else:
#                     if not isinstance(data, np.ndarray):
#                         raise ValueError("Single input must be a NumPy array")

#                     binary = data.tobytes()
#                     columns = [column, f"{column}_dtype", f"{column}_shape"]
#                     values = [binary, str(data.dtype), str(data.shape)]

#                     if additional_columns:
#                         columns = list(additional_columns.keys()) + columns
#                         values = list(additional_columns.values()) + values

#                     if where is not None:
#                         update_cols = [f"{col}=?" for col in columns]
#                         query = f"UPDATE {table_name} SET {','.join(update_cols)} WHERE {where}"
#                         self.execute(query, tuple(values))
#                     else:
#                         placeholders = ",".join(["?" for _ in columns])
#                         columns_str = ",".join(columns)
#                         query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
#                         self.execute(query, tuple(values))

#             except Exception as err:
#                 raise ValueError(f"Failed to save array: {err}")

#     def load_array(
#         self,
#         table_name: str,
#         column: str,
#         ids: Union[int, List[int], str] = "all",
#         where: str = None,
#         order_by: str = None,
#         batch_size: int = 128,
#         dtype: np.dtype = None,
#         shape: Optional[Tuple] = None,
#     ) -> Optional[np.ndarray]:
#         """Loads array data from SQLite database with metadata support."""
#         try:
#             if ids == "all":
#                 query = f"SELECT id FROM {table_name}"
#                 if where:
#                     query += f" WHERE {where}"
#                 self.cursor.execute(query)
#                 ids = [row[0] for row in self.cursor.fetchall()]
#             elif isinstance(ids, int):
#                 ids = [ids]

#             # Create mapping of id to data
#             id_to_data = {}
#             unique_ids = list(set(ids))

#             for idx in range(0, len(unique_ids), batch_size):
#                 batch_ids = unique_ids[idx : idx + batch_size]
#                 placeholders = ",".join("?" for _ in batch_ids)

#                 try:
#                     query = f"""
#                         SELECT id, {column},
#                                {column}_dtype,
#                                {column}_shape
#                         FROM {table_name}
#                         WHERE id IN ({placeholders})
#                     """
#                     self.cursor.execute(query, tuple(batch_ids))
#                     has_metadata = True
#                 except sqlite3.OperationalError:
#                     query = f"SELECT id, {column} FROM {table_name} WHERE id IN ({placeholders})"
#                     self.cursor.execute(query, tuple(batch_ids))
#                     has_metadata = False

#                 if where:
#                     query += f" AND {where}"
#                 if order_by:
#                     query += f" ORDER BY {order_by}"

#                 results = self.cursor.fetchall()
#                 if results:
#                     for result in results:
#                         if has_metadata:
#                             id_val, blob, dtype_str, shape_str = result
#                             data = np.frombuffer(
#                                 blob, dtype=np.dtype(dtype_str)
#                             ).reshape(eval(shape_str))
#                         else:
#                             id_val, blob = result
#                             data = (
#                                 np.frombuffer(blob, dtype=dtype)
#                                 if dtype
#                                 else np.frombuffer(blob)
#                             )
#                             if shape:
#                                 data = data.reshape(shape)
#                         id_to_data[id_val] = data

#             # Maintain input order and duplicates
#             all_data = [
#                 id_to_data[id_val] for id_val in ids if id_val in id_to_data
#             ]
#             return np.stack(all_data, axis=0) if all_data else None

#         except Exception as err:
#             raise ValueError(f"Failed to load array: {err}")

#     def binary_to_array(
#         self,
#         binary_data,
#         dtype_str=None,
#         shape_str=None,
#         dtype=None,
#         shape=None,
#     ):
#         """Convert binary data into numpy array."""
#         if binary_data is None:
#             return None

#         if dtype_str and shape_str:
#             return np.frombuffer(
#                 binary_data, dtype=np.dtype(dtype_str)
#             ).reshape(eval(shape_str))
#         elif dtype and shape:
#             return np.frombuffer(binary_data, dtype=dtype).reshape(shape)
#         return binary_data

#     def get_array_dict(self, df, columns=None, dtype=None, shape=None):
#         """Return dictionary of concatenated arrays for batch processing.

#         Returns:
#             dict: {column_name: numpy_array} where each array has shape (n_samples, *data_shape)
#         """
#         result = {}
#         if columns is None:
#             columns = [
#                 col
#                 for col in df.columns
#                 if not (col.endswith("_dtype") or col.endswith("_shape"))
#             ]

#         for col in columns:
#             if f"{col}_dtype" in df.columns and f"{col}_shape" in df.columns:
#                 arrays = [
#                     self.binary_to_array(
#                         row[col], row[f"{col}_dtype"], row[f"{col}_shape"]
#                     )
#                     for _, row in df.iterrows()
#                 ]
#             elif dtype and shape:
#                 arrays = [
#                     self.binary_to_array(x, dtype=dtype, shape=shape)
#                     for x in df[col]
#                 ]
#             result[col] = np.stack(arrays)

#         return result

#     def decode_array_columns(self, df, columns=None, dtype=None, shape=None):
#         """Decode binary columns to numpy arrays within DataFrame for exploration.

#         Modifies DataFrame in-place, replacing binary data with numpy arrays.
#         Returns modified DataFrame.
#         """
#         if columns is None:
#             columns = [
#                 col
#                 for col in df.columns
#                 if not (col.endswith("_dtype") or col.endswith("_shape"))
#             ]

#         for col in columns:
#             if f"{col}_dtype" in df.columns and f"{col}_shape" in df.columns:
#                 df[col] = df.apply(
#                     lambda row: self.binary_to_array(
#                         row[col], row[f"{col}_dtype"], row[f"{col}_shape"]
#                     ),
#                     axis=1,
#                 )
#             elif dtype and shape:
#                 df[col] = df[col].apply(
#                     lambda x: self.binary_to_array(x, dtype=dtype, shape=shape)
#                 )
#         return df

#     # ----------------------------------------
#     # Import/Export Operations
#     # ----------------------------------------
#     def load_from_csv(
#         self,
#         table_name: str,
#         csv_path: str,
#         if_exists: str = "append",
#         batch_size: int = 10_000,
#         chunk_size: int = 100_000,
#     ) -> None:
#         """Imports CSV data into table with batch processing.

#         Example
#         -------
#         >>> db.load_from_csv(
#         ...     'users',
#         ...     'data.csv',
#         ...     if_exists='replace',
#         ...     batch_size=5000
#         ... )

#         Parameters
#         ----------
#         table_name : str
#             Name of target table
#         csv_path : str
#             Path to CSV file
#         if_exists : str, optional
#             How to behave if table exists: 'fail', 'replace', 'append' (default: 'append')
#         batch_size : int, optional
#             Number of rows per batch for SQL insert (default: 10,000)
#         chunk_size : int, optional
#             Number of rows to read at once from CSV (default: 100,000)

#         Raises
#         ------
#         ValueError
#             If file or table operations fail
#         FileNotFoundError
#             If CSV file does not exist
#         """
#         with self.transaction():
#             try:
#                 for chunk in pd.read_csv(csv_path, chunksize=chunk_size):
#                     chunk.to_sql(
#                         table_name,
#                         self.conn,
#                         if_exists=if_exists,
#                         index=False,
#                         chunksize=batch_size,
#                     )
#                     if_exists = "append"
#             except FileNotFoundError:
#                 raise FileNotFoundError(f"CSV file not found: {csv_path}")
#             except Exception as err:
#                 raise ValueError(f"Failed to import from CSV: {err}")

#     def save_to_csv(
#         self,
#         table_name: str,
#         output_path: str,
#         columns: List[str] = ["*"],
#         where: str = None,
#         batch_size: int = 10_000,
#     ) -> None:
#         """Exports table data to CSV file with batch processing.

#         Example
#         -------
#         >>> db.save_to_csv(
#         ...     'users',
#         ...     'output.csv',
#         ...     columns=['id', 'name'],
#         ...     where="age >= 18",
#         ...     batch_size=5000
#         ... )

#         Parameters
#         ----------
#         table_name : str
#             Name of source table
#         output_path : str
#             Path for output CSV file
#         columns : List[str], optional
#             Columns to export (default: ["*"])
#         where : str, optional
#             SQL WHERE clause for filtering rows
#         batch_size : int, optional
#             Number of rows per batch (default: 10,000)

#         Raises
#         ------
#         ValueError
#             If export operation fails
#         PermissionError
#             If writing to output path fails
#         """
#         try:
#             # First batch
#             df = self.get_rows(
#                 columns=columns,
#                 table_name=table_name,
#                 where=where,
#                 limit=batch_size,
#                 offset=0,
#             )
#             df.to_csv(output_path, index=False, mode="w")

#             # Subsequent batches
#             offset = batch_size
#             while len(df) == batch_size:
#                 df = self.get_rows(
#                     columns=columns,
#                     table_name=table_name,
#                     where=where,
#                     limit=batch_size,
#                     offset=offset,
#                 )
#                 if len(df) > 0:
#                     df.to_csv(output_path, index=False, mode="a", header=False)
#                 offset += batch_size
#         except PermissionError:
#             raise PermissionError(f"Cannot write to: {output_path}")
#         except Exception as err:
#             raise ValueError(f"Failed to export to CSV: {err}")

#     # ----------------------------------------
#     # Database Maintenance
#     # ----------------------------------------
#     @contextlib.contextmanager
#     def maintenance_lock(self) -> ContextManager[None]:
#         """Acquires maintenance lock for disruptive operations.

#         Example
#         -------
#         >>> with db.maintenance_lock():
#         ...     db.vacuum()
#         ...     db.optimize()
#         """
#         if not self._maintenance_lock.acquire(timeout=300):
#             raise TimeoutError("Could not acquire maintenance lock")
#         try:
#             yield
#         finally:
#             self._maintenance_lock.release()

#     def backup(
#         self,
#         backup_path: str,
#         pages: int = -1,
#         progress: Optional[
#             Callable[[sqlite3.Connection, int, int], None]
#         ] = None,
#     ) -> None:
#         """Creates database backup with optional progress tracking.

#         Example
#         -------
#         >>> def show_progress(conn, remaining, total):
#         ...     print(f"Progress: {((total-remaining)/total)*100:.1f}%")
#         >>> db.backup('backup.db', progress=show_progress)

#         Parameters
#         ----------
#         backup_path : str
#             Path for backup database file
#         pages : int, optional
#             Number of pages to copy (-1 for all, default: -1)
#         progress : Optional[Callable[[sqlite3.Connection, int, int], None]], optional
#             Callback function for progress updates

#         Raises
#         ------
#         ValueError
#             If backup fails
#         sqlite3.Error
#             If database operation fails
#         """
#         with self.maintenance_lock():
#             try:

#                 def _progress(
#                     status: sqlite3.Connection, remaining: int, total: int
#                 ) -> None:
#                     if progress:
#                         progress(total - remaining, total)

#                 backup_conn = sqlite3.connect(backup_path)
#                 with backup_conn:
#                     self.conn.backup(
#                         backup_conn, pages=pages, progress=_progress
#                     )
#                 backup_conn.close()
#             except (sqlite3.Error, Exception) as err:
#                 raise ValueError(f"Failed to create backup: {err}")

#     def vacuum(self, into: Optional[str] = None) -> None:
#         """Rebuilds database file to reclaim unused space.

#         Example
#         -------
#         >>> db.vacuum()  # Regular vacuum
#         >>> db.vacuum(into='optimized.db')  # Vacuum into new file

#         Parameters
#         ----------
#         into : Optional[str], optional
#             Path to new database file for vacuum (default: None)

#         Raises
#         ------
#         sqlite3.Error
#             If vacuum operation fails
#         ValueError
#             If target path is invalid
#         """
#         with self.maintenance_lock():
#             try:
#                 if into:
#                     self.execute(f"VACUUM INTO '{into}'")
#                 else:
#                     self.execute("VACUUM")
#             except sqlite3.Error as err:
#                 raise ValueError(f"Vacuum operation failed: {err}")

#     def optimize(self, analyze: bool = True) -> None:
#         """Optimizes database performance with optional analysis.

#         Example
#         -------
#         >>> db.optimize()  # Full optimization
#         >>> db.optimize(analyze=False)  # Skip analysis phase

#         Parameters
#         ----------
#         analyze : bool, optional
#             Whether to run ANALYZE after optimization (default: True)

#         Raises
#         ------
#         ValueError
#             If optimization fails
#         sqlite3.Error
#             If database operations fail
#         """
#         with self.maintenance_lock():
#             try:
#                 self.execute("PRAGMA optimize")
#                 self.vacuum()
#                 if analyze:
#                     self.execute("ANALYZE")
#             except sqlite3.Error as err:
#                 raise ValueError(f"Failed to optimize database: {err}")

#     # # without non-null count
#     # def get_database_size(self, format: str = "bytes") -> Union[int, str]:
#     #     """Gets database file size in specified format.

#     #     Example
#     #     -------
#     #     >>> size_bytes = db.get_database_size()
#     #     >>> size_mb = db.get_database_size(format='mb')
#     #     >>> print(f"Database size: {size_mb} MB")

#     #     Parameters
#     #     ----------
#     #     format : str, optional
#     #         Output format: 'bytes', 'kb', 'mb', 'gb' (default: 'bytes')

#     #     Returns
#     #     -------
#     #     Union[int, str]
#     #         File size in requested format

#     #     Raises
#     #     ------
#     #     FileNotFoundError
#     #         If database file doesn't exist
#     #     ValueError
#     #         If format is invalid
#     #     """
#     #     if not os.path.exists(self.db_path):
#     #         raise FileNotFoundError(f"Database file not found: {self.db_path}")

#     #     size_bytes = os.path.getsize(self.db_path)

#     #     format_map = {
#     #         "bytes": lambda x: x,
#     #         "kb": lambda x: f"{x / 1024:.2f} KB",
#     #         "mb": lambda x: f"{x / (1024 * 1024):.2f} MB",
#     #         "gb": lambda x: f"{x / (1024 * 1024 * 1024):.2f} GB",
#     #     }

#     #     if format.lower() not in format_map:
#     #         raise ValueError(
#     #             f"Invalid format. Choose from: {list(format_map.keys())}"
#     #         )

#     #     return format_map[format.lower()](size_bytes)

#     def get_summaries(
#         self,
#         table_names: Optional[List[str]] = None,
#         verbose: bool = True,
#         limit: int = 5,
#     ) -> Dict[str, pd.DataFrame]:

#         # Handling table_names
#         if table_names is None:
#             table_names = self.get_table_names()
#         if isinstance(table_names, str):
#             table_names = [table_names]

#         sample_tables = {}
#         for table_name in table_names:
#             columns = self.get_table_schema(table_name)
#             table_sample = self.get_rows(table_name=table_name, limit=limit)

#             for column in table_sample.columns:
#                 print(column)
#                 if table_sample[column].dtype == object:

#                     try:
#                         # Try parsing as datetime
#                         pd.to_datetime(table_sample[column])
#                         continue
#                     except:
#                         pass

#                     # Check if all values are strings
#                     if (
#                         table_sample[column]
#                         .apply(lambda x: isinstance(x, str))
#                         .all()
#                     ):
#                         continue

#             sample_tables[table_name] = table_sample

#         return sample_tables

#     # def print_summary(
#     #     self,
#     #     table_names: Optional[List[str]] = None,
#     #     verbose: bool = True,
#     #     limit: int = 5,
#     # ):
#     #     """Prints a friendly summary of all tables in the database."""
#     #     with pd.option_context(
#     #         "display.max_columns",
#     #         None,
#     #         "display.width",
#     #         None,
#     #         "display.max_colwidth",
#     #         None,
#     #     ):

#     #         summaries = self.get_summaries(
#     #             table_names=table_names, verbose=verbose, limit=limit
#     #         )

#     #         print("\n=== Database Summary ===")
#     #         for table_name, df_sample in summaries.items():
#     #             print("-" * (len(table_name) + 7))
#     #             print(f"Table: {table_name}")
#     #             print("-" * (len(table_name) + 7))
#     #             if df_sample.empty:
#     #                 print("Empty table")
#     #             else:
#     #                 # Get full table for accurate counts
#     #                 with self.lock:
#     #                     full_df = pd.read_sql_query(
#     #                         f"SELECT * FROM {table_name}", self.conn
#     #                     )
#     #                 print(f"\nSample rows ({len(df_sample)} shown):\n")
#     #                 dtype_df = pd.DataFrame(
#     #                     [df_sample.dtypes], index=["dtype"]
#     #                 )
#     #                 non_null_counts = pd.DataFrame(
#     #                     [full_df.notna().sum()], index=["non-null count"]
#     #                 )
#     #                 print(pd.concat([df_sample, dtype_df, non_null_counts]))

#     #             print()

#     @property
#     def summary(self):
#         self()

#

# EOF
