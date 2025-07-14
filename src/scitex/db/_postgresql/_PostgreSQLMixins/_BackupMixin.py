#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-24 23:06:03 (ywatanabe)"
# File: ./scitex_repo/src/scitex/db/_PostgreSQLMixins/_BackupMixin.py

THIS_FILE = (
    "/home/ywatanabe/proj/scitex_repo/src/scitex/db/_PostgreSQLMixins/_BackupMixin.py"
)

import subprocess
import os
from typing import Optional, List
from ..._BaseMixins._BaseBackupMixin import _BaseBackupMixin


class _BackupMixin(_BaseBackupMixin):
    def backup_table(self, table: str, file_path: str) -> None:
        """Backup a specific table using pg_dump"""
        connection_params = self._get_connection_params()
        cmd = [
            "pg_dump",
            "-h",
            connection_params["host"],
            "-p",
            str(connection_params["port"]),
            "-U",
            connection_params["user"],
            "-d",
            connection_params["database"],
            "-t",
            table,
            "-f",
            file_path,
        ]

        env = os.environ.copy()
        env["PGPASSWORD"] = connection_params["password"]

        try:
            subprocess.run(cmd, env=env, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            raise Exception(f"Backup failed: {e.stderr.decode()}")

    def restore_table(self, table: str, file_path: str) -> None:
        """Restore a specific table from backup"""
        self._check_writable()
        connection_params = self._get_connection_params()
        cmd = [
            "psql",
            "-h",
            connection_params["host"],
            "-p",
            str(connection_params["port"]),
            "-U",
            connection_params["user"],
            "-d",
            connection_params["database"],
            "-f",
            file_path,
        ]

        env = os.environ.copy()
        env["PGPASSWORD"] = connection_params["password"]

        try:
            subprocess.run(cmd, env=env, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            raise Exception(f"Restore failed: {e.stderr.decode()}")

    def backup_database(self, file_path: str) -> None:
        """Backup entire database using pg_dump"""
        connection_params = self._get_connection_params()
        cmd = [
            "pg_dump",
            "-h",
            connection_params["host"],
            "-p",
            str(connection_params["port"]),
            "-U",
            connection_params["user"],
            "-d",
            connection_params["database"],
            "-F",
            "c",  # Custom format
            "-f",
            file_path,
        ]

        env = os.environ.copy()
        env["PGPASSWORD"] = connection_params["password"]

        try:
            subprocess.run(cmd, env=env, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            raise Exception(f"Database backup failed: {e.stderr.decode()}")

    def restore_database(self, file_path: str) -> None:
        """Restore entire database from backup"""
        self._check_writable()
        connection_params = self._get_connection_params()
        cmd = [
            "pg_restore",
            "-h",
            connection_params["host"],
            "-p",
            str(connection_params["port"]),
            "-U",
            connection_params["user"],
            "-d",
            connection_params["database"],
            "--clean",  # Clean (drop) database objects before recreating
            file_path,
        ]

        env = os.environ.copy()
        env["PGPASSWORD"] = connection_params["password"]

        try:
            subprocess.run(cmd, env=env, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            raise Exception(f"Database restore failed: {e.stderr.decode()}")

    def copy_table(
        self, source_table: str, target_table: str, where: Optional[str] = None
    ) -> None:
        """Copy data from one table to another"""
        self._check_writable()

        # Get column names from source table
        self.execute(
            f"""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = %s
            ORDER BY ordinal_position
        """,
            (source_table,),
        )
        columns: List[str] = [row[0] for row in self.cursor.fetchall()]
        columns_str = ", ".join(columns)

        # Create the target table with the same structure
        self.execute(
            f"CREATE TABLE IF NOT EXISTS {target_table} AS SELECT * FROM {source_table} WHERE 1=0"
        )

        # Copy data
        query = f"INSERT INTO {target_table} ({columns_str}) SELECT {columns_str} FROM {source_table}"
        if where:
            query += f" WHERE {where}"

        self.execute(query)

    def _get_connection_params(self) -> dict:
        """Extract connection parameters from the current connection"""
        dsn = self.conn.get_dsn_parameters()
        return {
            "host": dsn.get("host", "localhost"),
            "port": dsn.get("port", 5432),
            "user": dsn.get("user", ""),
            "password": dsn.get("password", ""),
            "database": dsn.get("dbname", ""),
        }


# EOF
