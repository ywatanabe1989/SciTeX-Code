#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-02-27 22:14:52 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_dev/src/scitex/db/_PostgreSQLMixins/_ConnectionMixin.py

THIS_FILE = (
    "/home/ywatanabe/proj/scitex_repo/src/scitex/db/_PostgreSQLMixins/_ConnectionMixin.py"
)

from typing import Any, Tuple
import psycopg2

from ..._BaseMixins._BaseConnectionMixin import _BaseConnectionMixin


class _ConnectionMixin(_BaseConnectionMixin):
    def __init__(
        self,
        dbname: str,
        user: str,
        password: str,
        host: str = "localhost",
        port: int = 5432,
    ):
        super().__init__()
        self.db_config = {
            "dbname": dbname,
            "user": user,
            "password": password,
            "host": host,
            "port": port,
        }
        if dbname:
            self.connect()

    def connect(self) -> None:
        if self.conn:
            self.close()

        self.conn = psycopg2.connect(**self.db_config)
        self.cursor = self.conn.cursor()

        with self.lock:
            self.conn.autocommit = False
            self.cursor.execute(
                "SET SESSION CHARACTERISTICS AS TRANSACTION ISOLATION LEVEL READ COMMITTED"
            )

    def close(self) -> None:
        if self.cursor:
            self.cursor.close()
        if self.conn:
            try:
                self.conn.close()
            except psycopg2.Error:
                pass
        self.cursor = None
        self.conn = None

    def reconnect(self) -> None:
        if self.db_config:
            self.connect()
        else:
            raise ValueError("No database configuration specified for reconnection")

    def execute(self, query: str, parameters: Tuple = None) -> Any:
        """Execute a database query."""
        if not self.cursor:
            raise ConnectionError("Database not connected")

        try:
            self.cursor.execute(query, parameters)
            self.conn.commit()
            return self.cursor
        except psycopg2.Error as err:
            self.conn.rollback()
            raise psycopg2.Error(f"Query execution failed: {err}")

    def executemany(self, query: str, parameters: list) -> None:
        """Execute multiple database queries."""
        if not self.cursor:
            raise ConnectionError("Database not connected")

        try:
            self.cursor.executemany(query, parameters)
            self.conn.commit()
        except psycopg2.Error as err:
            self.conn.rollback()
            raise psycopg2.Error(f"Batch query execution failed: {err}")


# EOF
